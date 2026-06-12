"""
MEDHA — BanglaBERT Behavioral Classifier Training Script (Ultra-Robust v3)
========================================================================
Run on Kaggle Notebook with GPU T4 x2

Improvements in v3:
- Fully automated HuggingFace username detection & upload
- Suppressed ALL tokenizers and PyTorch warnings
- Data Augmentation: Randomly masks 'confidence' feature to train model to rely on
  behavioral data (time, skips, switches) simulating students turning the feature off.
- Increased epochs to 100 with patience=10 for maximum accuracy.
- Added a robust real-time training dashboard.

Instructions:
1. New Kaggle notebook → Settings → GPU T4 x2 → Internet ON
2. Upload the unified dataset from app/ml/kaggle_dataset as a dataset
3. Add your HF_TOKEN as a Kaggle Secret (Secrets tab)
4. Run all cells!
"""

# ── CELL 1: Install & Suppress Warnings ───────────────────────────────────────
import os
import warnings

# MUST set before importing torch/transformers to suppress the fork warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "true"
warnings.filterwarnings("ignore")

import subprocess
# Install quietly
subprocess.run([
    "pip", "install", "-q",
    "transformers==4.44.0", "datasets", "evaluate", "scikit-learn", "accelerate"
])

import json, numpy as np, re
from pathlib import Path

# ── CONFIGURATION ─────────────────────────────────────────────────────────────
# Set your token here, or use Kaggle Secrets (recommended)
HF_TOKEN     = os.getenv("HF_TOKEN", "")
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

# Hyperparameters for 5-6 hours potential training (Early stopping will halt it at perfection)
EPOCHS      = 100         # Massive epochs, let early stopping decide when it's perfect
BATCH_SIZE  = 32          
LR          = 2e-5        
MAX_LENGTH  = 128         
SEED        = 42


# ── CELL 2: HuggingFace Login & Username Auth ─────────────────────────────────
from huggingface_hub import login, HfApi

# Authenticate
login(token=HF_TOKEN)

# Auto-fetch username so we NEVER get a 403 Forbidden Error
try:
    api = HfApi()
    user_info = api.whoami(token=HF_TOKEN)
    HF_USERNAME = user_info["name"]
    print(f"✅ Successfully authenticated as HuggingFace User: '{HF_USERNAME}'")
except Exception as e:
    print(f"❌ Failed to fetch username from token. Error: {e}")
    HF_USERNAME = "medha-training" # Fallback

REPO_ID = f"{HF_USERNAME}/{MODEL_NAME}"
print(f"🚀 Model will be uploaded to: https://huggingface.co/{REPO_ID}")


# ── CELL 3: Load Data & Data Augmentation ─────────────────────────────────────
from datasets import Dataset
import torch

torch.manual_seed(SEED)
np.random.seed(SEED)

def load_jsonl(filepath, is_train=False):
    data = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line.strip())
            item["label"] = LABEL2ID[item["label"]]
            
            # 🧠 DATA AUGMENTATION (Training only)
            # Simulating students who turn OFF the "Sure/Unsure/Guessing" option.
            # We randomly mask out the confidence feature 40% of the time.
            # This forces the model to learn from analytical behavior (time spent, skipping).
            if is_train and np.random.rand() < 0.40:
                item["text"] = re.sub(r"confidence: [^|]+\| ", "confidence: hidden | ", item["text"])
                
            data.append(item)
    return data

import glob

# Auto-find Kaggle files
train_files = glob.glob("/kaggle/input/**/classifier_train.jsonl", recursive=True)
val_files   = glob.glob("/kaggle/input/**/classifier_val.jsonl", recursive=True)

TRAIN_PATH = train_files[0] if train_files else "classifier_train.jsonl"
VAL_PATH   = val_files[0]   if val_files   else "classifier_val.jsonl"

print(f"Using TRAIN_PATH: {TRAIN_PATH}")
print(f"Using VAL_PATH: {VAL_PATH}")

train_data = load_jsonl(TRAIN_PATH, is_train=True)
val_data   = load_jsonl(VAL_PATH, is_train=False)

