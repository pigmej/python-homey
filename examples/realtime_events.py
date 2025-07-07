"""
Real-time Events Example for python-homey library.

This example demonstrates how to listen to real-time events from your Homey,
such as device state changes, zone activity, flow executions, and more.
"""

import asyncio
import logging
from datetime import datetime
from homey import HomeyClient, HomeyError
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

HOMEY_URL = os.getenv("HOMEY_API_URL", "http://localhost")
TOKEN = os.getenv("HOMEY_API_TOKEN", "make-it-real-token")


class HomeyEventMonitor:
    """Event monitor for Homey real-time events."""

    def __init__(self):
        self.event_count = 0
        self.device_events = 0
        self.zone_events = 0
        self.flow_events = 0
        self.app_events = 0
        self.start_time = datetime.now()

    async def on_device_event(self, event_data):
        """Handle device events."""
        self.device_events += 1
        self.event_count += 1

        timestamp = datetime.now().strftime("%H:%M:%S")
        device_id = event_data.get("id", "unknown")
        device_name = event_data.get("name", "Unknown Device")

        logger.info(f"🔌 [{timestamp}] Device Event: {device_name} ({device_id})")

        # Log capability changes
        if "capabilities" in event_data:
            capabilities = event_data["capabilities"]
            for cap_id, cap_data in capabilities.items():
                if isinstance(cap_data, dict) and "value" in cap_data:
                    value = cap_data["value"]
                    logger.info(f"   📊 {cap_id}: {value}")

    async def on_zone_event(self, event_data):
        """Handle zone events."""
        self.zone_events += 1
        self.event_count += 1

        timestamp = datetime.now().strftime("%H:%M:%S")
        zone_id = event_data.get("id", "unknown")
        zone_name = event_data.get("name", "Unknown Zone")

        logger.info(f"🏠 [{timestamp}] Zone Event: {zone_name} ({zone_id})")

        # Log zone activity changes
        if "active" in event_data:
            active = event_data["active"]
            status = "🟢 Active" if active else "🔴 Inactive"
            logger.info(f"   {status}")

    async def on_flow_event(self, event_data):
        """Handle flow events."""
        self.flow_events += 1
        self.event_count += 1

        timestamp = datetime.now().strftime("%H:%M:%S")
        flow_id = event_data.get("id", "unknown")
        flow_name = event_data.get("name", "Unknown Flow")

        logger.info(f"🔄 [{timestamp}] Flow Event: {flow_name} ({flow_id})")

        # Log flow state changes
        if "enabled" in event_data:
            enabled = event_data["enabled"]
            status = "✅ Enabled" if enabled else "❌ Disabled"
            logger.info(f"   {status}")

        if "lastExecuted" in event_data:
            logger.info("   🚀 Flow executed")

    async def on_app_event(self, event_data):
        """Handle app events."""
        self.app_events += 1
        self.event_count += 1

        timestamp = datetime.now().strftime("%H:%M:%S")
        app_id = event_data.get("id", "unknown")
        app_name = event_data.get("name", "Unknown App")

        logger.info(f"📱 [{timestamp}] App Event: {app_name} ({app_id})")

        # Log app state changes
        if "state" in event_data:
            state = event_data["state"]
            logger.info(f"   State: {state}")

    async def on_generic_event(self, event_data):
        """Handle any other events."""
        self.event_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        logger.info(f"📡 [{timestamp}] Generic Event: {event_data}")

    def print_statistics(self):
        """Print event statistics."""
        runtime = datetime.now() - self.start_time
        runtime_seconds = runtime.total_seconds()

        logger.info(f"\n📊 Event Statistics (Runtime: {runtime_seconds:.1f}s)")
        logger.info(f"  Total events: {self.event_count}")
        logger.info(f"  Device events: {self.device_events}")
        logger.info(f"  Zone events: {self.zone_events}")
        logger.info(f"  Flow events: {self.flow_events}")
        logger.info(f"  App events: {self.app_events}")
        logger.info(
            f"  Events per minute: {(self.event_count / runtime_seconds * 60):.1f}"
        )


