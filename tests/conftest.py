"""Configuration for pytest tests."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import AsyncGenerator, Generator, Optional

from homey import HomeyClient
from homey.models import Device, Zone, Flow, App


@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for each test."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_homey_client() -> Mock:
    """Create a mock Homey client."""
    client = Mock(spec=HomeyClient)
    client.base_url = "http://test.homey.local"
    client.token = "test-token"
    client.is_connected = Mock(return_value=True)
    client.is_authenticated = Mock(return_value=True)
    return client


@pytest.fixture
def sample_device_data() -> dict:
    """Sample device data for testing."""
    return {
        "id": "test-device-id",
        "name": "Test Device",
        "driverUri": "homey:app:test.app",
        "driverId": "test-driver",
        "zone": "test-zone-id",
        "zoneName": "Test Zone",
        "class": "light",
        "capabilities": ["onoff", "dim"],
        "capabilitiesObj": {
            "onoff": {
                "value": True,
                "id": "onoff",
                "type": "boolean",
                "getable": True,
                "setable": True,
                "reportable": True,
                "title": "On/Off",
                "desc": "Turn device on or off",
            },
            "dim": {
                "value": 0.5,
                "id": "dim",
                "type": "number",
                "getable": True,
                "setable": True,
                "reportable": True,
                "title": "Brightness",
                "desc": "Control brightness",
                "min": 0,
                "max": 1,
                "step": 0.01,
            },
        },
        "ready": True,
        "available": True,
        "repair": False,
        "unpair": False,
        "settings": {},
        "energy": {},
        "insights": [],
    }


@pytest.fixture
def sample_device(sample_device_data) -> Device:
    """Create a sample device for testing."""
    return Device(**sample_device_data)


@pytest.fixture
def sample_zone_data() -> dict:
    """Sample zone data for testing."""
    return {
        "id": "test-zone-id",
        "name": "Test Zone",
        "parent": None,
        "icon": "home",
        "active": True,
        "activeLastUpdated": "2024-01-01T00:00:00.000Z",
    }


@pytest.fixture
def sample_zone(sample_zone_data) -> Zone:
    """Create a sample zone for testing."""
    return Zone(**sample_zone_data)


@pytest.fixture
def sample_flow_data() -> dict:
    """Sample flow data for testing."""
    return {
        "id": "test-flow-id",
        "name": "Test Flow",
        "type": "flow",
        "enabled": True,
        "trigger": {
            "id": "trigger-id",
            "uri": "homey:app:test.app",
            "title": "Test Trigger",
            "type": "trigger",
        },
        "conditions": [
            {
                "id": "condition-id",
                "uri": "homey:app:test.app",
                "title": "Test Condition",
                "type": "condition",
            }
        ],
        "actions": [
            {
                "id": "action-id",
                "uri": "homey:app:test.app",
                "title": "Test Action",
                "type": "action",
            }
        ],
        "folder": None,
        "broken": False,
        "lastExecuted": "2024-01-01T00:00:00.000Z",
        "executionCount": 10,
        "advanced": False,
    }


@pytest.fixture
def sample_flow(sample_flow_data) -> Flow:
    """Create a sample flow for testing."""
    return Flow(**sample_flow_data)


@pytest.fixture
def sample_app_data() -> dict:
    """Sample app data for testing."""
    return {
        "id": "test.app",
        "name": "Test App",
        "version": "1.0.0",
        "origin": "app-store",
        "channel": "stable",
        "autoupdate": True,
        "enabled": True,
        "installed": True,
        "state": "running",
        "crashed": False,
        "permissions": ["homey:manager:api"],
        "settings": {},
        "brandColor": "#FF0000",
        "category": "tools",
        "compatibility": ">=5.0.0",
        "description": {"en": "Test application"},
        "platforms": ["local"],
        "author": {"name": "Test Author", "email": "test@example.com"},
    }


@pytest.fixture
def sample_app(sample_app_data) -> App:
    """Create a sample app for testing."""
    return App(**sample_app_data)


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for testing."""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "success"}
    mock_client.request.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_websocket():
    """Mock websocket connection for testing."""
    mock_ws = AsyncMock()
    mock_ws.close = AsyncMock()
    return mock_ws


