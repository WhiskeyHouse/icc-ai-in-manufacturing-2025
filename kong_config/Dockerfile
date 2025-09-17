FROM kong:latest

# Set environment variables
ENV KONG_DATABASE=off \
  KONG_PG_DATABASE=kong \
  KONG_PG_HOST=db \
  KONG_PG_USER=kong \
  KONG_PG_PASSWORD_FILE=/run/secrets/kong_postgres_password \
  KONG_ADMIN_ACCESS_LOG=/dev/stdout \
  KONG_ADMIN_ERROR_LOG=/dev/stderr \
  KONG_PROXY_LISTEN="0.0.0.0:8000" \
  KONG_ADMIN_LISTEN="0.0.0.0:8001" \
  KONG_ADMIN_GUI_LISTEN="0.0.0.0:8002" \
  KONG_PROXY_ACCESS_LOG=/dev/stdout \
  KONG_PROXY_ERROR_LOG=/dev/stderr \
  KONG_PREFIX=/var/run/kong \
  KONG_DECLARATIVE_CONFIG="/opt/kong/kong.yaml"

# Copy the kong configuration file
COPY kong.yaml /opt/kong/kong.yaml

# Healthcheck to ensure service is up
HEALTHCHECK --interval=10s --timeout=10s --retries=10 CMD kong health

USER root

# Ping the orders service to ensure connectivity
RUN apt-get update && apt-get install -y curl  && \
  apt-get install -y iproute2
# && \
# curl -s http://orders-server:3001/health || exit 1