async def main():
    """Main example function."""
    if TOKEN == "your-personal-access-token":
        print("❌ Please update the HOMEY_URL and TOKEN variables!")
        return

    try:
        client = await HomeyClient.create(base_url=HOMEY_URL, token=TOKEN)

        async with client:
            logger.info("✅ Connected to Homey!")

            # Connect to WebSocket for real-time events
            try:
                await client.connect_websocket(auto_reconnect=True)
                logger.info("🔌 WebSocket connected for real-time events")
            except Exception as ws_error:
                logger.error(f"❌ WebSocket connection failed: {ws_error}")
                logger.info("💡 Continuing without real-time events")
                return

            # Create event monitor
            monitor = HomeyEventMonitor()

            # Register event handlers
            client.on("device", monitor.on_device_event)
            client.on("zone", monitor.on_zone_event)
            client.on("flow", monitor.on_flow_event)
            client.on("app", monitor.on_app_event)

            # You can also register a generic handler for all events
            # client.on("*", monitor.on_generic_event)

            logger.info("👂 Listening for real-time events...")
            logger.info(
                "💡 Try changing device states, triggering flows, or moving around your home!"
            )
            logger.info("⏱️  Monitoring for 60 seconds...")

            # Listen for events for 60 seconds
            await asyncio.sleep(60)

            # Remove event handlers
            client.off("device")
            client.off("zone")
            client.off("flow")
            client.off("app")

            # Disconnect WebSocket
            await client.disconnect_websocket()

            # Print statistics
            monitor.print_statistics()

            logger.info("🎉 Real-time events example completed!")

    except HomeyError as e:
        logger.error(f"❌ Homey error: {e.message}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")


async def device_monitoring_example():
    """Example focused on device monitoring."""
    if TOKEN == "your-personal-access-token":
        print("❌ Please update the HOMEY_URL and TOKEN variables!")
        return

    try:
        client = await HomeyClient.create(base_url=HOMEY_URL, token=TOKEN)

        async with client:
            logger.info("🔌 Starting device monitoring...")

            # Connect to WebSocket for real-time events
            try:
                await client.connect_websocket(auto_reconnect=True)
                logger.info("🔌 WebSocket connected for device monitoring")
            except Exception as ws_error:
                logger.error(f"❌ WebSocket connection failed: {ws_error}")
                logger.info("💡 Cannot monitor device changes without WebSocket")
                return

            # Get initial device states
            devices = await client.devices.get_devices()
            logger.info(f"📱 Monitoring {len(devices)} devices")

            # Track device state changes
            device_states = {}
            for device in devices:
                device_states[device.id] = {"name": device.name, "capabilities": {}}
                for cap_id in device.capabilities:
                    value = device.get_capability_value(cap_id)
                    device_states[device.id]["capabilities"][cap_id] = value

            async def on_device_change(event_data):
                device_id = event_data.get("id")
                if device_id in device_states:
                    device_name = device_states[device_id]["name"]
                    logger.info(f"🔄 {device_name} changed:")

                    # Check for capability changes
                    if "capabilities" in event_data:
                        new_caps = event_data["capabilities"]
                        old_caps = device_states[device_id]["capabilities"]

                        for cap_id, cap_data in new_caps.items():
                            if isinstance(cap_data, dict) and "value" in cap_data:
                                new_value = cap_data["value"]
                                old_value = old_caps.get(cap_id)

                                if new_value != old_value:
                                    logger.info(
                                        f"   {cap_id}: {old_value} → {new_value}"
                                    )
                                    device_states[device_id]["capabilities"][cap_id] = (
                                        new_value
                                    )

            client.on("device", on_device_change)

            logger.info("👁️  Monitoring device changes for 30 seconds...")
            await asyncio.sleep(30)

            client.off("device")
            await client.disconnect_websocket()
            logger.info("🔌 Device monitoring stopped")

    except HomeyError as e:
        logger.error(f"❌ Homey error: {e.message}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")


