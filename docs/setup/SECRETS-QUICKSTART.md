# Ignition 8.3 Secrets Management - Quick Start

Get up and running with secure secrets management in 5 minutes! 🚀

## Prerequisites
- Ignition 8.3 running in Docker
- API access configured
- Basic command line knowledge

## 1. Quick Setup (2 minutes)

### Update Your Secrets
```bash
# 1. Set your actual passwords in secret files
echo "your_secure_db_password" > secrets/IGNITION_DB_PASSWORD
echo "your_api_secret_key" > secrets/IGNITION_API_SECRET
echo "your_smtp_password" > secrets/IGNITION_EMAIL_PASSWORD
echo "your_mqtt_password" > secrets/IGNITION_MQTT_PASSWORD

# 2. Restart container to load secrets
docker compose restart ignition
```

### Run Automated Setup
```bash
# Wait for Ignition to start (about 30 seconds), then run:
./scripts/secrets/setup-secrets.sh
```

**Expected Output:**
```
🚀 Ignition 8.3 Secrets Setup
==============================

✅ Ignition is ready!
🔧 Ensuring secret provider exists: Docker Secrets
   ✅ Secret provider 'Docker Secrets' created successfully
🐳 Setting up secrets from Docker secret files...
   📁 Found Docker secret: ignition-db-password -> database_connection_password
   ✅ Secret created successfully
   📁 Found Docker secret: ignition-api-secret -> external_api_key
   ✅ Secret created successfully

🎉 Secrets setup complete!
```

## 2. Verify Setup (30 seconds)

```bash
# Check what secret providers exist
./scripts/secrets/manage-secrets.sh list-providers

# Check what secrets are available
./scripts/secrets/manage-secrets.sh list-secrets "Docker Secrets"
```

**Expected Output:**
```
📋 Listing Secret Providers...
Name: Docker Secrets, Type: internal, Enabled: true

🔍 Listing secrets in provider: Docker Secrets
   - database_connection_password
   - external_api_key
   - smtp_server_password
   - mqtt_broker_auth_password
```

## 3. Use Secrets in Resources (2 minutes)

### Create a Secure Database Connection
1. **Open Ignition Gateway** web interface: `http://localhost:9088`
2. **Go to**: Configuration → Database → Database Connections
3. **Click**: "Create new Database Connection"
4. **Fill in details**:
   - Name: `SecureDatabase`
   - Database URL: `jdbc:postgresql://db:5432/your_database`
   - Username: `admin`
   - **Password**: Instead of typing a password, use:
     - **Secret Provider**: `Docker Secrets`
     - **Secret Name**: `database_connection_password`

5. **Test Connection** → **Save**

### Create a Secure Email Profile
1. **Go to**: Configuration → Email → Email Profiles  
2. **Click**: "Create new Email Profile"
3. **Fill in details**:
   - Name: `SecureEmail`
   - SMTP Server: `smtp.gmail.com`
   - Username: `your-email@domain.com`
   - **Password**: Use secret instead:
     - **Secret Provider**: `Docker Secrets`
     - **Secret Name**: `smtp_server_password`

4. **Test Email** → **Save**

## 4. Common Operations

### Add a New Secret
```bash
# Add a new secret via command line
./scripts/secrets/manage-secrets.sh create "Docker Secrets" "new_secret_name" "secret_value"

# Or add via file + sync
echo "new_secret_value" > secrets/NEW_SECRET_FILE
# Add to docker-compose.yml secrets section
docker compose restart ignition
./scripts/secrets/manage-secrets.sh sync-docker "Docker Secrets"
```

### Update an Existing Secret
```bash
# Method 1: Update via command line
./scripts/secrets/manage-secrets.sh update "Docker Secrets" "database_connection_password" "new_password"

# Method 2: Update file + sync
echo "new_secure_password" > secrets/IGNITION_DB_PASSWORD
docker compose restart ignition
./scripts/secrets/manage-secrets.sh sync-docker "Docker Secrets"
```

### List All Secrets
```bash
# Quick overview
./scripts/secrets/manage-secrets.sh

# Detailed view
./scripts/secrets/manage-secrets.sh list-secrets "Docker Secrets"
```

## 5. Testing Your Setup

### Test Database Connection
```bash
# Test via API
curl -H "X-Ignition-API-Token: mcp2:6uAHjHhz8FaYm654IgcTNSVWV4cukaFuXED0CvGGuBE" \
  "http://localhost:9088/data/api/v1/resources/list/ignition/database-connection"
```

### Test Secret Access
```bash
# Verify secrets are accessible
curl -H "X-Ignition-API-Token: mcp2:6uAHjHhz8FaYm654IgcTNSVWV4cukaFuXED0CvGGuBE" \
  "http://localhost:9088/data/api/v1/secret-providers/Docker%20Secrets/secrets"
```

## 6. Quick Fixes

### Problem: "Secret provider not found"
```bash
# Run setup again
./scripts/secrets/setup-secrets.sh
```

### Problem: "Secret not found"
```bash
# Check if secret file exists
ls -la secrets/IGNITION_DB_PASSWORD

# Re-sync secrets
./scripts/secrets/manage-secrets.sh sync-docker "Docker Secrets"
```

### Problem: "API token error"
```bash
# Verify API token is set
echo $IGNITION_API_KEY

# Test API access
curl -H "X-Ignition-API-Token: mcp2:6uAHjHhz8FaYm654IgcTNSVWV4cukaFuXED0CvGGuBE" \
  "http://localhost:9088/data/api/v1/gateway-info"
```

## 7. What's Next?

### ✅ You're Done! Your secrets are now secure.

**Benefits you now have:**
- 🔒 **No passwords in config files**
- 🔄 **Easy password rotation** 
- 🛡️ **Encrypted storage**
- 🔍 **API management**
- 📋 **Audit trail**

### Want to do more?

1. **Read the full guide**: [IGNITION-SECRETS-GUIDE.md](./IGNITION-SECRETS-GUIDE.md)
2. **Set up more resources**: Use secrets in MQTT connections, web services, etc.
3. **Automate secret rotation**: Set up scripts to rotate passwords automatically
4. **Monitor usage**: Set up alerts for secret access

### Quick Commands Reference
```bash
# Setup everything
./scripts/secrets/setup-secrets.sh

# List providers
./scripts/secrets/manage-secrets.sh list-providers

# List secrets
./scripts/secrets/manage-secrets.sh list-secrets "Docker Secrets"

# Create secret
./scripts/secrets/manage-secrets.sh create "Docker Secrets" "name" "value"

# Update secret  
./scripts/secrets/manage-secrets.sh update "Docker Secrets" "name" "new_value"

# Sync all Docker secrets
./scripts/secrets/manage-secrets.sh sync-docker "Docker Secrets"

# Get help
./scripts/secrets/manage-secrets.sh --help
```

---

## 🎉 Congratulations!

You now have enterprise-grade secrets management running with Ignition 8.3! Your passwords are secure, your setup is automated, and you're ready for production use.

**Need help?** Check the [full documentation](./IGNITION-SECRETS-GUIDE.md) or run any script with `--help`.