"""
Fuzzy matching utilities for data validation
"""
from thefuzz import fuzz, process
from typing import List, Tuple, Optional


def fuzzy_match_strings(str1: str, str2: str, threshold: float = 0.85) -> Tuple[bool, float]:
    """
    Perform fuzzy string matching
    
    Returns:
        Tuple of (is_match, similarity_score)
    """
    if not str1 or not str2:
        return False, 0.0
    
    # Normalize strings
    str1 = str1.lower().strip()
    str2 = str2.lower().strip()
    
    # Calculate similarity using multiple methods
    ratio = fuzz.ratio(str1, str2) / 100.0
    partial_ratio = fuzz.partial_ratio(str1, str2) / 100.0
    token_sort_ratio = fuzz.token_sort_ratio(str1, str2) / 100.0
    token_set_ratio = fuzz.token_set_ratio(str1, str2) / 100.0
    
    # Weighted average
    similarity = (ratio * 0.3 + partial_ratio * 0.2 + token_sort_ratio * 0.25 + token_set_ratio * 0.25)
    
    is_match = similarity >= threshold
    return is_match, similarity


def calculate_similarity(str1: str, str2: str) -> float:
    """Calculate similarity score between two strings"""
    _, similarity = fuzzy_match_strings(str1, str2, threshold=0.0)
    return similarity


def find_best_match(query: str, choices: List[str], threshold: float = 0.7) -> Optional[Tuple[str, float]]:
    """
    Find best matching string from a list of choices
    
    Returns:
        Tuple of (matched_string, similarity_score) or None
    """
    if not query or not choices:
        return None
    
    result = process.extractOne(query, choices, scorer=fuzz.token_set_ratio)
    if result:
        matched_string, score = result
        normalized_score = score / 100.0
        if normalized_score >= threshold:
            return (matched_string, normalized_score)
    
    return None


