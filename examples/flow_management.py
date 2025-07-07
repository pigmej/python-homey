"""
Flow Management Example for python-homey library.

This example demonstrates how to work with flows in your Homey.
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

            # Get all flows
            flows = await client.flows.get_flows()
            logger.info(f"🔄 Found {len(flows)} flows total")

            # Show flow statistics
            enabled_flows = await client.flows.get_enabled_flows()
            disabled_flows = await client.flows.get_disabled_flows()
            broken_flows = await client.flows.get_broken_flows()
            advanced_flows = await client.flows.get_advanced_flows()

            logger.info("📊 Flow Statistics:")
            logger.info(f"  ✅ Enabled: {len(enabled_flows)}")
            logger.info(f"  ❌ Disabled: {len(disabled_flows)}")
            logger.info(f"  ⚠️ Broken: {len(broken_flows)}")
            logger.info(f"  🔧 Advanced: {len(advanced_flows)}")

            # Show first few flows with details
            logger.info("\n📋 Flow Details:")
            for i, flow in enumerate(flows[:5]):
                status_icon = "✅" if flow.is_enabled() else "❌"
                if flow.is_broken():
                    status_icon = "⚠️"

                flow_type = "Advanced" if flow.is_advanced() else "Basic"
                executions = flow.executionCount or 0

                logger.info(f"  {i + 1}. {status_icon} {flow.name}")
                logger.info(f"     Type: {flow_type}, Executions: {executions}")

                # Show trigger, conditions, and actions count
                conditions_count = len(flow.get_conditions())
                actions_count = len(flow.get_actions())
                logger.info(
                    f"     Structure: 1 trigger → {conditions_count} conditions → {actions_count} actions"
                )

            # Show broken flows (if any)
            if broken_flows:
                logger.warning(f"\n⚠️ Found {len(broken_flows)} broken flows:")
                for flow in broken_flows:
                    logger.warning(f"  - {flow.name} (ID: {flow.id})")

            # Show recently executed flows
            recent_flows = await client.flows.get_recently_executed_flows(5)
            if recent_flows:
                logger.info("\n🕐 Recently executed flows:")
                for flow in recent_flows:
                    logger.info(
                        f"  - {flow.name} (executed {flow.executionCount} times)"
                    )

            # Show most executed flows
            popular_flows = await client.flows.get_most_executed_flows(5)
            if popular_flows:
                logger.info("\n🔥 Most executed flows:")
                for flow in popular_flows:
                    logger.info(f"  - {flow.name} ({flow.executionCount} executions)")

            # Example: Create a test flow (commented out to avoid creating actual flows)
            """
            logger.info("\n🆕 Creating a test flow...")
            test_flow = await client.flows.create_flow(
                name="Test Flow from Python",
                enabled=False  # Create disabled so it doesn't actually run
            )
            logger.info(f"✅ Created flow: {test_flow.name} (ID: {test_flow.id})")

            # Update the flow
            updated_flow = await client.flows.update_flow(
                test_flow.id,
                name="Updated Test Flow from Python"
            )
            logger.info(f"✏️ Updated flow name to: {updated_flow.name}")

            # Delete the test flow
            await client.flows.delete_flow(test_flow.id)
            logger.info("🗑️ Deleted test flow")
            """

            # Example: Enable/disable flows (commented out to avoid changing actual flows)
            """
            if disabled_flows:
                # Enable the first disabled flow
                flow = disabled_flows[0]
                logger.info(f"🔄 Enabling flow: {flow.name}")
                await client.flows.enable_flow(flow.id)
                logger.info("✅ Flow enabled")

                # Wait a moment, then disable it again
                await asyncio.sleep(1)
                await client.flows.disable_flow(flow.id)
                logger.info("❌ Flow disabled again")
            """

            # Example: Trigger a flow manually (commented out to avoid triggering actual flows)
            """
            if enabled_flows:
                # Find a simple flow to trigger
                simple_flow = None
                for flow in enabled_flows:
                    if not flow.is_broken() and not flow.is_advanced():
                        simple_flow = flow
                        break

                if simple_flow:
                    logger.info(f"🚀 Triggering flow: {simple_flow.name}")
                    await client.flows.trigger_flow(simple_flow.id)
                    logger.info("✅ Flow triggered successfully")
            """

            # Flow folders
            try:
                folders = await client.flows.get_flow_folders()
                logger.info(f"\n📁 Found {len(folders)} flow folders")
                for folder in folders:
                    folder_flows = await client.flows.get_flows_by_folder(
                        folder.get("id", "")
                    )
                    logger.info(
                        f"  - {folder.get('name', 'Unknown')}: {len(folder_flows)} flows"
                    )

                # Flows without folders
                orphan_flows = await client.flows.get_flows_without_folder()
                logger.info(f"  - (No folder): {len(orphan_flows)} flows")
            except Exception:
                logger.info("📁 Flow folders not available or accessible")

            # Search flows
            if flows:
                # Search for flows containing "light"
                light_flows = await client.flows.search_flows("light")
                logger.info(f"\n🔍 Found {len(light_flows)} flows containing 'light'")

                # Search for flows containing "motion"
                motion_flows = await client.flows.search_flows("motion")
                logger.info(f"🔍 Found {len(motion_flows)} flows containing 'motion'")

            # Flow export/import example (commented out)
            """
            if flows:
                # Export the first flow
                flow = flows[0]
                logger.info(f"📤 Exporting flow: {flow.name}")
                exported_data = await client.flows.export_flow(flow.id)
                logger.info(f"✅ Exported flow data (size: {len(str(exported_data))} chars)")

                # You could save this data and import it later:
                # imported_flow = await client.flows.import_flow(exported_data)
            """

            logger.info("\n🎉 Flow management example completed!")

    except HomeyError as e:
        logger.error(f"❌ Homey error: {e.message}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")


async def flow_monitoring_example(client: HomeyClient):
    """Example of monitoring flow executions in real-time."""
    logger.info("\n👁️ Starting flow monitoring (10 seconds)...")

    # Set up event handler for flow events
    async def on_flow_event(event_data):
        logger.info(f"🔄 Flow event: {event_data}")

    # Register the event handler
    client.on("flow", on_flow_event)

    # Monitor for 10 seconds
    await asyncio.sleep(10)

    # Remove the event handler
    client.off("flow")
    logger.info("👁️ Flow monitoring stopped")


async def flow_statistics_example(client: HomeyClient):
    """Example of gathering detailed flow statistics."""
    logger.info("\n📊 Gathering detailed flow statistics...")

    flows = await client.flows.get_flows()

    # Count flows by type
    basic_count = len([f for f in flows if not f.is_advanced()])
    advanced_count = len([f for f in flows if f.is_advanced()])

    # Count by status
    enabled_count = len([f for f in flows if f.is_enabled()])
    disabled_count = len([f for f in flows if not f.is_enabled()])
    broken_count = len([f for f in flows if f.is_broken()])

    # Execution statistics
    total_executions = sum(f.executionCount or 0 for f in flows)
    executed_flows = [f for f in flows if (f.executionCount or 0) > 0]
    avg_executions = total_executions / len(executed_flows) if executed_flows else 0

    logger.info("📊 Flow Statistics Summary:")
    logger.info(f"  Total flows: {len(flows)}")
    logger.info(f"  Basic: {basic_count}, Advanced: {advanced_count}")
    logger.info(
        f"  Enabled: {enabled_count}, Disabled: {disabled_count}, Broken: {broken_count}"
    )
    logger.info(f"  Total executions: {total_executions}")
    logger.info(f"  Flows with executions: {len(executed_flows)}")
    logger.info(f"  Average executions per active flow: {avg_executions:.1f}")


if __name__ == "__main__":
    print("🔄 Flow Management Example")
    print("=" * 50)
    asyncio.run(main())
