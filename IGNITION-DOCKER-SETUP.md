# Ignition Docker Setup Guide

This guide explains how to configure the Ignition gateway with custom username, password, and skip commissioning during Docker startup.

## Quick Start

1. **Copy the environment variables file:**
   ```bash
   cp env-variables-example.txt .env
   ```

2. **Ensure the gateway admin password secret exists:**
   ```bash
   echo "your_secure_password" > secrets/GATEWAY_ADMIN_PASSWORD
   ```

3. **Start the Docker environment:**
   ```bash
   docker compose up -d
   ```

## Configuration Options

### Environment Variables

The following environment variables control the Ignition gateway setup:

| Variable | Default | Description |
|----------|---------|-------------|
| `GATEWAY_ADMIN_USERNAME` | `admin` | The username for the gateway admin account |
| `GATEWAY_SKIP_COMMISSIONING` | `true` | Skip the commissioning wizard on first startup |
| `IGNITION_VERSION` | `8.3.0-rc1` | The Ignition version to use |

### Secrets

The gateway admin password is stored as a Docker secret for security:

- **File**: `secrets/GATEWAY_ADMIN_PASSWORD`
- **Usage**: Automatically loaded during container startup
- **Security**: Never stored in environment variables or logs

## How It Works

1. **Entrypoint Script**: The `docker-entrypoint-shim.sh` script handles the configuration:
   - Checks if commissioning should be skipped
   - Sets up admin credentials on first startup
   - Waits for the database to initialize before configuring

2. **Password Registration**: The `register-password.sh` script:
   - Generates a salted hash of the password
   - Updates the Ignition configuration database
   - Sets the admin username and password

3. **Skip Commissioning**: When enabled:
   - Creates a commissioning completion marker
   - Sets environment variables to bypass the setup wizard
   - Allows immediate access to the gateway

## Accessing the Gateway

After startup, access the Ignition gateway at:
- **URL**: `http://localhost:9088`
- **Username**: Value from `GATEWAY_ADMIN_USERNAME` (default: `admin`)
- **Password**: Value from `secrets/GATEWAY_ADMIN_PASSWORD`

## Customization

### Using a Different Username

Edit your `.env` file:
```bash
GATEWAY_ADMIN_USERNAME=myusername
```

### Enabling Commissioning

To show the commissioning wizard on first startup:
```bash
GATEWAY_SKIP_COMMISSIONING=false
```

### Changing the Password

1. Update the secret file:
   ```bash
   echo "new_secure_password" > secrets/GATEWAY_ADMIN_PASSWORD
   ```

2. Rebuild and restart the container:
   ```bash
   docker compose down
   docker compose build ignition
   docker compose up -d
   ```

## Troubleshooting

### Password Not Working

1. Check the secret file exists:
   ```bash
   ls -la secrets/GATEWAY_ADMIN_PASSWORD
   ```

2. Verify the container can read the secret:
   ```bash
   docker compose exec ignition cat /run/secrets/gateway-admin-password
   ```

3. Check the logs for errors:
   ```bash
   docker compose logs ignition | grep -i password
   ```

### Commissioning Wizard Still Appears

1. Verify the environment variable is set:
   ```bash
   docker compose exec ignition env | grep GATEWAY_SKIP_COMMISSIONING
   ```

2. Clear the data volume and restart:
   ```bash
   docker compose down
   docker volume rm icc-ai-in-manufacturing-2025_gw-data
   docker compose up -d
   ```

### Database Not Initializing

If the admin credentials aren't being set:

1. Check the entrypoint script logs:
   ```bash
   docker compose logs ignition | grep -i "admin"
   ```

2. Manually trigger password registration:
   ```bash
   docker compose exec ignition /usr/local/bin/register-password.sh \
     -u admin \
     -f /run/secrets/gateway-admin-password \
     -d /usr/local/bin/ignition/data/db/config.idb
   ```

## Security Best Practices

1. **Use Strong Passwords**: Generate secure passwords for production
2. **Protect Secret Files**: Set appropriate file permissions (600)
3. **Don't Commit Secrets**: Never commit `.env` or `secrets/` to version control
4. **Rotate Credentials**: Regularly update passwords in production
5. **Use SSL**: Enable SSL for production deployments

## Related Documentation

- [Ignition Docker Image Documentation](https://docs.inductiveautomation.com/docs/8.3/platform/docker-image)
- [Docker Secrets Documentation](https://docs.docker.com/compose/use-secrets/)
- [Ignition Security Guide](https://docs.inductiveautomation.com/docs/8.3/platform/security)
