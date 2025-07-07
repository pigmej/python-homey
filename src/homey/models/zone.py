"""Zone model for the Homey API."""

from typing import Optional

from pydantic import Field

from .base import BaseModel


class Zone(BaseModel):
    """Represents a Homey zone."""

    id: Optional[str] = Field(None, description="Zone ID")
    name: Optional[str] = Field(None, description="Zone name")
    parent: Optional[str] = Field(None, description="Parent zone ID")
    icon: Optional[str] = Field(None, description="Zone icon")
    active: bool = Field(True, description="Whether the zone is active")
    activeLastUpdated: Optional[str] = Field(None, description="Last active update")

    def is_active(self) -> bool:
        """Check if the zone is active."""
        return self.active

    def get_parent_id(self) -> Optional[str]:
        """Get the parent zone ID."""
        return self.parent

    def is_root_zone(self) -> bool:
        """Check if this is a root zone (no parent)."""
        return self.parent is None

    def __str__(self) -> str:
        """String representation of the zone."""
        return f"Zone(id={self.id}, name={self.name}, active={self.active})"
