#!/bin/bash
set -euo pipefail

### Custom logic for gateway configuration

# Function to wait for Ignition to be ready
wait_for_ignition() {
    echo "Waiting for Ignition to be ready..."
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if [ -f "${IGNITION_INSTALL_LOCATION}/data/db/config.idb" ]; then
            echo "Ignition database found, gateway is initializing..."
            return 0
        fi
        sleep 5
        attempt=$((attempt + 1))
    done
    
    echo "Timeout waiting for Ignition to initialize"
    return 1
}

# Set up admin username and password if provided
setup_admin_credentials() {
    if [ -n "${GATEWAY_ADMIN_USERNAME:-}" ]; then
        echo "Setting up admin username: ${GATEWAY_ADMIN_USERNAME}"
        
        # Check if password file is provided
        if [ -n "${GATEWAY_ADMIN_PASSWORD_FILE:-}" ] && [ -f "${GATEWAY_ADMIN_PASSWORD_FILE}" ]; then
            echo "Using password from file: ${GATEWAY_ADMIN_PASSWORD_FILE}"
            export GATEWAY_ADMIN_PASSWORD=$(<"${GATEWAY_ADMIN_PASSWORD_FILE}")
        fi
        
        # If we have both username and password, set them
        if [ -n "${GATEWAY_ADMIN_PASSWORD:-}" ]; then
            # Create a temporary file for the password
            TEMP_PASSWORD_FILE="/tmp/admin_password.txt"
            echo "${GATEWAY_ADMIN_PASSWORD}" > "${TEMP_PASSWORD_FILE}"
            
            # Register the password using the existing script if available
            if [ -f "/usr/local/bin/register-password.sh" ]; then
                echo "Registering admin credentials..."
                /usr/local/bin/register-password.sh \
                    -u "${GATEWAY_ADMIN_USERNAME}" \
                    -f "${TEMP_PASSWORD_FILE}" \
                    -d "${IGNITION_INSTALL_LOCATION}/data/db/config.idb" || true
            fi
            
            # Clean up
            rm -f "${TEMP_PASSWORD_FILE}"
        fi
    fi
}

# Skip commissioning if requested
handle_commissioning() {
    if [ "${GATEWAY_SKIP_COMMISSIONING:-false}" = "true" ]; then
        echo "Skipping gateway commissioning..."
        
        # Create commissioning completed marker if it doesn't exist
        COMMISSIONING_MARKER="${IGNITION_INSTALL_LOCATION}/data/.commissioning-completed"
        if [ ! -f "${COMMISSIONING_MARKER}" ]; then
            touch "${COMMISSIONING_MARKER}"
            echo "Commissioning marked as completed"
        fi
        
        # Set system properties to skip commissioning
        export IGNITION_SKIP_COMMISSIONING=true
        export GATEWAY_SKIP_SETUP_WIZARD=true
    fi
}

# Main execution
echo "Starting Ignition Gateway with custom configuration..."

# Handle commissioning settings
handle_commissioning

# Set up admin credentials if this is a fresh installation
if [ ! -f "${IGNITION_INSTALL_LOCATION}/data/db/config.idb" ]; then
    echo "Fresh installation detected, will set up admin credentials after initialization..."
    
    # Start Ignition in the background temporarily to initialize the database
    if [ "${GATEWAY_ADMIN_USERNAME:-}" != "" ] && [ "${GATEWAY_ADMIN_PASSWORD:-}" != "" ]; then
        # Fork the main entrypoint to let it initialize
        docker-entrypoint.sh "$@" &
        IGNITION_PID=$!
        
        # Wait for database to be created
        wait_for_ignition
        
        # Set up credentials
        setup_admin_credentials
        
        # Stop the temporary instance
        kill $IGNITION_PID 2>/dev/null || true
        wait $IGNITION_PID 2>/dev/null || true
    fi
fi

# Kick off the built-in entrypoint with all arguments
exec docker-entrypoint.sh "$@"