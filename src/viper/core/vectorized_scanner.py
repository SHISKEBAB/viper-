#!/usr/bin/env python3
"""
# ULTRA-FAST VECTORIZED SCANNING ENGINE
WebSocket-only scanning with NumPy vectorization for maximum speed

Features:
- Pure WebSocket data (no REST fallbacks)
- Vectorized batch scoring with NumPy
- Parallel processing of multiple symbols
- Real-time opportunity detection
- Memory-efficient vectorized operations
- Ultra-low latency signal detection
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque
import threading

from websocket_only_streamer import WebSocketOnlyStreamer, MarketData, WebSocketConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradingOpportunity:
    """Trading opportunity with vectorized scoring"""
    symbol: str
    side: str  # 'buy' or 'sell'
    score: float
    price: float
    volume: float
    change_24h: float
    volatility: float
    momentum_score: float
    volume_score: float
    technical_score: float
    risk_score: float
    timestamp: float
    confidence: float = 0.0

    def to_array(self) -> np.ndarray:
        """Convert to NumPy array for vectorized operations"""
        return np.array([
            self.score, self.price, self.volume, self.change_24h,
            self.volatility, self.momentum_score, self.volume_score,
            self.technical_score, self.risk_score, self.confidence
        ])

@dataclass
class ScanningConfig:
    """Configuration for vectorized scanning"""
    min_score_threshold: float = 65.0
    max_positions: int = 10
    scan_interval: float = 0.1  # 100ms scanning interval
    batch_size: int = 100
    min_volume_threshold: float = 1000000.0
    max_volatility_threshold: float = 20.0
    momentum_weight: float = 0.35
    volume_weight: float = 0.25
    technical_weight: float = 0.20
    volatility_weight: float = 0.10
    risk_weight: float = 0.10

class VectorizedScanningEngine:
    """Ultra-fast WebSocket-only scanning with vectorized processing"""
    
    def __init__(self, symbols: List[str], config: ScanningConfig):
        self.symbols = symbols
        self.config = config
        self.running = False
        
        # WebSocket streamer
        ws_config = WebSocketConfig(
            url="wss://ws.bitget.com/mix/v1/stream",
            batch_size=config.batch_size,
            max_reconnect_attempts=20
        )
        self.streamer = WebSocketOnlyStreamer(ws_config, symbols)
        
        # Vectorized data structures
        self.symbol_data: Dict[str, np.ndarray] = {}
        self.historical_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.active_positions: Set[str] = set()
        self.opportunity_callbacks: List[callable] = []
        
        # Performance metrics
        self.scans_completed = 0
        self.opportunities_found = 0
        self.scanning_times = deque(maxlen=1000)
        self.last_scan_time = 0.0
        
        # Vectorized scoring arrays
        self._precompute_scoring_arrays()
        
        logger.info(f"🚀 Vectorized Scanner initialized for {len(symbols)} symbols")

    def _precompute_scoring_arrays(self):
        """Precompute scoring arrays for ultra-fast vectorized calculations"""
        # Volume thresholds for vectorized scoring
        self.volume_thresholds = np.array([
            100000, 500000, 1000000, 5000000, 10000000, 50000000, 100000000
        ])
        self.volume_scores = np.array([0, 5, 15, 25, 35, 45, 50])
        
        # Price change thresholds
        self.change_thresholds = np.array([0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0])
        self.momentum_scores = np.array([0, 10, 20, 30, 40, 50, 60])
        
        # Volatility thresholds
        self.volatility_thresholds = np.array([0.5, 1.0, 2.0, 4.0, 6.0, 10.0, 15.0])
        self.volatility_scores = np.array([5, 10, 15, 20, 15, 10, 5])  # Peak at moderate volatility
        
        logger.info("📊 Precomputed vectorized scoring arrays")

    async def start_scanning(self):
        """Start the ultra-fast scanning engine"""
        self.running = True
        
        # Start WebSocket streamer
        await self.streamer.start()
        
        # Register data callback
        self.streamer.register_data_callback(self._update_symbol_data)
        
        # Wait for connections to establish
        logger.info("⏳ Waiting for WebSocket connections...")
        while not self.streamer.is_ready() and self.running:
            await asyncio.sleep(1)
        
        logger.info("✅ WebSocket connections ready - starting scanning")
        
        # Start scanning loop
        scan_task = asyncio.create_task(self._ultra_fast_scanning_loop())
        
        return scan_task

    async def stop_scanning(self):
        """Stop the scanning engine"""
        self.running = False
        await self.streamer.stop()
        logger.info("🛑 Scanning engine stopped")

    async def _update_symbol_data(self, symbol: str, data: MarketData):
        """Update symbol data from WebSocket stream"""
        try:
            # Store latest data as NumPy array
            self.symbol_data[symbol] = data.to_array()
            
            # Add to historical data
            self.historical_data[symbol].append(data)
            
        except Exception as e:
            logger.error(f"❌ Error updating data for {symbol}: {e}")

    async def _ultra_fast_scanning_loop(self):
        """Ultra-fast scanning loop with vectorized processing"""
        logger.info("🔥 Starting ultra-fast scanning loop (WebSocket-only)")
        
        while self.running:
            scan_start = time.time()
            
            try:
                # Get all available data for vectorized processing
                opportunities = await self._vectorized_scan_all_symbols()
                
                # Process opportunities
                if opportunities:
                    await self._process_opportunities(opportunities)
                
                # Update performance metrics
                scan_time = time.time() - scan_start
                self.scanning_times.append(scan_time)
                self.scans_completed += 1
                self.last_scan_time = scan_time
                
                # Log performance every 100 scans
                if self.scans_completed % 100 == 0:
                    avg_scan_time = np.mean(list(self.scanning_times))
                    scans_per_second = 1.0 / avg_scan_time if avg_scan_time > 0 else 0
                    
                    logger.info(f"⚡ Performance: {scans_per_second:.1f} scans/s, "
                              f"avg {avg_scan_time*1000:.1f}ms, "
                              f"{self.opportunities_found} opportunities found")
                
                # Ultra-fast scanning interval
                await asyncio.sleep(self.config.scan_interval)
                
            except Exception as e:
                logger.error(f"❌ Scanning loop error: {e}")
                await asyncio.sleep(1)

    async def _vectorized_scan_all_symbols(self) -> List[TradingOpportunity]:
        """Vectorized scanning of all symbols simultaneously"""
        try:
            # Get symbols that have data and are not in active positions
            available_symbols = [
                symbol for symbol in self.symbol_data.keys()
                if symbol not in self.active_positions and len(self.historical_data[symbol]) >= 5
            ]
            
            if not available_symbols:
                return []
            
            # Batch vectorized scoring
            opportunities = await self._batch_vectorized_scoring(available_symbols)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ Vectorized scanning error: {e}")
            return []

    async def _batch_vectorized_scoring(self, symbols: List[str]) -> List[TradingOpportunity]:
        """Ultra-fast batch scoring using vectorized operations"""
        opportunities = []
        
        try:
            # Prepare data arrays for all symbols
            symbol_count = len(symbols)
            
            if symbol_count == 0:
                return []
            
            # Create vectorized data matrices
            prices = np.zeros(symbol_count)
            volumes = np.zeros(symbol_count)
            changes_24h = np.zeros(symbol_count)
            high_24h = np.zeros(symbol_count)
            low_24h = np.zeros(symbol_count)
            
            # Fill arrays with current data
            for i, symbol in enumerate(symbols):
                data_array = self.symbol_data[symbol]
                prices[i] = data_array[0]  # price
                volumes[i] = data_array[1]  # volume
                changes_24h[i] = data_array[2]  # change_24h
                high_24h[i] = data_array[3]  # high_24h
                low_24h[i] = data_array[4]  # low_24h
            
            # Vectorized score calculations
            momentum_scores = self._vectorized_momentum_score(changes_24h)
            volume_scores = self._vectorized_volume_score(volumes)
            volatility_scores = self._vectorized_volatility_score(prices, high_24h, low_24h)
            technical_scores = await self._vectorized_technical_score(symbols)
            risk_scores = self._vectorized_risk_score(changes_24h, volumes)
            
            # Combined scores using vectorized weights
            total_scores = (
                momentum_scores * self.config.momentum_weight +
                volume_scores * self.config.volume_weight +
                volatility_scores * self.config.volatility_weight +
                technical_scores * self.config.technical_weight +
                risk_scores * self.config.risk_weight
            )
            
            # Find high-scoring opportunities
            high_score_indices = np.where(total_scores >= self.config.min_score_threshold)[0]
            
            # Create opportunity objects for high scores
            for idx in high_score_indices:
                symbol = symbols[idx]
                score = total_scores[idx]
                
                # Determine side based on momentum and trend
                side = 'buy' if changes_24h[idx] > 0 and momentum_scores[idx] > 20 else 'sell'
                
                # Calculate volatility
                volatility = ((high_24h[idx] - low_24h[idx]) / low_24h[idx]) * 100 if low_24h[idx] > 0 else 0
                
                # Calculate confidence
                confidence = min(score / 100.0, 1.0)
                
                opportunity = TradingOpportunity(
                    symbol=symbol,
                    side=side,
                    score=score,
                    price=prices[idx],
                    volume=volumes[idx],
                    change_24h=changes_24h[idx],
                    volatility=volatility,
                    momentum_score=momentum_scores[idx],
                    volume_score=volume_scores[idx],
                    technical_score=technical_scores[idx],
                    risk_score=risk_scores[idx],
                    timestamp=time.time(),
                    confidence=confidence
                )
                
                opportunities.append(opportunity)
            
            # Sort by score (highest first)
            opportunities.sort(key=lambda x: x.score, reverse=True)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ Batch scoring error: {e}")
            return []

    def _vectorized_momentum_score(self, changes_24h: np.ndarray) -> np.ndarray:
        """Vectorized momentum scoring"""
        abs_changes = np.abs(changes_24h)
        return np.interp(abs_changes, self.change_thresholds, self.momentum_scores)

    def _vectorized_volume_score(self, volumes: np.ndarray) -> np.ndarray:
        """Vectorized volume scoring"""
        return np.interp(volumes, self.volume_thresholds, self.volume_scores)

    def _vectorized_volatility_score(self, prices: np.ndarray, highs: np.ndarray, lows: np.ndarray) -> np.ndarray:
        """Vectorized volatility scoring"""
        # Calculate volatility percentage
        volatilities = np.where(lows > 0, ((highs - lows) / lows) * 100, 0)
        return np.interp(volatilities, self.volatility_thresholds, self.volatility_scores)

    async def _vectorized_technical_score(self, symbols: List[str]) -> np.ndarray:
        """Vectorized technical analysis scoring"""
        scores = np.zeros(len(symbols))
        
        try:
            for i, symbol in enumerate(symbols):
                historical = list(self.historical_data[symbol])
                if len(historical) >= 10:
                    # Simple technical analysis using recent price movement
                    recent_prices = np.array([d.price for d in historical[-10:]])
                    
                    # Simple moving average trend
                    if len(recent_prices) >= 5:
                        ma_short = np.mean(recent_prices[-3:])
                        ma_long = np.mean(recent_prices[-5:])
                        
                        # Score based on trend direction
                        if ma_short > ma_long:
                            scores[i] = 15  # Uptrend
                        elif ma_short < ma_long:
                            scores[i] = 5   # Downtrend
                        else:
                            scores[i] = 10  # Neutral
                    else:
                        scores[i] = 10  # Default neutral score
                else:
                    scores[i] = 10  # Default neutral score
                    
        except Exception as e:
            logger.error(f"❌ Technical scoring error: {e}")
            scores.fill(10)  # Default scores on error
            
        return scores

    def _vectorized_risk_score(self, changes_24h: np.ndarray, volumes: np.ndarray) -> np.ndarray:
        """Vectorized risk scoring"""
        # Higher volume + moderate change = lower risk
        risk_scores = np.zeros(len(changes_24h))
        
        # Volume risk component
        volume_risk = np.where(volumes > self.config.min_volume_threshold, 10, -5)
        
        # Change risk component (extreme changes = higher risk)
        change_risk = np.where(np.abs(changes_24h) > 10, -5, 5)
        
        risk_scores = volume_risk + change_risk
        
        return np.clip(risk_scores, -10, 15)

    async def _process_opportunities(self, opportunities: List[TradingOpportunity]):
        """Process found opportunities"""
        if not opportunities:
            return
            
        self.opportunities_found += len(opportunities)
        
        # Log top opportunities
        top_opportunities = opportunities[:5]  # Top 5
        for opp in top_opportunities:
            logger.info(f"🎯 OPPORTUNITY: {opp.symbol} {opp.side.upper()} "
                       f"Score: {opp.score:.1f} Price: ${opp.price:.4f} "
                       f"Change: {opp.change_24h:+.2f}% Confidence: {opp.confidence:.2f}")
        
        # Call registered callbacks
        for callback in self.opportunity_callbacks:
            try:
                await callback(opportunities)
            except Exception as e:
                logger.error(f"❌ Opportunity callback error: {e}")

    def register_opportunity_callback(self, callback: callable):
        """Register callback for trading opportunities"""
        self.opportunity_callbacks.append(callback)

    def add_active_position(self, symbol: str):
        """Add symbol to active positions (prevents new positions)"""
        self.active_positions.add(symbol)
        logger.info(f"📍 Added active position: {symbol}")

    def remove_active_position(self, symbol: str):
        """Remove symbol from active positions"""
        self.active_positions.discard(symbol)
        logger.info(f"📍 Removed active position: {symbol}")

    def get_performance_metrics(self) -> Dict[str, float]:
        """Get scanning performance metrics"""
        avg_scan_time = np.mean(list(self.scanning_times)) if self.scanning_times else 0
        scans_per_second = 1.0 / avg_scan_time if avg_scan_time > 0 else 0
        
        return {
            'scans_completed': self.scans_completed,
            'opportunities_found': self.opportunities_found,
            'avg_scan_time_ms': avg_scan_time * 1000,
            'scans_per_second': scans_per_second,
            'symbols_count': len(self.symbols),
            'active_positions': len(self.active_positions),
            'websocket_connections': len(self.streamer.get_connection_status())
        }


# Example usage and test
async def test_vectorized_scanner():
    """Test the vectorized scanning engine"""
    symbols = [
        "BTC/USDT:USDT", "ETH/USDT:USDT", "ADA/USDT:USDT", "DOT/USDT:USDT", 
        "LINK/USDT:USDT", "UNI/USDT:USDT", "AAVE/USDT:USDT", "SUSHI/USDT:USDT"
    ]
    
    config = ScanningConfig(
        min_score_threshold=60.0,
        scan_interval=0.05,  # 50ms ultra-fast scanning
        batch_size=200
    )
    
    scanner = VectorizedScanningEngine(symbols, config)
    
    # Register opportunity callback
    async def opportunity_handler(opportunities: List[TradingOpportunity]):
        for opp in opportunities[:3]:  # Show top 3
            print(f"🔥 SIGNAL: {opp.symbol} {opp.side.upper()} - Score: {opp.score:.1f}")
    
    scanner.register_opportunity_callback(opportunity_handler)
    
    try:
        # Start scanning
        scan_task = await scanner.start_scanning()
        
        # Run for demonstration
        await asyncio.sleep(30)
        
        # Show performance metrics
        metrics = scanner.get_performance_metrics()
        print(f"\n📊 Performance Metrics: {metrics}")
        
    finally:
        await scanner.stop_scanning()


if __name__ == "__main__":
    asyncio.run(test_vectorized_scanner())