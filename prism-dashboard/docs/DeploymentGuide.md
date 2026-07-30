# Production Deployment Guide

## Building Production Bundle

```bash
cd prism-dashboard
npm run build
```

This compiles static assets into `prism-dashboard/dist/`.

## NGINX Reverse Proxy Configuration

```nginx
server {
    listen 80;
    server_name soc.prism-ids.local;

    root /var/www/prism-dashboard/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
    }

    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
```
