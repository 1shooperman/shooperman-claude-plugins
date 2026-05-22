#!/usr/bin/env python3
"""Generate a random type matchup quiz question from type_chart.json."""
import json
import random
import sys
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent.parent / "type-chart" / ".cache" / "type_chart.json"

def load_chart():
    with open(DATA_FILE) as f:
        return json.load(f)["chart"]

def get_mult(chart, atk, dfn):
    return chart.get(atk, {}).get(dfn, 1.0)

def dual_defender_mult(chart, atk, types):
    m = 1.0
    for t in types:
        m *= get_mult(chart, atk, t)
    return round(m, 6)

def fmt_mult(m):
    if m > 2.5:   return "2.56x (double SE)"
    if m > 1.5:   return "1.6x (SE)"
    if m > 0.9:   return "1.0x (neutral)"
    if m > 0.45:  return "0.625x (NVE)"
    if m > 0.3:   return "0.39x (double NVE / immune)"
    return f"{m:.3f}x (triple resist)"

def q_single_matchup(chart, all_types):
    """What multiplier does X hit Y for?"""
    atk = random.choice(all_types)
    dfn = random.choice(all_types)
    mult = get_mult(chart, atk, dfn)
    return {
        "question": f"What multiplier does a {atk.upper()} move hit a {dfn.upper()} type defender for?",
        "answer": fmt_mult(mult),
        "mult": mult,
        "explanation": f"{atk.upper()} vs {dfn.upper()} = {fmt_mult(mult)} in Pokemon GO."
    }

def q_dual_defender(chart, all_types):
    """What multiplier does X hit Y/Z for?"""
    atk = random.choice(all_types)
    t1, t2 = random.sample(all_types, 2)
    mult = dual_defender_mult(chart, atk, [t1, t2])
    return {
        "question": f"Opponent has a {t1.upper()}/{t2.upper()} type Pokemon. You throw a {atk.upper()} move. What's the multiplier?",
        "answer": fmt_mult(mult),
        "mult": mult,
        "explanation": (
            f"{atk.upper()} vs {t1.upper()} = {fmt_mult(get_mult(chart, atk, t1))}, "
            f"vs {t2.upper()} = {fmt_mult(get_mult(chart, atk, t2))}. "
            f"Combined: {fmt_mult(mult)}."
        )
    }

def q_list_se_attackers(chart, all_types):
    """What types hit X for SE?"""
    dfn = random.choice(all_types)
    se = sorted(atk for atk in all_types if get_mult(chart, atk, dfn) > 1.5)
    return {
        "question": f"Name all types that hit {dfn.upper()} for SE (1.6x) damage.",
        "answer": ", ".join(se) if se else "none",
        "mult": None,
        "explanation": f"Types SE vs {dfn.upper()}: {', '.join(se) if se else 'none'}."
    }

def q_double_weakness(chart, all_types):
    """What's the double weakness of type combo X/Y?"""
    t1, t2 = random.sample(all_types, 2)
    double_weak = sorted(
        atk for atk in all_types
        if dual_defender_mult(chart, atk, [t1, t2]) > 2.5
    )
    if not double_weak:
        # fallback — no double weakness on this combo, retry with different q
        return q_dual_defender(chart, all_types)
    return {
        "question": f"What type(s) hit {t1.upper()}/{t2.upper()} for double SE (2.56x)?",
        "answer": ", ".join(double_weak),
        "mult": None,
        "explanation": f"Both {t1.upper()} and {t2.upper()} are weak to {', '.join(double_weak)}, so combined = 2.56x."
    }

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else None
    if seed is not None:
        random.seed(seed)

    chart = load_chart()
    all_types = list(chart.keys())

    generators = [
        q_single_matchup,
        q_dual_defender,
        q_dual_defender,   # weighted heavier — more relevant in-game
        q_list_se_attackers,
        q_double_weakness,
    ]

    q = random.choice(generators)(chart, all_types)
    print(json.dumps(q, indent=2))

if __name__ == "__main__":
    main()
