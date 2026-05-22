#!/usr/bin/env python3
import json
import sys
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / ".cache" / "type_chart.json"

BUCKETS = [
    (2.50,  99,   "2.56x  double SE"),
    (1.55,  2.50, "1.6x   SE"),
    (0.95,  1.55, "1.0x   neutral"),
    (0.50,  0.95, "0.625x NVE"),
    (0.35,  0.50, "0.39x  immune / double NVE"),
    (0.00,  0.35, "0.24x  triple resist"),
]

def bucket_label(mult):
    for lo, hi, label in BUCKETS:
        if lo < mult <= hi:
            return label
    return f"{mult:.3f}x"

def main():
    if len(sys.argv) < 2:
        print("Usage: query_types.py <type1> [type2]")
        sys.exit(1)

    types = [t.lower() for t in sys.argv[1:3]]

    with open(DATA_FILE) as f:
        data = json.load(f)
    chart = data["chart"]
    all_types = list(chart.keys())

    for t in types:
        if t not in all_types:
            print(f"Unknown type: {t}. Valid: {', '.join(sorted(all_types))}")
            sys.exit(1)

    label = " / ".join(t.upper() for t in types)

    # Defender perspective — combined dual type
    print(f"\n{'='*50}")
    print(f"  {label} — DEFENDER")
    print(f"{'='*50}")
    matchups = {}
    for atk in all_types:
        mult = 1.0
        for t in types:
            mult *= chart.get(atk, {}).get(t, 1.0)
        matchups[atk] = round(mult, 6)

    groups = {}
    for atk, mult in matchups.items():
        lbl = bucket_label(mult)
        groups.setdefault(lbl, []).append(atk)

    for _, _, lbl in BUCKETS:
        if lbl in groups and "neutral" not in lbl:
            print(f"  {lbl}: {', '.join(sorted(groups[lbl]))}")
    if "1.0x   neutral" in groups:
        print(f"  1.0x   neutral: {', '.join(sorted(groups['1.0x   neutral']))}")

    # Attacker perspective — one block per type
    for t in types:
        print(f"\n{'='*50}")
        print(f"  {t.upper()} — ATTACKER")
        print(f"{'='*50}")
        se    = sorted(d for d, m in chart.get(t, {}).items() if m > 1.0)
        nve   = sorted(d for d, m in chart.get(t, {}).items() if 0.4 < m < 1.0)
        immun = sorted(d for d, m in chart.get(t, {}).items() if m <= 0.4)
        neutral = sorted(d for d in all_types
                         if d not in chart.get(t, {}) )

        if se:    print(f"  1.6x   SE:      {', '.join(se)}")
        if nve:   print(f"  0.625x NVE:     {', '.join(nve)}")
        if immun: print(f"  0.39x  immune:  {', '.join(immun)}")
        print(f"  1.0x   neutral: {', '.join(neutral)}")

if __name__ == "__main__":
    main()
