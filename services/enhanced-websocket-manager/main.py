#!/usr/bin/env python3
"""
# Rocket VIPER Trading Bot - Enhanced Websocket Manager with Vectorization
High-performance websocket connection manager with advanced optimizations

Features:
- Vectorized data processing for maximum speed
- Connection pooling and load balancing
- Automatic reconnection with exponential backoff
- Real-time data compression and buffering
- Multi-threaded message processing
- Memory-optimized data structures
- Advanced error handling and recovery
- Performance monitoring and metrics
"""

import os
import sys
import json
import asyncio
import logging
import websockets
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import time
import gzip
import pickle
from collections import defaultdict, deque
import redis.asyncio as redis

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    """Vectorized market data structure for optimal performance"""
    symbol: str
    timestamp: float
    price: float
    volume: float
    bid: float
    ask: float
    high_24h: float
    low_24h: float
    change_24h: float
    
    def to_numpy_array(self) -> np.ndarray:
        """Convert to numpy array for vectorized operations"""
        return np.array([
            self.timestamp, self.price, self.volume, self.bid, 
            self.ask, self.high_24h, self.low_24h, self.change_24h
        ], dtype=np.float64)
    
    @classmethod
    def from_numpy_array(cls, symbol: str, arr: np.ndarray) -> 'MarketData':
        """Create from numpy array"""
        return cls(
            symbol=symbol,
            timestamp=float(arr[0]),
            price=float(arr[1]),
            volume=float(arr[2]),
            bid=float(arr[3]),
            ask=float(arr[4]),
            high_24h=float(arr[5]),
            low_24h=float(arr[6]),
            change_24h=float(arr[7])
        )

