#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display usage
function show_usage {
  echo -e "${YELLOW}Usage: $0 [command]${NC}"
  echo ""
  echo "Commands:"
  echo "  build             Build the Docker image"
  echo "  run               Run the service in Docker"
  echo "  stop              Stop the running container"
  echo "  dev               Run the service in development mode (without Docker)"
  echo "  test [query]      Test the service (provide optional query)"
  echo "  test-compose      Run service with test docker-compose environment"
  echo ""
}

# Check if Docker is available
function check_docker {
  if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed or not available in PATH${NC}"
    exit 1
  fi
}

# Check if Docker Compose is available
function check_docker_compose {
  if ! command -v docker-compose &> /dev/null; then
    if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
      echo -e "${RED}Error: Docker Compose is not installed or not available${NC}"
      exit 1
    fi
  fi
}

# Check if uv is available and install if needed
function check_uv {
  if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}uv is not installed. Installing...${NC}"
    if command -v pip &> /dev/null; then
      pip install uv
    elif command -v brew &> /dev/null; then
      brew install uv
    else
      echo -e "${RED}Error: Cannot install uv. Please install it manually: https://github.com/astral-sh/uv${NC}"
      exit 1
    fi
  fi
}

# Build Docker image
function build {
  echo -e "${GREEN}Building Docker image...${NC}"
  # Add cache cleaning to ensure dependencies are properly installed
  echo -e "${YELLOW}Using simplified build with clean pip cache${NC}"
  docker build --no-cache -t llama-index-service .
}

# Run the service in Docker
function run {
  echo -e "${GREEN}Starting Llama Index service...${NC}"
  
  # Check if .env file exists
  if [ ! -f ../.env ]; then
    echo -e "${YELLOW}Warning: .env file not found in parent directory${NC}"
    echo -e "${YELLOW}Creating a temporary .env file with required variables${NC}"
    
    # Create minimal .env file if it doesn't exist
    cat > .env << EOL
OPENAI_API_KEY=your-openai-api-key-here
DB_HOST=localhost
DB_PORT=5432
DB_USER=admin
DB_PASSWORD=admin
MES_DB_NAME=whk-mes
VECTOR_DB_NAME=whk_vectors
VECTOR_DB_HOST=localhost
VECTOR_DB_PORT=5432
VECTOR_DB_USER=admin
VECTOR_DB_PASSWORD=admin
DEFAULT_OPENAI_MODEL=gpt-4o-mini
EMBED_MODEL=text-embedding-3-small
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_TTL=5000
EOL
  fi
  
  # Stop existing container if running
  docker stop llama-index-service 2>/dev/null || true
  docker rm llama-index-service 2>/dev/null || true
  
  # Run the container
  docker run -d --name llama-index-service \
    -p 8080:8080 \
    --env-file ../.env \
    -v "$(pwd)/storage:/app/storage" \
    llama-index-service
  
  echo -e "${GREEN}Service started on http://localhost:8080${NC}"
  echo -e "${YELLOW}Check logs with: docker logs -f llama-index-service${NC}"
}

# Run the service using Docker Compose test environment
function test_compose {
  echo -e "${GREEN}Starting Llama Index service with test environment...${NC}"
  
  # Check if .env file exists, if not create minimal one
  if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating a temporary .env file with required variables${NC}"
    cat > .env << EOL
OPENAI_API_KEY=your-openai-api-key-here
DEFAULT_OPENAI_MODEL=gpt-4o-mini
EMBED_MODEL=text-embedding-3-small
EOL
    echo -e "${YELLOW}Created .env file. Make sure to set your OPENAI_API_KEY.${NC}"
  fi
  
  # Use docker compose directly with the test file
  if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.test.yml up -d
  else
    docker compose -f docker-compose.test.yml up -d
  fi
  
  echo -e "${GREEN}Test environment started on http://localhost:8080${NC}"
  echo -e "${YELLOW}Check logs with: docker compose -f docker-compose.test.yml logs -f${NC}"
}

# Stop the service
function stop {
  echo -e "${GREEN}Stopping Llama Index service...${NC}"
  docker stop llama-index-service
  
  # Also stop docker-compose services if running
  if [ -f docker-compose.test.yml ]; then
    echo -e "${GREEN}Stopping Docker Compose test environment...${NC}"
    if command -v docker-compose &> /dev/null; then
      docker-compose -f docker-compose.test.yml down
    else
      docker compose -f docker-compose.test.yml down
    fi
  fi
}

# Run the service in development mode with uv
function dev {
  echo -e "${GREEN}Starting service in development mode using uv...${NC}"
  
  # Check if uv is available
  check_uv
  
  # Create uv environment if it doesn't exist
  if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment with uv...${NC}"
    uv venv
  fi
  
  # Activate virtual environment
  source .venv/bin/activate || { echo -e "${RED}Failed to activate virtual environment${NC}"; exit 1; }
  
  # Install dependencies with uv
  echo -e "${GREEN}Installing dependencies with uv...${NC}"
  uv pip install -r requirements.txt
  
  # Run the service
  echo -e "${GREEN}Starting service on http://localhost:8080${NC}"
  cd app && uvicorn main:app --reload --host 0.0.0.0 --port 8080
}

# Test the service with uv
function test {
  echo -e "${GREEN}Testing Llama Index service...${NC}"
  
  # Check if uv is available
  check_uv
  
  # Check if uv environment exists
  if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment with uv...${NC}"
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
  else
    source .venv/bin/activate
  fi
  
  # Install required packages for test with uv
  uv pip install requests python-dotenv
  
  # Run the test script
  if [ -n "$1" ]; then
    python test_query.py --query "$1"
  else
    python test_query.py
  fi
}

# Main script execution
if [ $# -eq 0 ]; then
  show_usage
  exit 0
fi

case "$1" in
  "build")
    check_docker
    build
    ;;
  "run")
    check_docker
    build
    run
    ;;
  "stop")
    check_docker
    stop
    ;;
  "dev")
    dev
    ;;
  "test")
    test "$2"
    ;;
  "test-compose")
    check_docker
    check_docker_compose
    test_compose
    ;;
  *)
    echo -e "${RED}Unknown command: $1${NC}"
    show_usage
    exit 1
    ;;
esac 