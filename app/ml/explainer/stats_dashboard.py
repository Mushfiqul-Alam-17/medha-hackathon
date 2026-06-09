"""
Training Data Stats Dashboard - serves on port 8001
Shows live stats and provides an interactive side-by-side search explorer for the 1,212 training records.
"""
import json, sys, re, os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = Path(r"c:\Users\mushf\Downloads\Medha\app\ml\explainer\data")
MAIN_FILE = DATA_DIR / "explainer_training_data.jsonl"
BACKUP_FILE = DATA_DIR / "explainer_training_data_backup.jsonl"
QC_FILE = Path(r"c:\Users\mushf\Downloads\Medha\app\backend\data\questions_clean.jsonl")

def get_stats():
    # Main file
    main_records = []
    if MAIN_FILE.exists():
        with open(MAIN_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        main_records.append(json.loads(line.strip()))
                    except:
                        pass
    
    # Backup
    backup_count = 0
    if BACKUP_FILE.exists():
        with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
            backup_count = sum(1 for l in f if l.strip())
    
    # Source questions
    src_count = 0
    if QC_FILE.exists():
        with open(QC_FILE, 'r', encoding='utf-8') as f:
            src_count = sum(1 for l in f if l.strip())
    
    # Analyze main records
    wrong_count = 0
    correct_count = 0
    unique_questions = set()
    chapters = {}
    states = {}
    has_textbook_ref = 0
    has_enriched_ref = 0
    quality_ok = 0
    quality_bad = 0
    
    parsed_records = []
    for i, r in enumerate(main_records):
        inp = r['input']
        out_str = r['output']
        
        # Count wrong/correct
        if '(Wrong)' in inp:
            wrong_count += 1
        elif '(Correct)' in inp:
            correct_count += 1
        
        # Extract fields
        lines = inp.strip().split('\n')
        q_text = student_ans = correct_ans = state = chapter = ""
        is_correct = False
        for line in lines:
            if line.startswith("Question:"):
                q_text = line.split(":", 1)[1].strip()
            elif line.startswith("Student answered:"):
                ans_part = line.split(":", 1)[1].strip()
                if ans_part.endswith("(Wrong)"):
                    student_ans = ans_part[:-7].strip()
                    is_correct = False
                elif ans_part.endswith("(Correct)"):
                    student_ans = ans_part[:-9].strip()
                    is_correct = True
                else:
                    student_ans = ans_part
                    is_correct = False
            elif line.startswith("Correct answer:"):
                correct_ans = line.split(":", 1)[1].strip()
            elif line.startswith("Behavioral state:"):
                state = line.split(":", 1)[1].strip()
            elif line.startswith("Chapter:"):
                chapter = line.split(":", 1)[1].strip()
        
        if q_text:
            unique_questions.add(q_text)
        if chapter:
            chapters[chapter] = chapters.get(chapter, 0) + 1
        if state:
            states[state] = states.get(state, 0) + 1
            
        try:
            out = json.loads(out_str)
            exp = out.get('explanation', '')
            why_wrg = out.get('why_wrong', '')
            mem_trck = out.get('memory_trick', '')
            txt_ref = out.get('textbook_ref', '')
            
            if txt_ref:
                has_textbook_ref += 1
            if 'পৃষ্ঠা' in txt_ref and ('আবুল হাসান' in txt_ref or 'গাজী আজমল' in txt_ref):
                has_enriched_ref += 1
            
            if len(exp) > 20 and len(mem_trck) > 5:
                quality_ok += 1
            else:
                quality_bad += 1
        except:
            out = {}
            quality_bad += 1
            
        parsed_records.append({
            "line_num": i + 1,
            "question": q_text,
            "student_answer": student_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "state": state,
            "chapter": chapter,
            "explanation": out.get('explanation', ''),
            "why_wrong": out.get('why_wrong', ''),
            "memory_trick": out.get('memory_trick', ''),
            "textbook_ref": out.get('textbook_ref', '')
        })
        
    expected = 1212  # 218 questions × 6 variants, deduped
    
    return {
        "main_count": len(main_records),
        "backup_count": backup_count,
        "source_questions": src_count,
        "expected_total": expected,
        "completion_pct": round(len(main_records) / expected * 100, 1) if expected > 0 else 0,
        "wrong_count": wrong_count,
        "correct_count": correct_count,
        "unique_questions": len(unique_questions),
        "chapters": dict(sorted(chapters.items(), key=lambda x: -x[1])),
        "states": states,
        "has_textbook_ref": has_textbook_ref,
        "has_enriched_ref": has_enriched_ref,
        "quality_ok": quality_ok,
        "quality_bad": quality_bad,
        "records": parsed_records
    }

class StatsHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            stats = get_stats()
            html = self.build_html(stats)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        elif self.path == '/api/stats':
            stats = get_stats()
            # Remove full records list from summary API to keep payload light if requested
            summary = {k: v for k, v in stats.items() if k != "records"}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(summary, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/api/records':
            stats = get_stats()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(stats["records"], ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def build_html(self, s):
        chapters_html = ""
        for ch, cnt in s['chapters'].items():
            pct = cnt / s['main_count'] * 100 if s['main_count'] > 0 else 0
            chapters_html += f"""
            <div class="chapter-row">
                <span class="ch-name">{ch}</span>
                <div class="ch-bar-bg"><div class="ch-bar" style="width:{pct}%"></div></div>
                <span class="ch-count">{cnt}</span>
            </div>"""
        
        states_html = ""
        for st, cnt in s['states'].items():
            color = {"PRIORITY_FOCUS": "#ef4444", "GROWTH_AREA": "#f59e0b", "MASTERY": "#22c55e", "TRUST_GAP": "#3b82f6"}.get(st, "#888")
            states_html += f'<div class="state-chip" style="background:{color}20;color:{color};border:1px solid {color}40">{st}: {cnt}</div>'
        
        completion_color = "#22c55e" if s['completion_pct'] >= 100 else "#f59e0b" if s['completion_pct'] >= 80 else "#ef4444"
        
        # Serialize records safely for HTML script inclusion
        records_json = json.dumps(s['records'], ensure_ascii=False)
        chapter_list = list(s['chapters'].keys())
        
        return f"""<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <title>MEDHA Training Data Explorer</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:'Inter',sans-serif; background:#0a0a0f; color:#e2e8f0; min-height:100vh; padding:24px; padding-bottom:120px; }}
        .header {{ text-align:center; margin-bottom:32px; }}
        .header h1 {{ font-size:28px; font-weight:800; background:linear-gradient(135deg,#6366f1,#a855f7,#ec4899); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
        .header p {{ color:#94a3b8; margin-top:4px; font-size:14px; }}
        .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:16px; margin-bottom:24px; }}
        .card {{ background:linear-gradient(145deg,#1e1b2e,#141420); border:1px solid #2d2b3d; border-radius:12px; padding:20px; }}
        .card .label {{ font-size:12px; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }}
        .card .value {{ font-size:32px; font-weight:800; }}
        .card .sub {{ font-size:12px; color:#64748b; margin-top:4px; }}
        .card.highlight {{ border-color:{completion_color}40; }}
        .card.highlight .value {{ color:{completion_color}; }}
        .progress-bar {{ width:100%; height:8px; background:#1e1b2e; border-radius:4px; margin-top:12px; overflow:hidden; }}
        .progress-fill {{ height:100%; background:linear-gradient(90deg,#6366f1,#a855f7); border-radius:4px; transition:width 0.5s; }}
        .section {{ background:linear-gradient(145deg,#1e1b2e,#141420); border:1px solid #2d2b3d; border-radius:12px; padding:20px; margin-bottom:16px; }}
        .section h2 {{ font-size:16px; font-weight:700; margin-bottom:16px; color:#c4b5fd; border-bottom: 1px solid #2d2b3d; padding-bottom: 8px; }}
        .chapter-row {{ display:flex; align-items:center; gap:12px; margin-bottom:8px; }}
        .ch-name {{ font-size:13px; min-width:180px; color:#cbd5e1; }}
        .ch-bar-bg {{ flex:1; height:6px; background:#1a1a2e; border-radius:3px; overflow:hidden; }}
        .ch-bar {{ height:100%; background:linear-gradient(90deg,#6366f1,#a855f7); border-radius:3px; }}
        .ch-count {{ font-size:13px; color:#94a3b8; min-width:40px; text-align:right; }}
        .state-chip {{ display:inline-block; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:600; margin:4px; }}
        .states-row {{ display:flex; flex-wrap:wrap; gap:8px; }}
        .file-info {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:12px; }}
        .file-card {{ background:#0f0f1a; border:1px solid #2d2b3d; border-radius:8px; padding:14px; }}
        .file-card .fname {{ font-size:14px; font-weight:600; color:#a78bfa; }}
        .file-card .fdetail {{ font-size:12px; color:#64748b; margin-top:4px; }}
        .quality-grid {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; }}
        .q-card {{ text-align:center; background:#0f0f1a; border-radius:8px; padding:14px; }}
        .q-card .q-val {{ font-size:24px; font-weight:700; }}
        .q-card .q-label {{ font-size:11px; color:#94a3b8; margin-top:4px; }}
        
        /* Interactive Search Explorer Styling */
        .explorer-header {{ display:flex; flex-wrap:wrap; gap:12px; align-items:center; margin-bottom:20px; background:#0f0f1a; padding:14px; border-radius:10px; border:1px solid #2d2b3d; }}
        .search-box {{ flex: 2; min-width: 250px; position: relative; }}
        .search-box input {{ width: 100%; padding: 10px 14px; background: #1a1a2a; border: 1px solid #3d3b5d; border-radius: 8px; color: #fff; font-size: 14px; outline: none; transition: border-color 0.2s; }}
        .search-box input:focus {{ border-color: #6366f1; }}
        .filter-select {{ flex: 1; min-width: 150px; }}
        .filter-select select {{ width: 100%; padding: 10px 14px; background: #1a1a2a; border: 1px solid #3d3b5d; border-radius: 8px; color: #fff; font-size: 14px; cursor: pointer; outline: none; }}
        .filter-select select:focus {{ border-color: #6366f1; }}
        
        .results-bar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 13px; color: #94a3b8; }}
        .results-count {{ font-weight: 600; color: #cbd5e1; }}
        
        .explorer-grid {{ display: flex; flex-direction: column; gap: 16px; }}
        .rec-card {{ background: linear-gradient(145deg, #181525, #0f0f1c); border: 1px solid #27253b; border-radius: 12px; padding: 16px; overflow: hidden; position: relative; transition: transform 0.1s, border-color 0.2s; }}
        .rec-card:hover {{ border-color: #4338ca; }}
        
        .rec-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed #27253b; padding-bottom: 10px; margin-bottom: 12px; }}
        .rec-line-num {{ font-size: 14px; font-weight: 700; color: #a78bfa; background: #8b5cf615; padding: 4px 8px; border-radius: 4px; }}
        .rec-meta {{ display: flex; gap: 8px; align-items: center; }}
        .rec-badge {{ font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 4px; text-transform: uppercase; }}
        .rec-badge.mastery {{ background: #22c55e15; color: #22c55e; border: 1px solid #22c55e30; }}
        .rec-badge.priority_focus {{ background: #ef444415; color: #ef4444; border: 1px solid #ef444430; }}
        .rec-badge.trust_gap {{ background: #3b82f615; color: #3b82f6; border: 1px solid #3b82f630; }}
        .rec-badge.growth_area {{ background: #f59e0b15; color: #f59e0b; border: 1px solid #f59e0b30; }}
        .rec-chapter {{ font-size: 12px; background: #1e293b; color: #94a3b8; padding: 3px 8px; border-radius: 4px; }}
        
        .rec-cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        @media (max-width: 768px) {{
            .rec-cols {{ grid-template-columns: 1fr; gap: 16px; }}
        }}
        .rec-col-left {{ border-right: 1px solid #27253b80; padding-right: 10px; }}
        @media (max-width: 768px) {{
            .rec-col-left {{ border-right: none; padding-right: 0; border-bottom: 1px solid #27253b80; padding-bottom: 12px; }}
        }}
        
        .field-group {{ margin-bottom: 10px; }}
        .field-group:last-child {{ margin-bottom: 0; }}
        .field-title {{ font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }}
        .field-value {{ font-size: 14px; line-height: 1.5; color: #cbd5e1; }}
        .field-value.question {{ font-weight: 600; color: #fff; }}
        
        .ans-pill {{ display: inline-flex; align-items: center; gap: 6px; padding: 2px 8px; border-radius: 4px; font-size: 13px; font-weight: 500; margin-top: 2px; }}
        .ans-pill.correct {{ background: #22c55e15; color: #4ade80; }}
        .ans-pill.wrong {{ background: #ef444415; color: #f87171; }}
        
        .text-trick {{ font-family: 'Inter', sans-serif; font-style: italic; color: #f472b6; font-weight: 500; }}
        .text-ref {{ color: #60a5fa; font-weight: 600; }}
        
        .load-more-btn {{ width: 100%; padding: 14px; background: #1a1a2a; border: 1px solid #2d2b3d; color: #a78bfa; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; text-align: center; margin-top: 16px; transition: background 0.2s; }}
        .load-more-btn:hover {{ background: #23233b; color: #c084fc; }}
        
        .top-nav-btn {{ position:fixed; bottom:24px; right:24px; background:linear-gradient(135deg,#6366f1,#a855f7); color:white; border:none; padding:12px 24px; border-radius:12px; font-size:14px; font-weight:600; cursor:pointer; box-shadow:0 4px 20px rgba(99,102,241,0.4); z-index: 999; }}
        .top-nav-btn:hover {{ transform:scale(1.05); }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 MEDHA Training Data Explorer</h1>
        <p>Verified Fine-tuning Dataset (Qwen2.5-3B Explainer)</p>
    </div>
    
    <div class="grid">
        <div class="card highlight">
            <div class="label">Total Records</div>
            <div class="value">{s['main_count']}</div>
            <div class="sub">Target: {s['expected_total']}</div>
            <div class="progress-bar"><div class="progress-fill" style="width:{s['completion_pct']}%"></div></div>
        </div>
        <div class="card">
            <div class="label">Completion</div>
            <div class="value" style="color:{completion_color}">{s['completion_pct']}%</div>
            <div class="sub">{'✅ COMPLETE' if s['completion_pct'] >= 100 else '⏳ Generating...'}</div>
        </div>
        <div class="card">
            <div class="label">Unique Questions</div>
            <div class="value" style="color:#a78bfa">{s['unique_questions']}</div>
            <div class="sub">From {s['source_questions']} source (24 dups)</div>
        </div>
        <div class="card">
            <div class="label">Wrong / Correct</div>
            <div class="value" style="font-size:22px"><span style="color:#ef4444">{s['wrong_count']}</span> / <span style="color:#22c55e">{s['correct_count']}</span></div>
            <div class="sub">4 wrong + 2 right per question</div>
        </div>
    </div>
    
    <div class="section">
        <h2>📚 Chapters & Syllabus Coverage</h2>
        {chapters_html}
    </div>
    
    <div class="section">
        <h2>🧠 Cognitive State Volumes</h2>
        <div class="states-row">{states_html}</div>
    </div>

    <!-- Live Search Explorer Section -->
    <div class="section" id="explorer-section">
        <h2>🔎 Training Data Live Explorer (Side-by-Side)</h2>
        
        <div class="explorer-header">
            <div class="search-box">
                <input type="text" id="explorer-search" placeholder="Search line num (e.g. 1212), question text, explanations, or memory tricks...">
            </div>
            
            <div class="filter-select">
                <select id="filter-state">
                    <option value="">All Behavioral States</option>
                    <option value="MASTERY">MASTERY</option>
                    <option value="PRIORITY_FOCUS">PRIORITY_FOCUS</option>
                    <option value="TRUST_GAP">TRUST_GAP</option>
                    <option value="GROWTH_AREA">GROWTH_AREA</option>
                </select>
            </div>
            
            <div class="filter-select">
                <select id="filter-chapter">
                    <option value="">All Chapters</option>
                    {"".join(f'<option value="{ch}">{ch}</option>' for ch in chapter_list)}
                </select>
            </div>
            
            <div class="filter-select">
                <select id="filter-correctness">
                    <option value="">All Answers</option>
                    <option value="correct">Correct Only</option>
                    <option value="wrong">Wrong Only</option>
                </select>
            </div>
        </div>
        
        <div class="results-bar">
            <div>Showing <span id="current-shown">0</span> of <span id="total-matched" class="results-count">0</span> matched records (Total: <span class="results-count">{s['main_count']}</span>)</div>
        </div>
        
        <div class="explorer-grid" id="explorer-grid">
            <!-- Cards populated dynamically via JS -->
        </div>
        
        <button class="load-more-btn" id="load-more-btn">Load More Records</button>
    </div>
    
    <button class="top-nav-btn" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}})">⬆ Scroll to Top</button>
    
    <script>
        // Injected data from backend
        const allRecords = {records_json};
        
        let filteredRecords = [...allRecords];
        let displayLimit = 50;
        
        const searchInput = document.getElementById('explorer-search');
        const stateSelect = document.getElementById('filter-state');
        const chapterSelect = document.getElementById('filter-chapter');
        const correctnessSelect = document.getElementById('filter-correctness');
        
        const gridContainer = document.getElementById('explorer-grid');
        const currentShownSpan = document.getElementById('current-shown');
        const totalMatchedSpan = document.getElementById('total-matched');
        const loadMoreBtn = document.getElementById('load-more-btn');
        
        function applyFilters() {{
            const searchVal = searchInput.value.trim().toLowerCase();
            const stateFilter = stateSelect.value;
            const chapterFilter = chapterSelect.value;
            const correctnessFilter = correctnessSelect.value;
            
            filteredRecords = allRecords.filter(r => {{
                // Chapter Filter
                if (chapterFilter && r.chapter !== chapterFilter) return false;
                
                // State Filter
                if (stateFilter && r.state !== stateFilter) return false;
                
                // Correctness Filter
                if (correctnessFilter === 'correct' && !r.is_correct) return false;
                if (correctnessFilter === 'wrong' && r.is_correct) return false;
                
                // Search Keyword Filter
                if (searchVal) {{
                    // Line number exact match
                    if (!isNaN(searchVal)) {{
                        const lineNum = parseInt(searchVal);
                        if (r.line_num === lineNum) return true;
                    }}
                    
                    const qMatch = r.question.toLowerCase().includes(searchVal);
                    const sMatch = r.student_answer.toLowerCase().includes(searchVal);
                    const cMatch = r.correct_answer.toLowerCase().includes(searchVal);
                    const eMatch = r.explanation.toLowerCase().includes(searchVal);
                    const wMatch = r.why_wrong.toLowerCase().includes(searchVal);
                    const mMatch = r.memory_trick.toLowerCase().includes(searchVal);
                    const rMatch = r.textbook_ref.toLowerCase().includes(searchVal);
                    
                    return qMatch || sMatch || cMatch || eMatch || wMatch || mMatch || rMatch;
                }}
                
                return true;
            }});
            
            displayLimit = 50;
            renderGrid();
        }}
        
        function renderGrid() {{
            const toShow = filteredRecords.slice(0, displayLimit);
            
            if (toShow.length === 0) {{
                gridContainer.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: #64748b; background: #0f0f1a; border-radius: 8px; border: 1px dashed #2d2b3d;">
                        No matching records found. Try adjusting your search query or filters.
                    </div>`;
                loadMoreBtn.style.display = 'none';
                currentShownSpan.textContent = '0';
                totalMatchedSpan.textContent = '0';
                return;
            }}
            
            let html = "";
            toShow.forEach(r => {{
                const stateClass = r.state.toLowerCase();
                const correctnessClass = r.is_correct ? 'correct' : 'wrong';
                const correctnessLabel = r.is_correct ? 'Correct' : 'Wrong';
                const correctnessSymbol = r.is_correct ? '✓' : '✗';
                
                html += `
                <div class="rec-card">
                    <div class="rec-header">
                        <span class="rec-line-num">#Line ${{r.line_num}}</span>
                        <div class="rec-meta">
                            <span class="rec-badge ${{stateClass}}">${{r.state}}</span>
                            <span class="rec-chapter">${{r.chapter}}</span>
                        </div>
                    </div>
                    <div class="rec-cols">
                        <div class="rec-col-left">
                            <div class="field-group">
                                <div class="field-title">Question</div>
                                <div class="field-value question">${{r.question}}</div>
                            </div>
                            <div class="field-group">
                                <div class="field-title">Student Choice</div>
                                <div class="field-value">
                                    <span class="ans-pill ${{correctnessClass}}">
                                        ${{correctnessSymbol}} ${{r.student_answer}} (${{correctnessLabel}})
                                    </span>
                                </div>
                            </div>
                            <div class="field-group">
                                <div class="field-title">Database Correct Answer</div>
                                <div class="field-value" style="color: #4ade80; font-weight: 500;">
                                    ${{r.correct_answer}}
                                </div>
                            </div>
                        </div>
                        <div>
                            <div class="field-group">
                                <div class="field-title">Metacognitive Explanation</div>
                                <div class="field-value">${{r.explanation}}</div>
                            </div>
                            <div class="field-group">
                                <div class="field-title">Core Misconception (why_wrong)</div>
                                <div class="field-value" style="color: #f87171;">${{r.why_wrong || 'None (Correct Answer)'}}</div>
                            </div>
                            <div class="field-group">
                                <div class="field-title">Mnemonic Memory Trick</div>
                                <div class="field-value text-trick">${{r.memory_trick}}</div>
                            </div>
                            <div class="field-group">
                                <div class="field-title">Textbook Reference</div>
                                <div class="field-value text-ref">${{r.textbook_ref}}</div>
                            </div>
                        </div>
                    </div>
                </div>`;
            }});
            
            gridContainer.innerHTML = html;
            currentShownSpan.textContent = toShow.length;
            totalMatchedSpan.textContent = filteredRecords.length;
            
            if (filteredRecords.length > displayLimit) {{
                loadMoreBtn.style.display = 'block';
            }} else {{
                loadMoreBtn.style.display = 'none';
            }}
        }}
        
        // Event Listeners
        searchInput.addEventListener('input', applyFilters);
        stateSelect.addEventListener('change', applyFilters);
        chapterSelect.addEventListener('change', applyFilters);
        correctnessSelect.addEventListener('change', applyFilters);
        
        loadMoreBtn.addEventListener('click', () => {{
            displayLimit += 50;
            renderGrid();
        }});
        
        // Initial load
        applyFilters();
    </script>
</body>
</html>"""

    def log_message(self, format, *args):
        pass  # Suppress request logs

if __name__ == '__main__':
    port = 8001
    server = HTTPServer(('0.0.0.0', port), StatsHandler)
    print(f"Stats dashboard running at http://localhost:{port}", flush=True)
    server.serve_forever()
