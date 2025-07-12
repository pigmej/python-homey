"""Device model for the Homey API."""

from typing import Any, Dict, List, Optional, Union

from pydantic import Field

from .base import BaseModel


class DeviceCapability(BaseModel):
    """Represents a device capability."""

    id: Optional[str] = Field(None, description="Capability ID")
    title: Optional[str] = Field(None, description="Capability title")
    desc: Optional[str] = Field(None, description="Capability description")
    type: Optional[str] = Field(None, description="Capability type")
    getable: bool = Field(True, description="Whether the capability is getable")
    setable: bool = Field(True, description="Whether the capability is setable")
    reportable: bool = Field(True, description="Whether the capability is reportable")
    value: Optional[Union[bool, int, float, str]] = Field(
        None, description="Current value"
    )
    units: Optional[str] = Field(None, description="Units of measurement")
    min: Optional[Union[int, float]] = Field(None, description="Minimum value")
    max: Optional[Union[int, float]] = Field(None, description="Maximum value")
    step: Optional[Union[int, float]] = Field(None, description="Step value")
    decimals: Optional[int] = Field(None, description="Number of decimal places")
    duration: Optional[bool] = Field(
        None, description="Whether capability supports duration"
    )

    def __str__(self) -> str:
        """String representation of the capability."""
        return f"DeviceCapability(id={self.id}, value={self.value})"


class Device(BaseModel):
    """Represents a Homey device."""

    id: Optional[str] = Field(None, description="Device ID")
    name: Optional[str] = Field(None, description="Device name")
    driverUri: Optional[str] = Field(None, description="Driver URI")
    driverId: Optional[str] = Field(None, description="Driver ID")
    zone: Optional[str] = Field(None, description="Zone ID")
    icon: Optional[str] = Field(None, description="Device icon")
    iconObj: Optional[Dict[str, Any]] = Field(None, description="Device icon object")
    class_: Optional[str] = Field(None, alias="class", description="Device class")
    energy: Optional[Dict[str, Any]] = Field(None, description="Energy information")
    energyObj: Optional[Dict[str, Any]] = Field(None, description="Energy object")
    insights: Optional[List[Dict[str, Any]]] = Field(
        None, description="Device insights"
    )
    hidden: Optional[bool] = Field(None, description="Whether the device is hidden")
    ready: bool = Field(True, description="Whether the device is ready")
    available: bool = Field(True, description="Whether the device is available")
    repair: Optional[bool] = Field(False, description="Whether the device needs repair")
    unpair: Optional[bool] = Field(False, description="Whether the device is unpaired")
    speechExamples: Optional[List[str]] = Field(None, description="Speech examples")
    images: Optional[List[Dict[str, Any]]] = Field(None, description="Device images")
    ui: Optional[Dict[str, Any]] = Field(None, description="UI configuration")
    uiIndicator: Optional[str] = Field(None, description="UI indicator")
    capabilities: List[str] = Field(default_factory=list, description="Capability IDs")
    capabilitiesObj: Optional[Dict[str, DeviceCapability]] = Field(
        None, description="Capabilities object"
    )
    settings: Optional[Dict[str, Any]] = Field(None, description="Device settings")
    # settingsObj: Optional[Dict[str, Any]] = Field(None, description="Settings object")
    settingsObj: Optional[bool] = Field(
        True, description="Whether the settings are attached"
    )
    flags: Optional[List[str]] = Field(None, description="Device flags")
    virtualClass: Optional[str] = Field(None, description="Virtual device class")
    note: Optional[str] = Field(
        None, description="Device note, might contain additional information"
    )

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization processing."""
        # Convert capabilities object to DeviceCapability instances
        if self.capabilitiesObj:
            capabilities = {}
            for cap_id, cap_data in self.capabilitiesObj.items():
                if isinstance(cap_data, dict):
                    capabilities[cap_id] = DeviceCapability(id=cap_id, **cap_data)
                else:
                    capabilities[cap_id] = cap_data
            self.capabilitiesObj = capabilities

    def get_capability(self, capability_id: str) -> Optional[DeviceCapability]:
        """Get a capability by ID."""
        if self.capabilitiesObj:
            return self.capabilitiesObj.get(capability_id)
        return None

    def get_capability_value(
        self, capability_id: str
    ) -> Optional[Union[bool, int, float, str]]:
        """Get the current value of a capability."""
        capability = self.get_capability(capability_id)
        if capability:
            return capability.value
        return None

    def has_capability(self, capability_id: str) -> bool:
        """Check if the device has a specific capability."""
        return capability_id in self.capabilities

    def is_online(self) -> bool:
        """Check if the device is online and available."""
        return self.available and self.ready and not self.repair

    def get_zone_id(self) -> Optional[str]:
        """Get the zone ID of the device."""
        return self.zone

    def get_driver_id(self) -> Optional[str]:
        """Get the driver ID of the device."""
        return self.driverId

    def model_dump_compact(self, *args, **kwargs) -> Dict[str, Any]:
        exc = kwargs.get("exclude", [])
        exc.extend(
            [
                "capabilitiesObj",
                "color",
                "data",
                "driverId",
                "driver_id",
                "driverUri",
                "driver_url",
                "flags",
                "icon",
                "iconObj",
                "iconOverride",
                "images",
                "insights",  # use get_device_insights() instead, save some more space in the output
                "ownerUri",
                "settingsObj",
                "settings",
                "speechExamples",
                "uiIndicator",
                "unpair",
                "unavailableMessage",
                "warningMessage",
                "created_at",
                "updated_at",
                "ui",
            ]
        )
        if not self.energy:
            exc.append("energyObj")
        kwargs["exclude"] = exc
        return self.model_dump(*args, **kwargs)

    def __str__(self) -> str:
        """String representation of the device."""
        status = "online" if self.is_online() else "offline"
        return f"Device(id={self.id}, name={self.name}, status={status})"
