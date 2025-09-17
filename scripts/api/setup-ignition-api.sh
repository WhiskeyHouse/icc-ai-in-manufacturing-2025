#!/bin/bash
set -euo pipefail

# Ignition 8.3 API Setup Script
# This script helps configure the Ignition REST API and initial settings

IGNITION_HOST="${IGNITION_HOST:-localhost}"
IGNITION_PORT="${IGNITION_PORT:-9088}"
IGNITION_USER="${IGNITION_API_USER:-admin}"
IGNITION_API_KEY="${IGNITION_API_KEY:-mcp2:6uAHjHhz8FaYm654IgcTNSVWV4cukaFuXED0CvGGuBE}"
API_BASE_URL="https://${IGNITION_HOST}:9043"
API_HTTP_URL="http://${IGNITION_HOST}:${IGNITION_PORT}"

echo "🚀 Ignition 8.3 API Setup Script"
echo "=================================="
echo "Host: ${IGNITION_HOST}"
echo "Port: ${IGNITION_PORT}"
echo "User: ${IGNITION_USER}"
echo ""

# Function to check if Ignition is running
check_ignition_status() {
    echo "🔍 Checking Ignition status..."
    if curl -s -f "${API_HTTP_URL}/data/status" > /dev/null 2>&1; then
        echo "✅ Ignition is running and accessible"
        return 0
    else
        echo "❌ Ignition is not accessible at ${API_HTTP_URL}"
        return 1
    fi
}

# Function to check API documentation availability
check_api_docs() {
    echo "🔍 Checking API documentation..."
    if curl -s -f "${API_HTTP_URL}/openapi" > /dev/null 2>&1; then
        echo "✅ API documentation available at ${API_HTTP_URL}/openapi"
        return 0
    else
        echo "⚠️  API documentation not accessible (may require authentication)"
        return 1
    fi
}

# Function to test API authentication
test_api_auth() {
    echo "🔐 Testing API authentication..."
    
    # Test with the API key
    local response=$(curl -s -w "%{http_code}" -o /dev/null \
        -H "X-Ignition-API-Token: ${IGNITION_API_KEY}" \
        "${API_HTTP_URL}/data/gateway/status" || echo "000")
    
    if [ "$response" = "200" ]; then
        echo "✅ API authentication successful"
        return 0
    elif [ "$response" = "401" ]; then
        echo "❌ API authentication failed - invalid token"
        return 1
    elif [ "$response" = "000" ]; then
        echo "⚠️  Could not connect to API endpoint"
        return 1
    else
        echo "⚠️  API returned status code: $response"
        return 1
    fi
}

# Function to get gateway information via API
get_gateway_info() {
    echo "📊 Getting gateway information..."
    
    local gateway_info=$(curl -s \
        -H "X-Ignition-API-Token: ${IGNITION_API_KEY}" \
        "${API_HTTP_URL}/data/gateway/status" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ ! -z "$gateway_info" ]; then
        echo "Gateway Status Information:"
        echo "$gateway_info" | jq '.' 2>/dev/null || echo "$gateway_info"
    else
        echo "⚠️  Could not retrieve gateway information"
    fi
}

# Function to display configuration summary
show_config_summary() {
    echo ""
    echo "📋 Configuration Summary"
    echo "========================"
    echo "Gateway URL: ${API_HTTP_URL}"
    echo "HTTPS URL: ${API_BASE_URL}"
    echo "API Docs: ${API_HTTP_URL}/openapi"
    echo "Gateway Config: ${API_HTTP_URL}/data/app/gateway"
    echo ""
    echo "📁 Volume Mappings:"
    echo "   - Config: ./ignition-config -> /usr/local/bin/ignition/data/config"
    echo "   - Projects: ./ignition-projects -> /usr/local/bin/ignition/data/projects"
    echo "   - Backups: ./ignition-backups -> /usr/local/bin/ignition/backups"
    echo ""
}

# Function to create initial git setup for version control
setup_git_integration() {
    echo "🔧 Setting up Git integration..."
    
    # Create .gitignore for Ignition projects
    cat > ignition-projects/.gitignore << 'EOF'
# Ignition Project .gitignore
*.pyc
*.pyo
__pycache__/
.DS_Store
Thumbs.db

# Ignition specific
*.tmp
*.bak
*.backup
resource.lock
*.idb
*.jar-cache/

# Logs
*.log
logs/

# Local configuration that shouldn't be versioned
local/
.container-init.conf
.context.tmp
EOF

    # Create initial README for projects
    cat > ignition-projects/README.md << 'EOF'
# Ignition Projects

This directory contains Ignition 8.3 projects stored as JSON files for version control.

## Structure
- Each project is stored in its own subdirectory
- All configurations are in JSON format
- Use git to track changes and collaborate

## Usage
1. Create projects in Ignition Designer
2. Projects are automatically saved as JSON files here
3. Commit changes to git as needed
4. Deploy projects using Ignition's deployment modes

## Version Control Best Practices
- Commit logical changes together
- Use descriptive commit messages
- Tag releases for production deployments
- Use branches for feature development
EOF

    echo "✅ Git integration setup complete"
}

# Function to create backup automation script
create_backup_script() {
    echo "🔧 Creating backup automation script..."
    
    cat > ../backup-ignition.sh << 'EOF'
#!/bin/bash
# Ignition 8.3 Backup Script

set -euo pipefail

BACKUP_DIR="./ignition-backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="ignition_backup_${TIMESTAMP}"

echo "📦 Creating Ignition backup: ${BACKUP_NAME}"

# Create backup directory structure
mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"

# Copy configuration files
echo "📁 Backing up configuration..."
cp -r ./ignition-config "${BACKUP_DIR}/${BACKUP_NAME}/config" 2>/dev/null || echo "⚠️  Config directory not found"

# Copy projects
echo "📁 Backing up projects..."
cp -r ./ignition-projects "${BACKUP_DIR}/${BACKUP_NAME}/projects" 2>/dev/null || echo "⚠️  Projects directory not found"

# Create manifest
cat > "${BACKUP_DIR}/${BACKUP_NAME}/manifest.json" << EOL
{
  "backup_name": "${BACKUP_NAME}",
  "timestamp": "${TIMESTAMP}",
  "ignition_version": "8.3.0-rc1",
  "backup_type": "filesystem",
  "components": ["config", "projects"]
}
EOL

# Create compressed archive
echo "🗜️  Creating compressed archive..."
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}/"
rm -rf "${BACKUP_NAME}/"

echo "✅ Backup created: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
EOF

    chmod +x ../backup-ignition.sh
    echo "✅ Backup script created at ../backup-ignition.sh"
}

# Main execution
main() {
    show_config_summary
    
    if check_ignition_status; then
        check_api_docs
        test_api_auth
        if [ $? -eq 0 ]; then
            get_gateway_info
        fi
    else
        echo "⚠️  Start Ignition with 'docker compose up -d' first"
    fi
    
    setup_git_integration
    create_backup_script
    
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Access Ignition at ${API_HTTP_URL}"
    echo "2. Complete initial commissioning if needed"
    echo "3. Access API docs at ${API_HTTP_URL}/openapi"
    echo "4. Create your first project and see it appear in ./ignition-projects/"
    echo "5. Use git to version control your configurations"
    echo ""
    echo "Useful commands:"
    echo "- docker compose logs ignition (view logs)"
    echo "- ./scripts/backup-ignition.sh (create backup)"
    echo "- git init ./ignition-projects (initialize version control)"
}

main "$@"