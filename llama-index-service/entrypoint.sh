#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
python -m app.utils.db_check

# Run database initialization if needed
if [ "$INIT_DB" = "true" ]; then
    echo "Initializing database..."
    python -m app.utils.init_db
fi

# Execute the command provided as arguments
exec "$@" 