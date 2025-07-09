"""
Python client library for Homey v3 Local API.

This library provides a high-level, pythonic interface for interacting with
Homey's local API, allowing you to control devices, manage zones, work with
flows, and more.

Basic Usage:
    ```python
    import asyncio
    from homey import HomeyClient

    async def main():
        # Create and authenticate client
        client = await HomeyClient.create(
            base_url="http://192.168.1.100",
            token="your-personal-access-token"
        )

        # Get all devices
        devices = await client.devices.get_devices()
        print(f"Found {len(devices)} devices")

        # Turn on a device
        await client.devices.turn_on("device-id")

        # Get all zones
        zones = await client.zones.get_zones()
        print(f"Found {len(zones)} zones")

        # Get all flows
        flows = await client.flows.get_flows()
        print(f"Found {len(flows)} flows")

        # Clean up
        await client.disconnect()

    asyncio.run(main())
    ```

Real-time Events (Optional):
    ```python
    import asyncio
    from homey import HomeyClient

    async def main():
        client = await HomeyClient.create(
            base_url="http://192.168.1.100",
            token="your-personal-access-token"
        )

        async with client:
            # WebSocket connection is completely optional
            await client.connect_websocket(auto_reconnect=True)

            # Register event handlers
            async def on_device_event(event_data):
                print(f"Device event: {event_data}")

            client.on("device", on_device_event)

            # Listen for events
            await asyncio.sleep(30)

            # Disconnect WebSocket when done
            await client.disconnect_websocket()

    asyncio.run(main())
    ```

Context Manager Usage:
    ```python
    import asyncio
    from homey import HomeyClient

    async def main():
        async with HomeyClient.create(
            base_url="http://192.168.1.100",
            token="your-personal-access-token"
        ) as client:
            # Work with the client - WebSocket is NOT automatically connected
            devices = await client.devices.get_devices()

            # Optionally connect WebSocket for real-time events
            # await client.connect_websocket()

            # Connection automatically closed when exiting context

    asyncio.run(main())
    ```
"""

from .auth import HomeyAuth
from .client import HomeyClient
from .exceptions import (
    HomeyAPIError,
    HomeyAppError,
    HomeyAuthenticationError,
    HomeyConnectionError,
    HomeyDeviceError,
    HomeyError,
    HomeyFlowError,
    HomeyNotFoundError,
    HomeyPermissionError,
    HomeyTimeoutError,
    HomeyValidationError,
    HomeyWebSocketError,
    HomeyZoneError,
)
from .managers import (
    AppManager,
    BaseManager,
    DeviceManager,
    FlowManager,
    ZoneManager,
)
from .models import (
    AdvancedFlow,
    AdvancedFlowBlock,
    App,
    BaseModel,
    Device,
    DeviceCapability,
    Flow,
    FlowCard,
    Zone,
)

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__license__ = "MIT"
__description__ = "Python client library for Homey v3 Local API"

__all__ = [
    # Main client
    "HomeyClient",
    "HomeyAuth",
    # Exceptions
    "HomeyError",
    "HomeyConnectionError",
    "HomeyAuthenticationError",
    "HomeyNotFoundError",
    "HomeyPermissionError",
    "HomeyAPIError",
    "HomeyTimeoutError",
    "HomeyValidationError",
    "HomeyDeviceError",
    "HomeyFlowError",
    "HomeyWebSocketError",
    "HomeyZoneError",
    "HomeyAppError",
    # Models
    "BaseModel",
    "Device",
    "DeviceCapability",
    "Zone",
    "Flow",
    "FlowCard",
    "AdvancedFlow",
    "AdvancedFlowBlock",
    "App",
    # Managers
    "BaseManager",
    "DeviceManager",
    "ZoneManager",
    "FlowManager",
    "AppManager",
]


# Module-level convenience functions
async def create_client(
    base_url: str,
    token: str,
    *,
    timeout: float = 30.0,
    verify_ssl: bool = True,
    debug: bool = False,
) -> HomeyClient:
    """
    Create and authenticate a Homey client.

    This is a convenience function that creates a HomeyClient instance
    and automatically authenticates it.

    Args:
        base_url: The base URL of your Homey (e.g., "http://192.168.1.100")
        token: Personal Access Token for authentication
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates
        debug: Enable debug logging

    Returns:
        Authenticated HomeyClient instance

    Raises:
        HomeyAuthenticationError: If authentication fails
        HomeyConnectionError: If connection fails

    Example:
        ```python
        import asyncio
        from homey import create_client

        async def main():
            client = await create_client(
                base_url="http://192.168.1.100",
                token="your-token"
            )

            devices = await client.devices.get_devices()
            print(f"Found {len(devices)} devices")

            await client.disconnect()

        asyncio.run(main())
        ```
    """
    return await HomeyClient.create(
        base_url=base_url,
        token=token,
        timeout=timeout,
        verify_ssl=verify_ssl,
        debug=debug,
    )


def get_token_url(homey_url: str) -> str:
    """
    Get the URL for creating a Personal Access Token.

    Args:
        homey_url: The base URL of your Homey

    Returns:
        URL for creating a Personal Access Token

    Example:
        ```python
        from homey import get_token_url

        url = get_token_url("http://192.168.1.100")
        print(f"Create token at: {url}")
        ```
    """
    return HomeyAuth.create_personal_access_token_url(homey_url)
