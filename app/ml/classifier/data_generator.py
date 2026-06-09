"""
MEDHA — Synthetic Training Data Generator for BanglaBERT Behavioral Classifier

Generates 5,000 behavioral training examples in JSONL format.
Each example converts behavioral exam signals into a text sequence for fine-tuning
BanglaBERT as a 4-class sequence classifier.

Labels: MASTERY, PRIORITY_FOCUS, TRUST_GAP, GROWTH_AREA

Usage:
    python classifier_data_generator.py
    
Output:
    data/classifier_train.jsonl   (training split — 80%)
    data/classifier_val.jsonl     (validation split — 20%)
"""

import json
import random
import os
from pathlib import Path

# ── Configuration ──
TOTAL_EXAMPLES = 5000
TRAIN_SPLIT = 0.80
RANDOM_SEED = 42
EQUILIBRIUM_SECONDS = 45  # 2025-26 BD medical format: 75min / 100 questions

# ── Topics (Bengali + English mix for bilingual BanglaBERT) ──
TOPICS_BN = [
    "অণুজীব ও ভাইরাস", "অন্তঃক্ষরা তন্ত্র", "ইন্দ্রিয় তন্ত্র", "উদ্ভিদ শরীরতত্ত্ব",
    "উদ্ভিদবিজ্ঞান ও শ্রেণীবিন্যাস", "কঙ্কাল ও পেশী তন্ত্র", "কোষ ও কোষ অঙ্গাণু", "কোষ বিভাজন",
    "জনন তন্ত্র", "জিনতত্ত্ব ও বিবর্তন", "জীবপ্রযুক্তি", "পরিপাক তন্ত্র", "প্রাণীর বিভিন্নতা",
    "বিবিধ ও সাধারণ", "রেচন তন্ত্র", "রোগ প্রতিরোধ ও রক্তের গ্রুপ", "শ্বসন তন্ত্র",
    "সংবহন তন্ত্র", "স্নায়ুতন্ত্র"
]

TOPICS_EN = [
    "Animal Diversity", "Biotechnology", "Cell Division", "Cell Structure & Organelles",
    "Circulatory System", "Digestive System", "Endocrine System", "Excretory System",
    "Genetics & Evolution", "Immunity & Blood Groups", "Microorganisms & Viruses",
    "Miscellaneous", "Nervous System", "Plant Classification", "Plant Physiology",
    "Reproduction", "Respiratory System", "Sense Organs", "Skeletal & Muscular System"
]

DIFFICULTIES = ["easy", "medium", "hard"]
CONFIDENCES = ["sure", "unsure", "guessing"]


def random_topic():
    """Return a random topic — mix of Bengali and English for bilingual training."""
    if random.random() < 0.6:  # 60% Bengali topics
        return random.choice(TOPICS_BN)
    return random.choice(TOPICS_EN)


def generate_mastery_example():
    """
    MASTERY: Student knows it cold.
    - correct=true
    - time_ratio <= 0.5 (answered within half the equilibrium)
    - confidence = sure
    - switches <= 1
    """
    topic = random_topic()
    time_ratio = round(random.uniform(0.05, 0.50), 3)
    switches = random.choices([0, 1], weights=[85, 15])[0]
    confidence = "sure"
    correct = True
    difficulty = random.choices(DIFFICULTIES, weights=[30, 50, 20])[0]

    return _build_example(topic, time_ratio, switches, confidence, correct, difficulty, "MASTERY")


def generate_priority_focus_example():
    """
    PRIORITY_FOCUS: Confidently wrong — most dangerous state.
    - correct=false
    - time_ratio <= 0.6 (answered fast — didn't stop to think)
    - confidence = sure (believed the wrong answer)
    - switches <= 2
    """
    topic = random_topic()
    time_ratio = round(random.uniform(0.05, 0.60), 3)
    switches = random.choices([0, 1, 2], weights=[60, 30, 10])[0]
    confidence = "sure"
    correct = False
    difficulty = random.choices(DIFFICULTIES, weights=[20, 50, 30])[0]

    return _build_example(topic, time_ratio, switches, confidence, correct, difficulty, "PRIORITY_FOCUS")


