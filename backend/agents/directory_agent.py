"""
Directory Management Agent - Manages provider directory and prioritization
"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from agents.base_agent import BaseAgent
from utils.confidence import calculate_overall_confidence


class DirectoryAgent(BaseAgent):
    """Agent responsible for directory management and prioritization"""
    
    def __init__(self):
        super().__init__("directory")
    
    async def process(self, provider_data: Dict[str, Any], session: AsyncSession) -> Dict[str, Any]:
        """Process provider for directory inclusion"""
        directory_results = {
            "is_validated": False,
            "priority_score": 0.0,
            "directory_status": "pending"
        }
        
        # Calculate priority score based on multiple factors
        priority_factors = {
            "confidence": provider_data.get("confidence_overall", 0.0) * 0.4,
            "completeness": self._calculate_completeness(provider_data) * 0.3,
            "critical_fields": self._check_critical_fields(provider_data) * 0.3
        }
        
        priority_score = sum(priority_factors.values())
        directory_results["priority_score"] = priority_score
        
        # Determine if provider should be auto-validated
        if (
            provider_data.get("confidence_overall", 0.0) >= 0.8 and
            not provider_data.get("needs_review", False) and
            not provider_data.get("is_suspicious", False) and
            self._check_critical_fields(provider_data) >= 0.8
        ):
            directory_results["is_validated"] = True
            directory_results["directory_status"] = "validated"
        elif provider_data.get("needs_review", False) or provider_data.get("is_suspicious", False):
            directory_results["directory_status"] = "needs_review"
        else:
            directory_results["directory_status"] = "pending"
        
        return directory_results
    
    def _calculate_completeness(self, provider_data: Dict[str, Any]) -> float:
        """Calculate data completeness score"""
        fields = [
            "name", "npi", "specialty", "phone", "email",
            "address", "city", "state", "zip_code", "website"
        ]
        
        filled_fields = 0
        for field in fields:
            if provider_data.get(field) or provider_data.get(f"validated_{field}"):
                filled_fields += 1
        
        return filled_fields / len(fields)
    
    def _check_critical_fields(self, provider_data: Dict[str, Any]) -> float:
        """Check if critical fields are present"""
        critical_fields = ["name", "phone", "address"]
        present_fields = 0
        
        for field in critical_fields:
            if provider_data.get(field) or provider_data.get(f"validated_{field}"):
                present_fields += 1
        
        return present_fields / len(critical_fields)


