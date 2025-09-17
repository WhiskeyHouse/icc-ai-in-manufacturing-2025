# Bad Script Example - Multiple Validation Issues
# Missing proper error handling, logging, and safety measures

import system

def startProduction():
    # No error handling - VIOLATION
    # No WHK logging - VIOLATION  
    # Using unsafe tag.write instead of writeBlocking - VIOLATION
    # No audit logging for production operation - VIOLATION
    
    # Read some values
    temperature = system.tag.read("[default]Tank/Temperature").value
    
    # Unsafe tag write without error handling
    system.tag.write("[default]Production/Start"], [True])
    
    # Basic print instead of proper logging
    print("Production started")
    
    # No audit trail for batch operations
    if temperature > 80:
        system.tag.write("[default]Production/Stop"], [True])
        print("Temperature too high, stopping")

# Execute without proper structure
startProduction()