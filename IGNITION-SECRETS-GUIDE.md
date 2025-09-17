# Ignition 8.3 Secrets Management Guide

This guide covers the comprehensive secrets management setup for Ignition 8.3, including Docker integration and automated workflows.

## Overview

Ignition 8.3 introduces a new Secrets Management system that:
- **Removes passwords from configuration files**
- **Stores sensitive data securely** 
- **Integrates with external secret providers**
- **Provides API access for automation**
- **Supports Docker secrets** out of the box

## Architecture

### Secret Providers
- **Internal Provider**: Secrets stored in Ignition's internal database (encrypted)
- **Docker Secrets**: Integration with Docker Compose secrets
- **Environment Variables**: Read secrets from environment variables
- **External Providers**: Future integration with HashiCorp Vault, Azure Key Vault, etc.

### Our Setup
```
Docker Secrets → Ignition Secret Providers → Gateway Resources
     ↓                    ↓                        ↓
Secret Files         API Management         Database Connections
Environment Vars     Automated Sync         Email Profiles  
                                           MQTT Connections
```

## Docker Secrets Configuration

### Secret Files Structure
```
secrets/
├── GATEWAY_ADMIN_PASSWORD      # Gateway admin password
├── IGNITION_DB_PASSWORD       # Database connection password
├── IGNITION_API_SECRET        # External API authentication
├── IGNITION_EMAIL_PASSWORD    # SMTP server password
├── IGNITION_MQTT_PASSWORD     # MQTT broker password
└── POSTGRES_PASSWORD          # PostgreSQL password
```

### Docker Compose Integration
Our `docker-compose.yml` includes:
```yaml
services:
  ignition:
    secrets:
      - gateway-admin-password
      - ignition-db-password
      - ignition-api-secret
      - ignition-email-password
      - ignition-mqtt-password
    environment:
      # Secret file paths inside container
      - IGNITION_DB_PASSWORD_FILE=/run/secrets/ignition-db-password
      - IGNITION_API_SECRET_FILE=/run/secrets/ignition-api-secret
      - IGNITION_EMAIL_PASSWORD_FILE=/run/secrets/ignition-email-password
      - IGNITION_MQTT_PASSWORD_FILE=/run/secrets/ignition-mqtt-password

secrets:
  ignition-db-password:
    file: secrets/IGNITION_DB_PASSWORD
  ignition-api-secret:
    file: secrets/IGNITION_API_SECRET
  # ... other secrets
```

## API Endpoints

### Secret Providers Management

#### List Secret Providers
```bash
curl -H "X-Ignition-API-Token: YOUR_TOKEN" \
  "http://localhost:9088/data/api/v1/resources/list/ignition/secret-provider"
```

#### Get Provider Details
```bash
curl -H "X-Ignition-API-Token: YOUR_TOKEN" \
  "http://localhost:9088/data/api/v1/resources/find/ignition/secret-provider/Docker%20Secrets"
```

#### Create Secret Provider
```bash
curl -X POST \
  -H "X-Ignition-API-Token: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Secret Provider",
    "description": "Custom secret provider",
    "enabled": true,
    "config": {
      "profile": {
        "type": "internal"
      },
      "settings": {
        "secrets": {}
      }
    }
  }' \
  "http://localhost:9088/data/api/v1/resources/ignition/secret-provider"
```

### Secrets Management

#### List Secrets in Provider
```bash
curl -H "X-Ignition-API-Token: YOUR_TOKEN" \
  "http://localhost:9088/data/api/v1/secret-providers/Docker%20Secrets/secrets"
```

#### Create Secret
```bash
curl -X POST \
  -H "X-Ignition-API-Token: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "database_password",
    "value": "secure_password_here"
  }' \
  "http://localhost:9088/data/api/v1/secret-providers/Docker%20Secrets/secrets"
```

