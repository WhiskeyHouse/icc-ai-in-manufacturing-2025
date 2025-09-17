# Docker Services Architecture

## Overview

This document details the complete Docker services architecture for the AI-enhanced Ignition development environment. The architecture provides a scalable, containerized solution that integrates AI context engineering capabilities with existing Ignition infrastructure while maintaining production-level reliability and performance.

## 🏗️ Service Architecture

### Service Topology

```mermaid
graph TB
    subgraph "Load Balancing & Gateway"
        LB[Load Balancer<br/>NGINX/Traefik]
        Kong[Kong API Gateway<br/>:8000, :8001]
    end
    
    subgraph "Core Ignition Platform"
        IGW[Ignition Gateway<br/>:9088, :9043]
        IGWData[(Ignition Data<br/>Projects, Tags, Alarms)]
    end
    
    subgraph "AI Context Services"
        RAG[Ignition RAG Service<br/>:8081]
        MCP[MCP Tools Server<br/>:8082]
        Rules[AI Rules Engine<br/>:8083]
        Orch[AI Orchestrator<br/>:8084]
        FineTune[Fine-Tuning Pipeline<br/>:8085]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL<br/>Main Database :5432)]
        VecDB[(Vector Database<br/>pgvector :5433)]
        Redis[(Redis Cache<br/>:6379)]
        Mongo[(MongoDB<br/>Batch Data :27017)]
    end
    
    subgraph "Message & Communication"
        MQTT[MQTT Broker<br/>EMQX :1883, :8083, :18083]
        RMQ[RabbitMQ<br/>:5672, :15672]
    end
    
    subgraph "Monitoring & Analytics"
        Prometheus[Prometheus<br/>:9090]
        Grafana[Grafana<br/>:3000]
        Netdata[Netdata<br/>:19999]
        cAdvisor[cAdvisor<br/>:8080]
        NodeExp[Node Exporter<br/>:9100]
    end
    
    subgraph "Development & Management"
        Portainer[Portainer<br/>:9000, :9443]
        CodeAnalyzer[Code Analyzer<br/>:8086]
        PatternMiner[Pattern Miner<br/>:8087]
        FeedbackLoop[Feedback Processor<br/>:8088]
    end
    
    LB --> Kong
    Kong --> IGW
    Kong --> RAG
    Kong --> MCP
    Kong --> Rules
    
    IGW --> IGWData
    IGW --> PG
    IGW --> MQTT
    
    RAG --> VecDB
    RAG --> Redis
    MCP --> IGW
    Rules --> Redis
    Orch --> RAG
    Orch --> MCP
    Orch --> Rules
    
    FineTune --> VecDB
    FineTune --> CodeAnalyzer
    CodeAnalyzer --> PatternMiner
    PatternMiner --> FeedbackLoop
    FeedbackLoop --> RAG
    
    Prometheus --> NodeExp
    Prometheus --> cAdvisor
    Prometheus --> IGW
    Prometheus --> RAG
    Prometheus --> MCP
    Grafana --> Prometheus
    Grafana --> PG
    Grafana --> VecDB
    
    style IGW fill:#e8f5e8
    style RAG fill:#e1f5fe
    style MCP fill:#f3e5f5
    style Rules fill:#fff3e0
    style VecDB fill:#fce4ec
```

## 🐳 Service Definitions

### Core AI Context Services

#### 1. Ignition RAG Service

