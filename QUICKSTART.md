# Quick Start Guide

Get your Finance Data Crawler up and running in 2 minutes!

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed
- At least 2GB of free RAM

## One-Command Setup

```bash
chmod +x setup.sh && ./setup.sh
```

That's it! 🎉

## What Happens During Setup

1. **Checks Prerequisites** - Verifies Docker and Docker Compose are installed
2. **Builds Images** - Creates optimized containers for all services
3. **Starts Database** - Launches PostgreSQL with proper configuration
4. **Waits for Health** - Ensures database is ready before continuing
5. **Migrates Data** - Automatically imports any existing JSON data
6. **Starts Services** - Launches backend API and frontend application
7. **Health Checks** - Verifies all services are running correctly

## Access Your Application

Once setup is complete, you can access:

- **Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## First Steps

1. **Open the Dashboard** at http://localhost:3000
2. **Navigate to "Add Company"** in the top menu
3. **Enter a company URL** from screener.in (e.g., `https://www.screener.in/company/RELIANCE/`)
4. **Click "Add to Queue"** to start crawling
5. **View the data** once crawling is complete

## Useful Commands

### View Live Logs
```bash
docker-compose logs -f
```

### View Specific Service Logs
```bash
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Stop All Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild After Code Changes
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

### Reset Everything (Including Data)
```bash
docker-compose down -v
```

### Access PostgreSQL Database
```bash
docker-compose exec postgres psql -U finance_user -d finance_crawler
```

### Run Migration Manually
```bash
docker-compose exec backend python migrate_json_to_db.py
```

## Troubleshooting

### Services Won't Start

Check if ports are already in use:
```bash
# Check if port 3000 is in use
lsof -i :3000

# Check if port 8000 is in use
lsof -i :8000

# Check if port 5432 is in use
lsof -i :5432
```

### Database Connection Errors

Restart the database:
```bash
docker-compose restart postgres
docker-compose restart backend
```

### Frontend Can't Connect to Backend

Check if backend is healthy:
```bash
docker-compose ps
curl http://localhost:8000
```

### Services Keep Restarting

Check logs for errors:
```bash
docker-compose logs --tail=50
```

### Clear Everything and Start Fresh

```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove all images (optional)
docker-compose down --rmi all -v

# Run setup again
./setup.sh
```

## Production Deployment

For production deployment:

1. **Update environment variables** in `backend/.env` and `frontend-nextjs/.env.local`
2. **Change database credentials** in `docker-compose.yml`
3. **Build production images**:
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```
4. **Use a reverse proxy** (nginx/Caddy) for SSL/HTTPS
5. **Set up proper backups** for PostgreSQL data

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                  Docker Network                  │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │   Frontend   │  │   Backend    │            │
│  │   Next.js    │→→│   FastAPI    │            │
│  │   :3000      │  │   :8000      │            │
│  └──────────────┘  └──────┬───────┘            │
│                           ↓                      │
│                    ┌──────────────┐             │
│                    │  PostgreSQL  │             │
│                    │    :5432     │             │
│                    └──────────────┘             │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the [API Documentation](http://localhost:8000/docs)
- Check out the database schema in `backend/models.py`
- Customize the frontend in `frontend-nextjs/src/`

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify Docker is running: `docker ps`
3. Ensure ports are free: `lsof -i :3000 :8000 :5432`
4. Restart services: `docker-compose restart`

Happy analyzing! 📊