async def zone_activity_monitoring():
    """Example focused on zone activity monitoring."""
    if TOKEN == "your-personal-access-token":
        print("❌ Please update the HOMEY_URL and TOKEN variables!")
        return

    try:
        client = await HomeyClient.create(base_url=HOMEY_URL, token=TOKEN)

        async with client:
            logger.info("🏠 Starting zone activity monitoring...")

            # Connect to WebSocket for real-time events
            try:
                await client.connect_websocket(auto_reconnect=True)
                logger.info("🔌 WebSocket connected for zone monitoring")
            except Exception as ws_error:
                logger.error(f"❌ WebSocket connection failed: {ws_error}")
                logger.info("💡 Cannot monitor zone activity without WebSocket")
                return

            # Get zones
            zones = await client.zones.get_zones()
            logger.info(f"📍 Monitoring {len(zones)} zones")

            # Track zone activity
            zone_activity = {}
            for zone in zones:
                zone_activity[zone.id] = {
                    "name": zone.name,
                    "active": zone.active,
                    "activity_count": 0,
                }
                logger.info(
                    f"   {zone.name}: {'🟢 Active' if zone.active else '🔴 Inactive'}"
                )

            async def on_zone_activity(event_data):
                zone_id = event_data.get("id")
                if zone_id in zone_activity:
                    zone_name = zone_activity[zone_id]["name"]

                    if "active" in event_data:
                        new_active = event_data["active"]
                        old_active = zone_activity[zone_id]["active"]

                        if new_active != old_active:
                            zone_activity[zone_id]["active"] = new_active
                            zone_activity[zone_id]["activity_count"] += 1

                            status = (
                                "🟢 became active"
                                if new_active
                                else "🔴 became inactive"
                            )
                            count = zone_activity[zone_id]["activity_count"]
                            logger.info(f"🏠 {zone_name} {status} (change #{count})")

            client.on("zone", on_zone_activity)

            logger.info("👁️  Monitoring zone activity for 45 seconds...")
            logger.info("🚶 Try moving around your home to trigger motion sensors!")
            await asyncio.sleep(45)

            client.off("zone")
            await client.disconnect_websocket()

            # Print activity summary
            logger.info("\n📊 Zone Activity Summary:")
            for zone_data in zone_activity.values():
                count = zone_data["activity_count"]
                status = "🟢 Active" if zone_data["active"] else "🔴 Inactive"
                logger.info(
                    f"   {zone_data['name']}: {count} changes, currently {status}"
                )

    except HomeyError as e:
        logger.error(f"❌ Homey error: {e.message}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")


async def flow_execution_monitoring():
    """Example focused on monitoring flow executions."""
    if TOKEN == "your-personal-access-token":
        print("❌ Please update the HOMEY_URL and TOKEN variables!")
        return

    try:
        client = await HomeyClient.create(base_url=HOMEY_URL, token=TOKEN)

        async with client:
            logger.info("🔄 Starting flow execution monitoring...")

            # Connect to WebSocket for real-time events
            try:
                await client.connect_websocket(auto_reconnect=True)
                logger.info("🔌 WebSocket connected for flow monitoring")
            except Exception as ws_error:
                logger.error(f"❌ WebSocket connection failed: {ws_error}")
                logger.info("💡 Cannot monitor flow executions without WebSocket")
                return

            # Track flow executions
            flow_executions = {}

            async def on_flow_execution(event_data):
                flow_id = event_data.get("id", "unknown")
                flow_name = event_data.get("name", "Unknown Flow")

                if flow_id not in flow_executions:
                    flow_executions[flow_id] = {"name": flow_name, "execution_count": 0}

                if "lastExecuted" in event_data:
                    flow_executions[flow_id]["execution_count"] += 1
                    count = flow_executions[flow_id]["execution_count"]
                    logger.info(f"🚀 Flow executed: {flow_name} (#{count})")

            client.on("flow", on_flow_execution)

            logger.info("👁️  Monitoring flow executions for 30 seconds...")
            logger.info("🔄 Try triggering some flows manually or through automation!")
            await asyncio.sleep(30)

            client.off("flow")
            await client.disconnect_websocket()

            # Print execution summary
            if flow_executions:
                logger.info("\n📊 Flow Execution Summary:")
                for flow_data in flow_executions.values():
                    count = flow_data["execution_count"]
                    logger.info(f"   {flow_data['name']}: {count} executions")
            else:
                logger.info("\n📊 No flow executions detected during monitoring period")

    except HomeyError as e:
        logger.error(f"❌ Homey error: {e.message}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    print("📡 Real-time Events Example")
    print("=" * 50)
    print("This example will monitor your Homey for real-time events.")
    print("Make sure to interact with your devices during the monitoring period!")
    print()

    # Run the main example
    asyncio.run(main())

    # Uncomment to run specific monitoring examples
    # print("\n" + "="*50)
    # asyncio.run(device_monitoring_example())

    # print("\n" + "="*50)
    # asyncio.run(zone_activity_monitoring())

    # print("\n" + "="*50)
    # asyncio.run(flow_execution_monitoring())
