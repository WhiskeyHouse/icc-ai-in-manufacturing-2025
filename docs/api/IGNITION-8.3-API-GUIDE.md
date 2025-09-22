# Ignition 8.3 REST API Guide

This guide covers the REST API features introduced in Ignition 8.3 and how to use them with your containerized setup.

## Overview

Ignition 8.3 introduces a comprehensive REST API that allows for:
- Programmatic configuration management
- Remote monitoring and control
- Integration with external systems
- Automated deployment and DevOps workflows

## API Access

### Base URLs
- **HTTP**: `http://localhost:9088`
- **HTTPS**: `https://localhost:9043`
- **API Documentation**: `http://localhost:9088/openapi`

### Authentication

Ignition 8.3 uses the `X-Ignition-API-Token` header for authentication:

```bash
# Using API token in header (correct method)
curl -X GET "http://localhost:9088/data/api/v1/gateway-info" \
  -H "X-Ignition-API-Token: mcp2:6uAHjHhz8FaYm654IgcTNSVWV4cukaFuXED0CvGGuBE"
```

**Note**: Replace the API token with your actual token. You can find it in the Ignition Gateway web interface under Configuration > Security > API Keys.

## Core API Endpoints

### Gateway Management

#### Get Gateway Information
```bash
curl -X GET "http://localhost:9088/data/api/v1/gateway-info" \
  -H "X-Ignition-API-Token: YOUR_API_TOKEN"
```

#### Get Gateway Overview
```bash
curl -X GET "http://localhost:9088/data/api/v1/overview" \
  -H "X-Ignition-API-Token: YOUR_API_TOKEN"
```

#### Get Gateway Connections
```bash
curl -X GET "http://localhost:9088/data/api/v1/overview/connections" \
  -H "X-Ignition-API-Token: YOUR_API_TOKEN"
```

### Project Management

#### List Projects
```bash
curl -X GET "http://localhost:9088/data/api/v1/projects/list" \
  -H "X-Ignition-API-Token: YOUR_API_TOKEN"
```

#### Get Project Names
```bash
curl -X GET "http://localhost:9088/data/api/v1/projects/names" \
  -H "X-Ignition-API-Token: YOUR_API_TOKEN"
```

#### Find Project
```bash
curl -X GET "http://localhost:9088/data/api/v1/projects/find/{project_name}" \
  -H "X-Ignition-API-Token: YOUR_API_TOKEN"
```

#### Export Project
```bash
curl -X GET "http://localhost:9088/data/api/v1/projects/export/{project_name}" \
  -H "X-Ignition-API-Token: YOUR_API_TOKEN" \
  -o "project_export.zip"
```

#### Import Project
```bash
curl -X POST "http://localhost:9088/data/api/v1/projects/import/{project_name}" \
  -H "X-Ignition-API-Token: YOUR_API_TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@project_export.zip"
```

### Tag Management

#### Get Tag Configuration
```bash
curl -X GET "http://localhost:9088/data/tags" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Create Tag
```bash
curl -X POST "http://localhost:9088/data/tags" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Tank1_Level",
    "tagType": "MEMORY",
    "dataType": "Float4",
    "value": 0.0
  }'
```

#### Read Tag Values
```bash
curl -X GET "http://localhost:9088/data/tags/read" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -G -d "tags=Tank1_Level,Tank2_Level"
```

#### Write Tag Values
```bash
curl -X POST "http://localhost:9088/data/tags/write" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '[
    {
      "tagPath": "Tank1_Level",
      "value": 75.5
    }
  ]'
```

### Module Management

#### List Installed Modules
```bash
curl -X GET "http://localhost:9088/data/modules" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Install Module
```bash
curl -X POST "http://localhost:9088/data/modules/install" \
  -H "Content-Type: multipart/form-data" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@module.modl"
```

### Backup and Restore

#### Create Backup
```bash
curl -X POST "http://localhost:9088/data/backup/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "api_backup_$(date +%Y%m%d_%H%M%S)",
    "description": "Backup created via API"
  }'
```

#### Download Backup
```bash
curl -X GET "http://localhost:9088/data/backup/download/{backup_id}" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o "gateway_backup.gwbk"
```

#### Restore from Backup
```bash
curl -X POST "http://localhost:9088/data/backup/restore" \
  -H "Content-Type: multipart/form-data" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@gateway_backup.gwbk"
```

## Practical Examples

### 1. Automated Project Deployment

```bash
#!/bin/bash
# deploy-project.sh

API_BASE="http://localhost:9088"
PROJECT_NAME="ProductionHMI"
TOKEN="your_token_here"

echo "🚀 Deploying project: ${PROJECT_NAME}"

# Upload project
curl -X POST "${API_BASE}/data/projects/${PROJECT_NAME}/import" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@${PROJECT_NAME}.zip"

# Enable project
curl -X PUT "${API_BASE}/data/projects/${PROJECT_NAME}/enabled" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

echo "✅ Project deployed successfully"
```

