"""
Training Data Stats Dashboard - serves on port 8001
Shows live stats of the training dataset generation.
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
    
    for r in main_records:
        inp = r['input']
        
        # Count wrong/correct
        if '(Wrong)' in inp:
            wrong_count += 1
        elif '(Correct)' in inp:
            correct_count += 1
        
        # Extract question
        q_m = re.search(r"Question:\s*(.*?)\n", inp)
        if q_m:
            unique_questions.add(q_m.group(1).strip())
        
        # Chapter
        ch_m = re.search(r"Chapter:\s*(.*?)\n", inp)
        if ch_m:
            ch = ch_m.group(1).strip()
            chapters[ch] = chapters.get(ch, 0) + 1
        
        # State
        s_m = re.search(r"Behavioral state:\s*(.*?)\n", inp)
        if s_m:
            s = s_m.group(1).strip()
            states[s] = states.get(s, 0) + 1
        
        # Output quality
        try:
            out = json.loads(r['output'])
            exp = out.get('explanation', '')
            mem = out.get('memory_trick', '')
            ref = out.get('textbook_ref', '')
            
            if ref:
                has_textbook_ref += 1
            if 'পৃষ্ঠা' in ref and ('আবুল হাসান' in ref or 'গাজী আজমল' in ref):
                has_enriched_ref += 1
            
            if len(exp) > 20 and len(mem) > 5:
                quality_ok += 1
            else:
                quality_bad += 1
        except:
            quality_bad += 1
    
    # Expected total
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
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(stats, ensure_ascii=False).encode('utf-8'))
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
        
        return f"""<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <title>MEDHA Training Data Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:'Inter',sans-serif; background:#0a0a0f; color:#e2e8f0; min-height:100vh; padding:24px; }}
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
        .section h2 {{ font-size:16px; font-weight:700; margin-bottom:16px; color:#c4b5fd; }}
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
        .refresh-btn {{ position:fixed; bottom:24px; right:24px; background:linear-gradient(135deg,#6366f1,#a855f7); color:white; border:none; padding:12px 24px; border-radius:12px; font-size:14px; font-weight:600; cursor:pointer; box-shadow:0 4px 20px rgba(99,102,241,0.4); }}
        .refresh-btn:hover {{ transform:scale(1.05); }}
        .badge {{ display:inline-block; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700; }}
        .badge.active {{ background:#22c55e20; color:#22c55e; }}
        .badge.old {{ background:#f59e0b20; color:#f59e0b; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 MEDHA Training Data Dashboard</h1>
        <p>Qwen2.5-3B Explainer Fine-tuning Dataset</p>
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
        <h2>📁 Files</h2>
        <div class="file-info">
            <div class="file-card">
                <div class="fname">explainer_training_data.jsonl <span class="badge active">MAIN</span></div>
                <div class="fdetail">{s['main_count']} records • This is the file used for training</div>
            </div>
            <div class="file-card">
                <div class="fname">explainer_training_data_backup.jsonl <span class="badge old">BACKUP</span></div>
                <div class="fdetail">{s['backup_count']} records • Old partial run (first generation attempt)</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>✅ Quality Metrics</h2>
        <div class="quality-grid">
            <div class="q-card">
                <div class="q-val" style="color:#22c55e">{s['quality_ok']}</div>
                <div class="q-label">Good Quality</div>
            </div>
            <div class="q-card">
                <div class="q-val" style="color:#ef4444">{s['quality_bad']}</div>
                <div class="q-label">Needs Fix</div>
            </div>
            <div class="q-card">
                <div class="q-val" style="color:#a78bfa">{s['has_enriched_ref']}</div>
                <div class="q-label">Enriched Textbook Refs</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>🧠 Behavioral States</h2>
        <div class="states-row">{states_html}</div>
    </div>
    
    <div class="section">
        <h2>📚 Chapters Distribution</h2>
        {chapters_html}
    </div>
    
    <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
    
    <script>
        // Auto-refresh every 10 seconds while generating
        setTimeout(() => location.reload(), 10000);
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
