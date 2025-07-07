"""App manager for the Homey API."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..exceptions import HomeyAppError, HomeyValidationError
from ..models.app import App
from .base import BaseManager

if TYPE_CHECKING:
    from ..client import HomeyClient


class AppManager(BaseManager):
    """Manager for Homey apps."""

    def __init__(self, client: "HomeyClient") -> None:
        """Initialize the app manager."""
        super().__init__(client)
        self._endpoint = "/manager/apps"

    async def get_apps(self) -> List[App]:
        """Get all apps."""
        try:
            response_data = await self._get(self._endpoint)
            # Apps are returned as a dictionary with app IDs as keys
            if isinstance(response_data, dict):
                apps = []
                for app_id, app_data in response_data.items():
                    app_data["id"] = app_id
                    apps.append(App(**app_data))
                return apps
            return []
        except Exception as e:
            raise HomeyAppError(f"Failed to get apps: {str(e)}")

    async def get_app(self, app_id: str) -> App:
        """Get a specific app by ID."""
        self._validate_id(app_id)
        try:
            response_data = await self._get(f"{self._endpoint}/{app_id}")
            response_data["id"] = app_id
            return App(**response_data)
        except Exception as e:
            raise HomeyAppError(f"Failed to get app: {str(e)}", app_id=app_id)

    async def install_app(self, app_id: str, channel: str = "stable") -> App:
        """Install an app."""
        self._validate_id(app_id)
        if channel not in ["stable", "test", "beta", "alpha"]:
            raise HomeyValidationError(
                "Invalid channel. Must be one of: stable, test, beta, alpha"
            )

        data = {"channel": channel}
        try:
            response_data = await self._post(
                f"{self._endpoint}/{app_id}/install", data=data
            )
            response_data["id"] = app_id
            return App(**response_data)
        except Exception as e:
            raise HomeyAppError(f"Failed to install app: {str(e)}", app_id=app_id)

    async def uninstall_app(self, app_id: str) -> bool:
        """Uninstall an app."""
        self._validate_id(app_id)
        try:
            await self._delete(f"{self._endpoint}/{app_id}")
            return True
        except Exception as e:
            raise HomeyAppError(f"Failed to uninstall app: {str(e)}", app_id=app_id)

    async def enable_app(self, app_id: str) -> App:
        """Enable an app."""
        self._validate_id(app_id)
        try:
            response_data = await self._post(f"{self._endpoint}/{app_id}/enable")
            response_data["id"] = app_id
            return App(**response_data)
        except Exception as e:
            raise HomeyAppError(f"Failed to enable app: {str(e)}", app_id=app_id)

    async def disable_app(self, app_id: str) -> App:
        """Disable an app."""
        self._validate_id(app_id)
        try:
            response_data = await self._post(f"{self._endpoint}/{app_id}/disable")
            response_data["id"] = app_id
            return App(**response_data)
        except Exception as e:
            raise HomeyAppError(f"Failed to disable app: {str(e)}", app_id=app_id)

    async def restart_app(self, app_id: str) -> App:
        """Restart an app."""
        self._validate_id(app_id)
        try:
            response_data = await self._post(f"{self._endpoint}/{app_id}/restart")
            response_data["id"] = app_id
            return App(**response_data)
        except Exception as e:
            raise HomeyAppError(f"Failed to restart app: {str(e)}", app_id=app_id)

    async def update_app(self, app_id: str, channel: str = "stable") -> App:
        """Update an app to the latest version."""
        self._validate_id(app_id)
        if channel not in ["stable", "test", "beta", "alpha"]:
            raise HomeyValidationError(
                "Invalid channel. Must be one of: stable, test, beta, alpha"
            )

        data = {"channel": channel}
        try:
            response_data = await self._post(
                f"{self._endpoint}/{app_id}/update", data=data
            )
            response_data["id"] = app_id
            return App(**response_data)
        except Exception as e:
            raise HomeyAppError(f"Failed to update app: {str(e)}", app_id=app_id)

    async def get_installed_apps(self) -> List[App]:
        """Get all installed apps."""
        all_apps = await self.get_apps()
        return [app for app in all_apps if app.is_installed()]

    async def get_enabled_apps(self) -> List[App]:
        """Get all enabled apps."""
        all_apps = await self.get_apps()
        return [app for app in all_apps if app.is_enabled()]

    async def get_disabled_apps(self) -> List[App]:
        """Get all disabled apps."""
        all_apps = await self.get_apps()
        return [app for app in all_apps if not app.is_enabled()]

    async def get_running_apps(self) -> List[App]:
        """Get all running apps."""
        all_apps = await self.get_apps()
        return [app for app in all_apps if app.is_running()]

    async def get_crashed_apps(self) -> List[App]:
        """Get all crashed apps."""
        all_apps = await self.get_apps()
        return [app for app in all_apps if app.is_crashed()]

    async def get_apps_by_category(self, category: str) -> List[App]:
        """Get all apps in a specific category."""
        if not category:
            raise HomeyValidationError("Category cannot be empty")

        all_apps = await self.get_apps()
        return [app for app in all_apps if app.category == category]

    async def search_apps(self, query: str) -> List[App]:
        """Search apps by name."""
        if not query:
            raise HomeyValidationError("Search query cannot be empty")

        all_apps = await self.get_apps()
        query_lower = query.lower()
        return [app for app in all_apps if app.name and query_lower in app.name.lower()]

    async def get_app_settings(self, app_id: str) -> Dict[str, Any]:
        """Get app settings."""
        self._validate_id(app_id)
        try:
            response_data = await self._get(f"{self._endpoint}/{app_id}/settings")
            return response_data if isinstance(response_data, dict) else {}
        except Exception as e:
            raise HomeyAppError(f"Failed to get app settings: {str(e)}", app_id=app_id)

    async def set_app_settings(self, app_id: str, settings: Dict[str, Any]) -> bool:
        """Set app settings."""
        self._validate_id(app_id)
        if not settings:
            raise HomeyValidationError("Settings cannot be empty")

        try:
            await self._put(f"{self._endpoint}/{app_id}/settings", data=settings)
            return True
        except Exception as e:
            raise HomeyAppError(f"Failed to set app settings: {str(e)}", app_id=app_id)

    async def get_app_logs(self, app_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get app logs."""
        self._validate_id(app_id)
        if limit <= 0:
            raise HomeyValidationError("Limit must be greater than 0")

        try:
            params = {"limit": limit}
            response_data = await self._get(
                f"{self._endpoint}/{app_id}/logs", params=params
            )
            return response_data if isinstance(response_data, list) else []
        except Exception as e:
            raise HomeyAppError(f"Failed to get app logs: {str(e)}", app_id=app_id)

    async def get_app_store_info(self, app_id: str) -> Dict[str, Any]:
        """Get app store information."""
        self._validate_id(app_id)
        try:
            response_data = await self._get(f"{self._endpoint}/{app_id}/store")
            return response_data if isinstance(response_data, dict) else {}
        except Exception as e:
            raise HomeyAppError(
                f"Failed to get app store info: {str(e)}", app_id=app_id
            )

    async def get_app_permissions(self, app_id: str) -> List[str]:
        """Get app permissions."""
        app = await self.get_app(app_id)
        return app.get_permissions()

    async def has_permission(self, app_id: str, permission: str) -> bool:
        """Check if an app has a specific permission."""
        app = await self.get_app(app_id)
        return app.has_permission(permission)

    async def get_app_version(self, app_id: str) -> Optional[str]:
        """Get app version."""
        app = await self.get_app(app_id)
        return app.get_version()

    async def get_app_author(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get app author information."""
        app = await self.get_app(app_id)
        return app.get_author()

    async def get_outdated_apps(self) -> List[App]:
        """Get apps that have updates available."""
        # Note: This would require additional API endpoint to check for updates
        # For now, we'll return an empty list as placeholder
        try:
            response_data = await self._get(f"{self._endpoint}/updates")
            if isinstance(response_data, dict):
                apps = []
                for app_id, app_data in response_data.items():
                    app_data["id"] = app_id
                    apps.append(App(**app_data))
                return apps
            return []
        except Exception:
            # If the endpoint doesn't exist, return empty list
            return []

    async def update_all_apps(self) -> List[App]:
        """Update all apps that have updates available."""
        updated_apps = []
        outdated_apps = await self.get_outdated_apps()

        for app in outdated_apps:
            if app.id:
                try:
                    updated_app = await self.update_app(app.id)
                    updated_apps.append(updated_app)
                except Exception:
                    # Continue with other apps if one fails
                    continue

        return updated_apps

    async def get_app_categories(self) -> List[str]:
        """Get all available app categories."""
        all_apps = await self.get_apps()
        categories = set()
        for app in all_apps:
            if app.category:
                categories.add(app.category)
        return sorted(list(categories))

    async def get_apps_by_origin(self, origin: str) -> List[App]:
        """Get apps by origin (e.g., 'app-store', 'development')."""
        if not origin:
            raise HomeyValidationError("Origin cannot be empty")

        all_apps = await self.get_apps()
        return [app for app in all_apps if app.origin == origin]

    async def get_system_apps(self) -> List[App]:
        """Get system apps."""
        return await self.get_apps_by_origin("system")

    async def get_store_apps(self) -> List[App]:
        """Get apps from the app store."""
        return await self.get_apps_by_origin("app-store")

    async def get_development_apps(self) -> List[App]:
        """Get development apps."""
        return await self.get_apps_by_origin("development")