### 2. Health Check Monitoring

```bash
#!/bin/bash
# health-check.sh

API_BASE="http://localhost:9088"
TOKEN="your_token_here"

# Check gateway status
STATUS=$(curl -s -X GET "${API_BASE}/data/gateway/status" \
  -H "Authorization: Bearer ${TOKEN}" | jq -r '.status')

if [ "$STATUS" = "RUNNING" ]; then
    echo "✅ Gateway is healthy"
    exit 0
else
    echo "❌ Gateway unhealthy: ${STATUS}"
    exit 1
fi
```

### 3. Configuration Backup Automation

```bash
#!/bin/bash
# auto-backup.sh

API_BASE="http://localhost:9088"
TOKEN="your_token_here"
BACKUP_DIR="./ignition-backups"

# Create timestamped backup
BACKUP_NAME="auto_backup_$(date +%Y%m%d_%H%M%S)"

echo "📦 Creating backup: ${BACKUP_NAME}"

# Create backup via API
BACKUP_ID=$(curl -s -X POST "${API_BASE}/data/backup/create" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"${BACKUP_NAME}\"}" | jq -r '.backupId')

# Download backup
curl -X GET "${API_BASE}/data/backup/download/${BACKUP_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -o "${BACKUP_DIR}/${BACKUP_NAME}.gwbk"

echo "✅ Backup saved: ${BACKUP_DIR}/${BACKUP_NAME}.gwbk"
```

## Integration with Docker Setup

### Environment Variables
Your `.env` file includes these API-related variables:
```bash
IGNITION_API_ENABLED=true
IGNITION_API_USER=admin
IGNITION_API_TOKEN_EXPIRY=3600
```

### Volume Mappings
The docker-compose.yml maps these directories for API access:
- `./ignition-config` → Gateway configuration (JSON files)
- `./ignition-projects` → Project files (JSON format)
- `./ignition-backups` → Backup files

### Setup Script Usage
```bash
# Run the setup script
./scripts/api/setup-ignition-api.sh

# Initialize git integration
./scripts/git-integration.sh

# Create backup
./scripts/backup-ignition.sh
```

## Security Best Practices

### 1. Use HTTPS in Production
```bash
# Always use HTTPS for production
API_BASE="https://localhost:9043"
```

### 2. Secure API Keys
```bash
# Store API keys securely
export IGNITION_API_KEY=$(cat /secure/path/api_key)
```

### 3. Token Rotation
```bash
# Implement token rotation
curl -X POST "${API_BASE}/data/auth/refresh" \
  -H "Authorization: Bearer ${OLD_TOKEN}"
```

### 4. IP Restrictions
Configure IP allowlists in Ignition gateway settings:
```json
{
  "allowedIPs": ["192.168.1.0/24", "10.0.0.0/8"],
  "denyByDefault": true
}
```

## Error Handling

### Common HTTP Status Codes
- `200` - Success
- `400` - Bad Request (invalid JSON/parameters)
- `401` - Unauthorized (invalid credentials)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (endpoint/resource doesn't exist)
- `500` - Internal Server Error

### Example Error Response
```json
{
  "error": {
    "code": "INVALID_PROJECT_NAME",
    "message": "Project name contains invalid characters",
    "details": "Project names must contain only alphanumeric characters and underscores"
  }
}
```

## Troubleshooting

### API Not Accessible
1. Check if Ignition is running: `docker compose ps`
2. Verify port mapping: `docker compose port ignition 8088`
3. Check firewall settings
4. Review Ignition logs: `docker compose logs ignition`

### Authentication Issues
1. Verify credentials
2. Check token expiry
3. Ensure proper headers
4. Review gateway user permissions

### JSON Configuration Issues
1. Validate JSON syntax
2. Check file permissions
3. Verify volume mappings
4. Review gateway logs for errors

## Additional Resources

- [Ignition 8.3 API Documentation](http://localhost:9088/openapi)
- [Secrets Management Quick Start](./SECRETS-QUICKSTART.md) - Get secure secrets running in 5 minutes
- [Complete Secrets Management Guide](./IGNITION-SECRETS-GUIDE.md) - Full secrets documentation
- [Git Workflow Guide](./GIT-WORKFLOW.md)
- [Inductive Automation User Manual](https://docs.inductiveautomation.com/)
- [Ignition Forum](https://forum.inductiveautomation.com/)

## Scripts and Automation

The following scripts are available in this setup:
- `./scripts/api/setup-ignition-api.sh` - Initial API setup
- `./scripts/git-integration.sh` - Git version control setup
- `./scripts/backup-ignition.sh` - Automated backup creation
- `./scripts/deploy-project.sh` - Project deployment automation

Run any script with `--help` for usage information.