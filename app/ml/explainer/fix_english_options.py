"""
Fix English options in questions_clean.jsonl AND in the already-generated training data.
This script:
1. Scans questions_clean.jsonl for options with English-only bn text
2. Uses a mapping dict to translate common scientific terms to Bengali
3. Updates questions_clean.jsonl with Bengali translations
4. Re-scans explainer_training_data_temp.jsonl and replaces English answer texts
   in the input fields with their Bengali counterparts
"""
import sys, json, re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# ---------- English -> Bengali translation map for scientific/biology terms ----------
ENGLISH_TO_BENGALI = {
    # Biology terms
    "Rhizoid": "রাইজয়েড",
    "Fragmentation": "খণ্ডায়ন",
    "Tuber": "টিউবার",
    "Spore": "স্পোর",
    "Interferon": "ইন্টারফেরন",
    "Lactone": "ল্যাকটোন",
    "Lysozyme": "লাইসোজাইম",
    "Defensin": "ডেফেনসিন",
    "Homie": "হোমি",
    "Hibiscus rosa-sinensis": "হিবিসকাস রোজা-সাইনেনসিস (জবা)",
    "Rose": "গোলাপ",
    "Lemon": "লেবু",
    "Chitin": "কাইটিন",
    "Cellulose": "সেলুলোজ",
    "Glygogen": "গ্লাইকোজেন",
    "Starch": "স্টার্চ",
    "Cytoplasm": "সাইটোপ্লাজম",
    "Ribosome": "রাইবোসোম",
    "Mitochondria": "মাইটোকন্ড্রিয়া",
    "Chloroplast": "ক্লোরোপ্লাস্ট",
    "citric acid cycle": "সাইট্রিক অ্যাসিড চক্র",
    "oxidative phosphorylation": "জারণমূলক ফসফোরাইলেশন",
    "electron transport": "ইলেকট্রন পরিবহন",
    "glycolysis": "গ্লাইকোলাইসিস",
    "cytogenesis": "সাইটোজেনেসিস",
    "apogamy": "অ্যাপোগ্যামি",
    "oogenesis": "ওজেনেসিস",
    "sporogenesis": "স্পোরোজেনেসিস",
    "Mucor pusillus": "মিউকর পুসিলাস",
    "Aspergillus flavus": "অ্যাসপারজিলাস ফ্লেভাস",
    "Agaricus Ompestris": "অ্যাগারিকাস ক্যাম্পেস্ট্রিস",
    "Saccharomyces": "স্যাকারোমাইসিস",
    "Saccharomyces cerevisiae": "স্যাকারোমাইসিস সেরেভিসি",
    "Hepatitis D Virus": "হেপাটাইটিস ডি ভাইরাস",
    "Hepatitis A Virus": "হেপাটাইটিস এ ভাইরাস",
    "Hepatitis C Virus": "হেপাটাইটিস সি ভাইরাস",
    "Hepatitis B Virus": "হেপাটাইটিস বি ভাইরাস",
    "mutinous": "বিদ্রোহী",
    "compliant": "অনুগত",
    "docile": "বশীভূত",
    "amenable": "বাধ্য",
    "spain": "স্পেন",
    # Chemical formulas
    "$CH_3COOH$": "এসিটিক অ্যাসিড (CH₃COOH)",
    "HCHO": "ফর্মালডিহাইড (HCHO)",
    "$C_2H_4OH$": "ইথানল (C₂H₄OH)",
    "$CH_2OH$": "মিথানল (CH₂OH)",
    # LaTeX-formatted elemental symbols
    "$\\text{Cd}$": "ক্যাডমিয়াম (Cd)",
    "$\\text{As}$": "আর্সেনিক (As)",
    "$\\text{Cr}$": "ক্রোমিয়াম (Cr)",
    "$\\text{Fe}$": "আয়রন (Fe)",
    # Plain elemental symbols
    "As": "আর্সেনিক (As)",
    "Fe": "আয়রন (Fe)",
    "Cr": "ক্রোমিয়াম (Cr)",
    "Cd": "ক্যাডমিয়াম (Cd)",
    # Ion formulas (LaTeX)
    "$K^+$": "পটাসিয়াম (K⁺)",
    "$Fe^{+++}$": "আয়রন (Fe³⁺)",
    "$Mg^{++}$": "ম্যাগনেসিয়াম (Mg²⁺)",
    "$Ca^{++}$": "ক্যালসিয়াম (Ca²⁺)",
    # Organic chemistry formulas
    "$CH_3COO-COCH_3$": "অ্যাসিটিক অ্যানহাইড্রাইড (CH₃COO-COCH₃)",
    "$CH_3CH_2-O-CH_2CH_3$": "ডাই-ইথাইল ইথার (CH₃CH₂-O-CH₂CH₃)",
    "$CH_3-CO-CH_2CO-CH_3$": "অ্যাসিটাইল অ্যাসিটোন (CH₃-CO-CH₂CO-CH₃)",
    "$CH_3-COO-COO-CH_3$": "অক্সালিক অ্যাসিড ডাই-মিথাইল এস্টার (CH₃-COO-COO-CH₃)",
    # Molar concentrations
    "0.004M": "০.০০৪ মোলার",
    "4.0M": "৪.০ মোলার",
    "0.4M": "০.৪ মোলার",
    "0.04M": "০.০৪ মোলার",
    # Anions
    "NO3-": "NO₃⁻ (নাইট্রেট)",
    "HCO3-": "HCO₃⁻ (বাইকার্বনেট)",
    "SO4^2-": "SO₄²⁻ (সালফেট)",
    "OH-": "OH⁻ (হাইড্রক্সিল)",
    # Phylum names
    "Arthropoda": "আর্থ্রোপোডা",
    "Annelida": "অ্যানেলিডা",
    "Porifera": "পরিফেরা",
    "Mollusca": "মোলাস্কা",
    "Chordata": "কর্ডাটা",
    "Nematoda": "নেমাটোডা",
    # Liver lobes
    "Caudate lobe": "কডেট লোব",
    "Quadrate lobe": "কোয়াড্রেট লোব",
    "Right lobe": "ডান লোব",
    "Left lobe": "বাম লোব",
    # Tissue culture
    "Tissue culture": "টিস্যু কালচার",
    # Reproductive / Cell biology
    "Sperm": "শুক্রাণু",
    "Lysosome": "লাইসোসোম",
    "lysosome": "লাইসোসোম",
    "Enzyme": "এনজাইম",
    "endoplasmic reticulum": "এন্ডোপ্লাজমিক রেটিকুলাম",
    # Physiological processes
    "Osmosis": "অসমোসিস",
    "Respiration": "শ্বসন",
    "Transpiration": "প্রস্বেদন",
    "Diffusion": "ব্যাপন",
    # Glands & Organs
    "Thyroid gland": "থাইরয়েড গ্রন্থি",
    "Pancreas": "অগ্ন্যাশয়",
    "Liver": "যকৃত",
    "Salivary gland": "লালা গ্রন্থি",
    "Thalamus": "থ্যালামাস",
    "Hypothalamus": "হাইপোথ্যালামাস",
    "Adrenal gland": "অ্যাড্রেনাল গ্রন্থি",
    "Pituitary gland": "পিটুইটারি গ্রন্থি",
    # Musculoskeletal
    "Myofibril": "মায়োফাইব্রিল",
    "Ligament": "লিগামেন্ট",
    "Synovium": "সাইনোভিয়াম",
    "Tendon": "টেন্ডন",
    # Digestive enzymes
    "Lipase": "লাইপেজ",
    "Pepsin": "পেপসিন",
    "Lactase": "ল্যাক্টেজ",
    "Isomaltase": "আইসোমল্টেজ",
    "Ptyalin": "টায়ালিন",
    "Maltase": "মল্টেজ",
    "Trypsin": "ট্রিপসিন",
    "Amylase": "অ্যামাইলেজ",
    # Toxins / Blood
    "Hypnotoxin": "হিপনোটক্সিন",
    "Toxin": "টক্সিন",
    "Hemocyanin": "হিমোসায়ানিন",
    "Hemozoin": "হিমোজয়েন",
    "Leukocyte": "লিউকোসাইট",
    "Erythrocyte": "এরিথ্রোসাইট",
    "Thrombocyte": "থ্রম্বোসাইট",
    "Hemocyte": "হিমোসাইট",
    # Digestive tract layers
    "Serosa": "সেরোসা",
    "Muscularis mucosal": "মাসকুলারিস মিউকোসাল",
    "Mucosa": "মিউকোসা",
    "Submucosa": "সাবমিউকোসা",
    # Chromosome counts (plain numbers)
    "23": "২৩",
    "33": "৩৩",
    "29": "২৯",
    "17": "১৭",
    # Vaccines
    "Diphtheria vaccine": "ডিপথেরিয়া ভ্যাকসিন",
    "BCG vaccine": "বিসিজি ভ্যাকসিন",
    "Hepatitis B vaccine": "হেপাটাইটিস বি ভ্যাকসিন",
    "Tetanus vaccine": "টিটেনাস ভ্যাকসিন",
    # White blood cells
    "Eosinophil": "ইওসিনোফিল",
    "eosinophil": "ইওসিনোফিল",
    "Monocyte": "মনোসাইট",
    "monocyte": "মনোসাইট",
    "Basophil": "বেসোফিল",
    "basophil": "বেসোফিল",
    "Lymphocyte": "লিম্ফোসাইট",
    "lymphocyte": "লিম্ফোসাইট",
    "Neutrophil": "নিউট্রোফিল",
    "neutrophil": "নিউট্রোফিল",
    # Biochemistry
    "NADPH ATP": "এনএডিপিএইচ এটিপি",
    "genome": "জিনোম",
    "Chromosome": "ক্রোমোসোম",
    "nucleus": "নিউক্লিয়াস",
    # Viruses
    "Mumps virus": "মাম্পস ভাইরাস",
    "Rabies virus": "জলাতঙ্ক ভাইরাস",
    "Polio virus": "পোলিও ভাইরাস",
    "Variola virus": "ভ্যারিওলা ভাইরাস",
    # Plants
    "Eucalyptus": "ইউক্যালিপটাস",
    "Wolffia": "উলফিয়া",
    "Pisttia": "পিস্টিয়া",
    "Azolla": "অ্যাজোলা",
    # Cell division phases
    "prophase": "প্রোফেজ",
    "metaphase": "মেটাফেজ",
    "anaphase": "অ্যানাফেজ",
    "telophase": "টেলোফেজ",
    # Algae phyla
    "Euglenophyta": "ইউগ্লেনোফাইটা",
    "Pyrrhophyta": "পাইরোফাইটা",
    "Chrysophyta": "ক্রাইসোফাইটা",
    "Phaeophyta": "ফিওফাইটা",
    # Cell death / division types
    "necrosis": "নেক্রোসিস",
    "apoptosis": "অ্যাপোপটোসিস",
    "mitosis": "মাইটোসিস",
    "meiosis": "মিয়োসিস",
    # English grammar (for English vocab questions in exam)
    "noun": "বিশেষ্য (noun)",
    "participle": "কৃদন্ত (participle)",
    "verb": "ক্রিয়া (verb)",
    "adverb": "ক্রিয়াবিশেষণ (adverb)",
    # Additional scientific terms
    "DNA": "ডিএনএ",
    "RNA": "আরএনএ",
    "ATP": "এটিপি",
    "mRNA": "এমআরএনএ",
    "tRNA": "টিআরএনএ",
    # Cell cycle phases
    "G1": "জি১",
    "G2": "জি২",
    "S": "এস",
    "M": "এম",
}


