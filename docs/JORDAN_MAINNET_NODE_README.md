# 🌐 Jordan Mainnet Node Service

## Overview

The Jordan Mainnet Node Service is a blockchain node service that integrates with the VIPER trading system to provide blockchain data access, smart contract interaction, and network monitoring via the Model Context Protocol (MCP).

## Features

- **Blockchain Node Synchronization**: Full node synchronization with Jordan Mainnet
- **RPC API**: JSON-RPC 2.0 compliant API for blockchain operations
- **WebSocket Support**: Real-time blockchain data streaming
- **MCP Integration**: Full integration with VIPER's MCP system
- **GitHub Integration**: Automatic task creation and management via GitHub issues
- **Health Monitoring**: Comprehensive health checks and status monitoring
- **Metrics & Logging**: Prometheus metrics and structured logging
- **Security**: API key authentication and rate limiting
- **Docker Support**: Containerized deployment with Docker Compose

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   VIPER MCP     │    │ Jordan Mainnet   │    │ Jordan Mainnet  │
│     Server      │◄──►│    Node API      │◄──►│   Blockchain    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub API    │    │   Redis Cache    │    │  Blockchain     │
│   Integration   │    │   & State Mgmt   │    │   Data Storage  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Redis server
- Jordan Mainnet API credentials
- GitHub Personal Access Token

## Configuration

### Environment Variables

```bash
# Jordan Mainnet Configuration
JORDAN_MAINNET_KEY=your_api_key_here
JORDAN_MAINNET_SECRET=your_api_secret_here
JORDAN_MAINNET_PASSPHRASE=your_passphrase_here
JORDAN_MAINNET_ENABLED=true
JORDAN_MAINNET_RPC_URL=https://jordan-mainnet.example.com
JORDAN_MAINNET_CHAIN_ID=12345
JORDAN_MAINNET_EXPLORER=https://explorer.jordan-mainnet.example.com

# Service Configuration
JORDAN_MAINNET_NODE_PORT=8022
LOG_LEVEL=INFO
REDIS_URL=redis://redis:6379

# GitHub Integration
GITHUB_PAT=your_github_token_here
GITHUB_OWNER=your_github_username
GITHUB_REPO=your_repository_name
```

### Configuration File

The service uses a JSON configuration file located at `config/jordan_mainnet_config.json`:

```json
{
  "jordan_mainnet": {
    "network": {
      "name": "Jordan Mainnet",
      "chain_id": "12345",
      "currency_symbol": "JRD",
      "decimals": 18
    },
    "node": {
      "sync_mode": "fast",
      "max_peers": 50,
      "health_check_interval": 30
    },
    "api": {
      "enabled": true,
      "port": 8000,
      "rate_limit": 1000
    }
  }
}
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/stressica1/viper-.git
cd viper-
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Jordan Mainnet credentials
```

### 3. Start the Service

```bash
# Using the startup script
./scripts/start_jordan_mainnet_node.sh start

# Or using Docker Compose directly
docker-compose up -d jordan-mainnet-node
```

### 4. Verify Installation

```bash
# Check service status
./scripts/start_jordan_mainnet_node.sh status

# Check health endpoint
curl http://localhost:8022/health
```

## API Endpoints

### Health & Status

#### GET /health
Health check endpoint for the service.

**Response:**
```json
{
  "status": "healthy",
  "service": "jordan-mainnet-node",
  "version": "1.0.0",
  "node_status": "running",
  "sync_status": "synced",
  "last_block": 12345,
  "peer_count": 25,
  "chain_id": "12345"
}
```

#### GET /status
Get comprehensive node status information.

**Response:**
```json
{
  "status": "success",
  "node_status": "running",
  "sync_status": "synced",
  "last_block": 12345,
  "peer_count": 25,
  "chain_id": "12345",
  "rpc_status": {
    "connected": true,
    "chain_id": "0x3039",
    "response_time": 0.045
  },
  "network_info": {
    "network_id": "12345",
    "rpc_url": "https://jordan-mainnet.example.com",
    "explorer": "https://explorer.jordan-mainnet.example.com"
  },
  "timestamp": "2025-01-27T10:30:00Z"
}
```

### Node Operations

#### POST /start
Start the Jordan Mainnet node.

**Request Body:**
```json
{
  "operation": "start",
  "parameters": {}
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Jordan Mainnet node started successfully",
  "task_id": "uuid-here",
  "github_task": {
    "issue_number": 123,
    "issue_url": "https://github.com/user/repo/issues/123"
  },
  "node_status": "running",
  "rpc_status": {
    "connected": true
  }
}
```

#### POST /stop
Stop the Jordan Mainnet node.

#### POST /sync
Synchronize the node with the blockchain.

### Blockchain Data

#### GET /block/{block_number}
Get information about a specific block.

**Response:**
```json
{
  "status": "success",
  "block_data": {
    "number": "0x3039",
    "hash": "0x...",
    "parentHash": "0x...",
    "timestamp": "0x...",
    "transactions": []
  },
  "block_number": 12345
}
```

#### GET /transaction/{tx_hash}
Get information about a specific transaction.

#### POST /rpc
Make custom RPC calls to Jordan Mainnet.

**Request Body:**
```json
{
  "method": "eth_getBalance",
  "params": ["0x...", "latest"],
  "id": 1
}
```

### GitHub Integration

#### POST /github/create-task
Create a GitHub issue for node management.

#### GET /github/tasks
List GitHub tasks/issues for node management.

#### POST /github/update-task
Update a GitHub task/issue for node management.

## Usage Examples