def generate_trust_gap_example():
    """
    TRUST_GAP: Knows it but doesn't trust themselves.
    - correct=true
    - BUT: slow (time_ratio > 0.5) OR switched answers (>=2) OR not confident
    - At least one uncertainty signal must be present
    """
    topic = random_topic()
    correct = True

    # At least one uncertainty signal
    uncertainty_type = random.choice(["slow", "switched", "unsure", "mixed"])

    if uncertainty_type == "slow":
        time_ratio = round(random.uniform(0.51, 1.0), 3)
        switches = random.choices([0, 1], weights=[60, 40])[0]
        confidence = random.choices(["sure", "unsure"], weights=[40, 60])[0]
    elif uncertainty_type == "switched":
        time_ratio = round(random.uniform(0.20, 0.90), 3)
        switches = random.choices([2, 3, 4], weights=[60, 30, 10])[0]
        confidence = random.choices(CONFIDENCES, weights=[30, 50, 20])[0]
    elif uncertainty_type == "unsure":
        time_ratio = round(random.uniform(0.15, 0.85), 3)
        switches = random.choices([0, 1, 2], weights=[40, 40, 20])[0]
        confidence = random.choices(["unsure", "guessing"], weights=[70, 30])[0]
    else:  # mixed — multiple uncertainty signals
        time_ratio = round(random.uniform(0.50, 1.0), 3)
        switches = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
        confidence = random.choices(["unsure", "guessing"], weights=[60, 40])[0]

    difficulty = random.choices(DIFFICULTIES, weights=[25, 45, 30])[0]

    return _build_example(topic, time_ratio, switches, confidence, correct, difficulty, "TRUST_GAP")


def generate_growth_area_example():
    """
    GROWTH_AREA: Doesn't know it and knows they don't.
    - correct=false
    - slow or uncertain (not confidently wrong — that's PRIORITY_FOCUS)
    - Typically: time_ratio > 0.6, or guessing, or many switches
    """
    topic = random_topic()
    correct = False

    pattern = random.choice(["slow_wrong", "guessing_wrong", "confused_wrong", "expired"])

    if pattern == "slow_wrong":
        time_ratio = round(random.uniform(0.61, 1.0), 3)
        switches = random.choices([0, 1, 2], weights=[40, 35, 25])[0]
        confidence = random.choices(CONFIDENCES, weights=[15, 50, 35])[0]
    elif pattern == "guessing_wrong":
        time_ratio = round(random.uniform(0.10, 0.90), 3)
        switches = random.choices([0, 1, 2, 3], weights=[30, 30, 25, 15])[0]
        confidence = "guessing"
    elif pattern == "confused_wrong":
        time_ratio = round(random.uniform(0.30, 1.0), 3)
        switches = random.choices([2, 3, 4, 5], weights=[35, 35, 20, 10])[0]
        confidence = random.choices(["unsure", "guessing"], weights=[60, 40])[0]
    else:  # expired — ran out of time
        time_ratio = 1.0
        switches = random.choices([0, 1, 2, 3], weights=[25, 30, 25, 20])[0]
        confidence = random.choices(CONFIDENCES, weights=[10, 40, 50])[0]

    difficulty = random.choices(DIFFICULTIES, weights=[15, 40, 45])[0]

    return _build_example(topic, time_ratio, switches, confidence, correct, difficulty, "GROWTH_AREA")


def _build_example(topic, time_ratio, switches, confidence, correct, difficulty, label):
    """Build the text sequence + label pair for training."""
    text = (
        f"Topic: {topic} | "
        f"time_ratio: {time_ratio:.3f} | "
        f"switches: {switches} | "
        f"confidence: {confidence} | "
        f"correct: {str(correct).lower()} | "
        f"difficulty: {difficulty}"
    )
    return {"text": text, "label": label}


