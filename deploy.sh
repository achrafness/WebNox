#!/bin/bash

#######################################
# WebNox Deployment Script
# Automated deployment for WebNox platform
#######################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
INSTALL_DIR="/opt/webnox"
DATA_DIR="/opt/webnox/data"
LOG_FILE="/var/log/webnox-deploy.log"

# Print banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║     ██╗    ██╗███████╗██████╗ ███╗   ██╗ ██████╗ ██╗  ██╗    ║"
    echo "║     ██║    ██║██╔════╝██╔══██╗████╗  ██║██╔═══██╗╚██╗██╔╝    ║"
    echo "║     ██║ █╗ ██║█████╗  ██████╔╝██╔██╗ ██║██║   ██║ ╚███╔╝     ║"
    echo "║     ██║███╗██║██╔══╝  ██╔══██╗██║╚██╗██║██║   ██║ ██╔██╗     ║"
    echo "║     ╚███╔███╔╝███████╗██████╔╝██║ ╚████║╚██████╔╝██╔╝ ██╗    ║"
    echo "║      ╚══╝╚══╝ ╚══════╝╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝    ║"
    echo "║                                                              ║"
    echo "║           Web Security Learning Platform                     ║"
    echo "║                  Deployment Script                           ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE" 2>/dev/null || true
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "[ERROR] $1" >> "$LOG_FILE" 2>/dev/null || true
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "[WARNING] $1" >> "$LOG_FILE" 2>/dev/null || true
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        log_error "Cannot detect OS"
        exit 1
    fi
    log "Detected OS: $OS $VER"
}

# Install Docker
install_docker() {
    log "Checking Docker installation..."
    
    if command -v docker &> /dev/null; then
        log "Docker is already installed"
        docker --version
    else
        log "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
        systemctl enable docker
        systemctl start docker
        log "Docker installed successfully"
    fi
    
    # Install Docker Compose
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        log "Docker Compose is already installed"
    else
        log "Installing Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        log "Docker Compose installed successfully"
    fi
}

# Create .env file
create_env_file() {
    log "Creating environment configuration..."
    
    # Get server IP/domain
    if [ -z "$SERVER_HOST" ]; then
        # Try to detect public IP
        PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "localhost")
        
        echo -e "${YELLOW}"
        echo "═══════════════════════════════════════════════════════════════"
        echo "  SERVER CONFIGURATION"
        echo "═══════════════════════════════════════════════════════════════"
        echo -e "${NC}"
        echo "Detected public IP: $PUBLIC_IP"
        echo ""
        read -p "Enter your server domain or IP (press Enter for $PUBLIC_IP): " SERVER_HOST
        SERVER_HOST=${SERVER_HOST:-$PUBLIC_IP}
    fi
    
    # Generate secret key
    SECRET_KEY=$(openssl rand -hex 32)
    
    # Create .env file
    cat > .env << EOF
#######################################
# WebNox Configuration
# Generated on $(date)
#######################################

# Server Configuration
# The hostname or IP address where labs will be accessible
# This is shown to users when they start a lab instance
LAB_HOST=${SERVER_HOST}

# Application Settings
SECRET_KEY=${SECRET_KEY}
FLASK_ENV=production
DEBUG=false

# Database
DATABASE_URL=sqlite:///instance/webnox.db

# Docker Configuration
DOCKER_HOST=unix:///var/run/docker.sock
LAB_NETWORK=webnox-labs

# Lab Instance Settings
LAB_PORT_START=10000
LAB_PORT_END=20000
LAB_INSTANCE_TIMEOUT=7200

# Redis (for session management)
REDIS_URL=redis://redis:6379/0

# Optional: SSL/TLS
# SSL_CERT_PATH=/etc/ssl/certs/webnox.crt
# SSL_KEY_PATH=/etc/ssl/private/webnox.key

# Optional: SMTP for email notifications
# SMTP_HOST=smtp.example.com
# SMTP_PORT=587
# SMTP_USER=
# SMTP_PASSWORD=
# SMTP_FROM=noreply@webnox.local
EOF

    log "Environment file created: .env"
    log "Server host configured as: $SERVER_HOST"
}

# Create Docker network for labs
create_docker_network() {
    log "Creating Docker network for labs..."
    
    if docker network inspect webnox-labs &>/dev/null; then
        log "Network 'webnox-labs' already exists"
    else
        docker network create webnox-labs
        log "Network 'webnox-labs' created"
    fi
}

