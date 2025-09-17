#!/usr/bin/env bash
set -euo pipefail

# Demo runner script for AI Manufacturing Stack
# This script provides easy access to the interactive demo programs

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

# Ensure Go path is set for Homebrew
export PATH="/opt/homebrew/bin:$PATH"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_help() {
    echo -e "${BLUE}🚀 AI Manufacturing Stack Demo Runner${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo -e "${GREEN}Available Commands:${NC}"
    echo "  up [startup|health]     - Start the stack (with optional sub-demo)"
    echo "  down [shutdown|cleanup] - Stop the stack (with optional sub-demo)"
    echo "  auto [startup|health|shutdown] - Auto-running demos (no interaction)"
    echo "  cleanup                 - Force cleanup all containers (fixes conflicts)"
    echo "  help                    - Show this help message"
    echo ""
    echo -e "${GREEN}Demo Options (pass to up/down commands):${NC}"
    echo "  --auto                  - Run automatically without pausing"
    echo "  --dry-run              - Show commands without executing"
    echo "  --immediate            - Skip typewriter animation"
    echo "  --no-color             - Disable colored output"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo "  $0 cleanup              # Fix container conflicts before demo"
    echo "  $0 up                   # Interactive stack startup (requires ENTER presses)"
    echo "  $0 auto startup         # Automatic startup demo (no interaction)"
    echo "  $0 auto health          # Automatic health check"
    echo "  $0 up startup --auto    # Go framework auto mode"
    echo "  $0 up health --dry-run  # Show health check commands"
    echo "  $0 down                 # Interactive stack shutdown"
    echo "  $0 down cleanup --auto  # Automatic complete cleanup"
    echo ""
    echo -e "${YELLOW}🎯 For presentations (RECOMMENDED):${NC}"
    echo "  $0 auto startup         # Fully automatic, no key presses needed"
    echo "  $0 auto health          # Quick health check"
    echo "  $0 auto shutdown        # Graceful shutdown"
    echo ""
    echo -e "${YELLOW}🎓 For training/interactive demos:${NC}"
    echo "  $0 up startup           # Press ENTER between each step"
    echo "  $0 down shutdown        # Press ENTER between each step"
}

run_startup_demo() {
    local sub_command="${1:-startup}"
    shift || true
    
    echo -e "${GREEN}🚀 Starting AI Manufacturing Stack Demo...${NC}"
    
    if [ "$sub_command" = "startup" ]; then
        ./demo-stack-up --startup "$@"
    elif [ "$sub_command" = "health" ]; then
        ./demo-stack-up --health "$@"
    else
        echo -e "${RED}Unknown startup sub-command: $sub_command${NC}"
        echo "Available: startup, health"
        exit 1
    fi
}

run_shutdown_demo() {
    local sub_command="${1:-shutdown}"
    shift || true
    
    echo -e "${YELLOW}🛑 Starting Stack Shutdown Demo...${NC}"
    
    if [ "$sub_command" = "shutdown" ]; then
        ./demo-stack-down --shutdown "$@"
    elif [ "$sub_command" = "cleanup" ]; then
        echo -e "${RED}⚠️  WARNING: This will delete ALL data permanently!${NC}"
        read -p "Are you sure? Type 'yes' to continue: " confirm
        if [ "$confirm" = "yes" ]; then
            ./demo-stack-down --cleanup "$@"
        else
            echo "Cleanup cancelled."
            exit 0
        fi
    else
        echo -e "${RED}Unknown shutdown sub-command: $sub_command${NC}"
        echo "Available: shutdown, cleanup"
        exit 1
    fi
}

# Check if demo executables exist
if [ ! -f "./demo-stack-up" ] || [ ! -f "./demo-stack-down" ]; then
    echo -e "${YELLOW}Building demo executables...${NC}"
    go build -o demo-stack-up demo-stack-up.go
    go build -o demo-stack-down demo-stack-down.go
    echo -e "${GREEN}Demo executables built successfully!${NC}"
fi

run_auto_demo() {
    local sub_command="${1:-startup}"
    shift || true
    
    echo -e "${GREEN}🤖 Starting Auto-Running Demo (no interaction required)...${NC}"
    
    # Set environment variables for fast presentation mode
    export DEMO_NO_TYPEWRITER=1
    export DEMO_STEP_DELAY=2
    export DEMO_COMMAND_DELAY=1
    
    # Override with any user-provided environment variables
    if [ -n "${DEMO_FAST_MODE:-}" ]; then
        export DEMO_NO_TYPEWRITER=1
        export DEMO_STEP_DELAY=0
        export DEMO_COMMAND_DELAY=0.5
    fi
    
    ./demo-stack-auto.sh "$sub_command"
}

# Parse command line arguments
case "${1:-help}" in
    "up")
        shift
        run_startup_demo "$@"
        ;;
    "down")
        shift
        run_shutdown_demo "$@"
        ;;
    "auto")
        shift
        run_auto_demo "$@"
        ;;
    "cleanup")
        echo -e "${YELLOW}🧹 Running cleanup to fix container conflicts...${NC}"
        ./demo-cleanup.sh
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
