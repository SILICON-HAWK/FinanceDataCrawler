# Docker Setup Guide

This guide explains how to run the Finance Data Crawler using Docker.

## Prerequisites

- Docker 20.10 or higher
- Docker Compose 2.0 or higher
- 2GB+ free RAM
- 5GB+ free disk space

## Quick Start

### Option 1: Using the Setup Script (Recommended)

```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Using Make

```bash
make setup
```

### Option 3: Manual Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

## Architecture

The application runs in three Docker containers:

```
┌─────────────────────────────────────────────┐
│          Docker Network (finance_network)   │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │  Frontend Container                   │  │
│  │  - Next.js 14                         │  │
│  │  - Port: 3000                         │  │
│  │  - Node 20 Alpine                     │  │
│  └──────────────┬───────────────────────┘  │
│                 │                            │
│                 ↓                            │
│  ┌──────────────────────────────────────┐  │
│  │  Backend Container                    │  │
│  │  - FastAPI                            │  │
│  │  - Port: 8000                         │  │
│  │  - Python 3.11                        │  │
│  └──────────────┬───────────────────────┘  │
│                 │                            │
│                 ↓                            │
│  ┌──────────────────────────────────────┐  │
│  │  PostgreSQL Container                 │  │
│  │  - PostgreSQL 16                      │  │
│  │  - Port: 5432                         │  │
│  │  - Alpine Linux                       │  │
│  └──────────────────────────────────────┘  │
│                                              │
└─────────────────────────────────────────────┘
```

## Container Details

### PostgreSQL Database
- **Image**: postgres:16-alpine
- **Container Name**: finance_crawler_db
- **Port**: 5432
- **Credentials**:
  - User: finance_user
  - Password: finance_pass
  - Database: finance_crawler
- **Data**: Persisted in Docker volume `postgres_data`

### FastAPI Backend
- **Image**: Custom (built from backend/Dockerfile)
- **Container Name**: finance_crawler_backend
- **Port**: 8000
- **Features**:
  - Auto-creates database tables
  - Auto-migrates JSON data
  - Health checks enabled
  - Hot reload in development

### Next.js Frontend
- **Image**: Custom (built from frontend-nextjs/Dockerfile)
- **Container Name**: finance_crawler_frontend
- **Port**: 3000
- **Features**:
  - TypeScript compilation
  - Hot reload enabled
  - Tailwind CSS processing

## Health Checks

All services include health checks:

```bash
# View health status
docker-compose ps

# Services should show "healthy" after startup
```

**Health Check Details:**
- PostgreSQL: Checks if database accepts connections
- Backend: HTTP request to /
- Frontend: HTTP request to /

## Data Persistence

### Docker Volumes

```bash
# List volumes
docker volume ls | grep finance

# Inspect postgres data volume
docker volume inspect financedatacrawler_postgres_data

# Backup postgres data
docker run --rm -v financedatacrawler_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore postgres data
docker run --rm -v financedatacrawler_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

### Mounted Directories

The following local directories are mounted into containers:
- `./backend` → `/app` (backend)
- `./frontend-nextjs` → `/app` (frontend)
- `./companies` → `/app/companies` (backend)
- `./json` → `/app/json` (backend)

Changes to these directories are immediately reflected in containers.

## Common Operations

### Start/Stop Services

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
docker-compose restart postgres
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100
```

### Execute Commands

```bash
# Backend shell
docker-compose exec backend /bin/bash

# Run migration
docker-compose exec backend python migrate_json_to_db.py

# PostgreSQL shell
docker-compose exec postgres psql -U finance_user -d finance_crawler

# Check backend API
docker-compose exec backend curl http://localhost:8000/
```

### Rebuild Containers

```bash
# Rebuild all
docker-compose build --no-cache

# Rebuild specific service
docker-compose build --no-cache backend

# Rebuild and restart
docker-compose up -d --build
```

## Environment Variables

### Backend (.env)

Create `backend/.env`:
```env
DATABASE_URL=postgresql://finance_user:finance_pass@postgres:5432/finance_crawler
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend (.env.local)

Create `frontend-nextjs/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### Services Won't Start

```bash
# Check Docker daemon
docker info

# Check port conflicts
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Check logs
docker-compose logs
```

### Database Connection Errors

```bash
# Test database connection
docker-compose exec postgres pg_isready -U finance_user -d finance_crawler

# Restart database
docker-compose restart postgres

# View database logs
docker-compose logs postgres
```

### Frontend Can't Connect to Backend

```bash
# Check backend health
curl http://localhost:8000/

# Check backend logs
docker-compose logs backend

# Verify network
docker network inspect financedatacrawler_finance_network
```

### Container Keeps Restarting

```bash
# Check container status
docker-compose ps

# View recent logs
docker-compose logs --tail=50 backend

# Check health status
docker inspect finance_crawler_backend | grep -A 10 Health
```

### Out of Disk Space

```bash
# Clean up unused Docker resources
docker system prune -a

# Remove old images
docker image prune -a

# Remove unused volumes (WARNING: data loss)
docker volume prune
```

### Reset Everything

```bash
# Stop and remove everything
docker-compose down -v --rmi all

# Remove all Docker data (WARNING: affects all Docker projects)
docker system prune -a --volumes
```

## Production Deployment

### Security Considerations

1. **Change default credentials** in docker-compose.yml:
```yaml
environment:
  POSTGRES_USER: your_secure_user
  POSTGRES_PASSWORD: your_secure_password
  POSTGRES_DB: finance_crawler
```

2. **Use environment files**:
```bash
# Create .env file
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

# Reference in docker-compose.yml
env_file: .env
```

3. **Restrict ports**:
```yaml
# Only expose what's needed
ports:
  - "127.0.0.1:5432:5432"  # Database only on localhost
```

### Performance Tuning

1. **PostgreSQL Settings**:
```yaml
environment:
  POSTGRES_SHARED_BUFFERS: 256MB
  POSTGRES_EFFECTIVE_CACHE_SIZE: 1GB
  POSTGRES_WORK_MEM: 16MB
```

2. **Resource Limits**:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml finance_crawler

# Check services
docker stack services finance_crawler

# Remove stack
docker stack rm finance_crawler
```

## Useful Make Commands

If Make is available:

```bash
make setup      # Complete setup
make start      # Start services
make stop       # Stop services
make logs       # View logs
make migrate    # Run migration
make shell-db   # PostgreSQL shell
make clean      # Clean up
```

## Monitoring

### View Resource Usage

```bash
# All containers
docker stats

# Specific container
docker stats finance_crawler_backend

# JSON format
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Container Inspection

```bash
# Inspect container
docker inspect finance_crawler_backend

# Check network
docker network inspect financedatacrawler_finance_network

# View volumes
docker volume ls
```

## Backup and Restore

### Database Backup

```bash
# Dump database
docker-compose exec postgres pg_dump -U finance_user finance_crawler > backup.sql

# Restore database
docker-compose exec -T postgres psql -U finance_user finance_crawler < backup.sql
```

### Volume Backup

```bash
# Backup volume
docker run --rm -v financedatacrawler_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data

# Restore volume
docker run --rm -v financedatacrawler_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Node Docker Image](https://hub.docker.com/_/node)
- [Python Docker Image](https://hub.docker.com/_/python)
