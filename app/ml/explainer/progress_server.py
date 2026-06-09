from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
import json
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).parent
TEMP_FILE = BASE_DIR / "data" / "explainer_training_data_temp.jsonl"
FINAL_FILE = BASE_DIR / "data" / "explainer_training_data.jsonl"
BACKUP_FILE = BASE_DIR / "data" / "explainer_training_data_backup.jsonl"

def get_total_target():
    # Dynamically compute target based on unique inputs to match regenerate_dataset.py
    questions_file = BASE_DIR.parent.parent / "backend" / "data" / "questions_clean.jsonl"
    if not questions_file.exists():
        return 1219
    try:
        import json
        questions = []
        with open(questions_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    questions.append(json.loads(line))
        seen = set()
        for q in questions:
            wrong_options = [k for k in q['options'].keys() if k != q['correct']]
            if len(wrong_options) < 3:
                w0 = wrong_options[0] if len(wrong_options) > 0 else q['correct']
                w1 = wrong_options[1] if len(wrong_options) > 1 else w0
                w2 = wrong_options[2] if len(wrong_options) > 2 else w1
            else:
                w0, w1, w2 = wrong_options[0], wrong_options[1], wrong_options[2]
            
            wrong_variants = [
                (w0, 'PRIORITY_FOCUS'),
                (w1, 'GROWTH_AREA'),
                (w2, 'PRIORITY_FOCUS'),
                (w0, 'GROWTH_AREA')
            ]
            correct_variants = [
                (q['correct'], 'MASTERY'),
                (q['correct'], 'TRUST_GAP')
            ]
            
            q_bn = q['question_bn']
            correct_val = q['options'][q['correct']]['bn']
            ch_name = q['chapter_name_bn']
            
            for wrong_letter, state in wrong_variants:
                wrong_val = q['options'][wrong_letter]['bn']
                inp = f"Question: {q_bn}\nStudent answered: {wrong_val} (Wrong)\nCorrect answer: {correct_val}\nBehavioral state: {state}\nChapter: {ch_name}\n"
                seen.add(inp.strip().replace('\r\n', '\n'))
                
            for correct_letter, state in correct_variants:
                corr_val = q['options'][correct_letter]['bn']
                inp = f"Question: {q_bn}\nStudent answered: {corr_val} (Correct)\nCorrect answer: {correct_val}\nBehavioral state: {state}\nChapter: {ch_name}\n"
                seen.add(inp.strip().replace('\r\n', '\n'))
        return len(seen)
    except Exception:
        return 1219

TOTAL_TARGET = get_total_target()

@app.get("/", response_class=HTMLResponse)
def get_progress():
    count = 0
    status = "Idle"
    last_item = None
    
    # Read temp file progress if running
    if TEMP_FILE.exists():
        status = "Regenerating data..."
        try:
            with open(TEMP_FILE, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                count = len(lines)
                if lines:
                    last_item = json.loads(lines[-1])
        except Exception as e:
            print(f"Error reading temp file: {e}")
    # If backup exists, it means we ran and completed it
    elif BACKUP_FILE.exists():
        status = "Regeneration Complete!"
        count = TOTAL_TARGET
        try:
            with open(FINAL_FILE, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                if lines:
                    last_item = json.loads(lines[-1])
        except Exception as e:
            print(f"Error reading final file: {e}")
    else:
        status = "Ready to start"
        count = 0

    percentage = min(100, round((count / TOTAL_TARGET) * 100, 1))
    
    # Parse last item for display
    last_details_html = ""
    if last_item:
        try:
            inp = last_item.get("input", "")
            out = json.loads(last_item.get("output", "{}"))
            
            # Parse input fields
            q_text, wrong_ans, correct_ans, state, chapter = "", "", "", "", ""
            is_correct_ans = False
            for line in inp.strip().split('\n'):
                if line.startswith("Question:"):
                    q_text = line[len("Question:"):].strip()
                elif line.startswith("Student answered:"):
                    wrong_ans = line[len("Student answered:"):].strip()
                    is_correct_ans = "(Correct)" in wrong_ans
                elif line.startswith("Correct answer:"):
                    correct_ans = line[len("Correct answer:"):].strip()
                elif line.startswith("Behavioral state:"):
                    state = line[len("Behavioral state:"):].strip()
                elif line.startswith("Chapter:"):
                    chapter = line[len("Chapter:"):].strip()
            
            answer_label = "Student's Answer (Correct)" if is_correct_ans else "Student's Answer (Wrong)"
            answer_class = "correct-ans" if is_correct_ans else "wrong-ans"
            
            last_details_html = f"""
            <div class="last-record-card">
                <h3>Latest Processed Record</h3>
                <div class="record-meta">
                    <span class="badge state-{state.lower()}">{state}</span>
                    <span class="badge chapter">{chapter}</span>
                </div>
                <div class="field">
                    <div class="field-label">Question</div>
                    <div class="field-value">{q_text}</div>
                </div>
                <div class="q-grid">
                    <div class="field">
                        <div class="field-label">{answer_label}</div>
                        <div class="field-value {answer_class}">{wrong_ans}</div>
                    </div>
                    <div class="field">
                        <div class="field-label">Correct Answer</div>
                        <div class="field-value correct-ans">{correct_ans}</div>
                    </div>
                </div>
                <div class="field">
                    <div class="field-label">Regenerated Explanation</div>
                    <div class="field-value">{out.get('explanation', '')}</div>
                </div>
                <div class="field">
                    <div class="field-label">Why Wrong (Misconception)</div>
                    <div class="field-value">{out.get('why_wrong', '')}</div>
                </div>
                <div class="field">
                    <div class="field-label">Memory Trick</div>
                    <div class="field-value trick-val">{out.get('memory_trick', '')}</div>
                </div>
                <div class="field">
                    <div class="field-label">Textbook Reference</div>
                    <div class="field-value ref-val">{out.get('textbook_ref', '')}</div>
                </div>
            </div>
            """
        except Exception as e:
            last_details_html = f"<div class=\"error-msg\">Error parsing last record: {e}</div>"


    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MEDHA Dataset Progress</title>
            <meta http-equiv="refresh" content="3"> <!-- Auto-refresh every 3 seconds for active visual feedback -->
            <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;500;700&display=swap" rel="stylesheet">
            <style>
                :root {{
                    --bg-dark: #090d16;
                    --card-bg: rgba(30, 41, 59, 0.4);
                    --border-color: rgba(255, 255, 255, 0.08);
                    --primary: #8b5cf6;
                    --primary-glow: rgba(139, 92, 246, 0.4);
                    --accent: #06b6d4;
                    --text-main: #f8fafc;
                    --text-muted: #94a3b8;
                    --success: #10b981;
                    --danger: #ef4444;
                }}
                
                body {{
                    font-family: 'Plus Jakarta Sans', sans-serif;
                    background: radial-gradient(circle at top, #1e1b4b 0%, var(--bg-dark) 70%);
                    color: var(--text-main);
                    min-height: 100vh;
                    margin: 0;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                    box-sizing: border-box;
                }}
                
                .container {{
                    width: 100%;
                    max-width: 750px;
                    display: flex;
                    flex-direction: column;
                    gap: 24px;
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 10px;
                }}
                
                .header h1 {{
                    font-family: 'Outfit', sans-serif;
                    font-size: 2.5rem;
                    font-weight: 800;
                    margin: 0;
                    background: linear-gradient(135deg, #a78bfa 0%, #22d3ee 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    letter-spacing: -0.5px;
                }}
                
                .header p {{
                    color: var(--text-muted);
                    font-size: 1.1rem;
                    margin: 8px 0 0 0;
                }}

                .dashboard-card {{
                    background: var(--card-bg);
                    backdrop-filter: blur(16px);
                    border: 1px solid var(--border-color);
                    border-radius: 24px;
                    padding: 32px;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
                    position: relative;
                    overflow: hidden;
                }}

                .dashboard-card::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 2px;
                    background: linear-gradient(90deg, transparent, var(--primary), var(--accent), transparent);
                }}
                
                .status-indicator {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 24px;
                }}
                
                .status-badge {{
                    background: rgba(139, 92, 246, 0.15);
                    color: #c084fc;
                    border: 1px solid rgba(139, 92, 246, 0.3);
                    padding: 6px 16px;
                    border-radius: 99px;
                    font-weight: 600;
                    font-size: 0.85rem;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                
                .pulse-dot {{
                    width: 8px;
                    height: 8px;
                    background-color: #c084fc;
                    border-radius: 50%;
                    animation: pulse 1.5s infinite;
                }}

                @keyframes pulse {{
                    0% {{ transform: scale(0.9); opacity: 1; }}
                    50% {{ transform: scale(1.3); opacity: 0.5; }}
                    100% {{ transform: scale(0.9); opacity: 1; }}
                }}
                
                .progress-box {{
                    margin: 30px 0;
                }}
                
                .progress-info {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-end;
                    margin-bottom: 12px;
                }}
                
                .percentage-label {{
                    font-family: 'Outfit', sans-serif;
                    font-size: 2.8rem;
                    font-weight: 800;
                    color: var(--text-main);
                    line-height: 1;
                }}
                
                .count-label {{
                    font-size: 1.1rem;
                    color: var(--text-muted);
                    font-weight: 500;
                }}

                .progress-bar-container {{
                    width: 100%;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 12px;
                    height: 16px;
                    overflow: hidden;
                    padding: 2px;
                    border: 1px solid rgba(255, 255, 255, 0.05);
                }}
                
                .progress-fill {{
                    width: {percentage}%;
                    background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
                    height: 100%;
                    border-radius: 8px;
                    box-shadow: 0 0 12px var(--primary-glow);
                    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
                }}
                
                .last-record-card {{
                    background: rgba(15, 23, 42, 0.6);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-radius: 20px;
                    padding: 24px;
                    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
                }}
                
                .last-record-card h3 {{
                    margin: 0 0 16px 0;
                    font-size: 1.1rem;
                    font-weight: 700;
                    letter-spacing: 0.5px;
                    text-transform: uppercase;
                    color: var(--accent);
                }}
                
                .record-meta {{
                    display: flex;
                    gap: 10px;
                    margin-bottom: 16px;
                }}
                
                .badge {{
                    font-size: 0.75rem;
                    font-weight: 700;
                    padding: 4px 10px;
                    border-radius: 6px;
                    text-transform: uppercase;
                }}
                
                .state-priority_focus {{
                    background: rgba(239, 68, 68, 0.15);
                    color: #fca5a5;
                    border: 1px solid rgba(239, 68, 68, 0.3);
                }}
                
                .state-growth_area {{
                    background: rgba(16, 185, 129, 0.15);
                    color: #a7f3d0;
                    border: 1px solid rgba(16, 185, 129, 0.3);
                }}
                
                .chapter {{
                    background: rgba(6, 182, 212, 0.15);
                    color: #a5f3fc;
                    border: 1px solid rgba(6, 182, 212, 0.3);
                }}
                
                .field {{
                    margin-bottom: 16px;
                }}
                
                .field:last-child {{
                    margin-bottom: 0;
                }}
                
                .field-label {{
                    font-size: 0.75rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    color: var(--text-muted);
                    margin-bottom: 6px;
                    letter-spacing: 0.5px;
                }}
                
                .field-value {{
                    font-size: 0.95rem;
                    line-height: 1.5;
                    color: #e2e8f0;
                }}
                
                .q-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 16px;
                    margin-bottom: 16px;
                }}
                
                .wrong-ans {{
                    color: #f87171;
                    font-weight: 600;
                }}
                
                .correct-ans {{
                    color: #34d399;
                    font-weight: 600;
                }}
                
                .trick-val {{
                    color: #fde047;
                    font-style: italic;
                }}
                
                .ref-val {{
                    color: #38bdf8;
                }}

                .footer {{
                    text-align: center;
                    font-size: 0.8rem;
                    color: #475569;
                }}
                
                .error-msg {{
                    color: var(--danger);
                    font-weight: 500;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MEDHA</h1>
                    <p>Dataset Factual Verification & Regeneration</p>
                </div>
                
                <div class="dashboard-card">
                    <div class="status-indicator">
                        <div class="status-badge">
                            <div class="pulse-dot"></div>
                            {status}
                        </div>
                        <div class="count-label">Verified: {count} / {TOTAL_TARGET}</div>
                    </div>
                    
                    <div class="progress-box">
                        <div class="progress-info">
                            <div class="percentage-label">{percentage}%</div>
                            <div class="count-label">Remaining: {TOTAL_TARGET - count}</div>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-fill"></div>
                        </div>
                    </div>
                    
                    {last_details_html}
                </div>
                
                <div class="footer">
                    Auto-refreshing progress. Powering high-quality fine-tuning data for Qwen2.5-3B.
                </div>
            </div>
        </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    import uvicorn
    print("Starting progress server at http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="warning")
