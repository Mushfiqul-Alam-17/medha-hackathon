"""
MEDHA — Classifier Service
Calls HuggingFace Inference API for BanglaBERT behavioral classification.
Falls back to identical rule-based logic if HF is unavailable.
"""

import logging
import requests
from typing import Dict, List, Optional
from config import settings

logger = logging.getLogger("medha.classifier")

LABEL_ORDER = ["MASTERY", "PRIORITY_FOCUS", "TRUST_GAP", "GROWTH_AREA"]


def classify_result(result: Dict) -> Dict:
    """
    Classify a single question result into one of 4 behavioral states.
    
    Args:
        result: dict with keys: topic, time_taken, click_path, confidence_tap,
                is_correct, difficulty
    
    Returns:
        dict with keys: label, confidence (dict), source ("model" or "fallback")
    """
    # Build the text input exactly as training data format
    switches = max(0, len(result.get("click_path", [])) - 1)
    text = (
        f"Topic: {result.get('topic', 'Unknown')} | "
        f"time_ratio: {result['time_taken'] / settings.EQUILIBRIUM_SECONDS:.3f} | "
        f"switches: {switches} | "
        f"confidence: {result.get('confidence_tap', 'unsure')} | "
        f"correct: {str(result['is_correct']).lower()} | "
        f"difficulty: {result.get('difficulty', 'medium')}"
    )

    # Try HuggingFace Inference API
    if settings.HF_TOKEN and settings.HF_MODEL_ID:
        try:
            response = requests.post(
                settings.HF_API_URL,
                headers={"Authorization": f"Bearer {settings.HF_TOKEN}"},
                json={"inputs": text},
                timeout=15,
            )
            if response.status_code == 200:
                scores = response.json()
                # HF returns [[{label, score}, ...]] for classification
                if isinstance(scores, list) and len(scores) > 0:
                    if isinstance(scores[0], list):
                        scores = scores[0]
                    label = max(scores, key=lambda x: x["score"])["label"]
                    confidence = {s["label"]: round(s["score"], 4) for s in scores}
                    return {"label": label, "confidence": confidence, "source": "model"}
            else:
                logger.warning(f"HF API returned {response.status_code}: {response.text[:200]}")
        except Exception as e:
            logger.warning(f"HF API call failed: {e}")

    # Fallback to rule-based classification
    return _rule_based_fallback(result)


def _rule_based_fallback(result: Dict) -> Dict:
    """
    Deterministic rule-based classifier — identical output format to the ML model.
    Same logic used in demo. Reliable, zero-latency, always available.
    """
    t = result["time_taken"] / settings.EQUILIBRIUM_SECONDS
    switches = max(0, len(result.get("click_path", [])) - 1) if result.get("click_path") else 0
    confidence_tap = result.get("confidence_tap", "unsure")
    correct = result.get("is_correct", False)
    skipped = result.get("skipped", False)
    expired = result.get("time_expired", False)

    if skipped or expired:
        label = "GROWTH_AREA"
    elif correct:
        if confidence_tap == "guessing":
            label = "GROWTH_AREA"  # Lucky guess represents a knowledge gap
        elif t <= 0.5 and switches <= 1 and confidence_tap == "sure":
            label = "MASTERY"
        else:
            label = "TRUST_GAP"
    else:
        # Confidently wrong within reasonable timeframe represents a misconception
        if confidence_tap == "sure" and t <= 0.8 and switches <= 2:
            label = "PRIORITY_FOCUS"
        else:
            label = "GROWTH_AREA"

    # Generate pseudo-confidence scores
    confidence = {l: 0.0 for l in LABEL_ORDER}
    confidence[label] = 1.0

    return {"label": label, "confidence": confidence, "source": "fallback"}


def classify_session(results: List[Dict]) -> List[Dict]:
    """
    Batch classify all question results in a session.
    Returns the results enriched with classifier_label and classifier_confidence.
    """
    classified = []
    for r in results:
        classification = classify_result(r)
        enriched = {
            **r,
            "classifier_label": classification["label"],
            "classifier_confidence": classification["confidence"],
            "classifier_source": classification["source"],
        }
        classified.append(enriched)
    return classified


def check_classifier_available() -> bool:
    """Check if the HuggingFace model is reachable."""
    if not settings.HF_TOKEN or not settings.HF_MODEL_ID:
        return False
    try:
        response = requests.post(
            settings.HF_API_URL,
            headers={"Authorization": f"Bearer {settings.HF_TOKEN}"},
            json={"inputs": "test"},
            timeout=5,
        )
        return response.status_code == 200
    except Exception:
        return False
