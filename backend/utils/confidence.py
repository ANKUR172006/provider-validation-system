"""
Confidence scoring utilities
"""
from typing import Dict, Any, Optional, Tuple
import re


def calculate_confidence_score(
    original_value: Optional[str],
    validated_value: Optional[str],
    external_match: bool = False,
    fuzzy_score: float = 0.0
) -> float:
    """
    Calculate confidence score for a field
    
    Args:
        original_value: Original value from source
        validated_value: Validated value
        external_match: Whether external source confirms the value
        fuzzy_score: Fuzzy matching score (0-1)
    
    Returns:
        Confidence score (0-1)
    """
    if not original_value and not validated_value:
        return 0.0
    
    if not original_value or not validated_value:
        return 0.3  # Low confidence if one is missing
    
    # Base score from fuzzy matching
    base_score = fuzzy_score if fuzzy_score > 0 else 0.5
    
    # Boost if external source confirms
    if external_match:
        base_score = min(1.0, base_score + 0.3)
    
    # Boost if values match exactly
    if original_value.lower().strip() == validated_value.lower().strip():
        base_score = max(base_score, 0.9)
    
    # Penalize if values are very different
    if fuzzy_score < 0.5:
        base_score = max(0.0, base_score - 0.2)
    
    return min(1.0, max(0.0, base_score))


def calculate_overall_confidence(provider_data: Dict[str, Any]) -> float:
    """
    Calculate overall confidence score for a provider
    
    Args:
        provider_data: Dictionary with confidence scores for each field
    
    Returns:
        Overall confidence score (0-1)
    """
    weights = {
        "confidence_name": 0.25,
        "confidence_phone": 0.20,
        "confidence_address": 0.25,
        "confidence_specialty": 0.15,
        "confidence_email": 0.10,
        "confidence_website": 0.05
    }
    
    total_weight = 0.0
    weighted_sum = 0.0
    
    for field, weight in weights.items():
        score = provider_data.get(field, 0.0)
        weighted_sum += score * weight
        total_weight += weight
    
    if total_weight == 0:
        return 0.0
    
    return weighted_sum / total_weight


def validate_phone(phone: Optional[str]) -> Tuple[bool, float]:
    """Validate phone number format"""
    if not phone:
        return False, 0.0
    
    # Remove non-digits
    digits = re.sub(r'\D', '', phone)
    
    # Check if it's a valid US phone number (10 or 11 digits)
    if len(digits) == 10:
        return True, 1.0
    elif len(digits) == 11 and digits[0] == '1':
        return True, 0.9
    else:
        return False, 0.3


def validate_email(email: Optional[str]) -> Tuple[bool, float]:
    """Validate email format"""
    if not email:
        return False, 0.0
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, 1.0
    else:
        return False, 0.2


def validate_zip_code(zip_code: Optional[str]) -> Tuple[bool, float]:
    """Validate ZIP code format"""
    if not zip_code:
        return False, 0.0
    
    # Remove non-digits
    digits = re.sub(r'\D', '', zip_code)
    
    if len(digits) == 5:
        return True, 1.0
    elif len(digits) == 9:
        return True, 0.95
    else:
        return False, 0.3

