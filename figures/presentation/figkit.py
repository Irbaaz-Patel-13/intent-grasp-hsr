"""
figkit.py - shared style, layout helpers and data loaders for AffordGrasp figures.

Design rules baked in here (they are what prevent the usual figure defects):
  * one font family and a fixed type scale, so panels never disagree
  * constrained_layout everywhere; tight_layout is never called
  * text wrapping is measured, not guessed, so labels cannot overlap
  * every loader validates and reports; nothing is silently invented

Requires: matplotlib >= 3.6, numpy, pandas, pillow (only for image figures).
"""

from __future__ import annotations

import csv
import json
import re
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# --------------------------------------------------------------------------
# 1. STYLE  -- governed by figures/scripts/_style.py, not by this file.
#
# STORYBOARD_CONVENTIONS.md rules that _style.py (print, fig_5_x/6_x/7_x)
# governs every asset here, over figstyle.py's dark-slide palette. Values
# below are transcribed from _style.py so a figure built with figkit sits
# beside one built with _style.py without a visible seam.
# --------------------------------------------------------------------------

OKABE_ITO = {
    "black":      "#000000",
    "orange":     "#E69F00",
    "sky_blue":   "#56B4E9",
    "green":      "#009E73",
    "yellow":     "#F0E442",
    "blue":       "#0072B2",
    "vermillion": "#D55E00",
    "purple":     "#CC79A7",
}

SEMANTIC_COLOUR = {
    "reasoning":          OKABE_ITO["blue"],
    "perception":         OKABE_ITO["orange"],
    "geometric_planning": OKABE_ITO["green"],
    "robot_control":      OKABE_ITO["vermillion"],
    "verification":       OKABE_ITO["purple"],
    "measured":           OKABE_ITO["blue"],
    "estimated":          OKABE_ITO["sky_blue"],
    "reject":             OKABE_ITO["black"],
    "keep":               OKABE_ITO["green"],
}
SEMANTIC_HATCH = {
    "reasoning": "", "perception": "///", "geometric_planning": "...",
    "robot_control": "xxx", "verification": "\\\\\\",
    "measured": "", "estimated": "///",
}


def semantic_colour(layer):
    return SEMANTIC_COLOUR[layer]


def semantic_hatch(layer):
    return SEMANTIC_HATCH.get(layer, "")


# Aliases kept so existing builders read naturally.
BLUE   = OKABE_ITO["blue"]
ORANGE = OKABE_ITO["orange"]
GREEN  = OKABE_ITO["green"]
RED    = OKABE_ITO["vermillion"]
PURPLE = OKABE_ITO["purple"]
SKY    = OKABE_ITO["sky_blue"]
YELLOW = OKABE_ITO["yellow"]
INK    = "#000000"
MUTED  = "#5A5A5A"
RULE   = "#C8C8C8"
FAINT  = "#EDF2F7"

OUTCOME_COLOURS = {
    "GRASP_OK":        OKABE_ITO["green"],
    "ABORT":           OKABE_ITO["orange"],
    "HELD_LIFT_FAULT": OKABE_ITO["vermillion"],
    "MISSING":         "#FFFFFF",
}

# _style.py type scale
FS_TITLE = 9.0
FS_LABEL = 9.0
FS_TICK  = 8.0
FS_ANNOT = 8.0
FS_SMALL = 8.0

TEXT_WIDTH_IN = 6.27      # A4, 1 in margins
HALF_WIDTH_IN = 3.05
MAX_HEIGHT_IN = 8.0
COL_W  = TEXT_WIDTH_IN
HALF_W = HALF_WIDTH_IN


def use_style() -> None:
    """Apply _style.py's rcParams verbatim."""
    mpl.rcParams.update({
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "figure.dpi": 150,
        "savefig.dpi": 400,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans"],
        "font.size": 9,
        "axes.labelsize": 9,
        "axes.titlesize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "axes.linewidth": 0.8,
        "lines.linewidth": 1.4,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.constrained_layout.use": True,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "legend.frameon": False,
        "axes.grid": False,
        "grid.color": RULE,
        "grid.linewidth": 0.5,
    })


