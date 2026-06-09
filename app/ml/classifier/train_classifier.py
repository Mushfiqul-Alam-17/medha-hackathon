"""
MEDHA — BanglaBERT Behavioral Classifier Training Script
==========================================================
For Kaggle Notebook (GPU T4 x2)

Instructions:
1. Create a new Kaggle notebook
2. Enable GPU T4 x2 in Settings
3. Upload classifier_train.jsonl and classifier_val.jsonl as dataset
4. Paste this entire script into a cell and run
5. After training, the model will be pushed to HuggingFace Hub

Expected training time: 90-120 minutes on T4 x2
Target accuracy: >80% on validation set
"""

# ── Cell 1: Install dependencies ──
# !pip install -q transformers datasets peft bitsandbytes accelerate huggingface_hub evaluate scikit-learn

import os
import json
import numpy as np
from pathlib import Path

# ── Configuration ──
# UPDATE THESE before running:
HF_USERNAME = "YOUR_HF_USERNAME"  # Your HuggingFace username
HF_TOKEN = "YOUR_HF_TOKEN"       # Your HuggingFace write token
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

# Training hyperparameters
EPOCHS = 8
BATCH_SIZE = 16
LEARNING_RATE = 2e-4
MAX_LENGTH = 128  # Our text sequences are short
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.1

# ── Cell 2: Login to HuggingFace ──
from huggingface_hub import login
login(token=HF_TOKEN)

# ── Cell 3: Load and prepare data ──
from datasets import Dataset

def load_jsonl(filepath):
    """Load JSONL file into list of dicts."""
    data = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line.strip())
            item["label"] = LABEL_MAP[item["label"]]
            data.append(item)
    return data

# Update these paths based on your Kaggle dataset location
# If uploaded as a Kaggle dataset, it'll be in /kaggle/input/
TRAIN_PATH = "/kaggle/input/medha-classifier-data/classifier_train.jsonl"
VAL_PATH = "/kaggle/input/medha-classifier-data/classifier_val.jsonl"

# Fallback for local testing
if not os.path.exists(TRAIN_PATH):
    TRAIN_PATH = "data/classifier_train.jsonl"
    VAL_PATH = "data/classifier_val.jsonl"

train_data = load_jsonl(TRAIN_PATH)
val_data = load_jsonl(VAL_PATH)

train_dataset = Dataset.from_list(train_data)
val_dataset = Dataset.from_list(val_data)

print(f"Train samples: {len(train_dataset)}")
print(f"Val samples: {len(val_dataset)}")
print(f"Label distribution (train): {np.bincount([d['label'] for d in train_data])}")

# ── Cell 4: Tokenize ──
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

# ── Cell 5: Load model with QLoRA ──
import torch
from transformers import AutoModelForSequenceClassification, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training

# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

# Load base model
model = AutoModelForSequenceClassification.from_pretrained(
    BASE_MODEL,
    num_labels=NUM_LABELS,
    quantization_config=bnb_config,
    device_map="auto",
    id2label=ID_TO_LABEL,
    label2id=LABEL_MAP,
)

# Prepare for k-bit training
model = prepare_model_for_kbit_training(model)

