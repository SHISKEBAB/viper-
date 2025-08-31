#!/usr/bin/env python3
"""
# PURE WEBSOCKET STREAMING ENGINE FOR VIPER
Ultra-fast WebSocket-only market data streaming with vectorized processing
NO REST API FALLBACKS - WebSocket only for maximum speed

Features:
- Pure WebSocket streaming (no REST fallbacks)
- Vectorized batch processing with NumPy
- Connection pooling and auto-reconnection
- Real-time data caching with ultra-low latency
- Concurrent symbol streaming
- Memory-efficient data structures
"""

import asyncio
import logging
import websockets
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import ssl
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"

@dataclass
class WebSocketConfig:
    """Configuration for WebSocket connections"""
    url: str
    max_reconnect_attempts: int = 50
    reconnect_delay: float = 1.0
    ping_interval: int = 20
    ping_timeout: int = 10
    max_queue_size: int = 10000
    batch_size: int = 100
    compression: Optional[str] = None

@dataclass
class MarketData:
    """Vectorized market data structure"""
    symbol: str
    price: float
    volume: float
    change_24h: float
    high_24h: float
    low_24h: float
    bid: float
    ask: float
    timestamp: float
    
    def to_array(self) -> np.ndarray:
        """Convert to NumPy array for vectorized operations"""
        return np.array([
            self.price, self.volume, self.change_24h,
            self.high_24h, self.low_24h, self.bid, self.ask, self.timestamp
        ])

