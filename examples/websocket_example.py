"""
WebSocket Example for python-homey library.

This example demonstrates how to explicitly connect to WebSocket for real-time events.
WebSocket functionality is completely optional and must be explicitly enabled.
"""

import asyncio
import logging
from datetime import datetime
from homey import HomeyClient, HomeyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - Update these values
HOMEY_URL = "http://192.168.1.100"  # Your Homey's IP address
TOKEN = "your-personal-access-token"  # Your Personal Access Token


async def basic_websocket_example():
    """Basic example of WebSocket usage."""
    logger.info("=== Basic WebSocket Example ===")

    if TOKEN == "your-personal-access-token":
        print("❌ Please update the HOMEY_URL and TOKEN variables!")
        return

    try:
        # Create client (WebSocket NOT automatically connected)
        client = await HomeyClient.create(base_url=HOMEY_URL, token=TOKEN)

        async with client:
            logger.info("✅ Connected to Homey (without WebSocket)")

            # Check WebSocket status
            logger.info(f"WebSocket connected: {client.is_websocket_connected()}")

            # Explicitly connect to WebSocket for real-time events
            try:
                await client.connect_websocket(auto_reconnect=True)
                logger.info("🔌 WebSocket connected successfully")
                logger.info(f"WebSocket connected: {client.is_websocket_connected()}")
            except Exception as e:
                logger.error(f"❌ WebSocket connection failed: {e}")
                logger.info("💡 Continuing without real-time events")
                return

            # Define event handlers
            async def on_device_event(event_data):
                timestamp = datetime.now().strftime("%H:%M:%S")
                device_name = event_data.get("name", "Unknown Device")
                logger.info(f"🔌 [{timestamp}] Device event: {device_name}")

            async def on_zone_event(event_data):
                timestamp = datetime.now().strftime("%H:%M:%S")
                zone_name = event_data.get("name", "Unknown Zone")
                logger.info(f"🏠 [{timestamp}] Zone event: {zone_name}")

            # Register event handlers
            client.on("device", on_device_event)
            client.on("zone", on_zone_event)

            logger.info("👂 Listening for events for 15 seconds...")
            await asyncio.sleep(15)

            # Remove event handlers
            client.off("device")
            client.off("zone")

            # Explicitly disconnect WebSocket
            await client.disconnect_websocket()
            logger.info("🔌 WebSocket disconnected")
            logger.info(f"WebSocket connected: {client.is_websocket_connected()}")

    except HomeyError as e:
        logger.error(f"❌ Homey error: {e.message}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")


async def optional_websocket_example():
    """Example showing how to handle WebSocket connection failures gracefully."""
    logger.info("=== Optional WebSocket Example ===")

    if TOKEN == "your-personal-access-token":
        print("❌ Please update the HOMEY_URL and TOKEN variables!")
        return

    try:
        # Create client
        client = await HomeyClient.create(base_url=HOMEY_URL, token=TOKEN)

        async with client:
            logger.info("✅ Connected to Homey")

            # Get devices without WebSocket
            devices = await client.devices.get_devices()
            logger.info(f"📱 Found {len(devices)} devices (without WebSocket)")

            # Try to connect WebSocket, but don't fail if it doesn't work
            websocket_available = False
            try:
                await client.connect_websocket()
                websocket_available = True
                logger.info("🔌 WebSocket connected - real-time events available")
            except Exception as e:
                logger.warning(f"⚠️ WebSocket connection failed: {e}")
                logger.info("💡 Continuing with API-only functionality")

            # Show device information
            for device in devices[:3]:  # Show first 3 devices
                logger.info(f"  - {device.name} ({device.class_})")

            # If WebSocket is available, listen for events
            if websocket_available:

                def on_any_event(event_data):
                    logger.info(f"📡 Event received: {event_data}")

                client.on("device", on_any_event)
                logger.info("👂 Listening for device events for 10 seconds...")
                await asyncio.sleep(10)
                client.off("device")

                await client.disconnect_websocket()
                logger.info("🔌 WebSocket disconnected")
            else:
                logger.info("⏭️ Skipping real-time events (WebSocket not available)")

    except HomeyError as e:
        logger.error(f"❌ Homey error: {e.message}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")


async def websocket_status_example():
    """Example showing WebSocket status checking."""
    logger.info("=== WebSocket Status Example ===")

    if TOKEN == "your-personal-access-token":
        print("❌ Please update the HOMEY_URL and TOKEN variables!")
        return

    try:
        client = await HomeyClient.create(base_url=HOMEY_URL, token=TOKEN)

        async with client:
            # Check initial status
            logger.info(f"Initial WebSocket status: {client.is_websocket_connected()}")

            # Connect
            await client.connect_websocket()
            logger.info(f"After connect: {client.is_websocket_connected()}")

            # Wait a bit
            await asyncio.sleep(2)

            # Disconnect
            await client.disconnect_websocket()
            logger.info(f"After disconnect: {client.is_websocket_connected()}")

            # Try to connect again
            await client.connect_websocket()
            logger.info(f"After reconnect: {client.is_websocket_connected()}")

    except HomeyError as e:
        logger.error(f"❌ Homey error: {e.message}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")


async def without_websocket_example():
    """Example showing full API usage without WebSocket."""
    logger.info("=== Without WebSocket Example ===")

    if TOKEN == "your-personal-access-token":
        print("❌ Please update the HOMEY_URL and TOKEN variables!")
        return

    try:
        # Create client and never connect WebSocket
        client = await HomeyClient.create(base_url=HOMEY_URL, token=TOKEN)

        async with client:
            logger.info("✅ Connected to Homey (WebSocket never connected)")

            # All API functionality works without WebSocket
            devices = await client.devices.get_devices()
            logger.info(f"📱 Found {len(devices)} devices")

            zones = await client.zones.get_zones()
            logger.info(f"🏠 Found {len(zones)} zones")

            flows = await client.flows.get_flows()
            logger.info(f"🔄 Found {len(flows)} flows")

            # Event handlers can be registered but won't receive events
            def dummy_handler(event_data):
                logger.info(f"This won't be called: {event_data}")

            client.on("device", dummy_handler)
            logger.info("📵 Event handler registered but no events will be received")

            # Check WebSocket status
            logger.info(f"WebSocket status: {client.is_websocket_connected()}")

            logger.info("✅ All API functionality works without WebSocket!")

    except HomeyError as e:
        logger.error(f"❌ Homey error: {e.message}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")


async def main():
    """Main function to run all examples."""
    print("🔌 WebSocket Examples for python-homey")
    print("=" * 50)
    print("These examples show how WebSocket functionality is completely optional.")
    print("You can use the full Homey API without ever connecting to WebSocket.")
    print()

    # Run examples
    await basic_websocket_example()
    print("\n" + "=" * 50)

    await optional_websocket_example()
    print("\n" + "=" * 50)

    await websocket_status_example()
    print("\n" + "=" * 50)

    await without_websocket_example()
    print("\n" + "=" * 50)

    print("✅ All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