# Build lab images
build_lab_images() {
    log "Building lab Docker images..."
    
    LABS_DIR="./labs"
    
    if [ -d "$LABS_DIR" ]; then
        for lab_dir in "$LABS_DIR"/*/; do
            if [ -f "${lab_dir}Dockerfile" ]; then
                lab_name=$(basename "$lab_dir")
                log "Building lab image: webnox-${lab_name}"
                docker build -t "webnox-${lab_name}" "$lab_dir"
            fi
        done
        log "All lab images built successfully"
    else
        log_warning "Labs directory not found: $LABS_DIR"
    fi
}

# Initialize database
init_database() {
    log "Initializing database..."
    
    # Create instance directory on host (will be mounted)
    mkdir -p instance
    chmod 777 instance
    
    # Wait for container to be ready
    log "Waiting for webnox-app container to be ready..."
    sleep 3
    
    # Run seed script inside the running container
    if ! docker exec webnox-app test -f /app/instance/webnox.db 2>/dev/null; then
        log "Running database seed..."
        docker exec webnox-app python seed.py
    else
        log "Database already exists, skipping seed"
    fi
}

# Deploy with Docker Compose
deploy_docker_compose() {
    log "Deploying WebNox with Docker Compose..."
    
    # Stop existing containers
    docker-compose down 2>/dev/null || true
    
    # Build and start
    docker-compose build
    docker-compose up -d
    
    log "WebNox deployed successfully!"
}

# Setup systemd service
setup_systemd_service() {
    log "Setting up systemd service..."
    
    CURRENT_DIR=$(pwd)
    
    cat > /etc/systemd/system/webnox.service << EOF
[Unit]
Description=WebNox - Web Security Learning Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${CURRENT_DIR}
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable webnox
    
    log "Systemd service created: webnox.service"
}

# Setup firewall
setup_firewall() {
    log "Configuring firewall..."
    
    if command -v ufw &> /dev/null; then
        ufw allow 5000/tcp comment 'WebNox App'
        ufw allow 10000:20000/tcp comment 'WebNox Labs'
        log "UFW rules added"
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=5000/tcp
        firewall-cmd --permanent --add-port=10000-20000/tcp
        firewall-cmd --reload
        log "Firewalld rules added"
    else
        log_warning "No firewall detected. Please manually open ports 5000 and 10000-20000"
    fi
}

# Print deployment info
print_info() {
    echo ""
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              DEPLOYMENT SUCCESSFUL! 🎉                       ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "  ${BLUE}Application URL:${NC}  http://${SERVER_HOST}:5000"
    echo -e "  ${BLUE}Labs Host:${NC}        ${SERVER_HOST}"
    echo -e "  ${BLUE}Lab Port Range:${NC}   10000-20000"
    echo ""
    echo -e "  ${YELLOW}Default Credentials:${NC}"
    echo "    Admin:   admin@webnox.local / admin123"
    echo "    Student: student@webnox.local / student123"
    echo ""
    echo -e "  ${BLUE}Useful Commands:${NC}"
    echo "    Start:    docker-compose up -d"
    echo "    Stop:     docker-compose down"
    echo "    Logs:     docker-compose logs -f"
    echo "    Status:   docker-compose ps"
    echo ""
    echo -e "  ${YELLOW}⚠️  Security Notes:${NC}"
    echo "    - Change default passwords after first login"
    echo "    - Configure SSL/TLS for production"
    echo "    - Review firewall rules"
    echo ""
}

# Cleanup function
cleanup() {
    log "Cleaning up old containers and images..."
    
    # Remove stopped lab containers
    docker container prune -f --filter "label=webnox.lab=true"
    
    # Remove unused images
    docker image prune -f
    
    log "Cleanup complete"
}

# Show help
show_help() {
    echo "WebNox Deployment Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  install     Full installation (default)"
    echo "  update      Update existing installation"
    echo "  start       Start WebNox services"
    echo "  stop        Stop WebNox services"
    echo "  restart     Restart WebNox services"
    echo "  logs        Show logs"
    echo "  status      Show service status"
    echo "  cleanup     Clean up old containers"
    echo "  build-labs  Build/rebuild lab images"
    echo "  help        Show this help"
    echo ""
    echo "Environment Variables:"
    echo "  SERVER_HOST   Set server hostname/IP (e.g., SERVER_HOST=labs.example.com ./deploy.sh)"
    echo ""
}

# Main function
main() {
    print_banner
    
    case "${1:-install}" in
        install)
            check_root
            detect_os
            install_docker
            create_env_file
            create_docker_network
            build_lab_images
            deploy_docker_compose
            init_database
            setup_systemd_service
            setup_firewall
            print_info
            ;;
        update)
            log "Updating WebNox..."
            git pull origin main 2>/dev/null || true
            build_lab_images
            docker-compose build
            docker-compose up -d
            log "Update complete!"
            ;;
        start)
            docker-compose up -d
            log "WebNox started"
            ;;
        stop)
            docker-compose down
            log "WebNox stopped"
            ;;
        restart)
            docker-compose restart
            log "WebNox restarted"
            ;;
        logs)
            docker-compose logs -f
            ;;
        status)
            docker-compose ps
            ;;
        cleanup)
            cleanup
            ;;
        build-labs)
            build_lab_images
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main
main "$@"
