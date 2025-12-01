# WebNox Deployment Guide

This guide explains how to deploy WebNox on a production server.

## Prerequisites

- Ubuntu/Debian or CentOS/RHEL based Linux server
- Root or sudo access
- At least 2GB RAM and 10GB disk space
- Ports 5000, 80, 8080-8081, and 10000-20000 available

## Quick Deployment

### 1. Clone the Repository

```bash
git clone https://github.com/achrafness/WebNox.git
cd WebNox/backend
```

### 2. Run the Deployment Script

```bash
chmod +x deploy.sh
sudo ./deploy.sh install
```

During installation, you'll be prompted to enter your server's IP address or domain name. This is **critical** - it determines the URL shown to users when they access lab instances.

### 3. Access WebNox

- **Main Application**: `http://YOUR_SERVER:5000`
- **Labs**: Will be accessible on ports 10000-20000

## Configuration

### Environment Variables (.env file)

Copy the example configuration:

```bash
cp .env.example .env
nano .env
```

**Important Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `LAB_HOST` | **The hostname/IP shown to users for lab URLs** | localhost |
| `APP_PORT` | Main application port | 5000 |
| `SECRET_KEY` | Flask secret key (change in production!) | random |
| `DATABASE_URL` | Database connection string | sqlite:///instance/webnox.db |
| `LAB_PORT_START` | Start of port range for labs | 10000 |
| `LAB_PORT_END` | End of port range for labs | 20000 |

### LAB_HOST Configuration

The `LAB_HOST` variable is crucial for proper lab functionality:

- **Local development**: `LAB_HOST=localhost`
- **Server with IP**: `LAB_HOST=192.168.1.100` (your server's IP)
- **With domain**: `LAB_HOST=labs.yourdomain.com`

When a user starts a lab, they'll see:
```
Lab URL: http://LAB_HOST:PORT
```

## Deployment Commands

The `deploy.sh` script provides several commands:

```bash
# Full installation (Docker, dependencies, build, deploy)
sudo ./deploy.sh install

# Update application code
sudo ./deploy.sh update

# Start/Stop/Restart services
sudo ./deploy.sh start
sudo ./deploy.sh stop
sudo ./deploy.sh restart

# View logs
sudo ./deploy.sh logs

# Check status
sudo ./deploy.sh status

# Build lab images only
sudo ./deploy.sh build-labs

# Clean up unused resources
sudo ./deploy.sh cleanup
```

## Manual Deployment

If you prefer manual deployment:

### 1. Install Docker

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose-plugin -y
sudo systemctl enable --now docker
```

### 2. Create Environment File

```bash
cp .env.example .env
# Edit .env with your settings
nano .env
```

### 3. Create Lab Network

```bash
docker network create webnox-labs 2>/dev/null || true
```

### 4. Build Lab Images

```bash
for lab in labs/*/; do
    lab_name=$(basename "$lab")
    if [ -f "$lab/Dockerfile" ]; then
        docker build -t "webnox-lab-$lab_name" "$lab"
    fi
done
```

### 5. Start Services

```bash
docker compose up -d
```

### 6. Initialize Database

```bash
docker exec webnox-app python seed.py
```

## Production Recommendations

### Security

1. **Change SECRET_KEY**: Generate a secure key:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Firewall**: Only open necessary ports:
   ```bash
   sudo ufw allow 5000/tcp    # Main app
   sudo ufw allow 10000:20000/tcp  # Labs
   ```

3. **HTTPS**: Use a reverse proxy (nginx/caddy) with SSL

### Performance

1. **Use PostgreSQL** for production:
   ```env
   DATABASE_URL=postgresql://user:pass@localhost:5432/webnox
   ```

2. **Redis** for session management (already included)

### Reverse Proxy (Optional)

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Troubleshooting

### Labs not accessible

1. Check if lab containers are running:
   ```bash
   docker ps | grep webnox-lab
   ```

2. Verify LAB_HOST is correct:
   ```bash
   grep LAB_HOST .env
   ```

3. Check firewall allows lab ports:
   ```bash
   sudo ufw status
   ```

### Database issues

Reset the database:
```bash
docker exec webnox-app rm -f instance/webnox.db
docker exec webnox-app python seed.py
```

### Container issues

Check logs:
```bash
docker logs webnox-app
docker compose logs -f
```

### Port conflicts

If ports are in use:
```bash
sudo lsof -i :5000
sudo lsof -i :10000
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                              │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Host Server                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Docker Host                             │    │
│  │                                                      │    │
│  │  ┌──────────────┐  ┌──────────────┐                 │    │
│  │  │ webnox-app   │  │   redis      │                 │    │
│  │  │  Port 5000   │  │  Port 6379   │                 │    │
│  │  └──────────────┘  └──────────────┘                 │    │
│  │                                                      │    │
│  │  ┌──────────────────────────────────────────────┐   │    │
│  │  │           Lab Containers (Dynamic)            │   │    │
│  │  │  ┌────────┐ ┌────────┐ ┌────────┐           │   │    │
│  │  │  │XSS Lab │ │SQL Lab │ │CSRF Lab│  ...      │   │    │
│  │  │  │ :10001 │ │ :10002 │ │ :10003 │           │   │    │
│  │  │  └────────┘ └────────┘ └────────┘           │   │    │
│  │  └──────────────────────────────────────────────┘   │    │
│  │                   Network: webnox-labs              │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/achrafness/WebNox/issues
