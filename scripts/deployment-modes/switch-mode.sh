#!/bin/bash

# Ignition 8.3 Deployment Mode Switcher
# Switches between development, staging, and production modes

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

# Show usage information
show_usage() {
    cat << EOF
Usage: $0 <mode> [options]

Available deployment modes:
  development  - Simulators, relaxed security, extended sessions
  staging      - Test hardware, medium security, AD integration  
  production   - Real hardware, high security, IP restrictions

Options:
  --force         Force mode switch without confirmation
  --no-restart    Don't restart containers automatically
  --help          Show this help message

Examples:
  $0 development
  $0 production --force
  $0 staging --no-restart

EOF
}

# Validate deployment mode
validate_mode() {
    local mode="$1"
    local valid_modes=("development" "staging" "production")
    
    for valid_mode in "${valid_modes[@]}"; do
        if [[ "$mode" == "$valid_mode" ]]; then
            return 0
        fi
    done
    
    log_error "Invalid deployment mode: $mode"
    log_info "Valid modes: ${valid_modes[*]}"
    return 1
}

# Get current deployment mode
get_current_mode() {
    local env_file="$PROJECT_ROOT/.env"
    
    if [[ -f "$env_file" ]]; then
        local current_mode=$(grep "^DEPLOYMENT_ENVIRONMENT=" "$env_file" | cut -d'=' -f2)
        echo "${current_mode:-development}"
    else
        echo "development"
    fi
}

