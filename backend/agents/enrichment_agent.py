"""
Information Enrichment Agent - Enriches missing provider information
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from agents.base_agent import BaseAgent
from services.npi_service import NPIService
from services.website_service import WebsiteService


class EnrichmentAgent(BaseAgent):
    """Agent responsible for enriching missing provider data"""
    
    def __init__(self):
        super().__init__("enrichment")
        self.npi_service = NPIService()
        self.website_service = WebsiteService()
    
    async def process(self, provider_data: Dict[str, Any], session: AsyncSession) -> Dict[str, Any]:
        """Enrich missing provider data"""
        enriched_data = {
            "enriched_fields": [],
            "enriched_data": {}
        }
        
        # Enrich missing NPI
        if not provider_data.get("npi") and provider_data.get("name"):
            npi_results = await self.npi_service.search_by_name(
                provider_data.get("name"),
                provider_data.get("state")
            )
            if npi_results:
                # Use first match
                best_match = npi_results[0]
                enriched_data["enriched_data"]["npi"] = best_match.get("npi")
                enriched_data["enriched_fields"].append("npi")
        
        # Enrich missing address from NPI
        if not provider_data.get("address") and provider_data.get("npi"):
            npi_data = await self.npi_service.lookup_npi(provider_data.get("npi"))
            if npi_data:
                if npi_data.get("address"):
                    enriched_data["enriched_data"]["address"] = npi_data.get("address")
                    enriched_data["enriched_data"]["city"] = npi_data.get("city")
                    enriched_data["enriched_data"]["state"] = npi_data.get("state")
                    enriched_data["enriched_data"]["zip_code"] = npi_data.get("zip")
                    enriched_data["enriched_fields"].extend(["address", "city", "state", "zip_code"])
        
        # Enrich missing phone from NPI
        if not provider_data.get("phone") and provider_data.get("npi"):
            npi_data = await self.npi_service.lookup_npi(provider_data.get("npi"))
            if npi_data and npi_data.get("phone"):
                enriched_data["enriched_data"]["phone"] = npi_data.get("phone")
                enriched_data["enriched_fields"].append("phone")
        
        # Enrich missing specialty from NPI
        if not provider_data.get("specialty") and provider_data.get("npi"):
            npi_data = await self.npi_service.lookup_npi(provider_data.get("npi"))
            if npi_data and npi_data.get("specialty"):
                enriched_data["enriched_data"]["specialty"] = npi_data.get("specialty")
                enriched_data["enriched_fields"].append("specialty")
        
        # Enrich from website
        website = provider_data.get("website")
        if website:
            website_data = await self.website_service.scrape_website(website)
            if website_data:
                # Enrich missing fields from website
                if not provider_data.get("phone") and website_data.get("phone"):
                    enriched_data["enriched_data"]["phone"] = website_data.get("phone")
                    enriched_data["enriched_fields"].append("phone")
                
                if not provider_data.get("address") and website_data.get("address"):
                    enriched_data["enriched_data"]["address"] = website_data.get("address")
                    enriched_data["enriched_data"]["city"] = website_data.get("city")
                    enriched_data["enriched_data"]["state"] = website_data.get("state")
                    enriched_data["enriched_fields"].extend(["address", "city", "state"])
                
                if not provider_data.get("specialty") and website_data.get("specialties"):
                    enriched_data["enriched_data"]["specialty"] = ", ".join(website_data.get("specialties", []))
                    enriched_data["enriched_fields"].append("specialty")
        
        return enriched_data


