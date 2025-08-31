#!/usr/bin/env python3
"""
# Rocket VIPER Trading Bot - Bitget Authentication Utility
Shared HMAC signature generation and API authentication for all services

Features:
- Secure HMAC-SHA256 signature generation
- Bitget API authentication headers
- Request signing for all endpoint types
- Swap-specific endpoint configuration
- Error handling and validation
"""

import os
import time
import hmac
import hashlib
import base64
import json
import logging
from typing import Dict, Optional, Any
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class BitgetAuthenticator:
    """Bitget API authentication utility for USDT swap endpoints"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, api_password: str = None):
        """Initialize authenticator with API credentials"""
        self.api_key = api_key or os.getenv('BITGET_API_KEY', '')
        self.api_secret = api_secret or os.getenv('BITGET_API_SECRET', '')
        self.api_password = api_password or os.getenv('BITGET_API_PASSWORD', '')
        
        # Bitget swap API configuration
        self.base_url = 'https://api.bitget.com'
        self.swap_endpoints = {
            'account': '/api/mix/v1/account/account',
            'positions': '/api/mix/v1/position/allPosition',
            'ticker': '/api/mix/v1/market/ticker',
            'orderbook': '/api/mix/v1/market/depth',
            'klines': '/api/mix/v1/market/candles',
            'place_order': '/api/mix/v1/order/placeOrder',
            'cancel_order': '/api/mix/v1/order/cancel-order',
            'order_status': '/api/mix/v1/order/detail',
            'open_orders': '/api/mix/v1/order/current',
            'balance': '/api/mix/v1/account/account',
            'leverage': '/api/mix/v1/account/setLeverage'
        }
        
        if not all([self.api_key, self.api_secret, self.api_password]):
            logger.warning("Bitget API credentials not fully configured")
    
    def generate_signature(self, timestamp: str, method: str, request_path: str, body: str = '') -> str:
        """Generate HMAC-SHA256 signature for Bitget API"""
        try:
            # Create message to sign: timestamp + method + requestPath + body
            message = timestamp + method.upper() + request_path + body
            
            # Generate HMAC-SHA256 signature
            signature = hmac.new(
                self.api_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
            
            # Base64 encode the signature
            return base64.b64encode(signature).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Failed to generate signature: {e}")
            raise
    
    def get_auth_headers(self, method: str, endpoint: str, params: Dict = None, body: Dict = None) -> Dict[str, str]:
        """Generate authentication headers for Bitget API request"""
        try:
            # Generate timestamp
            timestamp = str(int(time.time() * 1000))
            
            # Build request path
            request_path = endpoint
            if params:
                request_path += '?' + urlencode(params)
            
            # Prepare body string
            body_str = json.dumps(body, separators=(',', ':')) if body else ''
            
            # Generate signature
            signature = self.generate_signature(timestamp, method, request_path, body_str)
            
            # Return headers
            return {
                'ACCESS-KEY': self.api_key,
                'ACCESS-SIGN': signature,
                'ACCESS-TIMESTAMP': timestamp,
                'ACCESS-PASSPHRASE': self.api_password,
                'Content-Type': 'application/json',
                'locale': 'en-US'
            }
            
        except Exception as e:
            logger.error(f"Failed to generate auth headers: {e}")
            raise
    
    def get_swap_endpoint(self, endpoint_type: str) -> str:
        """Get swap-specific endpoint URL"""
        if endpoint_type not in self.swap_endpoints:
            raise ValueError(f"Unknown endpoint type: {endpoint_type}")
        
        return self.swap_endpoints[endpoint_type]
    
    def build_swap_url(self, endpoint_type: str) -> str:
        """Build complete URL for swap endpoint"""
        endpoint = self.get_swap_endpoint(endpoint_type)
        return self.base_url + endpoint
    
    def validate_credentials(self) -> bool:
        """Validate that all required credentials are present"""
        return all([self.api_key, self.api_secret, self.api_password])
    
    def get_usdt_swap_symbol(self, base_symbol: str) -> str:
        """Convert symbol to USDT swap format (e.g., BTC -> BTCUSDT_UMCBL)"""
        if base_symbol.endswith('USDT_UMCBL'):
            return base_symbol
        elif base_symbol.endswith('USDT'):
            return f"{base_symbol}_UMCBL"
        else:
            return f"{base_symbol}USDT_UMCBL"
    
    def prepare_swap_order_params(self, symbol: str, side: str, size: str, 
                                order_type: str = 'market', price: str = None,
                                leverage: int = 20) -> Dict[str, Any]:
        """Prepare order parameters for USDT swap trading"""
        # Convert symbol to swap format
        swap_symbol = self.get_usdt_swap_symbol(symbol)
        
        params = {
            'symbol': swap_symbol,
            'productType': 'UMCBL',  # USDT-M Futures
            'marginCoin': 'USDT',
            'side': side.lower(),  # open_long, open_short, close_long, close_short
            'orderType': order_type.lower(),  # market, limit
            'size': str(size),
            'timeInForce': 'IOC' if order_type.lower() == 'market' else 'GTC'
        }
        
        if price and order_type.lower() == 'limit':
            params['price'] = str(price)
        
        return params
    
    def prepare_position_params(self, symbol: str = None) -> Dict[str, Any]:
        """Prepare parameters for position queries"""
        params = {
            'productType': 'UMCBL',  # USDT-M Futures
            'marginCoin': 'USDT'
        }
        
        if symbol:
            params['symbol'] = self.get_usdt_swap_symbol(symbol)
        
        return params
    
    def prepare_market_data_params(self, symbol: str, **kwargs) -> Dict[str, Any]:
        """Prepare parameters for market data queries"""
        swap_symbol = self.get_usdt_swap_symbol(symbol)
        
        params = {
            'symbol': swap_symbol,
            'productType': 'UMCBL'
        }
        
        # Add any additional parameters
        params.update(kwargs)
        
        return params

# Global authenticator instance
_authenticator = None

def get_bitget_authenticator() -> BitgetAuthenticator:
    """Get global Bitget authenticator instance"""
    global _authenticator
    if _authenticator is None:
        _authenticator = BitgetAuthenticator()
    return _authenticator

def create_bitget_authenticator(api_key: str, api_secret: str, api_password: str) -> BitgetAuthenticator:
    """Create new Bitget authenticator with specific credentials"""
    return BitgetAuthenticator(api_key, api_secret, api_password)