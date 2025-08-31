#!/usr/bin/env python3
"""
# WEBSOCKET-ONLY VIPER TRADER
Ultra-fast trading system using only WebSocket data with vectorized scanning

NO REST API FALLBACKS - Pure WebSocket streaming for maximum speed
"""

import asyncio
import logging
import os
import time
import numpy as np
from typing import Dict, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass

from websocket_only_streamer import WebSocketOnlyStreamer, WebSocketConfig, MarketData
from vectorized_scanner import VectorizedScanningEngine, ScanningConfig, TradingOpportunity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WebSocketTraderConfig:
    """Configuration for WebSocket-only trader"""
    symbols: List[str]
    max_positions: int = 5
    position_size_usd: float = 100.0
    min_score_threshold: float = 70.0
    scan_interval: float = 0.05  # 50ms ultra-fast scanning
    stop_loss_pct: float = 2.0
    take_profit_pct: float = 4.0
    max_position_hold_time: int = 3600  # 1 hour max hold

class WebSocketOnlyTrader:
    """Ultra-fast WebSocket-only trading system"""
    
    def __init__(self, config: WebSocketTraderConfig):
        self.config = config
        self.running = False
        
        # WebSocket scanner with vectorized processing
        scan_config = ScanningConfig(
            min_score_threshold=config.min_score_threshold,
            max_positions=config.max_positions,
            scan_interval=config.scan_interval,
            batch_size=200
        )
        
        self.scanner = VectorizedScanningEngine(config.symbols, scan_config)
        
        # Position tracking
        self.active_positions: Dict[str, Dict] = {}
        self.position_history: List[Dict] = []
        
        # Performance metrics
        self.total_trades = 0
        self.winning_trades = 0
        self.total_pnl = 0.0
        self.start_time = None
        
        # Risk management
        self.daily_loss_limit = 500.0  # $500 daily loss limit
        self.daily_pnl = 0.0
        
        logger.info(f"🚀 WebSocket-Only Trader initialized for {len(config.symbols)} symbols")

    async def start_trading(self):
        """Start the WebSocket-only trading system"""
        self.running = True
        self.start_time = time.time()
        
        logger.info("🔥 Starting WebSocket-Only Trading System")
        logger.info("⚡ NO REST API FALLBACKS - Pure WebSocket streaming")
        
        # Register opportunity callback
        self.scanner.register_opportunity_callback(self._handle_trading_opportunities)
        
        # Start scanning
        scan_task = await self.scanner.start_scanning()
        
        # Start position monitoring
        monitor_task = asyncio.create_task(self._position_monitoring_loop())
        
        # Start performance reporting
        reporting_task = asyncio.create_task(self._performance_reporting_loop())
        
        return [scan_task, monitor_task, reporting_task]

    async def stop_trading(self):
        """Stop the trading system"""
        self.running = False
        await self.scanner.stop_scanning()
        
        # Close all positions
        await self._close_all_positions()
        
        # Final performance report
        await self._generate_final_report()
        
        logger.info("🛑 WebSocket-Only Trading stopped")

    async def _handle_trading_opportunities(self, opportunities: List[TradingOpportunity]):
        """Handle trading opportunities from vectorized scanner"""
        if not self.running or self._check_risk_limits():
            return
        
        # Filter opportunities
        filtered_opportunities = await self._filter_opportunities(opportunities)
        
        # Execute trades
        for opportunity in filtered_opportunities[:3]:  # Max 3 simultaneous trades
            await self._execute_trade(opportunity)

    async def _filter_opportunities(self, opportunities: List[TradingOpportunity]) -> List[TradingOpportunity]:
        """Filter opportunities based on risk and position limits"""
        filtered = []
        
        for opp in opportunities:
            # Skip if already have position in this symbol
            if opp.symbol in self.active_positions:
                continue
            
            # Check position limits
            if len(self.active_positions) >= self.config.max_positions:
                break
            
            # Check minimum requirements
            if (opp.score >= self.config.min_score_threshold and
                opp.volume >= 1000000 and  # Minimum volume
                opp.volatility <= 15.0 and  # Maximum volatility
                opp.confidence >= 0.7):  # Minimum confidence
                
                filtered.append(opp)
        
        return filtered

    async def _execute_trade(self, opportunity: TradingOpportunity):
        """Execute a trade based on opportunity (simulated for demo)"""
        try:
            symbol = opportunity.symbol
            side = opportunity.side
            price = opportunity.price
            
            # Calculate position size
            position_size = self.config.position_size_usd / price
            
            # Simulate trade execution
            position = {
                'symbol': symbol,
                'side': side,
                'entry_price': price,
                'size': position_size,
                'value_usd': self.config.position_size_usd,
                'entry_time': time.time(),
                'stop_loss': self._calculate_stop_loss(price, side),
                'take_profit': self._calculate_take_profit(price, side),
                'opportunity_score': opportunity.score,
                'confidence': opportunity.confidence
            }
            
            # Add to active positions
            self.active_positions[symbol] = position
            self.scanner.add_active_position(symbol)
            
            self.total_trades += 1
            
            logger.info(f"🎯 TRADE EXECUTED: {symbol} {side.upper()} "
                       f"@${price:.4f} Size: {position_size:.4f} "
                       f"Score: {opportunity.score:.1f}")
            
        except Exception as e:
            logger.error(f"❌ Trade execution error: {e}")

    def _calculate_stop_loss(self, price: float, side: str) -> float:
        """Calculate stop loss price"""
        if side == 'buy':
            return price * (1 - self.config.stop_loss_pct / 100)
        else:
            return price * (1 + self.config.stop_loss_pct / 100)

    def _calculate_take_profit(self, price: float, side: str) -> float:
        """Calculate take profit price"""
        if side == 'buy':
            return price * (1 + self.config.take_profit_pct / 100)
        else:
            return price * (1 - self.config.take_profit_pct / 100)

    async def _position_monitoring_loop(self):
        """Monitor active positions and manage exits"""
        while self.running:
            try:
                await self._check_position_exits()
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"❌ Position monitoring error: {e}")
                await asyncio.sleep(5)

    async def _check_position_exits(self):
        """Check if any positions should be closed"""
        current_time = time.time()
        positions_to_close = []
        
        for symbol, position in self.active_positions.items():
            # Get current price from scanner
            current_data = self.scanner.streamer.get_latest_data(symbol)
            if not current_data:
                continue
            
            current_price = current_data.price
            entry_price = position['entry_price']
            side = position['side']
            
            # Calculate P&L
            if side == 'buy':
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
            else:
                pnl_pct = ((entry_price - current_price) / entry_price) * 100
            
            pnl_usd = (pnl_pct / 100) * position['value_usd']
            
            # Check exit conditions
            should_close = False
            close_reason = ""
            
            # Stop loss check
            if ((side == 'buy' and current_price <= position['stop_loss']) or
                (side == 'sell' and current_price >= position['stop_loss'])):
                should_close = True
                close_reason = "STOP_LOSS"
            
            # Take profit check
            elif ((side == 'buy' and current_price >= position['take_profit']) or
                  (side == 'sell' and current_price <= position['take_profit'])):
                should_close = True
                close_reason = "TAKE_PROFIT"
            
            # Max hold time check
            elif current_time - position['entry_time'] > self.config.max_position_hold_time:
                should_close = True
                close_reason = "MAX_HOLD_TIME"
            
            if should_close:
                positions_to_close.append((symbol, current_price, pnl_usd, close_reason))
        
        # Close positions
        for symbol, exit_price, pnl_usd, reason in positions_to_close:
            await self._close_position(symbol, exit_price, pnl_usd, reason)

    async def _close_position(self, symbol: str, exit_price: float, pnl_usd: float, reason: str):
        """Close a position"""
        try:
            position = self.active_positions[symbol]
            
            # Update P&L
            self.total_pnl += pnl_usd
            self.daily_pnl += pnl_usd
            
            if pnl_usd > 0:
                self.winning_trades += 1
            
            # Create history record
            history_record = {
                **position,
                'exit_price': exit_price,
                'exit_time': time.time(),
                'pnl_usd': pnl_usd,
                'close_reason': reason,
                'hold_time': time.time() - position['entry_time']
            }
            
            self.position_history.append(history_record)
            
            # Remove from active positions
            del self.active_positions[symbol]
            self.scanner.remove_active_position(symbol)
            
            logger.info(f"🏁 POSITION CLOSED: {symbol} {reason} "
                       f"P&L: ${pnl_usd:+.2f} Exit: ${exit_price:.4f}")
            
        except Exception as e:
            logger.error(f"❌ Error closing position {symbol}: {e}")

    async def _close_all_positions(self):
        """Close all active positions"""
        for symbol in list(self.active_positions.keys()):
            current_data = self.scanner.streamer.get_latest_data(symbol)
            if current_data:
                await self._close_position(symbol, current_data.price, 0.0, "SHUTDOWN")

    def _check_risk_limits(self) -> bool:
        """Check if risk limits are exceeded"""
        if self.daily_pnl <= -self.daily_loss_limit:
            logger.warning(f"🚨 Daily loss limit reached: ${self.daily_pnl:.2f}")
            return True
        return False

    async def _performance_reporting_loop(self):
        """Regular performance reporting"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Report every minute
                await self._log_performance_metrics()
                
            except Exception as e:
                logger.error(f"❌ Performance reporting error: {e}")
                await asyncio.sleep(60)

    async def _log_performance_metrics(self):
        """Log current performance metrics"""
        if not self.start_time:
            return
        
        runtime = time.time() - self.start_time
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        # Get scanner metrics
        scanner_metrics = self.scanner.get_performance_metrics()
        
        logger.info(f"📊 PERFORMANCE REPORT:")
        logger.info(f"   🎯 Trades: {self.total_trades} | Win Rate: {win_rate:.1f}%")
        logger.info(f"   💰 Total P&L: ${self.total_pnl:+.2f} | Daily: ${self.daily_pnl:+.2f}")
        logger.info(f"   📍 Active Positions: {len(self.active_positions)}")
        logger.info(f"   ⚡ Scans/sec: {scanner_metrics.get('scans_per_second', 0):.1f}")
        logger.info(f"   🔗 WebSocket Status: {len(self.scanner.streamer.get_connection_status())} connections")

    async def _generate_final_report(self):
        """Generate final trading report"""
        if not self.start_time:
            return
        
        runtime = time.time() - self.start_time
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        logger.info(f"\n🎯 FINAL TRADING REPORT")
        logger.info(f"=" * 50)
        logger.info(f"⏱️  Runtime: {runtime/3600:.2f} hours")
        logger.info(f"🎯 Total Trades: {self.total_trades}")
        logger.info(f"✅ Winning Trades: {self.winning_trades}")
        logger.info(f"📈 Win Rate: {win_rate:.1f}%")
        logger.info(f"💰 Total P&L: ${self.total_pnl:+.2f}")
        logger.info(f"📊 Avg P&L per Trade: ${self.total_pnl/self.total_trades:+.2f}" if self.total_trades > 0 else "N/A")
        logger.info(f"⚡ WebSocket-Only Mode: ✅ (No REST fallbacks used)")
        logger.info(f"=" * 50)


# Example usage and demo
async def demo_websocket_trader():
    """Demonstrate the WebSocket-only trader"""
    symbols = [
        "BTC/USDT", "ETH/USDT", "ADA/USDT", "DOT/USDT",
        "LINK/USDT", "UNI/USDT", "AAVE/USDT", "SUSHI/USDT",
        "ATOM/USDT", "AVAX/USDT"
    ]
    
    config = WebSocketTraderConfig(
        symbols=symbols,
        max_positions=3,
        position_size_usd=50.0,  # Small demo positions
        min_score_threshold=65.0,
        scan_interval=0.1,  # 100ms scanning
        stop_loss_pct=1.5,
        take_profit_pct=3.0
    )
    
    trader = WebSocketOnlyTrader(config)
    
    try:
        logger.info("🚀 Starting WebSocket-Only Demo Trading")
        
        # Start trading
        tasks = await trader.start_trading()
        
        # Run demo for 5 minutes
        await asyncio.sleep(300)
        
        logger.info("⏰ Demo time complete - stopping trading")
        
    finally:
        await trader.stop_trading()


if __name__ == "__main__":
    asyncio.run(demo_websocket_trader())