# --- DESIGN_STANDARD.md Rule 1 -------------------------------------------
# No internal identifier reaches a figure. display() raises on a missing
# entry so an unlabelled component is a build failure, not a silent leak.
DISPLAY_NAME = {
    "main_body":             "body",
    "top_protrusion":        "rim / lid region",
    "rim_ring":              "rim",
    "lateral_protrusion":    "handle (fragment 1)",
    "lateral_protrusion_1":  "handle (fragment 2)",
    "segment_a":             "thin end",
    "segment_b":             "mid-section",
    "segment_c":             "thick end",
    "A_heuristic":           "heuristic",
    "B_som":                 "Set-of-Mark",
    "C_pointing":            "pointing",
    "ok":                    "accepted",
    "LOW":                   "marginal",
    "NOISE":                 "refused",
}


def display(key, strict=True):
    """Reader-facing label for an internal identifier (Rule 1)."""
    k = str(key).strip()
    if k in DISPLAY_NAME:
        return DISPLAY_NAME[k]
    if strict:
        raise KeyError(f"No reader-facing name for {k!r} -- add one to "
                       f"figkit.DISPLAY_NAME before plotting it")
    return k


def display_soft(text):
    """Translate any embedded identifiers inside a free-text cell."""
    out = str(text)
    for k in sorted(DISPLAY_NAME, key=len, reverse=True):
        out = re.sub(rf"\b{re.escape(k)}\b", DISPLAY_NAME[k], out)
    return out


def new_figure(w=COL_W, h=3.4, **kw):
    if h > MAX_HEIGHT_IN:
        print(f"    ! figure height {h:.2f} in exceeds the {MAX_HEIGHT_IN} in "
              f"page limit; it will not fit without scaling")
    return plt.figure(figsize=(w, h), **kw)


def panel_label(ax, letter, x=0.0, y=1.06):
    """(a)/(b) above the top spine, left-aligned to the axes."""
    return ax.text(x, y, f"({letter})", transform=ax.transAxes,
                   ha="left", va="bottom", fontsize=FS_LABEL,
                   fontweight="bold")


def mask_contour(ax, part_mask, whole_mask=None, colour=None,
                 ref_colour=None, alpha=0.22):
    """
    _style.py's mask convention: the part mask gets BOTH a light fill and a
    hard boundary; the whole-object mask is a dashed neutral reference
    contour. Chosen so two near-identical masks stay distinguishable.
    """
    colour = colour or SEMANTIC_COLOUR["perception"]
    ref_colour = ref_colour or OKABE_ITO["black"]
    if whole_mask is not None and whole_mask.any():
        ax.contour(whole_mask.astype(float), levels=[0.5],
                   colors=[ref_colour], linewidths=1.0,
                   linestyles="dashed")
    if part_mask is not None and part_mask.any():
        rgba = np.zeros(part_mask.shape + (4,))
        rgba[..., :3] = mpl.colors.to_rgb(colour)
        rgba[..., 3] = part_mask.astype(float) * alpha
        ax.imshow(rgba, interpolation="nearest")
        ax.contour(part_mask.astype(float), levels=[0.5], colors=[colour],
                   linewidths=1.3)


def truncation_marker(ax, axis="y", at=0.0):
    """Explicit // break rather than a silent non-zero baseline."""
    kw = dict(transform=ax.transAxes, fontsize=FS_SMALL, color=INK,
              ha="center", va="center", zorder=10)
    if axis == "y":
        ax.text(0.0, at, "//", rotation=90, **kw)
    else:
        ax.text(at, 0.0, "//", **kw)


# --------------------------------------------------------------------------
# 2. LAYOUT HELPERS  (these are what stop overlap)
# --------------------------------------------------------------------------

def arrow() -> str:
    """A right-arrow the active serif font can actually render, else 'to'."""
    from matplotlib.font_manager import findfont, FontProperties
    try:
        from matplotlib.ft2font import FT2Font
        f = FT2Font(findfont(FontProperties(family=mpl.rcParams["font.family"])))
        if f.get_char_index(0x2192):
            return "\u2192"
    except Exception:
        pass
    return "to"


