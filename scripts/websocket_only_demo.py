#!/usr/bin/env python3
"""
# WEBSOCKET-ONLY VIPER DEMO
Quick demonstration of the WebSocket-only system with vectorized scanning

This script demonstrates:
- Pure WebSocket streaming (no REST fallbacks)
- Vectorized batch processing
- Ultra-fast scanning with NumPy
- Real-time opportunity detection
"""

import asyncio
import logging
import time
import numpy as np
from datetime import datetime
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebSocketOnlyDemo:
    """Demonstration of WebSocket-only trading system"""
    
    def __init__(self):
        self.symbols = [
            "BTC/USDT:USDT", "ETH/USDT:USDT", "ADA/USDT:USDT", "DOT/USDT:USDT",
            "LINK/USDT:USDT", "UNI/USDT:USDT", "AAVE/USDT:USDT", "SUSHI/USDT:USDT"
        ]
        
        # Simulated WebSocket data
        self.websocket_data = {}
        self.running = False
        
        # Performance metrics
        self.scans_completed = 0
        self.opportunities_found = 0
        self.scan_times = []
        
        # Vectorized scoring weights
        self.scoring_weights = np.array([0.35, 0.25, 0.20, 0.15, 0.05])  # [momentum, volume, volatility, technical, risk]

    async def start_demo(self):
        """Start the WebSocket-only demo"""
        self.running = True
        
        logger.info("🚀 STARTING WEBSOCKET-ONLY VIPER DEMO")
        logger.info("=" * 60)
        logger.info("⚡ NO REST API FALLBACKS - Pure WebSocket streaming")
        logger.info("📊 Vectorized batch processing with NumPy")
        logger.info("🎯 Ultra-fast scanning for trading opportunities")
        logger.info("")
        
        # Start WebSocket simulation
        websocket_task = asyncio.create_task(self._simulate_websocket_stream())
        
        # Start vectorized scanning
        scanning_task = asyncio.create_task(self._ultra_fast_scanning_loop())
        
        # Start performance monitoring
        monitor_task = asyncio.create_task(self._performance_monitor())
        
        # Run demo
        try:
            await asyncio.gather(websocket_task, scanning_task, monitor_task)
        except KeyboardInterrupt:
            logger.info("🛑 Demo stopped by user")
        finally:
            self.running = False

    async def _simulate_websocket_stream(self):
        """Simulate real-time WebSocket data stream"""
        logger.info("📡 Starting WebSocket data simulation...")
        
        while self.running:
            try:
                # Simulate real-time market data updates
                for symbol in self.symbols:
                    # Generate realistic market data
                    base_price = random.uniform(0.1, 100.0)
                    self.websocket_data[symbol] = {
                        'price': base_price + random.uniform(-0.1, 0.1),
                        'volume': random.uniform(1000000, 50000000),
                        'change_24h': random.uniform(-5.0, 5.0),
                        'high_24h': base_price + random.uniform(0.05, 0.2),
                        'low_24h': base_price - random.uniform(0.05, 0.2),
                        'bid': base_price - random.uniform(0.001, 0.01),
                        'ask': base_price + random.uniform(0.001, 0.01),
                        'timestamp': time.time(),
                        'websocket_source': True  # Mark as WebSocket data
                    }
                
                # Simulate WebSocket update frequency (very fast)
                await asyncio.sleep(0.1)  # 100ms updates
                
            except Exception as e:
                logger.error(f"❌ WebSocket simulation error: {e}")
                await asyncio.sleep(1)

    async def _ultra_fast_scanning_loop(self):
        """Ultra-fast vectorized scanning loop"""
        logger.info("⚡ Starting ultra-fast vectorized scanning...")
        
        await asyncio.sleep(2)  # Wait for some data
        
        while self.running:
            scan_start = time.time()
            
            try:
                # Get all available WebSocket data
                if len(self.websocket_data) < len(self.symbols):
                    await asyncio.sleep(0.01)
                    continue
                
                # Vectorized batch processing
                opportunities = await self._vectorized_batch_scan()
                
                if opportunities:
                    await self._process_opportunities(opportunities)
                
                # Update performance metrics
                scan_time = time.time() - scan_start
                self.scan_times.append(scan_time)
                self.scans_completed += 1
                
                # Ultra-fast scanning interval
                await asyncio.sleep(0.05)  # 50ms scanning interval = 20 scans/second
                
            except Exception as e:
                logger.error(f"❌ Scanning error: {e}")
                await asyncio.sleep(0.1)

    async def _vectorized_batch_scan(self):
        """Vectorized batch scanning using NumPy for maximum speed"""
        try:
            symbols_list = list(self.websocket_data.keys())
            num_symbols = len(symbols_list)
            
            if num_symbols == 0:
                return []
            
            # Create vectorized data arrays
            prices = np.zeros(num_symbols)
            volumes = np.zeros(num_symbols)
            changes_24h = np.zeros(num_symbols)
            volatilities = np.zeros(num_symbols)
            
            # Fill arrays with WebSocket data
            for i, symbol in enumerate(symbols_list):
                data = self.websocket_data[symbol]
                prices[i] = data['price']
                volumes[i] = data['volume']
                changes_24h[i] = data['change_24h']
                
                # Calculate volatility
                high = data['high_24h']
                low = data['low_24h']
                if low > 0:
                    volatilities[i] = ((high - low) / low) * 100
                else:
                    volatilities[i] = 0
            
            # Vectorized scoring calculations
            momentum_scores = self._vectorized_momentum_score(changes_24h)
            volume_scores = self._vectorized_volume_score(volumes)
            volatility_scores = self._vectorized_volatility_score(volatilities)
            technical_scores = self._vectorized_technical_score(changes_24h)
            risk_scores = self._vectorized_risk_score(volatilities, volumes)
            
            # Stack all scores for matrix operation
            score_matrix = np.vstack([
                momentum_scores, volume_scores, volatility_scores,
                technical_scores, risk_scores
            ])
            
            # Vectorized weighted combination
            total_scores = np.dot(self.scoring_weights, score_matrix)
            
            # Find high-scoring opportunities
            score_threshold = 65.0
            high_score_indices = np.where(total_scores >= score_threshold)[0]
            
            opportunities = []
            for idx in high_score_indices:
                symbol = symbols_list[idx]
                score = total_scores[idx]
                side = 'buy' if changes_24h[idx] > 0 else 'sell'
                
                opportunities.append({
                    'symbol': symbol,
                    'side': side,
                    'score': score,
                    'price': prices[idx],
                    'volume': volumes[idx],
                    'change_24h': changes_24h[idx],
                    'volatility': volatilities[idx],
                    'websocket_data': True
                })
            
            # Sort by score (highest first)
            opportunities.sort(key=lambda x: x['score'], reverse=True)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ Vectorized scanning error: {e}")
            return []

    def _vectorized_momentum_score(self, changes_24h):
        """Vectorized momentum scoring"""
        abs_changes = np.abs(changes_24h)
        return np.clip(abs_changes * 10, 0, 50)

    def _vectorized_volume_score(self, volumes):
        """Vectorized volume scoring"""
        # Logarithmic volume scoring
        log_volumes = np.log10(np.maximum(volumes, 1))
        return np.clip((log_volumes - 6) * 10, 0, 50)  # Scale from 1M volume

    def _vectorized_volatility_score(self, volatilities):
        """Vectorized volatility scoring (optimal range scoring)"""
        # Peak scoring around 2-5% volatility
        optimal_volatility = 3.5
        volatility_diff = np.abs(volatilities - optimal_volatility)
        return np.maximum(50 - volatility_diff * 5, 0)

    def _vectorized_technical_score(self, changes_24h):
        """Vectorized technical scoring"""
        # Simple momentum-based technical score
        return np.where(np.abs(changes_24h) > 1.0, 25, 10)

    def _vectorized_risk_score(self, volatilities, volumes):
        """Vectorized risk scoring"""
        # Lower risk for higher volume and moderate volatility
        volume_risk = np.where(volumes > 5000000, 10, 0)
        volatility_risk = np.where(volatilities > 10, -10, 5)
        return volume_risk + volatility_risk

    async def _process_opportunities(self, opportunities):
        """Process found trading opportunities"""
        self.opportunities_found += len(opportunities)
        
        # Log top opportunities
        for i, opp in enumerate(opportunities[:3]):  # Show top 3
            logger.info(f"🎯 OPPORTUNITY #{i+1}: {opp['symbol']} {opp['side'].upper()} "
                       f"Score: {opp['score']:.1f} Price: ${opp['price']:.4f} "
                       f"Change: {opp['change_24h']:+.2f}% Vol: {opp['volume']:.0f}")

    async def _performance_monitor(self):
        """Monitor and report performance metrics"""
        while self.running:
            await asyncio.sleep(30)  # Report every 30 seconds
            
            if self.scans_completed > 0 and self.scan_times:
                avg_scan_time = np.mean(self.scan_times[-100:])  # Last 100 scans
                scans_per_second = 1.0 / avg_scan_time if avg_scan_time > 0 else 0
                
                logger.info(f"📊 PERFORMANCE UPDATE:")
                logger.info(f"   ⚡ Scans completed: {self.scans_completed}")
                logger.info(f"   🚀 Scans per second: {scans_per_second:.1f}")
                logger.info(f"   🎯 Opportunities found: {self.opportunities_found}")
                logger.info(f"   ⏱️  Avg scan time: {avg_scan_time*1000:.2f}ms")
                logger.info(f"   📡 WebSocket symbols: {len(self.websocket_data)}")
                logger.info("")

    def get_final_stats(self):
        """Get final performance statistics"""
        if not self.scan_times:
            return None
        
        avg_scan_time = np.mean(self.scan_times)
        max_scan_time = np.max(self.scan_times)
        min_scan_time = np.min(self.scan_times)
        scans_per_second = 1.0 / avg_scan_time if avg_scan_time > 0 else 0
        
        return {
            'total_scans': self.scans_completed,
            'opportunities_found': self.opportunities_found,
            'avg_scan_time_ms': avg_scan_time * 1000,
            'max_scan_time_ms': max_scan_time * 1000,
            'min_scan_time_ms': min_scan_time * 1000,
            'scans_per_second': scans_per_second,
            'symbols_processed': len(self.websocket_data),
            'websocket_only': True
        }


