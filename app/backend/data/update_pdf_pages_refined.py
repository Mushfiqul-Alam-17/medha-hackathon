import sqlite3
import re
from pathlib import Path

# Path to database
backend_dir = Path(__file__).parent.parent
db_path = backend_dir / "medha.db"

print(f"Connecting to database at {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Fetch all questions
cursor.execute("SELECT id, question_bn, correct, option_a_bn, option_b_bn, option_c_bn, option_d_bn, chapter_code, chapter_name FROM questions")
questions = cursor.fetchall()

# Chapter level defaults as fallbacks
chapter_defaults = {
    # 1st Paper - Botany (Abul Hasan)
    "BIO-C01": ("ABUL_HASAN_BIO_1st_paper.pdf", 7),
    "BIO-C02": ("ABUL_HASAN_BIO_1st_paper.pdf", 51),
    "BIO-C04": ("ABUL_HASAN_BIO_1st_paper.pdf", 366),
    "BIO-C05": ("ABUL_HASAN_BIO_1st_paper.pdf", 126),
    "BIO-C06": ("ABUL_HASAN_BIO_1st_paper.pdf", 221),
    "BIO-C07": ("ABUL_HASAN_BIO_1st_paper.pdf", 281),
    
    # 2nd Paper - Zoology (Gazi Azmol)
    "BIO-C03": ("Azmol_BIO_2nd_paper.pdf", 391),
    "BIO-C08": ("Azmol_BIO_2nd_paper.pdf", 7),
    "BIO-C09": ("Azmol_BIO_2nd_paper.pdf", 96),
    "BIO-C10": ("Azmol_BIO_2nd_paper.pdf", 141),
    "BIO-C11": ("Azmol_BIO_2nd_paper.pdf", 186),
    "BIO-C12": ("Azmol_BIO_2nd_paper.pdf", 216),
    "BIO-C13": ("Azmol_BIO_2nd_paper.pdf", 271),
    "BIO-C14": ("Azmol_BIO_2nd_paper.pdf", 271),
    "BIO-C15": ("Azmol_BIO_2nd_paper.pdf", 241),
    "BIO-C16": ("Azmol_BIO_2nd_paper.pdf", 326),
    "BIO-C17": ("Azmol_BIO_2nd_paper.pdf", 361),
    "BIO-C18": ("Azmol_BIO_2nd_paper.pdf", 271),
    "BIO-C19": ("Azmol_BIO_2nd_paper.pdf", 7)
}

# Refined Keyword rules (Keyword -> (PDF Filename, Page Number))
# Ordered by priority (specific/multi-word terms first, general/short terms last)
keywords_rules = [
    # --- Multi-word and high-specificity terms first ---
    ("কোষ প্রাচীর", ("ABUL_HASAN_BIO_1st_paper.pdf", 8)),
    ("কোষঝিল্লি", ("ABUL_HASAN_BIO_1st_paper.pdf", 11)),
    ("কোষ ঝিল্লি", ("ABUL_HASAN_BIO_1st_paper.pdf", 11)),
    ("প্লাজমামেমব্রেন", ("ABUL_HASAN_BIO_1st_paper.pdf", 11)),
    ("প্লাজমা মেমব্রেন", ("ABUL_HASAN_BIO_1st_paper.pdf", 11)),
    ("ফ্লুইড মোজাইক", ("ABUL_HASAN_BIO_1st_paper.pdf", 11)),
    
    ("টিস্যু কালচার", ("ABUL_HASAN_BIO_1st_paper.pdf", 366)),
    ("টিস্যুকালচার", ("ABUL_HASAN_BIO_1st_paper.pdf", 366)),
    ("রিকম্বিনেন্ট ডিএনএ", ("ABUL_HASAN_BIO_1st_paper.pdf", 371)),
    ("রিকম্বিনেন্ট", ("ABUL_HASAN_BIO_1st_paper.pdf", 371)),
    ("রিকম্বিনেট", ("ABUL_HASAN_BIO_1st_paper.pdf", 371)),
    ("রেস্ট্রিকশন এনজাইম", ("ABUL_HASAN_BIO_1st_paper.pdf", 371)),
    ("রেস্ট্রিকশন", ("ABUL_HASAN_BIO_1st_paper.pdf", 371)),
    ("প্লাজমিড", ("ABUL_HASAN_BIO_1st_paper.pdf", 371)),
    
    ("কোষ বিভাজন", ("ABUL_HASAN_BIO_1st_paper.pdf", 54)),
    ("কোষ চক্র", ("ABUL_HASAN_BIO_1st_paper.pdf", 54)),
    ("কোষচক্র", ("ABUL_HASAN_BIO_1st_paper.pdf", 54)),
    ("মাইটোসিস", ("ABUL_HASAN_BIO_1st_paper.pdf", 54)),
    ("মিওসিস", ("ABUL_HASAN_BIO_1st_paper.pdf", 62)),
    ("ক্রসিং ওভার", ("Azmol_BIO_2nd_paper.pdf", 391)),
    ("ক্রসিংওভার", ("Azmol_BIO_2nd_paper.pdf", 391)),
    
    # Gymnosperms / Cycas
    ("সাইকাস", ("ABUL_HASAN_BIO_1st_paper.pdf", 226)),
    ("Cycas", ("ABUL_HASAN_BIO_1st_paper.pdf", 226)),
    
    ("অগ্নিশৈবাল", ("ABUL_HASAN_BIO_1st_paper.pdf", 181)),
    ("স্পিরোবাইরা", ("ABUL_HASAN_BIO_1st_paper.pdf", 181)),
    ("ডায়াটম", ("ABUL_HASAN_BIO_1st_paper.pdf", 181)),
    ("পাইরোফাইটা", ("ABUL_HASAN_BIO_1st_paper.pdf", 181)),
    ("প্রোটোনেমা", ("ABUL_HASAN_BIO_1st_paper.pdf", 206)),
    
    ("অনাল গ্রন্থি", ("Azmol_BIO_2nd_paper.pdf", 271)),
    ("ঐচ্ছিক পেশী", ("Azmol_BIO_2nd_paper.pdf", 248)),
    ("ঐচ্ছিক পেশি", ("Azmol_BIO_2nd_paper.pdf", 248)),
    ("রক্তের গ্রুপ", ("Azmol_BIO_2nd_paper.pdf", 361)),
    ("রক্তেরগ্রুপ", ("Azmol_BIO_2nd_paper.pdf", 361)),
    
    ("ম্যালেরিয়া", ("ABUL_HASAN_BIO_1st_paper.pdf", 155)),
    ("ম্যালেরিয়া", ("ABUL_HASAN_BIO_1st_paper.pdf", 155)),
    ("ভাইরাস", ("ABUL_HASAN_BIO_1st_paper.pdf", 126)),
    ("ব্যাকটেরিয়া", ("ABUL_HASAN_BIO_1st_paper.pdf", 142)),
    ("ব্যাকটেরিয়া", ("ABUL_HASAN_BIO_1st_paper.pdf", 142)),
    
    # --- Specific single-word terms ---
    ("গলগি বস্তু", ("ABUL_HASAN_BIO_1st_paper.pdf", 20)),
    ("গলগিবডি", ("ABUL_HASAN_BIO_1st_paper.pdf", 20)),
    ("গলগি বডি", ("ABUL_HASAN_BIO_1st_paper.pdf", 20)),
    ("রাইবোসোম", ("ABUL_HASAN_BIO_1st_paper.pdf", 15)),
    ("লাইসোসোম", ("ABUL_HASAN_BIO_1st_paper.pdf", 22)),
    ("মাইটোকন্ড্রিয়া", ("ABUL_HASAN_BIO_1st_paper.pdf", 24)),
    ("প্লাস্টিড", ("ABUL_HASAN_BIO_1st_paper.pdf", 28)),
    ("ক্লোরোপ্লাস্ট", ("ABUL_HASAN_BIO_1st_paper.pdf", 28)),
    ("কোষ গহ্বর", ("ABUL_HASAN_BIO_1st_paper.pdf", 23)),
    ("সুকেন্দ্রিক", ("ABUL_HASAN_BIO_1st_paper.pdf", 33)),
    ("নিউক্লিয়াস", ("ABUL_HASAN_BIO_1st_paper.pdf", 33)),
    ("ক্রোমোজোম", ("ABUL_HASAN_BIO_1st_paper.pdf", 37)),
    ("অনুলিখন", ("ABUL_HASAN_BIO_1st_paper.pdf", 43)),
    ("ট্রান্সক্রিপশন", ("ABUL_HASAN_BIO_1st_paper.pdf", 43)),
    ("ট্রান্সলেশন", ("ABUL_HASAN_BIO_1st_paper.pdf", 47)),
    ("Translation", ("ABUL_HASAN_BIO_1st_paper.pdf", 47)),
    ("pH রক্ষা", ("ABUL_HASAN_BIO_1st_paper.pdf", 23)),
    
    ("প্রোফেজ", ("ABUL_HASAN_BIO_1st_paper.pdf", 56)),
    ("মেটাফেজ", ("ABUL_HASAN_BIO_1st_paper.pdf", 57)),
    ("অ্যানাফেজ", ("ABUL_HASAN_BIO_1st_paper.pdf", 59)),
    ("টেলোফেজ", ("ABUL_HASAN_BIO_1st_paper.pdf", 60)),
    
    ("এক্সপ্লান্ট", ("ABUL_HASAN_BIO_1st_paper.pdf", 366)),
    ("এমব্রায়োজেনেসিস", ("ABUL_HASAN_BIO_1st_paper.pdf", 366)),
    ("সোমাটিক", ("ABUL_HASAN_BIO_1st_paper.pdf", 366)),
    
    ("ভিরিয়ন", ("ABUL_HASAN_BIO_1st_paper.pdf", 126)),
    ("প্রিয়ন", ("ABUL_HASAN_BIO_1st_paper.pdf", 126)),
    ("অ্যাসেপটিক", ("ABUL_HASAN_BIO_1st_paper.pdf", 126)),
    ("অ্যাসপটিক", ("ABUL_HASAN_BIO_1st_paper.pdf", 126)),
    
    ("শৈবাল", ("ABUL_HASAN_BIO_1st_paper.pdf", 181)),
    ("ছত্রাক", ("ABUL_HASAN_BIO_1st_paper.pdf", 192)),
    ("উলফিয়া", ("ABUL_HASAN_BIO_1st_paper.pdf", 222)),
    ("মস", ("ABUL_HASAN_BIO_1st_paper.pdf", 206)),
    ("ফার্ন", ("ABUL_HASAN_BIO_1st_paper.pdf", 210)),
    ("মালভেসি", ("ABUL_HASAN_BIO_1st_paper.pdf", 230)),
    ("ধান", ("ABUL_HASAN_BIO_1st_paper.pdf", 235)),
    ("বাঁশ", ("ABUL_HASAN_BIO_1st_paper.pdf", 235)),
    ("বাবলা", ("ABUL_HASAN_BIO_1st_paper.pdf", 245)),
    ("সুন্দরী", ("ABUL_HASAN_BIO_1st_paper.pdf", 245)),
    
    ("সালোকসংশ্লেষণ", ("ABUL_HASAN_BIO_1st_paper.pdf", 281)),
    ("পত্ররন্ধ্র", ("ABUL_HASAN_BIO_1st_paper.pdf", 275)),
    ("প্রস্বেদন", ("ABUL_HASAN_BIO_1st_paper.pdf", 275)),
    ("ক্যালসিয়াম", ("ABUL_HASAN_BIO_1st_paper.pdf", 265)),
    ("কপার", ("ABUL_HASAN_BIO_1st_paper.pdf", 265)),
    ("ম্যাগনেসিয়াম", ("ABUL_HASAN_BIO_1st_paper.pdf", 265)),
    
    ("নেমাটোসিস্ট", ("Azmol_BIO_2nd_paper.pdf", 50)),
    ("সিলেন্টেরন", ("Azmol_BIO_2nd_paper.pdf", 50)),
    ("নিডোব্লাস্ট", ("Azmol_BIO_2nd_paper.pdf", 50)),
    ("ডিগবাজি", ("Azmol_BIO_2nd_paper.pdf", 50)),
    ("হামাগুড়ি", ("Azmol_BIO_2nd_paper.pdf", 50)),
    ("Hydra", ("Azmol_BIO_2nd_paper.pdf", 50)),
    ("হাইড্রা", ("Azmol_BIO_2nd_paper.pdf", 50)),
    ("ঘাসফড়িং", ("Azmol_BIO_2nd_paper.pdf", 70)),
    ("ঘাস ফড়িং", ("Azmol_BIO_2nd_paper.pdf", 70)),
    ("পুঞ্জাক্ষী", ("Azmol_BIO_2nd_paper.pdf", 70)),
    ("ওমাটিডিয়াম", ("Azmol_BIO_2nd_paper.pdf", 70)),
    ("হিমোসাইট", ("Azmol_BIO_2nd_paper.pdf", 70)),
    ("রুই মাছ", ("Azmol_BIO_2nd_paper.pdf", 85)),
    ("রুই", ("Azmol_BIO_2nd_paper.pdf", 85)),
    ("বায়ুথলি", ("Azmol_BIO_2nd_paper.pdf", 85)),
    ("পুটকা", ("Azmol_BIO_2nd_paper.pdf", 85)),
    
    ("ক্ষুদ্রান্ত্র", ("Azmol_BIO_2nd_paper.pdf", 96)),
    ("পাকস্থলি", ("Azmol_BIO_2nd_paper.pdf", 96)),
    ("এনজাইম", ("Azmol_BIO_2nd_paper.pdf", 96)),
    ("পেপসিন", ("Azmol_BIO_2nd_paper.pdf", 96)),
    ("ট্রিপসিন", ("Azmol_BIO_2nd_paper.pdf", 101)),
    ("লালা", ("Azmol_BIO_2nd_paper.pdf", 98)),
    ("টায়ালিন", ("Azmol_BIO_2nd_paper.pdf", 98)),
    ("অগ্ন্যাশয়", ("Azmol_BIO_2nd_paper.pdf", 101)),
    ("অগ্ন্যাশয়", ("Azmol_BIO_2nd_paper.pdf", 101)),
    ("যকৃত", ("Azmol_BIO_2nd_paper.pdf", 105)),
    ("লিভার", ("Azmol_BIO_2nd_paper.pdf", 105)),
    ("গ্লাইকোজেন", ("Azmol_BIO_2nd_paper.pdf", 105)),
    ("অরনিথিন", ("Azmol_BIO_2nd_paper.pdf", 105)),
    ("গ্যাস্ট্রিন", ("Azmol_BIO_2nd_paper.pdf", 108)),
    ("পরিপাক", ("Azmol_BIO_2nd_paper.pdf", 96)),
    
    ("কপাটিকা", ("Azmol_BIO_2nd_paper.pdf", 141)),
    ("নিলয়", ("Azmol_BIO_2nd_paper.pdf", 141)),
    ("অলিন্দ", ("Azmol_BIO_2nd_paper.pdf", 141)),
    ("হৃদপিন্ড", ("Azmol_BIO_2nd_paper.pdf", 141)),
    ("হৃদپیণ্ড", ("Azmol_BIO_2nd_paper.pdf", 141)),
    
    ("হেপারিন", ("Azmol_BIO_2nd_paper.pdf", 135)),
    ("বেসোফিল", ("Azmol_BIO_2nd_paper.pdf", 135)),
    ("মনোসাইট", ("Azmol_BIO_2nd_paper.pdf", 135)),
    ("লিম্ফোসাইট", ("Azmol_BIO_2nd_paper.pdf", 135)),
    ("নিউট্রোফিল", ("Azmol_BIO_2nd_paper.pdf", 135)),
    ("ম্যাক্রোফেজ", ("Azmol_BIO_2nd_paper.pdf", 135)),
    ("শিরা", ("Azmol_BIO_2nd_paper.pdf", 138)),
    ("ধমনী", ("Azmol_BIO_2nd_paper.pdf", 138)),
    ("ডাক্টাস", ("Azmol_BIO_2nd_paper.pdf", 138)),
    ("হিমোগ্লোবিন", ("Azmol_BIO_2nd_paper.pdf", 137)),
    ("ক্যাডমিয়াম", ("Azmol_BIO_2nd_paper.pdf", 137)),
    ("লোহিত", ("Azmol_BIO_2nd_paper.pdf", 135)),
    ("শ্বেত", ("Azmol_BIO_2nd_paper.pdf", 135)),
    ("রক্ত", ("Azmol_BIO_2nd_paper.pdf", 135)),
    
    ("প্লুরা", ("Azmol_BIO_2nd_paper.pdf", 186)),
    ("প্লিওরা", ("Azmol_BIO_2nd_paper.pdf", 186)),
    ("শ্বসন", ("Azmol_BIO_2nd_paper.pdf", 186)),
    ("কার্বন ডাই অক্সাইড", ("Azmol_BIO_2nd_paper.pdf", 186)),
    ("ফুসফুস", ("Azmol_BIO_2nd_paper.pdf", 186)),
    
    ("নেফ্রন", ("Azmol_BIO_2nd_paper.pdf", 216)),
    ("রেচন", ("Azmol_BIO_2nd_paper.pdf", 216)),
    ("বৃক্ক", ("Azmol_BIO_2nd_paper.pdf", 216)),
    
    ("থ্যালামাস", ("Azmol_BIO_2nd_paper.pdf", 271)),
    ("হাইপোথ্যালামাস", ("Azmol_BIO_2nd_paper.pdf", 271)),
    ("সেরিবেলাম", ("Azmol_BIO_2nd_paper.pdf", 271)),
    ("সেরিব্রাম", ("Azmol_BIO_2nd_paper.pdf", 271)),
    ("মেডুলা", ("Azmol_BIO_2nd_paper.pdf", 271)),
    ("সুষুম্না", ("Azmol_BIO_2nd_paper.pdf", 271)),
    ("এন্টোরিক", ("Azmol_BIO_2nd_paper.pdf", 271)),
    ("মস্তিষ্ক", ("Azmol_BIO_2nd_paper.pdf", 271)),
    
    ("হিউমেরাস", ("Azmol_BIO_2nd_paper.pdf", 241)),
    ("করোটিকা", ("Azmol_BIO_2nd_paper.pdf", 241)),
    ("অস্থি", ("Azmol_BIO_2nd_paper.pdf", 241)),
    ("হাড়", ("Azmol_BIO_2nd_paper.pdf", 241)),
    ("কঙ্কাল", ("Azmol_BIO_2nd_paper.pdf", 241)),
    
    ("পেশী", ("Azmol_BIO_2nd_paper.pdf", 248)),
    ("পেশি", ("Azmol_BIO_2nd_paper.pdf", 248)),
    ("টেনডন", ("Azmol_BIO_2nd_paper.pdf", 248)),
    ("লিগামেন্ট", ("Azmol_BIO_2nd_paper.pdf", 248)),
    ("ডেলটয়েট", ("Azmol_BIO_2nd_paper.pdf", 248)),
    
    ("টিকা", ("Azmol_BIO_2nd_paper.pdf", 361)),
    ("ভ্যাকসিন", ("Azmol_BIO_2nd_paper.pdf", 361)),
    ("বিসিজি", ("Azmol_BIO_2nd_paper.pdf", 361)),
    ("ইমিউন", ("Azmol_BIO_2nd_paper.pdf", 361)),
    
    ("মেন্ডেল", ("Azmol_BIO_2nd_paper.pdf", 391)),
    ("জিনতত্ত্ব", ("Azmol_BIO_2nd_paper.pdf", 391)),
    
    # --- General/broad keywords placed at the bottom ---
    ("ডিএনএ", ("ABUL_HASAN_BIO_1st_paper.pdf", 41)),
    ("DNA", ("ABUL_HASAN_BIO_1st_paper.pdf", 41)),
    ("আরএনএ", ("ABUL_HASAN_BIO_1st_paper.pdf", 45)),
    ("RNA", ("ABUL_HASAN_BIO_1st_paper.pdf", 45)),
]

# Bengali common suffixes list to match inflection forms (e.g. 'কোষ চক্রের')
# while avoiding incorrect root overlaps (e.g. 'মস' in 'মস্তিষ্ক')
bengali_suffixes = [
    "", "ের", "ে", "কে", "তে", "টি", "টিই", "টিও", "টা", "টাই", "টাও", 
    "গুলো", "গুলোই", "গুলোও", "গুলি", "গুলিই", "র", "রা", "দের", 
    "দেরকে", "য়ে", "য়ের", "ন", "না", "নি", "টিতে", "গুলোতে"
]

updated_count = 0
for q_id, q_text, correct, opt_a, opt_b, opt_c, opt_d, ch_code, ch_name in questions:
    assigned_file = None
    assigned_page = None
    
    # Clean text to normalize search space
    combined_search_text = f"{q_text} {correct} {opt_a} {opt_b} {opt_c} {opt_d}".lower()
    
    # 1. Search keyword rules first
    for keyword, (pdf_file, pdf_page) in keywords_rules:
        if re.search(r'^[a-zA-Z0-9\s\-]+$', keyword):
            # For English keywords, use standard English word boundaries
            pattern = rf'\b{re.escape(keyword.lower())}\b'
        else:
            # For Bengali, use a suffix-aware lookahead that allows common diacritic suffixes
            # but fails on other letters/conjunctions (preventing 'মস' -> 'মস্তিষ্ক')
            suffix_pattern = "|".join([re.escape(s) for s in bengali_suffixes])
            pattern = rf'(?<![\u0980-\u09ff]){re.escape(keyword.lower())}(?:{suffix_pattern})(?![\u0980-\u09ff])'
            
        if re.search(pattern, combined_search_text):
            assigned_file = pdf_file
            assigned_page = pdf_page
            break
            
    # 2. Fall back to chapter level defaults
    if not assigned_file:
        assigned_file, assigned_page = chapter_defaults.get(ch_code, ("Azmol_BIO_2nd_paper.pdf", 7))
        
    # Update question in DB
    cursor.execute(
        "UPDATE questions SET pdf_file = ?, pdf_page = ? WHERE id = ?",
        (assigned_file, assigned_page, q_id)
    )
    updated_count += 1

conn.commit()
print(f"[SUCCESS] Updated {updated_count} questions with refined page numbers.")
conn.close()