### Starting the Node

```bash
# Start the service
curl -X POST http://localhost:8022/start \
  -H "Content-Type: application/json" \
  -d '{"operation": "start"}'
```

### Checking Node Status

```bash
# Get health status
curl http://localhost:8022/health

# Get detailed status
curl http://localhost:8022/status
```

### Making RPC Calls

```bash
# Get latest block number
curl -X POST http://localhost:8022/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "method": "eth_blockNumber",
    "params": [],
    "id": 1
  }'

# Get account balance
curl -X POST http://localhost:8022/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "method": "eth_getBalance",
    "params": ["0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6", "latest"],
    "id": 1
  }'
```

### Managing GitHub Tasks

```bash
# Create a task
curl -X POST http://localhost:8022/github/create-task \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Node Maintenance Required",
    "body": "Node needs attention",
    "labels": ["jordan-mainnet", "maintenance"]
  }'

# List tasks
curl http://localhost:8022/github/tasks?status=open
```

## Monitoring & Logging

### Health Checks

The service provides comprehensive health monitoring:

- **Service Health**: Basic service availability
- **Node Status**: Blockchain node operational status
- **RPC Connection**: Network connectivity status
- **Sync Status**: Blockchain synchronization status

### Logging

Logs are written to:
- `logs/jordan_mainnet_node.log` - General service logs
- `logs/jordan_mainnet_node_error.log` - Error logs

### Metrics

Prometheus metrics are available at `/metrics` endpoint:

- `jordan_mainnet_node_status` - Node status gauge
- `jordan_mainnet_rpc_requests_total` - RPC request counter
- `jordan_mainnet_sync_duration_seconds` - Sync duration histogram

## Troubleshooting

### Common Issues

#### 1. Service Won't Start

**Symptoms:**
- Docker container fails to start
- Service returns error on health check

**Solutions:**
- Check environment variables are set correctly
- Verify Jordan Mainnet credentials are valid
- Check Docker logs: `docker-compose logs jordan-mainnet-node`

#### 2. RPC Connection Failed

**Symptoms:**
- `rpc_status.connected: false`
- Timeout errors on RPC calls

**Solutions:**
- Verify `JORDAN_MAINNET_RPC_URL` is correct
- Check network connectivity
- Verify RPC endpoint is accessible

#### 3. GitHub Integration Issues

**Symptoms:**
- GitHub tasks not created
- Authentication errors

**Solutions:**
- Verify `GITHUB_PAT` is valid and has correct permissions
- Check `GITHUB_OWNER` and `GITHUB_REPO` are correct
- Ensure repository exists and is accessible

### Debug Mode

Enable debug logging by setting:

```bash
LOG_LEVEL=DEBUG
```

### Manual Testing

Test individual components:

```bash
# Test RPC connection
curl -X POST http://localhost:8022/rpc \
  -H "Content-Type: application/json" \
  -d '{"method": "eth_chainId", "params": [], "id": 1}'

# Test GitHub integration
curl http://localhost:8022/github/tasks
```

## Development

### Local Development

1. **Install Dependencies**
   ```bash
   cd services/jordan-mainnet-node
   pip install -r requirements.txt
   ```

2. **Run Service**
   ```bash
   python main.py
   ```

3. **Run Tests**
   ```bash
   pytest tests/
   ```

### Code Structure

```
services/jordan-mainnet-node/
├── main.py              # Main service implementation
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker container definition
├── __init__.py         # Package initialization
└── tests/              # Test suite
```

### Adding New Features

1. **Add New Endpoint**
   ```python
   @self.app.post("/new-endpoint")
   async def new_endpoint(request: Request):
       data = await request.json()
       return await self.handle_new_operation(data)
   ```

2. **Add New Method**
   ```python
   async def handle_new_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
       # Implementation here
       pass
   ```

3. **Update Configuration**
   - Add new environment variables to `.env`
   - Update `config/jordan_mainnet_config.json`
   - Update Docker Compose configuration

## Security Considerations

### API Security

- **Authentication**: API key-based authentication
- **Rate Limiting**: Configurable request rate limits
- **CORS**: Configurable cross-origin resource sharing
- **Input Validation**: Comprehensive input validation and sanitization

### Network Security

- **Firewall Rules**: Configurable firewall rules
- **SSL/TLS**: Optional SSL/TLS encryption
- **Access Control**: Network-level access restrictions

### Data Security

- **Encryption**: Optional data encryption
- **Access Logging**: Comprehensive access logging
- **Audit Trail**: Complete operation audit trail

## Performance Tuning

### Optimization Settings

```json
{
  "node": {
    "sync_mode": "fast",
    "max_peers": 50,
    "cache_size": "2GB"
  },
  "rpc": {
    "max_requests_per_second": 100,
    "max_batch_size": 100
  },
  "storage": {
    "pruning_enabled": true,
    "pruning_retain": 1000
  }
}
```

### Monitoring Performance

- **Response Times**: Monitor RPC response times
- **Throughput**: Track requests per second
- **Resource Usage**: Monitor CPU, memory, and disk usage
- **Network Latency**: Monitor blockchain network latency

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- **Issues**: Create an issue on GitHub
- **Documentation**: Check this README and project documentation
- **Community**: Join the VIPER trading community

## Changelog

### Version 1.0.0 (2025-01-27)
- Initial release
- Basic blockchain node functionality
- MCP integration
- GitHub task management
- Docker containerization
- Comprehensive monitoring and logging

---

**Note**: This service is designed to work with the VIPER trading system and requires proper configuration of Jordan Mainnet credentials and network parameters.