train_dataset = Dataset.from_list(train_data)
val_dataset   = Dataset.from_list(val_data)

from collections import Counter
print(f"\n📊 Dataset Sizes - Train: {len(train_dataset)} | Val: {len(val_dataset)}")
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


# ── CELL 5: Load Model ────────────────────────────────────────────────────────
from transformers import AutoModelForSequenceClassification

print(f"\nLoading {BASE_MODEL} for full fine-tuning...")

model = AutoModelForSequenceClassification.from_pretrained(
    BASE_MODEL,
    num_labels=NUM_LABELS,
    id2label=ID2LABEL,
    label2id=LABEL2ID,
    ignore_mismatched_sizes=True, 
)

model = model.cuda()
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")


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

# ── CELL 7: Training Args & Realtime Progress Dashboard ────────────────────────
from transformers import TrainingArguments, Trainer, EarlyStoppingCallback, DataCollatorWithPadding, TrainerCallback

class EnhancedProgressCallback(TrainerCallback):
    """Provides a beautiful real-time dashboard inside Kaggle Notebooks."""
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs and "loss" in logs:
            loss = logs["loss"]
            epoch = logs.get("epoch", 0.0)
            print(f"⏳ [Epoch {epoch:.2f}/{args.num_train_epochs}] Training Loss: {loss:.4f}")

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        if metrics:
            epoch = metrics.get("epoch", 0.0)
            acc = metrics.get("eval_accuracy", 0.0)
            f1 = metrics.get("eval_f1_weighted", 0.0)
            print(f"🎯 [Epoch {epoch:.2f} Eval] Accuracy: {acc:.4f} | F1: {f1:.4f}")

training_args = TrainingArguments(
    output_dir                  = "./medha-classifier-output",
    num_train_epochs            = EPOCHS,
    per_device_train_batch_size = BATCH_SIZE,
    per_device_eval_batch_size  = 64,
    learning_rate               = LR,
    weight_decay                = 0.01,
    warmup_ratio                = 0.1,
    
    eval_strategy               = "epoch",
    save_strategy               = "epoch",
    load_best_model_at_end      = True,
    metric_for_best_model       = "f1_weighted",
    greater_is_better           = True,
    save_total_limit            = 2,

    logging_strategy            = "epoch",
    fp16                        = True,
    dataloader_num_workers      = 2,
    seed                        = SEED,
    report_to                   = "none",
    save_safetensors            = False,   
)

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# Filter annoying gather warnings inside trainer
import warnings
warnings.filterwarnings("ignore", message="Was asked to gather along dimension 0")

trainer = Trainer(
    model           = model,
    args            = training_args,
    train_dataset   = train_dataset,
    eval_dataset    = val_dataset,
    tokenizer       = tokenizer,
    data_collator   = data_collator,
    compute_metrics = compute_metrics,
    callbacks       = [
        EarlyStoppingCallback(early_stopping_patience=10), # High patience to ensure perfection
        EnhancedProgressCallback()
    ],
)


# ── CELL 8: TRAIN ──────────────────────────────────────────────────────────────
print("\n" + "🔥"*30)
print("STARTING ROBUST BEHAVIORAL TRAINING")
print(f"Model:      {BASE_MODEL}")
print(f"Max Epochs: {EPOCHS} (Early stopping will halt when perfect)")
print("🔥"*30 + "\n")

train_result = trainer.train()

print(f"\n✅ Training complete!")
print(f"Runtime:    {train_result.metrics['train_runtime']/60:.1f} minutes")
print(f"Best Model loaded from checkpoints automatically.")


# ── CELL 9: Full Evaluation ────────────────────────────────────────────────────
eval_results = trainer.evaluate()

print("\n" + "="*60)
print("🏆 FINAL VALIDATION RESULTS")
print("="*60)
print(f"  Accuracy:         {eval_results['eval_accuracy']:.4f}")
print(f"  F1 Weighted:      {eval_results['eval_f1_weighted']:.4f}")
print(f"\n  Per-class F1:")
print(f"  MASTERY:          {eval_results['eval_f1_MASTERY']:.4f}")
print(f"  PRIORITY_FOCUS:   {eval_results['eval_f1_PRIORITY_FOCUS']:.4f}")
print(f"  TRUST_GAP:        {eval_results['eval_f1_TRUST_GAP']:.4f}")
print(f"  GROWTH_AREA:      {eval_results['eval_f1_GROWTH_AREA']:.4f}")