def add_boundary_noise(examples):
    """
    Add ~5% boundary cases where signals slightly overlap between classes.
    This makes the model learn fuzzy boundaries instead of hard cutoffs.
    """
    noise_count = int(len(examples) * 0.05)
    noisy_examples = []

    for _ in range(noise_count):
        case_type = random.choice(["mastery_edge", "priority_edge", "trust_edge", "growth_edge"])

        if case_type == "mastery_edge":
            # Fast + correct + sure but RIGHT at the time boundary
            topic = random_topic()
            time_ratio = round(random.uniform(0.45, 0.55), 3)
            noisy_examples.append(_build_example(
                topic, time_ratio, 0, "sure", True,
                random.choice(DIFFICULTIES), "MASTERY"
            ))

        elif case_type == "priority_edge":
            # Wrong + sure but slightly slow — edge between PRIORITY_FOCUS and GROWTH_AREA
            topic = random_topic()
            time_ratio = round(random.uniform(0.55, 0.65), 3)
            noisy_examples.append(_build_example(
                topic, time_ratio, 1, "sure", False,
                random.choice(DIFFICULTIES), "PRIORITY_FOCUS"
            ))

        elif case_type == "trust_edge":
            # Correct + 1 switch — edge between MASTERY and TRUST_GAP
            topic = random_topic()
            time_ratio = round(random.uniform(0.35, 0.55), 3)
            noisy_examples.append(_build_example(
                topic, time_ratio, 1, "unsure", True,
                random.choice(DIFFICULTIES), "TRUST_GAP"
            ))

        else:  # growth_edge
            # Wrong + unsure + moderate time — clear GROWTH_AREA
            topic = random_topic()
            time_ratio = round(random.uniform(0.50, 0.80), 3)
            noisy_examples.append(_build_example(
                topic, time_ratio, 2, "unsure", False,
                random.choice(DIFFICULTIES), "GROWTH_AREA"
            ))

    return noisy_examples


def generate_dataset():
    """Generate the full dataset with balanced distribution."""
    random.seed(RANDOM_SEED)

    # Target distribution: roughly balanced with slight natural skew
    # Real exam data tends to have fewer MASTERY and more GROWTH_AREA
    counts = {
        "MASTERY": int(TOTAL_EXAMPLES * 0.23),          # ~1150
        "PRIORITY_FOCUS": int(TOTAL_EXAMPLES * 0.22),   # ~1100
        "TRUST_GAP": int(TOTAL_EXAMPLES * 0.27),        # ~1350
        "GROWTH_AREA": int(TOTAL_EXAMPLES * 0.28),      # ~1400
    }

    generators = {
        "MASTERY": generate_mastery_example,
        "PRIORITY_FOCUS": generate_priority_focus_example,
        "TRUST_GAP": generate_trust_gap_example,
        "GROWTH_AREA": generate_growth_area_example,
    }

    examples = []
    for label, count in counts.items():
        for _ in range(count):
            examples.append(generators[label]())

    # Add boundary noise
    noise = add_boundary_noise(examples)
    examples.extend(noise)

    # Shuffle
    random.shuffle(examples)

    return examples


def save_dataset(examples):
    """Split and save to JSONL files."""
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)

    split_idx = int(len(examples) * TRAIN_SPLIT)
    train_data = examples[:split_idx]
    val_data = examples[split_idx:]

    train_file = data_dir / "classifier_train.jsonl"
    val_file = data_dir / "classifier_val.jsonl"

    with open(train_file, "w", encoding="utf-8") as f:
        for ex in train_data:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    with open(val_file, "w", encoding="utf-8") as f:
        for ex in val_data:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    return train_file, val_file, len(train_data), len(val_data)


def print_stats(examples):
    """Print distribution statistics."""
    from collections import Counter
    label_counts = Counter(ex["label"] for ex in examples)
    total = len(examples)

    print(f"\n{'='*60}")
    print(f"  MEDHA Classifier Training Data Generator")
    print(f"{'='*60}")
    print(f"\n  Total examples: {total}")
    print(f"  Equilibrium: {EQUILIBRIUM_SECONDS}s per question")
    print(f"\n  Label Distribution:")
    for label in ["MASTERY", "PRIORITY_FOCUS", "TRUST_GAP", "GROWTH_AREA"]:
        count = label_counts[label]
        pct = count / total * 100
        bar = "#" * int(pct / 2)
        print(f"    {label:20s} {count:5d} ({pct:5.1f}%) {bar}")

    # Skip sample printing — Bengali text crashes Windows cp1252 console
    # Data files save correctly with UTF-8 encoding


if __name__ == "__main__":
    examples = generate_dataset()
    print_stats(examples)

    train_file, val_file, train_count, val_count = save_dataset(examples)

    print(f"  Files saved:")
    print(f"    Train: {train_file} ({train_count} examples)")
    print(f"    Val:   {val_file} ({val_count} examples)")
    print(f"{'='*60}\n")
