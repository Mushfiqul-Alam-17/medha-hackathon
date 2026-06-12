import json

path = r'c:\Users\mushf\Downloads\Medha\app\ml\kaggle_dataset\medha_explainer_final.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] != 'code': continue
    source = ''.join(cell['source'])
    
    if 'train_result = trainer.train()' in source and 'trainer.save_model' in source:
        source = source.replace(
            'train_result = None\ntry:\n',
            'train_result = None\n# 🛠️ FIX: Patch state_dict to prevent bitsandbytes CUDA illegal memory access on dual GPU\nold_state_dict = trainer.model.state_dict\ntrainer.model.state_dict = lambda *args, **kwargs: {k: v for k, v in trainer.model.named_parameters() if v.requires_grad}\n\ntry:\n'
        )
        source = source.replace(
            'print("Checkpoint saved to ./qwen-medha-checkpoint ✅")',
            'print("Checkpoint saved to ./qwen-medha-checkpoint ✅")\n\n# Restore state_dict just in case\ntrainer.model.state_dict = old_state_dict'
        )
        cell['source'] = [line for line in source.splitlines(True)]

    if 'merged_model = model.merge_and_unload()' in source:
        source = source.replace(
            'print("Merging LoRA weights into base model...")\nprint("(This takes 2-3 minutes — model grows from ~2GB to ~6GB)")\n\ntry:\n    merged_model = model.merge_and_unload()\n    print("LoRA merge complete ✅")\n',
            'print("Pushing LoRA adapter to HuggingFace...")\nprint("(Pushing adapter directly prevents multi-GPU merge crashes and is much faster)")\n\ntry:\n'
        )
        source = source.replace('merged_model.push_to_hub(repo_id', 'model.push_to_hub(repo_id')
        source = source.replace('merged_model.save_pretrained("./qwen-medha-final")', 'model.save_pretrained("./qwen-medha-final")')
        source = source.replace('Fallback: saving model locally', 'Fallback: saving adapter locally')
        source = source.replace('(This uploads ~6GB — takes 5-10 minutes)', '(This uploads ~100MB — takes <1 minute)')
        cell['source'] = [line for line in source.splitlines(True)]

    if 'OPTION B: Local inference' in source:
        source = source.replace(
            'from transformers import pipeline\npipe = pipeline("text-generation", model="{repo_id}", device_map="auto")\n# Then call pipe(prompt, max_new_tokens=300)\n',
            'from transformers import AutoModelForCausalLM, AutoTokenizer\nfrom peft import PeftModel\nimport torch\n\nbase = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-3B-Instruct", torch_dtype=torch.float16, device_map="auto")\nmodel = PeftModel.from_pretrained(base, f"{repo_id}")\ntokenizer = AutoTokenizer.from_pretrained(f"{repo_id}")\n# Generate as usual with model.generate(...)\n'
        )
        cell['source'] = [line for line in source.splitlines(True)]

with open(path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print('Notebook patched successfully!')
