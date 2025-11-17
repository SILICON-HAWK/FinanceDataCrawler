#!/bin/bash

# Finance Data Crawler - One-Command Setup Script
# This script sets up the entire application stack automatically

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "=========================================="
echo "  Finance Data Crawler - Easy Setup"
echo "=========================================="
echo ""

# Check if Docker is installed
echo -e "${BLUE}Checking prerequisites...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose first.${NC}"
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed${NC}"
echo -e "${GREEN}✓ Docker Compose is installed${NC}"
echo ""

# Check if services are already running
if docker ps | grep -q "finance_crawler"; then
    echo -e "${YELLOW}⚠️  Finance Crawler services are already running.${NC}"
    read -p "Do you want to restart them? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Stopping existing services...${NC}"
        docker-compose down
    else
        echo "Setup cancelled."
        exit 0
    fi
fi

echo -e "${BLUE}Step 1/4: Building Docker images...${NC}"
docker-compose build --no-cache

echo ""
echo -e "${BLUE}Step 2/4: Starting PostgreSQL database...${NC}"
docker-compose up -d postgres

echo ""
echo -e "${BLUE}Step 3/4: Waiting for database to be ready...${NC}"
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U finance_user -d finance_crawler &> /dev/null; then
        echo -e "${GREEN}✓ Database is ready!${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Database failed to start${NC}"
        exit 1
    fi
done

echo ""
echo -e "${BLUE}Step 4/4: Starting all services...${NC}"
docker-compose up -d

echo ""
echo -e "${BLUE}Waiting for services to be healthy...${NC}"
for i in {1..60}; do
    backend_healthy=$(docker inspect --format='{{.State.Health.Status}}' finance_crawler_backend 2>/dev/null || echo "starting")
    frontend_healthy=$(docker inspect --format='{{.State.Health.Status}}' finance_crawler_frontend 2>/dev/null || echo "starting")

    if [ "$backend_healthy" = "healthy" ] && [ "$frontend_healthy" = "healthy" ]; then
        echo -e "${GREEN}✓ All services are healthy!${NC}"
        break
    fi
    echo -n "."
    sleep 2
    if [ $i -eq 60 ]; then
        echo -e "${YELLOW}⚠️  Services may still be starting. Check logs if needed.${NC}"
        break
    fi
done

echo ""
echo -e "${GREEN}=========================================="
echo "   🎉 Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "Your Finance Data Crawler is now running!"
echo ""
echo -e "${GREEN}Access the application:${NC}"
echo "  📊 Dashboard:    http://localhost:3000"
echo "  🔧 Backend API:  http://localhost:8000"
echo "  📚 API Docs:     http://localhost:8000/docs"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "  View logs:       docker-compose logs -f"
echo "  Stop services:   docker-compose down"
echo "  Restart:         docker-compose restart"
echo "  Reset data:      docker-compose down -v"
echo ""
echo -e "${YELLOW}First time setup?${NC}"
echo "  1. Visit http://localhost:3000"
echo "  2. Go to 'Add Company' to start crawling"
echo "  3. Enter a company URL from screener.in"
echo ""
echo "Happy analyzing! 📈"
echo ""
