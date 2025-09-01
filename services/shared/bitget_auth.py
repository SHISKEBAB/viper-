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
import aiohttp
import asyncio
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
        
        # Bitget swap API configuration - USE V2 ENDPOINTS WITH V2 PARAMETERS
        self.base_url = 'https://api.bitget.com'
        self.swap_endpoints = {
            'account': '/api/v2/mix/account/account',
            'positions': '/api/v2/mix/position/allPosition',
            'ticker': '/api/v2/mix/market/ticker',
            'orderbook': '/api/v2/mix/market/depth',
            'klines': '/api/v2/mix/market/candles',
            'place_order': '/api/v2/mix/order/place-order',
            'cancel_order': '/api/v2/mix/order/cancel-order',
            'order_status': '/api/v2/mix/order/detail',
            'open_orders': '/api/v2/mix/order/current',
            'balance': '/api/v2/mix/account/account',
            'leverage': '/api/v2/mix/account/setLeverage'
        }
        
        if not all([self.api_key, self.api_secret, self.api_password]):
            logger.warning("Bitget API credentials not fully configured")
    
    def generate_signature(self, timestamp: str, method: str, request_path: str, body: str = '') -> str:
        """Generate HMAC-SHA256 signature for Bitget API"""
        try:
            # Create message to sign: timestamp + method + requestPath + body
            message = timestamp + method.upper() + request_path + body

            # Debug logging
            logger.debug(f"Signature message: {message}")
            logger.debug(f"API Secret (first 8 chars): {self.api_secret[:8]}...")

            # Generate HMAC-SHA256 signature
            signature = hmac.new(
                self.api_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()

            # Base64 encode the signature
            signature_b64 = base64.b64encode(signature).decode('utf-8')
            logger.debug(f"Generated signature: {signature_b64[:20]}...")

            return signature_b64

        except Exception as e:
            logger.error(f"Failed to generate signature: {e}")
            raise
    
    async def test_api_connection(self) -> bool:
        """Test API connection with a simple authenticated request"""
        try:
            import aiohttp

            logger.info("🔍 Testing API key validity...")

            # Try a simpler endpoint first - ticker (might not require auth or special perms)
            logger.info("Testing with public ticker endpoint...")
            test_endpoint = '/api/v2/mix/market/ticker'
            params = {'symbol': 'BTCUSDT'}

            async with aiohttp.ClientSession() as session:
                query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
                url = f"{self.base_url}{test_endpoint}?{query_string}"

                async with session.get(url) as response:
                    result = await response.json()
                    logger.info(f"Public ticker response: {result}")

            # Now test authenticated endpoint
            logger.info("Testing authenticated account endpoint...")

            # Try account endpoint with minimal parameters
            test_endpoint = '/api/mix/v1/account/account'
            params = {'productType': 'umcbl'}
            headers = self.get_auth_headers('GET', test_endpoint, params=params)

            # Build URL with query parameters
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{self.base_url}{test_endpoint}?{query_string}"

            logger.info(f"Request URL: {url}")
            logger.info(f"Headers: ACCESS-KEY={headers.get('ACCESS-KEY', 'MISSING')[:10]}...")

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    result = await response.json()

                    logger.info(f"Response status: {response.status}")
                    logger.info(f"Response: {result}")

                    if response.status == 200 and result.get('code') == '00000':
                        logger.info("✅ Bitget API connection successful!")
                        return True
                    elif result.get('code') == '40006':
                        logger.error("❌ Invalid API key - key does not exist in Bitget system")
                        return False
                    elif result.get('code') == '40009':
                        logger.error("❌ Signature error - API key exists but signature is wrong")
                        return False
                    elif result.get('code') == '400172':
                        logger.error("❌ Parameter verification failed - API key exists but lacks permissions")
                        return False
                    elif result.get('code') == '40013':
                        logger.error("❌ Insufficient permissions - API key doesn't have trading permissions")
                        return False
                    else:
                        logger.warning(f"❌ Unexpected error: {result}")
                        return False

        except Exception as e:
            logger.error(f"❌ API test failed: {e}")
            return False

    def get_auth_headers(self, method: str, endpoint: str, params: Dict = None, body: Dict = None) -> Dict[str, str]:
        """Generate authentication headers for Bitget API request"""
        try:
            # Generate timestamp as close as possible to request time
            # Generate timestamp multiple times to get the most recent one
            for _ in range(3):
                timestamp = str(int(time.time() * 1000))

            # Build request path
            request_path = endpoint
            if params:
                request_path += '?' + urlencode(params)

            # Prepare body string - do this right before signature generation
            body_str = json.dumps(body, separators=(',', ':')) if body else ''

            # Generate signature immediately after body preparation
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
        """Convert symbol to USDT swap format - V2 API (e.g., BTC -> BTCUSDT)"""
        if base_symbol.endswith('USDT'):
            return base_symbol
        elif base_symbol.endswith('USDT_UMCBL'):
            # Convert from old format to new V2 format
            return base_symbol.replace('_UMCBL', '')
        else:
            return f"{base_symbol}USDT"
    
    def prepare_swap_order_params(self, symbol: str, side: str, size: str, 
                                order_type: str = 'market', price: str = None,
                                leverage: int = 20) -> Dict[str, Any]:
        """Prepare order parameters for USDT swap trading"""
        # Convert symbol to swap format
        swap_symbol = self.get_usdt_swap_symbol(symbol)
        
        params = {
            'symbol': swap_symbol,
            'productType': 'usdt-futures',  # V2 API: USDT-M Futures
            'marginCoin': 'USDT',
            'side': side.lower(),  # open_long, open_short, close_long, close_short
            'orderType': order_type.lower(),  # market, limit
            'size': str(size),
            'timeInForce': 'IOC' if order_type.lower() == 'market' else 'GTC',
            'marginMode': 'crossed'  # Required: cross or isolated margin mode
        }
        
        if price and order_type.lower() == 'limit':
            params['price'] = str(price)
        
        return params
    
    def prepare_position_params(self, symbol: str = None) -> Dict[str, Any]:
        """Prepare parameters for position queries"""
        params = {
            'productType': 'usdt-futures',  # V2 API: USDT-M Futures
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

    async def make_request(self, method: str, endpoint: str, params: Dict = None,
                          body: Dict = None) -> Dict[str, Any]:
        """Make authenticated HTTP request to Bitget API"""
        try:
            url = self.build_swap_url(endpoint)
            headers = self.get_auth_headers(method, self.get_swap_endpoint(endpoint), params, body)

            async with aiohttp.ClientSession() as session:
                if method.upper() == 'GET':
                    if params:
                        url += '?' + urlencode(params)
                    async with session.get(url, headers=headers) as response:
                        return await response.json()
                elif method.upper() == 'POST':
                    # Bitget expects raw JSON string, not json=body
                    body_string = json.dumps(body, separators=(',', ':')) if body else ''
                    async with session.post(url, headers=headers, data=body_string) as response:
                        return await response.json()
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {'code': '500', 'msg': str(e)}

    async def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance for USDT swap trading"""
        try:
            params = {
                'productType': 'UMCBL',  # V2 API: USDT-M Futures (correct format)
                'marginCoin': 'USDT'
            }

            response = await self.make_request('GET', 'account', params)
            return response

        except Exception as e:
            logger.error(f"Failed to get account balance: {e}")
            return {'code': '500', 'msg': str(e), 'data': []}

    async def get_positions(self) -> Dict[str, Any]:
        """Get all positions for USDT swap trading"""
        try:
            params = {
                'productType': 'UMCBL',  # V2 API: USDT-M Futures (correct format)
                'marginCoin': 'USDT'
            }

            response = await self.make_request('GET', 'positions', params)
            return response

        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return {'code': '500', 'msg': str(e), 'data': []}

    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get market ticker for USDT swap trading"""
        try:
            params = {
                'symbol': symbol,
                'productType': 'UMCBL'  # V2 API: USDT-M Futures (correct format)
            }

            response = await self.make_request('GET', 'ticker', params)
            return response

        except Exception as e:
            logger.error(f"Failed to get ticker: {e}")
            return {'code': '500', 'msg': str(e), 'data': []}

    async def get_open_orders(self, symbol: str = 'BTCUSDT') -> Dict[str, Any]:
        """Get open orders for USDT swap trading"""
        try:
            params = {
                'symbol': symbol,
                'productType': 'UMCBL',  # V2 API: USDT-M Futures (correct format)
                'marginCoin': 'USDT'
            }

            response = await self.make_request('GET', 'open_orders', params)
            return response

        except Exception as e:
            logger.error(f"Failed to get open orders: {e}")
            return {'code': '500', 'msg': str(e), 'data': []}

    async def get_klines(self, symbol: str, granularity: str, limit: int = 1000) -> Dict[str, Any]:
        """Get historical klines/candles for USDT swap trading
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            granularity: Timeframe ('1m', '5m', '15m', '30m', '1H', '4H', '1D')
            limit: Number of candles to fetch (max 1000)
        """
        try:
            params = {
                'symbol': self.get_usdt_swap_symbol(symbol),
                'productType': 'UMCBL',  # V2 API: USDT-M Futures
                'granularity': granularity,
                'limit': str(limit)
            }

            response = await self.make_request('GET', 'klines', params)
            return response

        except Exception as e:
            logger.error(f"Failed to get klines for {symbol}: {e}")
            return {'code': '500', 'msg': str(e), 'data': []}

    async def place_order(self, symbol: str, side: str, size: str,
                         order_type: str = 'market', price: str = None) -> Dict[str, Any]:
        """Place order for USDT swap trading"""
        try:
            order_params = self.prepare_swap_order_params(
                symbol, side, size, order_type, price
            )

            response = await self.make_request('POST', 'place_order', body=order_params)
            return response

        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return {'code': '500', 'msg': str(e)}

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