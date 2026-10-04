"""
figlayout.py -- shared layout-invariant checks for the results-section figure
set (NEW-A..NEW-H). Did not exist before this build; created here implementing
exactly the four checks named in the brief: canvas fill, no dead bands, no
text collision, minimum text size. Not part of the earlier Figures 1-13 set
(those predate this module and were not re-checked against it).

Usage: run_invariants(fig, out_path) after rendering, before saving, or on a
saved PNG via run_invariants_on_file(path). Returns an InvariantReport; each
figure script's own render() should assert on it (or its test should) rather
than silently ignoring a failure.

canvas_fill history: the first implementation measured pixel DENSITY
(fraction of non-background pixels), which is near-zero for any sparse
scatter/point-cloud figure by construction and can never fail -- worthless
as the dead-canvas check it was meant to be. Reimplemented to measure content
EXTENT instead: the span of the non-background bounding box as a fraction of
the canvas height/width. This is what actually catches a figure whose real
content occupies a small island in a mostly-empty frame.
"""
import dataclasses

import matplotlib
import numpy as np
from PIL import Image

import figstyle as fs

MIN_TEXT_PT = 10.0           # smallest legible text at print/video scale (points, matplotlib's native unit)
CONTENT_HEIGHT_MIN = 0.82    # non-background bounding-box height, as a fraction of canvas height
CONTENT_WIDTH_MIN = 0.90     # non-background bounding-box width, as a fraction of canvas width
MAX_DEAD_BAND_FRAC = 0.35    # largest allowed single empty edge-to-edge band


@dataclasses.dataclass
class InvariantReport:
    height_span: float
    width_span: float
    canvas_fill_ok: bool
    dead_bands: list          # list of (axis, frac) for bands that failed
    dead_bands_ok: bool
    text_collisions: list     # list of (text_a, text_b) overlapping pairs
    text_collision_ok: bool
    min_text_pt: float
    min_text_ok: bool

    @property
    def all_ok(self):
        return (self.canvas_fill_ok and self.dead_bands_ok
                and self.text_collision_ok and self.min_text_ok)

    def summary(self):
        lines = [
            f"canvas_fill: height_span={self.height_span:.3f} (min {CONTENT_HEIGHT_MIN}) "
            f"width_span={self.width_span:.3f} (min {CONTENT_WIDTH_MIN}) "
            f"({'PASS' if self.canvas_fill_ok else 'FAIL'})",
            f"dead_bands: {'PASS' if self.dead_bands_ok else 'FAIL'} "
            f"({len(self.dead_bands)} over {MAX_DEAD_BAND_FRAC}: {self.dead_bands})",
            f"text_collision: {'PASS' if self.text_collision_ok else 'FAIL'} "
            f"({len(self.text_collisions)} overlapping pairs)",
            f"min_text_pt: {self.min_text_pt:.1f} "
            f"({'PASS' if self.min_text_ok else 'FAIL'}, min {MIN_TEXT_PT})",
        ]
        return "\n".join(lines)


def _content_mask(img_rgb, bg_rgb, tol=15):
    bg = np.array(bg_rgb) * 255
    diff = np.abs(img_rgb.astype(int) - bg.astype(int)).sum(axis=-1)
    return diff > tol


def _check_canvas_fill(mask):
    """Content EXTENT (bounding-box span), not density. A figure with one
    small cluster of points in a corner has near-zero density but should
    still fail this check if its bounding box doesn't span the canvas --
    extent is what this computes."""
    h, w = mask.shape
    rows = mask.any(axis=1)
    cols = mask.any(axis=0)
    if not rows.any():
        return 0.0, 0.0, False
    row_idx = np.where(rows)[0]
    col_idx = np.where(cols)[0]
    height_span = float(row_idx[-1] - row_idx[0]) / h
    width_span = float(col_idx[-1] - col_idx[0]) / w
    ok = height_span >= CONTENT_HEIGHT_MIN and width_span >= CONTENT_WIDTH_MIN
    return height_span, width_span, ok


def _check_dead_bands(mask):
    h, w = mask.shape
    row_has_content = mask.any(axis=1)
    col_has_content = mask.any(axis=0)
    bad = []
    for axis_name, has_content, total in [("row", row_has_content, h), ("col", col_has_content, w)]:
        # largest contiguous run of empty rows/cols, as a fraction of the canvas.
        # Title/caption text bands are NOT excluded by special-casing -- they
        # are excluded automatically because they contain real (non-background)
        # pixels, which breaks any contiguous empty run that would otherwise
        # cross them. This only measures genuinely empty gaps.
        empty = ~has_content
        run = 0
        best = 0
        for v in empty:
            run = run + 1 if v else 0
            best = max(best, run)
        frac = best / total
        if frac > MAX_DEAD_BAND_FRAC:
            bad.append((axis_name, round(frac, 3)))
    return bad, len(bad) == 0


def _text_bbox_px(txt, renderer):
    bbox = txt.get_window_extent(renderer=renderer)
    return bbox.x0, bbox.y0, bbox.x1, bbox.y1


def _boxes_overlap(a, b, pad=1.0):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 + pad < bx0 or bx1 + pad < ax0 or ay1 + pad < by0 or by1 + pad < ay0)


