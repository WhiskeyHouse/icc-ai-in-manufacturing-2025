"""Bad Script Example - Demonstrates validation violations."""

import system


def start_production():
    # Missing try/except error handling (SCRIPT-001)
    # No WHK logging (SCRIPT-002)
    # Unsafe tag.write usage (SCRIPT-003)
    # Missing audit trail (SCRIPT-004)

    temperature = system.tag.read("[default]Tank/Temperature").value

    system.tag.write("[default]Production/Start", True)
    print("Production started")

    if temperature > 80:
        system.tag.write("[default]Production/Stop", True)
        print("Temperature too high, stopping")


start_production()

non_existent_func("hi")

# Non existent system func
system.util.fetchCoffee()