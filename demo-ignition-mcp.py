#!/usr/bin/env python3
"""
Ignition MCP Server Demonstration

This demo showcases the Ignition FastMCP server capabilities including:
1. Server startup and health checks
2. Tool discovery and availability
3. Real-time Ignition Gateway integration
4. Practical usage examples
5. AI assistant integration scenarios

Author: WHK AI Development Team
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests


class Colors:
    """ANSI color codes for terminal output"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}")
    print(f"{text.center(70)}")
    print(f"{'=' * 70}{Colors.ENDC}")


def print_section(text: str):
    """Print a formatted section header"""
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'-' * len(text)}{Colors.ENDC}")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def wait_for_user(message: str, auto_mode: bool = False):
    """Wait for user input unless in auto mode"""
    if auto_mode:
        print(
            f"{Colors.WARNING}[AUTO MODE] {message} (continuing automatically...){Colors.ENDC}"
        )
        time.sleep(2)
    else:
        input(f"\n{Colors.WARNING}Press Enter to continue: {message}{Colors.ENDC}")


class IgnitionMCPDemo:
    """Ignition MCP Server demonstration class"""

    def __init__(self, auto_mode: bool = False):
        self.auto_mode = auto_mode
        self.project_root = Path(__file__).parent
        self.ignition_mcp_dir = Path("../ignition-mcp").resolve()
        self.mcp_server_url = "http://127.0.0.1:8007/mcp"
        self.ignition_gateway_url = "http://localhost:9088"
        self.server_process = None
        self.server_running = False

    def check_prerequisites(self) -> bool:
        """Check if all required components are available"""
        print_section("🔍 Checking Prerequisites")
        success = True

        # Check if ignition-mcp directory exists
        if self.ignition_mcp_dir.exists():
            print_success(f"Ignition MCP directory found: {self.ignition_mcp_dir}")
        else:
            print_error(f"Ignition MCP directory not found: {self.ignition_mcp_dir}")
            success = False

        # Check if MCP server script exists
        mcp_server_script = self.ignition_mcp_dir / "mcp_server.py"
        if mcp_server_script.exists():
            print_success(f"MCP server script found: {mcp_server_script}")
        else:
            print_error(f"MCP server script not found: {mcp_server_script}")
            success = False

        # Check if uv is available
        try:
            result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print_success(f"uv available: {result.stdout.strip()}")
            else:
                print_error("uv not available")
                success = False
        except FileNotFoundError:
            print_error("uv not found - required for running the MCP server")
            success = False

        # Check if fastmcp is available
        try:
            result = subprocess.run(
                ["uv", "run", "fastmcp", "--version"],
                capture_output=True,
                text=True,
                cwd=self.ignition_mcp_dir,
            )
            if result.returncode == 0:
                print_success("FastMCP available")
            else:
                print_warning("FastMCP may not be available - will attempt to install")
        except Exception:
            print_warning("Could not check FastMCP availability")

        # Check MCP configuration
        mcp_config = self.project_root / ".cursor" / "mcp.json"
        if mcp_config.exists():
            print_success("MCP configuration found")
            try:
                with open(mcp_config) as f:
                    config = json.load(f)
                    if "ignition-fastmcp" in config.get("mcpServers", {}):
                        print_success("Ignition FastMCP server configured in MCP")
                    else:
                        print_warning(
                            "Ignition FastMCP server not found in MCP configuration"
                        )
            except Exception as e:
                print_warning(f"Could not parse MCP configuration: {e}")
        else:
            print_warning("MCP configuration not found")

        return success

    def show_architecture_overview(self):
        """Show the Ignition MCP architecture"""
        print_header("IGNITION MCP SERVER ARCHITECTURE")

        print_info("🏗️  Complete Ignition Gateway Integration via MCP")
        print_info("   Built on Ignition 8.3+ OpenAPI Specification")
        print()

        print_section("🌐 MCP Server Components")
        components = [
            "🔧 FastMCP Server (Port 8007) - Model Context Protocol endpoint",
            "🏭 Ignition Client - REST API integration with Gateway 8.3+",
            "🛠️ Dynamic Tool Generator - 42+ tools from Ignition 8.3 OpenAPI spec",
            "🔐 Authentication Manager - API key and basic auth support",
            "📊 Real-time Gateway Monitor - Status and health checks",
        ]

        for component in components:
            print(f"  {component}")

        print_section("🎯 Tool Categories")
        categories = [
            (
                "🔐 Activation Tools",
                "7 tools",
                "License management and gateway activation",
            ),
            ("💾 Backup Tools", "2 tools", "Gateway backup creation and restoration"),
            ("📋 Log Tools", "11 tools", "Log retrieval, management, and analysis"),
            (
                "📦 Module Tools",
                "10 tools",
                "Module health checks and certificate management",
            ),
            (
                "🏗️ Project Tools",
                "12 tools",
                "Project creation, import, export, and management",
            ),
        ]

        for category, count, description in categories:
            print(f"  {category.ljust(20)} - {count.ljust(8)} - {description}")

        print_section("🔗 Integration Benefits")
        benefits = [
            "🤖 AI Assistant Integration - Direct Gateway control via natural language",
            "⚡ Real-time Operations - Live status monitoring and management",
            "🛡️ Secure Access - Authenticated API calls with proper error handling",
            "📈 Scalable Architecture - Async operations for optimal performance",
            "🔧 Comprehensive Coverage - Full Gateway 8.3+ API surface area exposed",
            "🆕 Modern API Foundation - Built on latest Ignition 8.3 OpenAPI specification",
        ]

        for benefit in benefits:
            print(f"  {benefit}")

    def cleanup_port_8007(self):
        """Clean up any processes using port 8007"""
        try:
            print_info("🔍 Checking for processes using port 8007...")
            result = subprocess.run(
                ["lsof", "-ti", ":8007"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split("\n")
                for pid in pids:
                    if pid.strip():
                        print_info(f"🛑 Stopping process {pid.strip()} using port 8007")
                        subprocess.run(
                            ["kill", "-9", pid.strip()],
                            capture_output=True,
                            text=True,
                        )
                print_success("✅ Port 8007 cleaned up")
                time.sleep(2)  # Give time for port to be released
            else:
                print_info("ℹ️  Port 8007 is available")
        except Exception as e:
            print_warning(f"Could not check/cleanup port 8007: {e}")

    def start_mcp_server(self) -> bool:
        """Start the Ignition MCP server"""
        print_section("🚀 Starting Ignition MCP Server")

        # Clean up port first
        self.cleanup_port_8007()

        print_info("Starting FastMCP server for Ignition Gateway integration...")
        print_info(f"   Server URL: {self.mcp_server_url}")
        print_info(f"   Working directory: {self.ignition_mcp_dir}")

        try:
            # Ensure uv environment is set up
            print_info("🔧 Setting up uv environment...")
            setup_result = subprocess.run(
                ["uv", "sync"],
                cwd=self.ignition_mcp_dir,
                capture_output=True,
                text=True,
            )
            if setup_result.returncode != 0:
                print_warning(f"uv sync warning: {setup_result.stderr}")
            else:
                print_success("✅ uv environment ready")

            # Start the MCP server
            cmd = ["uv", "run", "python", "mcp_server.py"]
            print(f"Command: {' '.join(cmd)}")
            print()

            self.server_process = subprocess.Popen(
                cmd,
                cwd=self.ignition_mcp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait for server to start
            print_info("⏳ Waiting for server to start...")
            time.sleep(8)  # Increased wait time for uv environment setup

            # Check if server is running
            if self.check_server_health():
                print_success("✅ MCP server started successfully!")
                self.server_running = True
                return True
            else:
                # Try to get error output
                if self.server_process.poll() is not None:
                    stdout, stderr = self.server_process.communicate()
                    if stderr:
                        print_error(f"Server error: {stderr}")
                    if stdout:
                        print_info(f"Server output: {stdout}")
                else:
                    # Server is still running, let's check if it's just slow to start
                    print_info("🔄 Server process is running, checking again...")
                    time.sleep(3)
                    if self.check_server_health():
                        print_success("✅ MCP server started successfully!")
                        self.server_running = True
                        return True

                print_error("❌ Failed to start MCP server")
                return False

        except Exception as e:
            print_error(f"Error starting MCP server: {e}")
            return False

    def check_server_health(self) -> bool:
        """Check if the MCP server is healthy"""
        try:
            # Check if the MCP endpoint responds (even with an error is good)
            response = requests.get(self.mcp_server_url, timeout=5)
            # MCP server should respond with a JSON-RPC error for GET requests
            # This indicates the server is running and responding
            return response.status_code == 200 and "jsonrpc" in response.text
        except Exception:
            return False

    def discover_tools(self) -> Optional[List[Dict]]:
        """Discover available MCP tools"""
        print_section("🔍 Discovering Available Tools")

        try:
            print_info("Querying MCP server for available tools...")

            # Make a request to discover tools
            response = requests.post(
                self.mcp_server_url,
                json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                if "result" in data and "tools" in data["result"]:
                    tools = data["result"]["tools"]
                    print_success(f"✅ Discovered {len(tools)} tools")
                    return tools
                else:
                    print_warning("No tools found in response")
                    return None
            else:
                print_error(f"Failed to discover tools: HTTP {response.status_code}")
                return None

        except Exception as e:
            print_error(f"Error discovering tools: {e}")
            return None

    def show_tool_categories(self, tools: List[Dict]):
        """Show tools organized by category"""
        print_section("📋 Available Tool Categories")

        # Categorize tools
        categories = {
            "activation": {"name": "🔐 Activation", "tools": []},
            "backup": {"name": "💾 Backup", "tools": []},
            "logs": {"name": "📋 Logs", "tools": []},
            "modules": {"name": "📦 Modules", "tools": []},
            "projects": {"name": "🏗️ Projects", "tools": []},
            "other": {"name": "⚙️ Other", "tools": []},
        }

        for tool in tools:
            tool_name = tool.get("name", "")
            categorized = False

            for category_key, category_info in categories.items():
                if category_key in tool_name.lower():
                    category_info["tools"].append(tool)
                    categorized = True
                    break

            if not categorized:
                categories["other"]["tools"].append(tool)

        # Display categories
        for category_key, category_info in categories.items():
            if category_info["tools"]:
                print(
                    f"\n{category_info['name']} ({len(category_info['tools'])} tools)"
                )
                for tool in category_info["tools"][:5]:  # Show first 5 tools
                    name = tool.get("name", "Unknown")
                    description = tool.get("description", "No description")
                    print(f"  🔧 {name}")
                    print(f"     {description}")

                if len(category_info["tools"]) > 5:
                    print(f"     ... and {len(category_info['tools']) - 5} more tools")

    def test_gateway_connection(self) -> bool:
        """Test connection to Ignition Gateway"""
        print_section("🔗 Testing Gateway Connection")

        print_info(
            f"Testing connection to Ignition Gateway: {self.ignition_gateway_url}"
        )

        try:
            # Test basic connectivity
            response = requests.get(
                f"{self.ignition_gateway_url}/system/gwinfo", timeout=5
            )
            if response.status_code == 200:
                print_success("✅ Gateway is accessible")
                return True
            else:
                print_warning(f"Gateway responded with status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print_warning("⚠️  Gateway not accessible - may not be running")
            print_info("   This is expected if Ignition Gateway is not started")
            return False
        except Exception as e:
            print_error(f"Error testing gateway connection: {e}")
            return False

    def demonstrate_tool_usage(self, tools: List[Dict]):
        """Demonstrate practical tool usage"""
        print_section("🎯 Tool Usage Demonstration")

        print_info("Demonstrating key MCP tools with practical examples...")

        # Find some key tools to demonstrate
        demo_tools = []
        tool_names_to_demo = [
            "get_activation_is_online",
            "get_projects_list",
            "get_logs_wrapper_names",
            "get_modules_health",
        ]

        for tool_name in tool_names_to_demo:
            for tool in tools:
                if tool.get("name") == tool_name:
                    demo_tools.append(tool)
                    break

        if not demo_tools:
            print_warning("No suitable tools found for demonstration")
            return

        print_info(f"Found {len(demo_tools)} tools to demonstrate:")

        for tool in demo_tools:
            name = tool.get("name", "Unknown")
            description = tool.get("description", "No description")
            print(f"\n🔧 {Colors.BOLD}{name}{Colors.ENDC}")
            print(f"   {description}")

            # Show example usage
            if "activation" in name:
                print(
                    f"   {Colors.OKCYAN}Example: Check if Gateway is online and licensed{Colors.ENDC}"
                )
            elif "projects" in name:
                print(
                    f"   {Colors.OKCYAN}Example: List all Perspective and Vision projects{Colors.ENDC}"
                )
            elif "logs" in name:
                print(
                    f"   {Colors.OKCYAN}Example: Get available log categories for troubleshooting{Colors.ENDC}"
                )
            elif "modules" in name:
                print(
                    f"   {Colors.OKCYAN}Example: Check health status of all installed modules{Colors.ENDC}"
                )

    def show_ai_integration_examples(self):
        """Show examples of AI assistant integration"""
        print_section("🤖 AI Assistant Integration Examples")

        print_info(
            "The MCP server enables natural language interaction with Ignition Gateway:"
        )
        print()

        examples = [
            {
                "prompt": "Check if my Ignition Gateway is online and properly licensed",
                "tool": "get_activation_is_online",
                "description": "AI assistant uses activation tools to verify Gateway status",
            },
            {
                "prompt": "List all my Perspective projects and their current status",
                "tool": "get_projects_list",
                "description": "AI assistant queries project management tools",
            },
            {
                "prompt": "Show me recent error logs from the Gateway",
                "tool": "get_logs_*",
                "description": "AI assistant retrieves and analyzes log data",
            },
            {
                "prompt": "Create a backup of my Gateway configuration",
                "tool": "post_backup_create",
                "description": "AI assistant initiates backup operations",
            },
            {
                "prompt": "Check the health of all installed modules",
                "tool": "get_modules_health",
                "description": "AI assistant monitors module status",
            },
        ]

        for i, example in enumerate(examples, 1):
            print(f"{Colors.BOLD}{i}. Natural Language Request:{Colors.ENDC}")
            print(f'   "{example["prompt"]}"')
            print(f"   {Colors.OKCYAN}→ Uses tool: {example['tool']}{Colors.ENDC}")
            print(f"   {Colors.OKCYAN}→ {example['description']}{Colors.ENDC}")
            print()

    def show_integration_benefits(self):
        """Show the benefits of MCP integration"""
        print_section("🎯 Integration Benefits & Real-World Impact")

        benefits = [
            {
                "title": "🤖 Natural Language Gateway Control",
                "description": "Control Ignition Gateway through conversational AI",
                "impact": "Reduces complexity for non-technical users",
            },
            {
                "title": "⚡ Real-Time Operations",
                "description": "Live monitoring and management capabilities",
                "impact": "Immediate response to system events and issues",
            },
            {
                "title": "🔧 Comprehensive API Coverage",
                "description": "42+ tools covering all major Gateway functions",
                "impact": "Complete operational control through AI interface",
            },
            {
                "title": "🛡️ Secure Integration",
                "description": "Authenticated API calls with proper error handling",
                "impact": "Enterprise-grade security for production environments",
            },
            {
                "title": "📈 Scalable Architecture",
                "description": "Async operations and efficient resource usage",
                "impact": "Handles multiple concurrent AI requests efficiently",
            },
        ]

        for benefit in benefits:
            print(f"\n{Colors.BOLD}{benefit['title']}{Colors.ENDC}")
            print(f"  {benefit['description']}")
            print(f"  {Colors.OKGREEN}Impact: {benefit['impact']}{Colors.ENDC}")

        print_section("📊 Key Statistics")
        stats = [
            "✅ 42+ dynamically generated tools from Ignition 8.3 OpenAPI specification",
            "✅ 5 major tool categories covering all Gateway operations",
            "✅ Real-time integration with live Ignition Gateway 8.3+ instances",
            "✅ Full MCP protocol compliance for AI assistant integration",
            "✅ Async/await architecture for optimal performance",
            "✅ Comprehensive error handling and status reporting",
            "✅ Modern REST API foundation using latest Ignition capabilities",
        ]

        for stat in stats:
            print(f"  {stat}")

    def show_next_steps(self):
        """Show next steps for using the MCP server"""
        print_section("🚀 Next Steps & Usage Guide")

        print_info("Getting started with Ignition MCP server:")
        print()

        steps = [
            "1. Ensure Ignition Gateway is running and accessible",
            "2. Configure authentication (API key or basic auth) in environment",
            "3. Start the MCP server: cd ../ignition-mcp && uv run fastmcp run mcp_server.py",
            "4. Restart Cursor to load MCP configuration",
            "5. Use MCP tools in AI conversations for Gateway management",
        ]

        for step in steps:
            print(f"  {step}")

        print_section("💡 Usage Examples")
        examples = [
            "# Check server status",
            "curl http://127.0.0.1:8007/mcp/health",
            "",
            "# In AI conversations, use natural language:",
            '"Check if my Gateway is online"',
            '"List all my Perspective projects"',
            '"Show me recent error logs"',
            '"Create a Gateway backup"',
        ]

        for example in examples:
            if example.startswith("#"):
                print(f"  {Colors.OKCYAN}{example}{Colors.ENDC}")
            elif example.startswith('"'):
                print(f"  {Colors.WARNING}{example}{Colors.ENDC}")
            else:
                print(f"  {example}")

        print_section("🔗 Resources")
        resources = [
            "📚 Documentation: ../ignition-mcp/docs/",
            "🔧 Configuration: ../ignition-mcp/docs/configuration.md",
            "💡 Examples: ../ignition-mcp/docs/examples.md",
            "🛠️ API Reference: ../ignition-mcp/docs/api-reference.md",
        ]

        for resource in resources:
            print(f"  {resource}")

    def cleanup_server(self):
        """Clean up the MCP server process"""
        if self.server_process:
            print_info("🛑 Stopping MCP server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                print_success("✅ MCP server stopped")
            except subprocess.TimeoutExpired:
                print_warning("⚠️  Force killing MCP server...")
                self.server_process.kill()
                self.server_process.wait()
            self.server_process = None
            self.server_running = False

        # Also clean up any remaining processes on port 8007
        try:
            result = subprocess.run(
                ["lsof", "-ti", ":8007"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split("\n")
                for pid in pids:
                    if pid.strip():
                        subprocess.run(
                            ["kill", "-9", pid.strip()],
                            capture_output=True,
                            text=True,
                        )
                print_info("🧹 Cleaned up remaining processes on port 8007")
        except Exception:
            pass  # Ignore cleanup errors

    def run_full_demo(self) -> bool:
        """Run the complete Ignition MCP demonstration"""
        print_header("IGNITION MCP SERVER DEMONSTRATION")

        print_info("🎯 Welcome to the comprehensive Ignition MCP server demo!")
        print_info("   This demonstration showcases:")
        print_info("   • FastMCP server integration with Ignition Gateway")
        print_info("   • 42+ dynamically generated tools from OpenAPI")
        print_info("   • Real-time Gateway management capabilities")
        print_info("   • AI assistant integration scenarios")

        # Check prerequisites
        if not self.check_prerequisites():
            print_error("Prerequisites not met. Please fix issues above.")
            return False

        wait_for_user(
            "Prerequisites verified. Ready to start the demo?", self.auto_mode
        )

        try:
            # Show architecture overview
            self.show_architecture_overview()
            wait_for_user(
                "Architecture overview complete. Ready to start MCP server?",
                self.auto_mode,
            )

            # Start MCP server
            if not self.start_mcp_server():
                print_error("Failed to start MCP server. Demo cannot continue.")
                return False

            wait_for_user(
                "MCP server started. Ready to discover tools?", self.auto_mode
            )

            # Discover tools
            tools = self.discover_tools()
            if not tools:
                print_warning("Could not discover tools, but continuing with demo...")
                tools = []

            if tools:
                self.show_tool_categories(tools)
                wait_for_user(
                    "Tool discovery complete. Ready for usage demonstration?",
                    self.auto_mode,
                )

                self.demonstrate_tool_usage(tools)
                wait_for_user(
                    "Usage demo complete. Ready for AI integration examples?",
                    self.auto_mode,
                )

            # Test Gateway connection
            self.test_gateway_connection()
            wait_for_user(
                "Gateway test complete. Ready for AI integration examples?",
                self.auto_mode,
            )

            # Show AI integration examples
            self.show_ai_integration_examples()
            wait_for_user(
                "AI examples complete. Ready for benefits overview?", self.auto_mode
            )

            # Show integration benefits
            self.show_integration_benefits()
            wait_for_user(
                "Benefits overview complete. Ready for next steps?", self.auto_mode
            )

            # Show next steps
            self.show_next_steps()

            # Final summary
            print_header("DEMO COMPLETE!")
            print_success(
                "🎉 Ignition MCP server demonstration completed successfully!"
            )
            print()
            print_info(
                "🌐 Your Ignition MCP server is now running and ready for AI integration:"
            )
            print_info("   • 42+ tools available for Gateway management")
            print_info("   • Real-time integration with Ignition Gateway")
            print_info("   • Natural language control through AI assistants")
            print_info("   • Complete operational coverage of Gateway API")
            print()
            print_info("🔗 Access your MCP server:")
            print_info(f"   • Health endpoint: {self.mcp_server_url}/health")
            print_info(f"   • MCP endpoint: {self.mcp_server_url}")
            print_info("   • Use in Cursor AI conversations after restart")

            if not self.auto_mode:
                input(
                    f"\n{Colors.WARNING}Press Enter to stop the MCP server and exit...{Colors.ENDC}"
                )

            return True

        except KeyboardInterrupt:
            print_info("\n🛑 Demo interrupted by user")
            return False
        except Exception as e:
            print_error(f"Demo failed with error: {e}")
            return False
        finally:
            self.cleanup_server()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Ignition MCP Server Demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This demo showcases the Ignition FastMCP server capabilities:

1. FastMCP Server Integration
   - Dynamic tool generation from OpenAPI specification
   - Real-time Gateway API integration
   - MCP protocol compliance for AI assistants

2. Comprehensive Tool Coverage
   - 42+ tools across 5 major categories
   - Activation, backup, logs, modules, and projects
   - Complete Gateway operational control

3. AI Assistant Integration
   - Natural language Gateway control
   - Real-time monitoring and management
   - Secure, authenticated API operations

Run without arguments for the full interactive demo.
        """,
    )

    parser.add_argument(
        "--auto",
        "-a",
        action="store_true",
        help="Run demo automatically without user prompts",
    )

    parser.add_argument(
        "--section",
        "-s",
        choices=[
            "prereq",
            "architecture",
            "server",
            "tools",
            "gateway",
            "ai",
            "benefits",
            "steps",
        ],
        help="Run only a specific demo section",
    )

    args = parser.parse_args()

    demo = IgnitionMCPDemo(auto_mode=args.auto)

    if args.section:
        # Run specific section
        if args.section == "prereq":
            demo.check_prerequisites()
        elif args.section == "architecture":
            demo.show_architecture_overview()
        elif args.section == "server":
            if demo.start_mcp_server():
                input("Press Enter to stop server...")
                demo.cleanup_server()
        elif args.section == "tools":
            if demo.start_mcp_server():
                tools = demo.discover_tools()
                if tools:
                    demo.show_tool_categories(tools)
                demo.cleanup_server()
        elif args.section == "gateway":
            demo.test_gateway_connection()
        elif args.section == "ai":
            demo.show_ai_integration_examples()
        elif args.section == "benefits":
            demo.show_integration_benefits()
        elif args.section == "steps":
            demo.show_next_steps()
    else:
        # Run full demo
        success = demo.run_full_demo()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
