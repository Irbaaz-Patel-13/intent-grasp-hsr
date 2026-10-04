#!/usr/bin/env python3
r"""log_trial.py -- turn an executor run into one row of the results table.

Usage (workstation):
    python3 execute_place_grasp_raw.py ...args... 2>&1 | tee /tmp/trial.txt
    python3 log_trial.py /tmp/trial.txt --note "servo aligned, hand-placed=no"

Appends to trials.csv and prints the running success rate. The dissertation's
hardware results table is then a direct export of trials.csv rather than an
archaeology exercise over terminal scrollback.

Captured per trial: gates (G1/G2/G3), the constraint-derived policy actually
used, the contact-stop outcome (contact vs floor = empty), whether the lift
trajectory executed, and the final verdict -- including the distinction between
"grasp failed" and "grasp held but lift was dropped by a controller fault",
which the executor's own RESULT line conflates.
"""
import argparse, csv, os, re, sys
from datetime import datetime

CSV = "trials.csv"
FIELDS = ["timestamp", "grasp", "verdict", "held", "z_rise_m", "hand_motor",
          "contact_pos", "stop_reason", "lift_commanded", "lift_reached",
          "lift_executed", "close_params", "force_level", "cage_motor",
          "close_z", "hold_margin", "g1_xy", "g2_pos_err", "g2_ori_deg",
          "servo_used", "note"]


def grab(pat, text, group=1, cast=str, default=""):
    m = re.search(pat, text)
    if not m:
        return default
    try:
        return cast(m.group(group))
    except (ValueError, IndexError):
        return default


def parse(text):
    r = {f: "" for f in FIELDS}
    r["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    r["grasp"] = grab(r"grasp (\d+): B\*_rel", text)
    r["close_params"] = grab(r"--close_params\s+(\S+)", text) or "close_params.csv"

    # policy actually applied
    r["force_level"] = grab(r"\[policy\] force=(\S+)", text)
    r["cage_motor"] = grab(r"cage_motor=([\d.\-]+)", text)
    r["close_z"] = grab(r"close_z=([\d.\-]+)", text)
    r["hold_margin"] = grab(r"margin ([\d.\-]+)\)", text)

    # gates
    r["g1_xy"] = grab(r"G1 base-settled: \w+ \{'arrived_xy': ([\d.\-]+)", text)
    r["g2_pos_err"] = grab(r"G2 palm_err: \w+ \{'pos_err_m': ([\d.\-]+)", text)
    r["g2_ori_deg"] = grab(r"'ori_err_deg': ([\d.\-]+)", text)

    # contact-stop outcome
    r["stop_reason"] = grab(r"\[close\] stop reason=(\w+)", text)
    r["contact_pos"] = grab(r"holding at measured ([+\-][\d.]+)", text)

    # lift execution (the fault signature)
    lc = grab(r"lift execution: arm_lift ([\d.]+) -> ([\d.]+) \(commanded ([\d.]+)\)",
              text, group=3)
    l0 = grab(r"lift execution: arm_lift ([\d.]+) ->", text, group=1)
    l1 = grab(r"lift execution: arm_lift [\d.]+ -> ([\d.]+)", text, group=1)
    r["lift_commanded"], r["lift_reached"] = lc, l1
    if l0 and l1:
        r["lift_executed"] = "yes" if abs(float(l1) - float(l0)) > 0.01 else "NO"

    # G3
    r["z_rise_m"] = grab(r"'z_rise_m': ([\d.\-]+)", text)
    r["hand_motor"] = grab(r"'hand_motor': ([\d.\-]+)", text)
    r["held"] = grab(r"'held': (True|False)", text)

    # verdict, disambiguated
    if "GRASP OK" in text:
        r["verdict"] = "GRASP_OK"
    elif r["held"] == "True" and r["lift_executed"] == "NO":
        r["verdict"] = "HELD_LIFT_FAULT"       # grasp succeeded, controller faulted
    elif r["stop_reason"] == "floor":
        r["verdict"] = "EMPTY_NO_CONTACT"      # closed on air = alignment miss
    elif "ABORT" in text:
        r["verdict"] = "ABORT_" + grab(r"ABORT ?(\w+)", text)
    else:
        r["verdict"] = "FAILED_OTHER"
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logfile")
    ap.add_argument("--note", default="")
    ap.add_argument("--servo", choices=["yes", "no"], default="")
    ap.add_argument("--csv", default=CSV)
    a = ap.parse_args()

    if not os.path.exists(a.logfile):
        sys.exit("no such log: %s" % a.logfile)
    row = parse(open(a.logfile, encoding="utf-8", errors="replace").read())
    row["note"] = a.note
    row["servo_used"] = a.servo

    new = not os.path.exists(a.csv)
    with open(a.csv, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)

    print("logged: grasp=%s verdict=%s held=%s z_rise=%s contact=%s lift_exec=%s"
          % (row["grasp"], row["verdict"], row["held"], row["z_rise_m"],
             row["contact_pos"], row["lift_executed"]))

    rows = list(csv.DictReader(open(a.csv)))
    ok = sum(1 for x in rows if x["verdict"] == "GRASP_OK")
    grasped = sum(1 for x in rows if x["held"] == "True")
    print("\n--- %s: %d trials ---" % (a.csv, len(rows)))
    print("  full success (grasp + verified lift) : %d/%d" % (ok, len(rows)))
    print("  object secured in gripper            : %d/%d" % (grasped, len(rows)))
    from collections import Counter
    for v, n in Counter(x["verdict"] for x in rows).most_common():
        print("    %-18s %d" % (v, n))


if __name__ == "__main__":
    main()
