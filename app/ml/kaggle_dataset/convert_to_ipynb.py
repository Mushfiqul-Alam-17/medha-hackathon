import json
import re

def py_to_ipynb(py_filepath, ipynb_filepath):
    with open(py_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split the file into cells based on the '# ── CELL' or similar comments
    # First, let's just split by `# ── CELL`
    raw_cells = re.split(r'(?=# ── CELL)', content)
    
    notebook = {
        "cells": [],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.10.12"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    for raw_cell in raw_cells:
        if not raw_cell.strip():
            continue
            
        # Is this the top docstring? If so, make it a markdown cell
        if raw_cell.strip().startswith('"""') and '# ── CELL' not in raw_cell:
            # Try to extract the markdown content
            md_content = raw_cell.strip().strip('"""').strip()
            cell = {
                "cell_type": "markdown",
                "metadata": {},
                "source": [line + '\n' for line in md_content.split('\n')]
            }
            notebook["cells"].append(cell)
            continue

        # If it's a code cell, we need to handle it.
        # Ensure we don't end up with completely empty cells.
        source_lines = [line + '\n' for line in raw_cell.split('\n')]
        # Remove the very last newline if it's there, to keep it clean
        if source_lines and source_lines[-1] == '\n':
            source_lines.pop()

        cell = {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": source_lines
        }
        notebook["cells"].append(cell)

    with open(ipynb_filepath, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    
    print(f"Created {ipynb_filepath}")

if __name__ == "__main__":
    py_to_ipynb(
        r"c:\Users\mushf\Downloads\Medha\app\ml\classifier\train_classifier.py",
        r"c:\Users\mushf\Downloads\Medha\app\ml\kaggle_dataset\medha_classifier_training.ipynb"
    )
    py_to_ipynb(
        r"c:\Users\mushf\Downloads\Medha\app\ml\explainer\train_explainer.py",
        r"c:\Users\mushf\Downloads\Medha\app\ml\kaggle_dataset\medha_explainer_training.ipynb"
    )
