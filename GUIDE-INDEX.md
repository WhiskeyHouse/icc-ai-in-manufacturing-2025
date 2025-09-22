# Guide Index

Your roadmap to navigating this AI manufacturing demo platform. Start here for organized access to all documentation, services, and tools.

## 🚀 Getting Started (First Visit)

| I want to... | Go here |
|--------------|---------|
| **Understand what this platform does** | [`README.md`](README.md) |
| **Run a quick demo** | [`demos/README.md`](demos/README.md) |
| **Set up development environment** | [`docs/development/GETTING-STARTED.md`](docs/development/GETTING-STARTED.md) |
| **Fix a problem** | [`docs/troubleshooting/`](docs/troubleshooting/) |

## 📁 Documentation Hub

### Setup & Configuration
- [`docs/setup/`](docs/setup/) – Environment setup guides
  - [`IGNITION-DOCKER-SETUP.md`](docs/setup/IGNITION-DOCKER-SETUP.md) – Ignition development environment
  - [`SECRETS-QUICKSTART.md`](docs/setup/SECRETS-QUICKSTART.md) – Authentication & secrets setup
  - [`IGNITION-DEPLOYMENT-MODES.md`](docs/setup/IGNITION-DEPLOYMENT-MODES.md) – Deployment configurations

### Development Resources  
- [`docs/development/`](docs/development/) – Developer guides and tools
  - [`GETTING-STARTED.md`](docs/development/GETTING-STARTED.md) – Development environment setup
  - [`IGNITION-LINTER.md`](docs/development/IGNITION-LINTER.md) – Code quality tools
  - [`WHK-TESTING-FRAMEWORK.md`](docs/development/WHK-TESTING-FRAMEWORK.md) – Testing strategy
  - [`PLAYWRIGHT-MCP-SETUP.md`](docs/development/PLAYWRIGHT-MCP-SETUP.md) – Test automation setup
  - [`AGENTS.md`](docs/development/AGENTS.md) – AI agent configurations

### API Documentation
- [`docs/api/`](docs/api/) – API guides and references  
  - [`IGNITION-8.3-API-GUIDE.md`](docs/api/IGNITION-8.3-API-GUIDE.md) – Ignition API usage
  - [`IGNITION-8.3-OPENAPI-ADVANTAGE.md`](docs/api/IGNITION-8.3-OPENAPI-ADVANTAGE.md) – OpenAPI benefits

### Troubleshooting & Support
- [`docs/troubleshooting/`](docs/troubleshooting/) – Common issues & solutions
  - [`CONFLICT-RESOLUTION-GUIDE.md`](docs/troubleshooting/CONFLICT-RESOLUTION-GUIDE.md) – Port conflicts & fixes
  - [`ORBSTACK-CONFLICT-RESOLUTION.md`](docs/troubleshooting/ORBSTACK-CONFLICT-RESOLUTION.md) – OrbStack issues
  - [`BUGFIX-SUMMARY.md`](docs/troubleshooting/BUGFIX-SUMMARY.md) – Known issues & workarounds

## 🎯 Demos & Automation

### Demo Execution
- [`demos/`](demos/) – Interactive demonstrations hub
  - [`scripts/`](demos/scripts/) – Shell entry points (`run-*.sh`, `demo-*.sh`)
  - [`python/`](demos/python/) – Python demo orchestrators (`demo-*.py`)
  - [`go/`](demos/go/) – Go-powered CLI tools (`demo-stack-*.go`)

### Demo Documentation
- [`docs/demos/`](docs/demos/) – Demo guides and instructions
- [`docs/runbooks/`](docs/runbooks/) – Presentation runbooks
- [`docs/presentations/`](docs/presentations/) – Slide outlines and guides
- [`presentations/`](presentations/) – Finalized presentation materials

## 🔧 Services & Architecture

### Core Platform Services
- [`services/`](services/) – All platform microservices
  - [`ignition/`](services/ignition/) – SCADA/HMI system configurations
  - [`llama-index/`](services/llama-index/) – AI RAG service (formerly `llama-index-service/`)
  - [`rules-engine/`](services/rules-engine/) – Validation engine (formerly `rules-engine-service.py`)
  - [`monitoring/`](services/monitoring/) – Observability stack (Grafana, Prometheus)

### System Documentation  
- [`ARCHITECTURE.md`](ARCHITECTURE.md) – High-level system design & service breakdown
- [`docs/DOCKER-SERVICES.md`](docs/DOCKER-SERVICES.md) – Compose service details and ports

### Configuration Management
- [`config/`](config/) – Centralized configuration files
  - [`kong/`](config/kong/) – API gateway configuration
  - [`postgres/`](config/postgres/) – Database initialization
  - [`rabbitmq/`](config/rabbitmq/) – Message broker setup
  - [`certs/`](config/certs/) – SSL certificates

## 🛠️ Utilities & Scripts

### Essential Scripts
- [`scripts/demo-preflight.sh`](scripts/demo-preflight.sh) – Environment validation before demos
- [`scripts/demo-up.sh`](scripts/demo-up.sh) – Quick demo environment startup  
- [`scripts/demo-down.sh`](scripts/demo-down.sh) – Clean shutdown
- [`scripts/`](scripts/) – All automation utilities

### Quality Assurance
- [`tests/`](tests/) – Comprehensive test suites
- Linting & validation tools (see [`docs/development/`](docs/development/))

## 🗂️ Quick Reference

### Common Entry Points
1. **New Developer** → [`README.md`](README.md) → [`docs/development/GETTING-STARTED.md`](docs/development/GETTING-STARTED.md)
2. **Demo Presenter** → [`demos/README.md`](demos/README.md) → [`docs/runbooks/`](docs/runbooks/)
3. **Troubleshooter** → [`docs/troubleshooting/`](docs/troubleshooting/) → [`scripts/demo-preflight.sh`](scripts/demo-preflight.sh)
4. **Architect** → [`ARCHITECTURE.md`](ARCHITECTURE.md) → [`docs/DOCKER-SERVICES.md`](docs/DOCKER-SERVICES.md)

### File Organization Changes
- **Documentation**: Moved from root to organized `docs/` subdirectories
- **Services**: Consolidated in `services/` with clear separation by function
- **Configuration**: Centralized in `config/` directory
- **Legacy files**: Maintained in original locations where needed for compatibility

> 💡 **Pro Tip**: Bookmark this file and use it as your navigation hub. All paths are relative to the repository root.
