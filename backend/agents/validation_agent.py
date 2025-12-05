"""
Data Validation Agent - Validates provider data against external sources
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from agents.base_agent import BaseAgent
from services.npi_service import NPIService
from services.maps_service import MapsService
from services.website_service import WebsiteService
from utils.fuzzy_match import fuzzy_match_strings
from utils.confidence import calculate_confidence_score, validate_phone, validate_email


class ValidationAgent(BaseAgent):
    """Agent responsible for validating provider data"""
    
    def __init__(self):
        super().__init__("validation")
        self.npi_service = NPIService()
        self.maps_service = MapsService()
        self.website_service = WebsiteService()
    
    async def process(self, provider_data: Dict[str, Any], session: AsyncSession) -> Dict[str, Any]:
        """Validate provider data"""
        validated_data = {
            "validated_name": provider_data.get("name"),
            "validated_phone": provider_data.get("phone"),
            "validated_address": provider_data.get("address"),
            "validated_specialty": provider_data.get("specialty"),
            "validated_email": provider_data.get("email"),
            "validated_website": provider_data.get("website"),
            "confidence_name": 0.0,
            "confidence_phone": 0.0,
            "confidence_address": 0.0,
            "confidence_specialty": 0.0,
            "confidence_email": 0.0,
            "issues": []
        }
        
        # Validate NPI and get registry data
        npi = provider_data.get("npi")
        if npi:
            npi_data = await self.npi_service.lookup_npi(npi)
            if npi_data:
                # Validate name against NPI registry
                name_match, name_score = fuzzy_match_strings(
                    provider_data.get("name", ""),
                    npi_data.get("name", "")
                )
                validated_data["validated_name"] = npi_data.get("name")
                validated_data["confidence_name"] = calculate_confidence_score(
                    provider_data.get("name"),
                    npi_data.get("name"),
                    external_match=True,
                    fuzzy_score=name_score
                )
                
                # Validate address
                npi_address = f"{npi_data.get('address', '')} {npi_data.get('city', '')} {npi_data.get('state', '')}"
                provider_address = f"{provider_data.get('address', '')} {provider_data.get('city', '')} {provider_data.get('state', '')}"
                addr_match, addr_score = fuzzy_match_strings(provider_address, npi_address)
                validated_data["validated_address"] = npi_address
                validated_data["confidence_address"] = calculate_confidence_score(
                    provider_address,
                    npi_address,
                    external_match=True,
                    fuzzy_score=addr_score
                )
                
                # Validate specialty
                if npi_data.get("specialty"):
                    spec_match, spec_score = fuzzy_match_strings(
                        provider_data.get("specialty", ""),
                        npi_data.get("specialty", "")
                    )
                    validated_data["validated_specialty"] = npi_data.get("specialty")
                    validated_data["confidence_specialty"] = calculate_confidence_score(
                        provider_data.get("specialty"),
                        npi_data.get("specialty"),
                        external_match=True,
                        fuzzy_score=spec_score
                    )
                
                # Validate phone
                if npi_data.get("phone"):
                    phone_match, phone_score = fuzzy_match_strings(
                        provider_data.get("phone", ""),
                        npi_data.get("phone", "")
                    )
                    validated_data["validated_phone"] = npi_data.get("phone")
                    validated_data["confidence_phone"] = calculate_confidence_score(
                        provider_data.get("phone"),
                        npi_data.get("phone"),
                        external_match=True,
                        fuzzy_score=phone_score
                    )
            else:
                validated_data["issues"].append("NPI not found in registry")
        else:
            validated_data["issues"].append("NPI missing")
        
        # Validate address with Google Maps
        if provider_data.get("address"):
            is_valid, maps_data = await self.maps_service.validate_address(
                provider_data.get("address"),
                provider_data.get("city"),
                provider_data.get("state"),
                provider_data.get("zip_code")
            )
            if is_valid and maps_data:
                # Boost address confidence if Maps validates it
                if validated_data["confidence_address"] < 0.7:
                    validated_data["confidence_address"] = min(1.0, validated_data["confidence_address"] + 0.2)
                    validated_data["validated_address"] = maps_data.get("formatted_address", validated_data["validated_address"])
            else:
                validated_data["issues"].append("Address not validated by Google Maps")
                validated_data["confidence_address"] = max(0.0, validated_data["confidence_address"] - 0.2)
        
        # Validate phone format
        phone = provider_data.get("phone")
        if phone:
            is_valid, phone_score = validate_phone(phone)
            if not is_valid:
                validated_data["issues"].append("Phone number format invalid")
            validated_data["confidence_phone"] = max(validated_data["confidence_phone"], phone_score * 0.5)
        
        # Validate email format
        email = provider_data.get("email")
        if email:
            is_valid, email_score = validate_email(email)
            validated_data["validated_email"] = email
            validated_data["confidence_email"] = email_score
            if not is_valid:
                validated_data["issues"].append("Email format invalid")
        
        # Validate website
        website = provider_data.get("website")
        if website:
            website_data = await self.website_service.scrape_website(website)
            if website_data:
                # Cross-validate name and contact info
                if website_data.get("name"):
                    name_match, name_score = fuzzy_match_strings(
                        provider_data.get("name", ""),
                        website_data.get("name", "")
                    )
                    if name_score > 0.8:
                        validated_data["confidence_name"] = max(validated_data["confidence_name"], name_score * 0.3)
                
                # Validate phone from website
                if website_data.get("phone"):
                    phone_match, phone_score = fuzzy_match_strings(
                        provider_data.get("phone", ""),
                        website_data.get("phone", "")
                    )
                    if phone_match:
                        validated_data["confidence_phone"] = max(validated_data["confidence_phone"], phone_score * 0.3)
                        validated_data["validated_phone"] = website_data.get("phone")
        
        return validated_data


