import sqlite3
from pathlib import Path

# Path to database
backend_dir = Path(__file__).parent.parent
db_path = backend_dir / "medha.db"

print(f"Connecting to database at {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get existing columns
cursor.execute("PRAGMA table_info(questions)")
columns = [col[1] for col in cursor.fetchall()]
print(f"Existing columns: {columns}")

# Add missing columns if they don't exist
added_cols = []
if "pdf_file" not in columns:
    cursor.execute("ALTER TABLE questions ADD COLUMN pdf_file TEXT")
    added_cols.append("pdf_file")
if "pdf_page" not in columns:
    cursor.execute("ALTER TABLE questions ADD COLUMN pdf_page INTEGER")
    added_cols.append("pdf_page")
if "pdf_bbox" not in columns:
    cursor.execute("ALTER TABLE questions ADD COLUMN pdf_bbox TEXT")  # SQLite TEXT stores JSON
    added_cols.append("pdf_bbox")

conn.commit()

if added_cols:
    print(f"Successfully added columns: {added_cols}")
else:
    print("No columns were missing. Database schema is up to date.")

conn.close()
