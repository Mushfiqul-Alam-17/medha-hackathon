"""
MEDHA — BanglaBERT Behavioral Classifier Training Script (FIXED v2)
==========================================================
Run on Kaggle Notebook with GPU T4 x2

Changes from v1:
- Removed unnecessary QLoRA (BanglaBERT is 180M, fits T4 for full fine-tuning)
- Fixed deprecated evaluation_strategy → eval_strategy
- Changed metric_for_best_model to f1_weighted
- Added EarlyStoppingCallback
- Cleaner push logic

Instructions:
1. New Kaggle notebook → Settings → GPU T4 x2 → Internet ON
2. Upload classifier_train.jsonl + classifier_val.jsonl as a dataset
   (named: medha-classifier-data)
3. Add your HF_TOKEN as a Kaggle Secret (Secrets tab)
4. Paste entire script into a single cell and run

Expected training time: 60-90 minutes
Target: accuracy > 80%, f1_weighted > 0.80
"""

# ── CELL 1: Install ────────────────────────────────────────────────────────────
import subprocess
subprocess.run([
    "pip", "install", "-q",
    "transformers==4.44.0",   # pin version for stability
    "datasets", "evaluate",
    "scikit-learn", "accelerate"
])

import os, json, numpy as np
from pathlib import Path

# ── CONFIGURATION ─────────────────────────────────────────────────────────────
# !! UPDATE THESE BEFORE RUNNING !!
HF_USERNAME  = "YOUR_HF_USERNAME"
HF_TOKEN     = "YOUR_HF_TOKEN"        # better: use Kaggle Secrets
MODEL_NAME   = "medha-behavioral-classifier-v1"

BASE_MODEL   = "csebuetnlp/banglabert"
NUM_LABELS   = 4

LABEL2ID = {
    "MASTERY":        0,
    "PRIORITY_FOCUS": 1,
    "TRUST_GAP":      2,
    "GROWTH_AREA":    3,
}
ID2LABEL = {v: k for k, v in LABEL2ID.items()}

# Hyperparameters
EPOCHS      = 10          # more epochs, early stopping will cut off when needed
BATCH_SIZE  = 32          # T4 x2 can handle 32 for a 180M model
LR          = 2e-5        # standard BERT fine-tuning rate
MAX_LENGTH  = 128         # our inputs are ~29 tokens, 128 is safe ceiling
SEED        = 42

# ── CELL 2: HuggingFace Login ──────────────────────────────────────────────────
from huggingface_hub import login

# If using Kaggle Secrets:
# from kaggle_secrets import UserSecretsClient
# HF_TOKEN = UserSecretsClient().get_secret("HF_TOKEN")

login(token=HF_TOKEN)
print("Logged in to HuggingFace ✅")

# ── CELL 3: Load Data ──────────────────────────────────────────────────────────
from datasets import Dataset
import torch

torch.manual_seed(SEED)
np.random.seed(SEED)

def load_jsonl(filepath):
    data = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line.strip())
            item["label"] = LABEL2ID[item["label"]]
            data.append(item)
    return data

# Kaggle dataset path
TRAIN_PATH = "/kaggle/input/medha-classifier-data/classifier_train.jsonl"
VAL_PATH   = "/kaggle/input/medha-classifier-data/classifier_val.jsonl"

# Local fallback
if not os.path.exists(TRAIN_PATH):
    TRAIN_PATH = "classifier_train.jsonl"
    VAL_PATH   = "classifier_val.jsonl"

train_data = load_jsonl(TRAIN_PATH)
val_data   = load_jsonl(VAL_PATH)

train_dataset = Dataset.from_list(train_data)
val_dataset   = Dataset.from_list(val_data)

from collections import Counter
print(f"Train: {len(train_dataset)} | Val: {len(val_dataset)}")
print("Label distribution (train):")
for label, count in sorted(Counter(d['label'] for d in train_data).items()):
    print(f"  {ID2LABEL[label]:<25} {count} ({count/len(train_data)*100:.1f}%)")

# ── CELL 4: Tokenize ───────────────────────────────────────────────────────────
from transformers import AutoTokenizer

print(f"\nLoading tokenizer: {BASE_MODEL}")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

def tokenize_fn(examples):
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=MAX_LENGTH,
    )

train_dataset = train_dataset.map(tokenize_fn, batched=True, remove_columns=["text"])
val_dataset   = val_dataset.map(tokenize_fn,   batched=True, remove_columns=["text"])

train_dataset.set_format("torch")
val_dataset.set_format("torch")

# Verify
sample = train_dataset[0]
print(f"Sample input_ids length: {len(sample['input_ids'])}")
print(f"Sample label: {sample['label']} ({ID2LABEL[sample['label'].item()]})")

# ── CELL 5: Load Model — FULL FINE-TUNING, no QLoRA ───────────────────────────
from transformers import AutoModelForSequenceClassification

