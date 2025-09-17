"""
Whiskey Lab Demo Tag Management
Provides functions to initialize and manage demo tags for the AI Whiskey Lab Assistant
"""

import system.tag
import system.date

# Tag path constants to avoid duplication
TAG_TANK1_TEMPERATURE = "[Global]WhiskeyLab/Tank1/Temperature"
TAG_TANK1_FILL_LEVEL = "[Global]WhiskeyLab/Tank1/FillLevel"
TAG_TANK1_STATUS = "[Global]WhiskeyLab/Tank1/Status"
TAG_AI_CONFIDENCE = "[Global]WhiskeyLab/AI/Confidence"
TAG_AI_CURRENT_MESSAGE = "[Global]WhiskeyLab/AI/CurrentMessage"
TAG_AI_CURRENT_LOG_ENTRY = "[Global]WhiskeyLab/AI/CurrentLogEntry"
TAG_AI_LAST_ACTION = "[Global]WhiskeyLab/AI/LastAction"
TAG_AI_LAST_ACTION_TIME = "[Global]WhiskeyLab/AI/LastActionTime"
TAG_AI_NEXT_STEP_PROMPT = "[Global]WhiskeyLab/AI/NextStepPrompt"


def initialize_demo_tags():
    """Initialize all tags needed for the Whiskey Lab AI demo."""

    # Define the tag structure
    tag_configs = [
        # Tank 1 Process Variables
        {
            "name": TAG_TANK1_TEMPERATURE,
            "dataType": "Float4",
            "value": 75.0,
            "documentation": "Tank 1 temperature in Fahrenheit",
        },
        {
            "name": TAG_TANK1_FILL_LEVEL,
            "dataType": "Float4",
            "value": 45.0,
            "documentation": "Tank 1 fill level percentage",
        },
        {
            "name": TAG_TANK1_STATUS,
            "dataType": "String",
            "value": "OK",
            "documentation": "Tank 1 status: OK, Warning, Error, STOPPED",
        },
        # AI System Variables
        {
            "name": TAG_AI_CONFIDENCE,
            "dataType": "Int4",
            "value": 85,
            "documentation": "AI confidence level (0-100%)",
        },
        {
            "name": TAG_AI_CURRENT_MESSAGE,
            "dataType": "String",
            "value": "System initialized. Ready to monitor whiskey production process.",
            "documentation": "Current AI message to operator",
        },
        {
            "name": TAG_AI_CURRENT_LOG_ENTRY,
            "dataType": "String",
            "value": "✅ [12:00:00] System initialized - All parameters nominal",
            "documentation": "Current log entry for AI decisions",
        },
        {
            "name": TAG_AI_LAST_ACTION,
            "dataType": "String",
            "value": "INITIALIZED",
            "documentation": "Last operator action: ACCEPTED, OVERRIDDEN, RESET, INITIALIZED",
        },
        {
            "name": TAG_AI_LAST_ACTION_TIME,
            "dataType": "DateTime",
            "value": system.date.now(),
            "documentation": "Timestamp of last operator action",
        },
        {
            "name": TAG_AI_NEXT_STEP_PROMPT,
            "dataType": "String",
            "value": "Monitoring Tank 1 for stability...",
            "documentation": "Next step prompt displayed in status bar",
        },
    ]

    # Create the tags
    created_tags = []
    for tag_config in tag_configs:
        try:
            # Check if tag already exists
            existing_value = system.tag.readBlocking([tag_config["name"]])
            if existing_value[0].quality.isGood():
                print("Tag already exists: " + tag_config["name"])
                continue
        except Exception:
            pass  # Tag doesn't exist, we'll create it

        # Create the tag
        tag_path = tag_config["name"]
        data_type = tag_config["dataType"]
        initial_value = tag_config["value"]
        documentation = tag_config.get("documentation", "")

        # Use system.tag.configure to create the tag
        tag_def = {
            "name": tag_path,
            "tagType": "AtomicTag",
            "dataType": data_type,
            "value": initial_value,
            "documentation": documentation,
        }

        try:
            system.tag.configure("", [tag_def], "o")
            created_tags.append(tag_path)
            print("Created tag: " + tag_path)
        except Exception as e:
            print("Failed to create tag " + tag_path + ": " + str(e))

    return created_tags


