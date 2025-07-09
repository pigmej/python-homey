"""Main client class for the Homey API.

This client provides access to Homey's local API for managing devices, zones, flows,
and apps. WebSocket functionality for real-time events is optional and must be
explicitly enabled by calling connect_websocket().
"""

import asyncio
import logging
from typing import Any, Callable, Dict, Optional

import websockets

from .auth import HomeyAuth
from .exceptions import (
    HomeyValidationError,
    HomeyWebSocketError,
)
from .managers import (
    AppManager,
    DeviceManager,
    FlowManager,
    SystemManager,
    ZoneManager,
)

logger = logging.getLogger(__name__)


class HomeyClient:
    """
    Main client for interacting with the Homey Local API.

    This client provides access to all Homey API functionality including:
    - Device management and control
    - Zone management
    - Flow management
    - App management
    - Optional real-time events via WebSocket (requires explicit connection)

    WebSocket functionality is completely optional and must be explicitly enabled
    by calling connect_websocket() method.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        debug: bool = False,
    ) -> None:
        """
        Initialize the Homey client.

        Args:
            base_url: The base URL of your Homey (e.g., "http://192.168.1.100")
            token: Personal Access Token for authentication
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            debug: Enable debug logging
        """
        self.base_url = self._normalize_url(base_url)
        self.token = token
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Set up logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)

        # Validate inputs
        if not HomeyAuth.validate_url_format(self.base_url):
            raise HomeyValidationError(f"Invalid base URL: {base_url}")

        if not HomeyAuth.validate_token_format(token):
            raise HomeyValidationError("Invalid token format")

        # Initialize authentication
        self._auth = HomeyAuth(self.base_url, token)

        # Initialize managers
        self.devices = DeviceManager(self)
        self.zones = ZoneManager(self)
        self.flows = FlowManager(self)
        self.apps = AppManager(self)
        self.system = SystemManager(self)

        # WebSocket connection (optional)
        self._websocket: Optional[Any] = None
        self._websocket_task: Optional[asyncio.Task] = None
        self._event_handlers: Dict[str, Callable] = {}
        self._websocket_connected = False
        self._auto_reconnect = False

        # Connection state
        self._connected = False
        self._authenticated = False

    @classmethod
    async def create(
        cls,
        base_url: str,
        token: str,
        *,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        debug: bool = False,
    ) -> "HomeyClient":
        """
        Create and authenticate a Homey client.

        This creates a client that can interact with the Homey API for managing
        devices, zones, flows, and apps. WebSocket functionality for real-time
        events is NOT automatically enabled - use connect_websocket() to enable it.

        Args:
            base_url: The base URL of your Homey
            token: Personal Access Token
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            debug: Enable debug logging

        Returns:
            Authenticated HomeyClient instance

        Raises:
            HomeyAuthenticationError: If authentication fails
            HomeyConnectionError: If connection fails
        """
        client = cls(
            base_url=base_url,
            token=token,
            timeout=timeout,
            verify_ssl=verify_ssl,
            debug=debug,
        )

        await client.authenticate()
        client._connected = True
        return client

    async def authenticate(self) -> bool:
        """
        Authenticate with the Homey API.

        Returns:
            True if authentication successful

        Raises:
            HomeyAuthenticationError: If authentication fails
        """
        try:
            success = await self._auth.authenticate()
            if success:
                self._authenticated = True
                logger.info("Successfully authenticated with Homey")
                return True
            return False
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise

    async def connect(self) -> bool:
        """
        Connect to Homey and start WebSocket connection.

        Returns:
            True if connection successful
        """
        if not self._authenticated:
            await self.authenticate()

        # Connection is mainly about authentication
        self._connected = True
        logger.info("Successfully connected to Homey")
        return True

    async def disconnect(self) -> None:
        """Disconnect from Homey and close WebSocket connection if active."""
        self._connected = False

        # Disconnect WebSocket if connected
        if self._websocket_connected:
            await self.disconnect_websocket()

        logger.info("Disconnected from Homey")

    async def __aenter__(self) -> "HomeyClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()

    def is_connected(self) -> bool:
        """Check if the client is connected."""
        return self._connected and self._authenticated

    def is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        return self._authenticated

    async def get_system_info(self) -> Dict[str, Any]:
        """Get system information from Homey."""
        if not self._authenticated:
            await self.authenticate()

        session_info = self._auth.get_session_info()
        return session_info or {}

    async def ping(self) -> bool:
        """Ping Homey to test connection."""
        try:
            await self.get_system_info()
            return True
        except Exception:
            return False

    def on(self, event: str, handler: Callable) -> None:
        """
        Register an event handler for WebSocket events.

        Note: WebSocket must be connected using connect_websocket() to receive events.

        Args:
            event: Event name to listen for
            handler: Callable to handle the event
        """
        self._event_handlers[event] = handler

    def off(self, event: str) -> None:
        """
        Remove an event handler for WebSocket events.

        Args:
            event: Event name to remove handler for
        """
        self._event_handlers.pop(event, None)

    async def connect_websocket(self, *, auto_reconnect: bool = False) -> None:
        """
        Connect to WebSocket for real-time events.

        This method explicitly enables WebSocket functionality for receiving
        real-time events from Homey such as device state changes, zone activity,
        flow executions, and app events.

        Args:
            auto_reconnect: Whether to automatically reconnect on disconnect

        Raises:
            HomeyWebSocketError: If WebSocket connection fails

        Example:
            ```python
            # Connect to WebSocket for real-time events
            await client.connect_websocket(auto_reconnect=True)

            # Register event handlers
            client.on("device", my_device_handler)
            client.on("zone", my_zone_handler)

            # Listen for events...
            await asyncio.sleep(30)

            # Disconnect when done
            await client.disconnect_websocket()
            ```
        """
        if self._websocket_connected:
            logger.info("WebSocket already connected")
            return

        self._auto_reconnect = auto_reconnect
        await self._connect_websocket()

    async def disconnect_websocket(self) -> None:
        """
        Disconnect from WebSocket.

        This closes the WebSocket connection and stops receiving real-time events.
        Event handlers are kept registered and will work again if WebSocket is
        reconnected.
        """
        if not self._websocket_connected:
            logger.info("WebSocket already disconnected")
            return

        self._websocket_connected = False
        self._auto_reconnect = False

        if self._websocket_task and not self._websocket_task.done():
            self._websocket_task.cancel()
            try:
                await self._websocket_task
            except (asyncio.CancelledError, TypeError):
                pass

        if self._websocket:
            await self._websocket.close()
            self._websocket = None

        logger.info("WebSocket disconnected")

    def is_websocket_connected(self) -> bool:
        """
        Check if WebSocket is connected.

        Returns:
            True if WebSocket is connected and can receive real-time events
        """
        return self._websocket_connected

    async def _connect_websocket(self) -> None:
        """Connect to the WebSocket for real-time events."""
        # Note: Homey uses Socket.IO, not raw WebSockets
        # This is a placeholder implementation that will be improved in future versions
        # For now, we'll try a simple WebSocket connection to common endpoints

        endpoints_to_try = [
            "/socket.io/",
            "/api/socket.io/",
            "/api/manager/socket.io/",
        ]

        for endpoint in endpoints_to_try:
            try:
                # Convert HTTP(S) URL to WebSocket URL
                ws_url = self.base_url.replace("http://", "ws://").replace(
                    "https://", "wss://"
                )
                ws_url = f"{ws_url}{endpoint}"

                headers = self._auth.get_headers()
                self._websocket = await websockets.connect(
                    ws_url,
                    additional_headers=headers,
                    ping_interval=30,
                    ping_timeout=10,
                )

                # Start WebSocket message handler
                self._websocket_task = asyncio.create_task(
                    self._handle_websocket_messages()
                )

                self._websocket_connected = True
                logger.info(f"WebSocket connected to {endpoint}")
                return

            except Exception as e:
                logger.debug(f"Failed to connect to {endpoint}: {e}")
                continue

        # If all endpoints fail, raise an error
        raise HomeyWebSocketError(
            "WebSocket connection failed: No valid endpoint found"
        )

    async def _handle_websocket_messages(self) -> None:
        """Handle incoming WebSocket messages."""
        try:
            if self._websocket:
                async for message in self._websocket:
                    try:
                        # Parse and handle the message
                        await self._process_websocket_message(message)
                    except Exception as e:
                        logger.error(f"Error processing WebSocket message: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.debug("WebSocket connection closed")
            self._websocket_connected = False
            if self._auto_reconnect and self._connected:
                await self._reconnect_websocket()
        except Exception as e:
            logger.debug(f"WebSocket error: {e}")
            self._websocket_connected = False
            if self._auto_reconnect and self._connected:
                await self._reconnect_websocket()

    async def _process_websocket_message(self, message: str) -> None:
        """Process a WebSocket message."""
        try:
            import json

            data = json.loads(message)

            event_type = data.get("type", "unknown")
            event_data = data.get("data", {})

            # Call registered event handlers
            if event_type in self._event_handlers:
                handler = self._event_handlers[event_type]
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    handler(event_data)

            # Handle specific event types
            if event_type == "device":
                await self._handle_device_event(event_data)
            elif event_type == "zone":
                await self._handle_zone_event(event_data)
            elif event_type == "flow":
                await self._handle_flow_event(event_data)
            elif event_type == "app":
                await self._handle_app_event(event_data)

        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")

    async def _handle_device_event(self, event_data: Dict[str, Any]) -> None:
        """Handle device-related events."""
        # Emit device events to registered handlers
        if "device" in self._event_handlers:
            handler = self._event_handlers["device"]
            if asyncio.iscoroutinefunction(handler):
                await handler(event_data)
            else:
                handler(event_data)

    async def _handle_zone_event(self, event_data: Dict[str, Any]) -> None:
        """Handle zone-related events."""
        if "zone" in self._event_handlers:
            handler = self._event_handlers["zone"]
            if asyncio.iscoroutinefunction(handler):
                await handler(event_data)
            else:
                handler(event_data)

    async def _handle_flow_event(self, event_data: Dict[str, Any]) -> None:
        """Handle flow-related events."""
        if "flow" in self._event_handlers:
            handler = self._event_handlers["flow"]
            if asyncio.iscoroutinefunction(handler):
                await handler(event_data)
            else:
                handler(event_data)

    async def _handle_app_event(self, event_data: Dict[str, Any]) -> None:
        """Handle app-related events."""
        if "app" in self._event_handlers:
            handler = self._event_handlers["app"]
            if asyncio.iscoroutinefunction(handler):
                await handler(event_data)
            else:
                handler(event_data)

    async def _reconnect_websocket(self) -> None:
        """Reconnect WebSocket with exponential backoff."""
        max_retries = 3
        base_delay = 5.0

        for attempt in range(max_retries):
            try:
                delay = base_delay * (2**attempt)
                logger.debug(
                    f"Reconnecting WebSocket in {delay} seconds... (attempt {attempt + 1})"
                )
                await asyncio.sleep(delay)

                await self._connect_websocket()
                logger.debug("WebSocket reconnected successfully")
                return

            except Exception as e:
                logger.debug(
                    f"WebSocket reconnection attempt {attempt + 1} failed: {e}"
                )

        logger.debug("Failed to reconnect WebSocket after maximum retries")

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize the base URL."""
        url = url.strip().rstrip("/")
        if not url.startswith(("http://", "https://")):
            url = f"http://{url}"
        return url

    def __repr__(self) -> str:
        """String representation of the client."""
        status = "connected" if self.is_connected() else "disconnected"
        return f"HomeyClient(url={self.base_url}, status={status})"