```yaml
# Enhanced RAG service with production code analysis
ignition-rag:
  build: 
    context: ./ignition-rag
    dockerfile: Dockerfile
  image: whk/ignition-rag:latest
  container_name: ignition-rag
  restart: unless-stopped
  
  environment:
    # API Keys
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    
    # Database Connections
    - POSTGRES_VECTOR_URL=postgresql://${DB_USER}:${DB_PASSWORD}@vector-db:5432/whk_vectors
    - MAIN_DB_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${MES_DB_NAME}
    - REDIS_URL=redis://redis:6379
    
    # Ignition Integration
    - IGNITION_GATEWAY_URL=http://ignition:9088
    - IGNITION_PROJECTS_PATH=/ignition-data/projects
    - IGNITION_USERNAME=${IGNITION_USERNAME:-admin}
    - IGNITION_PASSWORD=${IGNITION_PASSWORD}
    
    # Processing Configuration
    - BATCH_SIZE=${RAG_BATCH_SIZE:-20}
    - MAX_RETRIES=${RAG_MAX_RETRIES:-5}
    - CHUNK_SIZE=${RAG_CHUNK_SIZE:-1024}
    - CHUNK_OVERLAP=${RAG_CHUNK_OVERLAP:-200}
    - EMBEDDING_MODEL=${EMBEDDING_MODEL:-text-embedding-3-large}
    
    # Monitoring
    - LOG_LEVEL=${LOG_LEVEL:-info}
    - METRICS_ENABLED=true
    - SENTRY_DSN=${SENTRY_DSN}
  
  volumes:
    - gw-data:/ignition-data:ro  # Read-only access to Ignition data
    - ./ignition-rag/storage:/app/storage
    - ./ignition-docs:/docs
    - ./production-analysis:/analysis
  
  networks:
    - whk-network
  
  ports:
    - "8081:8080"
  
  depends_on:
    - vector-db
    - redis
    - ignition
  
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 60s
  
  deploy:
    resources:
      limits:
        memory: 2G
        cpus: '1.5'
      reservations:
        memory: 1G
        cpus: '0.5'
  
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.rag.rule=PathPrefix(`/api/rag`)"
    - "traefik.http.services.rag.loadbalancer.server.port=8080"
    - "prometheus.scrape=true"
    - "prometheus.port=8080"
    - "prometheus.path=/metrics"
```

#### 2. MCP Tools Server

```yaml
ignition-mcp:
  build:
    context: ./ignition-mcp
    dockerfile: Dockerfile
    args:
      - NODE_VERSION=18
  image: whk/ignition-mcp:latest
  container_name: ignition-mcp
  restart: unless-stopped
  
  environment:
    # Ignition Connection
    - IGNITION_GATEWAY_URL=http://ignition:9088
    - IGNITION_GATEWAY_HTTPS_URL=https://ignition:9043
    - IGNITION_USERNAME=${IGNITION_USERNAME:-admin}
    - IGNITION_PASSWORD=${IGNITION_PASSWORD}
    - IGNITION_PROJECT=${IGNITION_DEFAULT_PROJECT:-WHK-Global}
    
    # Validation Configuration
    - VALIDATION_TIMEOUT=${MCP_VALIDATION_TIMEOUT:-30000}
    - JYTHON_ENGINE_PATH=/app/jython/jython-standalone.jar
    - RULES_PATH=/app/rules
    
    # Performance Settings
    - MAX_CONCURRENT_VALIDATIONS=${MCP_MAX_CONCURRENT:-5}
    - CACHE_TTL=${MCP_CACHE_TTL:-300}
    - REDIS_URL=redis://redis:6379
    
    # Security
    - TLS_VERIFY=${MCP_TLS_VERIFY:-false}  # Internal network
    - API_RATE_LIMIT=${MCP_RATE_LIMIT:-100}
    
    # Logging
    - LOG_LEVEL=${LOG_LEVEL:-info}
    - LOG_FORMAT=json
  
  volumes:
    - ./ignition-mcp/rules:/app/rules:ro
    - ./ignition-mcp/jython:/app/jython:ro
    - ./certs:/app/certs:ro
  
  networks:
    - whk-network
  
  ports:
    - "8082:8080"
  
  depends_on:
    - ignition
    - redis
  
  healthcheck:
    test: ["CMD", "node", "/app/healthcheck.js"]
    interval: 30s
    timeout: 10s
    retries: 3
  
  deploy:
    resources:
      limits:
        memory: 1G
        cpus: '1.0'
      reservations:
        memory: 512M
        cpus: '0.25'
```

