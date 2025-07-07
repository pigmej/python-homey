"""
Basic usage example for python-homey library.

This example demonstrates how to:
1. Connect to your Homey
2. Get device information
3. Control devices
4. Work with zones and flows
5. Handle errors properly
"""

import os
from dotenv import load_dotenv
import asyncio
import logging
from typing import Optional

from homey import (
    HomeyClient,
    HomeyConnectionError,
    HomeyAuthenticationError,
    HomeyError,
    App,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - Replace with your actual values
# HOMEY_URL = "http://192.168.1.100"  # Your Homey's IP address
# TOKEN = "your-personal-access-token"  # Your Personal Access Token
#
# Load environment variables


load_dotenv()

HOMEY_URL = os.getenv("HOMEY_URL", "http://localhost")
TOKEN = os.getenv("TOKEN", "make-it-real-token")


async def main():
    """Main example function."""
    try:
        # Create and connect to Homey
        client = await HomeyClient.create(
            base_url=HOMEY_URL,
            token=TOKEN,
            debug=True,  # Enable debug logging
        )

        async with client:
            logger.info("Connected to Homey successfully!")

            # Get system information
            system_info = await client.get_system_info()
            logger.info(f"System info: {system_info}")

            # Demonstrate device management
            await device_examples(client)

            # Demonstrate zone management
            await zone_examples(client)

            # Demonstrate flow management
            await flow_examples(client)

            # Note: Real-time events require explicit WebSocket connection
            # See realtime_events.py example for WebSocket usage

    except HomeyAuthenticationError:
        logger.error("Authentication failed! Check your token.")
        logger.info(f"Create a token at: {HOMEY_URL}/manager/users/token")
    except HomeyConnectionError:
        logger.error("Connection failed! Check your Homey URL and network.")
    except HomeyError as e:
        logger.error(f"Homey error: {e.message}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


async def device_examples(client: HomeyClient):
    """Demonstrate device management."""
    logger.info("=== Device Examples ===")

    try:
        # Get all devices
        devices = await client.devices.get_devices()
        logger.info(f"Found {len(devices)} devices")

        # Show device information
        for device in devices[:5]:  # Show first 5 devices
            logger.info(f"Device: {device.name} ({device.id})")
            logger.info(f"  - Zone: {device.zoneName}")
            logger.info(f"  - Class: {device.class_}")
            logger.info(f"  - Online: {device.is_online()}")
            logger.info(f"  - Capabilities: {device.capabilities}")

            # Show capability values
            for cap in device.capabilities[:3]:  # Show first 3 capabilities
                value = device.get_capability_value(cap)
                logger.info(f"  - {cap}: {value}")

        # Get devices by type
        lights = await client.devices.get_devices_by_class("light")
        logger.info(f"Found {len(lights)} lights")

        # Get online devices
        online_devices = await client.devices.get_online_devices()
        logger.info(f"Found {len(online_devices)} online devices")

        # Example: Control a light (if available)
        if lights:
            light = lights[0]
            logger.info(f"Controlling light: {light.name}")

            if light.has_capability("onoff"):
                # Turn on
                if light.id:
                    await client.devices.turn_on(light.id)
                logger.info("Light turned on")

                # Wait a bit
                await asyncio.sleep(2)

                # Turn off
                if light.id:
                    await client.devices.turn_off(light.id)
                logger.info("Light turned off")

            if light.has_capability("dim"):
                # Set brightness to 50%
                if light.id:
                    await client.devices.set_dim_level(light.id, 0.5)
                logger.info("Light dimmed to 50%")

    except Exception as e:
        logger.error(f"Device example error: {e}")


async def zone_examples(client: HomeyClient):
    """Demonstrate zone management."""
    logger.info("=== Zone Examples ===")

    try:
        # Get all zones
        zones = await client.zones.get_zones()
        logger.info(f"Found {len(zones)} zones")

        # Show zone hierarchy
        root_zones = await client.zones.get_root_zones()
        logger.info(f"Root zones: {[z.name for z in root_zones]}")

        # Show zone information
        for zone in zones[:5]:  # Show first 5 zones
            logger.info(f"Zone: {zone.name} ({zone.id})")
            logger.info(f"  - Active: {zone.is_active()}")
            logger.info(f"  - Parent: {zone.parent}")

            # Get devices in this zone
            if zone.id:
                zone_devices = await client.devices.get_devices_by_zone(zone.id)
            else:
                zone_devices = []
            logger.info(f"  - Devices: {len(zone_devices)}")

        # Get zone tree structure
        zone_tree = await client.zones.get_zone_tree()
        logger.info("Zone tree structure retrieved")

    except Exception as e:
        logger.error(f"Zone example error: {e}")


async def flow_examples(client: HomeyClient):
    """Demonstrate flow management."""
    logger.info("=== Flow Examples ===")

    try:
        # Get all flows
        flows = await client.flows.get_flows()
        logger.info(f"Found {len(flows)} flows")

        # Show flow information
        for flow in flows[:3]:  # Show first 3 flows
            logger.info(f"Flow: {flow.name} ({flow.id})")
            logger.info(f"  - Enabled: {flow.is_enabled()}")
            logger.info(f"  - Broken: {flow.is_broken()}")
            logger.info(f"  - Advanced: {flow.is_advanced()}")
            logger.info(f"  - Execution count: {flow.executionCount}")

        # Get flow categories
        enabled_flows = await client.flows.get_enabled_flows()
        broken_flows = await client.flows.get_broken_flows()
        advanced_flows = await client.flows.get_advanced_flows()

        logger.info(f"Enabled flows: {len(enabled_flows)}")
        logger.info(f"Broken flows: {len(broken_flows)}")
        logger.info(f"Advanced flows: {len(advanced_flows)}")

        # Show broken flows (if any)
        if broken_flows:
            logger.warning("Broken flows found:")
            for flow in broken_flows:
                logger.warning(f"  - {flow.name}")

    except Exception as e:
        logger.error(f"Flow example error: {e}")


async def websocket_examples(client: HomeyClient):
    """Demonstrate WebSocket connection for real-time events."""
    logger.info("=== WebSocket Examples ===")

    try:
        # Connect to WebSocket explicitly
        await client.connect_websocket(auto_reconnect=True)
        logger.info("✅ WebSocket connected for real-time events")

        # Define event handlers
        async def on_device_event(event_data):
            logger.info(f"Device event received: {event_data}")

        async def on_zone_event(event_data):
            logger.info(f"Zone event received: {event_data}")

        async def on_flow_event(event_data):
            logger.info(f"Flow event received: {event_data}")

        # Register event handlers
        client.on("device", on_device_event)
        client.on("zone", on_zone_event)
        client.on("flow", on_flow_event)

        logger.info("Listening for events for 10 seconds...")

        # Listen for events for 10 seconds
        await asyncio.sleep(10)

        # Remove event handlers
        client.off("device")
        client.off("zone")
        client.off("flow")

        # Disconnect WebSocket
        await client.disconnect_websocket()
        logger.info("WebSocket disconnected")

    except Exception as e:
        logger.error(f"WebSocket example error: {e}")
        logger.info("💡 See realtime_events.py for more detailed WebSocket examples")


async def advanced_examples(client: HomeyClient):
    """Advanced usage examples."""
    logger.info("=== Advanced Examples ===")

    try:
        # Batch operations - turn off all lights
        lights = await client.devices.get_devices_by_class("light")

        if lights:
            logger.info(f"Turning off {len(lights)} lights...")

            # Create tasks for concurrent execution
            tasks = []
            for light in lights:
                print(light)
                # if light.has_capability("onoff") and light.id:
                #     task = client.devices.turn_off(light.id)
                #     tasks.append(task)

            # Execute all tasks concurrently
            # await asyncio.gather(*tasks, return_exceptions=True)
            # logger.info("All lights turned off")

        # Search for devices
        bedroom_devices = await client.devices.search_devices("bedroom")
        logger.info(f"Found {len(bedroom_devices)} bedroom devices")

        # Get recently executed flows
        recent_flows = await client.flows.get_recently_executed_flows(5)
        logger.info(f"Recently executed flows: {[f.name for f in recent_flows]}")

        # Get most executed flows
        popular_flows = await client.flows.get_most_executed_flows(5)
        logger.info(f"Most executed flows: {[f.name for f in popular_flows]}")

    except Exception as e:
        logger.error(f"Advanced example error: {e}")


if __name__ == "__main__":
    # Check if configuration is set
    if TOKEN == "your-personal-access-token":
        print("Please set your Homey URL and token in the script!")
        print(f"Create a token at: {HOMEY_URL}/manager/users/token")
        exit(1)

    # Run the example
    asyncio.run(main())
