import re

with open(r'c:\Users\mushf\Downloads\Medha\app\frontend\src\DesignTemplate.js', 'r', encoding='utf-8') as f:
    c = f.read()

# Add onClick to data-screen
c = re.sub(r'data-screen="([^"]+)"', r'data-screen="\1" onClick={() => setView("\1")}', c)

# Fix nav-link active class
c = re.sub(r'className="nav-link( active)?" data-screen="([^"]+)"', r'className={`nav-link ${view === "\2" ? "active" : ""}`} data-screen="\2"', c)

# Same for sidebar-link
c = re.sub(r'className="sidebar-link( active)?" onClick=\{\(\) => setView\("([^"]+)"\)\}', r'className={`sidebar-link ${view === "\2" ? "active" : ""}`} onClick={() => setView("\2")}', c)

with open(r'c:\Users\mushf\Downloads\Medha\app\frontend\src\DesignTemplate.js', 'w', encoding='utf-8') as f:
    f.write(c)