class WebSocketOnlyStreamer:
    """Pure WebSocket streaming engine with vectorized processing"""
    
    def __init__(self, config: WebSocketConfig, symbols: List[str]):
        self.config = config
        self.symbols = set(symbols)
        self.connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.connection_status: Dict[str, ConnectionStatus] = {}
        self.data_buffers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.latest_data: Dict[str, MarketData] = {}
        self.vectorized_data: Dict[str, np.ndarray] = {}
        
        # Performance metrics
        self.message_count = 0
        self.last_message_time = time.time()
        self.messages_per_second = 0.0
        self.data_callbacks: List[Callable] = []
        
        # Threading and async
        self.loop = None
        self.running = False
        self.tasks: Set[asyncio.Task] = set()
        
        # Vectorized processing
        self.batch_processor = VectorizedBatchProcessor()
        
        logger.info(f"🚀 WebSocket-Only Streamer initialized for {len(symbols)} symbols")

    async def start(self):
        """Start WebSocket streaming for all symbols"""
        self.running = True
        self.loop = asyncio.get_event_loop()
        
        logger.info("🔗 Starting WebSocket-only streaming (NO REST FALLBACKS)")
        
        # Create connection tasks for all symbols
        for symbol in self.symbols:
            task = asyncio.create_task(self._connect_symbol(symbol))
            self.tasks.add(task)
            
        # Start performance monitoring
        monitor_task = asyncio.create_task(self._performance_monitor())
        self.tasks.add(monitor_task)
        
        # Start vectorized batch processing
        batch_task = asyncio.create_task(self._batch_processing_loop())
        self.tasks.add(batch_task)
        
        logger.info(f"✅ Started streaming for {len(self.symbols)} symbols")

    async def stop(self):
        """Stop all WebSocket connections"""
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
            
        # Close all connections
        for symbol, ws in self.connections.items():
            try:
                await ws.close()
                logger.info(f"🔌 Closed WebSocket for {symbol}")
            except Exception as e:
                logger.error(f"❌ Error closing WebSocket for {symbol}: {e}")
                
        logger.info("🛑 WebSocket streaming stopped")

    async def _connect_symbol(self, symbol: str):
        """Connect WebSocket for a specific symbol with auto-reconnection"""
        attempt = 0
        while self.running and attempt < self.config.max_reconnect_attempts:
            try:
                self.connection_status[symbol] = ConnectionStatus.CONNECTING
                
                # Build WebSocket URL for the symbol
                ws_url = self._build_websocket_url(symbol)
                
                logger.info(f"📡 Connecting to WebSocket for {symbol}: {ws_url}")
                
                # Connect with SSL context
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                async with websockets.connect(
                    ws_url,
                    ping_interval=self.config.ping_interval,
                    ping_timeout=self.config.ping_timeout,
                    ssl=ssl_context,
                    compression=self.config.compression
                ) as websocket:
                    self.connections[symbol] = websocket
                    self.connection_status[symbol] = ConnectionStatus.CONNECTED
                    
                    logger.info(f"✅ WebSocket connected for {symbol}")
                    
                    # Subscribe to ticker updates
                    await self._subscribe_to_ticker(websocket, symbol)
                    
                    # Listen for messages
                    await self._listen_for_messages(websocket, symbol)
                    
            except Exception as e:
                self.connection_status[symbol] = ConnectionStatus.ERROR
                logger.error(f"❌ WebSocket error for {symbol}: {e}")
                attempt += 1
                
                if attempt < self.config.max_reconnect_attempts:
                    self.connection_status[symbol] = ConnectionStatus.RECONNECTING
                    logger.info(f"🔄 Reconnecting {symbol} in {self.config.reconnect_delay}s (attempt {attempt})")
                    await asyncio.sleep(self.config.reconnect_delay)
                else:
                    logger.error(f"💀 Max reconnection attempts reached for {symbol}")
                    
        self.connection_status[symbol] = ConnectionStatus.DISCONNECTED

    def _build_websocket_url(self, symbol: str) -> str:
        """Build WebSocket URL for symbol (Bitget format)"""
        # Convert symbol format (e.g., BTC/USDT:USDT -> BTCUSDT)
        clean_symbol = symbol.replace('/', '').replace(':USDT', '').upper()
        return f"wss://ws.bitget.com/mix/v1/stream"

    async def _subscribe_to_ticker(self, websocket, symbol: str):
        """Subscribe to ticker updates for symbol"""
        # Convert symbol for Bitget API
        clean_symbol = symbol.replace('/', '').replace(':USDT', '').upper() + "USDT_UMCBL"
        
        subscription = {
            "op": "subscribe",
            "args": [
                {
                    "instType": "UMCBL",
                    "channel": "ticker",
                    "instId": clean_symbol
                }
            ]
        }
        
        await websocket.send(json.dumps(subscription))
        logger.debug(f"📤 Subscribed to ticker for {symbol}")

    async def _listen_for_messages(self, websocket, symbol: str):
        """Listen for WebSocket messages for a symbol"""
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._process_message(symbol, data)
                    
                    # Update performance metrics
                    self.message_count += 1
                    self.last_message_time = time.time()
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ Invalid JSON from {symbol}: {e}")
                except Exception as e:
                    logger.error(f"❌ Error processing message for {symbol}: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"🔌 WebSocket connection closed for {symbol}")
        except Exception as e:
            logger.error(f"❌ Error listening to {symbol}: {e}")

    async def _process_message(self, symbol: str, data: Dict[str, Any]):
        """Process incoming WebSocket message and update data structures"""
        try:
            # Parse Bitget ticker format
            if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
                ticker_data = data['data'][0]
                
                # Extract market data
                market_data = MarketData(
                    symbol=symbol,
                    price=float(ticker_data.get('last', 0)),
                    volume=float(ticker_data.get('baseVol', 0)),
                    change_24h=float(ticker_data.get('chgUtc', 0)),
                    high_24h=float(ticker_data.get('high24h', 0)),
                    low_24h=float(ticker_data.get('low24h', 0)),
                    bid=float(ticker_data.get('bidPr', 0)),
                    ask=float(ticker_data.get('askPr', 0)),
                    timestamp=time.time()
                )
                
                # Update latest data
                self.latest_data[symbol] = market_data
                
                # Add to buffer for batch processing
                self.data_buffers[symbol].append(market_data)
                
                # Update vectorized data
                self.vectorized_data[symbol] = market_data.to_array()
                
                # Call registered callbacks
                for callback in self.data_callbacks:
                    try:
                        await callback(symbol, market_data)
                    except Exception as e:
                        logger.error(f"❌ Callback error: {e}")
                        
                logger.debug(f"📊 Updated data for {symbol}: ${market_data.price}")
                
        except Exception as e:
            logger.error(f"❌ Error processing message for {symbol}: {e}")

    async def _performance_monitor(self):
        """Monitor streaming performance"""
        while self.running:
            try:
                current_time = time.time()
                time_diff = current_time - self.last_message_time
                
                if time_diff > 0:
                    self.messages_per_second = self.message_count / time_diff
                
                # Log performance stats every 30 seconds
                await asyncio.sleep(30)
                
                connected_count = sum(1 for status in self.connection_status.values() 
                                    if status == ConnectionStatus.CONNECTED)
                
                logger.info(f"📈 Performance: {self.messages_per_second:.1f} msg/s, "
                          f"{connected_count}/{len(self.symbols)} connected, "
                          f"{len(self.latest_data)} symbols with data")
                
            except Exception as e:
                logger.error(f"❌ Performance monitor error: {e}")
                await asyncio.sleep(30)

    async def _batch_processing_loop(self):
        """Process data in vectorized batches"""
        while self.running:
            try:
                # Collect data from all buffers
                batch_data = {}
                for symbol, buffer in self.data_buffers.items():
                    if len(buffer) >= self.config.batch_size:
                        batch_data[symbol] = list(buffer)
                        buffer.clear()
                
                if batch_data:
                    # Process batch with vectorized operations
                    await self.batch_processor.process_batch(batch_data)
                
                await asyncio.sleep(0.1)  # Process batches every 100ms
                
            except Exception as e:
                logger.error(f"❌ Batch processing error: {e}")
                await asyncio.sleep(1)

    def register_data_callback(self, callback: Callable):
        """Register callback for real-time data updates"""
        self.data_callbacks.append(callback)

    def get_latest_data(self, symbol: str) -> Optional[MarketData]:
        """Get latest market data for symbol (WebSocket-only)"""
        return self.latest_data.get(symbol)

    def get_vectorized_data(self, symbols: List[str] = None) -> Dict[str, np.ndarray]:
        """Get vectorized data for batch processing"""
        if symbols is None:
            return self.vectorized_data
        return {symbol: self.vectorized_data[symbol] for symbol in symbols 
                if symbol in self.vectorized_data}

    def get_connection_status(self) -> Dict[str, ConnectionStatus]:
        """Get connection status for all symbols"""
        return self.connection_status.copy()

    def is_ready(self) -> bool:
        """Check if WebSocket streaming is ready"""
        connected_count = sum(1 for status in self.connection_status.values() 
                            if status == ConnectionStatus.CONNECTED)
        return connected_count >= len(self.symbols) * 0.8  # 80% connected = ready


class VectorizedBatchProcessor:
    """High-performance vectorized batch processing"""
    
    def __init__(self):
        self.processed_batches = 0
        self.total_processing_time = 0.0
        
    async def process_batch(self, batch_data: Dict[str, List[MarketData]]):
        """Process batch of market data with vectorized operations"""
        start_time = time.time()
        
        try:
            # Convert all data to NumPy arrays for vectorized processing
            symbol_arrays = {}
            for symbol, data_list in batch_data.items():
                if data_list:
                    # Stack all data points into a 2D array
                    arrays = [data.to_array() for data in data_list]
                    symbol_arrays[symbol] = np.vstack(arrays)
            
            if symbol_arrays:
                # Perform vectorized calculations
                await self._vectorized_analysis(symbol_arrays)
                
            self.processed_batches += 1
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            
            logger.debug(f"⚡ Processed batch of {len(batch_data)} symbols in {processing_time:.3f}s")
            
        except Exception as e:
            logger.error(f"❌ Batch processing error: {e}")

    async def _vectorized_analysis(self, symbol_arrays: Dict[str, np.ndarray]):
        """Perform vectorized analysis on market data"""
        try:
            for symbol, data_array in symbol_arrays.items():
                # Vectorized calculations
                prices = data_array[:, 0]  # Price column
                volumes = data_array[:, 1]  # Volume column
                changes = data_array[:, 2]  # Change column
                
                # Calculate moving averages, volatility, etc. using NumPy
                if len(prices) > 1:
                    price_mean = np.mean(prices)
                    price_std = np.std(prices)
                    volume_mean = np.mean(volumes)
                    
                    # Store calculated metrics (could be used for scoring)
                    logger.debug(f"📊 {symbol}: Price μ={price_mean:.2f}, σ={price_std:.2f}, Vol μ={volume_mean:.0f}")
                    
        except Exception as e:
            logger.error(f"❌ Vectorized analysis error: {e}")


# Example usage and test function
async def test_websocket_streamer():
    """Test the WebSocket-only streamer"""
    symbols = ["BTC/USDT:USDT", "ETH/USDT:USDT", "ADA/USDT:USDT"]
    
    config = WebSocketConfig(
        url="wss://ws.bitget.com/mix/v1/stream",
        batch_size=50,
        max_reconnect_attempts=10
    )
    
    streamer = WebSocketOnlyStreamer(config, symbols)
    
    # Register a callback to see data updates
    async def data_callback(symbol: str, data: MarketData):
        logger.info(f"🔥 LIVE DATA: {symbol} = ${data.price:.4f} (Change: {data.change_24h:+.2f}%)")
    
    streamer.register_data_callback(data_callback)
    
    try:
        await streamer.start()
        
        # Wait for connections to establish
        await asyncio.sleep(10)
        
        # Show status
        status = streamer.get_connection_status()
        logger.info(f"📊 Connection Status: {status}")
        
        # Run for demonstration
        await asyncio.sleep(60)
        
    finally:
        await streamer.stop()


if __name__ == "__main__":
    asyncio.run(test_websocket_streamer())