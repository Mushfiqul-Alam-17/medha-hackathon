import json
import sqlite3
import random
from pathlib import Path

DB_PATH = Path(__file__).parent / "medha.db"
JSONL_PATH = Path(__file__).parent.parent / "ml" / "kaggle_dataset" / "explainer_training_data.jsonl"

def load_15_questions():
    questions = []
    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            data = json.loads(line)
            input_text = data["input"]
            output_data = json.loads(data["output"])
            
            # Parse input string
            # Question: কোষ বিভাজনের সময়...
            # Student answered: রাইবোসোম (Wrong)
            # Correct answer: গলগি বস্তু
            # Behavioral state: PRIORITY_FOCUS
            # Chapter: কোষ ও কোষ অঙ্গাণু
            
            lines = input_text.split("\n")
            q_text = lines[0].replace("Question: ", "").strip()
            
            student_ans_raw = lines[1].replace("Student answered: ", "").strip()
            student_ans = student_ans_raw.split(" (")[0]
            
            correct_ans = lines[2].replace("Correct answer: ", "").strip()
            chapter = lines[4].replace("Chapter: ", "").strip()
            
            explanation = output_data.get("explanation", "")
            memory_trick = output_data.get("memory_trick", "")
            
            # Skip if we don't have distinct wrong vs correct (some are (Correct))
            if "(Wrong)" not in student_ans_raw:
                continue
                
            # Create a question with 4 options
            options = [correct_ans, student_ans, "লাইসোসোম", "মাইটোকন্ড্রিয়া"]
            random.shuffle(options)
            correct_idx = options.index(correct_ans)
            correct_letter = ["A", "B", "C", "D"][correct_idx]
            
            # Check for duplicates
            if not any(q['question_bn'] == q_text for q in questions):
                questions.append({
                    "chapter_name": chapter,
                    "question_bn": q_text,
                    "option_a_bn": options[0],
                    "option_b_bn": options[1],
                    "option_c_bn": options[2],
                    "option_d_bn": options[3],
                    "correct": correct_letter,
                    "explanation_bn": explanation,
                    "memory_trick": memory_trick
                })
            
            if len(questions) >= 15:
                break
                
    # Insert into DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Let's just insert these 15 questions and give them a special chapter_code so they are queried easily
    special_chapter = "TEST15"
    
    for q in questions:
        c.execute("""
            INSERT INTO questions 
            (chapter_code, chapter_name, question_bn, option_a_bn, option_b_bn, option_c_bn, option_d_bn, correct, explanation_bn, memory_trick, difficulty) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            special_chapter, q["chapter_name"], q["question_bn"], 
            q["option_a_bn"], q["option_b_bn"], q["option_c_bn"], q["option_d_bn"],
            q["correct"], q["explanation_bn"], q["memory_trick"], "medium"
        ))
    
    conn.commit()
    conn.close()
    print(f"Loaded {len(questions)} questions into DB with chapter_code='TEST15'.")

if __name__ == "__main__":
    load_15_questions()
