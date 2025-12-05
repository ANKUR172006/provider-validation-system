"""
Quality Assurance Agent - Flags issues and suspicious providers
"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from agents.base_agent import BaseAgent
from utils.confidence import calculate_overall_confidence


class QAAgent(BaseAgent):
    """Agent responsible for quality assurance and flagging issues"""
    
    def __init__(self):
        super().__init__("qa")
    
    async def process(self, provider_data: Dict[str, Any], session: AsyncSession) -> Dict[str, Any]:
        """Perform QA checks and flag issues"""
        qa_results = {
            "needs_review": False,
            "is_suspicious": False,
            "issues": provider_data.get("issues", []),
            "validation_notes": ""
        }
        
        # Calculate overall confidence
        overall_confidence = calculate_overall_confidence(provider_data)
        provider_data["confidence_overall"] = overall_confidence
        
        # Flag if confidence is low
        if overall_confidence < 0.5:
            qa_results["needs_review"] = True
            qa_results["issues"].append("Low overall confidence score")
        
        # Flag if critical fields are missing
        critical_fields = ["name", "phone", "address"]
        missing_critical = []
        for field in critical_fields:
            if not provider_data.get(field) and not provider_data.get(f"validated_{field}"):
                missing_critical.append(field)
        
        if missing_critical:
            qa_results["needs_review"] = True
            qa_results["issues"].append(f"Missing critical fields: {', '.join(missing_critical)}")
        
        # Flag suspicious patterns
        suspicious_patterns = []
        
        # Check for mismatched data
        if provider_data.get("name") and provider_data.get("validated_name"):
            name_match_score = self._calculate_name_match(
                provider_data.get("name"),
                provider_data.get("validated_name")
            )
            if name_match_score < 0.7:
                suspicious_patterns.append("Name mismatch between original and validated")
        
        # Check for invalid phone
        if provider_data.get("phone"):
            phone_digits = ''.join(filter(str.isdigit, provider_data.get("phone", "")))
            if len(phone_digits) not in [10, 11]:
                suspicious_patterns.append("Invalid phone number format")
        
        # Check for suspicious address
        if provider_data.get("address"):
            address = provider_data.get("address", "").lower()
            suspicious_words = ["test", "example", "fake", "dummy", "12345"]
            if any(word in address for word in suspicious_words):
                suspicious_patterns.append("Suspicious address pattern")
        
        # Check for multiple issues
        if len(qa_results["issues"]) >= 3:
            qa_results["is_suspicious"] = True
            qa_results["issues"].append("Multiple validation issues detected")
        
        if suspicious_patterns:
            qa_results["is_suspicious"] = True
            qa_results["issues"].extend(suspicious_patterns)
        
        # Generate validation notes
        notes = []
        if qa_results["needs_review"]:
            notes.append("Requires manual review")
        if qa_results["is_suspicious"]:
            notes.append("Suspicious patterns detected")
        if overall_confidence >= 0.8:
            notes.append("High confidence validation")
        elif overall_confidence >= 0.6:
            notes.append("Moderate confidence validation")
        else:
            notes.append("Low confidence validation")
        
        qa_results["validation_notes"] = "; ".join(notes)
        
        return qa_results
    
    def _calculate_name_match(self, name1: str, name2: str) -> float:
        """Calculate name matching score"""
        from utils.fuzzy_match import calculate_similarity
        return calculate_similarity(name1, name2)