print(f"\nLoading {BASE_MODEL} for full fine-tuning...")
print("(No QLoRA — BanglaBERT at 180M fits T4 easily)")

model = AutoModelForSequenceClassification.from_pretrained(
    BASE_MODEL,
    num_labels=NUM_LABELS,
    id2label=ID2LABEL,
    label2id=LABEL2ID,
    ignore_mismatched_sizes=True,  # classifier head is new
)

model = model.cuda()

total_params     = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total params:     {total_params:,}")
print(f"Trainable params: {trainable_params:,}  (all of them — full fine-tuning)")
print(f"GPU: {torch.cuda.get_device_name(0)}")

# ── CELL 6: Metrics ────────────────────────────────────────────────────────────
import evaluate
from sklearn.metrics import classification_report

accuracy_metric = evaluate.load("accuracy")
f1_metric       = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions    = np.argmax(logits, axis=-1)

    acc  = accuracy_metric.compute(predictions=predictions, references=labels)["accuracy"]
    f1w  = f1_metric.compute(predictions=predictions, references=labels, average="weighted")["f1"]
    f1m  = f1_metric.compute(predictions=predictions, references=labels, average="macro")["f1"]
    f1pc = f1_metric.compute(predictions=predictions, references=labels, average=None)["f1"]

    return {
        "accuracy":           round(acc, 4),
        "f1_weighted":        round(f1w, 4),
        "f1_macro":           round(f1m, 4),
        "f1_MASTERY":         round(f1pc[0], 4),
        "f1_PRIORITY_FOCUS":  round(f1pc[1], 4),
        "f1_TRUST_GAP":       round(f1pc[2], 4),
        "f1_GROWTH_AREA":     round(f1pc[3], 4),
    }

# ── CELL 7: Training Args ──────────────────────────────────────────────────────
from transformers import TrainingArguments, Trainer, EarlyStoppingCallback, DataCollatorWithPadding

training_args = TrainingArguments(
    output_dir                  = "./medha-classifier-output",
    num_train_epochs            = EPOCHS,
    per_device_train_batch_size = BATCH_SIZE,
    per_device_eval_batch_size  = 64,
    learning_rate               = LR,
    weight_decay                = 0.01,
    warmup_ratio                = 0.1,

    # FIXED: use eval_strategy not evaluation_strategy
    eval_strategy               = "epoch",
    save_strategy               = "epoch",

    # FIXED: use f1_weighted not accuracy for best model selection
    load_best_model_at_end      = True,
    metric_for_best_model       = "f1_weighted",
    greater_is_better           = True,
    save_total_limit            = 2,

    logging_steps               = 50,
    fp16                        = True,
    dataloader_num_workers      = 2,
    seed                        = SEED,
    report_to                   = "none",
)

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

trainer = Trainer(
    model           = model,
    args            = training_args,
    train_dataset   = train_dataset,
    eval_dataset    = val_dataset,
    tokenizer       = tokenizer,
    data_collator   = data_collator,
    compute_metrics = compute_metrics,
    # FIXED: Added early stopping — stops if f1_weighted doesn't improve for 3 epochs
    callbacks       = [EarlyStoppingCallback(early_stopping_patience=3)],
)

# ── CELL 8: TRAIN ──────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STARTING TRAINING")
print(f"Model:      {BASE_MODEL} (full fine-tuning)")
print(f"Train size: {len(train_dataset)}")
print(f"Val size:   {len(val_dataset)}")
print(f"Epochs:     {EPOCHS} (with early stopping, patience=3)")
print(f"Batch:      {BATCH_SIZE} per device × {torch.cuda.device_count()} GPUs")
print(f"LR:         {LR}")
print("="*60 + "\n")

train_result = trainer.train()

print(f"\nTraining complete!")
print(f"Runtime:    {train_result.metrics['train_runtime']/60:.1f} minutes")
print(f"Train loss: {train_result.metrics['train_loss']:.4f}")

# ── CELL 9: Full Evaluation ────────────────────────────────────────────────────
eval_results = trainer.evaluate()

print("\n" + "="*60)
print("VALIDATION RESULTS")
print("="*60)
print(f"  Accuracy:         {eval_results['eval_accuracy']:.4f}")
print(f"  F1 Weighted:      {eval_results['eval_f1_weighted']:.4f}")
print(f"  F1 Macro:         {eval_results['eval_f1_macro']:.4f}")
print(f"\n  Per-class F1:")
print(f"  MASTERY:          {eval_results['eval_f1_MASTERY']:.4f}")
print(f"  PRIORITY_FOCUS:   {eval_results['eval_f1_PRIORITY_FOCUS']:.4f}")
print(f"  TRUST_GAP:        {eval_results['eval_f1_TRUST_GAP']:.4f}")
print(f"  GROWTH_AREA:      {eval_results['eval_f1_GROWTH_AREA']:.4f}")

# Detailed report + confusion matrix
preds_output = trainer.predict(val_dataset)
preds  = np.argmax(preds_output.predictions, axis=-1)
labels = preds_output.label_ids

