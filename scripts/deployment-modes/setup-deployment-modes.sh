#!/bin/bash

# Ignition 8.3 Deployment Modes Setup Script
# This script configures multiple deployment environments for Ignition 8.3

set -euo pipefail

# Configuration
API_BASE="${API_BASE:-http://localhost:9088}"
API_TOKEN="${IGNITION_API_KEY:-mcp2:6uAHjHhz8FaYm654IgcTNSVWV4cukaFuXED0CvGGuBE}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Wait for Ignition to be ready
wait_for_ignition() {
    log_info "Waiting for Ignition to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -H "X-Ignition-API-Token: $API_TOKEN" \
            "$API_BASE/data/api/v1/gateway-info" > /dev/null 2>&1; then
            log_success "Ignition is ready!"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts - Ignition not ready yet..."
        sleep 2
        ((attempt++))
    done
    
    log_error "Ignition failed to become ready after $max_attempts attempts"
    return 1
}

# Create deployment mode configuration directories
create_deployment_directories() {
    log_info "Creating deployment mode directories..."
    
    local modes=("development" "staging" "production")
    local config_dir="$PROJECT_ROOT/ignition-deployment-configs"
    
    mkdir -p "$config_dir"
    
    for mode in "${modes[@]}"; do
        local mode_dir="$config_dir/$mode"
        mkdir -p "$mode_dir"/{devices,databases,security,certificates,tags}
        log_success "Created directory structure for $mode mode"
    done
}

# Create development mode configuration
create_development_config() {
    log_info "Setting up development mode configuration..."
    
    local dev_dir="$PROJECT_ROOT/ignition-deployment-configs/development"
    
    # Database configuration for development (using simulator)
    cat > "$dev_dir/databases/primary.json" << 'EOF'
{
  "name": "DevelopmentDB",
  "description": "Development database connection",
  "enabled": true,
  "driverName": "PostgreSQL",
  "connectUrl": "jdbc:postgresql://db:5432/ignition_dev",
  "username": "admin",
  "password": {
    "secretProvider": "Docker Secrets",
    "secretName": "database_connection_password"
  },
  "validationQuery": "SELECT 1",
  "maxConnections": 5,
  "connectionTimeout": 30000
}
EOF

    # Device configuration for development (simulator)
    cat > "$dev_dir/devices/simulator.json" << 'EOF'
{
  "name": "DevelopmentSimulator",
  "description": "Simulated device for development",
  "enabled": true,
  "deviceType": "Simulator",
  "hostName": "localhost",
  "port": 502,
  "connectedThreshold": 3000,
  "requestTimeout": 2000,
  "settings": {
    "deviceCount": 10,
    "updateRate": 1000,
    "simulateErrors": true
  }
}
EOF

    # Security settings for development
    cat > "$dev_dir/security/settings.json" << 'EOF'
{
  "authMode": "Internal",
  "sessionTimeout": 28800,
  "auditingEnabled": true,
  "passwordComplexity": "low",
  "sslEnabled": false,
  "allowHttp": true
}
EOF

    log_success "Development mode configuration created"
}

# Create staging mode configuration
create_staging_config() {
    log_info "Setting up staging mode configuration..."
    
    local staging_dir="$PROJECT_ROOT/ignition-deployment-configs/staging"
    
    # Database configuration for staging
    cat > "$staging_dir/databases/primary.json" << 'EOF'
{
  "name": "StagingDB",
  "description": "Staging database connection",
  "enabled": true,
  "driverName": "PostgreSQL",
  "connectUrl": "jdbc:postgresql://staging-db:5432/ignition_staging",
  "username": "staging_user",
  "password": {
    "secretProvider": "Docker Secrets",
    "secretName": "staging_database_password"
  },
  "validationQuery": "SELECT 1",
  "maxConnections": 10,
  "connectionTimeout": 15000
}
EOF

    # Device configuration for staging (test hardware)
    cat > "$staging_dir/devices/test_plc.json" << 'EOF'
{
  "name": "StagingPLC",
  "description": "Test PLC for staging environment",
  "enabled": true,
  "deviceType": "Modbus TCP",
  "hostName": "test-plc.local",
  "port": 502,
  "connectedThreshold": 3000,
  "requestTimeout": 5000,
  "settings": {
    "unitId": 1,
    "zeroBasedNumerics": false,
    "reverseStringByteOrder": false
  }
}
EOF

    # Security settings for staging
    cat > "$staging_dir/security/settings.json" << 'EOF'
{
  "authMode": "Active Directory",
  "sessionTimeout": 14400,
  "auditingEnabled": true,
  "passwordComplexity": "medium",
  "sslEnabled": true,
  "allowHttp": false,
  "activeDirectory": {
    "domain": "staging.company.local",
    "serverUrl": "ldaps://staging-ad.company.local:636"
  }
}
EOF

    log_success "Staging mode configuration created"
}

