"""
MEDHA — Qwen2.5-3B Explainer Training Script (FIXED v2)
==========================================================
Run on Kaggle Notebook with GPU T4 x2

Changes from v1:
- Fixed double-formatting bug (dataset.map + formatting_func conflict)
- Fixed SFTTrainer API: formatting_func → dataset_text_field (trl 0.8+ compatible)
- Added train/val split (was training on 100% data with no validation)
- Added manual inference test after training
- Fixed DataCollatorForCompletionOnlyLM token encoding

Instructions:
1. New Kaggle notebook → Settings → GPU T4 x2 → Internet ON
2. Upload the unified dataset from app/ml/kaggle_dataset as dataset (named: medha-ml-dataset)
3. Add HF_TOKEN as a Kaggle Secret
4. Paste entire script into a single cell and run

Expected training time: 2-3 hours on T4 x2
"""

# ── CELL 1: Install & Setup (Foolproof Clean Version) ────────────────────────
import subprocess
import os

print("Installing required training libraries...")
subprocess.run([
    "pip", "install", "-q",
    "transformers>=4.45.0",
    "datasets==2.20.0",
    "peft==0.12.0",
    "bitsandbytes>=0.43.0",
    "accelerate>=0.30.0",
    "trl==0.9.6"
])

import os, warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore")

import json, torch
from pathlib import Path

# ── CONFIGURATION ─────────────────────────────────────────────────────────────
# !! UPDATE THESE BEFORE RUNNING !!
HF_USERNAME  = "medha-training"   # Will be automatically resolved from HF_TOKEN in Cell 2
HF_TOKEN     = os.getenv("HF_TOKEN", "")
MODEL_NAME   = "medha-explainer-v1"
BASE_MODEL   = "Qwen/Qwen2.5-3B-Instruct"

EPOCHS       = 5
BATCH_SIZE   = 4
GRAD_ACCUM   = 4            # effective batch = 16
LR           = 2e-4
MAX_SEQ_LEN  = 512
VAL_SPLIT    = 0.1          # 10% validation
SEED         = 42

# ── CELL 2: Login ──────────────────────────────────────────────────────────────
from huggingface_hub import login, HfApi
login(token=HF_TOKEN)
try:
    HF_USERNAME = HfApi().whoami(token=HF_TOKEN)["name"]
    print(f"Logged in to HuggingFace as user: '{HF_USERNAME}' ✅")
except Exception as e:
    print(f"Logged in to HuggingFace. Could not fetch username automatically ({e}). Using default: '{HF_USERNAME}'")


# ── CELL 3: Load Data ──────────────────────────────────────────────────────────
from datasets import Dataset

import glob
data_files = glob.glob("/kaggle/input/**/explainer_training_data.jsonl", recursive=True)
if data_files:
    DATA_PATH = data_files[0]
else:
    DATA_PATH = "explainer_training_data.jsonl"
print(f"Using DATA_PATH: {DATA_PATH}")

raw_data = []
with open(DATA_PATH, "r", encoding="utf-8") as f:
    for line in f:
        raw_data.append(json.loads(line.strip()))

print(f"Loaded {len(raw_data)} examples")

# ── CELL 4: Format as Instruction (do this ONCE, before creating Dataset) ──────

def build_prompt(example):
    """
    Builds the full chat-formatted prompt for Qwen2.5-Instruct.
    We determine system prompt based on whether it's a correct or wrong answer.
    """
    is_correct = "(Correct)" in example["input"]

    if is_correct:
        system_msg = (
            "তুমি MEDHA, বাংলাদেশের মেডিকেল ভর্তি পরীক্ষার একজন টিউটর। "
            "একজন শিক্ষার্থী সঠিক উত্তর দিয়েছে — তাদের বোঝাপড়া শক্তিশালী করো।"
        )
    else:
        system_msg = (
            "তুমি MEDHA, বাংলাদেশের মেডিকেল ভর্তি পরীক্ষার একজন টিউটর। "
            "একজন শিক্ষার্থী ভুল উত্তর দিয়েছে — তাদের ভুল ধারণা সংশোধন করো।"
        )

    # Qwen2.5 chat format
    prompt = (
        f"<|im_start|>system\n{system_msg}<|im_end|>\n"
        f"<|im_start|>user\n{example['input'].strip()}<|im_end|>\n"
        f"<|im_start|>assistant\n{example['output'].strip()}<|im_end|>"
    )
    return {"text": prompt}

# Format ALL examples first, then create dataset
# This avoids the double-formatting bug in v1
print("Formatting examples...")
formatted_data = [build_prompt(ex) for ex in raw_data]

# Split BEFORE creating Dataset objects
import random
random.seed(SEED)
random.shuffle(formatted_data)

split_idx   = int(len(formatted_data) * (1 - VAL_SPLIT))
train_data  = formatted_data[:split_idx]
val_data    = formatted_data[split_idx:]

train_dataset = Dataset.from_list(train_data)
val_dataset   = Dataset.from_list(val_data)

print(f"Train: {len(train_dataset)} | Val: {len(val_dataset)}")

# Quick sanity check on prompt format
sample_text = train_dataset[0]["text"]
print(f"\nSample prompt (first 200 chars):")
print(sample_text[:200])
print("...")
assert "<|im_start|>system" in sample_text, "System prompt missing"
assert "<|im_start|>assistant" in sample_text, "Assistant section missing"
print("Format check ✅")

# ── CELL 5: Load Tokenizer ─────────────────────────────────────────────────────
from transformers import AutoTokenizer

print(f"\nLoading tokenizer: {BASE_MODEL}")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"   # important for causal LM training

# Check token lengths
lengths = [len(tokenizer(ex["text"]).input_ids) for ex in formatted_data[:100]]
print(f"Token length stats (sample 100):")
print(f"  Min: {min(lengths)} | Max: {max(lengths)} | Avg: {sum(lengths)//len(lengths)}")
print(f"  MAX_SEQ_LEN={MAX_SEQ_LEN} {'✅ adequate' if max(lengths) < MAX_SEQ_LEN else '⚠️ INCREASE'}")

# ── CELL 6: Load Model with 4-bit quantization ─────────────────────────────────
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

print(f"\nLoading {BASE_MODEL} in 4-bit...")
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto",
)

model = prepare_model_for_kbit_training(model)

# QLoRA config for Qwen2.5
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ── CELL 7: Training Setup ─────────────────────────────────────────────────────
from transformers import TrainingArguments
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM

# Response template — only compute loss on assistant's reply
# This token sequence marks the start of the assistant's turn
response_template_str = "assistant\n"  # Fixed tokenizer special token bug
response_template_ids = tokenizer.encode(response_template_str, add_special_tokens=False)
print(f"Response template token IDs: {response_template_ids}")

collator = DataCollatorForCompletionOnlyLM(
    response_template=response_template_ids,
    tokenizer=tokenizer,
)

from transformers import TrainerCallback

class ProgressCallback(TrainerCallback):
    """Custom callback to provide a clean real-time training dashboard in stdout."""
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs and "loss" in logs:
            loss = logs["loss"]
            step = state.global_step
            epoch = logs.get("epoch", 0.0)
            lr = logs.get("learning_rate", 0.0)
            print(f"📊 [Step {step:04d}] Epoch {epoch:.2f} | Loss: {loss:.4f} | LR: {lr:.2e}")

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        if metrics:
            epoch = metrics.get("epoch", 0.0)
            loss = metrics.get("eval_loss", 0.0)
            print(f"✨ [Evaluation] Epoch {epoch:.2f} | Val Loss: {loss:.4f}")

training_args = TrainingArguments(
    output_dir                  = "./qwen-medha-output",
    num_train_epochs            = EPOCHS,
    per_device_train_batch_size = BATCH_SIZE,
    gradient_accumulation_steps = GRAD_ACCUM,   # effective batch = 16
    learning_rate               = LR,
    fp16                        = True,
    eval_strategy               = "epoch",      # FIXED from evaluation_strategy
    save_strategy               = "epoch",
    load_best_model_at_end      = True,
    metric_for_best_model       = "eval_loss",
    greater_is_better           = False,
    save_total_limit            = 2,
    logging_steps               = 5,            # Log every 5 steps for frequent visibility
    warmup_ratio                = 0.05,
    lr_scheduler_type           = "cosine",
    seed                        = SEED,
    report_to                   = "none",
)

# FIXED: use dataset_text_field instead of formatting_func
# The dataset already has a 'text' column from our build_prompt step
# No double-formatting issue
trainer = SFTTrainer(
    model              = model,
    train_dataset      = train_dataset,
    eval_dataset       = val_dataset,
    args               = training_args,
    data_collator      = collator,
    dataset_text_field = "text",     # FIXED: was formatting_func in v1
    max_seq_length     = MAX_SEQ_LEN,
    tokenizer          = tokenizer,
    callbacks          = [ProgressCallback()],
)


# ── CELL 8: TRAIN ──────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STARTING QWEN EXPLAINER TRAINING")
print(f"Base model:  {BASE_MODEL}")
print(f"Method:      QLoRA (4-bit) — 3B model requires quantization")
print(f"Train size:  {len(train_dataset)}")
print(f"Val size:    {len(val_dataset)}")
print(f"Epochs:      {EPOCHS}")
print(f"Eff. batch:  {BATCH_SIZE * GRAD_ACCUM}")
print("="*60 + "\n")

train_result = trainer.train()

print(f"\nTraining complete!")
print(f"Runtime:    {train_result.metrics['train_runtime']/60:.1f} minutes")
print(f"Train loss: {train_result.metrics['train_loss']:.4f}")

# ── CELL 9: Inference Test ─────────────────────────────────────────────────────
# No automated eval metric for generation — test manually
print("\n" + "="*60)
print("MANUAL INFERENCE TEST")
print("="*60)

from transformers import pipeline as hf_pipeline

# Use the merged model for inference test
test_model   = model.merge_and_unload()
gen_pipeline = hf_pipeline(
    "text-generation",
    model=test_model,
    tokenizer=tokenizer,
    device_map="auto",
    max_new_tokens=300,
    do_sample=False,        # deterministic for testing
)

test_input = {
    "input": (
        "Question: কোষ বিভাজনের সময় কোষপ্লেট তৈরিতে সাহায্য করে কোন অঙ্গাণু?\n"
        "Student answered: রাইবোসোম (Wrong)\n"
        "Correct answer: গলগি বস্তু\n"
        "Behavioral state: PRIORITY_FOCUS\n"
        "Chapter: কোষ ও কোষ অঙ্গাণু"
    ),
    "output": ""
}

test_prompt = build_prompt({**test_input, "output": ""})["text"]
# Strip everything from assistant onward (model will generate this)
input_part  = test_prompt.split("<|im_start|>assistant\n")[0] + "<|im_start|>assistant\n"

print("Input:")
print(input_part)
print("\nGenerating response...")

output = gen_pipeline(input_part)[0]["generated_text"]
response_part = output.split("<|im_start|>assistant\n")[-1].replace("<|im_end|>", "").strip()

print("Model output:")
print(response_part)

# Check output is valid JSON
try:
    parsed = json.loads(response_part)
    required = ["explanation", "why_wrong", "memory_trick", "textbook_ref"]
    missing  = [f for f in required if f not in parsed]
    if not missing:
        print("\n✅ Output is valid JSON with all required fields")
        for key, val in parsed.items():
            print(f"  {key}: {val[:80]}")
    else:
        print(f"\n⚠️  Valid JSON but missing fields: {missing}")
except json.JSONDecodeError:
    print("\n⚠️  Output is NOT valid JSON — model may need more epochs or the format needs adjustment")
    print("    This can happen if max_new_tokens is too low or if the model didn't learn JSON format")

# ── CELL 10: Save + Push ───────────────────────────────────────────────────────
print("\nMerging LoRA and pushing to HuggingFace...")

repo_id = f"{HF_USERNAME}/{MODEL_NAME}"
test_model.push_to_hub(repo_id, private=True, token=HF_TOKEN)
tokenizer.push_to_hub(repo_id, private=True, token=HF_TOKEN)

print(f"\n✅ Model pushed to: https://huggingface.co/{repo_id}")
print(f"\nAdd to your .env:")
print(f"  HF_EXPLAINER_ID={repo_id}")