class MockHomeyAPI:
    """Mock Homey API for integration tests."""

    def __init__(self):
        self.devices = {}
        self.zones = {}
        self.flows = {}
        self.apps = {}
        self.connected = False
        self.authenticated = False

    async def connect(self):
        """Mock connection."""
        self.connected = True
        return True

    async def authenticate(self, token: str):
        """Mock authentication."""
        if token == "valid-token":
            self.authenticated = True
            return True
        return False

    async def get_devices(self):
        """Mock get devices."""
        return self.devices

    async def get_zones(self):
        """Mock get zones."""
        return self.zones

    async def get_flows(self):
        """Mock get flows."""
        return self.flows

    async def get_apps(self):
        """Mock get apps."""
        return self.apps


@pytest.fixture
def mock_homey_api():
    """Create a mock Homey API instance."""
    return MockHomeyAPI()


@pytest.fixture
async def authenticated_client(mock_homey_api) -> AsyncGenerator[HomeyClient, None]:
    """Create an authenticated client for testing."""
    # This would need proper mocking in actual tests
    # For now, it's a placeholder
    client = Mock(spec=HomeyClient)
    client.base_url = "http://test.homey.local"
    client.token = "test-token"
    client.is_connected = Mock(return_value=True)
    client.is_authenticated = Mock(return_value=True)
    yield client


# Test data collections
@pytest.fixture
def multiple_devices_data(sample_device_data) -> dict:
    """Multiple devices data for testing."""
    devices = {}
    for i in range(3):
        device_data = sample_device_data.copy()
        device_data["id"] = f"device-{i}"
        device_data["name"] = f"Device {i}"
        devices[f"device-{i}"] = device_data
    return devices


@pytest.fixture
def multiple_zones_data(sample_zone_data) -> dict:
    """Multiple zones data for testing."""
    zones = {}
    for i in range(3):
        zone_data = sample_zone_data.copy()
        zone_data["id"] = f"zone-{i}"
        zone_data["name"] = f"Zone {i}"
        zones[f"zone-{i}"] = zone_data
    return zones


@pytest.fixture
def multiple_flows_data(sample_flow_data) -> dict:
    """Multiple flows data for testing."""
    flows = {}
    for i in range(3):
        flow_data = sample_flow_data.copy()
        flow_data["id"] = f"flow-{i}"
        flow_data["name"] = f"Flow {i}"
        flows[f"flow-{i}"] = flow_data
    return flows


@pytest.fixture
def multiple_apps_data(sample_app_data) -> dict:
    """Multiple apps data for testing."""
    apps = {}
    for i in range(3):
        app_data = sample_app_data.copy()
        app_data["id"] = f"app-{i}"
        app_data["name"] = f"App {i}"
        apps[f"app-{i}"] = app_data
    return apps


# Error simulation fixtures
@pytest.fixture
def connection_error():
    """Simulate connection error."""
    from homey.exceptions import HomeyConnectionError

    return HomeyConnectionError("Connection failed")


@pytest.fixture
def auth_error():
    """Simulate authentication error."""
    from homey.exceptions import HomeyAuthenticationError

    return HomeyAuthenticationError("Authentication failed")


@pytest.fixture
def api_error():
    """Simulate API error."""
    from homey.exceptions import HomeyAPIError

    return HomeyAPIError("API error", status_code=500)


@pytest.fixture
def timeout_error():
    """Simulate timeout error."""
    from homey.exceptions import HomeyTimeoutError

    return HomeyTimeoutError("Request timed out")


# Helper functions for tests
def create_mock_response(status_code: int = 200, json_data: Optional[dict] = None):
    """Create a mock HTTP response."""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data or {}
    return mock_response


def create_device_response(device_data: dict):
    """Create a mock device response."""
    return create_mock_response(200, device_data)


def create_zone_response(zone_data: dict):
    """Create a mock zone response."""
    return create_mock_response(200, zone_data)


def create_flow_response(flow_data: dict):
    """Create a mock flow response."""
    return create_mock_response(200, flow_data)


def create_app_response(app_data: dict):
    """Create a mock app response."""
    return create_mock_response(200, app_data)


# Async test utilities
async def wait_for_condition(
    condition_func, timeout: float = 1.0, interval: float = 0.1
):
    """Wait for a condition to be true."""
    elapsed = 0.0
    while elapsed < timeout:
        if (
            await condition_func()
            if asyncio.iscoroutinefunction(condition_func)
            else condition_func()
        ):
            return True
        await asyncio.sleep(interval)
        elapsed += interval
    return False


# Test markers - configure pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "slow: slow tests")
    config.addinivalue_line("markers", "network: network tests")
