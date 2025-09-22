#!/usr/bin/env python3
"""
Full Stack Demo - WHK Services + Ignition Linting Showcase
Comprehensive demonstration that spins up the complete WHK services infrastructure
alongside the Ignition linting capabilities.
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional


# Colors for terminal output
class Colors:
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
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_section(text: str):
    """Print a formatted section header."""
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'-'*len(text)}{Colors.ENDC}")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def wait_for_user(prompt: str = "Press Enter to continue...", auto_mode: bool = False):
    """Wait for user input."""
    if auto_mode:
        print(
            f"\n{Colors.WARNING}[AUTO MODE] {prompt} (continuing automatically...){Colors.ENDC}"
        )
        time.sleep(3)  # Longer pause for infrastructure operations
    else:
        print(f"\n{Colors.WARNING}{prompt}{Colors.ENDC}")
        input()


class FullStackDemo:
    """Complete WHK services and linting demonstration."""

    def __init__(self, auto_mode: bool = False):
        self.project_root = Path(__file__).parent
        self.services_dir = Path("../whk-services-deployments").resolve()
        self.auto_mode = auto_mode
        self.services_running = False

        # Core services for the demo
        self.core_services = [
            "db",
            "vector-db",
            "redis",
            "rabbitmq",
            "mqtt-broker",
            "kong",
            "ignition",
            "prometheus",
            "grafana",
            "portainer",
        ]

        # Service descriptions
        self.service_descriptions = {
            "kong": "API Gateway - Routes and manages all API traffic",
            "db": "PostgreSQL - Primary database for applications",
            "vector-db": "Vector Database - AI/ML embeddings and search",
            "redis": "Redis Cache - High-performance caching layer",
            "rabbitmq": "Message Queue - Asynchronous communication",
            "mqtt-broker": "MQTT Broker - IoT device communication",
            "ignition": "Ignition SCADA - Industrial automation platform",
            "prometheus": "Prometheus - Metrics collection and monitoring",
            "grafana": "Grafana - Visualization and dashboards",
            "portainer": "Portainer - Container management UI",
        }

    def check_prerequisites(self) -> bool:
        """Check if all required components are available."""
        print_section("🔍 Checking Prerequisites")

        success = True

        # Check Docker
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                print_success(f"Docker available: {result.stdout.strip()}")
            else:
                print_error("Docker not available")
                success = False
        except FileNotFoundError:
            print_error("Docker not found. Please install Docker first.")
            success = False

        # Check Docker Compose
        try:
            result = subprocess.run(
                ["docker", "compose", "version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                print_success(f"Docker Compose available: {result.stdout.strip()}")
            else:
                print_error("Docker Compose not available")
                success = False
        except Exception:
            print_error("Docker Compose not found")
            success = False

        # Check services directory
        if self.services_dir.exists():
            print_success(f"WHK Services directory found: {self.services_dir}")

            # Check docker-compose.yml
            compose_file = self.services_dir / "docker-compose.yml"
            if compose_file.exists():
                print_success("Docker Compose configuration found")
            else:
                print_error("docker-compose.yml not found")
                success = False

            # Check .env file
            env_file = self.services_dir / ".env"
            if env_file.exists():
                print_success("Environment configuration found")
            else:
                print_warning("No .env file found - using defaults")
        else:
            print_error(f"WHK Services directory not found: {self.services_dir}")
            success = False

        # Infrastructure demo focuses on services only
        print_success("Infrastructure demo components ready")

        return success

    def show_architecture_overview(self):
        """Show the complete architecture being deployed."""
        print_header("WHK SERVICES ARCHITECTURE OVERVIEW")

        print_info("🏗️  Complete Manufacturing & AI Infrastructure Stack")
        print()

        print_section("🌐 API & Gateway Layer")
        print("  🔧 Kong API Gateway (Port 8000)")
        print("     • Routes all API traffic")
        print("     • Rate limiting and authentication")
        print("     • Load balancing and health checks")
        print()

        print_section("🏭 Industrial Automation")
        print("  🔧 Ignition SCADA (Port 9088)")
        print("     • Industrial automation platform")
        print("     • Real-time data collection")
        print("     • HMI/SCADA interfaces")
        print("     • Tag management and historian")
        print()

        print_section("💾 Data Layer")
        print("  🔧 PostgreSQL Database (Port 5432)")
        print("     • Primary application database")
        print("     • Transactional data storage")
        print("  🔧 Vector Database (Port 6333)")
        print("     • AI/ML embeddings storage")
        print("     • Semantic search capabilities")
        print("  🔧 Redis Cache (Port 6379)")
        print("     • High-performance caching")
        print("     • Session storage")
        print()

        print_section("📡 Messaging & Communication")
        print("  🔧 RabbitMQ (Port 5672, 15672)")
        print("     • Message queuing system")
        print("     • Asynchronous processing")
        print("  🔧 MQTT Broker (Port 1883)")
        print("     • IoT device communication")
        print("     • Real-time telemetry")
        print()

        print_section("📊 Monitoring & Management")
        print("  🔧 Prometheus (Port 9090)")
        print("     • Metrics collection")
        print("     • Time-series database")
        print("  🔧 Grafana (Port 3000)")
        print("     • Visualization dashboards")
        print("     • Alerting and reporting")
        print("  🔧 Portainer (Port 9443)")
        print("     • Container management UI")
        print("     • Docker administration")
        print()

        print_section("🎯 Key Features")
        features = [
            "🔒 Production-ready security configuration",
            "📈 Comprehensive monitoring and alerting",
            "🔄 Automatic service discovery and health checks",
            "📊 Real-time metrics and logging",
            "🏭 Industrial IoT integration",
            "🤖 AI/ML infrastructure ready",
            "🌐 API-first architecture",
            "📱 Modern web interfaces",
        ]

        for feature in features:
            print(f"  {feature}")

    def check_and_cleanup_conflicts(self) -> bool:
        """Check for and clean up conflicting containers and port conflicts."""
        print_section("🔍 Checking for Container and Port Conflicts")

        # Common conflicting container names
        conflicting_containers = [
            "portainer",
            "/portainer",
            "prometheus",
            "/prometheus",
            "grafana",
            "/grafana",
            "ignition",
            "/ignition",
            "kong",
            "/kong",
            "redis",
            "/redis",
            "rabbitmq",
            "/rabbitmq",
            "postgres",
            "/postgres",
            # WHK services container names
            "whk-services-db-1",
            "whk-services-vector-db-1",
            "whk-services-redis-1",
            "whk-services-rabbitmq-1",
            "whk-services-kong-1",
            "whk-services-ignition-1",
            "whk-services-mongo-1",
            # Other common container patterns
            "mqtt-broker",
            "vector-db",
        ]

        # Critical ports used by our services
        critical_ports = [
            8000,  # Kong API Gateway
            9088,  # Ignition Gateway
            3000,  # Grafana
            9090,  # Prometheus
            9443,  # Portainer
            6379,  # Redis
            5432,  # PostgreSQL
            5433,  # Vector Database
            5672,  # RabbitMQ
            1883,  # MQTT
        ]

        conflicts_found = []
        port_conflicts = []

        try:
            # Check for running containers with conflicting names
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                running_containers = result.stdout.strip().split("\n")
                for container in conflicting_containers:
                    clean_name = container.lstrip("/")
                    if clean_name in running_containers:
                        conflicts_found.append(clean_name)

            # Check for port conflicts
            print_info("🔍 Checking for port conflicts...")
            for port in critical_ports:
                try:
                    # Check if port is in use
                    result = subprocess.run(
                        ["lsof", "-i", f":{port}"],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        port_conflicts.append(port)
                        # Check if it's OrbStack
                        if "OrbStack" in result.stdout:
                            print_warning(f"Port {port} is in use by OrbStack")
                        else:
                            print_warning(f"Port {port} is already in use")
                except Exception:
                    # lsof might not be available, skip port check
                    pass

            # Separate OrbStack conflicts from resolvable conflicts
            orbstack_conflicts = []
            resolvable_port_conflicts = []

            for port in port_conflicts:
                try:
                    result = subprocess.run(
                        ["lsof", "-i", f":{port}"],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0 and "OrbStack" in result.stdout:
                        orbstack_conflicts.append(port)
                    else:
                        resolvable_port_conflicts.append(port)
                except Exception:
                    resolvable_port_conflicts.append(
                        port
                    )  # Assume resolvable if can't check

            # Only count resolvable conflicts as blocking
            blocking_conflicts = len(conflicts_found) + len(resolvable_port_conflicts)

            if conflicts_found:
                print_warning(
                    f"Found conflicting containers: {', '.join(conflicts_found)}"
                )

            if resolvable_port_conflicts:
                print_warning(
                    f"Found resolvable port conflicts: {', '.join(map(str, resolvable_port_conflicts))}"
                )

            if orbstack_conflicts:
                print_warning(
                    f"OrbStack is using ports: {', '.join(map(str, orbstack_conflicts))}"
                )

                if not self.auto_mode:
                    stop_orbstack = input(
                        f"\n{Colors.WARNING}Stop OrbStack services using these ports? (Y/n): {Colors.ENDC}"
                    )
                    if stop_orbstack.lower() in ["n", "no"]:
                        print_info(
                            "OrbStack services will remain running - some services may be skipped"
                        )
                        return True
                else:
                    print_info(
                        "[AUTO MODE] Automatically stopping OrbStack services..."
                    )

                print_info(
                    "   Attempting to stop Docker containers using these ports..."
                )

                # Try to find and stop Docker containers using our ports
                stopped_any = False
                for port in orbstack_conflicts:
                    try:
                        print_info(f"🔍 Checking for containers using port {port}")
                        # Find containers using this port
                        result = subprocess.run(
                            ["docker", "ps", "--format", "{{.Names}}\t{{.Ports}}"],
                            capture_output=True,
                            text=True,
                        )
                        if result.returncode == 0:
                            for line in result.stdout.strip().split("\n"):
                                if "\t" in line and line.strip():
                                    container_name, ports = line.split("\t", 1)
                                    if f":{port}->" in ports or f":{port}/" in ports:
                                        print_info(
                                            f"🛑 Stopping container using port {port}: {container_name}"
                                        )
                                        stop_result = subprocess.run(
                                            ["docker", "stop", container_name],
                                            capture_output=True,
                                            text=True,
                                        )
                                        if stop_result.returncode == 0:
                                            stopped_any = True
                                            print_info(
                                                f"   Successfully stopped {container_name}"
                                            )
                                        else:
                                            print_warning(
                                                f"   Failed to stop {container_name}"
                                            )
                    except Exception as e:
                        print_warning(
                            f"Could not check/stop containers on port {port}: {e}"
                        )

                if stopped_any:
                    print_success(
                        "✅ Some OrbStack containers stopped - ports may now be available"
                    )
                else:
                    print_info("ℹ️  No Docker containers found using conflicting ports")
                    print_info(
                        "   OrbStack may be using ports directly - some services will be skipped"
                    )

            if blocking_conflicts > 0:
                print_info(
                    "Resolvable conflicts need to be cleaned up to avoid startup failures."
                )

                if not self.auto_mode:
                    cleanup_choice = input(
                        f"\n{Colors.WARNING}Stop conflicting containers and processes? (Y/n): {Colors.ENDC}"
                    )
                    if cleanup_choice.lower() in ["n", "no"]:
                        print_error("Cannot continue with conflicts present")
                        return False
                else:
                    print_info("[AUTO MODE] Automatically cleaning up conflicts...")

                # Stop and remove conflicting containers
                for container in conflicts_found:
                    try:
                        print_info(f"🛑 Stopping container: {container}")
                        subprocess.run(
                            ["docker", "stop", container],
                            capture_output=True,
                            text=True,
                        )
                        subprocess.run(
                            ["docker", "rm", container], capture_output=True, text=True
                        )
                    except Exception as e:
                        print_warning(f"Could not stop {container}: {e}")

                # For resolvable port conflicts, try to stop any Docker containers using those ports
                if resolvable_port_conflicts:
                    print_info("🔍 Attempting to resolve port conflicts...")
                    try:
                        # Get all running containers and their ports
                        result = subprocess.run(
                            ["docker", "ps", "--format", "{{.Names}}\t{{.Ports}}"],
                            capture_output=True,
                            text=True,
                        )
                        if result.returncode == 0:
                            for line in result.stdout.strip().split("\n"):
                                if "\t" in line:
                                    container_name, ports = line.split("\t", 1)
                                    for conflict_port in resolvable_port_conflicts:
                                        if (
                                            f":{conflict_port}->" in ports
                                            or f":{conflict_port}/" in ports
                                        ):
                                            print_info(
                                                f"🛑 Stopping container using port {conflict_port}: {container_name}"
                                            )
                                            subprocess.run(
                                                ["docker", "stop", container_name],
                                                capture_output=True,
                                                text=True,
                                            )
                    except Exception as e:
                        print_warning(f"Could not resolve all port conflicts: {e}")

                print_success("✅ Resolvable conflicts cleaned up")
            else:
                if orbstack_conflicts:
                    print_success(
                        "✅ No resolvable conflicts found (OrbStack conflicts noted)"
                    )
                else:
                    print_success("✅ No container or port conflicts found")

            return True

        except Exception as e:
            print_error(f"Error checking for conflicts: {e}")
            return False

    def start_services(self) -> bool:
        """Start the Docker Compose services."""
        print_header("STARTING WHK SERVICES INFRASTRUCTURE")

        print_info("🚀 Starting core manufacturing and AI services...")
        print_info(f"   Working directory: {self.services_dir}")
        print()

        # Check and cleanup conflicts first
        if not self.check_and_cleanup_conflicts():
            return False

        # Filter out services that conflict with OrbStack
        service_ports = {
            "kong": 8000,
            "db": 5432,
            "vector-db": 5433,
            "redis": 6379,
            "rabbitmq": 5672,
            "mqtt-broker": 1883,
            "ignition": 9088,
            "prometheus": 9090,
            "grafana": 3000,
            "portainer": 9443,
        }

        services_to_start = []
        skipped_services = []

        print_section("📋 Services to Start")

        for service in self.core_services:
            description = self.service_descriptions.get(service, "Service component")
            port = service_ports.get(service)

            # Check if this service's port is still in use after cleanup
            skip_service = False
            if port:
                try:
                    result = subprocess.run(
                        ["lsof", "-i", f":{port}"],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        # Port is still in use, check if it's OrbStack or something else
                        if "OrbStack" in result.stdout:
                            skip_service = True
                            skipped_services.append((service, description, port))
                            print(
                                f"  ⏭️  {service.ljust(15)} - {description} - SKIPPED (OrbStack still using port {port})"
                            )
                        else:
                            # Some other process is using the port
                            skip_service = True
                            skipped_services.append((service, description, port))
                            print(
                                f"  ⏭️  {service.ljust(15)} - {description} - SKIPPED (port {port} in use by other process)"
                            )
                except Exception:
                    pass  # If we can't check, assume it's safe

            if not skip_service:
                services_to_start.append(service)
                print(f"  🔧 {service.ljust(15)} - {description}")

        if skipped_services:
            print()
            print_info("⚠️  Services skipped due to OrbStack port conflicts:")
            for service, description, port in skipped_services:
                print_info(
                    f"   • {service} - {description.split(' - ')[0]} (port {port})"
                )

        if not services_to_start:
            print_warning("No services can be started due to port conflicts")
            return False

        wait_for_user("Ready to start the infrastructure?", self.auto_mode)

        try:
            print_info("🔄 Starting services (this may take a few minutes)...")

            # Start only non-conflicting services without dependencies to avoid conflicts
            cmd = ["docker", "compose", "up", "-d", "--no-deps"] + services_to_start
            print(f"Command: {' '.join(cmd)}")
            print()

            result = subprocess.run(
                cmd, cwd=self.services_dir, capture_output=True, text=True
            )

            if result.returncode == 0:
                print_success("✅ Services started successfully!")
                if skipped_services:
                    print_info(
                        f"   ({len(skipped_services)} services skipped due to OrbStack port conflicts)"
                    )
                self.services_running = True

                if result.stdout:
                    print("Output:")
                    print(result.stdout)

                return True
            else:
                print_error("❌ Failed to start services")
                if result.stderr:
                    print("Error:")
                    print(result.stderr)
                return False

        except Exception as e:
            print_error(f"Error starting services: {e}")
            return False

    def check_service_health(self):
        """Check the health of running services."""
        print_section("🏥 Service Health Check")

        if not self.services_running:
            print_warning("Services not started yet")
            return

        try:
            # Get service status
            result = subprocess.run(
                ["docker", "compose", "ps", "--format", "table"],
                cwd=self.services_dir,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("Service Status:")
                print(result.stdout)
            else:
                print_warning("Could not get service status")

        except Exception as e:
            print_error(f"Error checking service health: {e}")

        # Show service URLs
        print_section("🌐 Service Access URLs")
        service_urls = {
            "Ignition Gateway": "http://localhost:9088",
            "Kong Admin": "http://localhost:8011",
            "Grafana": "http://localhost:3000",
            "Prometheus": "http://localhost:9090",
            "RabbitMQ Management": "http://localhost:15672",
            "Portainer": "https://localhost:9443",
        }

        for name, url in service_urls.items():
            print(f"  🔗 {name.ljust(20)} - {url}")

    def show_service_integration(self):
        """Show how the services integrate with each other."""
        print_header("SERVICE INTEGRATION DEMONSTRATION")

        print_info("🔗 Demonstrating how services work together...")
        print_info("   This showcases the complete manufacturing ecosystem integration")

        wait_for_user("Ready to explore service integration?", self.auto_mode)

        print_section("🔗 Active Service Integrations")

        integrations = [
            "🏭 Ignition ↔ PostgreSQL: Real-time tag data storage and trending",
            "🌐 Kong ↔ All Services: API gateway routing and load balancing",
            "📊 Prometheus ↔ All Services: Metrics collection and monitoring",
            "📈 Grafana ↔ Prometheus: Visualization and alerting dashboards",
            "📡 RabbitMQ ↔ Services: Asynchronous message processing",
            "💾 Redis ↔ Services: High-performance caching layer",
            "🤖 Vector DB: Ready for AI/ML workloads and semantic search",
            "📱 MQTT ↔ Ignition: IoT device connectivity and telemetry",
        ]

        for integration in integrations:
            print(f"  {integration}")

        print_section("🎯 Ready for Development")
        print_info(
            "Your complete manufacturing infrastructure is now running and ready for:"
        )
        print_info("  • Industrial automation development")
        print_info("  • AI/ML model deployment")
        print_info("  • IoT device integration")
        print_info("  • Real-time monitoring and alerting")
        print_info("  • API development and testing")

    def show_integration_benefits(self):
        """Show how the services integrate with Ignition and linting."""
        print_header("INTEGRATION & BENEFITS OVERVIEW")

        print_section("🔗 Service Integration Points")

        integrations = [
            {
                "title": "🏭 Ignition ↔ Database Integration",
                "description": "Real-time tag data storage and historical trending",
                "benefits": [
                    "Persistent data storage",
                    "Advanced analytics",
                    "Reporting capabilities",
                ],
            },
            {
                "title": "🤖 AI/ML ↔ Vector Database",
                "description": "Semantic search and intelligent automation",
                "benefits": [
                    "Smart tag discovery",
                    "Predictive maintenance",
                    "Anomaly detection",
                ],
            },
            {
                "title": "📡 MQTT ↔ Ignition Gateway",
                "description": "IoT device integration and real-time telemetry",
                "benefits": [
                    "Device connectivity",
                    "Real-time monitoring",
                    "Edge computing",
                ],
            },
            {
                "title": "📊 Monitoring ↔ All Services",
                "description": "Comprehensive observability and alerting",
                "benefits": [
                    "Performance monitoring",
                    "Health checks",
                    "Proactive alerts",
                ],
            },
            {
                "title": "🔧 Development ↔ Infrastructure",
                "description": "Complete development environment ready",
                "benefits": [
                    "Full-stack development platform",
                    "Production-ready architecture",
                    "Scalable microservices design",
                ],
            },
        ]

        for integration in integrations:
            print(f"\n{Colors.BOLD}{integration['title']}{Colors.ENDC}")
            print(f"  {integration['description']}")
            for benefit in integration["benefits"]:
                print(f"    ✓ {benefit}")

        print_section("🎯 Complete Solution Benefits")

        solution_benefits = [
            "🏭 **Industrial-Grade Infrastructure** - Production-ready services",
            "🔒 **Security-First Design** - Comprehensive security controls",
            "📈 **Scalable Architecture** - Microservices-based design",
            "🤖 **AI-Ready Platform** - Vector database and ML infrastructure",
            "🔧 **Development Ready** - Complete development environment",
            "📊 **Full Observability** - Metrics, logs, and monitoring",
            "🌐 **API-First Approach** - Modern integration capabilities",
            "🏭 **Manufacturing Focus** - Purpose-built for industrial automation",
        ]

        for benefit in solution_benefits:
            print(f"  {benefit}")

    def cleanup_all_demo_services(self):
        """Stop and clean up all demo-related Docker services."""
        print_section("🧹 Comprehensive Service Cleanup")

        print_info("🛑 Stopping all demo-related services...")

        # Stop WHK services stack
        try:
            print_info("Stopping WHK services stack...")
            result = subprocess.run(
                ["docker", "compose", "down"],
                cwd=self.services_dir,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print_success("✅ WHK services stopped")
            else:
                print_warning("⚠️  Issues stopping WHK services")
        except Exception as e:
            print_warning(f"Could not stop WHK services: {e}")

        # Stop any remaining conflicting containers
        conflicting_containers = [
            "portainer",
            "prometheus",
            "grafana",
            "ignition",
            "redis",
            "rabbitmq",
            "kong",
            "postgres",
            "vector-db",
            "mqtt-broker",
            # WHK services container names
            "whk-services-db-1",
            "whk-services-vector-db-1",
            "whk-services-redis-1",
            "whk-services-rabbitmq-1",
            "whk-services-kong-1",
            "whk-services-ignition-1",
            "whk-services-mongo-1",
        ]

        for container in conflicting_containers:
            try:
                # Check if container exists and is running
                check_result = subprocess.run(
                    ["docker", "ps", "-q", "-f", f"name={container}"],
                    capture_output=True,
                    text=True,
                )

                if check_result.stdout.strip():
                    print_info(f"🛑 Stopping container: {container}")
                    subprocess.run(
                        ["docker", "stop", container], capture_output=True, text=True
                    )
                    subprocess.run(
                        ["docker", "rm", container], capture_output=True, text=True
                    )
            except Exception:
                pass  # Ignore errors for containers that don't exist

        # Clean up any demo networks
        try:
            print_info("🧹 Cleaning up demo networks...")
            subprocess.run(
                ["docker", "network", "prune", "-f"], capture_output=True, text=True
            )
        except Exception:
            pass

        print_success("✅ Comprehensive cleanup completed")
        self.services_running = False

    def cleanup_services(self):
        """Stop and clean up the Docker services."""
        print_section("🧹 Service Cleanup")

        if not self.services_running:
            print_info("No services to clean up")
            return

        try:
            print_info("🛑 Stopping services...")
            result = subprocess.run(
                ["docker", "compose", "down"],
                cwd=self.services_dir,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print_success("✅ Services stopped successfully")
                self.services_running = False
            else:
                print_warning("⚠️  Some issues during cleanup")
                if result.stderr:
                    print(result.stderr)

        except Exception as e:
            print_error(f"Error during cleanup: {e}")

    def run_full_demo(self) -> bool:
        """Run the complete full-stack demonstration."""
        print_header("WHK FULL STACK DEMONSTRATION")

        print_info(
            "🎯 Welcome to the complete WHK manufacturing and AI infrastructure demo!"
        )
        print_info("   This demonstration showcases:")
        print_info("   • Complete microservices infrastructure")
        print_info("   • Industrial automation platform (Ignition)")
        print_info("   • AI/ML ready architecture")
        print_info("   • Real-world service integration")

        # Check prerequisites
        if not self.check_prerequisites():
            print_error("Prerequisites not met. Please fix issues above.")
            return False

        wait_for_user(
            "Prerequisites verified. Ready to start the demo?", self.auto_mode
        )

        try:
            # Show architecture
            self.show_architecture_overview()
            wait_for_user(
                "Architecture overview complete. Ready to start services?",
                self.auto_mode,
            )

            # Start services
            if not self.start_services():
                print_error("Failed to start services. Demo cannot continue.")
                return False

            # Wait for services to stabilize
            print_info("⏳ Waiting for services to stabilize...")
            time.sleep(10 if not self.auto_mode else 5)

            # Check service health
            self.check_service_health()
            wait_for_user(
                "Services are running. Ready for integration demo?", self.auto_mode
            )

            # Show service integration
            self.show_service_integration()
            wait_for_user(
                "Integration demo complete. Ready for benefits overview?",
                self.auto_mode,
            )

            # Show integration benefits
            self.show_integration_benefits()

            # Final summary
            print_header("DEMO COMPLETE!")
            print_success("🎉 Full stack demonstration completed successfully!")
            print()
            print_info("🌐 Your complete WHK infrastructure is now running:")
            print_info("   • Manufacturing services and databases")
            print_info("   • Ignition SCADA platform")
            print_info("   • Monitoring and management tools")
            print_info("   • AI/ML ready architecture")
            print()
            print_info("🔗 Access your services:")
            print_info("   • Ignition Gateway: http://localhost:9088")
            print_info("   • Grafana Dashboards: http://localhost:3000")
            print_info("   • Container Management: https://localhost:9443")

            # Ask about cleanup
            if not self.auto_mode:
                cleanup = input(
                    f"\n{Colors.WARNING}Would you like to stop the services? (y/N): {Colors.ENDC}"
                )
                if cleanup.lower() in ["y", "yes"]:
                    self.cleanup_services()
                else:
                    print_info(
                        "Services left running. Use 'docker compose down' to stop them later."
                    )
            else:
                print_info("[AUTO MODE] Services left running for further exploration")

            return True

        except KeyboardInterrupt:
            print_warning("\n\nDemo interrupted by user.")
            self.cleanup_services()
            return False
        except Exception as e:
            print_error(f"Demo error: {e}")
            self.cleanup_services()
            return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="WHK Full Stack Demo - Complete Manufacturing Infrastructure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This demo showcases the complete WHK manufacturing infrastructure:

1. Docker Compose Services Stack
   - Kong API Gateway, PostgreSQL, Redis, RabbitMQ
   - Ignition SCADA, Prometheus, Grafana, Portainer
   - Complete microservices architecture

2. AI/ML Ready Platform
   - Vector database for semantic search
   - Real-time data processing
   - Scalable microservices design

3. Full Integration Demonstration
   - Service health monitoring
   - Real-world usage scenarios
   - Complete observability stack

Run without arguments for the full interactive demo.
        """,
    )

    parser.add_argument(
        "--auto",
        "-a",
        action="store_true",
        help="Run full demo automatically without user prompts",
    )

    parser.add_argument(
        "--services-only",
        action="store_true",
        help="Start services only, skip integration demo",
    )

    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Stop all running services and exit",
    )

    parser.add_argument(
        "--cleanup-all",
        action="store_true",
        help="Stop ALL demo-related services (comprehensive cleanup)",
    )

    args = parser.parse_args()

    demo = FullStackDemo(auto_mode=args.auto)

    if args.cleanup:
        demo.cleanup_services()
        return

    if args.cleanup_all:
        demo.cleanup_all_demo_services()
        return

    if args.services_only:
        # Services-only mode should be non-interactive
        demo.auto_mode = True
        if demo.check_prerequisites():
            demo.show_architecture_overview()
            if demo.start_services():
                demo.check_service_health()
                print_success("Services started successfully!")
            else:
                print_error("Failed to start services")
                sys.exit(1)
        else:
            print_error("Prerequisites not met")
            sys.exit(1)
    else:
        # Run full demo
        success = demo.run_full_demo()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
