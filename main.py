"""
Demonstration script for the python-homey library.

This script shows how to use the python-homey library to interact with your Homey.
Replace the configuration values below with your actual Homey details.
"""

import asyncio
import logging

from homey import HomeyClient, HomeyError, get_token_url

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration - Update these with your actual values
HOMEY_URL = "http://192.168.1.100"  # Replace with your Homey's IP address
TOKEN = "your-personal-access-token"  # Replace with your Personal Access Token


async def main():
    """Main demonstration function."""

    # Check if configuration is set
    if TOKEN == "your-personal-access-token":
        print("🚨 Configuration Required!")
        print("Please update the HOMEY_URL and TOKEN variables in this script.")
        print(f"Create a Personal Access Token at: {get_token_url(HOMEY_URL)}")
        return

    try:
        logger.info("🏠 Connecting to Homey...")

        # Create and connect to Homey using context manager
        client = await HomeyClient.create(base_url=HOMEY_URL, token=TOKEN, debug=True)

        async with client:
            logger.info("✅ Connected to Homey successfully!")

            # Get system information
            system_info = await client.get_system_info()
            logger.info(f"📊 System info: {system_info.get('name', 'Unknown')}")

            # Demonstrate device management
            await demo_devices(client)

            # Demonstrate zone management
            await demo_zones(client)

            # Demonstrate flow management
            await demo_flows(client)

            # Demonstrate app management
            await demo_apps(client)

            logger.info("🎉 Demo completed successfully!")

    except HomeyError as e:
        logger.error(f"❌ Homey error: {e.message}")
        if hasattr(e, "details") and e.details:
            logger.error(f"Details: {e.details}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")


async def demo_devices(client: HomeyClient):
    """Demonstrate device management."""
    logger.info("\n🔌 Device Management Demo")
    logger.info("=" * 50)

    try:
        # Get all devices
        devices = await client.devices.get_devices()
        logger.info(f"📱 Found {len(devices)} devices total")

        # Show first few devices
        for i, device in enumerate(devices[:3]):
            logger.info(f"  {i + 1}. {device.name} ({device.id})")
            logger.info(f"     Zone: {device.zoneName or 'No zone'}")
            logger.info(f"     Class: {device.class_ or 'Unknown'}")
            logger.info(f"     Online: {'✅' if device.is_online() else '❌'}")
            logger.info(f"     Capabilities: {', '.join(device.capabilities[:3])}...")

        # Get devices by category
        lights = await client.devices.get_devices_by_class("light")
        logger.info(f"💡 Found {len(lights)} lights")

        sensors = await client.devices.get_devices_by_class("sensor")
        logger.info(f"🌡️  Found {len(sensors)} sensors")

        # Get online/offline devices
        online_devices = await client.devices.get_online_devices()
        offline_devices = await client.devices.get_offline_devices()
        logger.info(
            f"📶 Online: {len(online_devices)}, Offline: {len(offline_devices)}"
        )

        # Example device control (if lights available)
        if lights:
            light = lights[0]
            logger.info(f"🔧 Testing control with: {light.name}")

            if light.has_capability("onoff"):
                # Check current state
                current_state = light.get_capability_value("onoff")
                logger.info(f"   Current state: {'On' if current_state else 'Off'}")

                # Toggle the light
                if light.id:
                    await client.devices.toggle(light.id)
                    logger.info("   🔄 Toggled light state")

                    # Wait a moment
                    await asyncio.sleep(1)

                    # Toggle again
                    await client.devices.toggle(light.id)
                    logger.info("   🔄 Toggled light state again")

            if light.has_capability("dim") and light.id:
                # Set brightness to 70%
                await client.devices.set_dim_level(light.id, 0.7)
                logger.info("   🔆 Set brightness to 70%")

    except Exception as e:
        logger.error(f"Device demo error: {e}")


