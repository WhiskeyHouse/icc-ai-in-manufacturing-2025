#!/bin/bash
set -euo pipefail

# Ignition 8.3 API Testing Script
# Tests various API endpoints with the correct authentication

IGNITION_HOST="${IGNITION_HOST:-localhost}"
IGNITION_PORT="${IGNITION_PORT:-9088}"
IGNITION_API_KEY="${IGNITION_API_KEY:-mcp2:6uAHjHhz8FaYm654IgcTNSVWV4cukaFuXED0CvGGuBE}"
API_BASE_URL="http://${IGNITION_HOST}:${IGNITION_PORT}"

echo "🧪 Ignition 8.3 API Testing Script"
echo "=================================="
echo "Base URL: ${API_BASE_URL}"
echo "API Key: ${IGNITION_API_KEY:0:10}..."
echo ""

# Helper function to make API requests
api_request() {
    local method="$1"
    local endpoint="$2"
    local description="$3"
    
    echo "🔍 Testing: $description"
    echo "   Endpoint: $method $endpoint"
    
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X "$method" \
        -H "X-Ignition-API-Token: ${IGNITION_API_KEY}" \
        -H "Content-Type: application/json" \
        "${API_BASE_URL}${endpoint}")
    
    local body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
    local status=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    
    if [ "$status" -ge 200 ] && [ "$status" -lt 300 ]; then
        echo "   ✅ Success ($status)"
        if [ ! -z "$body" ] && [ "$body" != "null" ]; then
            echo "   Response: $(echo "$body" | jq '.' 2>/dev/null || echo "$body" | head -c 100)..."
        fi
    elif [ "$status" = "404" ]; then
        echo "   ⚠️  Not Found ($status) - endpoint may not exist in this version"
    elif [ "$status" = "401" ]; then
        echo "   ❌ Unauthorized ($status) - check API key"
    else
        echo "   ⚠️  Status: $status"
        if [ ! -z "$body" ]; then
            echo "   Response: $(echo "$body" | head -c 200)"
        fi
    fi
    echo ""
}

# Test basic endpoints
echo "🚀 Testing Core API Endpoints"
echo "=============================="

api_request "GET" "/data/gateway/status" "Gateway Status"
api_request "GET" "/data/gateway/info" "Gateway Information"
api_request "GET" "/data/modules" "Module List"
api_request "GET" "/data/projects" "Project List"

echo "🏷️  Testing Tag System"
echo "======================"

api_request "GET" "/data/tags" "Tag Configuration"
api_request "GET" "/data/tags/read?tagPaths=_system._hostname" "Read System Tags"

echo "👥 Testing User Management"
echo "========================="

api_request "GET" "/data/users" "User List"
api_request "GET" "/data/user-sources" "User Sources"

echo "🔧 Testing System Configuration"
echo "==============================="

api_request "GET" "/data/config/gateway-settings" "Gateway Settings"
api_request "GET" "/data/config/logging" "Logging Configuration"

echo "📊 Testing Metrics and Monitoring"
echo "================================="

api_request "GET" "/data/metrics" "System Metrics"
api_request "GET" "/data/alarms" "Alarm Configuration"

echo "💾 Testing Backup and Restore"
echo "============================="

api_request "GET" "/data/backups" "Backup List"

echo "🌐 Testing Web Services"
echo "======================="

api_request "GET" "/data/web-services" "Web Services"

echo "🔐 Testing Security"
echo "==================="

api_request "GET" "/data/security/certificates" "SSL Certificates"
api_request "GET" "/data/security/roles" "Security Roles"

echo "📈 Testing Historical Data"
echo "=========================="

api_request "GET" "/data/historians" "Historian Configuration"

echo ""
echo "🎯 API Testing Summary"
echo "======================"
echo "All available endpoints have been tested with your API key."
echo "Check the results above to see which endpoints are available."
echo ""
echo "💡 Tips:"
echo "- Visit ${API_BASE_URL}/openapi for complete API documentation"
echo "- Use jq to format JSON responses: curl ... | jq '.'"
echo "- Check Ignition logs if unexpected errors occur"
echo ""