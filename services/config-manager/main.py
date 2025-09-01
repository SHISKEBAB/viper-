#!/usr/bin/env python3
"""
# Rocket VIPER Trading Bot - Unified Configuration Manager Service
Single source of truth for all VIPER system configurations

Features:
- Unified configuration management across all services
- Runtime configuration updates with validation
- Service-specific configuration injection
- Environment-aware configuration loading
- Real-time configuration synchronization
- Configuration versioning and rollback
"""

import os
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn
import redis.asyncio as redis
from datetime import datetime
import jsonschema
from jsonschema import validate, ValidationError

# Load environment variables
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
SERVICE_NAME = os.getenv('SERVICE_NAME', 'config-manager')

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)

class UnifiedConfigManager:
    """Unified configuration manager - single source of truth for all VIPER configurations"""

    def __init__(self):
        self.redis_client = None
        self.app = FastAPI(title="VIPER Unified Configuration Manager", version="2.0.0")
        self.config_cache = {}
        self.config_watchers = {}
        self.config_versions = {}
        
        # Configuration file paths
        self.config_dir = Path(__file__).parent.parent.parent / 'config'
        self.unified_config_file = self.config_dir / 'unified_trading_config.json'
        self.legacy_config_file = self.config_dir / 'SAFE_TRADING_CONFIG.json'
        self.jordan_config_file = self.config_dir / 'jordan_mainnet_config.json'
        
        # Master configuration - single source of truth
        self.master_config = {}
        
        logger.info("# Construction Unified Configuration Manager initialized")
        self.setup_routes()

    def setup_routes(self):
        """Setup unified configuration manager routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "service": "unified-config-manager",
                "version": "2.0.0",
                "redis_connected": self.redis_client is not None,
                "config_files_loaded": len(self.config_cache),
                "master_config_loaded": bool(self.master_config),
                "active_services": list(self.config_cache.keys())
            }

        @self.app.get("/config/unified")
        async def get_unified_config():
            """Get the complete unified configuration - master source of truth"""
            try:
                if not self.master_config:
                    await self.load_unified_configuration()
                
                return {
                    "status": "success", 
                    "config": self.master_config,
                    "version": self.config_versions.get('unified', '1.0.0'),
                    "last_updated": datetime.utcnow().isoformat()
                }
            except Exception as e:
                logger.error(f"Error getting unified config: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")

        @self.app.get("/config/{service_name}")
        async def get_service_config(service_name: str):
            """Get configuration for a specific service from unified config"""
            try:
                config = await self.get_service_configuration(service_name)
                if config:
                    return {
                        "status": "success", 
                        "service": service_name,
                        "config": config,
                        "source": "unified_config",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    raise HTTPException(status_code=404, detail=f"Configuration not found for service: {service_name}")
            except Exception as e:
                logger.error(f"Error getting config for {service_name}: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")

        @self.app.post("/config/unified")
        async def update_unified_config(request: Request):
            """Update the unified configuration - master update"""
            try:
                config_data = await request.json()
                success = await self.update_unified_configuration(config_data)
                if success:
                    return {
                        "status": "success", 
                        "message": "Unified configuration updated successfully",
                        "version": self.config_versions.get('unified', '1.0.0'),
                        "services_notified": await self.notify_all_services()
                    }
                else:
                    raise HTTPException(status_code=400, detail="Failed to update unified configuration")
            except Exception as e:
                logger.error(f"Error updating unified config: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")

        @self.app.post("/config/{service_name}")
        async def update_service_config(service_name: str, request: Request):
            """Update configuration for a specific service within unified config"""
            try:
                config_data = await request.json()
                success = await self.update_service_in_unified_config(service_name, config_data)
                if success:
                    return {
                        "status": "success", 
                        "message": f"Configuration updated for {service_name} in unified config",
                        "service": service_name
                    }
                else:
                    raise HTTPException(status_code=400, detail="Failed to update service configuration")
            except Exception as e:
                logger.error(f"Error updating config for {service_name}: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")

        @self.app.get("/config")
        async def get_all_service_configs():
            """Get all service configurations from unified config"""
            try:
                configs = await self.get_all_service_configurations()
                return {
                    "status": "success", 
                    "configs": configs,
                    "source": "unified_config",
                    "total_services": len(configs),
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                logger.error(f"Error getting all configs: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")

        @self.app.get("/strategies")
        async def get_trading_strategies():
            """Get all trading strategy configurations from unified config"""
            try:
                strategies = await self.get_trading_strategies()
                return {
                    "status": "success",
                    "strategies": strategies,
                    "enabled_strategies": [name for name, config in strategies.items() if config.get('enabled', False)],
                    "total_strategies": len(strategies)
                }
            except Exception as e:
                logger.error(f"Error getting trading strategies: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")

        @self.app.post("/validate/config")
        async def validate_configuration(request: Request):
            """Validate a configuration against the unified schema"""
            try:
                config_data = await request.json()
                is_valid, errors = await self.validate_config_structure(config_data)
                return {
                    "status": "success",
                    "valid": is_valid,
                    "errors": errors,
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                logger.error(f"Error validating configuration: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")

    async def startup(self):
        """Initialize Redis and load unified configuration"""
        try:
            # Connect to Redis
            self.redis_client = redis.from_url(REDIS_URL)
            await self.redis_client.ping()
            logger.info("# Check Redis connection established")

            # Load unified configuration - single source of truth
            await self.load_unified_configuration()
            
            # Migrate legacy configurations to unified format
            await self.migrate_legacy_configurations()
            
            # Initialize service configurations from unified config
            await self.initialize_service_configurations()
            
            logger.info("# Check Unified Configuration Manager started successfully")
            
        except Exception as e:
            logger.error(f"# X Startup error: {e}")

    async def load_unified_configuration(self):
        """Load the unified configuration - master source of truth"""
        try:
            if self.unified_config_file.exists():
                with open(self.unified_config_file, 'r') as f:
                    self.master_config = json.load(f)
                    
                # Store in Redis as master config
                await self.redis_client.setex(
                    "viper:config:unified:master",
                    86400 * 7,  # 7 days - longer TTL for master config
                    json.dumps(self.master_config)
                )
                
                self.config_versions['unified'] = self.master_config.get('system_info', {}).get('version', '1.0.0')
                logger.info(f"# Check Unified configuration loaded - version {self.config_versions['unified']}")
                return True
            else:
                logger.error(f"# X Unified config file not found: {self.unified_config_file}")
                return False
                
        except Exception as e:
            logger.error(f"# X Error loading unified configuration: {e}")
            return False

    async def migrate_legacy_configurations(self):
        """Migrate legacy configurations to unified format"""
        try:
            # Check if legacy configs exist and merge them
            legacy_configs = {}
            
            if self.legacy_config_file.exists():
                with open(self.legacy_config_file, 'r') as f:
                    legacy_configs['safe_trading'] = json.load(f)
                    logger.info("# Check Legacy SAFE_TRADING_CONFIG.json loaded for migration")
            
            if self.jordan_config_file.exists():
                with open(self.jordan_config_file, 'r') as f:
                    legacy_configs['jordan_mainnet'] = json.load(f)
                    logger.info("# Check Legacy jordan_mainnet_config.json loaded for migration")
            
            # Store legacy configs for reference
            if legacy_configs:
                await self.redis_client.setex(
                    "viper:config:legacy:backup",
                    86400 * 30,  # 30 days backup
                    json.dumps(legacy_configs)
                )
                logger.info("# Check Legacy configurations backed up")
                
        except Exception as e:
            logger.error(f"# X Error migrating legacy configurations: {e}")

    async def initialize_service_configurations(self):
        """Initialize individual service configurations from unified config"""
        try:
            if not self.master_config:
                await self.load_unified_configuration()
            
            services = self.master_config.get('services', {}).get('microservices', {})
            
            for service_name, service_info in services.items():
                if service_info.get('enabled', False):
                    service_config = await self.generate_service_config(service_name)
                    
                    await self.redis_client.setex(
                        f"viper:config:service:{service_name}",
                        86400,  # 24 hours
                        json.dumps(service_config)
                    )
                    
                    self.config_cache[service_name] = service_config
                    logger.info(f"# Check Service configuration initialized for {service_name}")
                    
        except Exception as e:
            logger.error(f"# X Error initializing service configurations: {e}")

    async def generate_service_config(self, service_name: str) -> Dict[str, Any]:
        """Generate service-specific configuration from unified config"""
        try:
            service_config = {
                'service_info': {
                    'name': service_name,
                    'version': self.master_config.get('system_info', {}).get('version', '2.0.0'),
                    'source': 'unified_config'
                },
                'global_settings': self.master_config.get('global_settings', {}),
                'performance': self.master_config.get('performance', {}),
                'monitoring': self.master_config.get('monitoring', {}),
                'security': self.master_config.get('security', {})
            }
            
            # Add service-specific configurations
            if service_name == 'live-trading-engine':
                service_config.update({
                    'exchanges': self.master_config.get('exchanges', {}),
                    'trading_pairs': self.master_config.get('trading_pairs', {}),
                    'risk_management': self.master_config.get('risk_management', {}),
                    'strategies': self.master_config.get('strategies', {}),
                    'api_credentials': self.master_config.get('api_credentials', {})
                })
            
            elif service_name == 'ultra-backtester':
                service_config.update({
                    'backtesting': self.master_config.get('backtesting', {}),
                    'strategies': self.master_config.get('strategies', {}),
                    'trading_pairs': self.master_config.get('trading_pairs', {}),
                    'data_management': self.master_config.get('data_management', {})
                })
            
            elif service_name == 'market-data-manager':
                service_config.update({
                    'exchanges': self.master_config.get('exchanges', {}),
                    'trading_pairs': self.master_config.get('trading_pairs', {}),
                    'data_management': self.master_config.get('data_management', {}),
                    'api_credentials': self.master_config.get('api_credentials', {})
                })
            
            elif service_name == 'risk-manager':
                service_config.update({
                    'risk_management': self.master_config.get('risk_management', {}),
                    'trading_pairs': self.master_config.get('trading_pairs', {}),
                    'compliance': self.master_config.get('compliance', {})
                })
            
            elif service_name == 'jordan-mainnet-node':
                jordan_config = self.master_config.get('jordan_mainnet', {})
                if not jordan_config and self.jordan_config_file.exists():
                    # Fallback to legacy config if not in unified config
                    with open(self.jordan_config_file, 'r') as f:
                        jordan_config = json.load(f)
                
                service_config.update({
                    'jordan_mainnet': jordan_config,
                    'api_credentials': self.master_config.get('api_credentials', {})
                })
            
            return service_config
            
        except Exception as e:
            logger.error(f"# X Error generating config for {service_name}: {e}")
            return {}

    async def get_service_configuration(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific service from unified config"""
        try:
            # Check cache first
            if service_name in self.config_cache:
                return self.config_cache[service_name]
            
            # Check Redis
            config_data = await self.redis_client.get(f"viper:config:service:{service_name}")
            if config_data:
                config = json.loads(config_data)
                self.config_cache[service_name] = config
                return config
            
            # Generate from unified config
            if self.master_config:
                service_config = await self.generate_service_config(service_name)
                if service_config:
                    self.config_cache[service_name] = service_config
                    return service_config
            
            return None
            
        except Exception as e:
            logger.error(f"# X Error getting config for {service_name}: {e}")
            return None

    async def update_unified_configuration(self, config_data: Dict[str, Any]) -> bool:
        """Update the unified configuration - master update"""
        try:
            # Validate configuration structure
            is_valid, errors = await self.validate_config_structure(config_data)
            if not is_valid:
                logger.error(f"# X Configuration validation failed: {errors}")
                return False
            
            # Backup current config
            backup_key = f"viper:config:unified:backup:{datetime.utcnow().isoformat()}"
            await self.redis_client.setex(backup_key, 86400 * 7, json.dumps(self.master_config))
            
            # Update master config
            self.master_config = config_data
            
            # Update version
            current_version = self.config_versions.get('unified', '1.0.0')
            new_version = config_data.get('system_info', {}).get('version', current_version)
            self.config_versions['unified'] = new_version
            
            # Store in Redis
            await self.redis_client.setex(
                "viper:config:unified:master",
                86400 * 7,
                json.dumps(self.master_config)
            )
            
            # Save to file
            with open(self.unified_config_file, 'w') as f:
                json.dump(self.master_config, f, indent=2)
            
            # Regenerate all service configurations
            await self.initialize_service_configurations()
            
            # Notify all services
            await self.notify_unified_config_change()
            
            logger.info(f"# Check Unified configuration updated to version {new_version}")
            return True
            
        except Exception as e:
            logger.error(f"# X Error updating unified configuration: {e}")
            return False

    async def update_service_in_unified_config(self, service_name: str, service_config: Dict[str, Any]) -> bool:
        """Update a specific service configuration within unified config"""
        try:
            if not self.master_config:
                await self.load_unified_configuration()
            
            # Update the relevant section in unified config based on service
            if service_name == 'live-trading-engine':
                if 'risk_management' in service_config:
                    self.master_config['risk_management'] = service_config['risk_management']
                if 'strategies' in service_config:
                    self.master_config['strategies'] = service_config['strategies']
            elif service_name == 'ultra-backtester':
                if 'backtesting' in service_config:
                    self.master_config['backtesting'] = service_config['backtesting']
            # Add more service-specific updates as needed
            
            # Save updated unified config
            return await self.update_unified_configuration(self.master_config)
            
        except Exception as e:
            logger.error(f"# X Error updating {service_name} in unified config: {e}")
            return False

    async def get_all_service_configurations(self) -> Dict[str, Any]:
        """Get all service configurations from unified config"""
        try:
            configs = {}
            services = self.master_config.get('services', {}).get('microservices', {})
            
            for service_name, service_info in services.items():
                if service_info.get('enabled', False):
                    config = await self.get_service_configuration(service_name)
                    if config:
                        configs[service_name] = config
            
            return configs
            
        except Exception as e:
            logger.error(f"# X Error getting all service configurations: {e}")
            return {}

    async def get_trading_strategies(self) -> Dict[str, Any]:
        """Get all trading strategy configurations from unified config"""
        try:
            return self.master_config.get('strategies', {})
        except Exception as e:
            logger.error(f"# X Error getting trading strategies: {e}")
            return {}

    async def validate_config_structure(self, config_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate configuration structure"""
        try:
            errors = []
            
            # Basic structure validation
            required_sections = ['system_info', 'global_settings', 'services', 'strategies']
            for section in required_sections:
                if section not in config_data:
                    errors.append(f"Missing required section: {section}")
            
            # Validate strategies
            if 'strategies' in config_data:
                strategies = config_data['strategies']
                if 'enabled_strategies' not in strategies:
                    errors.append("Missing 'enabled_strategies' in strategies section")
            
            # Validate services
            if 'services' in config_data:
                services = config_data['services']
                if 'microservices' not in services:
                    errors.append("Missing 'microservices' in services section")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]

    async def notify_all_services(self) -> List[str]:
        """Notify all services of configuration changes"""
        try:
            notified_services = []
            services = self.master_config.get('services', {}).get('microservices', {})
            
            for service_name in services.keys():
                await self.notify_service_config_change(service_name)
                notified_services.append(service_name)
            
            return notified_services
            
        except Exception as e:
            logger.error(f"# X Error notifying services: {e}")
            return []

    async def notify_unified_config_change(self):
        """Notify all services of unified configuration change"""
        try:
            notification = {
                'type': 'unified_config_update',
                'version': self.config_versions.get('unified', '1.0.0'),
                'timestamp': datetime.utcnow().isoformat(),
                'services_affected': list(self.master_config.get('services', {}).get('microservices', {}).keys())
            }
            
            await self.redis_client.publish('config_updates', json.dumps(notification))
            logger.info("# Check Unified configuration change notification sent to all services")
            
        except Exception as e:
            logger.error(f"# X Error sending unified config change notification: {e}")

    async def notify_service_config_change(self, service_name: str):
        """Notify a specific service of configuration changes"""
        try:
            config = await self.get_service_configuration(service_name)
            notification = {
                'type': 'service_config_update',
                'service': service_name,
                'config': config,
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'unified_config'
            }
            
            await self.redis_client.publish(f'config_updates:{service_name}', json.dumps(notification))
            logger.info(f"# Check Configuration change notification sent to {service_name}")
            
        except Exception as e:
            logger.error(f"# X Error sending config change notification to {service_name}: {e}")

    async def shutdown(self):
        """Cleanup on shutdown"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            logger.info("# Check Unified Configuration Manager shutdown complete")
        except Exception as e:
            logger.error(f"# X Shutdown error: {e}")

async def main():
    """Main entry point"""
    manager = UnifiedConfigManager()
    
    # Startup
    await manager.startup()
    
    # Start FastAPI server
    port = int(os.getenv('CONFIG_MANAGER_PORT', '8001'))
    config = uvicorn.Config(
        manager.app,
        host="0.0.0.0", 
        port=port,
        log_level=LOG_LEVEL.lower()
    )
    
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("# Stop Shutting down Unified Configuration Manager...")
    finally:
        await manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())