#### 3. AI Rules Engine

```yaml
ignition-rules-engine:
  build:
    context: ./ai-rules
    dockerfile: Dockerfile
  image: whk/ignition-rules:latest
  container_name: ignition-rules
  restart: unless-stopped
  
  environment:
    # Configuration
    - RULES_DIRECTORY=/app/rules
    - TEMPLATES_DIRECTORY=/app/templates
    - CACHE_ENABLED=true
    - CACHE_TTL=3600
    
    # Database
    - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${MES_DB_NAME}
    - REDIS_URL=redis://redis:6379
    
    # API Configuration
    - API_PORT=8083
    - API_WORKERS=${RULES_API_WORKERS:-4}
    - MAX_REQUEST_SIZE=${RULES_MAX_REQUEST_SIZE:-10MB}
    
    # Monitoring
    - METRICS_ENABLED=true
    - LOG_LEVEL=${LOG_LEVEL:-info}
  
  volumes:
    - ./ai-rules/rules:/app/rules:ro
    - ./ai-rules/templates:/app/templates:ro
    - ./ai-rules/custom:/app/custom
  
  networks:
    - whk-network
  
  ports:
    - "8083:8083"
  
  depends_on:
    - db
    - redis
  
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8083/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

#### 4. AI Context Orchestrator

```yaml
ai-context-orchestrator:
  build:
    context: ./ai-orchestrator
    dockerfile: Dockerfile
  image: whk/ai-orchestrator:latest
  container_name: ai-orchestrator
  restart: unless-stopped
  
  environment:
    # Service Endpoints
    - RAG_SERVICE_URL=http://ignition-rag:8080
    - MCP_SERVICE_URL=http://ignition-mcp:8080
    - RULES_SERVICE_URL=http://ignition-rules:8083
    - FINE_TUNING_SERVICE_URL=http://fine-tuning-pipeline:8085
    
    # AI Model Configuration
    - DEFAULT_AI_MODEL=${DEFAULT_AI_MODEL:-gpt-4}
    - AI_TEMPERATURE=${AI_TEMPERATURE:-0.3}
    - MAX_CONTEXT_LENGTH=${MAX_CONTEXT_LENGTH:-200000}
    - FALLBACK_MODEL=${FALLBACK_MODEL:-gpt-4o-mini}
    
    # Performance Settings
    - MAX_CONCURRENT_REQUESTS=${ORCHESTRATOR_MAX_CONCURRENT:-10}
    - REQUEST_TIMEOUT=${ORCHESTRATOR_TIMEOUT:-120}
    - CONTEXT_CACHE_TTL=1800  # 30 minutes
    
    # Redis for caching and coordination
    - REDIS_URL=redis://redis:6379
    - REDIS_DB_CONTEXT=1
    - REDIS_DB_METRICS=2
    
    # Monitoring
    - PROMETHEUS_METRICS=true
    - LOG_LEVEL=${LOG_LEVEL:-info}
    - TRACE_REQUESTS=${TRACE_REQUESTS:-false}
  
  networks:
    - whk-network
  
  ports:
    - "8084:8080"
  
  depends_on:
    - ignition-rag
    - ignition-mcp
    - ignition-rules-engine
    - redis
  
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
    interval: 30s
    timeout: 10s
    retries: 3
  
  deploy:
    resources:
      limits:
        memory: 1.5G
        cpus: '1.0'
      reservations:
        memory: 512M
        cpus: '0.25'
