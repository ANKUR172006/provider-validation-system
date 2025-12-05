"""
NPI Registry lookup service (mock implementation)
"""
import httpx
from typing import Dict, Any, Optional
import random


class NPIService:
    """Service for NPI registry lookups"""
    
    def __init__(self):
        self.base_url = "https://npiregistry.cms.hhs.gov/api/"
        # Mock NPI database for demo
        self.mock_npi_db = {
            "1234567890": {
                "npi": "1234567890",
                "name": "John Smith",
                "specialty": "Cardiology",
                "address": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "phone": "2125551234"
            },
            "9876543210": {
                "npi": "9876543210",
                "name": "Jane Doe",
                "specialty": "Pediatrics",
                "address": "456 Oak Ave",
                "city": "Los Angeles",
                "state": "CA",
                "zip": "90001",
                "phone": "3105555678"
            }
        }
    
    async def lookup_npi(self, npi: str) -> Optional[Dict[str, Any]]:
        """
        Lookup provider by NPI number
        
        Args:
            npi: NPI number (10 digits)
        
        Returns:
            Provider data from NPI registry or None
        """
        if not npi or len(npi) != 10:
            return None
        
        # Check mock database first
        if npi in self.mock_npi_db:
            return self.mock_npi_db[npi]
        
        # Mock API call - in production, this would call the real NPI API
        try:
            # Simulate API call delay
            import asyncio
            await asyncio.sleep(0.1)
            
            # For demo: randomly return data or None
            if random.random() > 0.3:  # 70% chance of finding a match
                return {
                    "npi": npi,
                    "name": f"Provider {npi[:5]}",
                    "specialty": random.choice(["Cardiology", "Pediatrics", "Orthopedics", "Dermatology"]),
                    "address": f"{random.randint(100, 999)} Provider St",
                    "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston"]),
                    "state": random.choice(["NY", "CA", "IL", "TX"]),
                    "zip": f"{random.randint(10000, 99999)}",
                    "phone": f"{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}"
                }
            
            return None
        except Exception as e:
            print(f"Error in NPI lookup: {e}")
            return None
    
    async def search_by_name(self, name: str, state: Optional[str] = None) -> list[Dict[str, Any]]:
        """
        Search providers by name
        
        Args:
            name: Provider name
            state: Optional state filter
        
        Returns:
            List of matching providers
        """
        results = []
        
        # Search mock database
        name_lower = name.lower()
        for npi, provider in self.mock_npi_db.items():
            if name_lower in provider["name"].lower():
                if not state or provider["state"] == state:
                    results.append(provider)
        
        # Mock additional results
        if len(results) < 3:
            for i in range(2):
                results.append({
                    "npi": f"{random.randint(1000000000, 9999999999)}",
                    "name": f"{name} {i+1}",
                    "specialty": random.choice(["Cardiology", "Pediatrics", "Orthopedics"]),
                    "address": f"{random.randint(100, 999)} St",
                    "city": "Unknown",
                    "state": state or "NY",
                    "zip": f"{random.randint(10000, 99999)}",
                    "phone": f"{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}"
                })
        
        return results[:5]  # Return max 5 results


