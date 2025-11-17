.PHONY: help setup start stop restart logs clean build migrate shell-backend shell-db status crawl crawl-test

# Default target
help:
	@echo "Finance Data Crawler - Available Commands"
	@echo "=========================================="
	@echo ""
	@echo "Setup & Start:"
	@echo "  make setup      - Complete setup (first time)"
	@echo "  make start      - Start all services"
	@echo "  make stop       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo ""
	@echo "Crawler:"
	@echo "  make crawl      - Run the web scraper"
	@echo "  make crawl-test - Test crawl a single company"
	@echo ""
	@echo "Development:"
	@echo "  make logs       - View logs (all services)"
	@echo "  make logs-f     - Follow logs (all services)"
	@echo "  make logs-fe    - Frontend logs only"
	@echo "  make logs-be    - Backend logs only"
	@echo "  make logs-db    - Database logs only"
	@echo ""
	@echo "Database:"
	@echo "  make migrate    - Run JSON to PostgreSQL migration"
	@echo "  make shell-db   - Access PostgreSQL shell"
	@echo ""
	@echo "Utilities:"
	@echo "  make shell-backend - Access backend container shell"
	@echo "  make status     - Check service status"
	@echo "  make build      - Rebuild all containers"
	@echo "  make clean      - Stop and remove all containers"
	@echo "  make clean-all  - Remove containers, volumes, and images"
	@echo ""

setup:
	@echo "Running complete setup..."
	@chmod +x setup.sh
	@./setup.sh

start:
	@echo "Starting all services..."
	@docker-compose up -d
	@echo "Services started!"
	@echo "Dashboard: http://localhost:3000"
	@echo "API: http://localhost:8000"

stop:
	@echo "Stopping all services..."
	@docker-compose down
	@echo "Services stopped!"

restart:
	@echo "Restarting all services..."
	@docker-compose restart
	@echo "Services restarted!"

logs:
	@docker-compose logs --tail=100

logs-f:
	@docker-compose logs -f

logs-fe:
	@docker-compose logs -f frontend

logs-be:
	@docker-compose logs -f backend

logs-db:
	@docker-compose logs -f postgres

migrate:
	@echo "Running database migration..."
	@docker-compose exec backend python migrate_json_to_db.py
	@echo "Migration complete!"

shell-backend:
	@docker-compose exec backend /bin/bash

shell-db:
	@docker-compose exec postgres psql -U finance_user -d finance_crawler

status:
	@docker-compose ps

build:
	@echo "Rebuilding all containers..."
	@docker-compose build --no-cache
	@echo "Build complete!"

clean:
	@echo "Stopping and removing containers..."
	@docker-compose down
	@echo "Clean complete!"

clean-all:
	@echo "WARNING: This will remove all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v --rmi all; \
		echo "Everything removed!"; \
	else \
		echo "Cancelled."; \
	fi

crawl:
	@echo "Starting crawler (live scraping)..."
	@python crawler_main.py

crawl-test:
	@echo "Running crawler test..."
	@python crawler_main.py
