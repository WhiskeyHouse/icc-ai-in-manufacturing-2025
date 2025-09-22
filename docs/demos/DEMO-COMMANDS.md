# Demo Commands & Scripts

## 🚀 Quick Reference Commands

### Essential Demo Commands (Copy-Paste Ready)

```bash
# Navigate to project root
cd /Users/pmannion/Documents/whiskeyhouse/icc-ai-in-manufacturing-2025

# Pre-flight check
./scripts/demo-preflight.sh

# Start entire stack
./scripts/demo-up.sh

# Open all UIs (macOS)
./scripts/demo-open.sh

# Check service health
docker ps | grep -E "(ignition|grafana|kong|rabbitmq|redis|postgres)"

# Stop and cleanup
./scripts/demo-down.sh
```

## 📋 Section-by-Section Demo Commands

### Part 1: Foundation & Setup (0-10 min)

#### Pre-Demo Setup
```bash
# Ensure in correct directory
pwd
# Should output: /Users/pmannion/Documents/whiskeyhouse/icc-ai-in-manufacturing-2025

# Pull latest images (run before presentation)
docker-compose pull

# Remove any existing containers
docker-compose down -v
```

#### Live Demo Commands
```bash
# 1. Preflight checks
./scripts/demo-preflight.sh

# 2. Start stack with timing
time ./scripts/demo-up.sh

# 3. Show services status
echo "🟢 Services Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(ignition|grafana|kong|redis|postgres|mqtt|rabbitmq)"

# 4. Open UIs (macOS)
echo "🌐 Opening UIs..."
open https://localhost:9043    # Ignition Gateway
open http://localhost:3000     # Grafana
open http://localhost:8000     # Kong Proxy
open http://localhost:15672    # RabbitMQ Management
open http://localhost:19999    # Netdata
```

#### Service Health Validation
```bash
# Check Ignition health
curl -k -s https://localhost:9043/status | head -1

# Check Grafana health
curl -s http://localhost:3000/api/health | jq .

# Check Kong health
curl -s http://localhost:8000/ | head -1

# Show container resource usage
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Part 2: AI Context Engineering (10-25 min)

#### RAG System Demo Commands
```bash
# Start RAG service (if not already running)
docker-compose up -d llama-index-service

# Check vector database status
docker exec -it $(docker ps --filter name=vector-db -q) psql -U admin -d whk_vectors -c "SELECT COUNT(*) FROM ignition_knowledge;"

# Test context retrieval API
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Create a fermentation tank control panel following WHK standards",
    "context": "whk-global",
    "limit": 5
  }' | jq .
```

#### MCP Tools Demo Commands
```bash
# Start MCP server
docker-compose up -d ignition-mcp

# Test component validation
curl -X POST http://localhost:8082/validate/perspective \
  -H "Content-Type: application/json" \
  -d '{
    "component": {
      "type": "ia.display.button",
      "props": {
        "text": "Start Pump"
      }
    },
    "context": {
      "project_name": "WHK-Global"
    }
  }' | jq .

# Test script analysis
curl -X POST http://localhost:8082/analyze/jython \
  -H "Content-Type: application/json" \
  -d '{
    "script": "system.tag.writeBlocking([\"\[default\]Equipment/Pump_01/Start\"], [True])",
    "context": {
      "execution_context": "gateway"
    }
  }' | jq .
```

#### Rules Engine Demo Commands
```bash
# Show rules configuration
cat docs/ENHANCED-RULES-ENGINE.md | grep -A 20 "BTN-ADV-001"

# Test rule violation
curl -X POST http://localhost:8082/validate/rules \
  -H "Content-Type: application/json" \
  -d '{
    "component": {
      "type": "ia.display.button",
      "props": {
        "text": "Emergency Stop"
      },
      "events": {
        "onActionPerformed": {
          "config": {
            "script": "system.tag.write(\"[default]Equipment/EmergencyStop\", True)"
          }
        }
      }
    },
    "rules": ["BTN-ADV-001", "SECURITY-001"]
  }' | jq .
