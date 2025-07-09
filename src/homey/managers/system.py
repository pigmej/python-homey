"""System manager for the Homey API."""

from typing import TYPE_CHECKING, Any, Dict, Optional

from ..exceptions import HomeyAPIError
from ..models.system import SystemConfig
from .base import BaseManager

if TYPE_CHECKING:
    from ..client import HomeyClient


class SystemManager(BaseManager):
    """Manager for Homey system configuration."""

    def __init__(self, client: "HomeyClient") -> None:
        """Initialize the system manager."""
        super().__init__(client)

    async def get_system_config(self) -> SystemConfig:
        """Get complete system configuration."""
        try:
            # Fetch all system configuration data
            location = await self._get_location()
            address = await self._get_address()
            language = await self._get_language()
            units = await self._get_units()

            # Create system config with all data
            return SystemConfig(
                location=location,
                address=address,
                language=language,
                units=units,
            )
        except Exception as e:
            raise HomeyAPIError(f"Failed to get system configuration: {str(e)}")

    async def get_location(self) -> Optional[Dict[str, Any]]:
        """Get system location from geolocation manager."""
        return await self._get_location()

    async def get_address(self) -> Optional[str]:
        """Get system address from geolocation manager."""
        return await self._get_address()

    async def get_language(self) -> Optional[str]:
        """Get system language from i18n manager."""
        return await self._get_language()

    async def get_units(self) -> Optional[str]:
        """Get system units from i18n manager."""
        return await self._get_units()

    async def _get_location(self) -> Optional[Dict[str, Any]]:
        """Internal method to get location from geolocation manager."""
        try:
            response_data = await self._get("/manager/geolocation/option/location")
            return response_data if isinstance(response_data, dict) else None
        except Exception as e:
            raise HomeyAPIError(f"Failed to get location: {str(e)}")

    async def _get_address(self) -> Optional[str]:
        """Internal method to get address from geolocation manager."""
        try:
            response_data = await self._get("/manager/geolocation/option/address")
            # Handle different response formats
            if isinstance(response_data, dict):
                return response_data.get("address") or response_data.get("value")
            elif isinstance(response_data, str):
                return response_data
            return None
        except Exception as e:
            raise HomeyAPIError(f"Failed to get address: {str(e)}")

    async def _get_language(self) -> Optional[str]:
        """Internal method to get language from i18n manager."""
        try:
            response_data = await self._get("/manager/i18n/option/language")
            # Handle different response formats
            if isinstance(response_data, dict):
                return response_data.get("language") or response_data.get("value")
            elif isinstance(response_data, str):
                return response_data
            return None
        except Exception as e:
            raise HomeyAPIError(f"Failed to get language: {str(e)}")

    async def _get_units(self) -> Optional[str]:
        """Internal method to get units from i18n manager."""
        try:
            response_data = await self._get("/manager/i18n/option/units")
            # Handle different response formats
            if isinstance(response_data, dict):
                return response_data.get("units") or response_data.get("value")
            elif isinstance(response_data, str):
                return response_data
            return None
        except Exception as e:
            raise HomeyAPIError(f"Failed to get units: {str(e)}")

    async def set_location(self, location: Dict[str, Any]) -> bool:
        """Set system location."""
        try:
            await self._put("/manager/geolocation/option/location", data=location)
            return True
        except Exception as e:
            raise HomeyAPIError(f"Failed to set location: {str(e)}")

    async def set_address(self, address: str) -> bool:
        """Set system address."""
        try:
            data = {"address": address}
            await self._put("/manager/geolocation/option/address", data=data)
            return True
        except Exception as e:
            raise HomeyAPIError(f"Failed to set address: {str(e)}")

    async def set_language(self, language: str) -> bool:
        """Set system language."""
        try:
            data = {"language": language}
            await self._put("/manager/i18n/option/language", data=data)
            return True
        except Exception as e:
            raise HomeyAPIError(f"Failed to set language: {str(e)}")

    async def set_units(self, units: str) -> bool:
        """Set system units."""
        try:
            data = {"units": units}
            await self._put("/manager/i18n/option/units", data=data)
            return True
        except Exception as e:
            raise HomeyAPIError(f"Failed to set units: {str(e)}")

    async def update_system_config(self, config: SystemConfig) -> SystemConfig:
        """Update system configuration with new values."""
        try:
            # Update each field that has a value
            if config.location is not None:
                await self.set_location(config.location)

            if config.address is not None:
                await self.set_address(config.address)

            if config.language is not None:
                await self.set_language(config.language)

            if config.units is not None:
                await self.set_units(config.units)

            # Return updated configuration
            return await self.get_system_config()
        except Exception as e:
            raise HomeyAPIError(f"Failed to update system configuration: {str(e)}")
