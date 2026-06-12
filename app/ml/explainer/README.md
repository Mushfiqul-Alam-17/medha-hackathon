# MEDHA Explainer — Qwen2.5-3B Fine-tuning (Phase 2)

This directory contains the training pipeline for MEDHA's Phase 2 explanation generator. 

## Why a separate model?
The **Classifier** (BanglaBERT) is fast and small. It reads behavior and outputs a state (e.g., `PRIORITY_FOCUS`).
The **Explainer** (Qwen2.5-3B) is larger. It takes the behavioral state + the question data, and generates a personalized Bengali explanation + memory trick.

## Step-by-Step Training on Kaggle (Free)

### STEP 1: Generate Training Data (If not already done)
Run the generator locally. This uses the Gemini free API to generate targeted explanations for each question in the database.

```bash
cd app/ml/explainer
python generate_training_data.py
```
This outputs `data/explainer_training_data.jsonl`.

### STEP 2: Upload Data to Kaggle
1. Go to https://kaggle.com → Sign In (create account if needed)
2. Click **Datasets** → **New Dataset**
3. Dataset name: `medha-ml-dataset`
4. Upload all 3 files from `app/ml/kaggle_dataset/`
5. Set visibility: **Private**
6. Click **Create**

### STEP 3: Create Kaggle Notebook
1. Click **Code** → **New Notebook**
2. Name: `medha-explainer-training`
3. In **Settings** (right sidebar):
   - **Accelerator:** `GPU T4 x2`
   - **Internet:** `On` (required to download Qwen model)
   - **Persistence:** `Files only`
4. Click **Add data** → search your `medha-ml-dataset` dataset → Add
5. **Add Hugging Face Token:** Under "Secrets" (or Add-ons -> Secrets), add your Hugging Face write token as `HF_TOKEN`.

### STEP 4: Run Training Script
The script for training is found in `train_explainer.py`. 
1. Copy the entire contents of `train_explainer.py` into a single cell in your Kaggle notebook (or break it into cells as denoted by the `# ── CELL X ──` markers).
2. Update the `HF_USERNAME` variable at the top to your actual Hugging Face username.
3. Update the `HF_TOKEN` variable to your token, or use Kaggle Secrets (e.g., `from kaggle_secrets import UserSecretsClient; HF_TOKEN = UserSecretsClient().get_secret("HF_TOKEN")`).
4. Run the notebook! Expected training time: 2-3 hours.
5. The model will merge its LoRA weights and automatically push itself to HuggingFace.

## Troubleshooting

- **Dataset Not Found Error**: Double check your Kaggle dataset path (`/kaggle/input/medha-ml-dataset/explainer_training_data.jsonl`) matches what you named the dataset.
- **CUDA OOM**: Reduce `BATCH_SIZE` in the configuration.
- **Double-formatting bug**: Ensure `trl>=0.8` is used as specified in the dependencies. The script uses `dataset_text_field`.

## Integration (For Later)

After the Qwen explainer finishes training and is uploaded to Hugging Face:
1. Take the generated Hugging Face model ID (e.g. `your_username/medha-explainer-v1`).
2. Update the backend `.env` file with the new explainer model ID:
   ```env
   HF_EXPLAINER_ID=your_username/medha-explainer-v1
   ```
3. Update the backend services (`app/backend/services/notes_service.py` or equivalent) to invoke your newly fine-tuned model via Hugging Face inference API or locally. (Detailed integration instructions can be requested when you are ready).
