# Python Homey

A modern, async Python client library for the Homey v3 Local API.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Features

- **Async/await support** - Built from the ground up with async/await
- **Type hints** - Fully typed with mypy support
- **High-level API** - Pythonic interface that's easy to use
- **Real-time events** - WebSocket support for real-time device updates
- **Comprehensive coverage** - Support for devices, zones, flows, apps, and more
- **Error handling** - Detailed exception hierarchy for better error handling
- **Auto-reconnection** - Automatic WebSocket reconnection with exponential backoff

## Installation

```bash
# Using uv (recommended)
uv add python-homey

# Using pip
pip install python-homey
```

## Quick Start

### Basic Usage

```python
import asyncio
from homey import HomeyClient

async def main():
    # Create and authenticate client
    client = await HomeyClient.create(
        base_url="http://192.168.1.100",  # Your Homey's IP address
        token="your-personal-access-token"
    )

    # Get all devices
    devices = await client.devices.get_devices()
    print(f"Found {len(devices)} devices")

    # Turn on a specific device
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

### Using Context Manager (Recommended)

```python
import asyncio
from homey import HomeyClient

async def main():
    async with HomeyClient.create(
        base_url="http://192.168.1.100",
        token="your-personal-access-token"
    ) as client:
        # Work with the client
        devices = await client.devices.get_devices()
        for device in devices:
            print(f"Device: {device.name} ({device.id})")
        
        # Connection automatically closed when exiting context

asyncio.run(main())
```

## Authentication

You'll need a Personal Access Token to authenticate with your Homey. You can create one by visiting your Homey's web interface:

```python
from homey import get_token_url

# Get the URL for creating a token
token_url = get_token_url("http://192.168.1.100")
print(f"Create your token at: {token_url}")
```

Or manually navigate to: `http://your-homey-ip/manager/users/token`

## Device Management

### Getting Devices

```python
async with HomeyClient.create(base_url="http://192.168.1.100", token="token") as client:
    # Get all devices
    devices = await client.devices.get_devices()
    
    # Get a specific device
    device = await client.devices.get_device("device-id")
    
    # Get devices by zone
    living_room_devices = await client.devices.get_devices_by_zone("living-room-id")
    
    # Get devices by class
    lights = await client.devices.get_devices_by_class("light")
    
    # Get devices by capability
    dimmable_devices = await client.devices.get_devices_by_capability("dim")
    
    # Get online/offline devices
    online_devices = await client.devices.get_online_devices()
    offline_devices = await client.devices.get_offline_devices()
    
    # Search devices
    bedroom_devices = await client.devices.search_devices("bedroom")
```

### Controlling Devices

```python
async with HomeyClient.create(base_url="http://192.168.1.100", token="token") as client:
    # Basic on/off control
    await client.devices.turn_on("device-id")
    await client.devices.turn_off("device-id")
    await client.devices.toggle("device-id")
    
    # Set capability values
    await client.devices.set_capability_value("light-id", "dim", 0.5)  # 50% brightness
    await client.devices.set_capability_value("thermostat-id", "target_temperature", 21.5)
    
    # Get capability values
    current_temp = await client.devices.get_capability_value("sensor-id", "measure_temperature")
    
    # Convenience methods
    await client.devices.set_dim_level("light-id", 0.8)  # 80% brightness
    await client.devices.set_target_temperature("thermostat-id", 22.0)
```

### Device Information

```python
async with HomeyClient.create(base_url="http://192.168.1.100", token="token") as client:
    device = await client.devices.get_device("device-id")
    
    # Device properties
    print(f"Name: {device.name}")
    print(f"Zone: {device.zoneName}")
    print(f"Class: {device.class_}")
    print(f"Online: {device.is_online()}")
    
    # Capabilities
    print(f"Capabilities: {device.capabilities}")
    if device.has_capability("onoff"):
        current_state = device.get_capability_value("onoff")
        print(f"Current state: {current_state}")
    
    # Get device settings
    settings = await client.devices.get_device_settings("device-id")
    
    # Get device flows
    flows = await client.devices.get_device_flows("device-id")
```

## Zone Management

### Working with Zones

```python
async with HomeyClient.create(base_url="http://192.168.1.100", token="token") as client:
    # Get all zones
    zones = await client.zones.get_zones()
    
    # Get a specific zone
    zone = await client.zones.get_zone("zone-id")
    
    # Create a new zone
    new_zone = await client.zones.create_zone("New Room", parent_id="parent-zone-id")
    
    # Update zone
    updated_zone = await client.zones.update_zone("zone-id", name="Updated Name")
    
    # Delete zone
    await client.zones.delete_zone("zone-id")
    
    # Zone hierarchy
    root_zones = await client.zones.get_root_zones()
    child_zones = await client.zones.get_child_zones("parent-zone-id")
    hierarchy = await client.zones.get_zone_hierarchy("zone-id")
    
    # Zone tree structure
    tree = await client.zones.get_zone_tree()
```

## Flow Management

### Working with Flows

```python
async with HomeyClient.create(base_url="http://192.168.1.100", token="token") as client:
    # Get all flows
    flows = await client.flows.get_flows()
    
    # Get a specific flow
    flow = await client.flows.get_flow("flow-id")
    
    # Create a new flow
    new_flow = await client.flows.create_flow("New Flow", enabled=True)
    
    # Update flow
    updated_flow = await client.flows.update_flow("flow-id", name="Updated Flow")
    
    # Enable/disable flows
    await client.flows.enable_flow("flow-id")
    await client.flows.disable_flow("flow-id")
    
    # Trigger a flow manually
    await client.flows.trigger_flow("flow-id", tokens={"temperature": 25.5})
    
    # Flow categories
    enabled_flows = await client.flows.get_enabled_flows()
    broken_flows = await client.flows.get_broken_flows()
    advanced_flows = await client.flows.get_advanced_flows()
    
    # Flow operations
    duplicate = await client.flows.duplicate_flow("flow-id", "Copy of Original")
    exported = await client.flows.export_flow("flow-id")
    imported = await client.flows.import_flow(exported)
```

