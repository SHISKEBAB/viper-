#!/usr/bin/env python3
"""
🔥 REAL-DATA API BACKTESTER
==========================

This script integrates with the existing VIPER API infrastructure
to run backtests with REAL market data from exchanges.

Features:
✅ Real Bitget API data integration
✅ Sub-1h timeframe support (1m, 5m, 15m, 30m)
✅ Comprehensive strategy testing
✅ Entry point optimization with real data
✅ Performance analysis and reporting
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'src'))
sys.path.append(str(project_root / 'services' / 'shared'))

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - REAL_DATA_BACKTESTER - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealDataProvider:
    """Real market data provider using existing API infrastructure"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"  # API server
        self.market_data_url = "http://localhost:8001"  # Market data manager
        self.cache = {}
        
        # Load environment variables
        self.api_key = os.getenv('BITGET_API_KEY', '')
        self.api_secret = os.getenv('BITGET_API_SECRET', '')
        self.api_password = os.getenv('BITGET_API_PASSWORD', '')
        
        logger.info("Real Data Provider initialized")
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        if not REQUESTS_AVAILABLE:
            logger.error("Requests library not available")
            return None
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Request failed with status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None
    
    def get_kline_data(self, symbol: str, timeframe: str, limit: int = 1000) -> List[Dict]:
        """Get real kline data from Bitget API"""
        
        # Try market data manager first
        try:
            url = f"{self.market_data_url}/api/klines"
            params = {
                'symbol': symbol,
                'interval': timeframe,
                'limit': limit
            }
            
            data = self._make_request(url, params)
            if data and 'success' in data and data['success']:
                return data.get('data', [])
        except Exception as e:
            logger.error(f"Market data manager not available: {e}")
        
        # NO FALLBACK TO SYNTHETIC DATA - REAL API ONLY!
        error_msg = f"❌ CRITICAL: Failed to fetch REAL data for {symbol} {timeframe}. NO SYNTHETIC DATA ALLOWED!"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    def get_historical_data(self, symbol: str, timeframe: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get historical data for specified time range"""
        cache_key = f"{symbol}_{timeframe}_{start_time}_{end_time}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Calculate required number of candles
        tf_minutes = {'1m': 1, '5m': 5, '15m': 15, '30m': 30}
        minutes = tf_minutes.get(timeframe, 15)
        total_minutes = int((end_time - start_time).total_seconds() / 60)
        required_candles = min(total_minutes // minutes, 1000)  # API limits
        
        data = self.get_kline_data(symbol, timeframe, required_candles)
        
        # Filter data by time range if available
        if data:
            start_ts = int(start_time.timestamp() * 1000)
            end_ts = int(end_time.timestamp() * 1000)
            
            filtered_data = []
            for candle in data:
                ts = candle.get('timestamp', 0)
                if start_ts <= ts <= end_ts:
                    filtered_data.append(candle)
            
            data = filtered_data
        
        self.cache[cache_key] = data
        return data

class RealDataBacktester:
    """Backtester using real market data"""
    
    def __init__(self):
        self.data_provider = RealDataProvider()
        
        # Import the comprehensive backtester components
        try:
            from comprehensive_sub1h_backtester import StrategyEngine, EntryPointOptimizer, BacktestConfiguration, BacktestResult
            self.strategy_engine = StrategyEngine()
            self.entry_optimizer = EntryPointOptimizer()
            self.BacktestConfiguration = BacktestConfiguration
            self.BacktestResult = BacktestResult
        except ImportError:
            logger.error("Could not import backtesting components")
            raise
        
        # Results storage
        self.results_dir = Path('/home/runner/work/viper-/viper-/backtest_results/real_data')
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Real Data Backtester initialized")
    
    def run_real_data_backtest(self, strategy: str, symbol: str, timeframe: str, parameters: Dict) -> Dict:
        """Run backtest with real data"""
        
        start_time = time.time()
        
        try:
            # Get real market data (last 7 days for faster execution)
            end_time = datetime.now()
            start_time_dt = end_time - timedelta(days=7)
            
            logger.info(f"Getting real data for {symbol} {timeframe} from {start_time_dt} to {end_time}")
            
            real_data = self.data_provider.get_historical_data(symbol, timeframe, start_time_dt, end_time)
            
            if not real_data:
                return {
                    'success': False,
                    'error': 'No real data available',
                    'strategy': strategy,
                    'symbol': symbol,
                    'timeframe': timeframe
                }
            
            # Convert data format for strategy engine
            formatted_data = []
            for candle in real_data:
                formatted_data.append({
                    'timestamp': datetime.fromtimestamp(candle['timestamp'] / 1000),
                    'open': float(candle['open']),
                    'high': float(candle['high']),
                    'low': float(candle['low']),
                    'close': float(candle['close']),
                    'volume': float(candle['volume'])
                })
            
            # Generate signals using real data
            signals = self.strategy_engine.generate_signals(strategy, formatted_data, parameters)
            
            if not signals:
                return {
                    'success': False,
                    'error': 'No signals generated',
                    'strategy': strategy,
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'data_points': len(formatted_data)
                }
            
            # Optimize entry points
            optimized_entries = []
            for signal in signals:
                optimized_entry = self.entry_optimizer.optimize_entry(formatted_data, signal)
                optimized_entries.append(optimized_entry)
            
            # Simulate trades with real data
            result = self._simulate_real_trades(formatted_data, signals, optimized_entries)
            
            result.update({
                'success': True,
                'strategy': strategy,
                'symbol': symbol,
                'timeframe': timeframe,
                'parameters': parameters,
                'data_points': len(formatted_data),
                'signals_generated': len(signals),
                'execution_time': time.time() - start_time,
                'data_source': 'real_api'
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Real data backtest failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'strategy': strategy,
                'symbol': symbol,
                'timeframe': timeframe,
                'execution_time': time.time() - start_time
            }
    
    def _simulate_real_trades(self, data: List[Dict], signals: List[Dict], optimized_entries) -> Dict:
        """Simulate trading with real market data"""
        
        initial_balance = 10000
        balance = initial_balance
        trades = []
        equity_curve = [initial_balance]
        
        position_size = 0.05  # 5% per trade for safer real-data testing
        
        for i, signal in enumerate(signals):
            if i >= len(optimized_entries):
                continue
            
            entry = optimized_entries[i]
            trade_amount = balance * position_size
            
            # Find the actual exit point using real data
            signal_time = signal['timestamp']
            signal_idx = None
            
            for j, candle in enumerate(data):
                if candle['timestamp'] == signal_time:
                    signal_idx = j
                    break
            
            if signal_idx is None or signal_idx >= len(data) - 10:
                continue
            
            # Look forward in real data to find exit
            entry_price = entry.price
            stop_loss = signal.get('stop_loss', entry_price * 0.98 if signal['type'] == 'buy' else entry_price * 1.02)
            take_profit = signal.get('take_profit', entry_price * 1.04 if signal['type'] == 'buy' else entry_price * 0.96)
            
            # Simulate trade execution using next 10 candles
            exit_price = None
            exit_reason = None
            
            for k in range(signal_idx + 1, min(signal_idx + 11, len(data))):
                candle = data[k]
                
                if signal['type'] == 'buy':
                    if candle['low'] <= stop_loss:
                        exit_price = stop_loss
                        exit_reason = 'stop_loss'
                        break
                    elif candle['high'] >= take_profit:
                        exit_price = take_profit
                        exit_reason = 'take_profit'
                        break
                else:  # sell
                    if candle['high'] >= stop_loss:
                        exit_price = stop_loss
                        exit_reason = 'stop_loss'
                        break
                    elif candle['low'] <= take_profit:
                        exit_price = take_profit
                        exit_reason = 'take_profit'
                        break
            
            # If no exit found, use last available price
            if exit_price is None:
                exit_price = data[min(signal_idx + 10, len(data) - 1)]['close']
                exit_reason = 'time_exit'
            
            # Calculate P&L
            if signal['type'] == 'buy':
                pnl = (exit_price - entry_price) / entry_price * trade_amount
            else:
                pnl = (entry_price - exit_price) / entry_price * trade_amount
            
            balance += pnl
            equity_curve.append(balance)
            
            trades.append({
                'entry_price': entry_price,
                'exit_price': exit_price,
                'pnl': pnl,
                'type': signal['type'],
                'exit_reason': exit_reason,
                'confidence': entry.confidence,
                'signal_strength': entry.signal_strength
            })
        
        # Calculate metrics
        if not trades:
            return {
                'total_return': 0.0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'max_drawdown': 0.0,
                'total_trades': 0,
                'avg_pnl': 0.0
            }
        
        total_return = (balance - initial_balance) / initial_balance
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] < 0]
        
        win_rate = len(winning_trades) / len(trades)
        avg_pnl = sum(t['pnl'] for t in trades) / len(trades)
        
        gross_profit = sum(t['pnl'] for t in winning_trades)
        gross_loss = abs(sum(t['pnl'] for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Max drawdown
        peak = equity_curve[0]
        max_drawdown = 0
        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        return {
            'total_return': total_return,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'avg_pnl': avg_pnl,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'final_balance': balance,
            'equity_curve_length': len(equity_curve),
            'trades': trades[:5]  # Include first 5 trades as examples
        }
    
    def run_comprehensive_real_data_test(self) -> Dict:
        """Run comprehensive test with real data across multiple configurations"""
        
        if console:
            console.print("🔥 Starting Real Data Comprehensive Backtesting", style="bold red")
        
        # Test configurations (reduced for real data testing)
        strategies = ['sma_crossover', 'rsi_oversold', 'bollinger_bands', 'ema_trend']
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT']
        timeframes = ['5m', '15m', '30m']  # Skip 1m for faster execution
        
        # Optimized parameter sets
        param_sets = {
            'sma_crossover': [
                {'fast_period': 8, 'slow_period': 21},
                {'fast_period': 12, 'slow_period': 26}
            ],
            'rsi_oversold': [
                {'rsi_period': 14, 'oversold_level': 30, 'overbought_level': 70},
                {'rsi_period': 21, 'oversold_level': 25, 'overbought_level': 75}
            ],
            'bollinger_bands': [
                {'bb_period': 20, 'std_dev': 2},
                {'bb_period': 15, 'std_dev': 1.8}
            ],
            'ema_trend': [
                {'ema_period': 21},
                {'ema_period': 34}
            ]
        }
        
        results = []
        total_tests = sum(len(param_sets[s]) for s in strategies) * len(symbols) * len(timeframes)
        
        if console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            ) as progress:
                task = progress.add_task(f"Testing {total_tests} configurations...", total=total_tests)
                
                test_count = 0
                for strategy in strategies:
                    for symbol in symbols:
                        for timeframe in timeframes:
                            for params in param_sets[strategy]:
                                test_count += 1
                                
                                progress.update(task, description=f"Testing {strategy} {symbol} {timeframe}")
                                
                                result = self.run_real_data_backtest(strategy, symbol, timeframe, params)
                                results.append(result)
                                
                                progress.update(task, advance=1)
                                
                                # Brief pause to avoid overwhelming the API
                                time.sleep(0.1)
        else:
            test_count = 0
            for strategy in strategies:
                for symbol in symbols:
                    for timeframe in timeframes:
                        for params in param_sets[strategy]:
                            test_count += 1
                            print(f"Testing {test_count}/{total_tests}: {strategy} {symbol} {timeframe}")
                            
                            result = self.run_real_data_backtest(strategy, symbol, timeframe, params)
                            results.append(result)
        
        # Analyze results
        successful_results = [r for r in results if r.get('success', False) and r.get('total_trades', 0) > 0]
        
        analysis = {
            'total_tests': len(results),
            'successful_tests': len(successful_results),
            'success_rate': len(successful_results) / len(results) * 100 if results else 0,
            'results': results,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        if successful_results:
            # Performance analysis
            returns = [r['total_return'] for r in successful_results]
            win_rates = [r['win_rate'] for r in successful_results]
            profit_factors = [r['profit_factor'] for r in successful_results]
            
            analysis.update({
                'avg_return': sum(returns) / len(returns) * 100,
                'best_return': max(returns) * 100,
                'worst_return': min(returns) * 100,
                'avg_win_rate': sum(win_rates) / len(win_rates) * 100,
                'avg_profit_factor': sum(profit_factors) / len(profit_factors),
                'top_performers': sorted(successful_results, key=lambda x: x['total_return'], reverse=True)[:5]
            })
        
        # Save results
        results_file = self.results_dir / f"real_data_comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(results_file, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            logger.info(f"Results saved to {results_file}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")
        
        return analysis

def main():
    """Main execution function"""
    
    if console:
        console.print("🔥 VIPER Real Data Backtesting System", style="bold red")
        console.print("Using REAL market data from APIs", style="yellow")
    else:
        print("🔥 VIPER Real Data Backtesting System")
        print("Using REAL market data from APIs")
    
    # Check environment
    api_key = os.getenv('BITGET_API_KEY', '')
    if not api_key or api_key == 'your_bitget_api_key_here':
        if console:
            console.print("⚠️ Warning: No API key configured. Using fallback data generation.", style="yellow")
        else:
            print("⚠️ Warning: No API key configured. Using fallback data generation.")
    
    # Initialize backtester
    backtester = RealDataBacktester()
    
    # Run comprehensive real data backtesting
    results = backtester.run_comprehensive_real_data_test()
    
    # Display results
    if console:
        table = Table(title="Real Data Backtesting Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Total Tests", str(results['total_tests']))
        table.add_row("Successful Tests", str(results['successful_tests']))
        table.add_row("Success Rate", f"{results['success_rate']:.1f}%")
        
        if results['successful_tests'] > 0:
            table.add_row("Average Return", f"{results.get('avg_return', 0):.2f}%")
            table.add_row("Best Return", f"{results.get('best_return', 0):.2f}%")
            table.add_row("Average Win Rate", f"{results.get('avg_win_rate', 0):.1f}%")
            table.add_row("Average Profit Factor", f"{results.get('avg_profit_factor', 0):.2f}")
        
        console.print(table)
        
        if results.get('top_performers'):
            console.print("\n🏆 Top Performers:", style="bold green")
            for i, performer in enumerate(results['top_performers'], 1):
                console.print(f"{i}. {performer['strategy']} {performer['symbol']} {performer['timeframe']} - "
                            f"Return: {performer['total_return']*100:.2f}%, WR: {performer['win_rate']*100:.1f}%")
    else:
        print(f"\n📊 Real Data Backtesting Results:")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Successful Tests: {results['successful_tests']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        
        if results['successful_tests'] > 0:
            print(f"Average Return: {results.get('avg_return', 0):.2f}%")
            print(f"Best Return: {results.get('best_return', 0):.2f}%")
            print(f"Average Win Rate: {results.get('avg_win_rate', 0):.1f}%")

if __name__ == "__main__":
    # Create required directories
    Path('/home/runner/work/viper-/viper-/logs').mkdir(exist_ok=True)
    Path('/home/runner/work/viper-/viper-/backtest_results').mkdir(exist_ok=True)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Real data backtesting interrupted by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        print(f"❌ Critical error: {e}")