# Check if configuration exists for mode
check_mode_config() {
    local mode="$1"
    local config_dir="$PROJECT_ROOT/ignition-deployment-configs/$mode"
    
    if [[ ! -d "$config_dir" ]]; then
        log_error "Configuration directory not found for $mode mode: $config_dir"
        log_info "Run setup-deployment-modes.sh first to create configurations"
        return 1
    fi
    
    # Check for essential configuration files
    local required_files=(
        "$config_dir/databases/primary.json"
        "$config_dir/security/settings.json"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_warning "Missing configuration file: $file"
        fi
    done
    
    return 0
}

# Update environment file
update_env_file() {
    local new_mode="$1"
    local env_file="$PROJECT_ROOT/.env"
    
    log_info "Updating .env file with new deployment mode..."
    
    if [[ -f "$env_file" ]]; then
        # Update existing DEPLOYMENT_ENVIRONMENT line
        if grep -q "^DEPLOYMENT_ENVIRONMENT=" "$env_file"; then
            sed -i.bak "s/^DEPLOYMENT_ENVIRONMENT=.*/DEPLOYMENT_ENVIRONMENT=$new_mode/" "$env_file"
        else
            # Add DEPLOYMENT_ENVIRONMENT line
            echo "DEPLOYMENT_ENVIRONMENT=$new_mode" >> "$env_file"
        fi
    else
        log_error ".env file not found at $env_file"
        return 1
    fi
    
    # Update IGNITION_DEPLOYMENT_MODE as well
    if grep -q "^IGNITION_DEPLOYMENT_MODE=" "$env_file"; then
        sed -i.bak "s/^IGNITION_DEPLOYMENT_MODE=.*/IGNITION_DEPLOYMENT_MODE=$new_mode/" "$env_file"
    else
        echo "IGNITION_DEPLOYMENT_MODE=$new_mode" >> "$env_file"
    fi
    
    log_success "Environment file updated"
}

# Check container status
check_containers() {
    log_info "Checking container status..."
    
    local ignition_status=$(docker compose ps -q ignition 2>/dev/null || echo "")
    
    if [[ -n "$ignition_status" ]]; then
        local status=$(docker compose ps ignition --format "table {{.State}}" | tail -n1)
        echo "$status"
    else
        echo "not_running"
    fi
}

# Restart containers
restart_containers() {
    log_info "Restarting Ignition container to apply new deployment mode..."
    
    # Restart ignition service specifically
    docker compose restart ignition
    
    log_info "Waiting for Ignition to restart..."
    sleep 10
    
    # Wait for API to be available
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -H "X-Ignition-API-Token: $API_TOKEN" \
            "$API_BASE/data/api/v1/gateway-info" > /dev/null 2>&1; then
            log_success "Ignition is ready with new deployment mode!"
            return 0
        fi
        
        log_info "Waiting for Ignition to be ready... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    log_warning "Ignition may still be starting up. Check manually."
    return 0
}

# Show deployment mode status
show_status() {
    local mode="$1"
    local config_dir="$PROJECT_ROOT/ignition-deployment-configs/$mode"
    
    echo ""
    log_success "Deployment mode switched to: $mode"
    echo ""
    log_info "Configuration details for $mode mode:"
    
    # Show database configuration if exists
    local db_config="$config_dir/databases/primary.json"
    if [[ -f "$db_config" ]]; then
        local db_name=$(jq -r '.name' "$db_config" 2>/dev/null || echo "Unknown")
        local db_url=$(jq -r '.connectUrl' "$db_config" 2>/dev/null || echo "Unknown")
        echo "  📊 Database: $db_name ($db_url)"
    fi
    
    # Show device configuration if exists
    local device_files=("$config_dir"/devices/*.json)
    if [[ -f "${device_files[0]}" ]]; then
        for device_file in "${device_files[@]}"; do
            if [[ -f "$device_file" ]]; then
                local device_name=$(jq -r '.name' "$device_file" 2>/dev/null || echo "Unknown")
                local device_type=$(jq -r '.deviceType' "$device_file" 2>/dev/null || echo "Unknown")
                echo "  🔧 Device: $device_name ($device_type)"
            fi
        done
    fi
    
    # Show security settings if exists
    local security_config="$config_dir/security/settings.json"
    if [[ -f "$security_config" ]]; then
        local auth_mode=$(jq -r '.authMode' "$security_config" 2>/dev/null || echo "Unknown")
        local ssl_enabled=$(jq -r '.sslEnabled' "$security_config" 2>/dev/null || echo "Unknown")
        echo "  🔒 Security: $auth_mode (SSL: $ssl_enabled)"
    fi
    
    echo ""
    log_info "Access Ignition at: http://localhost:9088"
    log_info "API Documentation: http://localhost:9088/openapi"
}

# Request user confirmation
confirm_switch() {
    local current_mode="$1"
    local new_mode="$2"
    
    echo ""
    log_warning "You are about to switch from '$current_mode' to '$new_mode' mode"
    log_warning "This will restart the Ignition container and may interrupt active connections"
    echo ""
    read -p "Are you sure you want to continue? [y/N]: " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Mode switch cancelled"
        exit 0
    fi
}

# Main function
main() {
    local target_mode=""
    local force_switch=false
    local auto_restart=true
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_usage
                exit 0
                ;;
            --force)
                force_switch=true
                shift
                ;;
            --no-restart)
                auto_restart=false
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                if [[ -z "$target_mode" ]]; then
                    target_mode="$1"
                else
                    log_error "Multiple modes specified"
                    show_usage
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Check if mode was specified
    if [[ -z "$target_mode" ]]; then
        log_error "No deployment mode specified"
        show_usage
        exit 1
    fi
    
    # Validate the target mode
    validate_mode "$target_mode"
    
    # Get current mode
    local current_mode=$(get_current_mode)
    
    log_info "🔄 Ignition 8.3 Deployment Mode Switcher"
    echo "========================================"
    log_info "Current mode: $current_mode"
    log_info "Target mode:  $target_mode"
    
    # Check if already in target mode
    if [[ "$current_mode" == "$target_mode" ]]; then
        log_warning "Already in $target_mode mode"
        exit 0
    fi
    
    # Check if configuration exists
    check_mode_config "$target_mode"
    
    # Request confirmation unless forced
    if [[ "$force_switch" != true ]]; then
        confirm_switch "$current_mode" "$target_mode"
    fi
    
    # Update environment file
    update_env_file "$target_mode"
    
    # Restart containers if requested
    if [[ "$auto_restart" == true ]]; then
        local container_status=$(check_containers)
        
        if [[ "$container_status" == "running" ]] || [[ "$container_status" == "Up" ]]; then
            restart_containers
        else
            log_info "Ignition container not running, start with: docker compose up -d ignition"
        fi
    else
        log_info "Skipping container restart (use --restart to enable)"
        log_info "Restart manually with: docker compose restart ignition"
    fi
    
    # Show status
    show_status "$target_mode"
    
    log_success "🎉 Deployment mode switch complete!"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi