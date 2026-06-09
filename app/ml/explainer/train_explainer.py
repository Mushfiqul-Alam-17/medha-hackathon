"""
MEDHA — Qwen2.5-3B Explainer Training Script (V2)
==========================================================
For Kaggle Notebook (GPU T4 x2)

Instructions:
1. Create a new Kaggle notebook
2. Enable GPU T4 x2 in Settings
3. Upload explainer_training_data.jsonl as dataset
4. Paste this entire script into a cell and run
"""

# ── Cell 1: Install dependencies ──
# !pip install -q transformers datasets peft bitsandbytes accelerate huggingface_hub trl

import os
import json
import torch
from pathlib import Path

# ── Configuration ──
HF_USERNAME = "YOUR_HF_USERNAME"  
HF_TOKEN = "YOUR_HF_TOKEN"       
MODEL_NAME = "medha-explainer-v1"

BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"

# ── Cell 2: Login ──
from huggingface_hub import login
login(token=HF_TOKEN)

# ── Cell 3: Load Data ──
from datasets import Dataset

def load_jsonl(filepath):
    data = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

TRAIN_PATH = "/kaggle/input/medha-explainer-data/explainer_training_data.jsonl"
if not os.path.exists(TRAIN_PATH):
    TRAIN_PATH = "data/explainer_training_data.jsonl"

dataset = Dataset.from_list(load_jsonl(TRAIN_PATH))

# Format as Instruction
def format_instruction(example):
    is_correct = "(Correct)" in example['input']
    if is_correct:
        system_prompt = "You are MEDHA, a medical exam tutor for Bangladesh students. Generate targeted study notes for a student who answered an exam question correctly to reinforce their understanding."
    else:
        system_prompt = "You are MEDHA, a medical exam tutor for Bangladesh students. Generate targeted study notes for a student who answered an exam question incorrectly."
    
    prompt = f"<|im_start|>system\n{system_prompt}\n<|im_end|>\n"
    prompt += f"<|im_start|>user\n{example['input']}\n<|im_end|>\n"
    prompt += f"<|im_start|>assistant\n{example['output']}<|im_end|>"
    return {"text": prompt}

dataset = dataset.map(format_instruction, remove_columns=["input", "output"])

# ── Cell 4: Load Model (4-bit) ──
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.pad_token = tokenizer.eos_token

model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# ── Cell 5: Train ──
from transformers import TrainingArguments
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM

# Only compute loss on assistant's response
response_template = "<|im_start|>assistant\n"
collator = DataCollatorForCompletionOnlyLM(response_template, tokenizer=tokenizer)

training_args = TrainingArguments(
    output_dir="./qwen-medha-output",
    num_train_epochs=5,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_strategy="epoch",
    warmup_ratio=0.05,
    lr_scheduler_type="cosine",
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=training_args,
    formatting_func=lambda x: x["text"],
    data_collator=collator,
    max_seq_length=512,
)

print("Starting training...")
trainer.train()

# ── Cell 6: Merge & Push ──
print("Merging LoRA weights...")
merged_model = model.merge_and_unload()

repo_id = f"{HF_USERNAME}/{MODEL_NAME}"
merged_model.push_to_hub(repo_id, private=True)
tokenizer.push_to_hub(repo_id, private=True)

print(f"Model pushed to: https://huggingface.co/{repo_id}")
