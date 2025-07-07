"""App model for the Homey API."""

from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import BaseModel


class App(BaseModel):
    """Represents a Homey app."""

    id: Optional[str] = Field(None, description="App ID")
    name: Optional[str] = Field(None, description="App name")
    version: Optional[str] = Field(None, description="App version")
    origin: Optional[str] = Field(None, description="App origin")
    channel: Optional[str] = Field(None, description="App channel")
    autoupdate: bool = Field(True, description="Whether auto-update is enabled")
    enabled: bool = Field(True, description="Whether the app is enabled")
    installed: bool = Field(False, description="Whether the app is installed")
    state: Optional[str] = Field(None, description="App state")
    crashed: bool = Field(False, description="Whether the app has crashed")
    permissions: Optional[List[str]] = Field(None, description="App permissions")
    settings: Optional[Dict[str, Any]] = Field(None, description="App settings")
    brandColor: Optional[str] = Field(None, description="Brand color")
    category: Optional[str] = Field(None, description="App category")
    compatibility: Optional[str] = Field(None, description="Compatibility version")
    description: Optional[Dict[str, str]] = Field(None, description="App description")
    homeyCommunityTopicId: Optional[int] = Field(None, description="Community topic ID")
    images: Optional[Dict[str, str]] = Field(None, description="App images")
    platforms: Optional[List[str]] = Field(None, description="Supported platforms")
    tags: Optional[Dict[str, List[str]]] = Field(None, description="App tags")
    author: Optional[Dict[str, Any]] = Field(None, description="App author")

    def is_enabled(self) -> bool:
        """Check if the app is enabled."""
        return self.enabled

    def is_installed(self) -> bool:
        """Check if the app is installed."""
        return self.installed

    def is_crashed(self) -> bool:
        """Check if the app has crashed."""
        return self.crashed

    def is_running(self) -> bool:
        """Check if the app is running (installed, enabled, not crashed)."""
        return self.installed and self.enabled and not self.crashed

    def get_version(self) -> Optional[str]:
        """Get the app version."""
        return self.version

    def get_state(self) -> Optional[str]:
        """Get the app state."""
        return self.state

    def get_permissions(self) -> List[str]:
        """Get the app permissions."""
        return self.permissions or []

    def get_category(self) -> Optional[str]:
        """Get the app category."""
        return self.category

    def get_author(self) -> Optional[Dict[str, Any]]:
        """Get the app author information."""
        return self.author

    def get_description(self, language: str = "en") -> Optional[str]:
        """Get the app description in the specified language."""
        if self.description:
            return self.description.get(language, self.description.get("en"))
        return None

    def has_permission(self, permission: str) -> bool:
        """Check if the app has a specific permission."""
        return permission in self.get_permissions()

    def __str__(self) -> str:
        """String representation of the app."""
        status = "running" if self.is_running() else "stopped"
        if self.is_crashed():
            status = "crashed"
        return f"App(id={self.id}, name={self.name}, version={self.version}, status={status})"