```

### Production Analysis Services

#### 5. Code Analyzer Service

```yaml
ignition-code-analyzer:
  build:
    context: ./code-analyzer
    dockerfile: Dockerfile
  image: whk/code-analyzer:latest
  container_name: code-analyzer
  restart: unless-stopped
  
  environment:
    # Analysis Configuration
    - ANALYSIS_INTERVAL=${CODE_ANALYSIS_INTERVAL:-3600}  # 1 hour
    - DEEP_ANALYSIS_INTERVAL=${DEEP_ANALYSIS_INTERVAL:-86400}  # Daily
    - PROJECTS_PATH=/ignition-data/projects
    - ANALYSIS_OUTPUT_PATH=/analysis
    
    # Git Integration
    - GIT_REPOS_PATH=/git-repos
    - GIT_ANALYSIS_DEPTH=${GIT_ANALYSIS_DEPTH:-365}  # Days
    - ENABLE_GIT_MINING=${ENABLE_GIT_MINING:-true}
    
    # Database
    - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${MES_DB_NAME}
    - VECTOR_DB_URL=postgresql://${DB_USER}:${DB_PASSWORD}@vector-db:5432/whk_vectors
    
    # AI Integration
    - RAG_SERVICE_URL=http://ignition-rag:8080
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    
    # Performance
    - MAX_WORKERS=${CODE_ANALYZER_WORKERS:-3}
    - BATCH_SIZE=${CODE_ANALYZER_BATCH_SIZE:-50}
  
  volumes:
    - gw-data:/ignition-data:ro
    - ./git-repos:/git-repos:ro
    - ./analysis-results:/analysis
    - ./code-analyzer/patterns:/patterns
  
  networks:
    - whk-network
  
  ports:
    - "8086:8080"
  
  depends_on:
    - db
    - vector-db
    - ignition
    - ignition-rag
  
  healthcheck:
    test: ["CMD", "python", "/app/healthcheck.py"]
    interval: 60s
    timeout: 15s
    retries: 3
    start_period: 120s
```

#### 6. Pattern Mining Service

```yaml
ignition-pattern-miner:
  build:
    context: ./pattern-miner
    dockerfile: Dockerfile
  image: whk/pattern-miner:latest
  container_name: pattern-miner
  restart: unless-stopped
  
  environment:
    # Mining Configuration
    - MINING_INTERVAL=${PATTERN_MINING_INTERVAL:-21600}  # 6 hours
    - MIN_PATTERN_FREQUENCY=${MIN_PATTERN_FREQUENCY:-3}
    - QUALITY_THRESHOLD=${PATTERN_QUALITY_THRESHOLD:-0.6}
    
    # Data Sources
    - IGNITION_PROJECTS_PATH=/ignition-data/projects
    - GIT_REPOS_PATH=/git-repos
    - ANALYSIS_DATA_PATH=/analysis
    
    # Output
    - PATTERNS_OUTPUT_PATH=/patterns
    - TRAINING_DATA_PATH=/training-data
    
    # Database
    - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${MES_DB_NAME}
    - VECTOR_DB_URL=postgresql://${DB_USER}:${DB_PASSWORD}@vector-db:5432/whk_vectors
    
    # Redis for coordination
    - REDIS_URL=redis://redis:6379
    - REDIS_DB_PATTERNS=3
  
  volumes:
    - gw-data:/ignition-data:ro
    - ./git-repos:/git-repos:ro
    - ./analysis-results:/analysis:ro
    - ./patterns-output:/patterns
    - ./training-data:/training-data
  
  networks:
    - whk-network
  
  ports:
    - "8087:8080"
  
  depends_on:
    - ignition-code-analyzer
    - db
    - vector-db
    - redis
  
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
    interval: 60s
    timeout: 15s
    retries: 3
