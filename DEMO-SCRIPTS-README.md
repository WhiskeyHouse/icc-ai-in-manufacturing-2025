# 🚀 AI Manufacturing Stack Demo Scripts

Interactive presentation demos built with the [saschagrunert/demo](https://github.com/saschagrunert/demo) framework for showcasing the complete AI-powered manufacturing stack.

## 📋 Overview

These demo scripts provide an interactive, presentation-ready way to:

- **Start up** the complete AI manufacturing stack with automatic license acceptance
- **Verify** all services are healthy and ready for demos
- **Shut down** the stack gracefully 
- **Clean up** completely for fresh environment resets

All demos include:
- ✅ **Automatic Ignition EULA acceptance** (`ACCEPT_IGNITION_EULA=Y`)
- ✅ **Self-signed certificate auto-acceptance**
- ✅ **Step-by-step explanations** perfect for presentations
- ✅ **Health checks** and verification at each stage
- ✅ **Graceful error handling** with continue-on-error options

## 🛠️ Prerequisites

1. **Go 1.25+** (install via Homebrew: `brew install go`)
2. **Docker & Docker Compose** 
3. **Required secrets** in `secrets/` directory
4. **Environment configuration** (`.env` file)

## 🚀 Quick Start

### Using the Demo Runner (Recommended)

```bash
# Interactive stack startup
./run-demo.sh up

# Interactive stack shutdown  
./run-demo.sh down

# Show all options
./run-demo.sh help
```

### Direct Demo Execution

```bash
# Build the demos (done automatically by run-demo.sh)
go build -o demo-stack-up demo-stack-up.go
go build -o demo-stack-down demo-stack-down.go

# Run startup demo
./demo-stack-up --startup

# Run shutdown demo
./demo-stack-down --shutdown
```

## 📖 Available Demos

### 🚀 Stack Startup (`demo-stack-up`)

#### `startup` - Complete Stack Startup
Interactive demo that starts all services in the correct order:

1. **Prerequisites Check** - Verify Docker, secrets, environment
2. **Infrastructure Services** - PostgreSQL, Redis, RabbitMQ, MQTT
3. **AI & API Services** - LlamaIndex RAG, Kong Gateway
4. **Ignition Gateway** - SCADA with auto license acceptance
5. **Monitoring Stack** - Grafana, Prometheus, Netdata, Portainer
6. **Health Verification** - Ensure all services are ready
7. **Access URLs** - Display all service endpoints

```bash
# Interactive mode (best for presentations)
./run-demo.sh up startup

# Automatic mode (for CI/testing)
./run-demo.sh up startup --auto

# Dry run (show commands without executing)
./run-demo.sh up startup --dry-run
```

#### `health` - Service Health Check
Comprehensive health verification of all stack components:

1. **Container Status** - Check all containers are running
2. **Network Connectivity** - Test inter-service communication
3. **Ignition Gateway** - Verify SCADA system is operational
4. **AI Services** - Test RAG service endpoints
5. **Monitoring** - Check Grafana, Prometheus, Netdata
6. **Summary Report** - Overall stack readiness

```bash
./run-demo.sh up health
```

### 🛑 Stack Shutdown (`demo-stack-down`)

#### `shutdown` - Graceful Shutdown
Proper shutdown sequence preserving data:

1. **Current Status** - Show what's running
2. **Monitoring Services** - Stop non-critical services first
3. **Ignition Gateway** - Graceful SCADA shutdown
4. **AI & API Services** - Stop processing services
5. **Message Brokers** - Stop RabbitMQ and MQTT
6. **Databases** - Stop PostgreSQL and Redis last
7. **Verification** - Confirm clean shutdown

```bash
./run-demo.sh down shutdown
```

#### `cleanup` - Complete Environment Reset
⚠️ **DESTRUCTIVE**: Removes ALL data including Docker volumes!

1. **Warning & Confirmation** - Clear data loss warning
2. **Force Stop** - Stop all containers immediately
3. **Remove Containers** - Delete containers and networks
4. **Delete Volumes** - **PERMANENT DATA LOSS**
5. **System Cleanup** - Prune Docker system
6. **Verification** - Confirm complete cleanup

```bash
./run-demo.sh down cleanup
# Will prompt for confirmation before data deletion
```

## 🎯 Presentation Mode

For live presentations, use these optimized commands:

```bash
# Fast startup demo (no typewriter delay)
./run-demo.sh up startup --immediate

# Automatic health check
./run-demo.sh up health --auto --immediate

# Fast shutdown demo
./run-demo.sh down shutdown --immediate
```

## 🔧 Demo Framework Options

All demos support these options from the saschagrunert/demo framework:

| Option | Description |
|--------|-------------|
| `--auto` | Run automatically without pausing between steps |
| `--dry-run` | Show commands without executing them |
| `--immediate` | Skip typewriter animation for faster display |
| `--no-color` | Disable colored output |
| `--continue-on-error` | Continue demo even if a step fails |
| `--skip-steps N` | Skip the first N steps |
| `--auto-timeout 2s` | Set timeout between auto steps |

## 🌐 Service Access URLs

After successful startup, access services at:

### 🏭 Ignition SCADA Gateway
- **HTTPS**: https://localhost:9043 (recommended)
- **HTTP**: http://localhost:9088
- **Credentials**: admin / (see `secrets/GATEWAY_ADMIN_PASSWORD`)

### 📊 Monitoring & Dashboards
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Netdata**: http://localhost:19999 (real-time monitoring)
- **Portainer**: http://localhost:9000 (Docker management)

### 🔧 Infrastructure Services
- **RabbitMQ**: http://localhost:15672 (user/password)
- **MQTT Web UI**: http://localhost:18083 (admin/public)
- **AI/RAG Service**: http://localhost:8085

## 🚨 Troubleshooting

### Demo Won't Start
```bash
# Check Go version
go version  # Should be 1.25+

# Rebuild demos
rm demo-stack-up demo-stack-down
./run-demo.sh up  # Will auto-rebuild
```

### Services Not Starting
```bash
# Check prerequisites
./scripts/demo-preflight.sh

# Run health check
./run-demo.sh up health

# Check Docker
docker compose ps
docker compose logs [service-name]
```

### License Issues
The demos automatically handle license acceptance via:
- `ACCEPT_IGNITION_EULA=Y` in docker-compose.yml
- Self-signed certificates are auto-trusted
- No manual intervention required

### Complete Reset
```bash
# Nuclear option - removes ALL data
./run-demo.sh down cleanup
# Then restart fresh
./run-demo.sh up startup
```

## 🎬 Demo Flow for Presentations

### Recommended Presentation Sequence

1. **Introduction** (2 min)
   ```bash
   ./run-demo.sh up startup --immediate
   ```

2. **Show Running Stack** (1 min)
   ```bash
   ./run-demo.sh up health --auto --immediate
   ```

3. **Demonstrate Features** (10-15 min)
   - Open Ignition Gateway: https://localhost:9043
   - Show Grafana dashboards: http://localhost:3000
   - Demo AI responses: http://localhost:8085

4. **Clean Shutdown** (1 min)
   ```bash
   ./run-demo.sh down shutdown --immediate
   ```

### Pre-Presentation Checklist

- [ ] Run `./scripts/demo-preflight.sh` to verify setup
- [ ] Test full demo cycle: `up startup` → `up health` → `down shutdown`
- [ ] Verify all service URLs are accessible
- [ ] Check secrets are in place
- [ ] Ensure stable internet connection for Docker pulls

## 📝 Customization

### Adding New Demo Steps

Edit `demo-stack-up.go` or `demo-stack-down.go`:

```go
// Add new step to existing demo
r.Step(demo.S(
    "📝 Your step description",
    "Additional context lines...",
), demo.S(
    "echo 'Your command here'",
    "docker compose ps",
))
```

### Creating New Demo Runs

```go
// Add to main() function
d.Add(yourNewDemo(), "new-demo", "Description of new demo")

// Create the demo function
func yourNewDemo() *demo.Run {
    r := demo.NewRun("Demo Title", "Description...")
    // Add steps...
    return r
}
```

## 🔗 Related Documentation

- [DOCKER-SERVICES.md](docs/DOCKER-SERVICES.md) - Service architecture
- [IGNITION-DOCKER-SETUP.md](IGNITION-DOCKER-SETUP.md) - Ignition configuration
- [SECRETS-QUICKSTART.md](SECRETS-QUICKSTART.md) - Secrets management
- [TALK-RUNBOOK.md](TALK-RUNBOOK.md) - Presentation guide

## 🤝 Contributing

To add new demo scenarios:

1. Create new demo functions in the Go files
2. Add them to the main demo registration
3. Test with `--dry-run` first
4. Update this README with new options

## 📄 License

MIT License - See LICENSE file for details.

---

**🎯 Ready to demo? Start with: `./run-demo.sh up`**
