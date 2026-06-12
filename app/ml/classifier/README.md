# MEDHA Behavioral Classifier — Training Guide

## Overview

This directory contains everything needed to train the MEDHA behavioral classifier:
a fine-tuned **BanglaBERT** model that classifies exam answers into 4 behavioral states.

| Component | File | Description |
|---|---|---|
| Data Generator | `data_generator.py` | Creates synthetic training data (5,000+ examples) |
| Training Script | `train_classifier.py` | BanglaBERT + QLoRA fine-tuning for Kaggle |
| Topics | `topics_for_training.json` | 38 real BD medical exam topics (Bengali + English) |
| Training Data | `data/classifier_train.jsonl` | 4,200 training examples |
| Validation Data | `data/classifier_val.jsonl` | 1,050 validation examples |

---

## What the Classifier Does

**Input:** A text string encoding behavioral signals from a single exam answer:
```
Topic: কোষ ও কোষ অঙ্গাণু | time_ratio: 0.200 | switches: 0 | confidence: sure | correct: true | difficulty: medium
```

**Output:** One of 4 labels:
- `MASTERY` — Fast + correct + confident → knows it cold
- `PRIORITY_FOCUS` — Fast + wrong + confident → confidently wrong (most dangerous)
- `TRUST_GAP` — Correct but slow/hesitant → knows it but doubts themselves
- `GROWTH_AREA` — Slow + wrong + unsure → genuine knowledge gap

---

## Training Platform: Kaggle (Free)

**Why Kaggle:** Free T4 x2 GPU, 30 hours/week quota, no credit card needed.

---

## Step-by-Step Training

### STEP 1: Create HuggingFace Account (10 min)

1. Go to https://huggingface.co → Sign Up
2. Go to Settings → Access Tokens → New Token
3. Name: `medha-training`
4. Permissions: **Write** (needed to push model)
5. Copy and save the token (starts with `hf_`)

### STEP 2: Regenerate Training Data with Real Topics (5 min)

Run the data generator locally to update training data with real exam topics:

```bash
cd app/ml/classifier
python data_generator.py
```

This creates/overwrites:
- `data/classifier_train.jsonl` — ~4,200 examples
- `data/classifier_val.jsonl` — ~1,050 examples

### STEP 3: Upload Data to Kaggle (10 min)

1. Go to https://kaggle.com → Sign In (create account if needed)
2. Click **Datasets** → **New Dataset**
3. Dataset name: `medha-ml-dataset`
4. Upload all 3 files from `app/ml/kaggle_dataset/`:
   - `classifier_train.jsonl`
   - `classifier_val.jsonl`
   - `explainer_training_data.jsonl`
5. Set visibility: **Private**
6. Click **Create**

### STEP 4: Create Kaggle Notebook (5 min)

1. Click **Code** → **New Notebook**
2. Name: `medha-classifier-training`
3. In **Settings** (right sidebar):
   - **Accelerator:** `GPU T4 x2`
   - **Internet:** `On` (required to download BanglaBERT)
   - **Persistence:** `Files only`
4. Click **Add data** → search your `medha-ml-dataset` dataset → Add

### STEP 5: Paste Training Code

The notebook has **11 cells**. Copy each cell below into a separate Kaggle cell.

---

#### Cell 1 — Install Dependencies
```python
!pip install -q transformers datasets peft bitsandbytes accelerate huggingface_hub evaluate scikit-learn
```

#### Cell 2 — Configuration
```python
import os
import json
import numpy as np
from pathlib import Path

# ═══════════════════════════════════════════
# UPDATE THESE TWO LINES WITH YOUR VALUES:
HF_USERNAME = "YOUR_HF_USERNAME"
HF_TOKEN = "hf_YOUR_ACTUAL_TOKEN"
# ═══════════════════════════════════════════

MODEL_NAME = "medha-behavioral-classifier-v1"
BASE_MODEL = "csebuetnlp/banglabert"
NUM_LABELS = 4

LABEL_MAP = {
    "MASTERY": 0,
    "PRIORITY_FOCUS": 1,
    "TRUST_GAP": 2,
    "GROWTH_AREA": 3,
}
ID_TO_LABEL = {v: k for k, v in LABEL_MAP.items()}

# Hyperparameters
EPOCHS = 8
BATCH_SIZE = 16
LEARNING_RATE = 2e-4
MAX_LENGTH = 128
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.1
```

#### Cell 3 — Login to HuggingFace
```python
from huggingface_hub import login
login(token=HF_TOKEN)
print("Logged into HuggingFace successfully")
```

#### Cell 4 — Load Data
```python
from datasets import Dataset

def load_jsonl(filepath):
    data = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line.strip())
            item["label"] = LABEL_MAP[item["label"]]
            data.append(item)
    return data

# Kaggle dataset path
TRAIN_PATH = "/kaggle/input/medha-ml-dataset/classifier_train.jsonl"
VAL_PATH = "/kaggle/input/medha-ml-dataset/classifier_val.jsonl"

train_data = load_jsonl(TRAIN_PATH)
val_data = load_jsonl(VAL_PATH)

train_dataset = Dataset.from_list(train_data)
val_dataset = Dataset.from_list(val_data)

print(f"Train: {len(train_dataset)} samples")
print(f"Val:   {len(val_dataset)} samples")
print(f"Label distribution: {np.bincount([d['label'] for d in train_data])}")
```

#### Cell 5 — Tokenize
```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

def tokenize_fn(examples):
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=MAX_LENGTH,
    )

train_dataset = train_dataset.map(tokenize_fn, batched=True, remove_columns=["text"])
val_dataset = val_dataset.map(tokenize_fn, batched=True, remove_columns=["text"])
train_dataset.set_format("torch")
val_dataset.set_format("torch")
print("Tokenization complete")
```