```

#### 7. Fine-Tuning Pipeline

```yaml
fine-tuning-pipeline:
  build:
    context: ./fine-tuning
    dockerfile: Dockerfile
  image: whk/fine-tuning-pipeline:latest
  container_name: fine-tuning-pipeline
  restart: unless-stopped
  
  environment:
    # AI Model Configuration
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - BASE_MODEL=${FINE_TUNE_BASE_MODEL:-gpt-4}
    - TRAINING_JOB_PREFIX=ignition-${ENVIRONMENT}
    
    # Training Configuration
    - TRAINING_DATA_PATH=/training-data
    - MODELS_OUTPUT_PATH=/models
    - BATCH_SIZE=${FINE_TUNE_BATCH_SIZE:-4}
    - LEARNING_RATE=${FINE_TUNE_LEARNING_RATE:-5e-6}
    - EPOCHS=${FINE_TUNE_EPOCHS:-3}
    
    # Data Pipeline
    - MIN_TRAINING_EXAMPLES=${MIN_TRAINING_EXAMPLES:-100}
    - VALIDATION_SPLIT=${VALIDATION_SPLIT:-0.2}
    - QUALITY_THRESHOLD=${TRAINING_QUALITY_THRESHOLD:-0.7}
    
    # Scheduling
    - TRAINING_SCHEDULE=${TRAINING_SCHEDULE:-0 2 * * 0}  # Weekly at 2 AM Sunday
    - AUTO_DEPLOY_THRESHOLD=${AUTO_DEPLOY_THRESHOLD:-0.85}
    
    # Database
    - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${MES_DB_NAME}
    - REDIS_URL=redis://redis:6379
    - REDIS_DB_JOBS=4
    
    # Resource Management
    - MAX_CONCURRENT_JOBS=1
    - JOB_TIMEOUT=${FINE_TUNE_TIMEOUT:-7200}  # 2 hours
  
  volumes:
    - ./training-data:/training-data:ro
    - ./fine-tuning/models:/models
    - ./fine-tuning/logs:/logs
  
  networks:
    - whk-network
  
  ports:
    - "8085:8080"
  
  depends_on:
    - ignition-pattern-miner
    - db
    - redis
  
  deploy:
    resources:
      limits:
        memory: 4G
        cpus: '2.0'
      reservations:
        memory: 2G
        cpus: '1.0'
```

### Enhanced Database Services

#### Vector Database with Optimizations

```yaml
vector-db:
  build:
    context: ./postgres-vector
    dockerfile: Dockerfile
    args:
      - POSTGRES_VERSION=15
      - PGVECTOR_VERSION=0.5.1
  image: whk/postgres-vector:latest
  container_name: postgres-vector
  restart: unless-stopped
  
  environment:
    - POSTGRES_USER=${DB_USER}
    - POSTGRES_PASSWORD=${DB_PASSWORD}
    - POSTGRES_DB=whk_vectors
    - POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=C --lc-ctype=C
    
    # Performance Tuning
    - POSTGRES_SHARED_BUFFERS=${VECTOR_DB_SHARED_BUFFERS:-256MB}
    - POSTGRES_WORK_MEM=${VECTOR_DB_WORK_MEM:-16MB}
    - POSTGRES_MAINTENANCE_WORK_MEM=${VECTOR_DB_MAINTENANCE_MEM:-256MB}
    - POSTGRES_EFFECTIVE_CACHE_SIZE=${VECTOR_DB_CACHE_SIZE:-1GB}
    - POSTGRES_CHECKPOINT_COMPLETION_TARGET=0.9
    - POSTGRES_WAL_BUFFERS=16MB
    - POSTGRES_DEFAULT_STATISTICS_TARGET=100
  
  volumes:
    - vector_postgres:/var/lib/postgresql/data
    - ./postgres-vector/init:/docker-entrypoint-initdb.d:ro
    - ./postgres-vector/config:/etc/postgresql:ro
  
  ports:
    - "${VECTOR_DB_PORT:-5433}:5432"
  
  networks:
    - whk-network
  
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d whk_vectors"]
    interval: 30s
    timeout: 10s
    retries: 3
  
  deploy:
    resources:
      limits:
        memory: 2G
        cpus: '1.5'
      reservations:
        memory: 1G
        cpus: '0.5'
  
  command: >
    postgres
    -c shared_preload_libraries=pg_stat_statements,vector
    -c pg_stat_statements.track=all
    -c log_statement=all
    -c log_min_duration_statement=1000
    -c log_checkpoints=on
    -c log_connections=on
    -c log_disconnections=on
