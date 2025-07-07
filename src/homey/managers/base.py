"""Base manager class for Homey API managers."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar
from urllib.parse import urljoin

import httpx

from ..exceptions import (
    HomeyAPIError,
    HomeyConnectionError,
    HomeyNotFoundError,
    HomeyPermissionError,
    HomeyTimeoutError,
)
from ..models.base import BaseModel

if TYPE_CHECKING:
    pass

T = TypeVar("T", bound=BaseModel)


class BaseManager:
    """Base class for all Homey API managers."""

    def __init__(self, client) -> None:
        """Initialize the manager with a client reference."""
        self.client = client
        self._base_url = f"{client.base_url}/api/manager"

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the Homey API."""
        url = urljoin(self._base_url, endpoint.lstrip("/"))

        headers = {
            "Authorization": f"Bearer {self.client.token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                )

                # Handle different response status codes
                if response.status_code == 200:
                    result = response.json()
                    return result if isinstance(result, dict) else {}
                elif response.status_code == 404:
                    raise HomeyNotFoundError(f"Resource not found: {endpoint}")
                elif response.status_code == 401:
                    raise HomeyPermissionError("Authentication failed")
                elif response.status_code == 403:
                    raise HomeyPermissionError("Insufficient permissions")
                elif response.status_code >= 400:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except Exception:
                        pass

                    raise HomeyAPIError(
                        f"API request failed: {response.status_code}",
                        status_code=response.status_code,
                        details=error_data,
                    )
                else:
                    # Fallback for other status codes
                    return {}

        except httpx.TimeoutException:
            raise HomeyTimeoutError(f"Request timed out after {timeout} seconds")
        except httpx.ConnectError:
            raise HomeyConnectionError("Failed to connect to Homey")
        except httpx.RequestError as e:
            raise HomeyConnectionError(f"Request failed: {str(e)}")

    async def _get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """Make a GET request."""
        return await self._request("GET", endpoint, params=params, timeout=timeout)

    async def _post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return await self._request(
            "POST", endpoint, data=data, params=params, timeout=timeout
        )

    async def _put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return await self._request(
            "PUT", endpoint, data=data, params=params, timeout=timeout
        )

    async def _delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """Make a DELETE request."""
        return await self._request("DELETE", endpoint, params=params, timeout=timeout)

    def _parse_response_list(
        self,
        response_data: Dict[str, Any],
        model_class: Type[T],
    ) -> List[T]:
        """Parse API response into list of model instances."""
        if "result" in response_data:
            items = response_data["result"]
        else:
            items = response_data

        if isinstance(items, dict):
            # Handle dictionary responses (e.g., devices by ID)
            return [model_class(**item) for item in items.values()]
        elif isinstance(items, list):
            # Handle list responses
            return [model_class(**item) for item in items]
        else:
            return []

    def _parse_response_single(
        self,
        response_data: Dict[str, Any],
        model_class: Type[T],
    ) -> T:
        """Parse API response into single model instance."""
        if "result" in response_data:
            return model_class(**response_data["result"])
        else:
            return model_class(**response_data)

    async def _get_all(
        self,
        endpoint: str,
        model_class: Type[T],
        params: Optional[Dict[str, Any]] = None,
    ) -> List[T]:
        """Get all items from an endpoint."""
        response_data = await self._get(endpoint, params=params)
        return self._parse_response_list(response_data, model_class)

    async def _get_by_id(
        self,
        endpoint: str,
        item_id: str,
        model_class: Type[T],
    ) -> T:
        """Get a single item by ID."""
        full_endpoint = f"{endpoint}/{item_id}"
        response_data = await self._get(full_endpoint)
        return self._parse_response_single(response_data, model_class)

    async def _create(
        self,
        endpoint: str,
        data: Dict[str, Any],
        model_class: Type[T],
    ) -> T:
        """Create a new item."""
        response_data = await self._post(endpoint, data=data)
        return self._parse_response_single(response_data, model_class)

    async def _update(
        self,
        endpoint: str,
        item_id: str,
        data: Dict[str, Any],
        model_class: Type[T],
    ) -> T:
        """Update an existing item."""
        full_endpoint = f"{endpoint}/{item_id}"
        response_data = await self._put(full_endpoint, data=data)
        return self._parse_response_single(response_data, model_class)

    async def _delete_by_id(
        self,
        endpoint: str,
        item_id: str,
    ) -> bool:
        """Delete an item by ID."""
        full_endpoint = f"{endpoint}/{item_id}"
        await self._delete(full_endpoint)
        return True

    def _validate_id(self, item_id: str) -> None:
        """Validate that an ID is provided and not empty."""
        if not item_id or not item_id.strip():
            raise ValueError("Item ID cannot be empty")
