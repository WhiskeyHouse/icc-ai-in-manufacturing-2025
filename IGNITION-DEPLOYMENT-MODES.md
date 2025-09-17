# Ignition 8.3 Deployment Modes Guide

This guide covers Ignition 8.3's new deployment modes feature, which allows you to manage multiple environment configurations (development, staging, production) within a single gateway configuration.

## Overview

Ignition 8.3 introduces deployment modes - a revolutionary feature that allows you to define alternative settings for any configuration resource based on the deployment environment. This eliminates the need for separate gateway backups for different environments and provides seamless switching between development, staging, and production configurations.

## Key Benefits

- **Single Gateway Backup**: All environment configurations stored in one backup
- **Seamless Environment Switching**: Switch between modes with a simple restart
- **Environment-Specific Settings**: Different devices, databases, security settings per mode
- **Version Control Friendly**: All configurations stored as JSON files
- **Reduced Configuration Drift**: Same logical resources across all environments

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Ignition Gateway                         │
├─────────────────────────────────────────────────────────────┤
│  Base Configuration (shared across all modes)              │
├─────────────────────────────────────────────────────────────┤
│  Development Mode    │  Staging Mode     │  Production Mode │
│  ├── Simulators     │  ├── Test PLCs    │  ├── Real PLCs   │
│  ├── Local DB       │  ├── Staging DB   │  ├── Prod DB     │
│  ├── Relaxed Auth   │  ├── AD Test      │  ├── AD + MFA    │
│  └── HTTP Only      │  └── SSL Optional │  └── SSL Required │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Modes Configuration

### File Structure
```
ignition-deployment-configs/
├── development/
│   ├── devices/
│   │   └── simulator.json
│   ├── databases/
│   │   └── primary.json
│   ├── security/
│   │   └── settings.json
│   ├── certificates/
│   └── tags/
├── staging/
│   ├── devices/
│   │   └── test_plc.json
│   ├── databases/
│   │   └── primary.json
│   ├── security/
│   │   └── settings.json
│   └── ...
└── production/
    ├── devices/
    │   └── production_plc.json
    ├── databases/
    │   └── primary.json
    ├── security/
    │   └── settings.json
    └── ...
```

## Environment Configurations

### Development Mode
- **Purpose**: Local development and testing
- **Devices**: Simulators only
- **Database**: Local development database
- **Security**: Internal authentication, HTTP allowed
- **Session Timeout**: 8 hours
- **SSL**: Disabled for easier testing

**Example Device Configuration:**
```json
{
  "name": "DevelopmentSimulator",
  "deviceType": "Simulator",
  "settings": {
    "deviceCount": 10,
    "updateRate": 1000,
    "simulateErrors": true
  }
}
```

### Staging Mode
- **Purpose**: Integration testing with test hardware
- **Devices**: Test PLCs and mock systems
- **Database**: Staging database with test data
- **Security**: Active Directory integration (test domain)
- **Session Timeout**: 4 hours
- **SSL**: Enabled but with test certificates

**Example Device Configuration:**
```json
{
  "name": "StagingPLC",
  "deviceType": "Modbus TCP",
  "hostName": "test-plc.local",
  "settings": {
    "unitId": 1,
    "zeroBasedNumerics": false
  }
}
```

### Production Mode
- **Purpose**: Live production environment
- **Devices**: Real production hardware
- **Database**: Production database with live data
- **Security**: Full AD integration with IP restrictions
- **Session Timeout**: 1 hour
- **SSL**: Required with production certificates

**Example Device Configuration:**
```json
{
  "name": "ProductionPLC",
  "deviceType": "Modbus TCP",
  "hostName": "192.168.1.100",
  "settings": {
    "unitId": 1,
    "redundancyEnabled": true,
    "backupHost": "192.168.1.101"
  }
}
```

## Setup Instructions

### 1. Initial Setup

Run the setup script to create all deployment mode configurations:

```bash
# Create deployment mode configurations
./scripts/deployment-modes/setup-deployment-modes.sh
```

This will:
- Create directory structure for all modes
- Generate example configurations for each environment
- Set up the initial deployment mode

### 2. Manual Configuration