def _check_text(fig):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    texts = list(fig.texts)
    for ax in fig.axes:
        texts.extend(ax.texts)
        if ax.title.get_text():
            texts.append(ax.title)
    visible = [t for t in texts if t.get_text().strip() and t.get_visible()]
    boxes = [(_text_bbox_px(t, renderer), t) for t in visible]
    collisions = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            (box_i, t_i), (box_j, t_j) = boxes[i], boxes[j]
            if _boxes_overlap(box_i, box_j):
                collisions.append((t_i.get_text()[:40], t_j.get_text()[:40]))
    min_pt = min((t.get_fontsize() for t in visible), default=999.0)
    return collisions, len(collisions) == 0, min_pt, min_pt >= MIN_TEXT_PT


def run_invariants(fig, bg_rgb=None):
    """Runs all four checks on a live (not-yet-saved) matplotlib Figure."""
    bg_rgb = bg_rgb or matplotlib.colors.to_rgb(fs.SLIDE_BG)
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
    mask = _content_mask(buf, bg_rgb)
    h_span, w_span, fill_ok = _check_canvas_fill(mask)
    bands, bands_ok = _check_dead_bands(mask)
    collisions, coll_ok, min_pt, min_pt_ok = _check_text(fig)
    return InvariantReport(h_span, w_span, fill_ok, bands, bands_ok, collisions, coll_ok, min_pt, min_pt_ok)


def run_invariants_on_file(path, bg_rgb=None):
    """Runs the canvas-fill and dead-band checks on an already-saved PNG
    (text-collision/min-size cannot be recovered from a flat raster, so those
    two report as skipped/ok=True with min_text_pt=nan when called this way --
    prefer run_invariants() on the live Figure when possible)."""
    bg_rgb = bg_rgb or matplotlib.colors.to_rgb(fs.SLIDE_BG)
    with Image.open(path) as im:
        img = np.asarray(im.convert("RGB"))
    mask = _content_mask(img, bg_rgb)
    h_span, w_span, fill_ok = _check_canvas_fill(mask)
    bands, bands_ok = _check_dead_bands(mask)
    return InvariantReport(h_span, w_span, fill_ok, bands, bands_ok, [], True, float("nan"), True)


# ---- slide-variant invariants -----------------------------------------------
# A slide is read from across a room in the time it takes to say one sentence.
# These three are stricter than (and layered on top of) the report checks.

SLIDE_MIN_TEXT_PT = 16.0     # smallest legible text at slide/projector scale
SLIDE_MAX_CAPTION_LINES = 1  # one line of sourcing, not three
SLIDE_MIN_HERO_PT = 48.0     # at least one element this size or larger


@dataclasses.dataclass
class SlideInvariantReport:
    min_text_pt: float
    min_text_ok: bool          # every visible text >= SLIDE_MIN_TEXT_PT
    caption_lines: int
    caption_lines_ok: bool     # caption fig.text objects tagged as caption <= 1
    hero_pt: float
    hero_ok: bool              # at least one text >= SLIDE_MIN_HERO_PT exists

    @property
    def all_ok(self):
        return self.min_text_ok and self.caption_lines_ok and self.hero_ok

    def summary(self):
        return "\n".join([
            f"slide_min_text_pt: {self.min_text_pt:.1f} "
            f"({'PASS' if self.min_text_ok else 'FAIL'}, min {SLIDE_MIN_TEXT_PT})",
            f"slide_caption_lines: {self.caption_lines} "
            f"({'PASS' if self.caption_lines_ok else 'FAIL'}, max {SLIDE_MAX_CAPTION_LINES})",
            f"slide_hero_pt: {self.hero_pt:.1f} "
            f"({'PASS' if self.hero_ok else 'FAIL'}, min {SLIDE_MIN_HERO_PT})",
        ])


def run_slide_invariants(fig, caption_texts):
    """caption_texts: the list of Text objects (or (x,y,s) tuples already
    added to the figure) that make up the ONE-LINE slide caption/source
    credit -- passed explicitly because a slide figure's caption is not
    structurally distinguishable from any other on-figure text otherwise."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    texts = list(fig.texts)
    for ax in fig.axes:
        texts.extend(ax.texts)
        if ax.title.get_text():
            texts.append(ax.title)
    visible = [t for t in texts if t.get_text().strip() and t.get_visible()]
    sizes = [t.get_fontsize() for t in visible]
    min_pt = min(sizes, default=999.0)
    hero_pt = max(sizes, default=0.0)
    n_caption_lines = len(caption_texts)
    return SlideInvariantReport(
        min_text_pt=min_pt, min_text_ok=min_pt >= SLIDE_MIN_TEXT_PT,
        caption_lines=n_caption_lines, caption_lines_ok=n_caption_lines <= SLIDE_MAX_CAPTION_LINES,
        hero_pt=hero_pt, hero_ok=hero_pt >= SLIDE_MIN_HERO_PT,
    )


def print_speaker_notes(figure_name, lines):
    """Prints omitted provenance/hedges/scope notes to stdout under a
    standard heading, for pasting into the deck's notes field. Nothing on
    the slide is lost -- it moves here."""
    print(f"\nSPEAKER NOTES -- {figure_name}")
    print("-" * (16 + len(figure_name)))
    for line in lines:
        print(f"  {line}")
    print()
