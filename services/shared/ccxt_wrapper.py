#!/usr/bin/env python3
"""
🔌 CCXT Wrapper for Bitget API
Replaces broken custom authentication with reliable CCXT implementation
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import ccxt.async_support as ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False
    logger.error("❌ CCXT not available - install with: pip install ccxt")

class CCXTBitgetWrapper:
    """CCXT wrapper for Bitget API operations"""
    
    def __init__(self):
        """Initialize CCXT wrapper"""
        if not CCXT_AVAILABLE:
            raise ImportError("CCXT not available")
        
        # Get API credentials
        self.api_key = os.getenv('BITGET_API_KEY')
        self.api_secret = os.getenv('BITGET_API_SECRET')
        self.api_password = os.getenv('BITGET_API_PASSWORD')
        
        if not all([self.api_key, self.api_secret, self.api_password]):
            raise ValueError("Missing Bitget API credentials")
        
        # Initialize exchange
        self.exchange = ccxt.bitget({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'password': self.api_password,
            'sandbox': False,  # Use live trading
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap',  # Use USDT-M futures
                'defaultMarginMode': 'cross',
                'defaultLeverage': 10
            }
        })
        
        logger.info("✅ CCXT Bitget wrapper initialized")
    
    async def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        try:
            balance = await self.exchange.fetch_balance()
            
            if balance and 'USDT' in balance:
                usdt_balance = balance['USDT']
                return {
                    'code': '00000',
                    'msg': 'success',
                    'data': [{
                        'marginCoin': 'USDT',
                        'available': str(usdt_balance.get('free', 0)),
                        'locked': str(usdt_balance.get('used', 0)),
                        'total': str(usdt_balance.get('total', 0)),
                        'unrealizedPL': '0'
                    }]
                }
            else:
                return {'code': '500', 'msg': 'No USDT balance found', 'data': []}
                
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {'code': '500', 'msg': str(e), 'data': []}
    
    async def get_positions(self) -> Dict[str, Any]:
        """Get all positions"""
        try:
            positions = await self.exchange.fetch_positions()
            
            if positions:
                # Filter open positions
                open_positions = [p for p in positions if p.get('size', 0) > 0]
                
                position_data = []
                for pos in open_positions:
                    position_data.append({
                        'id': pos.get('id', ''),
                        'symbol': pos.get('symbol', ''),
                        'side': pos.get('side', ''),
                        'size': str(pos.get('size', 0)),
                        'entryPrice': str(pos.get('entryPrice', 0)),
                        'markPrice': str(pos.get('markPrice', 0)),
                        'unrealizedPnl': str(pos.get('unrealizedPnl', 0)),
                        'marginMode': pos.get('marginMode', 'cross'),
                        'leverage': str(pos.get('leverage', 1))
                    })
                
                return {
                    'code': '00000',
                    'msg': 'success',
                    'data': position_data
                }
            else:
                return {'code': '00000', 'msg': 'success', 'data': []}
                
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return {'code': '500', 'msg': str(e), 'data': []}
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get market ticker"""
        try:
            # Convert symbol format for CCXT - Bitget uses BTC/USDT format
            if symbol == 'BTCUSDT':
                ccxt_symbol = 'BTC/USDT'
            elif symbol == 'ETHUSDT':
                ccxt_symbol = 'ETH/USDT'
            else:
                # Handle other symbols like XCZNBTCUSDT -> XCZNBTC/USDT, or keep as-is if already formatted
                if 'USDT' in symbol:
                    base = symbol.replace('USDT', '')
                    ccxt_symbol = f"{base}/USDT"
                else:
                    ccxt_symbol = symbol
            
            ticker = await self.exchange.fetch_ticker(ccxt_symbol)
            
            if ticker:
                return {
                    'code': '00000',
                    'msg': 'success',
                    'data': [{
                        'symbol': symbol,
                        'last': str(ticker.get('last', 0)),
                        'bid': str(ticker.get('bid', 0)),
                        'ask': str(ticker.get('ask', 0)),
                        'volume': str(ticker.get('baseVolume', 0)),
                        'change': str(ticker.get('change', 0))
                    }]
                }
            else:
                return {'code': '500', 'msg': 'Ticker not found', 'data': []}
                
        except Exception as e:
            logger.error(f"Error fetching ticker: {e}")
            return {'code': '500', 'msg': str(e), 'data': []}
    
    async def get_open_orders(self, symbol: str = 'BTCUSDT') -> Dict[str, Any]:
        """Get open orders"""
        try:
            orders = await self.exchange.fetch_open_orders()
            
            if orders:
                order_data = []
                for order in orders:
                    order_data.append({
                        'id': order.get('id', ''),
                        'symbol': order.get('symbol', ''),
                        'side': order.get('side', ''),
                        'type': order.get('type', ''),
                        'amount': str(order.get('amount', 0)),
                        'price': str(order.get('price', 0)),
                        'status': order.get('status', ''),
                        'timestamp': order.get('timestamp', 0)
                    })
                
                return {
                    'code': '00000',
                    'msg': 'success',
                    'data': order_data
                }
            else:
                return {'code': '00000', 'msg': 'success', 'data': []}
                
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return {'code': '500', 'msg': str(e), 'data': []}
    
    async def place_order(self, symbol: str, side: str, size: str, 
                         order_type: str = 'market', price: str = None) -> Dict[str, Any]:
        """Place an order"""
        try:
            # Convert symbol format for CCXT
            ccxt_symbol = f"{symbol}:USDT" if ':USDT' not in symbol else symbol
            
            # Convert side format
            ccxt_side = 'buy' if side in ['buy', 'open_long'] else 'sell'
            
            # Convert size to float
            try:
                amount = float(size)
            except ValueError:
                amount = 0.001  # Default safe size
            
            order_params = {}
            if order_type == 'limit' and price:
                order_params['price'] = float(price)
            
            order = await self.exchange.create_order(
                symbol=ccxt_symbol,
                type=order_type,
                side=ccxt_side,
                amount=amount,
                **order_params
            )
            
            if order and order.get('id'):
                return {
                    'code': '00000',
                    'msg': 'success',
                    'data': {
                        'orderId': order.get('id'),
                        'symbol': symbol,
                        'side': side,
                        'size': size,
                        'type': order_type,
                        'status': 'placed'
                    }
                }
            else:
                return {'code': '500', 'msg': 'Order placement failed', 'data': None}
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {'code': '500', 'msg': str(e), 'data': None}
    
    async def close(self):
        """Close exchange connection"""
        if hasattr(self, 'exchange'):
            await self.exchange.close()
            logger.info("✅ CCXT exchange connection closed")

# Global instance
_ccxt_wrapper = None

def get_ccxt_wrapper() -> CCXTBitgetWrapper:
    """Get global CCXT wrapper instance"""
    global _ccxt_wrapper
    if _ccxt_wrapper is None:
        _ccxt_wrapper = CCXTBitgetWrapper()
    return _ccxt_wrapper

async def close_ccxt_wrapper():
    """Close global CCXT wrapper"""
    global _ccxt_wrapper
    if _ccxt_wrapper:
        await _ccxt_wrapper.close()
        _ccxt_wrapper = None
