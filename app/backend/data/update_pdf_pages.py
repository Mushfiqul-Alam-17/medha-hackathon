import sqlite3
import os
from pathlib import Path

# Path to database
backend_dir = Path(__file__).parent.parent
db_path = backend_dir / "medha.db"

print(f"Connecting to database at {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Define chapter mappings:
# Chapter Code -> (PDF Filename, PDF Starting Page Number in PDF viewer)
# Note: PDF page offset is generally Book Page + 6
chapter_mappings = {
    # 1st Paper - Botany (Abul Hasan)
    "BIO-C01": ("ABUL_HASAN_BIO_1st_paper.pdf", 7),     # কোষ ও কোষ অঙ্গাণু (Book page 1)
    "BIO-C02": ("ABUL_HASAN_BIO_1st_paper.pdf", 51),    # কোষ বিভাজন (Book page 45)
    "BIO-C04": ("ABUL_HASAN_BIO_1st_paper.pdf", 366),   # জীবপ্রযুক্তি (Book page 360)
    "BIO-C05": ("ABUL_HASAN_BIO_1st_paper.pdf", 126),   # অণুজীব ও ভাইরাস (Book page 120)
    "BIO-C06": ("ABUL_HASAN_BIO_1st_paper.pdf", 221),   # উদ্ভিদবিজ্ঞান ও শ্রেণীবিন্যাস (Book page 215)
    "BIO-C07": ("ABUL_HASAN_BIO_1st_paper.pdf", 281),   # উদ্ভিদ শরীরতত্ত্ব (Book page 275)
    
    # 2nd Paper - Zoology (Gazi Azmal)
    "BIO-C03": ("Azmol_BIO_2nd_paper.pdf", 391),       # জিনতত্ত্ব ও বিবর্তন (Book page 385)
    "BIO-C08": ("Azmol_BIO_2nd_paper.pdf", 7),         # প্রাণীর বিভিন্নতা (Book page 1)
    "BIO-C09": ("Azmol_BIO_2nd_paper.pdf", 96),        # পরিপাক তন্ত্র (Book page 90)
    "BIO-C10": ("Azmol_BIO_2nd_paper.pdf", 141),       # সংবহন তন্ত্র (Book page 135)
    "BIO-C11": ("Azmol_BIO_2nd_paper.pdf", 186),       # শ্বসন তন্ত্র (Book page 180)
    "BIO-C12": ("Azmol_BIO_2nd_paper.pdf", 216),       # রেচন তন্ত্র (Book page 210)
    "BIO-C13": ("Azmol_BIO_2nd_paper.pdf", 271),       # স্নায়ুতন্ত্র (Book page 265)
    "BIO-C14": ("Azmol_BIO_2nd_paper.pdf", 271),       # অন্তঃক্ষরা তন্ত্র (Book page 265)
    "BIO-C15": ("Azmol_BIO_2nd_paper.pdf", 241),       # কঙ্কাল ও পেশী তন্ত্র (Book page 235)
    "BIO-C16": ("Azmol_BIO_2nd_paper.pdf", 326),       # জনন তন্ত্র (Book page 320)
    "BIO-C17": ("Azmol_BIO_2nd_paper.pdf", 361),       # রোগ প্রতিরোধ ও রক্তের গ্রুপ (Book page 355)
    "BIO-C18": ("Azmol_BIO_2nd_paper.pdf", 271),       # ইন্দ্রিয় তন্ত্র (Book page 265)
    
    # General / Miscellaneous defaults to Zoology Chapter 1
    "BIO-C19": ("Azmol_BIO_2nd_paper.pdf", 7)
}

updated_count = 0
for code, (pdf_file, pdf_page) in chapter_mappings.items():
    cursor.execute(
        "UPDATE questions SET pdf_file = ?, pdf_page = ? WHERE chapter_code = ?",
        (pdf_file, pdf_page, code)
    )
    affected = cursor.rowcount
    updated_count += affected
    print(f"  Chapter {code}: updated {affected} questions to {pdf_file} page {pdf_page}")

conn.commit()
print(f"\n[SUCCESS] Updated a total of {updated_count} questions in the database.")

# Double check counts
cursor.execute("SELECT COUNT(*) FROM questions WHERE pdf_file IS NULL")
null_count = cursor.fetchone()[0]
print(f"Questions remaining with null pdf_file: {null_count}")

conn.close()