def split_qualifier(label: str):
    """
    'part_width_m (perception input, not a VLM field)' ->
    ('part_width_m', 'perception input, not a VLM field').

    The routing table stores an identifier plus an explanatory aside in one
    cell; drawn as one string it overflows every box on the figure.
    """
    s = str(label).strip()
    m = re.match(r"^([^(\[]+?)\s*[(\[](.+?)[)\]]\s*$", s)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return s, ""


def wrap_ident(text: str, width_chars: int) -> str:
    """Wrap that may also break on underscores and slashes, not just spaces."""
    zwsp = "\u200b"
    s = re.sub(r"([_/,])", lambda mo: mo.group(1) + zwsp, str(text))
    out = textwrap.wrap(s, width=width_chars, break_long_words=True)
    return "\n".join(o.replace("\u200b", "") for o in out)


def wrap(text: str, width_chars: int) -> str:
    """Hard-wrap to a character count. Use for table cells and long labels."""
    if text is None:
        return ""
    return "\n".join(textwrap.wrap(str(text), width=width_chars)) or ""


def text_extent_inches(fig, artist) -> tuple[float, float]:
    """Measured width/height of a drawn text artist, in inches."""
    fig.canvas.draw()
    bb = artist.get_window_extent(renderer=fig.canvas.get_renderer())
    return bb.width / fig.dpi, bb.height / fig.dpi


def declutter(ax, xgrid=False, ygrid=True):
    """Light horizontal rules only. Gridlines sit behind the data."""
    ax.set_axisbelow(True)
    if ygrid:
        ax.grid(True, axis="y", color=RULE, linewidth=0.5)
    if xgrid:
        ax.grid(True, axis="x", color=RULE, linewidth=0.5)


def annotate_point(ax, xy, text, dx=12, dy=12, ha="left", va="bottom",
                   colour=INK, arrow=True, fontsize=FS_ANNOT):
    """
    Leader-line annotation with an offset in *points*, so the callout keeps its
    distance from the marker regardless of axis scaling.
    """
    kw = dict(xy=xy, xytext=(dx, dy), textcoords="offset points",
              fontsize=fontsize, color=colour, ha=ha, va=va,
              zorder=6,
              bbox=dict(boxstyle="round,pad=0.22", fc="white",
                        ec="none", alpha=0.88))
    if arrow:
        kw["arrowprops"] = dict(arrowstyle="-", color=MUTED,
                                linewidth=0.6, shrinkA=0, shrinkB=3)
    return ax.annotate(text, **kw)


def freeze_layout(fig):
    """Solve constrained_layout once, then fix it so later text cannot move it."""
    fig.canvas.draw()
    try:
        fig.set_layout_engine("none")
    except Exception:
        pass


def resolve_collisions(fig, artists, step_pt=8.0, max_iter=40, max_pt=44.0):
    """
    Nudge annotation artists vertically until their bounding boxes stop
    intersecting. Runs against a frozen layout so the axes cannot collapse,
    and refuses to push a label more than max_pt from its anchor.
    """
    freeze_layout(fig)
    rend = fig.canvas.get_renderer()
    for _ in range(max_iter):
        moved = False
        boxes = [(a, a.get_window_extent(renderer=rend)) for a in artists]
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a1, b1 = boxes[i]
                a2, b2 = boxes[j]
                if b1.overlaps(b2):
                    hi = a1 if b1.y0 >= b2.y0 else a2
                    ox, oy = hi.get_position() if isinstance(
                        hi.get_position(), tuple) else (0, 0)
                    # annotations store the offset in xyann/xytext
                    try:
                        cx, cy = hi.xyann
                        if abs(cy + step_pt) <= max_pt:
                            hi.xyann = (cx, cy + step_pt)
                            moved = True
                    except Exception:
                        pass
        if not moved:
            return
        fig.canvas.draw()