#### Cell 6 — Load Model with QLoRA
```python
import torch
from transformers import AutoModelForSequenceClassification, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

model = AutoModelForSequenceClassification.from_pretrained(
    BASE_MODEL,
    num_labels=NUM_LABELS,
    quantization_config=bnb_config,
    device_map="auto",
    id2label=ID_TO_LABEL,
    label2id=LABEL_MAP,
)

model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    task_type=TaskType.SEQ_CLS,
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    target_modules=["query", "value", "key", "dense"],
    bias="none",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
```

#### Cell 7 — Training Setup
```python
from transformers import TrainingArguments, Trainer
import evaluate

accuracy_metric = evaluate.load("accuracy")
f1_metric = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    acc = accuracy_metric.compute(predictions=predictions, references=labels)
    f1 = f1_metric.compute(predictions=predictions, references=labels, average="weighted")
    from sklearn.metrics import classification_report
    report = classification_report(labels, predictions, target_names=list(LABEL_MAP.keys()), output_dict=True)
    metrics = {"accuracy": acc["accuracy"], "f1_weighted": f1["f1"]}
    for label_name in LABEL_MAP.keys():
        metrics[f"f1_{label_name}"] = report[label_name]["f1-score"]
    return metrics

training_args = TrainingArguments(
    output_dir="./medha-classifier-output",
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE * 2,
    learning_rate=LEARNING_RATE,
    weight_decay=0.01,
    warmup_ratio=0.1,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_steps=50,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    greater_is_better=True,
    fp16=True,
    gradient_accumulation_steps=1,
    report_to="none",
    save_total_limit=2,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

print("Trainer ready. Starting training...")
```

#### Cell 8 — Train (90-120 min)
```python
train_result = trainer.train()
print(f"\nTraining complete!")
print(f"Training loss: {train_result.training_loss:.4f}")
```

#### Cell 9 — Evaluate
```python
eval_results = trainer.evaluate()
print(f"\nValidation Results:")
print(f"  Accuracy:    {eval_results['eval_accuracy']:.4f}")
print(f"  F1 Weighted: {eval_results['eval_f1_weighted']:.4f}")
print(f"\n  Per-class F1:")
for label_name in LABEL_MAP.keys():
    key = f"eval_f1_{label_name}"
    if key in eval_results:
        print(f"    {label_name:20s}: {eval_results[key]:.4f}")

if eval_results['eval_accuracy'] < 0.75:
    print("\nWARNING: Accuracy below 75%!")
elif eval_results['eval_accuracy'] < 0.80:
    print("\nAcceptable for MVP — consider one more epoch.")
else:
    print(f"\nAccuracy {eval_results['eval_accuracy']:.1%} — GOOD TO GO!")
```

#### Cell 10 — Confusion Matrix
```python
from sklearn.metrics import confusion_matrix, classification_report

predictions = trainer.predict(val_dataset)
preds = np.argmax(predictions.predictions, axis=-1)
labels = predictions.label_ids

print("\nClassification Report:")
print(classification_report(labels, preds, target_names=list(LABEL_MAP.keys()), digits=4))

cm = confusion_matrix(labels, preds)
print("Confusion Matrix:")
header = f"{'':20s}" + "".join(f"{n:>12s}" for n in LABEL_MAP.keys())
print(header)
for i, label_name in enumerate(LABEL_MAP.keys()):
    row = "".join(f"{cm[i][j]:12d}" for j in range(NUM_LABELS))
    print(f"{label_name:20s}{row}")
```

#### Cell 11 — Merge & Push to HuggingFace
```python
print("Merging LoRA weights and pushing to HuggingFace...")

merged_model = model.merge_and_unload()
local_path = "./medha-classifier-merged"
merged_model.save_pretrained(local_path)
tokenizer.save_pretrained(local_path)

# Save metadata
with open(os.path.join(local_path, "label_mapping.json"), "w") as f:
    json.dump({
        "label2id": LABEL_MAP,
        "id2label": ID_TO_LABEL,
        "equilibrium_seconds": 45,
        "model_version": "v1",
        "training_examples": len(train_data),
        "validation_accuracy": eval_results['eval_accuracy'],
    }, f, indent=2)

# Push
repo_id = f"{HF_USERNAME}/{MODEL_NAME}"
merged_model.push_to_hub(repo_id, private=True)
tokenizer.push_to_hub(repo_id, private=True)

print(f"\nModel pushed to: https://huggingface.co/{repo_id}")
print(f"Set in your .env:")
print(f"  HF_MODEL_ID={repo_id}")
```

---

### STEP 6: After Training Completes

1. Copy the `HF_MODEL_ID` from the output
2. Update your backend `.env`:
   ```
   HF_TOKEN=hf_your_token
   HF_MODEL_ID=your_username/medha-behavioral-classifier-v1
   ```
3. Restart backend — classifier_service.py will automatically use the HF model
4. If HF API is slow/cold, the rule-based fallback kicks in (same logic, zero latency)

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `CUDA out of memory` | Reduce `BATCH_SIZE` to 8 or 4 |
| `Model download fails` | Check Internet is ON in Kaggle settings |
| `bitsandbytes error` | Run `!pip install -q bitsandbytes --upgrade` |
| `evaluation_strategy deprecated` | Use `eval_strategy` instead (already done above) |
| Accuracy below 75% | Check class distribution, increase epochs to 12 |
| HF push fails | Check token has Write permission |

---

## Qwen2.5-3B Explainer (V2 — After Classifier)

After the classifier is trained and working, the next model to train is the explanation generator. See `../explainer/README.md` for that pipeline.