def is_english_only(text):
    """Check if text contains only ASCII/English characters (no Bengali Unicode)."""
    text = text.strip()
    if not text:
        return False
    # Check if there's any Bengali character (Unicode range 0980-09FF)
    has_bengali = bool(re.search(r'[\u0980-\u09FF]', text))
    return not has_bengali


def translate_option(text):
    """Translate an English option text to Bengali using the mapping."""
    text = text.strip()
    # Exact match first
    if text in ENGLISH_TO_BENGALI:
        return ENGLISH_TO_BENGALI[text]
    # Case-insensitive match
    for eng, bn in ENGLISH_TO_BENGALI.items():
        if eng.lower() == text.lower():
            return bn
    # If no match found, return original
    return text


def main():
    backend_dir = Path(__file__).parent.parent.parent / "backend"
    questions_file = backend_dir / "data" / "questions_clean.jsonl"
    temp_file = Path(__file__).parent / "data" / "explainer_training_data_temp.jsonl"

    # ===== STEP 1: Fix questions_clean.jsonl =====
    print("=" * 60)
    print("STEP 1: Fixing questions_clean.jsonl")
    print("=" * 60)

    questions = []
    with open(questions_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line.strip()))

    # Build a mapping of (question_id, option_key) -> (old_english, new_bengali)
    translation_log = {}
    fixed_count = 0
    untranslated = []

    for q in questions:
        for k, v in q['options'].items():
            bn = v['bn'].strip()
            if is_english_only(bn):
                new_bn = translate_option(bn)
                if new_bn != bn:
                    translation_log[(q['id'], k)] = (bn, new_bn)
                    v['bn'] = new_bn
                    fixed_count += 1
                else:
                    untranslated.append((q['id'], k, bn))

    print(f"  Fixed {fixed_count} English options to Bengali")
    if untranslated:
        print(f"  WARNING: {len(untranslated)} options could NOT be translated (no mapping):")
        for qid, k, bn in untranslated:
            print(f"    {qid} option {k}: '{bn}'")

    # Write updated questions_clean.jsonl
    with open(questions_file, 'w', encoding='utf-8') as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + '\n')
    print(f"  Updated {questions_file}")

    # ===== STEP 2: Fix training data temp file =====
    print()
    print("=" * 60)
    print("STEP 2: Fixing explainer_training_data_temp.jsonl")
    print("=" * 60)

    if not temp_file.exists():
        print("  Temp file not found, skipping.")
        return

    # Build a comprehensive replacement map for input field text
    # We need to replace English terms wherever they appear in "Student answered:" and "Correct answer:" lines
    all_eng_terms = list(ENGLISH_TO_BENGALI.keys())
    # Sort by length descending so longer matches come first (e.g. "Hibiscus rosa-sinensis" before "Rose")
    all_eng_terms.sort(key=len, reverse=True)

    records = []
    with open(temp_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line.strip()))

    fixed_records = 0
    for record in records:
        inp = record['input']
        original_inp = inp

        # Fix the input field - replace English answer texts in "Student answered:" and "Correct answer:" lines
        for eng_term in all_eng_terms:
            bn_term = ENGLISH_TO_BENGALI[eng_term]
            # Replace in "Student answered: <TERM> (Wrong)" and "Student answered: <TERM> (Correct)"
            inp = inp.replace(f"Student answered: {eng_term} (Wrong)", f"Student answered: {bn_term} (Wrong)")
            inp = inp.replace(f"Student answered: {eng_term} (Correct)", f"Student answered: {bn_term} (Correct)")
            # Replace in "Correct answer: <TERM>"
            inp = inp.replace(f"Correct answer: {eng_term}\n", f"Correct answer: {bn_term}\n")
            inp = inp.replace(f"Correct answer: {eng_term}\\n", f"Correct answer: {bn_term}\\n")

        if inp != original_inp:
            record['input'] = inp
            fixed_records += 1

    print(f"  Fixed input fields in {fixed_records} / {len(records)} records")

    # Write back
    with open(temp_file, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    print(f"  Updated {temp_file}")
    print(f"  Total records: {len(records)}")


if __name__ == "__main__":
    main()
