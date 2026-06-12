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
TOTAL_EXAMPLES = 10000
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
    - time_ratio <= 0.8 (answered within normal/slightly extended thinking time)
    - confidence = sure (believed the wrong answer)
    - switches <= 2 (decisive)
    """
    topic = random_topic()
    time_ratio = round(random.uniform(0.05, 0.80), 3)
    switches = random.choices([0, 1, 2], weights=[60, 30, 10])[0]
    confidence = "sure"
    correct = False
    difficulty = random.choices(DIFFICULTIES, weights=[20, 50, 30])[0]

    return _build_example(topic, time_ratio, switches, confidence, correct, difficulty, "PRIORITY_FOCUS")


def generate_trust_gap_example():
    """
    TRUST_GAP: Knows it but doesn't trust themselves.
    - correct=true
    - Either:
      - confidence = "sure" + (slow (time_ratio > 0.5) OR switched (switches >= 2))
      - OR confidence = "unsure"
    - Excludes confidence = "guessing" (which represents a lucky guess/GROWTH_AREA)
    """
    topic = random_topic()
    correct = True
    difficulty = random.choices(DIFFICULTIES, weights=[25, 45, 30])[0]

    pattern = random.choice(["slow_sure", "switched_sure", "unsure"])
    if pattern == "slow_sure":
        time_ratio = round(random.uniform(0.51, 1.0), 3)
        switches = random.choices([0, 1], weights=[65, 35])[0]
        confidence = "sure"
    elif pattern == "switched_sure":
        time_ratio = round(random.uniform(0.20, 0.90), 3)
        switches = random.choices([2, 3, 4], weights=[60, 35, 5])[0]
        confidence = "sure"
    else:  # unsure
        time_ratio = round(random.uniform(0.10, 0.90), 3)
        switches = random.choices([0, 1, 2], weights=[45, 45, 10])[0]
        confidence = "unsure"

    return _build_example(topic, time_ratio, switches, confidence, correct, difficulty, "TRUST_GAP")


def generate_growth_area_example():
    """
    GROWTH_AREA: Lacks knowledge & knows it / Lucky guess.
    - Case A: Incorrect + unconfident (unsure/guessing)
    - Case B: Incorrect + slow/undecisive (even if "sure")
    - Case C: Expired time
    - Case D: Lucky Guess (correct but guessing)
    """
    topic = random_topic()
    difficulty = random.choices(DIFFICULTIES, weights=[15, 40, 45])[0]

    pattern = random.choice(["wrong_unconfident", "wrong_slow_undecisive", "wrong_expired", "lucky_guess"])
    if pattern == "wrong_unconfident":
        correct = False
        time_ratio = round(random.uniform(0.10, 0.95), 3)
        switches = random.choices([0, 1, 2], weights=[45, 45, 10])[0]
        confidence = random.choice(["unsure", "guessing"])
    elif pattern == "wrong_slow_undecisive":
        correct = False
        if random.random() < 0.5:
            time_ratio = round(random.uniform(0.81, 1.0), 3)
            switches = random.choices([0, 1, 2], weights=[40, 40, 20])[0]
        else:
            time_ratio = round(random.uniform(0.10, 0.90), 3)
            switches = random.choices([3, 4, 5], weights=[60, 30, 10])[0]
        confidence = "sure"
    elif pattern == "wrong_expired":
        correct = False
        time_ratio = 1.0
        switches = random.choices([0, 1, 2, 3], weights=[30, 30, 25, 15])[0]
        confidence = random.choice(CONFIDENCES)
    else:  # lucky_guess
        correct = True
        time_ratio = round(random.uniform(0.15, 1.0), 3)
        switches = random.choices([0, 1, 2, 3, 4], weights=[20, 30, 30, 15, 5])[0]
        confidence = "guessing"

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
            time_ratio = round(random.uniform(0.48, 0.52), 3)
            noisy_examples.append(_build_example(
                topic, time_ratio, 1, "sure", True,
                random.choice(DIFFICULTIES), "MASTERY"
            ))

        elif case_type == "priority_edge":
            # Wrong + sure but slightly slow — edge between PRIORITY_FOCUS and GROWTH_AREA
            topic = random_topic()
            time_ratio = round(random.uniform(0.75, 0.85), 3)
            noisy_examples.append(_build_example(
                topic, time_ratio, 2, "sure", False,
                random.choice(DIFFICULTIES), "PRIORITY_FOCUS"
            ))

        elif case_type == "trust_edge":
            # Correct + 1 switch — edge between MASTERY and TRUST_GAP
            topic = random_topic()
            time_ratio = round(random.uniform(0.40, 0.60), 3)
            noisy_examples.append(_build_example(
                topic, time_ratio, 1, "unsure", True,
                random.choice(DIFFICULTIES), "TRUST_GAP"
            ))

        else:  # growth_edge
            # Correct + guessing but very fast — edge between lucky guess and mastery/trust gap
            topic = random_topic()
            time_ratio = round(random.uniform(0.10, 0.30), 3)
            noisy_examples.append(_build_example(
                topic, time_ratio, 0, "guessing", True,
                random.choice(DIFFICULTIES), "GROWTH_AREA"
            ))

    return noisy_examples


def generate_dataset():
    """Generate the full dataset with balanced distribution."""
    random.seed(RANDOM_SEED)

    # Target distribution: roughly balanced with slight natural skew
    # Real exam data tends to have fewer MASTERY and more GROWTH_AREA
    counts = {
        "MASTERY": int(TOTAL_EXAMPLES * 0.23),          # ~2300
        "PRIORITY_FOCUS": int(TOTAL_EXAMPLES * 0.22),   # ~2200
        "TRUST_GAP": int(TOTAL_EXAMPLES * 0.27),        # ~2700
        "GROWTH_AREA": int(TOTAL_EXAMPLES * 0.28),      # ~2800
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
    """Split and save to JSONL files in both ml/classifier/data/ and ml/kaggle_dataset/."""
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    kaggle_dir = Path(__file__).parent.parent / "kaggle_dataset"
    kaggle_dir.mkdir(exist_ok=True)

    split_idx = int(len(examples) * TRAIN_SPLIT)
    train_data = examples[:split_idx]
    val_data = examples[split_idx:]

    train_file = data_dir / "classifier_train.jsonl"
    val_file = data_dir / "classifier_val.jsonl"
    
    kaggle_train = kaggle_dir / "classifier_train.jsonl"
    kaggle_val = kaggle_dir / "classifier_val.jsonl"

    for path in [train_file, kaggle_train]:
        with open(path, "w", encoding="utf-8") as f:
            for ex in train_data:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    for path in [val_file, kaggle_val]:
        with open(path, "w", encoding="utf-8") as f:
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