# LoRA config
lora_config = LoraConfig(
    task_type=TaskType.SEQ_CLS,
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    target_modules=["query", "value", "key", "dense"],  # BanglaBERT attention layers
    bias="none",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ── Cell 6: Training setup ──
from transformers import TrainingArguments, Trainer
import evaluate

# Load metrics
accuracy_metric = evaluate.load("accuracy")
f1_metric = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    
    acc = accuracy_metric.compute(predictions=predictions, references=labels)
    f1 = f1_metric.compute(predictions=predictions, references=labels, average="weighted")
    
    # Per-class accuracy
    from sklearn.metrics import classification_report
    report = classification_report(labels, predictions, target_names=list(LABEL_MAP.keys()), output_dict=True)
    
    metrics = {
        "accuracy": acc["accuracy"],
        "f1_weighted": f1["f1"],
    }
    
    # Add per-class F1
    for label_name in LABEL_MAP.keys():
        metrics[f"f1_{label_name}"] = report[label_name]["f1-score"]
    
    return metrics

# Training arguments
training_args = TrainingArguments(
    output_dir=f"./medha-classifier-output",
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE * 2,
    learning_rate=LEARNING_RATE,
    weight_decay=0.01,
    warmup_ratio=0.1,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_steps=50,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    greater_is_better=True,
    fp16=True,
    gradient_accumulation_steps=1,
    report_to="none",  # Disable wandb on Kaggle
    save_total_limit=2,
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

# ── Cell 7: Train! ──
print("Starting training...")
print(f"Model: {BASE_MODEL}")
print(f"Method: QLoRA (4-bit)")
print(f"Epochs: {EPOCHS}")
print(f"Batch size: {BATCH_SIZE}")
print(f"Learning rate: {LEARNING_RATE}")
print(f"LoRA r={LORA_R}, alpha={LORA_ALPHA}")
print("=" * 60)

train_result = trainer.train()
print(f"\nTraining complete!")
print(f"Training loss: {train_result.training_loss:.4f}")

# ── Cell 8: Evaluate ──
eval_results = trainer.evaluate()
print(f"\nValidation Results:")
print(f"  Accuracy:    {eval_results['eval_accuracy']:.4f}")
print(f"  F1 Weighted: {eval_results['eval_f1_weighted']:.4f}")
print(f"\n  Per-class F1:")
for label_name in LABEL_MAP.keys():
    key = f"eval_f1_{label_name}"
    if key in eval_results:
        print(f"    {label_name:20s}: {eval_results[key]:.4f}")

# Quality gate
if eval_results['eval_accuracy'] < 0.75:
    print("\n⚠️  WARNING: Accuracy below 75%!")
    print("   Consider adjusting training data distribution.")
    print("   Common issue: PRIORITY_FOCUS bleeding into MASTERY")
elif eval_results['eval_accuracy'] < 0.80:
    print("\n⚡ Accuracy between 75-80%. Acceptable for MVP.")
    print("   Consider one more epoch or adjusting class weights.")
else:
    print(f"\n✅ Accuracy {eval_results['eval_accuracy']:.1%} — GOOD TO GO!")

# ── Cell 9: Confusion Matrix ──
from sklearn.metrics import confusion_matrix, classification_report

# Get predictions on validation set
predictions = trainer.predict(val_dataset)
preds = np.argmax(predictions.predictions, axis=-1)
labels = predictions.label_ids

# Print classification report
print("\nDetailed Classification Report:")
print(classification_report(
    labels, preds,
    target_names=list(LABEL_MAP.keys()),
    digits=4
))

# Confusion matrix
cm = confusion_matrix(labels, preds)
print("Confusion Matrix:")
print(f"{'':20s} {'MASTERY':>10s} {'PRI_FOCUS':>10s} {'TRUST_GAP':>10s} {'GROWTH':>10s}")
for i, label_name in enumerate(LABEL_MAP.keys()):
    row = "  ".join(f"{cm[i][j]:8d}" for j in range(NUM_LABELS))
    print(f"{label_name:20s} {row}")

# ── Cell 10: Merge and push to HuggingFace ──
print(f"\nMerging LoRA weights and pushing to HuggingFace...")

# Merge LoRA weights into base model
merged_model = model.merge_and_unload()

# Save locally first
local_path = f"./medha-classifier-merged"
merged_model.save_pretrained(local_path)
tokenizer.save_pretrained(local_path)

# Save label mapping
config_path = os.path.join(local_path, "label_mapping.json")
with open(config_path, "w") as f:
    json.dump({
        "label2id": LABEL_MAP,
        "id2label": ID_TO_LABEL,
        "equilibrium_seconds": 45,
        "model_version": "v1",
        "training_examples": len(train_data),
        "validation_accuracy": eval_results['eval_accuracy'],
    }, f, indent=2)

# Push to HuggingFace Hub
repo_id = f"{HF_USERNAME}/{MODEL_NAME}"
merged_model.push_to_hub(repo_id, private=True)
tokenizer.push_to_hub(repo_id, private=True)

print(f"\n✅ Model pushed to: https://huggingface.co/{repo_id}")
print(f"   Use this as HF_MODEL_ID in your .env file")
print(f"\n   HF_MODEL_ID={repo_id}")

# ── Cell 11: Test inference ──
print("\n" + "=" * 60)
print("Testing inference with sample inputs...")
print("=" * 60)

test_cases = [
    # Clear MASTERY: fast, correct, confident
    "Topic: Cell Division | time_ratio: 0.200 | switches: 0 | confidence: sure | correct: true | difficulty: medium",
    # Clear PRIORITY_FOCUS: fast, wrong, confident
    "Topic: Enzymes | time_ratio: 0.150 | switches: 0 | confidence: sure | correct: false | difficulty: medium",
    # Clear TRUST_GAP: correct but hesitant
    "Topic: Genetics | time_ratio: 0.800 | switches: 2 | confidence: unsure | correct: true | difficulty: hard",
    # Clear GROWTH_AREA: slow, wrong, unsure
    "Topic: Ecology | time_ratio: 0.900 | switches: 3 | confidence: guessing | correct: false | difficulty: hard",
]

expected = ["MASTERY", "PRIORITY_FOCUS", "TRUST_GAP", "GROWTH_AREA"]

from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model=local_path,
    tokenizer=local_path,
    device=0,
)

for text, exp in zip(test_cases, expected):
    result = classifier(text, top_k=4)
    pred = result[0]["label"]
    conf = result[0]["score"]
    status = "✅" if pred == exp else "❌"
    print(f"\n{status} Expected: {exp:20s} | Predicted: {pred:20s} ({conf:.2%})")
    print(f"   Input: {text[:70]}...")

print(f"\n{'=' * 60}")
print(f"DONE. Model ready at: {repo_id}")
print(f"{'=' * 60}")