```

### Part 3: Advanced Capabilities (25-40 min)

#### Production Learning Demo
```bash
# Show current pattern library
curl -X GET http://localhost:8080/patterns | jq '.patterns | length'

# Add new production pattern
curl -X POST http://localhost:8080/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source_path": "/demo/new_patterns",
    "source_type": "production_update"
  }'

# Re-query with updated patterns
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Create pump control with safety interlocks",
    "context": "whk-global",
    "include_recent": true
  }' | jq .
```

#### Performance Monitoring
```bash
# Show metrics endpoint
curl -s http://localhost:8080/metrics | grep -E "(response_time|cache_hit|validation_success)"

# Show Redis cache stats
docker exec -it $(docker ps --filter name=redis -q) redis-cli INFO | grep -E "(keyspace|memory)"

# Show vector database performance
docker exec -it $(docker ps --filter name=vector-db -q) psql -U admin -d whk_vectors -c "
SELECT 
  schemaname,
  tablename,
  n_tup_ins as inserts,
  n_tup_upd as updates,
  idx_scan as index_scans
FROM pg_stat_user_tables 
WHERE tablename = 'ignition_knowledge';"
```

#### Context Switching Demo
```bash
# Query with WHK-Global context
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Create tank level indicator",
    "context": "whk-global"
  }' | jq '.context_used'

# Query with Reporting context
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Create tank level indicator", 
    "context": "reporting"
  }' | jq '.context_used'
```

## 🎯 AI Prompts for Live Demos

### Component Generation Prompts

#### Fermentation Tank Control Panel
```
Create a Perspective fermentation tank control panel component following WHK standards. 
The component should include:
- Tank level indicator with safety limits
- Temperature monitoring with alarms
- Status indicator with appropriate colors
- Start/stop controls with security roles
- Audit logging for all actions
```

#### Pump Control Interface
```
Generate a pump control interface for whiskey production with the following requirements:
- Start/stop buttons with safety interlocks
- Flow rate display with units
- Pressure monitoring
- Emergency stop capability
- Maintenance scheduling integration
- Compliance with WHK safety standards
```

#### Batch Recipe Selector
```
Design a batch recipe management component that includes:
- Recipe dropdown with validation
- Step progression tracking
- Quality control checkpoints
- FDA audit trail generation
- Operator authentication
- Deviation handling procedures
```

### Script Generation Prompts

#### Gateway Timer Script
```
Write a gateway timer script that monitors pump status every 5 minutes and:
- Checks operational parameters (flow, pressure, temperature)
- Logs anomalies using WHK logging standards
- Updates alert tags for operator notification
- Includes proper error handling
- Follows production coding patterns
```

#### Transform Script
```
Create a transform script for tank level calculation that:
- Converts raw sensor values to engineering units
- Applies calibration factors
- Validates input ranges
- Handles sensor failures gracefully
- Includes performance optimization
```

#### Event Handler Script
```
Generate a button event handler for emergency stop that:
- Executes immediately without confirmation
- Stops all related equipment
- Updates safety systems
- Logs the event with operator details
- Triggers appropriate alarms
```

### Validation Test Prompts

#### Security Violation Test
```json
{
  "type": "ia.display.button",
  "props": {
    "text": "Start Production Line",
    "style": {
      "backgroundColor": "#28a745"
    }
  },
  "events": {
    "onActionPerformed": {
      "config": {
        "script": "system.tag.write('[default]Production/Line_01/Start', True)"
      }
    }
  }
}
```

#### Performance Issue Test
```python
# Inefficient script for validation testing
for i in range(100):
    value = system.tag.read("[default]Tank_" + str(i) + "/Level")
    if value.value > 80:
        system.tag.write("[default]Tank_" + str(i) + "/Alarm", True)
```

## 🔧 Troubleshooting Commands

### Service Recovery
```bash
# Restart individual services
docker-compose restart ignition
docker-compose restart grafana
docker-compose restart kong

# Check service logs
docker-compose logs ignition | tail -20
docker-compose logs grafana | tail -20
docker-compose logs llama-index-service | tail -20

