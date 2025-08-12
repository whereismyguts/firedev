# Firedev Production Deployment

## Quick Deploy
```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/sites-available/firedev
sudo ln -s /etc/nginx/sites-available/firedev /etc/nginx/sites-enabled/

# Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx

# Start services
docker compose up -d

# Verify
curl http://localhost:8283/health
```

## Service Endpoints
- **Main Site**: http://your-domain:8283
- **Map Interface**: http://your-domain:8283/ 
- **API Health**: http://your-domain:8283/health
- **Backend API**: http://your-domain:8283/api/

## Nginx Configuration Features
- ✅ Serves web map on port 8283
- ✅ Proxies API calls to backend
- ✅ CORS headers for Firebase integration
- ✅ Gzip compression
- ✅ Security headers
- ✅ Static asset caching
- ✅ Health check endpoint
- ✅ Error handling

## Production Checklist
- [ ] Update server_name in nginx.conf to your domain
- [ ] Set up SSL/TLS certificates (Let's Encrypt recommended)
- [ ] Configure firewall to allow port 8283
- [ ] Set up log rotation for nginx logs
- [ ] Consider setting up monitoring for health endpoints
- [ ] Update bot's map URL from localhost:8080 to your-domain:8283

## SSL Setup (Optional)
```bash
# For SSL, modify nginx.conf:
listen 8283 ssl;
ssl_certificate /path/to/your/cert.pem;
ssl_certificate_key /path/to/your/key.pem;
```

## Docker Production Override
Create `docker-compose.prod.yml`:
```yaml
version: "3.9"
services:
  backend:
    restart: always
  bot:
    restart: always
  web:
    restart: always
```

Deploy with: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`
