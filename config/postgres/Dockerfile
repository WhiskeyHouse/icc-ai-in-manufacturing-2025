FROM postgres:12

# Install build dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  build-essential \
  git \
  ca-certificates \
  postgresql-server-dev-12 \
  && rm -rf /var/lib/apt/lists/*

# Install pgvector extension
RUN git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git \
  && cd pgvector \
  && make \
  && make install \
  && cd .. \
  && rm -rf pgvector

# Set wal_level to logical for replication
CMD ["postgres", "-c", "wal_level=logical"] 