# Force recreate problematic service
docker-compose up -d --force-recreate ignition
```

### Database Issues
```bash
# Check database connectivity
docker exec -it $(docker ps --filter name=db -q) psql -U admin -c "SELECT version();"

# Check vector database
docker exec -it $(docker ps --filter name=vector-db -q) psql -U admin -d whk_vectors -c "SELECT COUNT(*) FROM ignition_knowledge;"

# Reset vector database if needed
docker-compose down vector-db
docker volume rm $(docker volume ls -q | grep vector)
docker-compose up -d vector-db
```

### Network Issues
```bash
# Check port availability
netstat -tuln | grep -E ":(9043|9088|3000|8000|15672|19999|8080|8082)"

# Test container networking
docker network ls
docker network inspect whk-network

# Check DNS resolution
docker exec -it $(docker ps --filter name=ignition -q) nslookup redis
```

### Performance Issues
```bash
# Check system resources
docker system df
docker system events --since 1m

# Monitor container performance
docker stats --no-stream

# Check memory usage
free -h
df -h
```

## 🎬 Demo Reset Commands

### Quick Reset Between Demos
```bash
# Reset Ignition state
docker exec -it $(docker ps --filter name=ignition -q) rm -rf /usr/local/bin/ignition/data/projects/*
docker-compose restart ignition

# Clear Redis cache
docker exec -it $(docker ps --filter name=redis -q) redis-cli FLUSHALL

# Reset demo data
./scripts/load-demo-data.sh
```

### Full Environment Reset
```bash
# Complete cleanup and restart
docker-compose down -v
docker system prune -f
./scripts/demo-up.sh
```

## 📊 Monitoring Commands

### Real-time Metrics
```bash
# Watch container stats
watch -n 2 'docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"'

# Monitor service health
watch -n 5 'curl -s http://localhost:3000/api/health && echo " - Grafana OK" || echo " - Grafana ERROR"'

# Check response times
time curl -s http://localhost:8080/health
time curl -s http://localhost:8082/health
```

### Log Monitoring
```bash
# Follow all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f ignition

# Follow multiple services
docker-compose logs -f ignition grafana kong
```

## 🔍 Debug Commands

### Container Inspection
```bash
# Exec into Ignition container
docker exec -it $(docker ps --filter name=ignition -q) bash

# Check Ignition project files
docker exec -it $(docker ps --filter name=ignition -q) ls -la /usr/local/bin/ignition/data/projects/

# Check Git integration
docker exec -it $(docker ps --filter name=ignition -q) cat /usr/local/bin/ignition/data/git.yaml

# Check environment variables
docker exec -it $(docker ps --filter name=ignition -q) env | grep -E "(IGNITION|GIT)"
```

### Configuration Validation
```bash
# Validate docker-compose file
docker-compose config

# Check secrets
ls -la secrets/
cat secrets/GATEWAY_ADMIN_PASSWORD

# Validate git.yaml
python -c "import yaml; print(yaml.safe_load(open('gw-init/git.yaml')))"
```

## 📱 Mobile/Backup Commands

### Minimal Demo Commands
```bash
# Essential services only
docker-compose up -d ignition grafana kong

# Quick status check
docker ps --filter "status=running" --format "{{.Names}}"

# Basic connectivity test
curl -k -s https://localhost:9043/status || echo "Ignition not ready"
curl -s http://localhost:3000/api/health || echo "Grafana not ready"
```

### Emergency Backup Procedures
```bash
# Save current state
docker commit $(docker ps --filter name=ignition -q) ignition-backup:$(date +%Y%m%d)

# Quick restore if needed
docker run -d --name ignition-backup ignition-backup:$(date +%Y%m%d)

# Export demo data
docker exec $(docker ps --filter name=ignition -q) tar -czf /tmp/demo-backup.tar.gz /usr/local/bin/ignition/data/
docker cp $(docker ps --filter name=ignition -q):/tmp/demo-backup.tar.gz ./demo-backup.tar.gz
```

---

**Usage**: Copy commands directly from this document during the presentation. Commands are tested and ready for immediate execution. Keep this document open in a separate window for quick reference.