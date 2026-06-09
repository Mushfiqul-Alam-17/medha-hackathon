"""
MEDHA — Notes Service (Zero-LLM Assembly)
Assembles personalized study notes directly from question bank metadata.
No runtime LLM calls — faster, cheaper, and more accurate because
it uses verified NCTB-sourced explanations instead of hallucinations.
"""

from typing import Dict, List, Any


def assemble_notes(dna_report: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Assemble study notes based on behavioral DNA groups.
    
    Structure:
    - PRIORITY_FOCUS: Gets explanation + confusable note (framed as false belief correction)
    - TRUST_GAP: Gets explanation (framed as confidence reinforcement)
    - GROWTH_AREA: Gets full explanation + confusable note (framed as new study material)
    - MASTERY: Excluded (student already knows it)
    """
    sections = []

    # 1. PRIORITY_FOCUS (Confidently Wrong)
    priority_items = dna_report.get("PRIORITY_FOCUS", [])
    if priority_items:
        items = []
        for q in priority_items:
            items.append({
                "topic": q.get("topic") or q.get("chapter_name", "Unknown Topic"),
                "question_text": q.get("question_bn", ""),
                "frame": "তুমি দ্রুত এবং আত্মবিশ্বাসের সাথে উত্তর দিয়েছ, কিন্তু উত্তরটি ভুল ছিল। এর মানে এই টপিকে তোমার একটি ভুল ধারণা (false belief) আছে যা দ্রুত সংশোধন করা প্রয়োজন।",
                "correct_answer": q.get("correct_answer_text", ""),
                "wrong_answer": q.get("final_answer_text", ""),
                "explanation": q.get("explanation_bn", "এই প্রশ্নের ব্যাখ্যা বর্তমানে উপলব্ধ নেই।"),
                "confusable_note": q.get("confusable_note_bn"),
                "memory_trick": q.get("memory_trick"),
                "trap_note": q.get("trap_note", "খুব কাছাকাছি অপশন দেখে বিভ্রান্ত হওয়া যাবে না।"),
                "pdf_file": q.get("pdf_file"),
                "pdf_page": q.get("pdf_page")
            })
        sections.append({
            "header": "অবিলম্বে সংশোধন প্রয়োজন (Priority Focus)",
            "description": "এই প্রশ্নগুলোতে তুমি আত্মবিশ্বাসী ছিলে কিন্তু ভুল করেছ। এগুলো সবচেয়ে বিপজ্জনক কারণ এখানে নেগেটিভ মার্কিং হওয়ার সম্ভাবনা সবচেয়ে বেশি।",
            "items": items
        })

    # 2. TRUST_GAP (Hesitant Success)
    trust_items = dna_report.get("TRUST_GAP", [])
    if trust_items:
        items = []
        for q in trust_items:
            items.append({
                "topic": q.get("topic") or q.get("chapter_name", "Unknown Topic"),
                "question_text": q.get("question_bn", ""),
                "frame": "তুমি সঠিক উত্তর দিয়েছ, কিন্তু দ্বিধা করেছ বা বেশি সময় নিয়েছ। কনসেপ্ট তোমার জানা আছে, শুধু নিজের উপর বিশ্বাস বাড়াতে হবে।",
                "correct_answer": q.get("correct_answer_text", ""),
                "explanation": q.get("explanation_bn", "এই কনসেপ্টটি বারবার রিভিশন দাও যাতে দ্রুত মনে পড়ে।"),
                "memory_trick": q.get("memory_trick"),
                "pdf_file": q.get("pdf_file"),
                "pdf_page": q.get("pdf_page")
            })
        sections.append({
            "header": "নিজের উপর বিশ্বাস রাখো (Trust Gap)",
            "description": "তুমি এগুলো পারো, কিন্তু পরীক্ষার হলে দ্বিধা করো। এই কনসেপ্টগুলোতে স্পিড বাড়াতে হবে।",
            "items": items
        })

    # 3. GROWTH_AREA (Needs Study)
    growth_items = dna_report.get("GROWTH_AREA", [])
    if growth_items:
        items = []
        for q in growth_items:
            items.append({
                "topic": q.get("topic") or q.get("chapter_name", "Unknown Topic"),
                "question_text": q.get("question_bn", ""),
                "frame": "এই টপিকটি তোমার এখনও ভালোভাবে পড়া হয়নি। এটি নতুন করে পড়ার জন্য সময় বের করো।",
                "correct_answer": q.get("correct_answer_text", ""),
                "explanation": q.get("explanation_bn", "মূল বইটি আবার ভালো করে পড়ে নাও।"),
                "confusable_note": q.get("confusable_note_bn"),
                "memory_trick": q.get("memory_trick"),
                "pdf_file": q.get("pdf_file"),
                "pdf_page": q.get("pdf_page")
            })
        sections.append({
            "header": "নতুন করে পড়তে হবে (Growth Area)",
            "description": "এই টপিকগুলোতে তোমার প্রস্তুতি এখনো অসম্পূর্ণ। সময় নিয়ে এগুলো ক্লিয়ার করতে হবে।",
            "items": items
        })

    return sections
