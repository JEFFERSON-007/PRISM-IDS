# Production Deployment Guide

## Docker Compose Deployment

```bash
docker-compose up --build -d
```

Verify service status:
```bash
docker-compose ps
```

Check server logs:
```bash
docker-compose logs -f server
```