class VectorizedDataProcessor:
    """High-performance vectorized data processing engine"""
    
    def __init__(self, buffer_size: int = 10000):
        self.buffer_size = buffer_size
        self.data_buffers = defaultdict(lambda: deque(maxlen=buffer_size))
        self.numpy_buffers = defaultdict(lambda: np.zeros((buffer_size, 8), dtype=np.float64))
        self.buffer_indices = defaultdict(int)
        self.processing_stats = {
            'messages_processed': 0,
            'processing_time_avg': 0.0,
            'throughput_msg_per_sec': 0.0,
            'memory_usage_mb': 0.0
        }
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="VectorProcessor")
        
    def add_data_point(self, data: MarketData):
        """Add data point to vectorized buffer"""
        try:
            symbol = data.symbol
            idx = self.buffer_indices[symbol] % self.buffer_size
            
            # Store in numpy buffer for vectorized operations
            self.numpy_buffers[symbol][idx] = data.to_numpy_array()
            self.buffer_indices[symbol] += 1
            
            # Update processing stats
            self.processing_stats['messages_processed'] += 1
            
        except Exception as e:
            logger.error(f"# X Error adding data point: {e}")
    
    def get_vectorized_data(self, symbol: str, lookback: int = 100) -> np.ndarray:
        """Get vectorized data for analysis"""
        try:
            buffer = self.numpy_buffers[symbol]
            current_idx = self.buffer_indices[symbol]
            
            if current_idx == 0:
                return np.array([])
            
            # Get the last 'lookback' data points in circular buffer order
            if current_idx >= self.buffer_size:
                # Buffer is full, need to handle wraparound
                start_idx = current_idx % self.buffer_size
                if start_idx >= lookback:
                    return buffer[start_idx - lookback:start_idx].copy()
                else:
                    # Wraparound case
                    part1 = buffer[self.buffer_size - (lookback - start_idx):]
                    part2 = buffer[:start_idx]
                    return np.vstack([part1, part2])
            else:
                # Buffer not full yet
                end_idx = min(current_idx, lookback)
                return buffer[:end_idx].copy()
                
        except Exception as e:
            logger.error(f"# X Error getting vectorized data for {symbol}: {e}")
            return np.array([])
    
    def calculate_technical_indicators(self, symbol: str, lookback: int = 50) -> Dict[str, np.ndarray]:
        """Calculate technical indicators using vectorized operations"""
        try:
            data = self.get_vectorized_data(symbol, lookback)
            if data.size == 0:
                return {}
            
            prices = data[:, 1]  # Price column
            volumes = data[:, 2]  # Volume column
            
            indicators = {}
            
            # Simple Moving Average (vectorized)
            if len(prices) >= 20:
                indicators['sma_20'] = np.convolve(prices, np.ones(20)/20, mode='valid')
            
            if len(prices) >= 50:
                indicators['sma_50'] = np.convolve(prices, np.ones(50)/50, mode='valid')
            
            # RSI (vectorized calculation)
            if len(prices) >= 14:
                indicators['rsi'] = self.calculate_rsi_vectorized(prices, 14)
            
            # Bollinger Bands
            if len(prices) >= 20:
                sma = np.convolve(prices, np.ones(20)/20, mode='valid')
                std = np.array([np.std(prices[i:i+20]) for i in range(len(prices)-19)])
                indicators['bb_upper'] = sma + (2 * std)
                indicators['bb_lower'] = sma - (2 * std)
                indicators['bb_middle'] = sma
            
            # Volume indicators
            if len(volumes) >= 20:
                indicators['volume_sma'] = np.convolve(volumes, np.ones(20)/20, mode='valid')
            
            # Price changes (vectorized)
            if len(prices) > 1:
                indicators['price_changes'] = np.diff(prices)
                indicators['returns'] = indicators['price_changes'] / prices[:-1]
            
            return indicators
            
        except Exception as e:
            logger.error(f"# X Error calculating technical indicators: {e}")
            return {}
    
    def calculate_rsi_vectorized(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """Vectorized RSI calculation"""
        try:
            if len(prices) < period + 1:
                return np.array([])
            
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            # Use pandas for efficient rolling calculations
            gains_series = pd.Series(gains)
            losses_series = pd.Series(losses)
            
            avg_gains = gains_series.rolling(window=period, min_periods=period).mean()
            avg_losses = losses_series.rolling(window=period, min_periods=period).mean()
            
            rs = avg_gains / avg_losses
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.fillna(50).values
            
        except Exception as e:
            logger.error(f"# X Error calculating RSI: {e}")
            return np.array([])
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get processing performance statistics"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            self.processing_stats['memory_usage_mb'] = memory_mb
            
            return self.processing_stats.copy()
            
        except Exception as e:
            logger.error(f"# X Error getting performance stats: {e}")
            return self.processing_stats.copy()

class EnhancedWebsocketManager:
    """Enhanced websocket manager with vectorization and performance optimizations"""
    
    def __init__(self):
        self.connections = {}
        self.connection_pools = {}
        self.data_processor = VectorizedDataProcessor()
        self.redis_client = None
        self.is_running = False
        
        # Performance settings
        self.max_connections = int(os.getenv('WS_MAX_CONNECTIONS', '20'))
        self.reconnect_delay = 1.0
        self.max_reconnect_delay = 60.0
        self.heartbeat_interval = 30
        self.message_buffer_size = int(os.getenv('WS_BUFFER_SIZE', '8192'))
        self.compression_enabled = os.getenv('WS_COMPRESSION', 'true').lower() == 'true'
        
        # Message processing queues
        self.message_queues = defaultdict(lambda: queue.Queue(maxsize=10000))
        self.processing_threads = []
        
        # Statistics
        self.stats = {
            'connections_active': 0,
            'messages_received': 0,
            'messages_processed': 0,
            'reconnections': 0,
            'errors': 0,
            'uptime_start': time.time(),
            'throughput_msg_per_sec': 0.0
        }
        
        # Event handlers
        self.event_handlers = defaultdict(list)
        
        logger.info("# Construction Enhanced Websocket Manager initialized")
    
    async def initialize(self):
        """Initialize the websocket manager"""
        try:
            # Connect to Redis for data caching
            self.redis_client = redis.from_url(REDIS_URL)
            await self.redis_client.ping()
            logger.info("# Check Redis connection established")
            
            # Start message processing threads
            self.start_processing_threads()
            
            self.is_running = True
            logger.info("# Check Enhanced Websocket Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"# X Initialization failed: {e}")
            return False
    
    def start_processing_threads(self):
        """Start message processing threads"""
        try:
            num_threads = min(4, os.cpu_count())
            for i in range(num_threads):
                thread = threading.Thread(
                    target=self.message_processing_worker,
                    name=f"WSProcessor-{i}",
                    daemon=True
                )
                thread.start()
                self.processing_threads.append(thread)
                
            logger.info(f"# Check Started {num_threads} message processing threads")
            
        except Exception as e:
            logger.error(f"# X Error starting processing threads: {e}")
    
    def message_processing_worker(self):
        """Worker thread for processing websocket messages"""
        while self.is_running:
            try:
                # Process messages from all symbol queues
                messages_processed = 0
                start_time = time.time()
                
                for symbol, message_queue in self.message_queues.items():
                    try:
                        while not message_queue.empty() and messages_processed < 100:
                            message = message_queue.get_nowait()
                            self.process_message(symbol, message)
                            messages_processed += 1
                            message_queue.task_done()
                    except queue.Empty:
                        continue
                    except Exception as e:
                        logger.error(f"# X Error processing message for {symbol}: {e}")
                
                # Update throughput statistics
                if messages_processed > 0:
                    processing_time = time.time() - start_time
                    throughput = messages_processed / processing_time if processing_time > 0 else 0
                    self.stats['throughput_msg_per_sec'] = throughput
                    self.stats['messages_processed'] += messages_processed
                
                # Brief sleep to prevent CPU spinning
                time.sleep(0.001)
                
            except Exception as e:
                logger.error(f"# X Error in message processing worker: {e}")
                time.sleep(0.1)
    
    def process_message(self, symbol: str, message: Dict):
        """Process a single websocket message with vectorized operations"""
        try:
            # Extract market data from message
            if 'data' in message:
                data = message['data']
                
                # Create market data object
                market_data = MarketData(
                    symbol=symbol,
                    timestamp=data.get('timestamp', time.time() * 1000),
                    price=float(data.get('price', data.get('last', 0))),
                    volume=float(data.get('volume', data.get('vol', 0))),
                    bid=float(data.get('bid', data.get('bidPrice', 0))),
                    ask=float(data.get('ask', data.get('askPrice', 0))),
                    high_24h=float(data.get('high24h', data.get('high', 0))),
                    low_24h=float(data.get('low24h', data.get('low', 0))),
                    change_24h=float(data.get('change24h', data.get('change', 0)))
                )
                
                # Add to vectorized processor
                self.data_processor.add_data_point(market_data)
                
                # Cache in Redis for other services
                asyncio.create_task(self.cache_market_data(symbol, asdict(market_data)))
                
                # Trigger event handlers
                self.trigger_event_handlers('market_data', symbol, market_data)
                
        except Exception as e:
            logger.error(f"# X Error processing message for {symbol}: {e}")
    
    async def cache_market_data(self, symbol: str, data: Dict):
        """Cache market data in Redis for other services"""
        try:
            if self.redis_client:
                # Compress data if enabled
                if self.compression_enabled:
                    data_bytes = gzip.compress(pickle.dumps(data))
                    await self.redis_client.setex(f"viper:market_data:{symbol}:compressed", 60, data_bytes)
                else:
                    await self.redis_client.setex(f"viper:market_data:{symbol}", 60, json.dumps(data))
                    
        except Exception as e:
            logger.error(f"# X Error caching market data: {e}")
    
    async def connect_exchange_websocket(self, exchange: str, symbols: List[str]) -> bool:
        """Connect to exchange websocket with optimization"""
        try:
            if exchange == 'bitget':
                return await self.connect_bitget_websocket(symbols)
            else:
                logger.error(f"# X Unsupported exchange: {exchange}")
                return False
                
        except Exception as e:
            logger.error(f"# X Error connecting to {exchange} websocket: {e}")
            return False
    
    async def connect_bitget_websocket(self, symbols: List[str]) -> bool:
        """Connect to Bitget websocket with enhanced features"""
        try:
            url = "wss://ws.bitget.com/mix/v1/stream"
            
            # Create connection pool for load balancing
            pool_id = f"bitget_{len(self.connection_pools)}"
            self.connection_pools[pool_id] = []
            
            # Create multiple connections for high throughput
            connections_per_pool = min(self.max_connections, len(symbols))
            symbols_per_connection = len(symbols) // connections_per_pool or 1
            
            for i in range(connections_per_pool):
                start_idx = i * symbols_per_connection
                end_idx = start_idx + symbols_per_connection if i < connections_per_pool - 1 else len(symbols)
                connection_symbols = symbols[start_idx:end_idx]
                
                connection_id = f"{pool_id}_conn_{i}"
                connection = await self.create_websocket_connection(
                    connection_id, url, connection_symbols, 'bitget'
                )
                
                if connection:
                    self.connection_pools[pool_id].append(connection)
                    self.connections[connection_id] = connection
                    
            logger.info(f"# Check Created {len(self.connection_pools[pool_id])} Bitget connections")
            return len(self.connection_pools[pool_id]) > 0
            
        except Exception as e:
            logger.error(f"# X Error connecting to Bitget websocket: {e}")
            return False
    
    async def create_websocket_connection(self, connection_id: str, url: str, 
                                        symbols: List[str], exchange: str):
        """Create individual websocket connection with reconnection logic"""
        try:
            connection_info = {
                'id': connection_id,
                'url': url,
                'symbols': symbols,
                'exchange': exchange,
                'websocket': None,
                'reconnect_count': 0,
                'last_message_time': time.time()
            }
            
            # Start connection task
            task = asyncio.create_task(
                self.maintain_websocket_connection(connection_info)
            )
            
            connection_info['task'] = task
            self.stats['connections_active'] += 1
            
            return connection_info
            
        except Exception as e:
            logger.error(f"# X Error creating websocket connection {connection_id}: {e}")
            return None
    
    async def maintain_websocket_connection(self, connection_info: Dict):
        """Maintain websocket connection with automatic reconnection"""
        connection_id = connection_info['id']
        url = connection_info['url']
        symbols = connection_info['symbols']
        exchange = connection_info['exchange']
        
        while self.is_running:
            try:
                logger.info(f"# Net Connecting to {exchange} websocket: {connection_id}")
                
                # Connect with compression and performance settings
                async with websockets.connect(
                    url,
                    compression="deflate" if self.compression_enabled else None,
                    max_size=self.message_buffer_size,
                    ping_interval=self.heartbeat_interval,
                    ping_timeout=10,
                    close_timeout=10
                ) as websocket:
                    
                    connection_info['websocket'] = websocket
                    connection_info['reconnect_count'] = 0
                    
                    # Subscribe to symbols
                    await self.subscribe_to_symbols(websocket, symbols, exchange)
                    
                    # Message receiving loop
                    async for message in websocket:
                        try:
                            connection_info['last_message_time'] = time.time()
                            self.stats['messages_received'] += 1
                            
                            # Parse message
                            data = json.loads(message)
                            
                            # Route message to appropriate queue for processing
                            if 'data' in data and len(data['data']) > 0:
                                symbol = self.extract_symbol_from_message(data, exchange)
                                if symbol and symbol in symbols:
                                    try:
                                        self.message_queues[symbol].put_nowait(data)
                                    except queue.Full:
                                        # Drop oldest message if queue is full
                                        try:
                                            self.message_queues[symbol].get_nowait()
                                            self.message_queues[symbol].put_nowait(data)
                                        except queue.Empty:
                                            pass
                            
                        except json.JSONDecodeError as e:
                            logger.warning(f"# Warning JSON decode error: {e}")
                        except Exception as e:
                            logger.error(f"# X Error processing websocket message: {e}")
                            self.stats['errors'] += 1
                            
            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"# Warning Websocket connection closed: {connection_id}")
                await self.handle_reconnection(connection_info)
            except Exception as e:
                logger.error(f"# X Websocket connection error for {connection_id}: {e}")
                await self.handle_reconnection(connection_info)
    
    async def handle_reconnection(self, connection_info: Dict):
        """Handle websocket reconnection with exponential backoff"""
        try:
            connection_info['reconnect_count'] += 1
            self.stats['reconnections'] += 1
            
            # Exponential backoff
            delay = min(
                self.reconnect_delay * (2 ** connection_info['reconnect_count']),
                self.max_reconnect_delay
            )
            
            logger.info(f"# Net Reconnecting {connection_info['id']} in {delay:.1f}s (attempt {connection_info['reconnect_count']})")
            await asyncio.sleep(delay)
            
        except Exception as e:
            logger.error(f"# X Error handling reconnection: {e}")
    
    async def subscribe_to_symbols(self, websocket, symbols: List[str], exchange: str):
        """Subscribe to trading symbols on websocket"""
        try:
            if exchange == 'bitget':
                # Subscribe to ticker updates
                for symbol in symbols:
                    subscribe_msg = {
                        "op": "subscribe",
                        "args": [f"ticker.{symbol}"]
                    }
                    await websocket.send(json.dumps(subscribe_msg))
                    await asyncio.sleep(0.1)  # Rate limiting
                
                logger.info(f"# Check Subscribed to {len(symbols)} symbols on {exchange}")
                
        except Exception as e:
            logger.error(f"# X Error subscribing to symbols: {e}")
    
    def extract_symbol_from_message(self, data: Dict, exchange: str) -> Optional[str]:
        """Extract symbol from websocket message"""
        try:
            if exchange == 'bitget':
                if 'arg' in data:
                    arg = data['arg']
                    if 'instId' in arg:
                        return arg['instId']
                    elif isinstance(arg, str) and 'ticker.' in arg:
                        return arg.split('.')[-1]
                        
                if 'data' in data and len(data['data']) > 0:
                    first_item = data['data'][0]
                    if 'instId' in first_item:
                        return first_item['instId']
            
            return None
            
        except Exception as e:
            logger.error(f"# X Error extracting symbol: {e}")
            return None
    
    def add_event_handler(self, event_type: str, handler: Callable):
        """Add event handler for websocket events"""
        self.event_handlers[event_type].append(handler)
    
    def trigger_event_handlers(self, event_type: str, *args):
        """Trigger event handlers"""
        try:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(*args)
                except Exception as e:
                    logger.error(f"# X Error in event handler: {e}")
        except Exception as e:
            logger.error(f"# X Error triggering event handlers: {e}")
    
    def get_technical_indicators(self, symbol: str, lookback: int = 50) -> Dict[str, np.ndarray]:
        """Get technical indicators for a symbol"""
        return self.data_processor.calculate_technical_indicators(symbol, lookback)
    
    def get_market_data_history(self, symbol: str, lookback: int = 100) -> np.ndarray:
        """Get market data history for a symbol"""
        return self.data_processor.get_vectorized_data(symbol, lookback)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        try:
            current_time = time.time()
            uptime = current_time - self.stats['uptime_start']
            
            processor_stats = self.data_processor.get_performance_stats()
            
            combined_stats = {
                **self.stats,
                'uptime_seconds': uptime,
                'uptime_minutes': uptime / 60,
                'processor_stats': processor_stats,
                'active_connections': len(self.connections),
                'connection_pools': len(self.connection_pools),
                'message_queues': {symbol: q.qsize() for symbol, q in self.message_queues.items()},
                'processing_threads': len([t for t in self.processing_threads if t.is_alive()])
            }
            
            return combined_stats
            
        except Exception as e:
            logger.error(f"# X Error getting performance stats: {e}")
            return self.stats
    
    async def shutdown(self):
        """Shutdown the websocket manager"""
        try:
            logger.info("# Stop Shutting down Enhanced Websocket Manager...")
            self.is_running = False
            
            # Close all websocket connections
            for connection_id, connection_info in self.connections.items():
                if 'task' in connection_info:
                    connection_info['task'].cancel()
                if 'websocket' in connection_info and connection_info['websocket']:
                    await connection_info['websocket'].close()
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            # Wait for processing threads to finish
            for thread in self.processing_threads:
                thread.join(timeout=5)
            
            logger.info("# Check Enhanced Websocket Manager shutdown complete")
            
        except Exception as e:
            logger.error(f"# X Shutdown error: {e}")

# Example usage and testing
async def main():
    """Example usage of Enhanced Websocket Manager"""
    manager = EnhancedWebsocketManager()
    
    try:
        # Initialize
        if not await manager.initialize():
            print("Failed to initialize websocket manager")
            return
        
        # Example event handler
        def on_market_data(symbol: str, data: MarketData):
            print(f"Received data for {symbol}: ${data.price:.4f}")
        
        manager.add_event_handler('market_data', on_market_data)
        
        # Connect to exchanges
        symbols = ['BTCUSDT_UMCBL', 'ETHUSDT_UMCBL', 'BNBUSDT_UMCBL']
        success = await manager.connect_exchange_websocket('bitget', symbols)
        
        if success:
            print("✅ Websocket connections established")
            
            # Run for demo period
            await asyncio.sleep(30)
            
            # Get performance stats
            stats = manager.get_performance_stats()
            print(f"📊 Performance Stats:")
            print(f"   Messages received: {stats['messages_received']}")
            print(f"   Messages processed: {stats['messages_processed']}")
            print(f"   Throughput: {stats['throughput_msg_per_sec']:.2f} msg/sec")
            print(f"   Active connections: {stats['active_connections']}")
            
            # Get technical indicators
            for symbol in symbols:
                indicators = manager.get_technical_indicators(symbol)
                if indicators:
                    print(f"📈 {symbol} indicators: {list(indicators.keys())}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())