"""
MEDHA — NCTB PDF Highlight Mapper
Reads NCTB Biology PDFs, extracts paragraphs and bounding boxes,
and maps our 218 database questions to specific textbook locations.

Requirements:
    pip install PyMuPDF scikit-learn
"""

import fitz  # PyMuPDF
import json
import os
import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Directories
BASE_DIR = Path(__file__).parent
PDF_DIR = BASE_DIR / "pdfs"
QUESTIONS_FILE = BASE_DIR / "questions_clean.jsonl"
OUTPUT_MAPPING_FILE = BASE_DIR / "question_pdf_mapping.json"

def clean_text(text):
    """Clean extracted Bengali text for better matching."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\u0980-\u09FFa-zA-Z0-9\s]', '', text) # Keep Bengali and English alphanumeric
    return text.strip()

def extract_paragraphs_with_bboxes(pdf_path):
    """
    Extracts text blocks from a PDF along with their page numbers and coordinates.
    Returns a list of dicts: {"page": int, "text": str, "bbox": [x0, y0, x1, y1]}
    """
    print(f"Reading {pdf_path.name}...")
    doc = fitz.open(pdf_path)
    paragraphs = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("blocks")
        
        for b in blocks:
            # Block format: (x0, y0, x1, y1, "text", block_no, block_type)
            # block_type 0 is text
            if b[6] == 0:
                text = b[4].replace('\n', ' ').strip()
                if len(text) > 30: # Ignore tiny fragments/page numbers
                    paragraphs.append({
                        "file": pdf_path.name,
                        "page": page_num + 1, # 1-indexed for humans
                        "text": text,
                        "clean_text": clean_text(text),
                        "bbox": [round(b[0], 2), round(b[1], 2), round(b[2], 2), round(b[3], 2)]
                    })
    
    doc.close()
    print(f"Extracted {len(paragraphs)} valid text blocks from {pdf_path.name}")
    return paragraphs

def map_questions_to_pdf(paragraphs, questions):
    """
    Uses TF-IDF Cosine Similarity to find the best matching textbook paragraph
    for each question.
    """
    print("Building TF-IDF Index...")
    
    corpus = [p["clean_text"] for p in paragraphs]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    mapping = {}
    matched_count = 0
    
    for q in questions:
        # We search using the question text AND the correct answer text
        correct_ans_letter = q["correct"]
        correct_ans_text = q["options"][correct_ans_letter]["bn"]
        
        search_query = clean_text(f"{q['question_bn']} {correct_ans_text}")
        query_vec = vectorizer.transform([search_query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
        
        # Get best match
        best_idx = similarities.argmax()
        best_score = similarities[best_idx]
        
        # Threshold: Only map if similarity is reasonably high (e.g., > 0.15 for short queries)
        if best_score > 0.15:
            best_para = paragraphs[best_idx]
            mapping[q["id"]] = {
                "file": best_para["file"],
                "page": best_para["page"],
                "bbox": best_para["bbox"],
                "match_score": round(best_score, 3),
                "matched_text": best_para["text"][:100] + "..." # Save snippet for review
            }
            matched_count += 1
        else:
            mapping[q["id"]] = None # No confident match found
            
    print(f"Successfully mapped {matched_count}/{len(questions)} questions to textbook coordinates.")
    return mapping

def run():
    PDF_DIR.mkdir(exist_ok=True)
    
    # 1. Check for PDFs
    pdf_files = list(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"ERROR: No PDF files found in {PDF_DIR}")
        print("Please place the NCTB Biology PDFs (e.g., biology_1st_paper.pdf) in that directory.")
        return

    # 2. Load Questions
    if not QUESTIONS_FILE.exists():
        print(f"ERROR: Questions file not found at {QUESTIONS_FILE}")
        return
        
    questions = []
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            questions.append(json.loads(line.strip()))
            
    print(f"Loaded {len(questions)} questions.")

    # 3. Extract all paragraphs from all PDFs
    all_paragraphs = []
    for pdf_path in pdf_files:
        paras = extract_paragraphs_with_bboxes(pdf_path)
        all_paragraphs.extend(paras)
        
    if not all_paragraphs:
        print("Failed to extract text from PDFs. Make sure they are not scanned images.")
        return

    # 4. Map questions to coordinates
    mapping = map_questions_to_pdf(all_paragraphs, questions)

    # 5. Save results
    with open(OUTPUT_MAPPING_FILE, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
        
    print(f"\nMapping saved to {OUTPUT_MAPPING_FILE}")
    print("Next step: Update backend load_questions.py to inject these coordinates into the SQLite DB.")

if __name__ == "__main__":
    run()
