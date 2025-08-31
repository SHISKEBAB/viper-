#!/bin/bash

# 🚀 Jordan Mainnet Node Startup Script
# VIPER Trading System - Blockchain Node Service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SERVICE_NAME="jordan-mainnet-node"
SERVICE_PORT="${JORDAN_MAINNET_NODE_PORT:-8022}"
LOG_DIR="$PROJECT_ROOT/logs"
CONFIG_DIR="$PROJECT_ROOT/config"
BLOCKCHAIN_DATA_DIR="$PROJECT_ROOT/blockchain_data"

# Logging
LOG_FILE="$LOG_DIR/jordan_mainnet_node.log"
ERROR_LOG_FILE="$LOG_DIR/jordan_mainnet_node_error.log"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if service is running
is_service_running() {
    if curl -s "http://localhost:$SERVICE_PORT/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $SERVICE_NAME to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if is_service_running; then
            print_success "$SERVICE_NAME is ready!"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - Service not ready yet, waiting..."
        sleep 2
        ((attempt++))
    done
    
    print_error "Service failed to start within expected time"
    return 1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error "docker-compose is not installed. Please install it first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        print_error ".env file not found in $PROJECT_ROOT"
        exit 1
    fi
    
    # Check if Jordan Mainnet credentials are configured
    if [ -z "$JORDAN_MAINNET_KEY" ] || [ -z "$JORDAN_MAINNET_SECRET" ] || [ -z "$JORDAN_MAINNET_PASSPHRASE" ]; then
        print_warning "Jordan Mainnet credentials not found in environment variables"
        print_status "Loading from .env file..."
        source "$PROJECT_ROOT/.env"
        
        if [ -z "$JORDAN_MAINNET_KEY" ] || [ -z "$JORDAN_MAINNET_SECRET" ] || [ -z "$JORDAN_MAINNET_PASSPHRASE" ]; then
            print_error "Jordan Mainnet credentials not configured in .env file"
            exit 1
        fi
    fi
    
    print_success "Prerequisites check passed"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$BLOCKCHAIN_DATA_DIR"
    
    print_success "Directories created"
}

# Function to start the service
start_service() {
    print_status "Starting $SERVICE_NAME service..."
    
    cd "$PROJECT_ROOT"
    
    # Start the service using docker-compose
    if docker-compose up -d jordan-mainnet-node; then
        print_success "$SERVICE_NAME service started successfully"
    else
        print_error "Failed to start $SERVICE_NAME service"
        exit 1
    fi
}

# Function to check service logs
check_logs() {
    print_status "Checking service logs..."
    
    if [ -f "$LOG_FILE" ]; then
        print_status "Recent log entries:"
        tail -n 20 "$LOG_FILE" 2>/dev/null || print_warning "No log entries found"
    else
        print_warning "Log file not found: $LOG_FILE"
    fi
    
    if [ -f "$ERROR_LOG_FILE" ]; then
        print_status "Recent error log entries:"
        tail -n 10 "$ERROR_LOG_FILE" 2>/dev/null || print_warning "No error log entries found"
    fi
}

# Function to show service status
show_status() {
    print_status "Service status:"
    
    if is_service_running; then
        print_success "$SERVICE_NAME is running on port $SERVICE_PORT"
        
        # Get detailed status
        if curl -s "http://localhost:$SERVICE_PORT/status" > /dev/null 2>&1; then
            print_status "Detailed status:"
            curl -s "http://localhost:$SERVICE_PORT/status" | jq '.' 2>/dev/null || curl -s "http://localhost:$SERVICE_PORT/status"
        fi
    else
        print_error "$SERVICE_NAME is not running"
    fi
}

# Function to stop the service
stop_service() {
    print_status "Stopping $SERVICE_NAME service..."
    
    cd "$PROJECT_ROOT"
    
    if docker-compose stop jordan-mainnet-node; then
        print_success "$SERVICE_NAME service stopped successfully"
    else
        print_error "Failed to stop $SERVICE_NAME service"
        exit 1
    fi
}

# Function to restart the service
restart_service() {
    print_status "Restarting $SERVICE_NAME service..."
    
    stop_service
    sleep 2
    start_service
    wait_for_service
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the Jordan Mainnet node service"
    echo "  stop      Stop the Jordan Mainnet node service"
    echo "  restart   Restart the Jordan Mainnet node service"
    echo "  status    Show service status"
    echo "  logs      Show service logs"
    echo "  help      Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  JORDAN_MAINNET_NODE_PORT  Port for the service (default: 8022)"
    echo "  JORDAN_MAINNET_KEY        Jordan Mainnet API key"
    echo "  JORDAN_MAINNET_SECRET     Jordan Mainnet API secret"
    echo "  JORDAN_MAINNET_PASSPHRASE Jordan Mainnet API passphrase"
}

# Main execution
main() {
    local command="${1:-start}"
    
    case "$command" in
        start)
            print_status "🚀 Starting Jordan Mainnet Node Service..."
            check_prerequisites
            create_directories
            start_service
            wait_for_service
            show_status
            print_success "Jordan Mainnet Node Service is ready!"
            ;;
        stop)
            print_status "🛑 Stopping Jordan Mainnet Node Service..."
            stop_service
            ;;
        restart)
            print_status "🔄 Restarting Jordan Mainnet Node Service..."
            restart_service
            ;;
        status)
            show_status
            ;;
        logs)
            check_logs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Trap to handle script interruption
trap 'print_error "Script interrupted"; exit 1' INT TERM

# Execute main function with all arguments
main "$@"
