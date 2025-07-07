"""
Device Control Example for python-homey library.

This example demonstrates how to control devices with your Homey.
"""

import asyncio
import logging
from homey import HomeyClient, HomeyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - Update these values
HOMEY_URL = "http://192.168.1.100"  # Your Homey's IP address
TOKEN = "your-personal-access-token"  # Your Personal Access Token


async def main():
    """Main example function."""
    if TOKEN == "your-personal-access-token":
        print("❌ Please update the HOMEY_URL and TOKEN variables!")
        return

    try:
        client = await HomeyClient.create(base_url=HOMEY_URL, token=TOKEN)

        async with client:
            logger.info("✅ Connected to Homey!")

            # Get all devices
            devices = await client.devices.get_devices()
            logger.info(f"📱 Found {len(devices)} devices")

            # Find lights
            lights = await client.devices.get_devices_by_class("light")
            logger.info(f"💡 Found {len(lights)} lights")

            if lights:
                # Control the first light
                light = lights[0]
                logger.info(f"🔧 Controlling: {light.name}")

                # Check if it has on/off capability
                if light.has_capability("onoff"):
                    current_state = light.get_capability_value("onoff")
                    logger.info(f"Current state: {'On' if current_state else 'Off'}")

                    # Turn on
                    if light.id:
                        await client.devices.turn_on(light.id)
                        logger.info("💡 Light turned ON")

                        await asyncio.sleep(2)

                        # Turn off
                        await client.devices.turn_off(light.id)
                        logger.info("🌑 Light turned OFF")

                # Check if it supports dimming
                if light.has_capability("dim"):
                    logger.info("🔆 Testing dimming...")

                    # Set to 25%
                    if light.id:
                        await client.devices.set_dim_level(light.id, 0.25)
                        logger.info("🔅 Set brightness to 25%")

                        await asyncio.sleep(1)

                        # Set to 75%
                        await client.devices.set_dim_level(light.id, 0.75)
                        logger.info("🔆 Set brightness to 75%")

                        await asyncio.sleep(1)

                        # Turn off
                        await client.devices.turn_off(light.id)
                        logger.info("🌑 Light turned OFF")

            # Find temperature sensors
            sensors = await client.devices.get_devices_by_capability(
                "measure_temperature"
            )
            logger.info(f"🌡️ Found {len(sensors)} temperature sensors")

            for sensor in sensors[:3]:  # Show first 3 sensors
                temp = sensor.get_capability_value("measure_temperature")
                logger.info(f"🌡️ {sensor.name}: {temp}°C")

            # Find all devices in a specific zone (if any)
            zones = await client.zones.get_zones()
            if zones:
                first_zone = zones[0]
                if first_zone.id:
                    zone_devices = await client.devices.get_devices_by_zone(
                        first_zone.id
                    )
                    logger.info(
                        f"🏠 Zone '{first_zone.name}' has {len(zone_devices)} devices"
                    )

            # Search for devices
            bedroom_devices = await client.devices.search_devices("bedroom")
            logger.info(f"🛏️ Found {len(bedroom_devices)} bedroom devices")

            # Get device status
            online_devices = await client.devices.get_online_devices()
            offline_devices = await client.devices.get_offline_devices()
            logger.info(
                f"📶 Online: {len(online_devices)}, Offline: {len(offline_devices)}"
            )

            logger.info("🎉 Device control example completed!")

    except HomeyError as e:
        logger.error(f"❌ Homey error: {e.message}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    print("🔌 Device Control Example")
    print("=" * 50)
    asyncio.run(main())