def save(fig, outdir, stem, formats=("pdf", "svg", "png")):
    """Write vector + raster. PDF is what you place in Word for print quality."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    # _style.py uses savefig.bbox="tight"; solve constrained_layout once and
    # freeze it first so annotations placed outside the axes cannot collapse
    # them during the tight-bbox pass.
    freeze_layout(fig)
    written = []
    for ext in formats:
        p = outdir / f"{stem}.{ext}"
        # No tight_layout, and no bbox_inches='tight': constrained_layout has
        # already reserved the correct margins. Cropping again would change the
        # physical width and break consistency between figures.
        fig.savefig(p, format=ext)
        written.append(p)
    plt.close(fig)
    for p in written:
        print(f"    wrote {p}")
    return written


# --------------------------------------------------------------------------
# 3. DATA LOADING
# --------------------------------------------------------------------------

class DataProblem(RuntimeError):
    pass


def _find(root: Path, *relatives) -> Path | None:
    """Return the first path that exists, else None."""
    for r in relatives:
        p = (root / r) if not Path(r).is_absolute() else Path(r)
        if p.exists():
            return p
    return None


def read_csv_tolerant(path: Path) -> list[dict]:
    """
    Read a CSV that may contain unquoted delimiters inside a field.

    Section 3.13 documents exactly this defect in the part-naming ablation file:
    a naive reader shifts every subsequent column on affected rows. Here, rows
    with too many fields are reported and the surplus is folded back into the
    last *quoted-looking* column rather than silently shifting the tail.
    """
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        raise DataProblem(f"{path} is empty")
    header = [h.strip() for h in rows[0]]
    n = len(header)
    out, malformed = [], []
    for ln, row in enumerate(rows[1:], start=2):
        if len(row) == n:
            out.append(dict(zip(header, [c.strip() for c in row])))
        elif len(row) > n:
            malformed.append(ln)
            merged = row[:n - 1] + [",".join(row[n - 1:])]
            out.append(dict(zip(header, [c.strip() for c in merged])))
        else:
            malformed.append(ln)
            padded = row + [""] * (n - len(row))
            out.append(dict(zip(header, [c.strip() for c in padded])))
    if malformed:
        print(f"    ! {path.name}: {len(malformed)} malformed row(s) at lines "
              f"{malformed[:6]}{'...' if len(malformed) > 6 else ''} "
              f"- surplus fields folded into the final column, tail not shifted")
    return out


def pick_column(rows: list[dict], *candidates, required=True, label=""):
    """
    Find a column by trying several names case-insensitively, then by substring.
    Your schemas have drifted across vintages, so this is safer than assuming.
    """
    if not rows:
        return None
    keys = list(rows[0].keys())
    low = {k.lower().strip(): k for k in keys}
    for c in candidates:
        if c.lower() in low:
            return low[c.lower()]
    for c in candidates:
        if len(c) < 3:
            continue                      # too short to substring-match safely
        for k in keys:
            kl = k.lower()
            if c.lower() == kl or re.search(rf"(^|[_\W]){re.escape(c.lower())}($|[_\W])", kl):
                return k
    for c in candidates:
        if len(c) < 3:
            continue
        for k in keys:
            if c.lower() in k.lower():
                return k
    if required:
        raise DataProblem(
            f"could not find a column for {label or candidates[0]!r}.\n"
            f"      tried: {candidates}\n"
            f"      available: {keys}")
    return None


def to_float(v, default=np.nan):
    try:
        return float(str(v).strip().replace("m", "").replace(",", ""))
    except (TypeError, ValueError):
        return default


# ---- trials ---------------------------------------------------------------

EXPECTED_TRIAL_IDS = [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12]   # 8 is genuinely absent


def load_trials(root: Path, bundle: str, explicit: Path | None = None) -> list[dict]:
    """
    Load the authoritative trial record and verify it is the bundle copy.

    The repository root holds a stale 7-row copy. Building Chapter 7 figures
    from that copy would understate the record, so this refuses to proceed
    unless the file matches the audited shape.
    """
    p = explicit if (explicit and explicit.exists()) else _find(
        root, "figure_data/trials_clean.csv", f"{bundle}/trials.csv",
        "trials.csv")
    if p is None:
        raise DataProblem(
            f"no trials.csv found under {root}. Expected {bundle}/trials.csv")
    print(f"    reading {p}")
    rows = read_csv_tolerant(p)

    c_id = pick_column(rows, "trial", "trial_id", "trial_no", "trial_index",
                       required=False)
    ids = []
    if c_id:
        ids = [int(to_float(r[c_id], 0)) for r in rows
               if str(r[c_id]).strip() != ""]
    if not ids or all(i == 0 for i in ids):
        c_id = None
        if len(rows) == len(EXPECTED_TRIAL_IDS):
            ids = list(EXPECTED_TRIAL_IDS)
            print("    no trial-id column; row order matches the audited "
                  "11-trial record, applying ids 1-7 and 9-12")
        else:
            ids = list(range(1, len(rows) + 1))
            print(f"    ! no trial-id column and {len(rows)} rows present, so "
                  f"row order was numbered 1-{len(rows)}. If this file is not "
                  f"the audited 11-trial record, pass the right one, or supply "
                  f"--trial-ids 1,2,3,4,5,6,7,9,10,11,12")

    # trials_clean.csv carries an explicit placeholder row for the missing
    # trial 8 (every field empty but `note`). Drop it: the figure draws the
    # gap from the absence, so keeping the row would double-count it.
    c_out = pick_column(rows, "outcome", "verdict", required=False)
    if c_out:
        keep = [(r, i) for r, i in zip(rows, ids)
                if str(r.get(c_out, "")).strip() != ""]
        if len(keep) < len(rows):
            dropped = [i for r, i in zip(rows, ids)
                       if str(r.get(c_out, "")).strip() == ""]
            print(f"    placeholder row(s) for trial(s) {dropped} dropped; "
                  f"the gap is drawn from the absence")
            rows = [r for r, _ in keep]
            ids = [i for _, i in keep]

    if sorted(ids) != EXPECTED_TRIAL_IDS:
        print(f"    ! trial ids present: {sorted(ids)}")
        print(f"    ! expected:          {EXPECTED_TRIAL_IDS}")
        if len(ids) <= 7:
            raise DataProblem(
                "this looks like the STALE root copy (7 rows). Point --root at "
                "the repo and make sure the report bundle is present, or pass "
                "--bundle with the correct folder name.")
        print("    ! continuing, but check this is the audited bundle copy")
    else:
        print(f"    ok: 11 trials, ids 1-7 and 9-12, trial 8 absent as recorded")
    for r, i in zip(rows, ids):
        r["_id"] = i
    return rows


# ---- perception components ------------------------------------------------

@dataclass
class Component:
    name: str
    width_mm: float
    pixels: float
    recovered: bool
    object: str = ""
    note: str = ""
    citable: bool = True


def load_components(root: Path, explicit: Path | None = None) -> list[Component]:
    """
    Component width/pixel measurements for the sensor-envelope figure.

    Tries, in order: an explicit CSV, components.csv, then a markdown table in
    PERCEPTION_EVIDENCE.md. If it cannot assemble the full set it writes a
    template for you to complete rather than inventing values.
    """
    src = explicit or _find(root, "figure_data/components.csv",
                            "components.csv",
                            "report_assets/components.csv")
    if src and src.exists():
        print(f"    reading {src}")
        rows = read_csv_tolerant(src)
        c_n = pick_column(rows, "name", "component", "part", label="name")
        c_o = pick_column(rows, "object", required=False)
        c_w = pick_column(rows, "width_mm", "width", "mm", label="width_mm")
        c_p = pick_column(rows, "pixels", "px", "pixel_width", label="pixels")
        c_r = pick_column(rows, "recovered", "resolved", "passed",
                          required=False)
        c_c = pick_column(rows, "citable", required=False)
        out = []
        for r in rows:
            rec = True
            if c_r:
                rec = str(r[c_r]).strip().lower() in ("1", "true", "yes", "y", "t")
            cit = truthy(r[c_c]) if c_c else True
            name = r[c_n].strip()
            if c_o and r.get(c_o, "").strip():
                name = f"{r[c_o].strip()} {name}"
            out.append(Component(name, to_float(r[c_w]), to_float(r[c_p]),
                                 rec, r.get(c_o, "") if c_o else "",
                                 r.get("note", ""), cit))
        return out

    md = _find(root, "PERCEPTION_EVIDENCE.md", "docs/PERCEPTION_EVIDENCE.md")
    if md:
        print(f"    parsing {md}")
        comps = _parse_md_components(md)
        if comps:
            return comps
        print("    ! no width/pixel table recognised in PERCEPTION_EVIDENCE.md")

    tpl = root / "components.csv"
    tpl.write_text(
        "name,width_mm,pixels,recovered,note\n"
        "mug handle,4.0,2.5,false,below evidence floor\n"
        "knife handle,,15.2,true,\n"
        "# fill in the remaining measured components, then re-run\n",
        encoding="utf-8")
    raise DataProblem(
        f"could not assemble the component set automatically.\n"
        f"      A template has been written to {tpl}\n"
        f"      Fill in the five measured components and re-run this figure.")


def _parse_md_components(md: Path) -> list[Component]:
    """Pull a pipe table with width and pixel columns out of a markdown file."""
    lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
    comps, header, hidx = [], None, {}
    for ln in lines:
        if "|" not in ln:
            header = None
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if set("".join(cells)) <= set("-: "):
            continue
        if header is None:
            header = [c.lower() for c in cells]
            hidx = {}
            for i, h in enumerate(header):
                if "width" in h or h.endswith("mm"):
                    hidx["w"] = i
                elif "pixel" in h or h == "px":
                    hidx["p"] = i
                elif any(k in h for k in ("component", "part", "name")):
                    hidx["n"] = i
                elif any(k in h for k in ("recover", "resolve", "gate")):
                    hidx["r"] = i
            if not {"w", "p"} <= set(hidx):
                header = None
            continue
        if len(cells) <= max(hidx.values()):
            continue
        w = to_float(re.sub(r"[^\d.]", "", cells[hidx["w"]]))
        p = to_float(re.sub(r"[^\d.]", "", cells[hidx["p"]]))
        if np.isnan(w) or np.isnan(p):
            continue
        name = cells[hidx["n"]] if "n" in hidx else f"component {len(comps)+1}"
        rec = True
        if "r" in hidx:
            rec = not any(k in cells[hidx["r"]].lower()
                          for k in ("no", "refus", "fail", "below"))
        comps.append(Component(name, w, p, rec))
    return comps


# ---- camera ---------------------------------------------------------------

@dataclass
class Camera:
    width_px: int = 640
    height_px: int = 480
    hfov_deg: float = 58.0
    vfov_deg: float = 45.0
    name: str = "Asus Xtion PRO Live"

    def mm_per_px(self, distance_m: float) -> float:
        """Lateral millimetres subtended by one pixel at a working distance."""
        span_m = 2.0 * distance_m * np.tan(np.radians(self.hfov_deg) / 2.0)
        return span_m * 1000.0 / self.width_px


def load_camera(root: Path) -> Camera:
    """Read intrinsics from a JSON if you have one, else use the head camera."""
    p = _find(root, "camera.json", "config/camera.json",
              "report_assets/camera.json")
    if p:
        print(f"    reading {p}")
        d = json.loads(p.read_text(encoding="utf-8"))
        return Camera(
            width_px=int(d.get("width", 640)),
            height_px=int(d.get("height", 480)),
            hfov_deg=float(d.get("hfov_deg", 58.0)),
            vfov_deg=float(d.get("vfov_deg", 45.0)),
            name=d.get("name", "head camera"))
    return Camera()


def split_ref(spec: str):
    """Split "file.npz::key" into (Path, key). Plain paths return (Path, None)."""
    s = str(spec).strip()
    if "::" in s:
        p, key = s.split("::", 1)
        return Path(p), key.strip()
    return Path(s), None


def load_array(root: Path, spec: str):
    """Load an array from a plain image, .npy, or an .npz member."""
    p, key = split_ref(spec)
    if not p.is_absolute():
        p = root / p
    if not p.exists():
        raise DataProblem(f"not found: {p}")
    if p.suffix == ".npz":
        z = np.load(p, allow_pickle=False)
        if key is None:
            key = list(z.keys())[0]
        if key not in z:
            raise DataProblem(
                f"{p.name} has no member {key!r}; available: {list(z.keys())}")
        return np.squeeze(z[key])
    if p.suffix == ".npy":
        return np.squeeze(np.load(p, allow_pickle=False))
    from PIL import Image
    return np.array(Image.open(p))


def truthy(v) -> bool:
    return str(v).strip().lower() in ("1", "true", "yes", "y", "t")


def flagged(v) -> bool:
    """
    True when a field carries an actual value.

    vlm_grid_raw.json stores the literal string "null" on one row instead of
    JSON null, so the string has to be treated as absent.
    """
    s = str(v).strip().lower()
    return s not in ("", "null", "none", "nan", "false", "0")


# ---- generic table loader (corrections, constraint map) -------------------

def load_table(root: Path, *relatives, label="table") -> list[dict] | None:
    p = _find(root, *relatives)
    if p is None:
        print(f"    ! no file found for {label}; tried {relatives}")
        return None
    print(f"    reading {p}")
    if p.suffix.lower() == ".json":
        return json.loads(p.read_text(encoding="utf-8"))
    rows = read_csv_tolerant(p)
    if not rows:
        print(f"    ! {p.name} has a header but no data rows")
    return rows


# --------------------------------------------------------------------------
# 4. IMAGE COMPOSITION
#
# Class D figures are photo-anchored: the capture carries object identity, the
# overlay carries the argument. These primitives place real crops onto data
# axes at a controlled physical size, so a figure can be a measurement AND a
# picture rather than choosing between them.
# --------------------------------------------------------------------------

def crop_to(mask, pad_frac=0.28, aspect=None, shape=None):
    """Bounding box around a mask, padded and optionally aspect-matched."""
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    H, W = shape if shape else mask.shape
    cw, ch = xs.max() - xs.min(), ys.max() - ys.min()
    pad = int(round(max(cw, ch) * pad_frac)) + 4
    x0, y0 = max(int(xs.min()) - pad, 0), max(int(ys.min()) - pad, 0)
    x1, y1 = min(int(xs.max()) + pad, W - 1), min(int(ys.max()) + pad, H - 1)
    if aspect:
        cw, ch = x1 - x0 + 1, y1 - y0 + 1
        if cw / ch < aspect:
            tw = int(round(ch * aspect))
            cx = (x0 + x1) // 2
            x0, x1 = max(cx - tw // 2, 0), min(max(cx - tw // 2, 0) + tw - 1, W - 1)
        else:
            th = int(round(cw / aspect))
            cy = (y0 + y1) // 2
            y0, y1 = max(cy - th // 2, 0), min(max(cy - th // 2, 0) + th - 1, H - 1)
    return (x0, y0, x1, y1)


def trim_caption_band(img, max_frac=0.34):
    """
    Strip a burnt-in debug caption band from a rendered crop.

    The pipeline's diagnostic crops carry a pale header strip with tiny text
    naming internal component keys. That text is illegible at figure scale and
    violates Rule 1, so the band is removed before the crop is placed. Rows are
    judged by colour saturation: photo rows are chromatic, caption rows are not.
    """
    a = np.asarray(img)
    if a.ndim != 3 or a.shape[2] < 3:
        return img
    f = a[..., :3].astype(float)
    sat = f.max(axis=2) - f.min(axis=2)          # cheap saturation proxy
    row_sat = sat.mean(axis=1)
    row_lum = f.mean(axis=(1, 2))
    photo = (row_sat > max(4.0, row_sat.max() * 0.18)) | (row_lum < 205)
    if not photo.any():
        return img
    lim = int(len(photo) * max_frac)
    top = 0
    while top < lim and not photo[top]:
        top += 1
    bot = len(photo) - 1
    while bot > len(photo) - 1 - lim and not photo[bot]:
        bot -= 1
    if top == 0 and bot == len(photo) - 1:
        return img
    return a[top:bot + 1]


def data_to_fig(ax, x, y):
    """Data coordinates to figure fraction."""
    disp = ax.transData.transform((x, y))
    return ax.figure.transFigure.inverted().transform(disp)


def image_inset(ax, xy, rgb, w_in=0.90, contours=(), box=None,
                label=None, label_colour=None, anchor="center",
                leader=True, leader_to=None, frame=INK, frame_lw=0.8,
                zorder=20):
    """
    Place a real capture crop on a data axes at a fixed physical width.

    `contours` is a sequence of (mask, colour, linestyle) drawn over the crop
    in crop coordinates, so the overlay stays registered to the pixels. A
    leader line ties the crop back to its anchor point on the plot.

    Returns the child axes so the caller can add further annotation.
    """
    fig = ax.figure
    fx, fy = data_to_fig(ax, *xy)
    if box is not None:
        x0, y0, x1, y1 = box
        sub = rgb[y0:y1 + 1, x0:x1 + 1]
        cnt = [(m[y0:y1 + 1, x0:x1 + 1], c, ls) for m, c, ls in contours]
    else:
        sub, cnt = rgb, list(contours)
    h_in = w_in * sub.shape[0] / sub.shape[1]
    W, H = fig.get_size_inches()
    fw, fh = w_in / W, h_in / H

    ox = {"center": fx - fw / 2, "left": fx, "right": fx - fw}[anchor]
    oy = fy - fh / 2
    ox = float(np.clip(ox, 0.002, 1 - fw - 0.002))
    oy = float(np.clip(oy, 0.002, 1 - fh - 0.002))

    cax = fig.add_axes([ox, oy, fw, fh], zorder=zorder)
    cax.imshow(sub, interpolation="antialiased")
    cax.set_xticks([]); cax.set_yticks([])
    for s in cax.spines.values():
        s.set_edgecolor(frame); s.set_linewidth(frame_lw)
    for m, c, ls in cnt:
        if m is not None and m.any():
            cax.contour(m, levels=[0.5], colors=[c], linewidths=1.3,
                        linestyles=ls)
    if label:
        cax.text(0.5, -0.10, label, transform=cax.transAxes, ha="center",
                 va="top", fontsize=FS_SMALL,
                 color=label_colour or MUTED, linespacing=1.15)
    if leader:
        con = mpl.patches.ConnectionPatch(
            xyA=(leader_to if leader_to is not None else xy),
            coordsA=ax.transData,
            xyB=(0.5, 0.5), coordsB=cax.transAxes,
            color=RULE, linewidth=0.7, zorder=zorder - 1)
        fig.add_artist(con)
    return cax


def hull_2d(points_xy, alpha_frac=0.06):
    """
    Concave-ish hull of a 2-D projected point set, as a closed polygon.

    Used instead of 3-D scatter: a projected cloud with a filled outline stays
    legible at report scale where a perspective scatter turns into a blob.
    Falls back to the convex hull when the alpha shape degenerates.
    """
    from scipy.spatial import Delaunay, ConvexHull
    P = np.asarray(points_xy, float)
    if len(P) < 4:
        return P
    try:
        span = float(np.ptp(P, axis=0).max())
        thr = span * alpha_frac
        tri = Delaunay(P)
        edges = {}
        for s in tri.simplices:
            for a, b in ((s[0], s[1]), (s[1], s[2]), (s[2], s[0])):
                if np.linalg.norm(P[a] - P[b]) > thr:
                    continue
                k = (min(a, b), max(a, b))
                edges[k] = edges.get(k, 0) + 1
        border = [e for e, n in edges.items() if n == 1]
        if len(border) < 3:
            raise ValueError
        adj = {}
        for a, b in border:
            adj.setdefault(a, []).append(b)
            adj.setdefault(b, []).append(a)
        start = border[0][0]
        loop, prev, cur = [start], None, start
        while True:
            nxts = [n for n in adj.get(cur, []) if n != prev]
            if not nxts:
                break
            prev, cur = cur, nxts[0]
            if cur == start:
                break
            loop.append(cur)
            if len(loop) > len(P):
                break
        if len(loop) < 3:
            raise ValueError
        return P[loop]
    except Exception:
        return P[ConvexHull(P).vertices]
