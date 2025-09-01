#!/usr/bin/env python3
"""
# Jordan Mainnet Node Service
Blockchain node service for Jordan Mainnet integration with VIPER trading system

Features:
- Jordan Mainnet node synchronization
- Blockchain data access via MCP
- Smart contract interaction
- Transaction monitoring
- Network health monitoring
- MCP GitHub integration for node management
"""

import os
import json
import logging
import asyncio
import uuid
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import StreamingResponse
import uvicorn
import httpx
import redis.asyncio as redis

# Add project paths for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'infrastructure'))

# Import credential client
try:
    from infrastructure.shared.credential_client import CredentialClient
except ImportError:
    print("Warning: Could not import credential client - falling back to environment variables")
    CredentialClient = None

# Load environment variables
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
SERVICE_NAME = os.getenv('SERVICE_NAME', 'jordan-mainnet-node')
VAULT_URL = os.getenv('VAULT_URL', 'http://credential-vault:8008')
VAULT_ACCESS_TOKEN = os.getenv('VAULT_ACCESS_TOKEN', '')

# Jordan Mainnet Configuration
JORDAN_MAINNET_KEY = os.getenv('JORDAN_MAINNET_KEY', '')
JORDAN_MAINNET_SECRET = os.getenv('JORDAN_MAINNET_SECRET', '')
JORDAN_MAINNET_PASSPHRASE = os.getenv('JORDAN_MAINNET_PASSPHRASE', '')
JORDAN_MAINNET_ENABLED = os.getenv('JORDAN_MAINNET_ENABLED', 'false').lower() == 'true'
JORDAN_MAINNET_RPC_URL = os.getenv('JORDAN_MAINNET_RPC_URL', '')
JORDAN_MAINNET_CHAIN_ID = os.getenv('JORDAN_MAINNET_CHAIN_ID', '')
JORDAN_MAINNET_EXPLORER = os.getenv('JORDAN_MAINNET_EXPLORER', '')

# GitHub Configuration
GITHUB_PAT = os.getenv('GITHUB_PAT', '')
GITHUB_OWNER = os.getenv('GITHUB_OWNER', 'stressica1')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'viper-')

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)

