"""Tests for the HomeyClient class."""

import pytest

from unittest.mock import Mock, AsyncMock, patch
from homey import HomeyClient
from homey.exceptions import (
    HomeyAuthenticationError,
    HomeyConnectionError,
    HomeyValidationError,
)


class TestHomeyClient:
    """Test cases for HomeyClient."""

    def test_init_with_valid_params(self):
        """Test client initialization with valid parameters."""
        client = HomeyClient(
            base_url="http://192.168.1.100",
            token="test-token",
            timeout=30.0,
            verify_ssl=True,
            debug=False,
        )

        assert client.base_url == "http://192.168.1.100"
        assert client.token == "test-token"
        assert client.timeout == 30.0
        assert client.verify_ssl is True
        assert client._connected is False
        assert client._authenticated is False

    def test_init_with_invalid_url(self):
        """Test client initialization with invalid URL."""
        with pytest.raises(HomeyValidationError, match="Invalid base URL"):
            HomeyClient(base_url="", token="test-token")

    def test_init_with_invalid_token(self):
        """Test client initialization with invalid token."""
        with pytest.raises(HomeyValidationError, match="Invalid token format"):
            HomeyClient(base_url="http://192.168.1.100", token="")

    def test_normalize_url(self):
        """Test URL normalization."""
        # Test with http://
        assert (
            HomeyClient._normalize_url("http://192.168.1.100") == "http://192.168.1.100"
        )

        # Test with https://
        assert (
            HomeyClient._normalize_url("https://192.168.1.100")
            == "https://192.168.1.100"
        )

        # Test without protocol
        assert HomeyClient._normalize_url("192.168.1.100") == "http://192.168.1.100"

        # Test with trailing slash
        assert (
            HomeyClient._normalize_url("http://192.168.1.100/")
            == "http://192.168.1.100"
        )

    def test_validate_url(self):
        """Test URL validation."""
        from homey.auth import HomeyAuth

        # Valid URLs
        assert HomeyAuth.validate_url_format("http://192.168.1.100") is True
        assert HomeyAuth.validate_url_format("https://192.168.1.100") is True
        assert HomeyAuth.validate_url_format("http://homey.local") is True

        # Invalid URLs
        assert HomeyAuth.validate_url_format("invalid-url") is False
        assert HomeyAuth.validate_url_format("") is False
        assert HomeyAuth.validate_url_format("ftp://192.168.1.100") is False

    def test_validate_token(self):
        """Test token validation."""
        from homey.auth import HomeyAuth

        # Valid tokens
        assert HomeyAuth.validate_token_format("test-token") is True
        assert HomeyAuth.validate_token_format("a" * 32) is True

        # Invalid tokens
        assert HomeyAuth.validate_token_format("") is False
        assert HomeyAuth.validate_token_format("   ") is False
        assert HomeyAuth.validate_token_format(None) is False

    @pytest.mark.asyncio
    async def test_create_success(self):
        """Test successful client creation."""
        with patch.object(
            HomeyClient, "authenticate", new_callable=AsyncMock
        ) as mock_auth:
            mock_auth.return_value = True

            client = await HomeyClient.create(
                base_url="http://192.168.1.100", token="test-token"
            )

            assert isinstance(client, HomeyClient)
            assert client.base_url == "http://192.168.1.100"
            assert client.token == "test-token"
            mock_auth.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_auth_failure(self):
        """Test client creation with authentication failure."""
        with patch.object(
            HomeyClient, "authenticate", new_callable=AsyncMock
        ) as mock_auth:
            mock_auth.side_effect = HomeyAuthenticationError("Auth failed")

            with pytest.raises(HomeyAuthenticationError):
                await HomeyClient.create(
                    base_url="http://192.168.1.100", token="invalid-token"
                )

    @pytest.mark.asyncio
    async def test_authenticate_success(self):
        """Test successful authentication."""
        client = HomeyClient(base_url="http://192.168.1.100", token="test-token")

        with patch.object(
            client._auth, "authenticate", new_callable=AsyncMock
        ) as mock_auth:
            mock_auth.return_value = True

            result = await client.authenticate()

            assert result is True
            assert client._authenticated is True
            mock_auth.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_failure(self):
        """Test authentication failure."""
        client = HomeyClient(base_url="http://192.168.1.100", token="invalid-token")

        with patch.object(
            client._auth, "authenticate", new_callable=AsyncMock
        ) as mock_auth:
            mock_auth.side_effect = HomeyAuthenticationError("Invalid token")

            with pytest.raises(HomeyAuthenticationError):
                await client.authenticate()

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful connection."""
        client = HomeyClient(base_url="http://192.168.1.100", token="test-token")

        with patch.object(client, "authenticate", new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = True

            result = await client.connect()

            assert result is True
            assert client._connected is True
            mock_auth.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_websocket_explicit(self):
        """Test explicit WebSocket connection."""
        client = HomeyClient(base_url="http://192.168.1.100", token="test-token")

        with patch.object(
            client, "_connect_websocket", new_callable=AsyncMock
        ) as mock_ws:

            async def mock_connect():
                client._websocket_connected = True
                return None

            mock_ws.side_effect = mock_connect

            await client.connect_websocket()

            assert client._websocket_connected is True
            mock_ws.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnection."""
        client = HomeyClient(base_url="http://192.168.1.100", token="test-token")
        client._connected = True
        client._websocket_connected = True  # Set WebSocket as connected

        with patch.object(
            client, "disconnect_websocket", new_callable=AsyncMock
        ) as mock_disconnect_ws:
            await client.disconnect()

            assert client._connected is False
            mock_disconnect_ws.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        client = HomeyClient(base_url="http://192.168.1.100", token="test-token")

        with patch.object(client, "connect", new_callable=AsyncMock) as mock_connect:
            with patch.object(
                client, "disconnect", new_callable=AsyncMock
            ) as mock_disconnect:
                mock_connect.return_value = True

                async with client as ctx_client:
                    assert ctx_client is client
                    mock_connect.assert_called_once()

                mock_disconnect.assert_called_once()

    def test_is_connected(self):
        """Test connection status check."""
        client = HomeyClient(base_url="http://192.168.1.100", token="test-token")

        # Initially not connected
        assert client.is_connected() is False

        # Set connected and authenticated
        client._connected = True
        client._authenticated = True
        assert client.is_connected() is True

        # Connected but not authenticated
        client._authenticated = False
        assert client.is_connected() is False

    def test_is_authenticated(self):
        """Test authentication status check."""
        client = HomeyClient(base_url="http://192.168.1.100", token="test-token")

        # Initially not authenticated
        assert client.is_authenticated() is False

        # Set authenticated
        client._authenticated = True
        assert client.is_authenticated() is True

    @pytest.mark.asyncio
    async def test_get_system_info(self):
        """Test getting system information."""
        client = HomeyClient(base_url="http://192.168.1.100", token="test-token")

        system_info = {"name": "Test Homey", "version": "1.0.0"}

        with patch.object(client, "authenticate", new_callable=AsyncMock) as mock_auth:
            with patch.object(client._auth, "get_session_info") as mock_session:
                mock_auth.return_value = True
                mock_session.return_value = system_info

                result = await client.get_system_info()

                assert result == system_info
                mock_auth.assert_called_once()

    @pytest.mark.asyncio
    async def test_ping_success(self):
        """Test successful ping."""
        client = HomeyClient(base_url="http://192.168.1.100", token="test-token")

        with patch.object(
            client, "get_system_info", new_callable=AsyncMock
        ) as mock_system:
            mock_system.return_value = {"name": "Test Homey"}

            result = await client.ping()

            assert result is True
            mock_system.assert_called_once()

    @pytest.mark.asyncio
    async def test_ping_failure(self):
        """Test ping failure."""
        client = HomeyClient(base_url="http://192.168.1.100", token="test-token")

        with patch.object(
            client, "get_system_info", new_callable=AsyncMock
        ) as mock_system:
            mock_system.side_effect = Exception("Connection failed")

            result = await client.ping()

            assert result is False

    def test_event_handlers(self):
        """Test event handler registration."""
        client = HomeyClient(base_url="http://192.168.1.100", token="test-token")

        def test_handler(data):
            pass

        # Register handler
        client.on("test_event", test_handler)
        assert "test_event" in client._event_handlers
        assert client._event_handlers["test_event"] is test_handler

        # Remove handler
        client.off("test_event")
        assert "test_event" not in client._event_handlers

    def test_managers_initialization(self):
        """Test that managers are properly initialized."""
        client = HomeyClient(base_url="http://192.168.1.100", token="test-token")

        assert client.devices is not None
        assert client.zones is not None
        assert client.flows is not None
        assert client.apps is not None

        # Check that managers have reference to client
        assert client.devices.client is client
        assert client.zones.client is client
        assert client.flows.client is client
        assert client.apps.client is client

    @pytest.mark.asyncio
    async def test_websocket_connection_status(self):
        """Test WebSocket connection status checking."""
        client = HomeyClient(base_url="http://192.168.1.100", token="test-token")

        # Initially not connected
        assert client.is_websocket_connected() is False

        # Mock WebSocket connection
        with patch.object(
            client, "_connect_websocket", new_callable=AsyncMock
        ) as mock_ws:

            async def mock_connect():
                client._websocket_connected = True
                return None

            mock_ws.side_effect = mock_connect

            await client.connect_websocket()
            assert client.is_websocket_connected() is True

    @pytest.mark.asyncio
    async def test_websocket_disconnect(self):
        """Test WebSocket disconnection."""
        client = HomeyClient(base_url="http://192.168.1.100", token="test-token")
        client._websocket_connected = True

        # Mock websocket
        mock_websocket = Mock()
        mock_websocket.close = AsyncMock()
        client._websocket = mock_websocket

        # Mock websocket task
        mock_task = Mock()
        mock_task.done.return_value = False
        mock_task.cancel = Mock()
        client._websocket_task = mock_task

        await client.disconnect_websocket()

        assert client._websocket_connected is False
        mock_websocket.close.assert_called_once()
        mock_task.cancel.assert_called_once()
        assert client._websocket is None

    def test_repr(self):
        """Test string representation."""
        client = HomeyClient(base_url="http://192.168.1.100", token="test-token")

        repr_str = repr(client)
        assert "HomeyClient" in repr_str
        assert "http://192.168.1.100" in repr_str
        assert "disconnected" in repr_str

        # Test connected state
        client._connected = True
        client._authenticated = True
        repr_str = repr(client)
        assert "connected" in repr_str
