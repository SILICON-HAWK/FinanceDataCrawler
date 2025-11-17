#!/bin/bash
set -e

echo "================================================"
echo "Finance Data Crawler - Backend Starting"
echo "================================================"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "postgres" -U "finance_user" -d "finance_crawler" -c '\q' 2>/dev/null; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is ready!"

# Run database migrations
echo "Creating database tables..."
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"

# Check if we should migrate JSON data
if [ -d "/app/companies" ] && [ "$(ls -A /app/companies 2>/dev/null)" ]; then
    echo "Found existing JSON data. Running migration to PostgreSQL..."
    python migrate_json_to_db.py || echo "Migration completed with warnings (this is normal if data already exists)"
else
    echo "No JSON data found to migrate."
fi

echo "================================================"
echo "Backend ready! Starting API server..."
echo "================================================"

# Start the FastAPI application
exec uvicorn main_db:app --host 0.0.0.0 --port 8000 --reload
