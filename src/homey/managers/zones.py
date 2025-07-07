"""Zone manager for the Homey API."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..exceptions import HomeyValidationError, HomeyZoneError
from ..models.zone import Zone
from .base import BaseManager

if TYPE_CHECKING:
    from ..client import HomeyClient


class ZoneManager(BaseManager):
    """Manager for Homey zones."""

    def __init__(self, client: "HomeyClient") -> None:
        """Initialize the zone manager."""
        super().__init__(client)
        self._endpoint = "/manager/zones/zone"

    async def get_zones(self) -> List[Zone]:
        """Get all zones."""
        try:
            response_data = await self._get(self._endpoint)
            # Zones are returned as a dictionary with zone IDs as keys
            if isinstance(response_data, dict):
                zones = []
                for zone_id, zone_data in response_data.items():
                    zone_data["id"] = zone_id
                    zones.append(Zone(**zone_data))
                return zones
            return []
        except Exception as e:
            raise HomeyZoneError(f"Failed to get zones: {str(e)}")

    async def get_zone(self, zone_id: str) -> Zone:
        """Get a specific zone by ID."""
        self._validate_id(zone_id)
        try:
            response_data = await self._get(f"{self._endpoint}/{zone_id}")
            response_data["id"] = zone_id
            return Zone(**response_data)
        except Exception as e:
            raise HomeyZoneError(f"Failed to get zone: {str(e)}", zone_id=zone_id)

    async def create_zone(self, name: str, parent_id: Optional[str] = None) -> Zone:
        """Create a new zone."""
        if not name or not name.strip():
            raise HomeyValidationError("Zone name cannot be empty")

        data = {"name": name.strip()}
        if parent_id:
            data["parent"] = parent_id

        try:
            response_data = await self._post(self._endpoint, data=data)
            if "id" in response_data:
                zone_id = response_data["id"]
                response_data["id"] = zone_id
                return Zone(**response_data)
            else:
                # If no ID in response, fetch the created zone
                return await self.get_zone(response_data.get("result", {}).get("id"))
        except Exception as e:
            raise HomeyZoneError(f"Failed to create zone: {str(e)}")

    async def update_zone(
        self, zone_id: str, name: Optional[str] = None, parent_id: Optional[str] = None
    ) -> Zone:
        """Update an existing zone."""
        self._validate_id(zone_id)

        data = {}
        if name is not None:
            if not name.strip():
                raise HomeyValidationError("Zone name cannot be empty")
            data["name"] = name.strip()

        if parent_id is not None:
            data["parent"] = parent_id

        if not data:
            raise HomeyValidationError("At least one field must be provided for update")

        try:
            response_data = await self._put(f"{self._endpoint}/{zone_id}", data=data)
            response_data["id"] = zone_id
            return Zone(**response_data)
        except Exception as e:
            raise HomeyZoneError(f"Failed to update zone: {str(e)}", zone_id=zone_id)

    async def delete_zone(self, zone_id: str) -> bool:
        """Delete a zone."""
        self._validate_id(zone_id)
        try:
            await self._delete(f"{self._endpoint}/{zone_id}")
            return True
        except Exception as e:
            raise HomeyZoneError(f"Failed to delete zone: {str(e)}", zone_id=zone_id)

    async def get_root_zones(self) -> List[Zone]:
        """Get all root zones (zones without a parent)."""
        all_zones = await self.get_zones()
        return [zone for zone in all_zones if zone.is_root_zone()]

    async def get_child_zones(self, parent_zone_id: str) -> List[Zone]:
        """Get all child zones of a specific parent zone."""
        self._validate_id(parent_zone_id)
        all_zones = await self.get_zones()
        return [zone for zone in all_zones if zone.parent == parent_zone_id]

    async def get_zone_hierarchy(self, zone_id: str) -> List[Zone]:
        """Get the full hierarchy path for a zone (from root to the specified zone)."""
        self._validate_id(zone_id)
        hierarchy = []
        current_zone = await self.get_zone(zone_id)
        hierarchy.append(current_zone)

        while current_zone.parent:
            current_zone = await self.get_zone(current_zone.parent)
            hierarchy.insert(0, current_zone)

        return hierarchy

    async def get_zone_tree(
        self, root_zone_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get a tree structure of zones starting from a root zone."""
        all_zones = await self.get_zones()

        # Create a mapping of zone ID to zone object
        zone_map = {zone.id: zone for zone in all_zones}

        def build_tree(parent_id: Optional[str]) -> List[Dict[str, Any]]:
            """Recursively build the zone tree."""
            children = []
            for zone in all_zones:
                if zone.parent == parent_id:
                    zone_dict = zone.to_dict()
                    zone_dict["children"] = build_tree(zone.id)
                    children.append(zone_dict)
            return children

        if root_zone_id:
            # Build tree from specific root zone
            root_zone = zone_map.get(root_zone_id)
            if not root_zone:
                raise HomeyZoneError(
                    f"Root zone {root_zone_id} not found", zone_id=root_zone_id
                )

            root_dict = root_zone.to_dict()
            root_dict["children"] = build_tree(root_zone_id)
            return [root_dict]
        else:
            # Build tree from all root zones
            return build_tree(None)

    async def search_zones(self, query: str) -> List[Zone]:
        """Search zones by name."""
        if not query:
            raise HomeyValidationError("Search query cannot be empty")

        all_zones = await self.get_zones()
        query_lower = query.lower()
        return [
            zone for zone in all_zones if zone.name and query_lower in zone.name.lower()
        ]

    async def get_active_zones(self) -> List[Zone]:
        """Get all active zones."""
        all_zones = await self.get_zones()
        return [zone for zone in all_zones if zone.is_active()]

    async def get_inactive_zones(self) -> List[Zone]:
        """Get all inactive zones."""
        all_zones = await self.get_zones()
        return [zone for zone in all_zones if not zone.is_active()]

    async def set_zone_active(self, zone_id: str, active: bool) -> Zone:
        """Set a zone's active status."""
        self._validate_id(zone_id)
        try:
            data = {"active": active}
            response_data = await self._put(f"{self._endpoint}/{zone_id}", data=data)
            response_data["id"] = zone_id
            return Zone(**response_data)
        except Exception as e:
            raise HomeyZoneError(
                f"Failed to set zone active status: {str(e)}", zone_id=zone_id
            )

    async def move_zone(self, zone_id: str, new_parent_id: Optional[str]) -> Zone:
        """Move a zone to a new parent."""
        self._validate_id(zone_id)

        # Validate that we're not creating a circular reference
        if new_parent_id:
            hierarchy = await self.get_zone_hierarchy(new_parent_id)
            if any(zone.id == zone_id for zone in hierarchy):
                raise HomeyValidationError("Cannot move zone to its own descendant")

        return await self.update_zone(zone_id, parent_id=new_parent_id)

    async def get_zone_depth(self, zone_id: str) -> int:
        """Get the depth of a zone in the hierarchy (root zones have depth 0)."""
        hierarchy = await self.get_zone_hierarchy(zone_id)
        return len(hierarchy) - 1

    async def get_zone_descendants(self, zone_id: str) -> List[Zone]:
        """Get all descendant zones of a given zone."""
        self._validate_id(zone_id)
        all_zones = await self.get_zones()
        descendants = []

        def collect_descendants(parent_id: str) -> None:
            for zone in all_zones:
                if zone.parent == parent_id:
                    descendants.append(zone)
                    if zone.id:
                        collect_descendants(zone.id)

        collect_descendants(zone_id)
        return descendants
