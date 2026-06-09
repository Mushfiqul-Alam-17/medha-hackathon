# MEDHA Explainer — Qwen2.5-3B Fine-tuning (Phase 2)

This directory contains the training pipeline for MEDHA's Phase 2 explanation generator. 

## Why a separate model?
The **Classifier** (BanglaBERT) is fast and small. It reads behavior and outputs a state (e.g., `PRIORITY_FOCUS`).
The **Explainer** (Qwen2.5-3B) is larger. It takes the behavioral state + the question data, and generates a personalized Bengali explanation + memory trick.

## Pipeline Steps

### 1. Generate Training Data
Run the generator locally. This uses the Gemini free API to generate targeted explanations for each question in the database.

```bash
cd app/ml/explainer
python generate_training_data.py
```
This outputs `data/explainer_training_data.jsonl`.

### 2. Train on Kaggle
1. Upload the generated `explainer_training_data.jsonl` to Kaggle as a dataset.
2. Create a new notebook with GPU T4 x2.
3. Paste the contents of `train_explainer.py` into the notebook cells.
4. Update your HuggingFace token and username in the script.
5. Run the notebook (takes ~2-3 hours).
6. The model will be pushed to HuggingFace.

### 3. Integration
Update the backend `.env` with the new explainer model ID. Future updates to `notes_service.py` will call this model instead of using rule-based assembly.
