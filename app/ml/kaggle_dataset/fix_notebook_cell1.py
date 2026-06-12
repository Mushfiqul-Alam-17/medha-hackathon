import json

path = r'c:\Users\mushf\Downloads\Medha\app\ml\kaggle_dataset\medha_explainer_final.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] != 'code': continue
    source = ''.join(cell['source'])
    
    if 'INSTALL_MARKER' in source and 'do_shutdown' in source:
        new_source = """# ── CELL 1: Install & Environment Setup ────────────────────────────────────
import os
import subprocess
import sys
import importlib

print("Installing packages...")
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-U', 
                'transformers', 'datasets', 'peft', 'bitsandbytes', 'accelerate', 'trl'])

# Invalidate python's module cache so it finds the newly installed packages WITHOUT restarting
importlib.invalidate_caches()
import site
site.main()

import warnings, json, random
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
warnings.filterwarnings('ignore')

import numpy as np, pandas as pd, torch
print(f'PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}, VRAM: {torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB x{torch.cuda.device_count()}')
print('Cell 1 complete! Ready to continue without restarting ✅')
"""
        cell['source'] = [line for line in new_source.splitlines(True)]

with open(path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print('Notebook Cell 1 patched successfully!')
