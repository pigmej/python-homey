"""System model for Homey API system configuration."""

from typing import Any, Dict, Optional

from pydantic import Field

from .base import BaseModel


class SystemConfig(BaseModel):
    """Model for Homey system configuration settings."""

    # Geolocation settings
    location: Optional[Dict[str, Any]] = Field(
        None, description="Geographic location coordinates"
    )
    address: Optional[str] = Field(None, description="Physical address")

    # Internationalization settings
    language: Optional[str] = Field(None, description="System language")
    units: Optional[str] = Field(None, description="Unit system (metric/imperial)")

    # Additional system info (if needed)
    timezone: Optional[str] = Field(None, description="System timezone")
    country: Optional[str] = Field(None, description="Country code")

    def __init__(self, **data: Any) -> None:
        """Initialize SystemConfig with flexible data structure."""
        super().__init__(**data)

    def update_location(self, location: Dict[str, Any]) -> None:
        """Update location information."""
        self.location = location

    def update_address(self, address: str) -> None:
        """Update address information."""
        self.address = address

    def update_language(self, language: str) -> None:
        """Update system language."""
        self.language = language

    def update_units(self, units: str) -> None:
        """Update unit system."""
        self.units = units

    def get_location_coordinates(self) -> Optional[Dict[str, float]]:
        """Get location coordinates if available."""
        if self.location and isinstance(self.location, dict):
            lat = self.location.get("latitude")
            lon = self.location.get("longitude")
            if lat is not None and lon is not None:
                return {"latitude": float(lat), "longitude": float(lon)}
        return None

    def is_metric(self) -> bool:
        """Check if system uses metric units."""
        return self.units == "metric" if self.units else True

    def is_imperial(self) -> bool:
        """Check if system uses imperial units."""
        return self.units == "imperial" if self.units else False

    def __str__(self) -> str:
        """String representation of the system config."""
        return f"SystemConfig(language={self.language}, units={self.units}, address={self.address})"
