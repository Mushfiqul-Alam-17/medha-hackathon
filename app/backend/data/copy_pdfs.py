import os
import shutil
from pathlib import Path

backend_dir = Path(__file__).parent.parent
dest_dir = backend_dir / "static" / "pdfs"

# Ensure destination directory exists
dest_dir.mkdir(parents=True, exist_ok=True)

src_pdf1 = r"c:\Users\mushf\Downloads\Medha\ABUL HASAN BIO 1st paper.pdf"
src_pdf2 = r"c:\Users\mushf\Downloads\Medha\Azmol BIO 2nd paper.pdf"

dest_pdf1 = dest_dir / "ABUL_HASAN_BIO_1st_paper.pdf"
dest_pdf2 = dest_dir / "Azmol_BIO_2nd_paper.pdf"

print("Copying PDFs to static directory...")

if os.path.exists(src_pdf1):
    print(f"Copying {src_pdf1} -> {dest_pdf1}...")
    shutil.copy2(src_pdf1, dest_pdf1)
    print("  Botany PDF copied successfully.")
else:
    print(f"ERROR: {src_pdf1} not found.")

if os.path.exists(src_pdf2):
    print(f"Copying {src_pdf2} -> {dest_pdf2}...")
    shutil.copy2(src_pdf2, dest_pdf2)
    print("  Zoology PDF copied successfully.")
else:
    print(f"ERROR: {src_pdf2} not found.")

print("\nDone copying!")