You can also manually create configurations by copying the examples and modifying them:

```bash
# Create directories
mkdir -p ignition-deployment-configs/{development,staging,production}/{devices,databases,security,certificates,tags}

# Copy and modify configurations as needed
cp examples/development-device.json ignition-deployment-configs/development/devices/
```

### 3. Environment Variables

Update your `.env` file with deployment mode settings:

```bash
# Ignition 8.3 Deployment Modes
IGNITION_DEPLOYMENT_MODES_ENABLED=true
DEPLOYMENT_ENVIRONMENT=development
IGNITION_MODE_SWITCHING_RESTART=true
IGNITION_DEPLOYMENT_JSON_CONFIG=true
```

## Switching Between Modes

### Using the Switch Script

The easiest way to switch modes is using the provided script:

```bash
# Switch to production mode
./scripts/deployment-modes/switch-mode.sh production

# Switch to staging mode with force (no confirmation)
./scripts/deployment-modes/switch-mode.sh staging --force

# Switch without automatic restart
./scripts/deployment-modes/switch-mode.sh development --no-restart
```

### Manual Mode Switching

1. **Update Environment Variable:**
   ```bash
   # Edit .env file
   DEPLOYMENT_ENVIRONMENT=production
   ```

2. **Restart Ignition Container:**
   ```bash
   docker compose restart ignition
   ```

3. **Verify Mode Switch:**
   ```bash
   # Check logs for deployment mode
   docker compose logs ignition | grep -i "deployment"
   ```

## Configuration Examples

### Database Connection (Multi-Mode)

**Development Mode** (`ignition-deployment-configs/development/databases/primary.json`):
```json
{
  "name": "DevelopmentDB",
  "connectUrl": "jdbc:postgresql://db:5432/ignition_dev",
  "username": "admin",
  "password": {
    "secretProvider": "Docker Secrets",
    "secretName": "database_connection_password"
  },
  "maxConnections": 5
}
```

**Production Mode** (`ignition-deployment-configs/production/databases/primary.json`):
```json
{
  "name": "ProductionDB",
  "connectUrl": "jdbc:postgresql://prod-db:5432/ignition_production",
  "username": "prod_user",
  "password": {
    "secretProvider": "Docker Secrets",
    "secretName": "production_database_password"
  },
  "maxConnections": 20,
  "connectionPooling": true
}
```

### Security Settings (Multi-Mode)

**Development** (`ignition-deployment-configs/development/security/settings.json`):
```json
{
  "authMode": "Internal",
  "sessionTimeout": 28800,
  "passwordComplexity": "low",
  "sslEnabled": false,
  "allowHttp": true
}
```

**Production** (`ignition-deployment-configs/production/security/settings.json`):
```json
{
  "authMode": "Active Directory",
  "sessionTimeout": 3600,
  "passwordComplexity": "high",
  "sslEnabled": true,
  "allowHttp": false,
  "ipWhitelist": ["192.168.1.0/24", "10.0.0.0/8"],
  "maxConcurrentSessions": 50
}
```

## API Integration

### Get Current Deployment Mode

```bash
curl -H "X-Ignition-API-Token: $IGNITION_API_KEY" \
  "http://localhost:9088/data/api/v1/gateway-info"
```

### Switch Mode via API

```bash
curl -X PUT \
  -H "X-Ignition-API-Token: $IGNITION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"deploymentMode": "production"}' \
  "http://localhost:9088/data/api/v1/gateway/deployment-mode"
```

## Best Practices

### 1. Configuration Management

- **Keep configurations in version control**: All JSON files should be committed to Git
- **Use descriptive names**: Make resource names indicate their purpose and environment
- **Document differences**: Maintain a README in each mode directory explaining the configuration

### 2. Security Considerations

- **Separate secrets per environment**: Use different secret providers or keys for each mode
- **Progressive security**: Development < Staging < Production security levels
- **IP restrictions**: Use IP whitelisting for production environments

### 3. Testing Workflows

- **Test in development first**: Always validate changes in development mode
- **Staging validation**: Use staging mode for integration testing
- **Production deployment**: Only deploy tested configurations to production