```

#### Redis with Clustering Support

```yaml
redis:
  image: redis:7-alpine
  container_name: redis-main
  restart: unless-stopped
  
  command: redis-server /etc/redis/redis.conf
  
  environment:
    - REDIS_PASSWORD=${REDIS_PASSWORD}
    - REDIS_MAXMEMORY=${REDIS_MAXMEMORY:-1gb}
    - REDIS_MAXMEMORY_POLICY=${REDIS_MAXMEMORY_POLICY:-allkeys-lru}
  
  volumes:
    - redis_data:/data
    - ./redis/config:/etc/redis:ro
  
  networks:
    - whk-network
  
  ports:
    - "${REDIS_PORT:-6379}:6379"
  
  healthcheck:
    test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
    interval: 30s
    timeout: 10s
    retries: 3
  
  deploy:
    resources:
      limits:
        memory: 1.5G
        cpus: '1.0'
      reservations:
        memory: 512M
        cpus: '0.25'

# Redis Sentinel for High Availability (optional)
redis-sentinel:
  image: redis:7-alpine
  container_name: redis-sentinel
  restart: unless-stopped
  
  command: redis-sentinel /etc/redis/sentinel.conf
  
  volumes:
    - ./redis/sentinel.conf:/etc/redis/sentinel.conf:ro
  
  networks:
    - whk-network
  
  ports:
    - "26379:26379"
  
  depends_on:
    - redis
  
  profiles:
    - high-availability
```

### Monitoring & Observability Stack

#### Enhanced Prometheus Configuration

```yaml
prometheus:
  image: prom/prometheus:latest
  container_name: prometheus
  restart: unless-stopped
  
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--storage.tsdb.retention.time=30d'
    - '--storage.tsdb.retention.size=10GB'
    - '--web.console.libraries=/etc/prometheus/console_libraries'
    - '--web.console.templates=/etc/prometheus/consoles'
    - '--web.enable-lifecycle'
    - '--web.enable-admin-api'
  
  environment:
    - PROMETHEUS_RETENTION_TIME=${PROMETHEUS_RETENTION_TIME:-30d}
    - PROMETHEUS_RETENTION_SIZE=${PROMETHEUS_RETENTION_SIZE:-10GB}
  
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    - ./monitoring/prometheus/rules:/etc/prometheus/rules:ro
    - prometheus_data:/prometheus
  
  networks:
    - whk-network
  
  ports:
    - "9090:9090"
  
  depends_on:
    - node-exporter
    - cadvisor
  
  healthcheck:
    test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:9090/-/healthy"]
    interval: 30s
    timeout: 10s
    retries: 3
```

#### Grafana with Provisioning

```yaml
grafana:
  image: grafana/grafana:latest
  container_name: grafana
  restart: unless-stopped
  
  environment:
    # Admin Configuration
    - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER:-admin}
    - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}
    
    # Authentication
    - GF_AUTH_ANONYMOUS_ENABLED=false
    - GF_USERS_ALLOW_SIGN_UP=false
    - GF_USERS_DEFAULT_THEME=dark
    
    # Database
    - GF_DATABASE_TYPE=postgres
    - GF_DATABASE_HOST=db:5432
    - GF_DATABASE_NAME=${GRAFANA_DB_NAME:-grafana}
    - GF_DATABASE_USER=${DB_USER}
    - GF_DATABASE_PASSWORD=${DB_PASSWORD}
    
    # Features
    - GF_FEATURE_TOGGLES_ENABLE=ngalert
    - GF_UNIFIED_ALERTING_ENABLED=true
    - GF_ALERTING_ENABLED=false
    
    # Performance
    - GF_DATAPROXY_TIMEOUT=30
    - GF_DATAPROXY_KEEP_ALIVE_SECONDS=30
    - GF_EXPLORE_ENABLED=true
  
  volumes:
    - grafana_data:/var/lib/grafana
    - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
    - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards:ro
    - ./monitoring/grafana/plugins:/var/lib/grafana/plugins
  
  networks:
    - whk-network
  
  ports:
    - "3000:3000"
  
  depends_on:
    - prometheus
    - db
  
  healthcheck:
    test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1"]
    interval: 30s
    timeout: 10s
    retries: 3
