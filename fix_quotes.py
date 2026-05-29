import os
from pathlib import Path

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple replacement of \" with "
    if r'\"' in content:
        content = content.replace(r'\"', '"')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filepath}")

def main():
    target_dir = Path(r"c:\Users\mushf\Downloads\Medha\app")
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.py', '.js', '.jsx', '.css', '.html')):
                filepath = os.path.join(root, file)
                fix_file(filepath)

if __name__ == "__main__":
    main()