### 4. Automation

- **CI/CD Integration**: Automate deployment mode switching in your pipelines
- **Health checks**: Verify system health after mode switches
- **Rollback procedures**: Have rollback plans for each environment

## Troubleshooting

### Common Issues

#### 1. Mode Switch Fails
```bash
# Check container status
docker compose ps ignition

# Check logs for errors
docker compose logs ignition | tail -50

# Verify environment variable
grep DEPLOYMENT_ENVIRONMENT .env
```

#### 2. Configuration Not Loading
```bash
# Verify configuration files exist
ls -la ignition-deployment-configs/$DEPLOYMENT_ENVIRONMENT/

# Check file permissions
chmod 644 ignition-deployment-configs/**/*.json

# Validate JSON syntax
jq . ignition-deployment-configs/development/databases/primary.json
```

#### 3. API Connection Issues
```bash
# Test API connectivity
curl -H "X-Ignition-API-Token: $IGNITION_API_KEY" \
  "http://localhost:9088/data/api/v1/gateway-info"

# Check if Ignition is ready
./scripts/deployment-modes/switch-mode.sh development --force
```

### Debug Mode

Enable debug logging for deployment modes:

```bash
# Add to .env file
IGNITION_DEBUG_DEPLOYMENT_MODES=true

# Restart container
docker compose restart ignition

# Check debug logs
docker compose logs ignition | grep -i deployment
```

## Integration with Other Features

### Secrets Management

Deployment modes work seamlessly with Ignition's secrets management:

```json
{
  "password": {
    "secretProvider": "Docker Secrets",
    "secretName": "production_database_password"
  }
}
```

### Version Control

All deployment configurations are JSON files, making them perfect for Git:

```bash
# Commit configuration changes
git add ignition-deployment-configs/
git commit -m "Update production database configuration"
```

### Backup and Restore

Deployment mode configurations are included in gateway backups:

```bash
# Create backup with all deployment modes
./scripts/backup-ignition.sh

# Restore will preserve all deployment mode configurations
```

## Advanced Usage

### Custom Deployment Modes

Create additional deployment modes beyond the standard three:

```bash
# Create disaster recovery mode
mkdir -p ignition-deployment-configs/disaster-recovery/{devices,databases,security}

# Configure DR-specific settings
# Update switch script to include new mode
```

### Environment-Specific Modules

Use deployment modes to load different modules per environment:

```json
{
  "modules": {
    "development": ["simulator", "debug-tools"],
    "staging": ["test-connectors"],
    "production": ["production-connectors", "redundancy"]
  }
}
```

## Migration from Legacy Setup

### From Multiple Gateways

If you currently use separate gateways for each environment:

1. **Export configurations** from each gateway
2. **Convert to deployment mode format** using provided scripts
3. **Test in development mode** first
4. **Migrate progressively** from dev → staging → production

### From Manual Configuration

If you manually manage environment differences:

1. **Document current differences** between environments
2. **Create deployment mode configurations** based on documentation
3. **Test switching** between modes in non-production
4. **Validate all resources** work correctly in each mode

## Conclusion

Ignition 8.3's deployment modes revolutionize how SCADA systems are deployed and managed across multiple environments. By leveraging this feature with our Docker setup, you get:

- **Simplified deployment workflows**
- **Reduced configuration drift**
- **Better version control integration**
- **Easier testing and validation**
- **Professional DevOps practices for industrial systems**

The combination of deployment modes, secrets management, and JSON-based configuration makes Ignition 8.3 the most DevOps-friendly SCADA platform available.

---

## Quick Commands Reference

```bash
# Setup deployment modes
./scripts/deployment-modes/setup-deployment-modes.sh

# Switch to development mode
./scripts/deployment-modes/switch-mode.sh development

# Switch to production mode with force
./scripts/deployment-modes/switch-mode.sh production --force

# Check current deployment mode
grep DEPLOYMENT_ENVIRONMENT .env

# View configuration files
ls -la ignition-deployment-configs/development/

# Test API connection
curl -H "X-Ignition-API-Token: $IGNITION_API_KEY" \
  "http://localhost:9088/data/api/v1/gateway-info"
```