import json

path = r'c:\Users\mushf\Downloads\Medha\app\ml\kaggle_dataset\medha_explainer_final.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] != 'code': continue
    source = ''.join(cell['source'])
    
    if 'MAX_SEQ_LEN' in source and 'BATCH_SIZE' in source:
        source = source.replace('MAX_SEQ_LEN  = 512', 'MAX_SEQ_LEN  = 1024')
        source = source.replace('BATCH_SIZE   = 4', 'BATCH_SIZE   = 2')
        source = source.replace('GRAD_ACCUM   = 4', 'GRAD_ACCUM   = 8')
        
        cell['source'] = [line for line in source.splitlines(True)]

with open(path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print('Notebook Config patched successfully for MAX_SEQ_LEN=1024!')