print("\nClassification Report:")
print(classification_report(labels, preds, target_names=list(LABEL2ID.keys()), digits=4))

from sklearn.metrics import confusion_matrix
cm = confusion_matrix(labels, preds)
print("Confusion Matrix (row=true, col=pred):")
header = f"{'':>20}" + "".join(f"{n:>16}" for n in LABEL2ID.keys())
print(header)
for i, name in enumerate(LABEL2ID.keys()):
    row = f"{name:>20}" + "".join(f"{cm[i][j]:>16}" for j in range(NUM_LABELS))
    print(row)

# Quality gate
acc = eval_results['eval_accuracy']
if acc >= 0.85:
    print(f"\n✅ EXCELLENT — {acc:.1%} accuracy. Ready for production.")
elif acc >= 0.80:
    print(f"\n✅ GOOD — {acc:.1%} accuracy. Ready for MVP.")
elif acc >= 0.75:
    print(f"\n⚡ ACCEPTABLE — {acc:.1%}. Check PRIORITY_FOCUS F1 specifically.")
else:
    print(f"\n❌ BELOW TARGET — {acc:.1%}. Check data distribution and rerun.")

# ── CELL 10: Manual Test Cases ─────────────────────────────────────────────────
print("\n" + "="*60)
print("MANUAL TEST CASES")
print("="*60)

test_cases = [
    {
        "text":     "Topic: Cell Division | time_ratio: 0.180 | switches: 0 | confidence: sure | correct: true | difficulty: medium",
        "expected": "MASTERY",
        "desc":     "Fast + correct + confident → MASTERY"
    },
    {
        "text":     "Topic: স্নায়ুতন্ত্র | time_ratio: 0.220 | switches: 0 | confidence: sure | correct: false | difficulty: medium",
        "expected": "PRIORITY_FOCUS",
        "desc":     "Fast + confident + WRONG → PRIORITY_FOCUS"
    },
    {
        "text":     "Topic: Genetics & Evolution | time_ratio: 1.450 | switches: 3 | confidence: unsure | correct: true | difficulty: hard",
        "expected": "TRUST_GAP",
        "desc":     "Slow + hesitant + correct → TRUST_GAP"
    },
    {
        "text":     "Topic: Digestive System | time_ratio: 2.800 | switches: 4 | confidence: guessing | correct: false | difficulty: hard",
        "expected": "GROWTH_AREA",
        "desc":     "Very slow + guessing + wrong → GROWTH_AREA"
    },
]

from transformers import pipeline
classifier_pipeline = pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    device=0,
    top_k=None,
)

all_pass = True
for tc in test_cases:
    result = classifier_pipeline(tc["text"])[0]
    result_sorted = sorted(result, key=lambda x: x['score'], reverse=True)
    predicted = result_sorted[0]["label"]
    confidence = result_sorted[0]["score"]
    passed = predicted == tc["expected"]
    all_pass = all_pass and passed
    status = "✅" if passed else "❌"
    print(f"\n{status} {tc['desc']}")
    print(f"   Expected:  {tc['expected']}")
    print(f"   Predicted: {predicted} ({confidence:.1%})")
    if not passed:
        for r in result_sorted:
            print(f"   {r['label']:<25} {r['score']:.3f}")

print(f"\n{'✅ ALL TESTS PASSED' if all_pass else '❌ SOME TESTS FAILED — review before pushing'}")

# ── CELL 11: Save + Push ───────────────────────────────────────────────────────
if eval_results['eval_accuracy'] >= 0.75 and all_pass:
    print("\nSaving and pushing model...")

    save_path = "./medha-classifier-final"
    trainer.save_model(save_path)
    tokenizer.save_pretrained(save_path)

    # Save label config
    with open(f"{save_path}/medha_label_config.json", "w") as f:
        json.dump({
            "label2id":            LABEL2ID,
            "id2label":            ID2LABEL,
            "equilibrium_seconds": 45,
            "model_version":       "v1",
            "base_model":          BASE_MODEL,
            "training_examples":   len(train_data),
            "val_accuracy":        round(eval_results['eval_accuracy'], 4),
            "val_f1_weighted":     round(eval_results['eval_f1_weighted'], 4),
        }, f, indent=2)

    repo_id = f"{HF_USERNAME}/{MODEL_NAME}"
    model.push_to_hub(repo_id, private=True, token=HF_TOKEN)
    tokenizer.push_to_hub(repo_id, private=True, token=HF_TOKEN)

    print(f"\n✅ Model pushed to: https://huggingface.co/{repo_id}")
    print(f"\nAdd to your .env:")
    print(f"  HF_MODEL_ID={repo_id}")
    print(f"  HF_TOKEN=<your token>")
else:
    print("\n⚠️ Model NOT pushed — accuracy or test cases below threshold")
    print("   Review the evaluation results above and retrain if needed")
