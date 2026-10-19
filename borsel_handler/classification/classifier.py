"""
Rule-Based Classification and Event Tagging Engine
"""
import re
from typing import List, Tuple
from borsel_handler.classification.taxonomy import (
    EVENT_RULES, CATEGORY_GENERAL
)


def clean_text_for_matching(text: str) -> str:
    if not text:
        return ""
    t = text.lower()
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def classify_event(
    title: str, snippet: str = "", source_category: str = ""
) -> Tuple[str, float, List[str]]:
    """
    Evaluates text against the market event taxonomy.
    Returns:
        (best_category: str, confidence_score: float [0-100], tags: List[str])
    """
    clean_title = clean_text_for_matching(title)
    clean_snippet = clean_text_for_matching(snippet)
    clean_source_cat = clean_text_for_matching(source_category)
    combined_text = f"{clean_title} {clean_snippet}"

    best_category = CATEGORY_GENERAL
    highest_score = 0.0
    matched_tags: List[str] = []

    for cat_name, rules in EVENT_RULES.items():
        # Check negative phrases first
        negatives = rules.get("negative", [])
        if any(neg in combined_text for neg in negatives):
            continue

        raw_score = 0.0
        cat_tags = []

        # Category hints matching
        hints = rules.get("category_hints", [])
        for hint in hints:
            if hint in clean_source_cat or hint in clean_title:
                raw_score += 1.5
                cat_tags.append(hint)

        # Keyword matching
        for phrase, weight in rules.get("keywords", []):
            if phrase in combined_text:
                raw_score += weight
                cat_tags.append(phrase)

        # Normalize score into a 0 - 100 range
        normalized_score = min(100.0, raw_score * 20.0)

        if normalized_score > highest_score and normalized_score >= 20.0:
            highest_score = normalized_score
            best_category = cat_name
            matched_tags = cat_tags

    if highest_score < 20.0:
        return CATEGORY_GENERAL, 50.0, []

    return best_category, highest_score, list(set(matched_tags))
