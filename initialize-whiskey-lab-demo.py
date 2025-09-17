#!/usr/bin/env python3
"""
Whiskey Lab Demo Initialization Script

This script helps initialize the AI Whiskey Lab Assistant demo by creating
the necessary tags and setting up initial values.

Run this script from the Ignition Designer Script Console or as a startup script.
"""


def main():
    """Main initialization function."""

    print("🥃 Initializing AI Whiskey Lab Assistant Demo...")
    print("=" * 50)

    try:
        # Import the demo module
        import whk.whiskey_lab_demo as demo

        # Initialize demo tags
        print("Creating demo tags...")
        created_tags = demo.initialize_demo_tags()

        if created_tags:
            print(f"✅ Successfully created {len(created_tags)} tags:")
            for tag in created_tags:
                print(f"   - {tag}")
        else:
            print("ℹ️  All tags already exist")

        # Reset to default values
        print("\nResetting to default values...")
        if demo.reset_demo_to_defaults():
            print("✅ Demo reset successful")
        else:
            print("❌ Demo reset failed")

        # Show current status
        print("\nCurrent demo status:")
        status = demo.get_demo_status()
        if status:
            for tag_name, info in status.items():
                print(f"   {tag_name}: {info['value']} (Quality: {info['quality']})")

        print("\n" + "=" * 50)
        print("🎉 Demo initialization complete!")
        print("\nTo access the demo:")
        print("1. Open Perspective Workstation")
        print("2. Navigate to: http://localhost:9088/data/perspective/client/Global")
        print("3. The AI Whiskey Lab Assistant should load automatically")
        print("\nDemo scenarios available:")
        print("- demo.demo_scenario_temperature_spike() - Simulate overheating")
        print("- demo.demo_scenario_normal_operation() - Return to normal")
        print("- demo.start_demo_simulation() - Start realistic variations")

    except ImportError as e:
        print(f"❌ Error importing demo module: {e}")
        print(
            "Make sure the whk.whiskey_lab_demo module is available in the Global project"
        )

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
