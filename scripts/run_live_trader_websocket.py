#!/usr/bin/env python3
"""
🚀 VIPER MULTI-PAIR LIVE TRADER - WEBSOCKET VERSION WITH CCXT
Live trading system using CCXT's built-in websocket functionality for real-time data
"""

import os
import sys
import time
import logging
import ccxt
import asyncio
import random
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Optional, Set
from collections import defaultdict, deque
import threading
import queue

# Load environment variables
load_dotenv()

# Add project paths
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - VIPER_WS_TRADER - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/viper_websocket_trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebSocketMultiPairVIPERTrader:
    """VIPER Trader that uses CCXT websockets for real-time market data"""

    def __init__(self):
        # Load API credentials
        self.api_key = os.getenv('BITGET_API_KEY')
        self.api_secret = os.getenv('BITGET_API_SECRET')
        self.api_password = os.getenv('BITGET_API_PASSWORD')

        # Trading configuration - AS PER USER REQUIREMENTS
        self.position_size_percent = float(os.getenv('RISK_PER_TRADE', '0.001'))
        self.max_leverage = int(os.getenv('MAX_LEVERAGE', '50'))
        self.take_profit_pct = float(os.getenv('TAKE_PROFIT_PCT', '3.0'))
        self.stop_loss_pct = float(os.getenv('STOP_LOSS_PCT', '2.0'))
        self.max_positions = int(os.getenv('MAX_POSITIONS', '10'))
        self.min_margin_per_trade = float(os.getenv('MIN_MARGIN_PER_TRADE', '2.0'))  # $2.0 as per rules

        self.exchange = None
        self.all_pairs = []
        self.active_positions = {}
        self.is_running = False
        
        # Websocket data storage
        self.market_data = {}  # Real-time market data from websockets
        self.ohlcv_data = defaultdict(lambda: defaultdict(deque))  # [symbol][timeframe] = deque of ohlcv
        self.tickers = {}  # Real-time ticker data
        
        # Threading for websockets
        self.ws_thread = None
        self.data_lock = threading.RLock()
        
        logger.info(f"🎯 WEBSOCKET TRADER - Position Limit: {self.max_positions}")
        logger.info(f"📊 Margin per trade: ${self.min_margin_per_trade} × {self.max_leverage}x = ${self.min_margin_per_trade * self.max_leverage} notional")

    def connect(self):
        """Connect to Bitget and setup websocket connections"""
        try:
            if not all([self.api_key, self.api_secret, self.api_password]):
                logger.error("❌ Missing API credentials")
                return False

            logger.info("🔌 Connecting to Bitget with WebSocket support...")
            self.exchange = ccxt.bitget({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'password': self.api_password,
                'options': {
                    'defaultType': 'swap',
                    'adjustForTimeDifference': True,
                    'hedgeMode': False,
                    'createMarketBuyOrderRequiresPrice': False,  # Fix for market buy orders
                },
                'sandbox': False,
            })

            # Load markets
            markets = self.exchange.load_markets()
            self.all_pairs = [
                symbol for symbol in markets.keys()
                if (markets[symbol]['active'] and 
                    markets[symbol].get('type') == 'swap' and
                    markets[symbol].get('quote') == 'USDT' and
                    (symbol.endswith('USDT') or symbol.endswith(':USDT')) and
                    symbol.count('USDT') == 1)
            ]

            logger.info(f"✅ Connected to Bitget - {len(self.all_pairs)} swap pairs available")
            logger.info("🔥 WebSocket trader ready!")
            return True

        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False

    def start_websocket_feeds(self, symbols: List[str]):
        """Start websocket feeds for multiple symbols"""
        logger.info(f"🔗 Starting websocket feeds for {len(symbols)} symbols...")
        
        # Start websocket thread
        self.ws_thread = threading.Thread(target=self._run_websocket_feeds, args=(symbols,))
        self.ws_thread.daemon = True
        self.ws_thread.start()
        
        # Give websockets time to connect
        time.sleep(2)
        logger.info("✅ WebSocket feeds started")

    def _run_websocket_feeds(self, symbols: List[str]):
        """Run websocket feeds in async event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._websocket_manager(symbols))
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
        finally:
            loop.close()

    async def _websocket_manager(self, symbols: List[str]):
        """Manage multiple websocket connections"""
        logger.info(f"🔗 Setting up websocket streams for {len(symbols)} symbols...")
        
        tasks = []
        
        # Watch tickers for all symbols (real-time price data)
        if hasattr(self.exchange, 'watch_tickers'):
            tasks.append(self._watch_tickers(symbols))
        
        # Watch OHLCV for multiple timeframes
        timeframes = ['1m', '5m', '15m']
        for timeframe in timeframes:
            if hasattr(self.exchange, 'watch_ohlcv_for_symbols'):
                tasks.append(self._watch_ohlcv_multiple(symbols, timeframe))
        
        # Watch positions and balance
        if hasattr(self.exchange, 'watch_positions'):
            tasks.append(self._watch_positions())
        
        if hasattr(self.exchange, 'watch_balance'):
            tasks.append(self._watch_balance())
        
        # Run all websocket tasks concurrently
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _watch_tickers(self, symbols: List[str]):
        """Watch real-time ticker data for multiple symbols"""
        logger.info(f"📊 Watching tickers for {len(symbols)} symbols...")
        
        while self.is_running:
            try:
                tickers = await self.exchange.watch_tickers(symbols)
                
                with self.data_lock:
                    self.tickers.update(tickers)
                
                logger.debug(f"📊 Updated {len(tickers)} tickers")
                
            except Exception as e:
                logger.error(f"❌ Ticker websocket error: {e}")
                await asyncio.sleep(1)

    async def _watch_ohlcv_multiple(self, symbols: List[str], timeframe: str):
        """Watch OHLCV data for multiple symbols and timeframe"""
        logger.info(f"📈 Watching {timeframe} OHLCV for {len(symbols)} symbols...")
        
        while self.is_running:
            try:
                # Watch OHLCV for all symbols in this timeframe
                for symbol in symbols:
                    if not self.is_running:
                        break
                        
                    try:
                        ohlcv_data = await self.exchange.watch_ohlcv(symbol, timeframe)
                        
                        with self.data_lock:
                            # Store latest 100 candles per timeframe
                            if len(self.ohlcv_data[symbol][timeframe]) > 100:
                                self.ohlcv_data[symbol][timeframe].popleft()
                            
                            # Update with latest data
                            if ohlcv_data:
                                for candle in ohlcv_data:
                                    self.ohlcv_data[symbol][timeframe].append(candle)
                        
                    except Exception as symbol_error:
                        logger.debug(f"⚠️ OHLCV error for {symbol} {timeframe}: {symbol_error}")
                        continue
                
                await asyncio.sleep(0.1)  # Small delay to prevent overwhelming
                
            except Exception as e:
                logger.error(f"❌ OHLCV websocket error for {timeframe}: {e}")
                await asyncio.sleep(1)

    async def _watch_positions(self):
        """Watch real-time position updates"""
        logger.info("📊 Watching positions...")
        
        while self.is_running:
            try:
                positions = await self.exchange.watch_positions()
                
                with self.data_lock:
                    # Update active positions based on real-time data
                    open_symbols = {pos['symbol'] for pos in positions if float(pos.get('contracts', 0)) > 0}
                    
                    # Remove closed positions from tracking
                    positions_to_remove = [symbol for symbol in self.active_positions if symbol not in open_symbols]
                    for symbol in positions_to_remove:
                        logger.info(f"🎯 Position closed via websocket: {symbol}")
                        del self.active_positions[symbol]
                
            except Exception as e:
                logger.error(f"❌ Position websocket error: {e}")
                await asyncio.sleep(5)

    async def _watch_balance(self):
        """Watch real-time balance updates"""
        logger.info("💰 Watching balance...")
        
        while self.is_running:
            try:
                balance = await self.exchange.watch_balance()
                # Balance updates received automatically
                logger.debug("💰 Balance updated via websocket")
                
            except Exception as e:
                logger.error(f"❌ Balance websocket error: {e}")
                await asyncio.sleep(5)

    def get_websocket_ohlcv(self, symbol: str, timeframe: str, limit: int = 30) -> List[List]:
        """Get OHLCV data from websocket cache"""
        with self.data_lock:
            if symbol in self.ohlcv_data and timeframe in self.ohlcv_data[symbol]:
                data = list(self.ohlcv_data[symbol][timeframe])
                return data[-limit:] if len(data) >= limit else data
            return []

    def get_websocket_ticker(self, symbol: str) -> Optional[Dict]:
        """Get ticker data from websocket cache"""
        with self.data_lock:
            return self.tickers.get(symbol)

    def generate_signal_websocket(self, symbol):
        """Generate trading signal using websocket data - VIPER Style"""
        try:
            # Get real-time OHLCV data from websocket cache
            ohlcv_1m = self.get_websocket_ohlcv(symbol, '1m', 30)
            ohlcv_5m = self.get_websocket_ohlcv(symbol, '5m', 20)
            ohlcv_15m = self.get_websocket_ohlcv(symbol, '15m', 12)

            if len(ohlcv_1m) < 10 or len(ohlcv_5m) < 10 or len(ohlcv_15m) < 6:
                logger.debug(f"📊 {symbol}: Insufficient websocket data for analysis")
                return 'HOLD'

            # Extract closing prices for analysis
            closes_1m = [candle[4] for candle in ohlcv_1m]
            closes_5m = [candle[4] for candle in ohlcv_5m]
            closes_15m = [candle[4] for candle in ohlcv_15m]

            # MULTI-TIMEFRAME ANALYSIS using websocket data
            primary_trend = self.analyze_trend_relaxed(closes_15m)
            secondary_trend = self.analyze_trend_relaxed(closes_5m)
            fast_trend = self.analyze_trend_relaxed(closes_1m)

            current_price = closes_1m[-1]

            # Same signal logic as REST version but using websocket data
            if (primary_trend in ['BULLISH', 'WEAK_BULLISH'] and 
                secondary_trend in ['BULLISH', 'WEAK_BULLISH', 'SIDEWAYS'] and
                fast_trend in ['BULLISH', 'WEAK_BULLISH', 'SIDEWAYS']):
                
                recent_low = min(closes_1m[-5:])
                if current_price > recent_low * 1.005:
                    logger.info(f"📈 {symbol}: WEBSOCKET BULLISH - 15m:{primary_trend}, 5m:{secondary_trend}, 1m:{fast_trend}")
                    return 'BUY'

            elif (primary_trend in ['BEARISH', 'WEAK_BEARISH'] and 
                  secondary_trend in ['BEARISH', 'WEAK_BEARISH', 'SIDEWAYS'] and
                  fast_trend in ['BEARISH', 'WEAK_BEARISH', 'SIDEWAYS']):
                
                recent_high = max(closes_1m[-5:])
                if current_price < recent_high * 0.995:
                    logger.info(f"📉 {symbol}: WEBSOCKET BEARISH - 15m:{primary_trend}, 5m:{secondary_trend}, 1m:{fast_trend}")
                    return 'SELL'

            return 'HOLD'

        except Exception as e:
            logger.error(f"❌ Websocket signal generation error for {symbol}: {e}")
            return 'HOLD'

    def analyze_trend_relaxed(self, closes):
        """Relaxed trend analysis for more flexible signal generation"""
        if len(closes) < 8:
            return 'SIDEWAYS'

        # Simple moving averages for trend direction
        short_ma = sum(closes[-5:]) / 5
        long_ma = sum(closes[-10:]) / 10
        current_price = closes[-1]
        ma_diff = (short_ma - long_ma) / long_ma * 100

        # Trend strength based on MA separation
        if ma_diff > 0.2:
            if current_price > short_ma * 1.002:
                return 'BULLISH'
            else:
                return 'WEAK_BULLISH'
        elif ma_diff < -0.2:
            if current_price < short_ma * 0.998:
                return 'BEARISH'
            else:
                return 'WEAK_BEARISH'

        # Check for sideways with slight bias
        recent_change = (closes[-1] - closes[-5]) / closes[-5] * 100
        if abs(recent_change) < 0.3:
            return 'SIDEWAYS'
        elif recent_change > 0:
            return 'WEAK_BULLISH'
        else:
            return 'WEAK_BEARISH'

    def execute_trade(self, symbol, signal):
        """Execute trade using websocket data for current price"""
        try:
            # Get current price from websocket ticker data
            ticker = self.get_websocket_ticker(symbol)
            if not ticker:
                logger.warning(f"⚠️ No websocket ticker data for {symbol}, falling back to REST")
                ticker = self.exchange.fetch_ticker(symbol)
            
            current_price = ticker['last']

            # Calculate position size
            try:
                balance = self.exchange.fetch_balance({'type': 'swap'})
                usdt_balance = float(balance.get('USDT', {}).get('free', 0))
                
                if usdt_balance <= 0:
                    logger.error(f"❌ No USDT balance available for {symbol}")
                    return None

                # Use configured minimum margin ($1.0 as requested)
                margin_value_usdt = self.min_margin_per_trade

                if usdt_balance < margin_value_usdt:
                    logger.warning(f"⚠️ Insufficient balance: ${usdt_balance:.2f} < ${margin_value_usdt:.2f}")
                    return None

                # Get coin's max leverage
                try:
                    market_info = self.exchange.market(symbol)
                    coin_max_leverage = market_info.get('limits', {}).get('leverage', {}).get('max', 50)
                    coin_max_leverage = min(coin_max_leverage, 100)
                except:
                    coin_max_leverage = 50

                # Calculate notional: $1 margin × leverage = $50 notional (as requested)
                notional_value_usdt = margin_value_usdt * coin_max_leverage
                position_size = notional_value_usdt / current_price

                logger.info(f"💰 WEBSOCKET: ${margin_value_usdt} Margin × {coin_max_leverage}x = ${notional_value_usdt:.2f} Notional")

                # Execute order
                if signal == 'BUY':
                    order = self.exchange.create_market_buy_order(
                        symbol,
                        position_size,
                        params={
                            'leverage': coin_max_leverage,
                            'marginMode': 'isolated',
                            'tradeSide': 'open'
                        }
                    )
                elif signal == 'SELL':
                    order = self.exchange.create_market_sell_order(
                        symbol,
                        position_size,
                        params={
                            'leverage': coin_max_leverage,
                            'marginMode': 'isolated',
                            'tradeSide': 'open'
                        }
                    )

                logger.info(f"✅ WEBSOCKET Trade executed: {order['id']}")
                
                # Set TP/SL orders
                entry_price = order.get('price', current_price)
                
                if signal == 'BUY':
                    tp_price = entry_price * (1 + self.take_profit_pct / 100)
                    sl_price = entry_price * (1 - self.stop_loss_pct / 100)
                    tp_side = 'sell'
                    sl_side = 'sell'
                else:
                    tp_price = entry_price * (1 - self.take_profit_pct / 100)
                    sl_price = entry_price * (1 + self.stop_loss_pct / 100)
                    tp_side = 'buy'
                    sl_side = 'buy'

                # Create TP/SL orders
                try:
                    tp_order = self.exchange.create_limit_order(
                        symbol, tp_side, position_size, tp_price,
                        params={'leverage': coin_max_leverage, 'marginMode': 'isolated', 
                               'tradeSide': 'close', 'reduceOnly': True})
                    
                    sl_order = self.exchange.create_limit_order(
                        symbol, sl_side, position_size, sl_price,
                        params={'leverage': coin_max_leverage, 'marginMode': 'isolated',
                               'tradeSide': 'close', 'reduceOnly': True})
                    
                    logger.info(f"✅ TP/SL orders placed for {symbol}")
                
                except Exception as tp_sl_error:
                    logger.error(f"❌ Failed to set TP/SL for {symbol}: {tp_sl_error}")

                return order

            except Exception as e:
                logger.error(f"❌ Position calculation error for {symbol}: {e}")
                return None

        except Exception as e:
            logger.error(f"❌ Websocket trade execution error for {symbol}: {e}")
            return None

    def scan_markets_websocket(self):
        """Scan markets using websocket data"""
        opportunities = []
        
        logger.info(f"🔍 WEBSOCKET SCAN: {len(self.all_pairs)} pairs...")
        
        # Scan subset of pairs
        pairs_to_scan = min(25, len(self.all_pairs))
        scanned_pairs = random.sample(self.all_pairs, pairs_to_scan)
        
        for symbol in scanned_pairs:
            if len(self.active_positions) >= self.max_positions:
                break
            
            if symbol in self.active_positions:
                continue
            
            # Use websocket data for signal generation
            signal = self.generate_signal_websocket(symbol)
            
            if signal in ['BUY', 'SELL']:
                opportunities.append({
                    'symbol': symbol,
                    'signal': signal,
                    'confidence': 0.8,  # High confidence for websocket signals
                    'timestamp': time.time(),
                    'source': 'websocket'
                })
                logger.info(f"📊 WEBSOCKET opportunity: {symbol} -> {signal}")
        
        return opportunities

    def run(self):
        """Main trading loop with websocket data"""
        self.is_running = True
        cycle = 0
        
        logger.info("🚀 Starting WEBSOCKET MULTI-PAIR TRADING!")
        logger.info("=" * 80)
        
        # Start websocket feeds for top symbols
        top_symbols = self.all_pairs[:50]  # Start with top 50 symbols
        self.start_websocket_feeds(top_symbols)
        
        # Give websockets time to collect data
        logger.info("⏰ Waiting for websocket data collection...")
        time.sleep(10)
        
        while self.is_running:
            cycle += 1
            logger.info(f"\n🔄 WEBSOCKET Cycle #{cycle}")
            
            # Scan using websocket data
            opportunities = self.scan_markets_websocket()
            
            trades_this_cycle = 0
            for opportunity in opportunities:
                if not self.is_running:
                    break
                    
                symbol = opportunity['symbol']
                signal = opportunity['signal']
                
                order = self.execute_trade(symbol, signal)
                if order:
                    trades_this_cycle += 1
                    
                    # Track position
                    self.active_positions[symbol] = {
                        'order_id': order['id'],
                        'signal': signal,
                        'entry_price': order.get('price', 0),
                        'quantity': order['amount'],
                        'timestamp': time.time(),
                        'source': 'websocket'
                    }
            
            logger.info(f"✅ WEBSOCKET Cycle #{cycle} - {trades_this_cycle} trades executed")
            logger.info(f"📊 Active positions: {len(self.active_positions)}")
            
            # Show websocket data status
            with self.data_lock:
                symbols_with_data = len([s for s in top_symbols if s in self.tickers])
                logger.info(f"📡 Websocket data: {symbols_with_data}/{len(top_symbols)} symbols active")
            
            time.sleep(30)

    def stop(self):
        """Stop websocket trading"""
        logger.info("🛑 Stopping websocket trader...")
        self.is_running = False
        
        if self.ws_thread and self.ws_thread.is_alive():
            self.ws_thread.join(timeout=5)
            logger.info("✅ Websocket threads stopped")

def main():
    """Main entry point for websocket trader"""
    print("🚀 VIPER WEBSOCKET MULTI-PAIR LIVE TRADING SYSTEM")
    print("📡 Using CCXT built-in websockets for real-time data")
    print("=" * 80)

    # Verify API credentials
    api_key = os.getenv('BITGET_API_KEY')
    api_secret = os.getenv('BITGET_API_SECRET')
    api_password = os.getenv('BITGET_API_PASSWORD')

    if not all([api_key, api_secret, api_password]):
        logger.error("❌ Missing API credentials!")
        return False

    try:
        logger.info("🔄 Initializing WebSocket VIPER Trader...")
        trader = WebSocketMultiPairVIPERTrader()

        if not trader.connect():
            logger.error("❌ Failed to connect to exchange")
            return False

        logger.info("✅ Connected to Bitget with WebSocket support")
        logger.info(f"📡 Ready to trade with real-time websocket data!")
        logger.info("🚀 Starting websocket live trading...")

        trader.run()

    except KeyboardInterrupt:
        logger.info("🛑 Trading stopped by user")
        if 'trader' in locals():
            trader.stop()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return False

    return True

if __name__ == "__main__":
    main()