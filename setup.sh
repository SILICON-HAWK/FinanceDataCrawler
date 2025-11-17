#!/bin/bash

# Finance Data Crawler - Setup Script
# This script sets up the entire application stack

set -e

echo "=========================================="
echo "Finance Data Crawler - Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose not found. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${BLUE}Step 1: Building Docker images...${NC}"
docker-compose build

echo ""
echo -e "${BLUE}Step 2: Starting services...${NC}"
docker-compose up -d postgres

echo ""
echo -e "${BLUE}Step 3: Waiting for PostgreSQL to be ready...${NC}"
sleep 10

echo ""
echo -e "${BLUE}Step 4: Running database migrations...${NC}"
docker-compose run --rm backend python migrate_json_to_db.py

echo ""
echo -e "${BLUE}Step 5: Starting all services...${NC}"
docker-compose up -d

echo ""
echo -e "${GREEN}=========================================="
echo "Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "Services are now running:"
echo "  - Frontend:  http://localhost:3000"
echo "  - Backend:   http://localhost:8000"
echo "  - API Docs:  http://localhost:8000/docs"
echo "  - PostgreSQL: localhost:5432"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop:      docker-compose down"
echo ""
