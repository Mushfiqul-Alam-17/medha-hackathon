"""
MEDHA — Scoring Service
Calculates raw score, negative marking, skip coach analysis, and readiness score.
Pure math — no external dependencies.
"""

from typing import List, Dict, Any


def calculate_scoring(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate exam scoring with negative marking and skip coach.
    
    BD Medical Admission rules:
    - +1 per correct answer
    - -0.25 per wrong answer
    - 0 for skipped
    """
    total = len(results)
    correct = sum(1 for r in results if r.get("is_correct") and not r.get("skipped"))
    wrong = sum(1 for r in results if not r.get("is_correct") and not r.get("skipped") and not r.get("time_expired"))
    skipped = sum(1 for r in results if r.get("skipped") or r.get("time_expired"))

    raw_score = correct
    negative_deduction = round(wrong * 0.25, 2)
    final_score = round(raw_score - negative_deduction, 2)

    # Skip coach: identify risky attempts
    # A risky attempt = wrong answer where student was guessing OR switched a lot
    risky = [
        r for r in results
        if not r.get("is_correct")
        and not r.get("skipped")
        and not r.get("time_expired")
        and (
            r.get("confidence_tap") == "guessing"
            or len(r.get("click_path", [])) - 1 >= 2
        )
    ]

    potential_saving = round(len(risky) * 0.25, 2)

    return {
        "total": total,
        "correct": correct,
        "wrong": wrong,
        "skipped": skipped,
        "raw_score": raw_score,
        "negative_deduction": negative_deduction,
        "final_score": final_score,
        "risky_attempts": len(risky),
        "potential_saving": potential_saving,
        "skip_coach_score": round(final_score + potential_saving, 2),
        "accuracy": round(correct / max(total - skipped, 1) * 100, 1),
    }


def calculate_readiness(groups: Dict[str, list]) -> int:
    """
    Calculate readiness score (0-100) from behavioral group distribution.
    
    Weights:
    - MASTERY: 1.00 (fully prepared)
    - TRUST_GAP: 0.55 (knows it, needs confidence)
    - PRIORITY_FOCUS: 0.15 (dangerous — thinks they know but don't)
    - GROWTH_AREA: 0.05 (needs study, at least aware of gap)
    """
    total = sum(len(v) for v in groups.values())
    if total == 0:
        return 0

    weighted = (
        len(groups.get("MASTERY", [])) * 1.00
        + len(groups.get("TRUST_GAP", [])) * 0.55
        + len(groups.get("PRIORITY_FOCUS", [])) * 0.15
        + len(groups.get("GROWTH_AREA", [])) * 0.05
    )
    return round((weighted / total) * 100)


def build_dna_groups(classified_results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group classified results into the 4 behavioral DNA buckets."""
    groups = {
        "MASTERY": [],
        "PRIORITY_FOCUS": [],
        "TRUST_GAP": [],
        "GROWTH_AREA": [],
    }
    for r in classified_results:
        label = r.get("classifier_label", "GROWTH_AREA")
        if label in groups:
            groups[label].append(r)
        else:
            groups["GROWTH_AREA"].append(r)
    return groups