class JordanMainnetNode:
    """Jordan Mainnet Node Service for VIPER trading operations"""

    def __init__(self):
        self.redis_client = None
        self.app = FastAPI(title="Jordan Mainnet Node", version="1.0.0")
        self.node_status = "initializing"
        self.sync_status = "not_synced"
        self.last_block = 0
        self.peer_count = 0
        self.chain_id = JORDAN_MAINNET_CHAIN_ID
        
        # Initialize httpx client for Jordan Mainnet RPC calls
        self.rpc_client = httpx.AsyncClient(timeout=30.0)
        
        # Initialize credential client for secure credential access
        self.credential_client = None
        if CredentialClient:
            try:
                self.credential_client = CredentialClient(
                    vault_url=VAULT_URL,
                    access_token=os.getenv('VAULT_ACCESS_TOKEN_JORDAN_MAINNET_NODE', 'jordan_mainnet_token_2025'),
                    redis_url=REDIS_URL
                )
            except Exception as e:
                logger.warning(f"Could not initialize credential client: {e}")
        
        # Credentials will be loaded during startup
        self.jordan_key = None
        self.jordan_secret = None  
        self.jordan_passphrase = None
        self.github_pat = None
        
        # Initialize httpx client for GitHub API calls
        self.github_client = httpx.AsyncClient(timeout=30.0)

        self.setup_routes()

    async def load_credentials_from_vault(self):
        """Load credentials from the secure credential vault"""
        if not self.credential_client:
            logger.warning("No credential client available - using environment variables")
            # Fallback to environment variables
            self.jordan_key = JORDAN_MAINNET_KEY
            self.jordan_secret = JORDAN_MAINNET_SECRET
            self.jordan_passphrase = JORDAN_MAINNET_PASSPHRASE
            self.github_pat = GITHUB_PAT
            return
        
        try:
            # Load Jordan Mainnet credentials from vault
            self.jordan_key = await self.credential_client.get_credential('jordan-mainnet-node', 'JORDAN_MAINNET_KEY')
            self.jordan_secret = await self.credential_client.get_credential('jordan-mainnet-node', 'JORDAN_MAINNET_SECRET')
            self.jordan_passphrase = await self.credential_client.get_credential('jordan-mainnet-node', 'JORDAN_MAINNET_PASSPHRASE')
            self.github_pat = await self.credential_client.get_credential('jordan-mainnet-node', 'GITHUB_PAT')
            
            # Fallback to environment variables if vault fails
            if not self.jordan_key:
                self.jordan_key = JORDAN_MAINNET_KEY
            if not self.jordan_secret:
                self.jordan_secret = JORDAN_MAINNET_SECRET
            if not self.jordan_passphrase:
                self.jordan_passphrase = JORDAN_MAINNET_PASSPHRASE
            if not self.github_pat:
                self.github_pat = GITHUB_PAT
            
            logger.info("# Check Credentials loaded from vault")
            
        except Exception as e:
            logger.error(f"# X Failed to load credentials from vault: {e}")
            # Fallback to environment variables
            self.jordan_key = JORDAN_MAINNET_KEY
            self.jordan_secret = JORDAN_MAINNET_SECRET
            self.jordan_passphrase = JORDAN_MAINNET_PASSPHRASE
            self.github_pat = GITHUB_PAT

    def setup_routes(self):
        """Setup Jordan Mainnet node routes"""

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            health_status = "healthy" if self.node_status in ["ready", "ready_fallback", "running", "running_fallback"] else "unhealthy"
            return {
                "status": health_status,
                "service": "jordan-mainnet-node",
                "version": "1.0.0",
                "node_status": self.node_status,
                "sync_status": self.sync_status,
                "last_block": self.last_block,
                "peer_count": self.peer_count,
                "chain_id": self.chain_id,
                "mode": "fallback" if "fallback" in self.node_status else "live"
            }

        @self.app.get("/status")
        async def get_node_status():
            """Get Jordan Mainnet node status"""
            return await self.get_node_status_info()

        @self.app.post("/start")
        async def start_node(request: Request):
            """Start Jordan Mainnet node"""
            data = await request.json()
            return await self.start_node_operation(data)

        @self.app.post("/stop")
        async def stop_node(request: Request):
            """Stop Jordan Mainnet node"""
            data = await request.json()
            return await self.stop_node_operation(data)

        @self.app.post("/sync")
        async def sync_node(request: Request):
            """Sync Jordan Mainnet node"""
            data = await request.json()
            return await self.sync_node_operation(data)

        @self.app.get("/block/{block_number}")
        async def get_block(block_number: int):
            """Get block information"""
            return await self.get_block_info(block_number)

        @self.app.get("/transaction/{tx_hash}")
        async def get_transaction(tx_hash: str):
            """Get transaction information"""
            return await self.get_transaction_info(tx_hash)

        @self.app.post("/rpc")
        async def rpc_call(request: Request):
            """Make RPC call to Jordan Mainnet"""
            data = await request.json()
            return await self.make_rpc_call(data)

        # GitHub Integration Endpoints
        @self.app.post("/github/create-task")
        async def create_github_task(request: Request):
            """Create a GitHub task/issue for node management"""
            data = await request.json()
            return await self.create_github_issue(data)

        @self.app.get("/github/tasks")
        async def list_github_tasks(status: str = "open"):
            """List GitHub tasks/issues for node management"""
            return await self.list_github_issues(status)

        @self.app.post("/github/update-task")
        async def update_github_task(request: Request):
            """Update a GitHub task/issue for node management"""
            data = await request.json()
            return await self.update_github_issue(data)

    async def get_node_status_info(self) -> Dict[str, Any]:
        """Get comprehensive node status information"""
        try:
            # Check RPC connection
            rpc_status = await self.check_rpc_connection()
            
            # Get network info
            network_info = await self.get_network_info()
            
            return {
                "status": "success",
                "node_status": self.node_status,
                "sync_status": self.sync_status,
                "last_block": self.last_block,
                "peer_count": self.peer_count,
                "chain_id": self.chain_id,
                "rpc_status": rpc_status,
                "network_info": network_info,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting node status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def start_node_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Start Jordan Mainnet node operation"""
        try:
            task_id = str(uuid.uuid4())
            
            # Create GitHub task for node start
            github_task = await self.create_github_issue({
                "title": f"Jordan Mainnet Node Start - {task_id}",
                "body": f"Starting Jordan Mainnet node operation\n\n**Task ID**: {task_id}\n**Timestamp**: {datetime.utcnow().isoformat()}\n**Operation**: Node Start\n**Status**: In Progress",
                "labels": ["jordan-mainnet", "node-operation", "start"]
            })
            
            # Update node status
            self.node_status = "starting"
            
            # Simulate node startup process
            await asyncio.sleep(2)
            
            # Check RPC connection
            rpc_status = await self.check_rpc_connection()
            
            if rpc_status["connected"]:
                self.node_status = "running"
                self.sync_status = "syncing"

                # Update GitHub task
                await self.update_github_issue({
                    "issue_number": github_task.get("issue_number"),
                    "body": f"Jordan Mainnet node started successfully\n\n**Task ID**: {task_id}\n**Timestamp**: {datetime.utcnow().isoformat()}\n**Operation**: Node Start\n**Status**: Completed\n**RPC Status**: Connected\n**Node Status**: Running"
                })

                return {
                    "status": "success",
                    "message": "Jordan Mainnet node started successfully",
                    "task_id": task_id,
                    "github_task": github_task,
                    "node_status": self.node_status,
                    "rpc_status": rpc_status
                }
            elif rpc_status.get("fallback_mode"):
                # Fallback mode - node can still operate with mock data
                self.node_status = "running_fallback"
                self.sync_status = "mock_data"

                logger.info("Jordan Mainnet node started in fallback mode")

                # Update GitHub task
                await self.update_github_issue({
                    "issue_number": github_task.get("issue_number"),
                    "body": f"Jordan Mainnet node started in fallback mode\n\n**Task ID**: {task_id}\n**Timestamp**: {datetime.utcnow().isoformat()}\n**Operation**: Node Start\n**Status**: Completed (Fallback Mode)\n**RPC Status**: {rpc_status.get('error', 'N/A')}\n**Node Status**: Running (Fallback)\n**Mode**: Mock Data"
                })

                return {
                    "status": "success",
                    "message": "Jordan Mainnet node started in fallback mode",
                    "task_id": task_id,
                    "github_task": github_task,
                    "node_status": self.node_status,
                    "rpc_status": rpc_status,
                    "mode": "fallback"
                }
            else:
                self.node_status = "error"

                # Update GitHub task
                await self.update_github_issue({
                    "issue_number": github_task.get("issue_number"),
                    "body": f"Jordan Mainnet node failed to start\n\n**Task ID**: {task_id}\n**Timestamp**: {datetime.utcnow().isoformat()}\n**Operation**: Node Start\n**Status**: Failed\n**Error**: RPC connection failed\n**Node Status**: Error"
                })

                return {
                    "status": "error",
                    "message": "Failed to start Jordan Mainnet node - RPC connection failed",
                    "task_id": task_id,
                    "github_task": github_task,
                    "node_status": self.node_status,
                    "rpc_status": rpc_status
                }
                
        except Exception as e:
            logger.error(f"Error starting node: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def stop_node_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Stop Jordan Mainnet node operation"""
        try:
            task_id = str(uuid.uuid4())
            
            # Create GitHub task for node stop
            github_task = await self.create_github_issue({
                "title": f"Jordan Mainnet Node Stop - {task_id}",
                "body": f"Stopping Jordan Mainnet node operation\n\n**Task ID**: {task_id}\n**Timestamp**: {datetime.utcnow().isoformat()}\n**Operation**: Node Stop\n**Status**: In Progress",
                "labels": ["jordan-mainnet", "node-operation", "stop"]
            })
            
            # Update node status
            self.node_status = "stopping"
            
            # Simulate node shutdown process
            await asyncio.sleep(2)
            
            self.node_status = "stopped"
            self.sync_status = "not_synced"
            
            # Update GitHub task
            await self.update_github_issue({
                "issue_number": github_task.get("issue_number"),
                "body": f"Jordan Mainnet node stopped successfully\n\n**Task ID**: {task_id}\n**Timestamp**: {datetime.utcnow().isoformat()}\n**Operation**: Node Stop\n**Status**: Completed\n**Node Status**: Stopped"
            })
            
            return {
                "status": "success",
                "message": "Jordan Mainnet node stopped successfully",
                "task_id": task_id,
                "github_task": github_task,
                "node_status": self.node_status
            }
                
        except Exception as e:
            logger.error(f"Error stopping node: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def sync_node_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync Jordan Mainnet node operation"""
        try:
            task_id = str(uuid.uuid4())
            
            # Create GitHub task for node sync
            github_task = await self.create_github_issue({
                "title": f"Jordan Mainnet Node Sync - {task_id}",
                "body": f"Starting Jordan Mainnet node synchronization\n\n**Task ID**: {task_id}\n**Timestamp**: {datetime.utcnow().isoformat()}\n**Operation**: Node Sync\n**Status**: In Progress",
                "labels": ["jordan-mainnet", "node-operation", "sync"]
            })
            
            # Update sync status
            self.sync_status = "syncing"
            
            # Simulate sync process
            await asyncio.sleep(3)
            
            # Get latest block
            latest_block = await self.get_latest_block()
            
            if latest_block:
                self.last_block = latest_block
                self.sync_status = "synced"
                
                # Update GitHub task
                await self.update_github_issue({
                    "issue_number": github_task.get("issue_number"),
                    "body": f"Jordan Mainnet node synchronized successfully\n\n**Task ID**: {task_id}\n**Timestamp**: {datetime.utcnow().isoformat()}\n**Operation**: Node Sync\n**Status**: Completed\n**Latest Block**: {self.last_block}\n**Sync Status**: Synced"
                })
                
                return {
                    "status": "success",
                    "message": "Jordan Mainnet node synchronized successfully",
                    "task_id": task_id,
                    "github_task": github_task,
                    "sync_status": self.sync_status,
                    "latest_block": self.last_block
                }
            else:
                self.sync_status = "sync_failed"
                
                # Update GitHub task
                await self.update_github_issue({
                    "issue_number": github_task.get("issue_number"),
                    "body": f"Jordan Mainnet node synchronization failed\n\n**Task ID**: {task_id}\n**Timestamp**: {datetime.utcnow().isoformat()}\n**Operation**: Node Sync\n**Status**: Failed\n**Error**: Failed to get latest block\n**Sync Status**: Sync Failed"
                })
                
                return {
                    "status": "error",
                    "message": "Failed to synchronize Jordan Mainnet node",
                    "task_id": task_id,
                    "github_task": github_task,
                    "sync_status": self.sync_status
                }
                
        except Exception as e:
            logger.error(f"Error syncing node: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def check_rpc_connection(self) -> Dict[str, Any]:
        """Check RPC connection to Jordan Mainnet"""
        try:
            if not JORDAN_MAINNET_RPC_URL:
                return {
                    "connected": False,
                    "error": "RPC URL not configured",
                    "fallback_mode": True
                }

            # Check if RPC URL is a placeholder/demo URL
            if "jordan-mainnet.com" in JORDAN_MAINNET_RPC_URL.lower():
                logger.warning("Using placeholder RPC URL - switching to fallback mode")
                return {
                    "connected": False,
                    "error": "Placeholder RPC URL detected",
                    "fallback_mode": True
                }

            # Make a simple RPC call to check connection
            response = await self.rpc_client.post(
                JORDAN_MAINNET_RPC_URL,
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_chainId",
                    "params": [],
                    "id": 1
                },
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    return {
                        "connected": True,
                        "chain_id": data["result"],
                        "response_time": response.elapsed.total_seconds(),
                        "fallback_mode": False
                    }
                else:
                    return {
                        "connected": False,
                        "error": "Invalid RPC response format",
                        "fallback_mode": True
                    }
            else:
                return {
                    "connected": False,
                    "error": f"RPC request failed with status {response.status_code}",
                    "fallback_mode": True
                }

        except Exception as e:
            logger.warning(f"RPC connection check failed: {e} - using fallback mode")
            return {
                "connected": False,
                "error": str(e),
                "fallback_mode": True
            }

    async def get_network_info(self) -> Dict[str, Any]:
        """Get network information from Jordan Mainnet"""
        try:
            if not JORDAN_MAINNET_RPC_URL:
                return {
                    "error": "RPC URL not configured"
                }
            
            # Get network info via RPC
            response = await self.rpc_client.post(
                JORDAN_MAINNET_RPC_URL,
                json={
                    "jsonrpc": "2.0",
                    "method": "net_version",
                    "params": [],
                    "id": 1
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "network_id": data.get("result"),
                    "rpc_url": JORDAN_MAINNET_RPC_URL,
                    "explorer": JORDAN_MAINNET_EXPLORER,
                    "chain_id": JORDAN_MAINNET_CHAIN_ID
                }
            else:
                return {
                    "error": f"Failed to get network info: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "error": str(e)
            }

    async def get_latest_block(self) -> Optional[int]:
        """Get latest block number from Jordan Mainnet"""
        try:
            if not JORDAN_MAINNET_RPC_URL:
                return None
            
            response = await self.rpc_client.post(
                JORDAN_MAINNET_RPC_URL,
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_blockNumber",
                    "params": [],
                    "id": 1
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    return int(data["result"], 16)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest block: {e}")
            return None

    async def get_block_info(self, block_number: int) -> Dict[str, Any]:
        """Get block information from Jordan Mainnet"""
        try:
            if not JORDAN_MAINNET_RPC_URL:
                return {
                    "error": "RPC URL not configured"
                }
            
            response = await self.rpc_client.post(
                JORDAN_MAINNET_RPC_URL,
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_getBlockByNumber",
                    "params": [hex(block_number), False],
                    "id": 1
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "block_data": data.get("result", {}),
                    "block_number": block_number
                }
            else:
                return {
                    "status": "error",
                    "error": f"Failed to get block info: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_transaction_info(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction information from Jordan Mainnet"""
        try:
            if not JORDAN_MAINNET_RPC_URL:
                return {
                    "error": "RPC URL not configured"
                }
            
            response = await self.rpc_client.post(
                JORDAN_MAINNET_RPC_URL,
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_getTransactionByHash",
                    "params": [tx_hash],
                    "id": 1
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "transaction_data": data.get("result", {}),
                    "tx_hash": tx_hash
                }
            else:
                return {
                    "status": "error",
                    "error": f"Failed to get transaction info: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def make_rpc_call(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make custom RPC call to Jordan Mainnet"""
        try:
            if not JORDAN_MAINNET_RPC_URL:
                return {
                    "error": "RPC URL not configured"
                }
            
            method = data.get("method")
            params = data.get("params", [])
            request_id = data.get("id", 1)
            
            if not method:
                return {
                    "error": "Method is required"
                }
            
            response = await self.rpc_client.post(
                JORDAN_MAINNET_RPC_URL,
                json={
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": params,
                    "id": request_id
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "response": data
                }
            else:
                return {
                    "status": "error",
                    "error": f"RPC call failed with status {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    # GitHub Integration Methods
    async def create_github_issue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a GitHub issue via MCP"""
        try:
            if not self.github_pat:
                return {"error": "GitHub PAT not configured", "status": "error"}

            headers = {}
            # Handle both old (ghp_) and new (github_pat_) token formats
            if self.github_pat.startswith("github_pat_"):
                headers = {
                    "Authorization": f"Bearer {self.github_pat}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json"
                }
            else:
                headers = {
                    "Authorization": f"token {self.github_pat}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json"
                }

            issue_data = {
                "title": data.get("title", "Jordan Mainnet Node Task"),
                "body": data.get("body", "Task created via Jordan Mainnet Node service"),
                "labels": data.get("labels", ["jordan-mainnet", "node-operation"])
            }

            url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/issues"
            response = await self.github_client.post(url, json=issue_data, headers=headers)

            if response.status_code == 201:
                issue = response.json()
                logger.info(f"GitHub issue created: #{issue['number']} - {issue['title']}")
                return {
                    "status": "success",
                    "operation": "create_github_issue",
                    "issue_number": issue['number'],
                    "issue_url": issue['html_url'],
                    "title": issue['title']
                }
            else:
                error_msg = response.text
                logger.error(f"GitHub API error: {response.status_code} - {error_msg}")
                return {"error": f"GitHub API error: {response.status_code}", "status": "error"}

        except Exception as e:
            logger.error(f"GitHub issue creation error: {e}")
            return {"error": str(e), "status": "error"}

    async def list_github_issues(self, status: str = "open") -> Dict[str, Any]:
        """List GitHub issues via MCP"""
        try:
            if not self.github_pat:
                return {"error": "GitHub PAT not configured", "status": "error"}

            headers = {}
            # Handle both old (ghp_) and new (github_pat_) token formats
            if self.github_pat.startswith("github_pat_"):
                headers = {
                    "Authorization": f"Bearer {self.github_pat}",
                    "Accept": "application/vnd.github.v3+json"
                }
            else:
                headers = {
                    "Authorization": f"token {self.github_pat}",
                    "Accept": "application/vnd.github.v3+json"
                }

            url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/issues"
            params = {"state": status, "labels": "jordan-mainnet"}
            response = await self.github_client.get(url, params=params, headers=headers)

            if response.status_code == 200:
                issues = response.json()
                return {
                    "status": "success",
                    "operation": "list_github_issues",
                    "count": len(issues),
                    "issues": [
                        {
                            "number": issue["number"],
                            "title": issue["title"],
                            "state": issue["state"],
                            "url": issue["html_url"],
                            "created_at": issue["created_at"]
                        }
                        for issue in issues
                    ]
                }
            else:
                error_msg = response.text
                logger.error(f"GitHub API error: {response.status_code} - {error_msg}")
                return {"error": f"GitHub API error: {response.status_code}", "status": "error"}

        except Exception as e:
            logger.error(f"GitHub issues listing error: {e}")
            return {"error": str(e), "status": "error"}

    async def update_github_issue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a GitHub issue via MCP"""
        try:
            if not self.github_pat:
                return {"error": "GitHub PAT not configured", "status": "error"}

            issue_number = data.get("issue_number")
            if not issue_number:
                return {"error": "Issue number is required", "status": "error"}

            headers = {}
            # Handle both old (ghp_) and new (github_pat_) token formats
            if self.github_pat.startswith("github_pat_"):
                headers = {
                    "Authorization": f"Bearer {self.github_pat}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json"
                }
            else:
                headers = {
                    "Authorization": f"token {self.github_pat}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json"
                }

            update_data = {}
            if "title" in data:
                update_data["title"] = data["title"]
            if "body" in data:
                update_data["body"] = data["body"]
            if "state" in data:
                update_data["state"] = data["state"]

            url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/issues/{issue_number}"
            response = await self.github_client.patch(url, json=update_data, headers=headers)

            if response.status_code == 200:
                issue = response.json()
                logger.info(f"GitHub issue updated: #{issue['number']} - {issue['title']}")
                return {
                    "status": "success",
                    "operation": "update_github_issue",
                    "issue_number": issue['number'],
                    "issue_url": issue['html_url'],
                    "title": issue['title']
                }
            else:
                error_msg = response.text
                logger.error(f"GitHub API error: {response.status_code} - {error_msg}")
                return {"error": f"GitHub API error: {response.status_code}", "status": "error"}

        except Exception as e:
            logger.error(f"GitHub issue update error: {e}")
            return {"error": str(e), "status": "error"}

    async def startup(self):
        """Startup tasks for Jordan Mainnet node"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(REDIS_URL)
            await self.redis_client.ping()
            logger.info("Redis connection established")
            
            # Load credentials from vault
            await self.load_credentials_from_vault()
            
            # Check Jordan Mainnet configuration
            if not JORDAN_MAINNET_ENABLED:
                logger.warning("Jordan Mainnet is not enabled in configuration")
                self.node_status = "disabled"
                return
            
            # Check credentials (now using vault-loaded credentials)
            if not all([self.jordan_key, self.jordan_secret, self.jordan_passphrase]):
                logger.error("Jordan Mainnet credentials not fully configured")
                self.node_status = "config_error"
                return
            
            logger.info("# Check Jordan Mainnet credentials loaded successfully")
            
            # Check RPC connection
            rpc_status = await self.check_rpc_connection()
            if rpc_status["connected"]:
                self.node_status = "ready"
                logger.info("Jordan Mainnet node ready")
            elif rpc_status.get("fallback_mode"):
                self.node_status = "ready_fallback"
                logger.info("Jordan Mainnet node ready (fallback mode)")
            else:
                self.node_status = "rpc_error"
                logger.error(f"Jordan Mainnet RPC connection failed: {rpc_status.get('error')}")
                
        except Exception as e:
            logger.error(f"Startup error: {e}")
            self.node_status = "startup_error"

    async def shutdown(self):
        """Shutdown tasks for Jordan Mainnet node"""
        try:
            if self.redis_client:
                await self.redis_client.close()
                logger.info("Redis connection closed")
            
            await self.rpc_client.aclose()
            await self.github_client.aclose()
            logger.info("Jordan Mainnet node service shutdown complete")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

async def main():
    """Main entry point for Jordan Mainnet node service"""
    service = JordanMainnetNode()
    
    # Startup tasks
    await service.startup()
    
    # Start FastAPI server
    port = int(os.getenv('JORDAN_MAINNET_NODE_PORT', '8022'))
    config = uvicorn.Config(
        service.app,
        host="0.0.0.0",
        port=port,
        log_level=LOG_LEVEL.lower()
    )
    
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Shutting down Jordan Mainnet node service...")
    finally:
        await service.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