# Quality gate
acc = eval_results['eval_accuracy']
if acc >= 0.87:
    print(f"\n🌟 EXCELLENT — {acc:.1%} accuracy. Target completely smashed!")
elif acc >= 0.80:
    print(f"\n⚡ ACCEPTABLE — {acc:.1%} accuracy. MVP ready.")
else:
    print(f"\n⚠️ BELOW TARGET — {acc:.1%}. Needs more data.")


# ── CELL 10: Manual Test Cases ─────────────────────────────────────────────────
print("\n" + "="*60)
print("MANUAL TEST CASES (Including No-Confidence Tests)")
print("="*60)

test_cases = [
    {
        "text":     "Topic: Cell Division | time_ratio: 0.180 | switches: 0 | confidence: sure | correct: true | difficulty: medium",
        "expected": "MASTERY",
        "desc":     "Standard: Fast + correct + confident → MASTERY"
    },
    {
        "text":     "Topic: Genetics & Evolution | time_ratio: 1.450 | switches: 3 | confidence: hidden | correct: true | difficulty: hard",
        "expected": "TRUST_GAP",
        "desc":     "Behavioral Only: Slow + skipped/switched + correct + NO CONFIDENCE → TRUST_GAP"
    },
    {
        "text":     "Topic: Digestive System | time_ratio: 2.800 | switches: 4 | confidence: hidden | correct: false | difficulty: hard",
        "expected": "GROWTH_AREA",
        "desc":     "Behavioral Only: Very slow + high switches + wrong + NO CONFIDENCE → GROWTH_AREA"
    },
]

import torch.nn.functional as F

device = next(model.parameters()).device
model.eval()

all_pass = True
for tc in test_cases:
    inputs = tokenizer(tc["text"], return_tensors="pt", truncation=True, max_length=MAX_LENGTH)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)[0]
    
    pred_idx = torch.argmax(probs).item()
    predicted = ID2LABEL[pred_idx]
    confidence = probs[pred_idx].item()
    
    passed = predicted == tc["expected"]
    all_pass = all_pass and passed
    status = "✅" if passed else "❌"
    print(f"\n{status} {tc['desc']}")
    print(f"   Expected:  {tc['expected']}")
    print(f"   Predicted: {predicted} ({confidence:.1%})")

print(f"\n{'🎯 ALL MANUAL TESTS PASSED' if all_pass else '⚠️ SOME TESTS FAILED'}")


# ── CELL 11: Save + Push to HuggingFace Hub ────────────────────────────────────
if acc >= 0.80: 
    print(f"\nSaving and pushing model directly to https://huggingface.co/{REPO_ID} ...")

    save_path = "./medha-classifier-final"
    trainer.save_model(save_path)
    tokenizer.save_pretrained(save_path)

    # Save label config
    with open(f"{save_path}/medha_label_config.json", "w") as f:
        json.dump({
            "label2id":            LABEL2ID,
            "id2label":            ID2LABEL,
            "model_version":       "v3_robust",
            "val_accuracy":        round(eval_results['eval_accuracy'], 4),
        }, f, indent=2)

    # Automatically Push!
    try:
        model.push_to_hub(REPO_ID, private=True, token=HF_TOKEN, safe_serialization=False)
        tokenizer.push_to_hub(REPO_ID, private=True, token=HF_TOKEN)
        print(f"\n✅✅✅ MODEL UPLOAD SUCCESSFUL TO: https://huggingface.co/{REPO_ID}")
        print("\nBACKEND INTEGRATION:")
        print(f"Update your backend .env with:")
        print(f"HF_MODEL_ID={REPO_ID}")
    except Exception as e:
        print(f"\n❌ PUSH FAILED: {e}")
        print("Please check your HF_TOKEN permissions.")
else:
    print("\n⚠️ Model NOT pushed — accuracy below threshold")