## App Management

### Working with Apps

```python
async with HomeyClient.create(base_url="http://192.168.1.100", token="token") as client:
    # Get all apps
    apps = await client.apps.get_apps()
    
    # Get a specific app
    app = await client.apps.get_app("app-id")
    
    # App control
    await client.apps.enable_app("app-id")
    await client.apps.disable_app("app-id")
    await client.apps.restart_app("app-id")
    
    # App categories
    running_apps = await client.apps.get_running_apps()
    crashed_apps = await client.apps.get_crashed_apps()
    system_apps = await client.apps.get_system_apps()
    
    # App settings
    settings = await client.apps.get_app_settings("app-id")
    await client.apps.set_app_settings("app-id", {"key": "value"})
    
    # App logs
    logs = await client.apps.get_app_logs("app-id", limit=100)
```

## Real-time Events

Listen to real-time events from your Homey:

```python
async def on_device_update(event_data):
    print(f"Device updated: {event_data}")

async def on_zone_update(event_data):
    print(f"Zone updated: {event_data}")

async with HomeyClient.create(base_url="http://192.168.1.100", token="token") as client:
    # Register event handlers
    client.on("device", on_device_update)
    client.on("zone", on_zone_update)
    
    # Keep the connection alive to receive events
    await asyncio.sleep(60)  # Listen for 60 seconds
```

## Error Handling

The library provides a comprehensive exception hierarchy:

```python
from homey import (
    HomeyError,
    HomeyConnectionError,
    HomeyAuthenticationError,
    HomeyNotFoundError,
    HomeyPermissionError,
    HomeyAPIError,
    HomeyTimeoutError,
    HomeyValidationError,
    HomeyDeviceError,
    HomeyFlowError,
    HomeyWebSocketError,
)

async def safe_device_control():
    try:
        async with HomeyClient.create(base_url="http://192.168.1.100", token="token") as client:
            await client.devices.turn_on("device-id")
    except HomeyAuthenticationError:
        print("Authentication failed - check your token")
    except HomeyDeviceError as e:
        print(f"Device error: {e.message}")
        if e.device_id:
            print(f"Device ID: {e.device_id}")
    except HomeyConnectionError:
        print("Connection failed - check your Homey's IP address")
    except HomeyError as e:
        print(f"General Homey error: {e.message}")
```

## Advanced Usage

### Custom Timeout and SSL Settings

```python
async with HomeyClient.create(
    base_url="https://192.168.1.100",  # HTTPS
    token="token",
    timeout=60.0,  # 60 second timeout
    verify_ssl=False,  # Disable SSL verification
    auto_reconnect=True,  # Auto-reconnect WebSocket
    debug=True  # Enable debug logging
) as client:
    # Your code here
    pass
```

### Working with Device Capabilities

```python
async with HomeyClient.create(base_url="http://192.168.1.100", token="token") as client:
    device = await client.devices.get_device("device-id")
    
    # Check capabilities
    if device.has_capability("onoff"):
        print("Device can be turned on/off")
    
    if device.has_capability("dim"):
        print("Device can be dimmed")
        current_level = device.get_capability_value("dim")
        print(f"Current dim level: {current_level}")
    
    # Get all capabilities
    capabilities = await client.devices.get_device_capabilities("device-id")
    for cap_id, capability in capabilities.items():
        print(f"Capability {cap_id}: {capability.value}")
```

### Batch Operations

```python
async with HomeyClient.create(base_url="http://192.168.1.100", token="token") as client:
    # Get all lights in the living room
    living_room_lights = await client.devices.get_devices_by_zone("living-room-id")
    lights = [d for d in living_room_lights if d.has_capability("onoff")]
    
    # Turn on all lights
    for light in lights:
        await client.devices.turn_on(light.id)
    
    # Or turn off all lights at once
    tasks = [client.devices.turn_off(light.id) for light in lights]
    await asyncio.gather(*tasks)
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/python-homey.git
cd python-homey

# Install dependencies using uv
uv sync

# Install development dependencies
uv sync --extra dev
```

### Testing

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=homey

# Run specific test file
uv run pytest tests/test_client.py
```

### Code Quality

```bash
# Format code
uv run black src/homey tests/

# Sort imports
uv run isort src/homey tests/

# Type checking
uv run mypy src/homey

# Run all quality checks
uv run pre-commit run --all-files
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for the [Homey](https://homey.app) smart home platform
- Inspired by the official [node-homey-api](https://github.com/athombv/node-homey-api) library
- Thanks to the Homey community for their support and feedback

## Support

- 📖 [Documentation](https://python-homey.readthedocs.io)
- 🐛 [Issue Tracker](https://github.com/yourusername/python-homey/issues)
- 💬 [Homey Community Forum](https://community.homey.app)
- 🔧 [Stack Overflow](https://stackoverflow.com/questions/tagged/homey) (use the `homey` tag)

## Changelog

### 0.1.0 (2024-01-01)

- Initial release
- Support for devices, zones, flows, and apps
- WebSocket support for real-time events
- Comprehensive error handling
- Full async/await support
- Type hints and mypy support