#### Update Secret
```bash
curl -X PUT \
  -H "X-Ignition-API-Token: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "value": "new_secure_password"
  }' \
  "http://localhost:9088/data/api/v1/secret-providers/Docker%20Secrets/secrets/database_password"
```

#### Delete Secret
```bash
curl -X DELETE \
  -H "X-Ignition-API-Token: YOUR_TOKEN" \
  "http://localhost:9088/data/api/v1/secret-providers/Docker%20Secrets/secrets/database_password"
```

## Automation Scripts

### 1. Setup Script (`./scripts/secrets/setup-secrets.sh`)
Automatically configures secrets when Ignition starts:
- Creates secret providers
- Syncs Docker secrets to Ignition
- Syncs environment variables
- Creates example configurations

```bash
# Run during container startup
./scripts/secrets/setup-secrets.sh
```

### 2. Management Script (`./scripts/secrets/manage-secrets.sh`)
Interactive secrets management:

```bash
# List all providers
./scripts/secrets/manage-secrets.sh list-providers

# List secrets in a provider
./scripts/secrets/manage-secrets.sh list-secrets "Docker Secrets"

# Create a new secret
./scripts/secrets/manage-secrets.sh create "Docker Secrets" "my_secret" "secret_value"

# Update existing secret
./scripts/secrets/manage-secrets.sh update "Docker Secrets" "my_secret" "new_value"

# Delete a secret
./scripts/secrets/manage-secrets.sh delete "Docker Secrets" "my_secret"

# Sync all Docker secrets
./scripts/secrets/manage-secrets.sh sync-docker "Docker Secrets"

# Sync environment variables
./scripts/secrets/manage-secrets.sh sync-env "Environment Variables"

# Sync everything
./scripts/secrets/manage-secrets.sh sync-all "Docker Secrets"
```

## Using Secrets in Ignition Resources

### Database Connection Example
```json
{
  "name": "SecureDatabase",
  "driverName": "PostgreSQL",
  "connectUrl": "jdbc:postgresql://db:5432/ignition",
  "username": "admin",
  "password": {
    "secretProvider": "Docker Secrets",
    "secretName": "database_password"
  },
  "validationQuery": "SELECT 1"
}
```

### Email Profile Example
```json
{
  "name": "SecureEmailProfile",
  "smtpServer": "smtp.gmail.com",
  "smtpPort": 587,
  "username": "noreply@yourdomain.com",
  "password": {
    "secretProvider": "Docker Secrets", 
    "secretName": "smtp_password"
  },
  "useSSL": true,
  "useAuth": true
}
```

### MQTT Connection Example
```json
{
  "name": "SecureMQTTConnection",
  "brokerUrl": "tcp://mqtt-broker:1883",
  "username": "mqtt_user",
  "password": {
    "secretProvider": "Docker Secrets",
    "secretName": "mqtt_password"
  },
  "clientId": "ignition_gateway"
}
```

## Security Best Practices

### 1. Secret File Permissions
```bash
# Ensure secret files have restricted permissions
chmod 600 secrets/*
chown root:root secrets/*
```

### 2. Secret Rotation
```bash
# Update secret file
echo "new_password" > secrets/IGNITION_DB_PASSWORD

# Restart container to reload secrets
docker compose restart ignition

# Update secret in Ignition
./scripts/secrets/manage-secrets.sh sync-docker "Docker Secrets"
```

### 3. Environment-Specific Secrets
```bash
# Development
secrets/
├── dev/
│   ├── IGNITION_DB_PASSWORD
│   └── IGNITION_API_SECRET

# Production  
└── prod/
    ├── IGNITION_DB_PASSWORD
    └── IGNITION_API_SECRET
```

### 4. Backup and Recovery
```bash
# Backup secrets configuration
curl -H "X-Ignition-API-Token: YOUR_TOKEN" \
  "http://localhost:9088/data/api/v1/resources/list/ignition/secret-provider" \
  > secrets-backup.json

# Include secrets in gateway backup
./scripts/backup-ignition.sh
```