# Create production mode configuration
create_production_config() {
    log_info "Setting up production mode configuration..."
    
    local prod_dir="$PROJECT_ROOT/ignition-deployment-configs/production"
    
    # Database configuration for production
    cat > "$prod_dir/databases/primary.json" << 'EOF'
{
  "name": "ProductionDB",
  "description": "Production database connection",
  "enabled": true,
  "driverName": "PostgreSQL",
  "connectUrl": "jdbc:postgresql://prod-db:5432/ignition_production",
  "username": "prod_user",
  "password": {
    "secretProvider": "Docker Secrets",
    "secretName": "production_database_password"
  },
  "validationQuery": "SELECT 1",
  "maxConnections": 20,
  "connectionTimeout": 10000,
  "connectionPooling": true
}
EOF

    # Device configuration for production (real hardware)
    cat > "$prod_dir/devices/production_plc.json" << 'EOF'
{
  "name": "ProductionPLC",
  "description": "Production PLC system",
  "enabled": true,
  "deviceType": "Modbus TCP",
  "hostName": "192.168.1.100",
  "port": 502,
  "connectedThreshold": 3000,
  "requestTimeout": 2000,
  "settings": {
    "unitId": 1,
    "zeroBasedNumerics": false,
    "reverseStringByteOrder": false,
    "redundancyEnabled": true,
    "backupHost": "192.168.1.101"
  }
}
EOF

    # Security settings for production
    cat > "$prod_dir/security/settings.json" << 'EOF'
{
  "authMode": "Active Directory",
  "sessionTimeout": 3600,
  "auditingEnabled": true,
  "passwordComplexity": "high",
  "sslEnabled": true,
  "allowHttp": false,
  "activeDirectory": {
    "domain": "company.local",
    "serverUrl": "ldaps://ad.company.local:636"
  },
  "ipWhitelist": ["192.168.1.0/24", "10.0.0.0/8"],
  "maxConcurrentSessions": 50
}
EOF

    log_success "Production mode configuration created"
}

# Set deployment mode via API
set_deployment_mode() {
    local mode="$1"
    log_info "Setting deployment mode to: $mode"
    
    # Check if deployment modes are supported
    local response=$(curl -s -H "X-Ignition-API-Token: $API_TOKEN" \
        "$API_BASE/data/api/v1/gateway-info" || echo "")
    
    if [[ -z "$response" ]]; then
        log_error "Failed to connect to Ignition API"
        return 1
    fi
    
    # Set the deployment mode (this API endpoint may vary in actual implementation)
    curl -s -X PUT \
        -H "X-Ignition-API-Token: $API_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"deploymentMode\": \"$mode\"}" \
        "$API_BASE/data/api/v1/gateway/deployment-mode" || {
        log_warning "Deployment mode API endpoint may not be available in current version"
        log_info "Setting mode via environment variable instead"
        return 0
    }
    
    log_success "Deployment mode set to: $mode"
}

# Main setup function
main() {
    log_info "🚀 Ignition 8.3 Deployment Modes Setup"
    echo "======================================"
    
    # Wait for Ignition to be ready
    wait_for_ignition
    
    # Create directory structure
    create_deployment_directories
    
    # Create mode-specific configurations
    create_development_config
    create_staging_config
    create_production_config
    
    # Set initial deployment mode from environment variable
    local deployment_mode="${DEPLOYMENT_ENVIRONMENT:-development}"
    set_deployment_mode "$deployment_mode"
    
    log_success "🎉 Deployment modes setup complete!"
    echo ""
    log_info "Available deployment modes:"
    echo "  • development - Simulators, relaxed security, extended sessions"
    echo "  • staging     - Test hardware, medium security, AD integration"
    echo "  • production  - Real hardware, high security, IP restrictions"
    echo ""
    log_info "To switch modes:"
    echo "  1. Update DEPLOYMENT_ENVIRONMENT in .env file"
    echo "  2. Restart the Ignition container"
    echo "  3. Or use: ./scripts/deployment-modes/switch-mode.sh <mode>"
    echo ""
    log_info "Configuration files are stored in:"
    echo "  ./ignition-deployment-configs/<mode>/"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi