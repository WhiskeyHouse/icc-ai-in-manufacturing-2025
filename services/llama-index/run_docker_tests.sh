#!/bin/bash
set -e

# Colors for prettier output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running LlamaIndex Service Tests in Docker${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}Docker is not running. Please start Docker and try again.${NC}"
  exit 1
fi

# Build the test image
echo -e "${GREEN}Building test environment...${NC}"
docker-compose -f docker-compose.test.yml build

# Run the tests
echo -e "${GREEN}Running tests...${NC}"
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Check exit code
EXIT_CODE=$?

# Clean up
echo -e "${GREEN}Cleaning up...${NC}"
docker-compose -f docker-compose.test.yml down --volumes

# Exit with the same code as the tests
if [ $EXIT_CODE -eq 0 ]; then
  echo -e "${GREEN}Tests completed successfully!${NC}"
else
  echo -e "${RED}Tests failed with exit code ${EXIT_CODE}${NC}"
fi

exit $EXIT_CODE 