## Monitoring and Auditing

### 1. Secret Provider Health
```bash
# Check provider status
curl -H "X-Ignition-API-Token: YOUR_TOKEN" \
  "http://localhost:9088/data/api/v1/resources/list/ignition/secret-provider" | \
  jq '.items[] | {name, enabled, type: .config.profile.type}'
```

### 2. Secret Usage Monitoring
```bash
# Monitor which resources use secrets
grep -r "secretProvider" ./ignition-config/
```

### 3. Audit Log Integration
- Enable audit logging in Ignition
- Monitor secret access and modifications
- Set up alerts for unauthorized secret access

## Troubleshooting

### Common Issues

#### 1. Secret Not Found
```bash
# Check if secret exists
./scripts/secrets/manage-secrets.sh list-secrets "Docker Secrets"

# Verify secret file exists
ls -la secrets/IGNITION_DB_PASSWORD

# Check Docker secret mounting
docker exec ignition-container ls -la /run/secrets/
```

#### 2. Permission Denied
```bash
# Check file permissions
ls -la secrets/

# Fix permissions
chmod 600 secrets/*
sudo chown root:docker secrets/*
```

#### 3. API Authentication Failed
```bash
# Verify API token
curl -H "X-Ignition-API-Token: YOUR_TOKEN" \
  "http://localhost:9088/data/api/v1/gateway-info"

# Check token in environment
echo $IGNITION_API_KEY
```

#### 4. Provider Not Available
```bash
# Restart Ignition service
docker compose restart ignition

# Check Ignition logs
docker compose logs ignition | grep -i secret
```

### Debug Mode
```bash
# Enable debug logging for secrets
export IGNITION_DEBUG_SECRETS=true

# Run scripts with verbose output
bash -x ./scripts/secrets/manage-secrets.sh list-providers
```

## Migration from Legacy Setup

### 1. Identify Hard-coded Passwords
```bash
# Find configuration files with passwords
grep -r "password" ./ignition-config/ --include="*.json"
```

### 2. Extract to Secrets
```bash
# For each password found:
# 1. Create secret file
echo "extracted_password" > secrets/NEW_SECRET_NAME

# 2. Add to docker-compose.yml
# 3. Update configuration to reference secret
# 4. Test the connection
```

### 3. Validate Migration
```bash
# Test all connections using secrets
./scripts/test-connections.sh

# Verify no plain-text passwords remain
grep -r "password.*:" ./ignition-config/ --include="*.json" | grep -v secretProvider
```

## Advanced Configuration

### Custom Secret Provider
```json
{
  "name": "External Vault",
  "description": "HashiCorp Vault integration",
  "enabled": true,
  "config": {
    "profile": {
      "type": "external",
      "vaultUrl": "https://vault.company.com",
      "authMethod": "token"
    },
    "settings": {
      "refreshInterval": 3600,
      "cachingEnabled": true
    }
  }
}
```

### Deployment-Specific Secrets
```yaml
# docker-compose.override.yml for production
services:
  ignition:
    secrets:
      - production-db-password
      - production-api-key
    environment:
      - IGNITION_DEPLOYMENT_MODE=production

secrets:
  production-db-password:
    external: true
    name: prod_ignition_db_password
```

## Integration Examples

### CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
- name: Deploy Secrets
  run: |
    echo "${{ secrets.IGNITION_DB_PASSWORD }}" > secrets/IGNITION_DB_PASSWORD
    echo "${{ secrets.IGNITION_API_SECRET }}" > secrets/IGNITION_API_SECRET
    docker compose up -d
    ./scripts/secrets/setup-secrets.sh
```

### Kubernetes Integration
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ignition-secrets
data:
  database-password: <base64-encoded-password>
  api-secret: <base64-encoded-secret>
```

This comprehensive secrets management setup ensures your Ignition 8.3 gateway operates with enterprise-grade security while maintaining automation and ease of management.