```

## 🔧 Service Configuration Management

### Environment Configuration

```yaml
# .env.production
# AI Services Configuration
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_AI_MODEL=gpt-4
AI_TEMPERATURE=0.3
MAX_CONTEXT_LENGTH=200000

# Database Configuration
DB_USER=admin
DB_PASSWORD=secure_password_here
MES_DB_NAME=whk-mes
VECTOR_DB_PORT=5433
GRAFANA_DB_NAME=grafana

# Redis Configuration
REDIS_PASSWORD=redis_password_here
REDIS_MAXMEMORY=1gb
REDIS_PORT=6379

# Ignition Configuration
IGNITION_USERNAME=admin
IGNITION_PASSWORD=ignition_password_here
IGNITION_DEFAULT_PROJECT=WHK-Global

# Service Resource Limits
RAG_BATCH_SIZE=20
MCP_MAX_CONCURRENT=5
ORCHESTRATOR_MAX_CONCURRENT=10
CODE_ANALYZER_WORKERS=3

# Monitoring Configuration
LOG_LEVEL=info
PROMETHEUS_RETENTION_TIME=30d
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=secure_grafana_password

# Security
ENABLE_TLS=true
TLS_CERT_PATH=/certs
API_RATE_LIMIT=100

# Development/Production Flags
ENVIRONMENT=production
DEBUG=false
TRACE_REQUESTS=false
```

### Service Health Monitoring

```yaml
# monitoring/docker-compose.override.yml
version: '3.8'

services:
  # Health Check Aggregator
  health-monitor:
    image: containous/whoami
    container_name: health-monitor
    restart: unless-stopped
    
    environment:
      - SERVICES_TO_MONITOR=ignition,ignition-rag,ignition-mcp,ignition-rules-engine,ai-context-orchestrator
      - CHECK_INTERVAL=30
      - ALERT_WEBHOOK=${HEALTH_ALERT_WEBHOOK}
    
    networks:
      - whk-network
    
    depends_on:
      - ignition
      - ignition-rag
      - ignition-mcp
      - ignition-rules-engine
      - ai-context-orchestrator
    
    profiles:
      - monitoring
  
  # Log Aggregator
  loki:
    image: grafana/loki:2.9.0
    container_name: loki
    restart: unless-stopped
    
    command: -config.file=/etc/loki/local-config.yaml
    
    volumes:
      - ./monitoring/loki:/etc/loki:ro
      - loki_data:/loki
    
    networks:
      - whk-network
    
    ports:
      - "3100:3100"
    
    profiles:
      - logging
  
  # Log Shipper
  promtail:
    image: grafana/promtail:2.9.0
    container_name: promtail
    restart: unless-stopped
    
    command: -config.file=/etc/promtail/config.yml
    
    volumes:
      - ./monitoring/promtail:/etc/promtail:ro
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    
    networks:
      - whk-network
    
    depends_on:
      - loki
    
    profiles:
      - logging
```

## 📊 Performance Optimization

### Resource Allocation Strategy

```yaml
# Resource limits and reservations
x-resource-defaults: &default-resources
  deploy:
    resources:
      limits:
        memory: 1G
        cpus: '1.0'
      reservations:
        memory: 256M
        cpus: '0.25'

x-ai-service-resources: &ai-service-resources
  deploy:
    resources:
      limits:
        memory: 2G
        cpus: '1.5'
      reservations:
        memory: 512M
        cpus: '0.5'

x-database-resources: &database-resources
  deploy:
    resources:
      limits:
        memory: 3G
        cpus: '2.0'
      reservations:
        memory: 1G
        cpus: '1.0'
