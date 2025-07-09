"""Flow manager for the Homey API."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..exceptions import HomeyFlowError, HomeyValidationError
from ..models.flow import AdvancedFlow, Flow
from .base import BaseManager

if TYPE_CHECKING:
    from ..client import HomeyClient


class FlowManager(BaseManager):
    """Manager for Homey flows."""

    def __init__(self, client: "HomeyClient") -> None:
        """Initialize the flow manager."""
        super().__init__(client)
        self._endpoint = "/manager/flow/flow"
        self._advanced_endpoint = "/manager/flow/advancedflow"

    async def get_flows(self) -> List[Flow]:
        """Get all flows."""
        try:
            response_data = await self._get(self._endpoint)
            # Flows are returned as a dictionary with flow IDs as keys
            if isinstance(response_data, dict):
                flows = []
                for flow_id, flow_data in response_data.items():
                    flow_data["id"] = flow_id
                    flows.append(Flow(**flow_data))
                return flows
            return []
        except Exception as e:
            raise HomeyFlowError(f"Failed to get flows: {str(e)}")

    async def get_flow(self, flow_id: str) -> Flow:
        """Get a specific flow by ID."""
        self._validate_id(flow_id)
        try:
            response_data = await self._get(f"{self._endpoint}/{flow_id}")
            response_data["id"] = flow_id
            return Flow(**response_data)
        except Exception as e:
            raise HomeyFlowError(f"Failed to get flow: {str(e)}", flow_id=flow_id)

    async def create_flow(self, name: str, **kwargs: Any) -> Flow:
        """Create a new flow."""
        if not name or not name.strip():
            raise HomeyValidationError("Flow name cannot be empty")

        data = {"name": name.strip()}

        # Add optional parameters
        if "enabled" in kwargs:
            data["enabled"] = kwargs["enabled"]
        if "trigger" in kwargs:
            data["trigger"] = kwargs["trigger"]
        if "conditions" in kwargs:
            data["conditions"] = kwargs["conditions"]
        if "actions" in kwargs:
            data["actions"] = kwargs["actions"]
        if "folder" in kwargs:
            data["folder"] = kwargs["folder"]

        try:
            response_data = await self._post(self._endpoint, data=data)
            if "id" in response_data:
                flow_id = response_data["id"]
                response_data["id"] = flow_id
                return Flow(**response_data)
            else:
                # If no ID in response, fetch the created flow
                return await self.get_flow(response_data.get("result", {}).get("id"))
        except Exception as e:
            raise HomeyFlowError(f"Failed to create flow: {str(e)}")

    async def update_flow(self, flow_id: str, **kwargs: Any) -> Flow:
        """Update an existing flow."""
        self._validate_id(flow_id)

        data = {}
        allowed_fields = [
            "name",
            "enabled",
            "trigger",
            "conditions",
            "actions",
            "folder",
        ]

        for field in allowed_fields:
            if field in kwargs:
                if field == "name" and kwargs[field] is not None:
                    if not kwargs[field].strip():
                        raise HomeyValidationError("Flow name cannot be empty")
                    data[field] = kwargs[field].strip()
                else:
                    data[field] = kwargs[field]

        if not data:
            raise HomeyValidationError("At least one field must be provided for update")

        try:
            response_data = await self._put(f"{self._endpoint}/{flow_id}", data=data)
            response_data["id"] = flow_id
            return Flow(**response_data)
        except Exception as e:
            raise HomeyFlowError(f"Failed to update flow: {str(e)}", flow_id=flow_id)

    async def delete_flow(self, flow_id: str) -> bool:
        """Delete a flow."""
        self._validate_id(flow_id)
        try:
            await self._delete(f"{self._endpoint}/{flow_id}")
            return True
        except Exception as e:
            raise HomeyFlowError(f"Failed to delete flow: {str(e)}", flow_id=flow_id)

    async def enable_flow(self, flow_id: str) -> Flow:
        """Enable a flow."""
        return await self.update_flow(flow_id, enabled=True)

    async def disable_flow(self, flow_id: str) -> Flow:
        """Disable a flow."""
        return await self.update_flow(flow_id, enabled=False)

    async def trigger_flow(
        self, flow_id: str, tokens: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Trigger a flow manually."""
        self._validate_id(flow_id)

        data = {}
        if tokens:
            data["tokens"] = tokens

        try:
            await self._post(f"{self._endpoint}/{flow_id}/trigger", data=data)
            return True
        except Exception as e:
            raise HomeyFlowError(f"Failed to trigger flow: {str(e)}", flow_id=flow_id)

    async def get_enabled_flows(self) -> List[Flow]:
        """Get all enabled flows."""
        all_flows = await self.get_flows()
        return [flow for flow in all_flows if flow.is_enabled()]

    async def get_disabled_flows(self) -> List[Flow]:
        """Get all disabled flows."""
        all_flows = await self.get_flows()
        return [flow for flow in all_flows if not flow.is_enabled()]

    async def get_broken_flows(self) -> List[Flow]:
        """Get all broken flows."""
        all_flows = await self.get_flows()
        return [flow for flow in all_flows if flow.is_broken()]

    async def search_flows(self, query: str) -> List[Flow]:
        """Search flows by name."""
        if not query:
            raise HomeyValidationError("Search query cannot be empty")

        all_flows = await self.get_flows()
        query_lower = query.lower()
        return [
            flow for flow in all_flows if flow.name and query_lower in flow.name.lower()
        ]

    async def get_flows_by_folder(self, folder_id: str) -> List[Flow]:
        """Get all flows in a specific folder."""
        self._validate_id(folder_id)
        all_flows = await self.get_flows()
        return [flow for flow in all_flows if flow.folder == folder_id]

    async def get_flows_without_folder(self) -> List[Flow]:
        """Get all flows that are not in any folder."""
        all_flows = await self.get_flows()
        return [flow for flow in all_flows if not flow.folder]

    async def get_flow_execution_stats(self, flow_id: str) -> Dict[str, Any]:
        """Get execution statistics for a flow."""
        self._validate_id(flow_id)
        try:
            response_data = await self._get(f"{self._endpoint}/{flow_id}/stats")
            return response_data if isinstance(response_data, dict) else {}
        except Exception as e:
            raise HomeyFlowError(f"Failed to get flow stats: {str(e)}", flow_id=flow_id)

    async def get_flow_logs(
        self, flow_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get execution logs for a flow."""
        self._validate_id(flow_id)
        if limit <= 0:
            raise HomeyValidationError("Limit must be greater than 0")

        try:
            params = {"limit": limit}
            response_data = await self._get(
                f"{self._endpoint}/{flow_id}/logs", params=params
            )
            return response_data if isinstance(response_data, list) else []
        except Exception as e:
            raise HomeyFlowError(f"Failed to get flow logs: {str(e)}", flow_id=flow_id)

    async def duplicate_flow(
        self, flow_id: str, new_name: Optional[str] = None
    ) -> Flow:
        """Duplicate an existing flow."""
        self._validate_id(flow_id)

        # Get the original flow
        original_flow = await self.get_flow(flow_id)

        # Prepare data for the new flow
        data = original_flow.to_dict()
        data.pop("id", None)  # Remove ID so a new one is generated
        data.pop("created_at", None)
        data.pop("updated_at", None)
        data.pop("lastExecuted", None)
        data.pop("executionCount", None)

        # Set new name
        if new_name:
            data["name"] = new_name.strip()
        else:
            data["name"] = f"{original_flow.name} (Copy)"

        # Disable the duplicate by default
        data["enabled"] = False

        try:
            response_data = await self._post(self._endpoint, data=data)
            if "id" in response_data:
                flow_id = response_data["id"]
                response_data["id"] = flow_id
                return Flow(**response_data)
            else:
                return await self.get_flow(response_data.get("result", {}).get("id"))
        except Exception as e:
            raise HomeyFlowError(f"Failed to duplicate flow: {str(e)}", flow_id=flow_id)

    async def export_flow(self, flow_id: str) -> Dict[str, Any]:
        """Export a flow as JSON."""
        self._validate_id(flow_id)
        try:
            response_data = await self._get(f"{self._endpoint}/{flow_id}/export")
            return response_data if isinstance(response_data, dict) else {}
        except Exception as e:
            raise HomeyFlowError(f"Failed to export flow: {str(e)}", flow_id=flow_id)

    async def import_flow(self, flow_data: Dict[str, Any]) -> Flow:
        """Import a flow from JSON data."""
        if not flow_data:
            raise HomeyValidationError("Flow data cannot be empty")

        if "name" not in flow_data:
            raise HomeyValidationError("Flow data must contain a name")

        try:
            response_data = await self._post(f"{self._endpoint}/import", data=flow_data)
            if "id" in response_data:
                flow_id = response_data["id"]
                response_data["id"] = flow_id
                return Flow(**response_data)
            else:
                return await self.get_flow(response_data.get("result", {}).get("id"))
        except Exception as e:
            raise HomeyFlowError(f"Failed to import flow: {str(e)}")

    async def get_flow_folders(self) -> List[Dict[str, Any]]:
        """Get all flow folders."""
        try:
            response_data = await self._get(f"{self._endpoint}/folders")
            return response_data if isinstance(response_data, list) else []
        except Exception as e:
            raise HomeyFlowError(f"Failed to get flow folders: {str(e)}")

    async def create_flow_folder(self, name: str) -> Dict[str, Any]:
        """Create a new flow folder."""
        if not name or not name.strip():
            raise HomeyValidationError("Folder name cannot be empty")

        data = {"name": name.strip()}
        try:
            response_data = await self._post(f"{self._endpoint}/folders", data=data)
            return response_data if isinstance(response_data, dict) else {}
        except Exception as e:
            raise HomeyFlowError(f"Failed to create flow folder: {str(e)}")

    async def move_flow_to_folder(self, flow_id: str, folder_id: Optional[str]) -> Flow:
        """Move a flow to a folder (or remove from folder if folder_id is None)."""
        return await self.update_flow(flow_id, folder=folder_id)

    # Advanced Flow Methods
    async def get_advanced_flows(self) -> List[AdvancedFlow]:
        """Get all advanced flow objects."""
        try:
            response_data = await self._get(self._advanced_endpoint)
            # Advanced flows are returned as a dictionary with flow IDs as keys
            if isinstance(response_data, dict):
                flows = []
                for flow_id, flow_data in response_data.items():
                    flow_data["id"] = flow_id
                    flows.append(AdvancedFlow(**flow_data))
                return flows
            return []
        except Exception as e:
            raise HomeyFlowError(f"Failed to get advanced flow objects: {str(e)}")

    async def get_advanced_flow(self, flow_id: str) -> AdvancedFlow:
        """Get a specific advanced flow by ID."""
        self._validate_id(flow_id)
        try:
            response_data = await self._get(f"{self._advanced_endpoint}/{flow_id}")
            response_data["id"] = flow_id
            return AdvancedFlow(**response_data)
        except Exception as e:
            raise HomeyFlowError(
                f"Failed to get advanced flow: {str(e)}", flow_id=flow_id
            )

    async def create_advanced_flow(self, name: str, **kwargs: Any) -> AdvancedFlow:
        """Create a new advanced flow."""
        if not name or not name.strip():
            raise HomeyValidationError("Advanced flow name cannot be empty")

        data = {"name": name.strip()}

        # Add optional parameters
        if "enabled" in kwargs:
            data["enabled"] = kwargs["enabled"]
        if "folder" in kwargs:
            data["folder"] = kwargs["folder"]
        if "cards" in kwargs:
            data["cards"] = kwargs["cards"]

        try:
            response_data = await self._post(self._advanced_endpoint, data=data)
            if "id" in response_data:
                flow_id = response_data["id"]
                response_data["id"] = flow_id
                return AdvancedFlow(**response_data)
            else:
                # If no ID in response, fetch the created flow
                return await self.get_advanced_flow(
                    response_data.get("result", {}).get("id")
                )
        except Exception as e:
            raise HomeyFlowError(f"Failed to create advanced flow: {str(e)}")

    async def update_advanced_flow(self, flow_id: str, **kwargs: Any) -> AdvancedFlow:
        """Update an existing advanced flow."""
        self._validate_id(flow_id)

        data = {}
        allowed_fields = [
            "name",
            "enabled",
            "folder",
            "cards",
        ]

        for field in allowed_fields:
            if field in kwargs:
                if field == "name" and kwargs[field] is not None:
                    if not kwargs[field].strip():
                        raise HomeyValidationError("Advanced flow name cannot be empty")
                    data[field] = kwargs[field].strip()
                else:
                    data[field] = kwargs[field]

        if not data:
            raise HomeyValidationError("At least one field must be provided for update")

        try:
            response_data = await self._put(
                f"{self._advanced_endpoint}/{flow_id}", data=data
            )
            response_data["id"] = flow_id
            return AdvancedFlow(**response_data)
        except Exception as e:
            raise HomeyFlowError(
                f"Failed to update advanced flow: {str(e)}", flow_id=flow_id
            )

    async def delete_advanced_flow(self, flow_id: str) -> bool:
        """Delete an advanced flow."""
        self._validate_id(flow_id)
        try:
            await self._delete(f"{self._advanced_endpoint}/{flow_id}")
            return True
        except Exception as e:
            raise HomeyFlowError(
                f"Failed to delete advanced flow: {str(e)}", flow_id=flow_id
            )

    async def enable_advanced_flow(self, flow_id: str) -> AdvancedFlow:
        """Enable an advanced flow."""
        return await self.update_advanced_flow(flow_id, enabled=True)

    async def disable_advanced_flow(self, flow_id: str) -> AdvancedFlow:
        """Disable an advanced flow."""
        return await self.update_advanced_flow(flow_id, enabled=False)

    async def trigger_advanced_flow(
        self, flow_id: str, tokens: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Trigger an advanced flow manually."""
        self._validate_id(flow_id)

        data = {}
        if tokens:
            data["tokens"] = tokens

        try:
            await self._post(f"{self._advanced_endpoint}/{flow_id}/trigger", data=data)
            return True
        except Exception as e:
            raise HomeyFlowError(
                f"Failed to trigger advanced flow: {str(e)}", flow_id=flow_id
            )

    async def get_enabled_advanced_flows(self) -> List[AdvancedFlow]:
        """Get all enabled advanced flows."""
        all_flows = await self.get_advanced_flows()
        return [flow for flow in all_flows if flow.is_enabled()]

    async def get_disabled_advanced_flows(self) -> List[AdvancedFlow]:
        """Get all disabled advanced flows."""
        all_flows = await self.get_advanced_flows()
        return [flow for flow in all_flows if not flow.is_enabled()]

    async def get_broken_advanced_flows(self) -> List[AdvancedFlow]:
        """Get all broken advanced flows."""
        all_flows = await self.get_advanced_flows()
        return [flow for flow in all_flows if flow.is_broken()]

    async def search_advanced_flows(self, query: str) -> List[AdvancedFlow]:
        """Search advanced flows by name."""
        if not query:
            raise HomeyValidationError("Search query cannot be empty")

        all_flows = await self.get_advanced_flows()
        query_lower = query.lower()
        return [
            flow for flow in all_flows if flow.name and query_lower in flow.name.lower()
        ]

    async def get_advanced_flows_by_folder(self, folder_id: str) -> List[AdvancedFlow]:
        """Get all advanced flows in a specific folder."""
        self._validate_id(folder_id)
        all_flows = await self.get_advanced_flows()
        return [flow for flow in all_flows if flow.folder == folder_id]

    async def get_advanced_flows_without_folder(self) -> List[AdvancedFlow]:
        """Get all advanced flows that are not in any folder."""
        all_flows = await self.get_advanced_flows()
        return [flow for flow in all_flows if not flow.folder]

    async def export_advanced_flow(self, flow_id: str) -> Dict[str, Any]:
        """Export an advanced flow as JSON."""
        self._validate_id(flow_id)
        try:
            response_data = await self._get(
                f"{self._advanced_endpoint}/{flow_id}/export"
            )
            return response_data if isinstance(response_data, dict) else {}
        except Exception as e:
            raise HomeyFlowError(
                f"Failed to export advanced flow: {str(e)}", flow_id=flow_id
            )

    async def import_advanced_flow(self, flow_data: Dict[str, Any]) -> AdvancedFlow:
        """Import an advanced flow from JSON data."""
        if not flow_data:
            raise HomeyValidationError("Advanced flow data cannot be empty")

        if "name" not in flow_data:
            raise HomeyValidationError("Advanced flow data must contain a name")

        try:
            response_data = await self._post(
                f"{self._advanced_endpoint}/import", data=flow_data
            )
            if "id" in response_data:
                flow_id = response_data["id"]
                response_data["id"] = flow_id
                return AdvancedFlow(**response_data)
            else:
                return await self.get_advanced_flow(
                    response_data.get("result", {}).get("id")
                )
        except Exception as e:
            raise HomeyFlowError(f"Failed to import advanced flow: {str(e)}")

    async def move_advanced_flow_to_folder(
        self, flow_id: str, folder_id: Optional[str]
    ) -> AdvancedFlow:
        """Move an advanced flow to a folder (or remove from folder if folder_id is None)."""
        return await self.update_advanced_flow(flow_id, folder=folder_id)

    async def get_advanced_flows_with_inline_scripts(self) -> List[AdvancedFlow]:
        """Get all advanced flows that contain inline HomeyScript blocks."""
        all_flows = await self.get_advanced_flows()
        return [flow for flow in all_flows if flow.has_inline_scripts()]
