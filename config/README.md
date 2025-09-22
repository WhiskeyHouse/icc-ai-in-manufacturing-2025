# Configuration Management

Centralized configuration files for all platform services, organized by service type for easy management and deployment.

## Directory Structure

```
config/
├── kong/           # API Gateway configuration
├── postgres/       # Database initialization scripts
├── rabbitmq/       # Message broker configuration
├── certs/          # SSL certificates and security
├── otel-config.yml # OpenTelemetry configuration
├── newrelic.js     # New Relic monitoring
└── playwright.config.js # Browser automation config
```

## Configuration Categories

### API Gateway (`kong/`)
Kong API Gateway configuration for request routing, authentication, and load balancing.

**Files**:
- `Dockerfile` - Custom Kong image build
- `kong.yaml` - Declarative configuration for routes, services, and plugins

**Key Features**:
- Basic authentication
- Proxy caching
- Rate limiting
- Request/response transformation

### Database (`postgres/`)
PostgreSQL database initialization and setup scripts.

**Files**:
- `Dockerfile` - Custom PostgreSQL image with extensions
- `01-init-vector.sh` - Vector database extension setup
- `init-databases.sql` - Database and user creation

**Features**:
- pgvector extension for AI/ML workloads
- Multiple database setup
- User permissions and security

### Message Broker (`rabbitmq/`)
RabbitMQ configuration for event-driven architecture.

**Files**:
- `Dockerfile` - Custom RabbitMQ image
- `rabbitmq.conf` - Main configuration
- `definitions.json` - Queue and exchange definitions
- `enabled_plugins` - Plugin configuration
- `hash.py` - Password hashing utility

**Features**:
- Management interface
- Custom queue definitions
- Authentication and authorization

### Security (`certs/`)
SSL certificates and security configurations.

**Files**:
- `cert.pem` - SSL certificate
- `key.pem` - Private key

**Security Notes**:
- Self-signed certificates for development
- Production deployments should use proper CA-signed certificates
- Certificates used by Ignition Gateway and other HTTPS services

### Monitoring (`*.yml`, `*.js`)
Application monitoring and observability configurations.

**Files**:
- `otel-config.yml` - OpenTelemetry tracing configuration
- `newrelic.js` - New Relic APM configuration
- `playwright.config.js` - Browser automation test configuration

## Usage

### Environment Variables
Configuration files often reference environment variables:

```bash
# Database configuration
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_USER=admin

# API Gateway
KONG_ADMIN_ACCESS_LOG=/dev/stdout
KONG_ADMIN_ERROR_LOG=/dev/stderr

# Monitoring
NEW_RELIC_LICENSE_KEY=${NEW_RELIC_LICENSE_KEY}
```

### Docker Compose Integration
Configurations are mounted into containers via docker-compose.yml:

```yaml
services:
  kong:
    volumes:
      - ./config/kong/kong.yaml:/usr/local/kong/declarative/kong.yaml
  
  postgres:
    volumes:
      - ./config/postgres/init-databases.sql:/docker-entrypoint-initdb.d/init.sql
  
  rabbitmq:
    volumes:
      - ./config/rabbitmq/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf
```

## Development

### Modifying Configurations

#### Kong API Gateway
```bash
# Edit Kong configuration
vim config/kong/kong.yaml

# Reload Kong configuration (requires restart)
docker compose restart kong

# Verify configuration
curl http://localhost:8001/config
```

#### Database Setup
```bash
# Modify initialization scripts
vim config/postgres/init-databases.sql

# Apply changes (requires volume recreation)
docker compose down -v
docker compose up -d postgres

# Verify changes
docker exec -it $(docker compose ps -q postgres) psql -U admin -l
```

#### RabbitMQ Configuration
```bash
# Edit RabbitMQ configuration
vim config/rabbitmq/rabbitmq.conf

# Update queue definitions
vim config/rabbitmq/definitions.json

# Restart RabbitMQ
docker compose restart rabbitmq

# Verify via management interface
open http://localhost:15672
```

### Configuration Validation

#### Pre-deployment Checks
```bash
# Validate YAML syntax
yamllint config/kong/kong.yaml
yamllint config/otel-config.yml

# Check SQL syntax
psql -f config/postgres/init-databases.sql --dry-run

# Validate JSON files
jq . config/rabbitmq/definitions.json
```