```

### Scaling Configuration

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  # Horizontal scaling for AI services
  ignition-rag:
    <<: *ai-service-resources
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
  
  ignition-mcp:
    <<: *default-resources
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
  
  # Load balancer for AI services
  ai-load-balancer:
    image: nginx:alpine
    container_name: ai-lb
    
    volumes:
      - ./nginx/ai-lb.conf:/etc/nginx/nginx.conf:ro
    
    networks:
      - whk-network
    
    ports:
      - "8080:80"
    
    depends_on:
      - ignition-rag
      - ignition-mcp
      - ignition-rules-engine
    
    profiles:
      - scaling
```

## 🔧 Deployment Scripts

### Deployment Automation

```bash
#!/bin/bash
# scripts/deploy-ai-services.sh

set -e

echo "🚀 Deploying AI-Enhanced Ignition Environment"

# Environment validation
echo "📋 Validating environment..."
if [ ! -f .env ]; then
    echo "❌ .env file not found. Copy from .env.example and configure."
    exit 1
fi

# Check required environment variables
required_vars=("OPENAI_API_KEY" "DB_PASSWORD" "IGNITION_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set"
        exit 1
    fi
done

# Pre-deployment setup
echo "🔧 Setting up pre-deployment requirements..."
./scripts/setup-secrets.sh
./scripts/setup-volumes.sh
./scripts/setup-networks.sh

# Database initialization
echo "💾 Initializing databases..."
docker-compose up -d db vector-db redis
sleep 30
docker-compose run --rm ignition-rag python -m scripts.init_vector_db

# Core services deployment
echo "🏗️ Deploying core services..."
docker-compose up -d ignition

# Wait for Ignition to be healthy
echo "⏳ Waiting for Ignition Gateway to be ready..."
timeout=300
counter=0
while ! curl -f -s http://localhost:9088/health &>/dev/null; do
    sleep 5
    counter=$((counter + 5))
    if [ $counter -ge $timeout ]; then
        echo "❌ Ignition Gateway failed to start within $timeout seconds"
        exit 1
    fi
    echo "⏳ Still waiting for Ignition... (${counter}s)"
done

# AI services deployment
echo "🤖 Deploying AI services..."
docker-compose up -d ignition-rag ignition-mcp ignition-rules-engine

# Orchestrator deployment
echo "🎼 Deploying AI orchestrator..."
docker-compose up -d ai-context-orchestrator

# Analytics services
echo "📊 Deploying analytics services..."
docker-compose up -d ignition-code-analyzer ignition-pattern-miner

# Monitoring stack
echo "📈 Deploying monitoring stack..."
docker-compose up -d prometheus grafana netdata

# Health verification
echo "🏥 Verifying service health..."
services=("ignition:9088" "ignition-rag:8081" "ignition-mcp:8082" "ignition-rules-engine:8083" "ai-context-orchestrator:8084")

for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    echo "Checking $name..."
    timeout=60
    counter=0
    while ! curl -f -s http://localhost:$port/health &>/dev/null; do
        sleep 2
        counter=$((counter + 2))
        if [ $counter -ge $timeout ]; then
            echo "❌ $name failed health check"
            docker-compose logs $name
            exit 1
        fi
    done
    echo "✅ $name is healthy"
done

echo "🎉 Deployment completed successfully!"
echo ""
echo "📊 Services Overview:"
echo "- Ignition Gateway: https://localhost:9043"
echo "- AI RAG Service: http://localhost:8081"
echo "- MCP Tools: http://localhost:8082" 
echo "- Rules Engine: http://localhost:8083"
echo "- AI Orchestrator: http://localhost:8084"
echo "- Grafana Monitoring: http://localhost:3000"
echo "- Portainer Management: http://localhost:9000"
echo ""
echo "🔧 Next steps:"
echo "1. Configure Ignition projects and Git integration"
echo "2. Run initial RAG indexing: docker-compose exec ignition-rag python -m scripts.index_production_code"
echo "3. Verify AI context generation: curl http://localhost:8084/generate-context"
```

This comprehensive Docker services architecture provides a production-ready, scalable foundation for AI-enhanced Ignition development with full observability, security, and performance optimization.