async def main():
    """Run the WebSocket-only demo"""
    demo = WebSocketOnlyDemo()
    
    try:
        await asyncio.wait_for(demo.start_demo(), timeout=120)  # 2-minute demo
    except asyncio.TimeoutError:
        logger.info("⏰ Demo completed (2 minutes)")
    except KeyboardInterrupt:
        logger.info("🛑 Demo stopped by user")
    finally:
        demo.running = False
        
        # Show final statistics
        stats = demo.get_final_stats()
        if stats:
            logger.info("")
            logger.info("🏆 FINAL PERFORMANCE STATISTICS:")
            logger.info("=" * 50)
            logger.info(f"📊 Total scans: {stats['total_scans']}")
            logger.info(f"🎯 Opportunities found: {stats['opportunities_found']}")
            logger.info(f"⚡ Scans per second: {stats['scans_per_second']:.1f}")
            logger.info(f"⏱️  Average scan time: {stats['avg_scan_time_ms']:.2f}ms")
            logger.info(f"🚀 Fastest scan: {stats['min_scan_time_ms']:.2f}ms")
            logger.info(f"📡 Symbols processed: {stats['symbols_processed']}")
            logger.info(f"🔗 WebSocket-only: {'✅' if stats['websocket_only'] else '❌'}")
            logger.info("=" * 50)
            
            # Performance rating
            if stats['scans_per_second'] > 15:
                logger.info("🔥 PERFORMANCE: EXCELLENT - Ultra-fast scanning!")
            elif stats['scans_per_second'] > 10:
                logger.info("✅ PERFORMANCE: GOOD - Fast scanning")
            elif stats['scans_per_second'] > 5:
                logger.info("⚠️  PERFORMANCE: FAIR - Moderate speed")
            else:
                logger.info("❌ PERFORMANCE: NEEDS IMPROVEMENT")


if __name__ == "__main__":
    print("🚀 Starting WebSocket-Only VIPER Demo...")
    print("Press Ctrl+C to stop the demo early")
    print("")
    asyncio.run(main())