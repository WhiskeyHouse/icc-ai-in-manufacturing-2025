# 🏭 WHK Full Stack Demo Guide

## 🎯 Overview

The **WHK Full Stack Demo** showcases a complete manufacturing and AI infrastructure alongside production-validated Ignition linting capabilities. This comprehensive demonstration spins up the entire WHK services ecosystem and integrates it with real-world code quality validation.

## 🚀 Quick Start

### One-Command Demo
```bash
# Full automated demo - complete infrastructure + linting
./run-full-stack-demo.sh --auto

# Interactive demo with user control
./run-full-stack-demo.sh

# Services only (no linting demo)
./run-full-stack-demo.sh --services-only
```

### Direct Python Execution
```bash
# Full interactive demo
uv run python demo-full-stack.py

# Automated mode
uv run python demo-full-stack.py --auto

# Services only
uv run python demo-full-stack.py --services-only

# Cleanup services
uv run python demo-full-stack.py --cleanup
```

## 🏗️ Infrastructure Architecture

### 🌐 **API & Gateway Layer**
- **Kong API Gateway** (Port 8000) - Routes all API traffic with rate limiting and authentication

### 🏭 **Industrial Automation**
- **Ignition SCADA** (Port 9088) - Complete industrial automation platform
  - Real-time data collection and historian
  - HMI/SCADA interfaces
  - Tag management and trending

### 💾 **Data Layer**
- **PostgreSQL** (Port 5432) - Primary application database
- **Vector Database** (Port 6333) - AI/ML embeddings and semantic search
- **Redis Cache** (Port 6379) - High-performance caching and session storage

### 📡 **Messaging & Communication**
- **RabbitMQ** (Port 5672, 15672) - Message queuing and asynchronous processing
- **MQTT Broker** (Port 1883) - IoT device communication and real-time telemetry

### 📊 **Monitoring & Management**
- **Prometheus** (Port 9090) - Metrics collection and time-series database
- **Grafana** (Port 3000) - Visualization dashboards and alerting
- **Portainer** (Port 9443) - Container management and Docker administration

## 🎬 Demo Flow

### 1. **Prerequisites Check** (30 seconds)
- ✅ Docker and Docker Compose availability
- ✅ WHK services directory validation
- ✅ Environment configuration check
- ✅ Linting tools verification

### 2. **Architecture Overview** (60 seconds)
- 🏗️ Complete infrastructure explanation
- 🔗 Service integration points
- 🌐 Access URLs and ports
- 📊 Monitoring capabilities

### 3. **Service Deployment** (2-5 minutes)
- 🚀 Docker Compose stack startup
- 🏥 Health check validation
- 📋 Service status verification
- 🌐 Access URL confirmation

### 4. **Linting Integration** (2-3 minutes)
- 🔍 Production code validation
- 📊 Real distillery project analysis
- 🎯 Quality metrics demonstration
- 🤖 AI-assisted development showcase

### 5. **Integration Benefits** (60 seconds)
- 🔗 Service interconnection explanation
- 🎯 Complete solution benefits
- 🏭 Manufacturing-focused advantages
- 📈 Scalability and security features

**Total Demo Time: 6-10 minutes** (depending on service startup)

## 📊 Real Production Scale

### WHK Distillery Project Integration
```
🏭 Real Production Code Analysis:
• 1,347 Python script files
• 552,399 lines of code
• 8,153 total issues identified
• 53 critical issues requiring attention
• 226 Perspective view files
• 2,660 UI components validated
• 95.7% schema compliance rate
```

### Infrastructure Scale
```
🌐 Complete Services Stack:
• 10+ microservices deployed
• Full monitoring and observability
• Production-ready security configuration
• Automatic service discovery
• Comprehensive health checking
• Real-time metrics collection
```

## 🔗 Service Access URLs

Once the demo is running, access these services:

| Service | URL | Purpose |
|---------|-----|---------|
| **Ignition Gateway** | http://localhost:9088 | Industrial automation platform |
| **Grafana Dashboards** | http://localhost:3000 | Visualization and monitoring |
| **Prometheus Metrics** | http://localhost:9090 | Metrics and time-series data |
| **RabbitMQ Management** | http://localhost:15672 | Message queue administration |
| **Portainer** | https://localhost:9443 | Container management UI |
| **Kong Admin** | http://localhost:8011 | API gateway administration |

## 🎯 Demo Modes

### 🎪 **Interactive Mode** (Default)
- User-controlled progression through demo sections
- Detailed explanations at each step
- Ability to pause and explore services
- Perfect for learning and exploration

### 🤖 **Auto Mode** (`--auto`)
- Continuous execution without user prompts
- 3-second pauses for readability
- Complete demo in 6-10 minutes
- Ideal for presentations and CI/CD

### 🔧 **Services Only** (`--services-only`)
- Starts infrastructure without linting demo
- Quick service deployment
- Perfect for development environments
- Leaves services running for exploration

### 🧹 **Cleanup Mode** (`--cleanup`)
- Stops all running services
- Cleans up Docker resources
- Safe shutdown of infrastructure
- Returns system to clean state

## 🎯 Key Integration Points

### 🏭 **Ignition ↔ Database Integration**
- Real-time tag data storage in PostgreSQL
- Historical trending and analytics
- Advanced reporting capabilities

