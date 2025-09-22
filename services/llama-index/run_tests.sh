#!/bin/bash
set -e

# Colors for prettier output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Set environment variables for test
export ENV=test
export OPENAI_API_KEY=sk-test-dummy-key
export PRELOAD_INDEXES=false
export EMBED_MODEL=text-embedding-ada-002

echo -e "${YELLOW}Setting up test environment...${NC}"

# Check if Docker is available
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo -e "${GREEN}Docker is available. Tests can use Docker containers.${NC}"
else
    echo -e "${YELLOW}Docker is not available. Tests will use mock environments.${NC}"
fi

# Run tests with coverage
echo -e "${GREEN}Running tests with coverage...${NC}"
python -m pytest tests/ --cov=app -v

# Generate coverage report
echo -e "${GREEN}Generating coverage report...${NC}"
python -m pytest tests/ --cov=app --cov-report=xml:coverage/coverage.xml --cov-report=html:coverage/html --cov-report=term

echo -e "${GREEN}Tests completed.${NC}" 