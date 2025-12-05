"""
Google Maps validation service (mock implementation)
"""
from typing import Dict, Any, Optional, Tuple
import random


class MapsService:
    """Service for Google Maps address validation"""
    
    def __init__(self):
        # Mock validated addresses for demo
        self.validated_addresses = {
            "123 main st new york ny 10001": {
                "formatted_address": "123 Main St, New York, NY 10001",
                "valid": True,
                "lat": 40.7128,
                "lng": -74.0060,
                "place_id": "mock_place_123"
            },
            "456 oak ave los angeles ca 90001": {
                "formatted_address": "456 Oak Ave, Los Angeles, CA 90001",
                "valid": True,
                "lat": 34.0522,
                "lng": -118.2437,
                "place_id": "mock_place_456"
            }
        }
    
    async def validate_address(
        self,
        address: str,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate address using Google Maps API (mock)
        
        Args:
            address: Street address
            city: City name
            state: State code
            zip_code: ZIP code
        
        Returns:
            Tuple of (is_valid, address_data)
        """
        if not address:
            return False, None
        
        # Normalize address for lookup
        full_address = f"{address} {city or ''} {state or ''} {zip_code or ''}".lower().strip()
        
        # Check mock database
        if full_address in self.validated_addresses:
            return True, self.validated_addresses[full_address]
        
        # Mock validation - simulate API call
        import asyncio
        await asyncio.sleep(0.1)
        
        # Random validation result for demo
        is_valid = random.random() > 0.2  # 80% valid
        
        if is_valid:
            return True, {
                "formatted_address": f"{address}, {city or 'Unknown'}, {state or 'XX'} {zip_code or '00000'}",
                "valid": True,
                "lat": random.uniform(25.0, 49.0),
                "lng": random.uniform(-125.0, -66.0),
                "place_id": f"mock_place_{random.randint(1000, 9999)}"
            }
        else:
            return False, {
                "formatted_address": None,
                "valid": False,
                "error": "Address not found"
            }
    
    async def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """Geocode an address to get coordinates"""
        is_valid, data = await self.validate_address(address)
        if is_valid and data:
            return {
                "lat": data.get("lat"),
                "lng": data.get("lng")
            }
        return None
    
    async def reverse_geocode(self, lat: float, lng: float) -> Optional[str]:
        """Reverse geocode coordinates to address"""
        # Mock implementation
        return f"Address at {lat}, {lng}"


