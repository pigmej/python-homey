"""Device manager for the Homey API."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from ..exceptions import HomeyDeviceError, HomeyValidationError
from ..models.device import Device, DeviceCapability
from .base import BaseManager

if TYPE_CHECKING:
    from ..client import HomeyClient


class DeviceManager(BaseManager):
    """Manager for Homey devices."""

    def __init__(self, client: "HomeyClient") -> None:
        """Initialize the device manager."""
        super().__init__(client)
        self._endpoint = "/manager/devices/device"

    async def get_devices(self) -> List[Device]:
        """Get all devices."""
        try:
            response_data = await self._get(self._endpoint)
            # Devices are returned as a dictionary with device IDs as keys
            if isinstance(response_data, dict):
                devices = []
                for device_id, device_data in response_data.items():
                    device_data["id"] = device_id
                    devices.append(Device(**device_data))
                return devices
            return []
        except Exception as e:
            raise HomeyDeviceError(f"Failed to get devices: {str(e)}")

    async def get_device(self, device_id: str) -> Device:
        """Get a specific device by ID."""
        self._validate_id(device_id)
        try:
            response_data = await self._get(f"{self._endpoint}/{device_id}")
            response_data["id"] = device_id
            return Device(**response_data)
        except Exception as e:
            raise HomeyDeviceError(
                f"Failed to get device: {str(e)}", device_id=device_id
            )

    async def set_capability_value(
        self,
        device_id: str,
        capability_id: str,
        value: Union[bool, int, float, str],
        opts: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Set a capability value for a device."""
        self._validate_id(device_id)
        if not capability_id:
            raise HomeyValidationError("Capability ID cannot be empty")

        data: Dict[str, Any] = {
            "capabilityId": capability_id,
            "value": value,
        }
        if opts:
            data["opts"] = opts

        try:
            await self._put(
                f"{self._endpoint}/{device_id}/capabilities/{capability_id}", data=data
            )
            return True
        except Exception as e:
            raise HomeyDeviceError(
                f"Failed to set capability value: {str(e)}", device_id=device_id
            )

    async def get_capability_value(
        self, device_id: str, capability_id: str
    ) -> Optional[Union[bool, int, float, str]]:
        """Get a capability value for a device."""
        self._validate_id(device_id)
        if not capability_id:
            raise HomeyValidationError("Capability ID cannot be empty")

        try:
            response_data = await self._get(
                f"{self._endpoint}/{device_id}/capabilities/{capability_id}"
            )
            return response_data.get("value")
        except Exception as e:
            raise HomeyDeviceError(
                f"Failed to get capability value: {str(e)}", device_id=device_id
            )

    async def turn_on(self, device_id: str) -> bool:
        """Turn on a device (set onoff capability to true)."""
        return await self.set_capability_value(device_id, "onoff", True)

    async def turn_off(self, device_id: str) -> bool:
        """Turn off a device (set onoff capability to false)."""
        return await self.set_capability_value(device_id, "onoff", False)

    async def toggle(self, device_id: str) -> bool:
        """Toggle a device's onoff state."""
        current_value = await self.get_capability_value(device_id, "onoff")
        if current_value is None:
            raise HomeyDeviceError(
                "Device does not have onoff capability", device_id=device_id
            )
        return await self.set_capability_value(device_id, "onoff", not current_value)

    async def set_dim_level(self, device_id: str, level: float) -> bool:
        """Set the dim level of a device (0.0 to 1.0)."""
        if not 0.0 <= level <= 1.0:
            raise HomeyValidationError("Dim level must be between 0.0 and 1.0")
        return await self.set_capability_value(device_id, "dim", level)

    async def set_target_temperature(self, device_id: str, temperature: float) -> bool:
        """Set the target temperature of a device."""
        return await self.set_capability_value(
            device_id, "target_temperature", temperature
        )

    async def get_devices_by_zone(self, zone_id: str) -> List[Device]:
        """Get all devices in a specific zone."""
        self._validate_id(zone_id)
        all_devices = await self.get_devices()
        return [device for device in all_devices if device.zone == zone_id]

    async def get_devices_by_class(self, device_class: str) -> List[Device]:
        """Get all devices of a specific class."""
        if not device_class:
            raise HomeyValidationError("Device class cannot be empty")
        all_devices = await self.get_devices()
        return [device for device in all_devices if device.class_ == device_class]

    async def get_devices_by_capability(self, capability_id: str) -> List[Device]:
        """Get all devices that have a specific capability."""
        if not capability_id:
            raise HomeyValidationError("Capability ID cannot be empty")
        all_devices = await self.get_devices()
        return [
            device for device in all_devices if device.has_capability(capability_id)
        ]

    async def get_online_devices(self) -> List[Device]:
        """Get all online devices."""
        all_devices = await self.get_devices()
        return [device for device in all_devices if device.is_online()]

    async def get_offline_devices(self) -> List[Device]:
        """Get all offline devices."""
        all_devices = await self.get_devices()
        return [device for device in all_devices if not device.is_online()]

    async def search_devices(self, query: str) -> List[Device]:
        """Search devices by name."""
        if not query:
            raise HomeyValidationError("Search query cannot be empty")

        all_devices = await self.get_devices()
        query_lower = query.lower()
        return [
            device
            for device in all_devices
            if device.name and query_lower in device.name.lower()
        ]

    async def get_device_flows(self, device_id: str) -> List[Dict[str, Any]]:
        """Get flows associated with a device."""
        self._validate_id(device_id)
        try:
            response_data = await self._get(f"{self._endpoint}/{device_id}/flows")
            return response_data if isinstance(response_data, list) else []
        except Exception as e:
            raise HomeyDeviceError(
                f"Failed to get device flows: {str(e)}", device_id=device_id
            )

    async def get_device_insights(self, device_id: str) -> List[Dict[str, Any]]:
        """Get insights data for a device."""
        self._validate_id(device_id)
        try:
            response_data = await self._get(f"{self._endpoint}/{device_id}/insights")
            return response_data if isinstance(response_data, list) else []
        except Exception as e:
            raise HomeyDeviceError(
                f"Failed to get device insights: {str(e)}", device_id=device_id
            )

    async def repair_device(self, device_id: str) -> bool:
        """Repair a device."""
        self._validate_id(device_id)
        try:
            await self._post(f"{self._endpoint}/{device_id}/repair")
            return True
        except Exception as e:
            raise HomeyDeviceError(
                f"Failed to repair device: {str(e)}", device_id=device_id
            )

    async def unpair_device(self, device_id: str) -> bool:
        """Unpair a device."""
        self._validate_id(device_id)
        try:
            await self._delete(f"{self._endpoint}/{device_id}")
            return True
        except Exception as e:
            raise HomeyDeviceError(
                f"Failed to unpair device: {str(e)}", device_id=device_id
            )

    async def get_device_settings(self, device_id: str) -> Dict[str, Any]:
        """Get device settings."""
        self._validate_id(device_id)
        try:
            response_data = await self._get(f"{self._endpoint}/{device_id}/settings")
            return response_data if isinstance(response_data, dict) else {}
        except Exception as e:
            raise HomeyDeviceError(
                f"Failed to get device settings: {str(e)}", device_id=device_id
            )

    async def set_device_settings(
        self, device_id: str, settings: Dict[str, Any]
    ) -> bool:
        """Set device settings."""
        self._validate_id(device_id)
        if not settings:
            raise HomeyValidationError("Settings cannot be empty")

        try:
            await self._put(f"{self._endpoint}/{device_id}/settings", data=settings)
            return True
        except Exception as e:
            raise HomeyDeviceError(
                f"Failed to set device settings: {str(e)}", device_id=device_id
            )

    async def get_device_capabilities(
        self, device_id: str
    ) -> Dict[str, DeviceCapability]:
        """Get device capabilities."""
        device = await self.get_device(device_id)
        return device.capabilitiesObj or {}

    async def has_capability(self, device_id: str, capability_id: str) -> bool:
        """Check if a device has a specific capability."""
        device = await self.get_device(device_id)
        return device.has_capability(capability_id)