async def demo_zones(client: HomeyClient):
    """Demonstrate zone management."""
    logger.info("\n🏠 Zone Management Demo")
    logger.info("=" * 50)

    try:
        # Get all zones
        zones = await client.zones.get_zones()
        logger.info(f"🏠 Found {len(zones)} zones total")

        # Show zone hierarchy
        root_zones = await client.zones.get_root_zones()
        logger.info(f"🏠 Root zones: {[z.name for z in root_zones]}")

        # Show zone details
        for zone in zones[:5]:  # Show first 5 zones
            logger.info(f"  📍 {zone.name} ({zone.id})")
            logger.info(f"     Active: {'✅' if zone.is_active() else '❌'}")
            logger.info(f"     Parent: {zone.parent or 'None'}")

            # Get devices in this zone
            if zone.id:
                zone_devices = await client.devices.get_devices_by_zone(zone.id)
            else:
                zone_devices = []
            logger.info(f"     Devices: {len(zone_devices)}")

        # Show active/inactive zones
        active_zones = await client.zones.get_active_zones()
        inactive_zones = await client.zones.get_inactive_zones()
        logger.info(f"📊 Active: {len(active_zones)}, Inactive: {len(inactive_zones)}")

    except Exception as e:
        logger.error(f"Zone demo error: {e}")


async def demo_flows(client: HomeyClient):
    """Demonstrate flow management."""
    logger.info("\n🔄 Flow Management Demo")
    logger.info("=" * 50)

    try:
        # Get all flows
        flows = await client.flows.get_flows()
        logger.info(f"🔄 Found {len(flows)} flows total")

        # Show flow categories
        enabled_flows = await client.flows.get_enabled_flows()
        disabled_flows = await client.flows.get_disabled_flows()
        broken_flows = await client.flows.get_broken_flows()
        advanced_flows = await client.flows.get_advanced_flows()

        logger.info(
            f"📊 Enabled: {len(enabled_flows)}, Disabled: {len(disabled_flows)}"
        )
        logger.info(f"📊 Broken: {len(broken_flows)}, Advanced: {len(advanced_flows)}")

        # Show first few flows
        for i, flow in enumerate(flows[:3]):
            status = "✅ Enabled" if flow.is_enabled() else "❌ Disabled"
            if flow.is_broken():
                status = "⚠️ Broken"

            logger.info(f"  {i + 1}. {flow.name} ({flow.id})")
            logger.info(f"     Status: {status}")
            logger.info(f"     Type: {'Advanced' if flow.is_advanced() else 'Basic'}")
            logger.info(f"     Executions: {flow.executionCount or 0}")

        # Show broken flows (if any)
        if broken_flows:
            logger.warning("⚠️ Broken flows found:")
            for flow in broken_flows:
                logger.warning(f"  - {flow.name}")

        # Get recently executed flows
        recent_flows = await client.flows.get_recently_executed_flows(3)
        if recent_flows:
            logger.info(f"🕐 Recently executed: {[f.name for f in recent_flows]}")

    except Exception as e:
        logger.error(f"Flow demo error: {e}")


async def demo_apps(client: HomeyClient):
    """Demonstrate app management."""
    logger.info("\n📱 App Management Demo")
    logger.info("=" * 50)

    try:
        # Get all apps
        apps = await client.apps.get_apps()
        logger.info(f"📱 Found {len(apps)} apps total")

        # Show app categories
        running_apps = await client.apps.get_running_apps()
        crashed_apps = await client.apps.get_crashed_apps()
        enabled_apps = await client.apps.get_enabled_apps()

        logger.info(f"📊 Running: {len(running_apps)}, Crashed: {len(crashed_apps)}")
        logger.info(f"📊 Enabled: {len(enabled_apps)}")

        # Show first few apps
        for i, app in enumerate(apps[:5]):
            status = "✅ Running" if app.is_running() else "❌ Stopped"
            if app.is_crashed():
                status = "💥 Crashed"

            logger.info(f"  {i + 1}. {app.name} ({app.id})")
            logger.info(f"     Status: {status}")
            logger.info(f"     Version: {app.version or 'Unknown'}")
            logger.info(f"     Origin: {app.origin or 'Unknown'}")

        # Show crashed apps (if any)
        if crashed_apps:
            logger.warning("💥 Crashed apps found:")
            for app in crashed_apps:
                logger.warning(f"  - {app.name}")

        # Get app categories
        categories = await client.apps.get_app_categories()
        logger.info(f"📂 App categories: {', '.join(categories[:5])}...")

    except Exception as e:
        logger.error(f"App demo error: {e}")


if __name__ == "__main__":
    print("🚀 Python Homey Library Demo")
    print("=" * 50)
    print("This script demonstrates the python-homey library capabilities.")
    print("Make sure to update the configuration at the top of this file!\n")

    # Run the demo
    asyncio.run(main())