#### Runtime Validation
```bash
# Test Kong configuration
docker compose exec kong kong config parse /usr/local/kong/declarative/kong.yaml

# Check database connections
docker compose exec postgres pg_isready -U admin

# Verify RabbitMQ status
docker compose exec rabbitmq rabbitmqctl status
```

## Security Considerations

### Secrets Management
- **Never commit secrets**: Use environment variables or Docker secrets
- **Rotate certificates**: Update SSL certificates regularly
- **Secure passwords**: Use strong, generated passwords

### Configuration Security
```bash
# Check file permissions
ls -la config/certs/

# Ensure certificates are read-only
chmod 600 config/certs/*.pem

# Validate SSL certificates
openssl x509 -in config/certs/cert.pem -text -noout
```

### Access Control
- **Database users**: Create minimal privilege users for applications
- **API Gateway**: Implement proper authentication and rate limiting
- **Message broker**: Use authentication and limit queue access

## Deployment

### Environment-Specific Configurations
Create environment-specific configuration files:

```bash
config/
├── kong/
│   ├── kong.dev.yaml      # Development configuration
│   ├── kong.staging.yaml  # Staging configuration
│   └── kong.prod.yaml     # Production configuration
```

### Configuration Management
```bash
# Development deployment
export ENVIRONMENT=dev
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production deployment (example)
export ENVIRONMENT=prod
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Backup and Recovery
```bash
# Backup configurations
tar -czf configs-backup-$(date +%Y%m%d).tar.gz config/

# Export running configurations
docker compose exec kong kong config db_export /tmp/kong-backup.yaml
docker compose exec rabbitmq rabbitmqctl export_definitions /tmp/rabbit-backup.json
```

## Troubleshooting

### Common Issues

#### Kong Configuration Errors
```bash
# Check Kong logs
docker compose logs kong

# Validate configuration syntax
docker compose exec kong kong config parse /usr/local/kong/declarative/kong.yaml

# Test API routes
curl -i http://localhost:8000/api/health
```

#### Database Connection Issues
```bash
# Check PostgreSQL logs
docker compose logs postgres

# Test database connectivity
docker compose exec postgres pg_isready -U admin

# Verify database initialization
docker compose exec postgres psql -U admin -c "\l"
```

#### Certificate Problems
```bash
# Verify certificate validity
openssl x509 -in config/certs/cert.pem -noout -dates

# Check certificate chain
openssl verify config/certs/cert.pem

# Test HTTPS connectivity
curl -k https://localhost:9043/health
```

## Best Practices

### Configuration Management
1. **Version control**: Keep all configurations in Git
2. **Environment separation**: Use different configs for dev/staging/prod
3. **Documentation**: Comment complex configurations
4. **Validation**: Test configurations before deployment

### Security
1. **Principle of least privilege**: Minimal required permissions
2. **Regular updates**: Keep configurations current
3. **Secret rotation**: Regularly update passwords and certificates
4. **Audit access**: Monitor configuration changes

### Monitoring
1. **Health checks**: Implement configuration validation
2. **Logging**: Enable appropriate logging levels
3. **Alerting**: Monitor for configuration errors
4. **Backup**: Regular configuration backups

## Contributing

When modifying configurations:

1. **Test locally**: Verify changes work in development
2. **Document changes**: Update relevant documentation
3. **Follow patterns**: Maintain consistency with existing configs
4. **Security review**: Consider security implications
5. **Validate**: Test configuration loading and syntax

For detailed contribution guidelines, see [`../CONTRIBUTING.md`](../CONTRIBUTING.md).

## Reference

### Related Documentation
- **Architecture overview**: [`../ARCHITECTURE.md`](../ARCHITECTURE.md)
- **Service details**: [`../services/README.md`](../services/README.md)
- **Development setup**: [`../docs/development/GETTING-STARTED.md`](../docs/development/GETTING-STARTED.md)
- **Troubleshooting**: [`../docs/troubleshooting/`](../docs/troubleshooting/)

### External Resources
- [Kong Configuration Reference](https://docs.konghq.com/gateway/latest/reference/configuration/)
- [PostgreSQL Configuration](https://www.postgresql.org/docs/current/config-setting.html)
- [RabbitMQ Configuration](https://www.rabbitmq.com/configure.html)
- [OpenTelemetry Configuration](https://opentelemetry.io/docs/reference/specification/configuration/)