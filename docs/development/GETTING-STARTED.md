# Developer Getting Started Guide

Complete setup guide for contributing to the AI in Manufacturing 2025 platform.

## Prerequisites

### Required Software
- **Docker & Docker Compose** (v2.0+)
- **Node.js** (18+ with npm)
- **Git** with GitHub access
- **Python** (3.9+ for local development)

### GitHub Setup
1. **Personal Access Token**: Follow [`../setup/SECRETS-QUICKSTART.md`](../setup/SECRETS-QUICKSTART.md)
2. **Repository Access**: Ensure you can clone and push to the repository
3. **Docker Registry**: Token must have `read:packages` permission

## Environment Setup

### 1. Clone and Initialize
```bash
git clone <repository-url>
cd icc-ai-in-manufacturing-2025

# Install Node.js dependencies
npm install

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment Variables
Edit `.env` file with your settings:
```bash
# Required: GitHub token for Docker registry
GITHUB_TOKEN=your_github_personal_access_token

# Optional: Customize ports if needed
IGNITION_HTTP_PORT=9088
IGNITION_HTTPS_PORT=9043
LLAMA_INDEX_PORT=8080
```

### 3. Set Up Secrets
```bash
# Create secrets directory (if not exists)
mkdir -p secrets

# Add your GitHub token
echo "your_github_personal_access_token" > secrets/GIT_USER_TOKEN

# Set other secrets (use generated passwords)
echo "your_db_password" > secrets/POSTGRES_PASSWORD
echo "your_gateway_password" > secrets/GATEWAY_ADMIN_PASSWORD
```

### 4. Start Development Environment
```bash
# Start all services
docker compose up -d

# Verify services are running
docker compose ps

# Check logs if needed
docker compose logs -f ignition
```

### 5. Verify Installation
```bash
# Run preflight checks
./scripts/demo-preflight.sh

# Test a quick demo
./demos/scripts/run-full-stack-demo.sh --auto
```

## Development Workflow

### Daily Development
```bash
# Start your development session
docker compose up -d

# Check service health
./scripts/demo-preflight.sh

# Make your changes...

# Test changes
npm test

# Run integration tests
./demos/scripts/run-full-stack-demo.sh

# Stop services when done
docker compose down
```

### Service-Specific Development

#### Ignition Development
```bash
# Access Ignition Gateway
open https://localhost:9043

# Exec into container for debugging
docker exec -it $(docker compose ps -q ignition) bash

# Check Ignition logs
docker compose logs -f ignition
```

#### AI RAG Service Development
```bash
# Navigate to service
cd services/llama-index

# Run tests
python -m pytest

# Start service locally (optional)
python -m uvicorn app.main:app --reload --port 8080
```

#### Rules Engine Development
```bash
# Navigate to service
cd services/rules-engine

# Test the service
python rules-engine-service.py --test

# View validation rules
cat validation_rules.json
```

## Testing Your Changes

### Automated Testing
```bash
# Run all tests
npm test

# Run specific test suites
npm run test:unit
npm run test:integration
npm run test:e2e

# Python service tests
cd services/llama-index && python -m pytest
```

### Manual Testing
```bash
# 1. Environment validation
./scripts/demo-preflight.sh

# 2. Core services test
curl http://localhost:8000/health

# 3. Ignition Gateway test
open https://localhost:9043

# 4. RAG service test
curl http://localhost:8080/health

# 5. End-to-end demo
./demos/scripts/run-full-stack-demo.sh --auto
```

## Common Development Tasks

### Adding a New Service
1. Create directory in `services/your-service/`
2. Add service to `docker-compose.yml`
3. Create service documentation
4. Add health checks and tests
5. Update `docs/` as needed

### Modifying Ignition Projects
1. Access Designer via Gateway (https://localhost:9043)
2. Make changes in Designer
3. Commit changes via Git module
4. Test changes thoroughly
5. Document any new components

### Updating Documentation
1. Determine correct location in `docs/`
2. Follow existing documentation patterns
3. Update `GUIDE-INDEX.md` if adding new sections
4. Test all links and examples

## Debugging Common Issues

### Port Conflicts
```bash
# Check which ports are in use
lsof -i :9043  # Ignition HTTPS
lsof -i :8080  # RAG Service
lsof -i :3000  # Grafana (potential conflict)

# See resolution guide
cat docs/troubleshooting/CONFLICT-RESOLUTION-GUIDE.md
```

### Service Startup Issues
```bash
# Check service status
docker compose ps

# View service logs
docker compose logs service-name

# Restart specific service
docker compose restart service-name

# Full restart
docker compose down && docker compose up -d
```

### Authentication Problems
```bash
# Verify GitHub token
cat secrets/GIT_USER_TOKEN

# Test Docker registry access
docker login ghcr.io -u your-username

# Check Ignition authentication
cat secrets/GATEWAY_ADMIN_PASSWORD
```

### Database Issues
```bash
# Check database connectivity
docker exec -it $(docker compose ps -q postgres) psql -U admin -d manufacturing

# View database logs
docker compose logs postgres

# Reset database (destructive)
docker compose down -v && docker compose up -d
```

## IDE and Editor Setup

### VS Code Recommendations
Install these extensions:
- Docker
- Python
- YAML
- Markdown All in One
- GitLens

### Recommended Settings
```json
{
  "python.defaultInterpreterPath": "./services/llama-index/venv/bin/python",
  "docker.showStartPage": false,
  "yaml.schemas": {
    "docker-compose.yml": "docker-compose.yml"
  }
}
```

## Performance Tips

### Docker Optimization
```bash
# Use Docker build cache
export DOCKER_BUILDKIT=1

# Clean up unused resources
docker system prune -f

# Monitor resource usage
docker stats
```

### Development Efficiency
- Use `docker compose up service-name` to start specific services
- Keep frequently used commands in shell aliases
- Use `--watch` flags for auto-reloading during development
- Monitor logs with `docker compose logs -f --tail=100`

## Getting Help

### Documentation Resources
- **Architecture overview**: [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
- **Service details**: [`../../../services/README.md`](../../../services/README.md)
- **Troubleshooting**: [`../troubleshooting/`](../troubleshooting/)
- **API documentation**: [`../api/`](../api/)

### Quick Reference
```bash
# Essential commands
./scripts/demo-preflight.sh    # Validate environment
docker compose ps              # Check service status
docker compose logs -f         # Follow all logs
./demos/scripts/run-*.sh       # Run specific demos

# Useful URLs
# Ignition Gateway: https://localhost:9043
# API Gateway: http://localhost:8000
# Grafana: http://localhost:3001
# RAG Service: http://localhost:8080
```

### Common Solutions
- **Slow startup**: Increase Docker memory allocation
- **Permission errors**: Check file ownership and Docker permissions
- **Network issues**: Restart Docker daemon
- **Cache issues**: Run `docker compose build --no-cache`

Ready to contribute? Check out our [`CONTRIBUTING.md`](../../CONTRIBUTING.md) guide!