### 🤖 **AI/ML ↔ Vector Database**
- Semantic search for intelligent automation
- Smart tag discovery and recommendations
- Predictive maintenance capabilities

### 📡 **MQTT ↔ Ignition Gateway**
- IoT device integration and connectivity
- Real-time telemetry and monitoring
- Edge computing capabilities

### 📊 **Monitoring ↔ All Services**
- Comprehensive observability stack
- Performance monitoring and alerting
- Health checks and proactive notifications

### 🔍 **Linting ↔ Development Workflow**
- Automated code quality validation
- Production-validated rules and standards
- AI-assisted development integration

## 🎯 Benefits Demonstrated

### 🏭 **Industrial-Grade Infrastructure**
- Production-ready service configuration
- Comprehensive security controls
- Scalable microservices architecture
- Manufacturing-focused design

### 🤖 **AI-Ready Platform**
- Vector database for ML workloads
- Semantic search capabilities
- Intelligent automation infrastructure
- Real-time data processing

### 🔍 **Quality Assurance**
- Production-validated linting rules
- Zero false positives on critical systems
- Automated code quality checks
- AI-assisted development workflow

### 📊 **Full Observability**
- Comprehensive metrics collection
- Real-time monitoring dashboards
- Proactive alerting and notifications
- Complete system visibility

## 🚀 Usage Scenarios

### 🎪 **Live Presentations**
```bash
./run-full-stack-demo.sh --auto
# Perfect for conferences, sales demos, training sessions
```

### 🏭 **Development Environment**
```bash
./run-full-stack-demo.sh --services-only
# Quick infrastructure setup for development work
```

### 🧪 **Testing and Validation**
```bash
uv run python demo-full-stack.py --auto
# Automated testing of complete stack functionality
```

### 📚 **Training and Onboarding**
```bash
./run-full-stack-demo.sh
# Interactive learning experience for new team members
```

## 🔧 Prerequisites

### Required Software
- ✅ **Docker** - Container runtime
- ✅ **Docker Compose** - Multi-container orchestration
- ✅ **UV** - Python package management
- ✅ **Python 3.13** - Runtime environment

### Required Repositories
- ✅ **Current Project** - Linting tools and demo scripts
- ✅ **WHK Services** - `../whk-services-deployments/` directory
- ✅ **Distillery Project** - `../whk-distillery01-ignition-global/` (optional)

### System Resources
- **Memory**: 4GB+ recommended for full stack
- **Storage**: 2GB+ for Docker images
- **Network**: Internet access for image downloads

## 🐛 Troubleshooting

### Common Issues

#### **Services Won't Start**
```bash
# Check Docker daemon
docker info

# Check available ports
netstat -an | grep -E "(8000|9088|3000|5432)"

# Check Docker Compose file
cd ../whk-services-deployments && docker compose config
```

#### **Port Conflicts**
```bash
# Stop conflicting services
docker compose down

# Check what's using ports
lsof -i :9088  # Check Ignition port
lsof -i :3000  # Check Grafana port
```

#### **Memory Issues**
```bash
# Check Docker resources
docker system df

# Clean up unused resources
docker system prune -f
```

### Debug Commands
```bash
# Check service logs
cd ../whk-services-deployments
docker compose logs ignition
docker compose logs kong
docker compose logs grafana

# Check service health
docker compose ps
docker compose top

# Manual cleanup
docker compose down --volumes --remove-orphans
```

## 📈 Performance Expectations

### Service Startup Times
- **Database Services**: 30-60 seconds
- **Ignition Gateway**: 60-120 seconds
- **Monitoring Stack**: 30-45 seconds
- **API Gateway**: 15-30 seconds

### Resource Usage
- **Memory**: 2-4GB total for full stack
- **CPU**: Moderate during startup, low at idle
- **Storage**: 1-2GB for images and data

### Network Requirements
- **Initial Setup**: Internet for image downloads
- **Runtime**: Local network only
- **Bandwidth**: Minimal after startup

## 🎉 Success Criteria

After running the demo, you should have:

✅ **Complete Infrastructure** - All services running and healthy  
✅ **Service Access** - All URLs accessible and functional  
✅ **Linting Integration** - Production code validated successfully  
✅ **Monitoring Active** - Dashboards showing real metrics  
✅ **Quality Validation** - Real issues identified and reported  

## 🚀 Next Steps

### For Developers
1. **Explore Services** - Use provided URLs to explore each component
2. **Review Code** - Examine linting results and recommendations
3. **Integrate Workflow** - Add linting to development process
4. **Customize Configuration** - Adapt services for specific needs

### For Operations
1. **Monitor Health** - Use Grafana dashboards for system monitoring
2. **Review Metrics** - Analyze Prometheus data for performance
3. **Plan Scaling** - Consider resource requirements for production
4. **Security Review** - Evaluate security configurations

### For Management
1. **Assess Value** - Review quality improvements from linting
2. **Plan Rollout** - Consider organization-wide implementation
3. **Training Needs** - Identify team training requirements
4. **ROI Analysis** - Calculate benefits of automated quality assurance

---

**🎉 Ready to showcase the complete WHK manufacturing and AI infrastructure with production-validated quality assurance!**

```bash
./run-full-stack-demo.sh --auto
```
