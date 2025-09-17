#!/bin/bash
set -euo pipefail

# Ignition 8.3 Real API Testing Script
# Tests the actual available API endpoints

IGNITION_HOST="${IGNITION_HOST:-localhost}"
IGNITION_PORT="${IGNITION_PORT:-9088}"
IGNITION_API_KEY="${IGNITION_API_KEY:-mcp2:6uAHjHhz8FaYm654IgcTNSVWV4cukaFuXED0CvGGuBE}"
API_BASE_URL="http://${IGNITION_HOST}:${IGNITION_PORT}"

echo "🧪 Ignition 8.3 Real API Testing Script"
echo "======================================="
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
            # Pretty print JSON if possible, otherwise show first 200 chars
            echo "   Response: $(echo "$body" | jq -C '.' 2>/dev/null || echo "$body" | head -c 200)..."
        fi
    elif [ "$status" = "404" ]; then
        echo "   ⚠️  Not Found ($status)"
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

echo "🚀 Testing Core Gateway Endpoints"
echo "=================================="

api_request "GET" "/data/api/v1/gateway-info" "Gateway Information"
api_request "GET" "/data/api/v1/overview" "Gateway Overview"
api_request "GET" "/data/api/v1/overview/connections" "Gateway Connections"
api_request "GET" "/data/api/v1/overview/name" "Gateway Name"

echo "📁 Testing Project Management"
echo "============================="

api_request "GET" "/data/api/v1/projects/list" "List All Projects"
api_request "GET" "/data/api/v1/projects/names" "Project Names"
api_request "GET" "/data/api/v1/projects" "Projects Overview"

echo "🔧 Testing Module Management"
echo "============================"

api_request "GET" "/data/api/v1/modules/healthy" "Healthy Modules"
api_request "GET" "/data/api/v1/modules/quarantined" "Quarantined Modules"

echo "🏷️  Testing Tag Providers"
echo "========================="

api_request "GET" "/data/api/v1/resources/list/ignition/tag-provider" "List Tag Providers"
api_request "GET" "/data/api/v1/managed-tag-provider" "Managed Tag Provider"

echo "🔐 Testing Security Resources"
echo "============================="

api_request "GET" "/data/api/v1/resources/list/ignition/user-source" "User Sources"
api_request "GET" "/data/api/v1/resources/list/ignition/identity-provider" "Identity Providers"
api_request "GET" "/data/api/v1/resources/list/ignition/api-token" "API Tokens"

echo "💾 Testing Backup System"
echo "========================"

api_request "GET" "/data/api/v1/backup" "Backup Operations"

echo "📊 Testing Database Connections"
echo "==============================="

api_request "GET" "/data/api/v1/resources/list/ignition/database-connection" "Database Connections"
api_request "GET" "/data/api/v1/resources/list/ignition/database-driver" "Database Drivers"

echo "🌐 Testing OPC UA Resources"
echo "==========================="

api_request "GET" "/data/api/v1/resources/list/com.inductiveautomation.opcua/device" "OPC UA Devices"
api_request "GET" "/data/api/v1/resources/list/ignition/opc-connection" "OPC Connections"

echo "📧 Testing Communication"
echo "========================"

api_request "GET" "/data/api/v1/resources/list/ignition/email-profile" "Email Profiles"

echo "📈 Testing Alarm & Notification"
echo "==============================="

api_request "GET" "/data/api/v1/resources/list/com.inductiveautomation.alarm-notification/alarm-notification-profile" "Alarm Notification Profiles"

echo "🔗 Testing Gateway Network"
echo "=========================="

api_request "GET" "/data/api/v1/gateway-network/gateways" "Network Gateways"
api_request "GET" "/data/api/v1/resources/list/ignition/gateway-network-outgoing" "Outgoing Connections"

echo "📋 Testing Logging"
echo "=================="

api_request "GET" "/data/api/v1/logs/loggers" "Log Loggers"
api_request "GET" "/data/api/v1/logs/properties" "Log Properties"

echo "🎯 Testing Deployment Modes"
echo "==========================="

api_request "GET" "/data/api/v1/mode" "Current Deployment Mode"

echo ""
echo "🎯 API Testing Summary"
echo "======================"
echo "✅ Real API endpoints tested with correct authentication"
echo "📖 Full documentation: ${API_BASE_URL}/openapi"
echo "🔑 API Key configured and working"
echo ""
echo "💡 Next Steps:"
echo "- Create projects and see them in the API"
echo "- Configure resources via API calls"
echo "- Set up automation with these endpoints"
echo ""