def start_demo_simulation():
    """Start the demo simulation with realistic process variations."""

    # This would typically be called from a timer script or gateway event
    import random

    # Get current values
    current_temp = system.tag.readBlocking([TAG_TANK1_TEMPERATURE])[0].value
    current_fill = system.tag.readBlocking([TAG_TANK1_FILL_LEVEL])[0].value
    current_confidence = system.tag.readBlocking([TAG_AI_CONFIDENCE])[0].value

    # Simulate temperature variation (±2 degrees)
    temp_variation = random.uniform(-1.0, 1.0)
    new_temp = max(70.0, min(85.0, current_temp + temp_variation))

    # Simulate fill level change (slow increase during production)
    fill_variation = random.uniform(0.0, 0.5)
    new_fill = max(0.0, min(100.0, current_fill + fill_variation))

    # Adjust AI confidence based on temperature
    if new_temp > 80:
        new_confidence = max(50, current_confidence - 5)
        status = "Warning"
        message = "Temperature elevated. Monitoring closely and preparing cooling intervention."
    elif new_temp < 72:
        new_confidence = max(60, current_confidence - 2)
        status = "Warning"
        message = "Temperature below optimal range. Adjusting heating parameters."
    else:
        new_confidence = min(95, current_confidence + 1)
        status = "OK"
        message = "All parameters within optimal range. Process running smoothly."

    # Update tags
    updates = [
        (TAG_TANK1_TEMPERATURE, new_temp),
        (TAG_TANK1_FILL_LEVEL, new_fill),
        (TAG_TANK1_STATUS, status),
        (TAG_AI_CONFIDENCE, new_confidence),
        (TAG_AI_CURRENT_MESSAGE, message),
    ]

    tag_paths = [update[0] for update in updates]
    values = [update[1] for update in updates]

    try:
        system.tag.writeBlocking(tag_paths, values)

        # Add a log entry if there's a significant change
        if abs(temp_variation) > 0.5 or new_confidence != current_confidence:
            timestamp = system.date.format(system.date.now(), "HH:mm:ss")
            if new_temp > 80:
                log_entry = (
                    "⚠️ ["
                    + timestamp
                    + "] Temperature rising to "
                    + str(round(new_temp, 1))
                    + "°F - AI evaluating cooling options"
                )
            elif new_temp < 72:
                log_entry = (
                    "⚠️ ["
                    + timestamp
                    + "] Temperature dropping to "
                    + str(round(new_temp, 1))
                    + "°F - AI adjusting heating"
                )
            else:
                log_entry = (
                    "✅ ["
                    + timestamp
                    + "] Process stable at "
                    + str(round(new_temp, 1))
                    + "°F - Confidence: "
                    + str(new_confidence)
                    + "%"
                )

            system.tag.writeBlocking([TAG_AI_CURRENT_LOG_ENTRY], [log_entry])

    except Exception as e:
        print("Error updating simulation tags: " + str(e))


def reset_demo_to_defaults():
    """Reset all demo tags to their default values."""

    defaults = [
        (TAG_TANK1_TEMPERATURE, 75.0),
        (TAG_TANK1_FILL_LEVEL, 45.0),
        (TAG_TANK1_STATUS, "OK"),
        (TAG_AI_CONFIDENCE, 85),
        (TAG_AI_CURRENT_MESSAGE, "System reset complete. Ready for operation."),
        (
            TAG_AI_CURRENT_LOG_ENTRY,
            "🔄 System reset - All parameters restored to defaults",
        ),
        (TAG_AI_LAST_ACTION, "RESET"),
        (TAG_AI_LAST_ACTION_TIME, system.date.now()),
        (TAG_AI_NEXT_STEP_PROMPT, "Monitoring Tank 1 for stability..."),
    ]

    tag_paths = [item[0] for item in defaults]
    values = [item[1] for item in defaults]

    try:
        system.tag.writeBlocking(tag_paths, values)
        print("Demo reset to default values")
        return True
    except Exception as e:
        print("Error resetting demo: " + str(e))
        return False


def get_demo_status():
    """Get current status of all demo tags."""

    tag_paths = [
        TAG_TANK1_TEMPERATURE,
        TAG_TANK1_FILL_LEVEL,
        TAG_TANK1_STATUS,
        TAG_AI_CONFIDENCE,
        TAG_AI_CURRENT_MESSAGE,
        TAG_AI_LAST_ACTION,
    ]

    try:
        values = system.tag.readBlocking(tag_paths)
        status = {}
        for i, tag_path in enumerate(tag_paths):
            tag_name = tag_path.split("/")[-1]
            status[tag_name] = {
                "value": values[i].value,
                "quality": str(values[i].quality),
                "timestamp": values[i].timestamp,
            }
        return status
    except Exception as e:
        print("Error reading demo status: " + str(e))
        return None


# Demo scenario functions for conference presentation
def demo_scenario_temperature_spike():
    """Simulate a temperature spike scenario for demo."""

    # Simulate overheating
    system.tag.writeBlocking([TAG_TANK1_TEMPERATURE], [82.5])
    system.tag.writeBlocking([TAG_TANK1_STATUS], ["Warning"])
    system.tag.writeBlocking([TAG_AI_CONFIDENCE], [65])

    timestamp = system.date.format(system.date.now(), "HH:mm:ss")
    message = "ALERT: Temperature spike detected! Should we activate emergency cooling?"
    log_entry = (
        "⚠️ ["
        + timestamp
        + "] Temperature spike to 82.5°F - Emergency cooling recommended"
    )

    system.tag.writeBlocking(
        [TAG_AI_CURRENT_MESSAGE, TAG_AI_CURRENT_LOG_ENTRY, TAG_AI_NEXT_STEP_PROMPT],
        [message, log_entry, "Awaiting operator decision on emergency cooling..."],
    )


def demo_scenario_normal_operation():
    """Return to normal operation scenario."""

    system.tag.writeBlocking([TAG_TANK1_TEMPERATURE], [76.0])
    system.tag.writeBlocking([TAG_TANK1_STATUS], ["OK"])
    system.tag.writeBlocking([TAG_AI_CONFIDENCE], [92])

    timestamp = system.date.format(system.date.now(), "HH:mm:ss")
    message = "Excellent! Temperature stabilized. Process optimization in progress."
    log_entry = (
        "✅ ["
        + timestamp
        + "] Temperature normalized to 76°F - Process optimization active"
    )

    system.tag.writeBlocking(
        [TAG_AI_CURRENT_MESSAGE, TAG_AI_CURRENT_LOG_ENTRY, TAG_AI_NEXT_STEP_PROMPT],
        [message, log_entry, "Optimizing process parameters for maximum efficiency..."],
    )
