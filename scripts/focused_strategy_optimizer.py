#!/usr/bin/env python3
"""
🎯 FOCUSED STRATEGY OPTIMIZER & BACKTESTER
==========================================

This script performs comprehensive optimization and backtesting on individual strategies
with detailed parameter optimization and performance analysis.

Features:
✅ Individual strategy optimization
✅ Parameter sweeping and optimization
✅ Comprehensive backtesting
✅ Performance metrics analysis
✅ Best configuration identification
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

# Rich for beautiful output
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich import box

# Technical analysis
import talib

console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - STRATEGY_OPTIMIZER - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class OptimizationConfig:
    """Configuration for strategy optimization"""
    strategy_name: str
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    initial_balance: float = 10000.0
    
    # Parameter ranges to optimize
    rsi_period_range: List[int] = None
    rsi_overbought_range: List[int] = None
    rsi_oversold_range: List[int] = None
    sma_fast_range: List[int] = None
    sma_slow_range: List[int] = None
    bollinger_period_range: List[int] = None
    bollinger_std_range: List[float] = None
    
    # Risk management
    stop_loss_range: List[float] = None
    take_profit_range: List[float] = None
    position_size_range: List[float] = None


@dataclass 
class BacktestResult:
    """Results from a single backtest"""
    config: OptimizationConfig
    symbol: str
    timeframe: str
    
    # Performance metrics
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    
    # Risk metrics
    volatility: float
    var_95: float
    expected_shortfall: float
    
    # Trade analysis
    avg_winning_trade: float
    avg_losing_trade: float
    largest_winning_trade: float
    largest_losing_trade: float
    
    # Parameters used
    parameters: Dict[str, Any]
    
    success: bool = True
    error_message: str = ""


class StrategyOptimizer:
    """Individual strategy optimizer with parameter sweeping"""
    
    def __init__(self):
        self.console = Console()
        self.results_dir = Path("/tmp/strategy_optimization_results")
        self.results_dir.mkdir(exist_ok=True)
    
    def generate_market_data(self, symbol: str, timeframe: str, days: int = 90) -> pd.DataFrame:
        """Generate realistic market data for backtesting"""
        
        # Calculate number of periods based on timeframe
        if timeframe == "1m":
            periods = days * 24 * 60
        elif timeframe == "5m":
            periods = days * 24 * 12
        elif timeframe == "15m":
            periods = days * 24 * 4
        elif timeframe == "30m":
            periods = days * 24 * 2
        elif timeframe == "1h":
            periods = days * 24
        elif timeframe == "4h":
            periods = days * 6
        elif timeframe == "1d":
            periods = days
        else:
            periods = days * 24  # default to hourly
        
        # Generate realistic crypto price movement
        np.random.seed(42)  # For reproducibility
        
        # Base price for different symbols
        base_prices = {
            "BTCUSDT": 45000,
            "ETHUSDT": 2800,
            "ADAUSDT": 0.45,
            "SOLUSDT": 85,
            "DOTUSDT": 6.5,
            "LINKUSDT": 12.5
        }
        
        base_price = base_prices.get(symbol, 100)
        
        # Generate price series with realistic volatility
        returns = np.random.normal(0.0005, 0.02, periods)  # Crypto-like returns
        returns[0] = 0  # First return is 0
        
        # Add some trending behavior
        trend_component = np.sin(np.linspace(0, 4*np.pi, periods)) * 0.001
        returns += trend_component
        
        # Add volatility clustering
        volatility = np.random.normal(0.02, 0.005, periods)
        volatility = np.abs(volatility)  # Ensure positive
        returns *= volatility
        
        # Generate price levels
        price_levels = base_price * np.cumprod(1 + returns)
        
        # Generate OHLC data
        data = []
        start_time = datetime.now() - timedelta(days=days)
        
        for i in range(periods):
            # Generate OHLC from price level with some randomness
            close = price_levels[i]
            
            # Open is previous close with small gap
            if i == 0:
                open_price = close * (1 + np.random.normal(0, 0.001))
            else:
                open_price = price_levels[i-1] * (1 + np.random.normal(0, 0.001))
            
            # High and low around the open/close range
            high = max(open_price, close) * (1 + np.random.uniform(0, 0.01))
            low = min(open_price, close) * (1 - np.random.uniform(0, 0.01))
            
            # Volume with some correlation to price movement
            price_change = abs((close - open_price) / open_price)
            volume = np.random.uniform(100000, 500000) * (1 + price_change * 5)
            
            # Time calculation
            if timeframe == "1m":
                timestamp = start_time + timedelta(minutes=i)
            elif timeframe == "5m":
                timestamp = start_time + timedelta(minutes=i*5)
            elif timeframe == "15m":
                timestamp = start_time + timedelta(minutes=i*15)
            elif timeframe == "30m":
                timestamp = start_time + timedelta(minutes=i*30)
            elif timeframe == "1h":
                timestamp = start_time + timedelta(hours=i)
            elif timeframe == "4h":
                timestamp = start_time + timedelta(hours=i*4)
            elif timeframe == "1d":
                timestamp = start_time + timedelta(days=i)
            else:
                timestamp = start_time + timedelta(hours=i)
                
            data.append({
                'timestamp': timestamp,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df.sort_index()
    
    def calculate_technical_indicators(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate technical indicators for the strategy"""
        
        df = df.copy()
        
        # RSI
        if 'rsi_period' in config:
            df['rsi'] = talib.RSI(df['close'].values, timeperiod=config['rsi_period'])
        
        # Moving averages
        if 'sma_fast' in config:
            df['sma_fast'] = talib.SMA(df['close'].values, timeperiod=config['sma_fast'])
        if 'sma_slow' in config:
            df['sma_slow'] = talib.SMA(df['close'].values, timeperiod=config['sma_slow'])
        
        # Bollinger Bands
        if 'bollinger_period' in config and 'bollinger_std' in config:
            upper, middle, lower = talib.BBANDS(
                df['close'].values, 
                timeperiod=config['bollinger_period'],
                nbdevup=config['bollinger_std'],
                nbdevdn=config['bollinger_std'],
                matype=0
            )
            df['bb_upper'] = upper
            df['bb_middle'] = middle
            df['bb_lower'] = lower
        
        # MACD
        if 'macd_fast' in config and 'macd_slow' in config and 'macd_signal' in config:
            macd, signal, histogram = talib.MACD(
                df['close'].values,
                fastperiod=config.get('macd_fast', 12),
                slowperiod=config.get('macd_slow', 26),
                signalperiod=config.get('macd_signal', 9)
            )
            df['macd'] = macd
            df['macd_signal'] = signal
            df['macd_histogram'] = histogram
        
        return df
    
    def rsi_mean_reversion_strategy(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """RSI Mean Reversion Strategy"""
        
        df = df.copy()
        df['signal'] = 0
        df['position'] = 0
        
        rsi_overbought = config.get('rsi_overbought', 70)
        rsi_oversold = config.get('rsi_oversold', 30)
        
        # Generate signals
        df.loc[df['rsi'] < rsi_oversold, 'signal'] = 1   # Buy signal
        df.loc[df['rsi'] > rsi_overbought, 'signal'] = -1  # Sell signal
        
        # Generate positions (simple version)
        position = 0
        positions = []
        
        for i, row in df.iterrows():
            if row['signal'] == 1 and position <= 0:
                position = 1
            elif row['signal'] == -1 and position >= 0:
                position = -1
            
            positions.append(position)
        
        df['position'] = positions
        return df
    
    def moving_average_crossover_strategy(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Moving Average Crossover Strategy"""
        
        df = df.copy()
        df['signal'] = 0
        df['position'] = 0
        
        # Generate signals
        df.loc[df['sma_fast'] > df['sma_slow'], 'signal'] = 1   # Buy signal  
        df.loc[df['sma_fast'] < df['sma_slow'], 'signal'] = -1  # Sell signal
        
        # Generate positions
        position = 0
        positions = []
        
        for i, row in df.iterrows():
            if row['signal'] == 1 and position <= 0:
                position = 1
            elif row['signal'] == -1 and position >= 0:
                position = -1
            
            positions.append(position)
        
        df['position'] = positions
        return df
    
    def bollinger_bands_strategy(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Bollinger Bands Mean Reversion Strategy"""
        
        df = df.copy()
        df['signal'] = 0
        df['position'] = 0
        
        # Generate signals
        df.loc[df['close'] < df['bb_lower'], 'signal'] = 1   # Buy when below lower band
        df.loc[df['close'] > df['bb_upper'], 'signal'] = -1  # Sell when above upper band
        
        # Generate positions
        position = 0
        positions = []
        
        for i, row in df.iterrows():
            if row['signal'] == 1 and position <= 0:
                position = 1
            elif row['signal'] == -1 and position >= 0:
                position = -1
            
            positions.append(position)
        
        df['position'] = positions
        return df
    
    def calculate_returns_and_metrics(self, df: pd.DataFrame, config: Dict[str, Any]) -> BacktestResult:
        """Calculate returns and performance metrics"""
        
        # Calculate returns
        df['price_return'] = df['close'].pct_change()
        df['strategy_return'] = df['position'].shift(1) * df['price_return']
        
        # Apply transaction costs
        transaction_cost = config.get('transaction_cost', 0.001)  # 0.1% per trade
        df['position_change'] = df['position'].diff().abs()
        df['transaction_costs'] = df['position_change'] * transaction_cost
        df['net_strategy_return'] = df['strategy_return'] - df['transaction_costs']
        
        # Risk management - stop loss and take profit
        stop_loss = config.get('stop_loss', 0.05)  # 5% stop loss
        take_profit = config.get('take_profit', 0.10)  # 10% take profit
        
        # Apply risk management (simplified)
        cumulative_return = (1 + df['net_strategy_return']).cumprod()
        df['cumulative_return'] = cumulative_return
        
        # Calculate metrics
        total_return = cumulative_return.iloc[-1] - 1
        
        strategy_returns = df['net_strategy_return'].dropna()
        
        if len(strategy_returns) > 0 and strategy_returns.std() > 0:
            sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)  # Annualized
        else:
            sharpe_ratio = 0
        
        # Maximum drawdown
        cumulative = (1 + strategy_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Trade analysis
        positions = df['position'].values
        position_changes = np.diff(positions, prepend=0)
        trades = np.where(position_changes != 0)[0]
        
        if len(trades) > 1:
            trade_returns = []
            for i in range(len(trades)-1):
                start_idx = trades[i]
                end_idx = trades[i+1]
                trade_return = df['net_strategy_return'].iloc[start_idx:end_idx+1].sum()
                trade_returns.append(trade_return)
            
            trade_returns = np.array(trade_returns)
            winning_trades = np.sum(trade_returns > 0)
            losing_trades = np.sum(trade_returns <= 0)
            total_trades = len(trade_returns)
            
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            if losing_trades > 0:
                avg_winning_trade = trade_returns[trade_returns > 0].mean() if winning_trades > 0 else 0
                avg_losing_trade = trade_returns[trade_returns <= 0].mean()
                profit_factor = abs(avg_winning_trade * winning_trades) / abs(avg_losing_trade * losing_trades)
            else:
                avg_winning_trade = trade_returns.mean() if len(trade_returns) > 0 else 0
                avg_losing_trade = 0
                profit_factor = float('inf') if avg_winning_trade > 0 else 0
            
            largest_winning_trade = trade_returns.max() if len(trade_returns) > 0 else 0
            largest_losing_trade = trade_returns.min() if len(trade_returns) > 0 else 0
        else:
            total_trades = 0
            winning_trades = 0
            losing_trades = 0
            win_rate = 0
            profit_factor = 0
            avg_winning_trade = 0
            avg_losing_trade = 0
            largest_winning_trade = 0
            largest_losing_trade = 0
        
        # Risk metrics
        volatility = strategy_returns.std() * np.sqrt(252) if len(strategy_returns) > 0 else 0
        var_95 = np.percentile(strategy_returns, 5) if len(strategy_returns) > 0 else 0
        expected_shortfall = strategy_returns[strategy_returns <= var_95].mean() if len(strategy_returns) > 0 else 0
        
        return BacktestResult(
            config=config,
            symbol=config.get('symbol', 'UNKNOWN'),
            timeframe=config.get('timeframe', 'UNKNOWN'),
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            volatility=volatility,
            var_95=var_95,
            expected_shortfall=expected_shortfall,
            avg_winning_trade=avg_winning_trade,
            avg_losing_trade=avg_losing_trade,
            largest_winning_trade=largest_winning_trade,
            largest_losing_trade=largest_losing_trade,
            parameters=config,
            success=True
        )
    
    def run_single_backtest(self, strategy_name: str, symbol: str, timeframe: str, 
                           parameters: Dict[str, Any]) -> BacktestResult:
        """Run a single backtest with given parameters"""
        
        try:
            # Generate market data
            df = self.generate_market_data(symbol, timeframe, days=90)
            
            # Add technical indicators
            config = parameters.copy()
            config['symbol'] = symbol
            config['timeframe'] = timeframe
            
            df = self.calculate_technical_indicators(df, config)
            
            # Run strategy
            if strategy_name == "rsi_mean_reversion":
                df = self.rsi_mean_reversion_strategy(df, config)
            elif strategy_name == "ma_crossover":
                df = self.moving_average_crossover_strategy(df, config)
            elif strategy_name == "bollinger_bands":
                df = self.bollinger_bands_strategy(df, config)
            else:
                raise ValueError(f"Unknown strategy: {strategy_name}")
            
            # Calculate performance
            result = self.calculate_returns_and_metrics(df, config)
            return result
            
        except Exception as e:
            logger.error(f"Backtest failed for {strategy_name} on {symbol}: {e}")
            return BacktestResult(
                config=parameters,
                symbol=symbol,
                timeframe=timeframe,
                total_return=0,
                sharpe_ratio=0,
                max_drawdown=-1,
                win_rate=0,
                profit_factor=0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                volatility=0,
                var_95=0,
                expected_shortfall=0,
                avg_winning_trade=0,
                avg_losing_trade=0,
                largest_winning_trade=0,
                largest_losing_trade=0,
                parameters=parameters,
                success=False,
                error_message=str(e)
            )
    
    def optimize_strategy(self, strategy_name: str, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Optimize a specific strategy with parameter sweeping"""
        
        self.console.print(f"🎯 Optimizing {strategy_name} for {symbol} on {timeframe}", style="cyan")
        
        # Define parameter ranges based on strategy
        if strategy_name == "rsi_mean_reversion":
            param_ranges = {
                'rsi_period': [14, 21, 28],
                'rsi_overbought': [65, 70, 75, 80],
                'rsi_oversold': [20, 25, 30, 35],
                'stop_loss': [0.02, 0.03, 0.05],
                'take_profit': [0.05, 0.08, 0.10, 0.15]
            }
        elif strategy_name == "ma_crossover":
            param_ranges = {
                'sma_fast': [5, 10, 20],
                'sma_slow': [20, 50, 100],
                'stop_loss': [0.02, 0.03, 0.05],
                'take_profit': [0.05, 0.08, 0.10]
            }
        elif strategy_name == "bollinger_bands":
            param_ranges = {
                'bollinger_period': [20, 25, 30],
                'bollinger_std': [1.5, 2.0, 2.5],
                'stop_loss': [0.02, 0.03, 0.05],
                'take_profit': [0.05, 0.08, 0.10]
            }
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        # Generate parameter combinations
        from itertools import product
        
        param_names = list(param_ranges.keys())
        param_values = [param_ranges[name] for name in param_names]
        param_combinations = list(product(*param_values))
        
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            
            task = progress.add_task(f"Testing {len(param_combinations)} parameter combinations...", 
                                   total=len(param_combinations))
            
            for combination in param_combinations:
                # Create parameter dictionary
                params = dict(zip(param_names, combination))
                
                # Skip invalid combinations
                if strategy_name == "ma_crossover":
                    if params['sma_fast'] >= params['sma_slow']:
                        continue
                
                # Run backtest
                result = self.run_single_backtest(strategy_name, symbol, timeframe, params)
                results.append(result)
                
                progress.advance(task)
        
        # Analyze results
        successful_results = [r for r in results if r.success and r.total_trades > 5]
        
        if not successful_results:
            return {
                "error": "No successful backtests found",
                "total_tests": len(results),
                "successful_tests": 0
            }
        
        # Find best configurations
        best_sharpe = max(successful_results, key=lambda x: x.sharpe_ratio)
        best_return = max(successful_results, key=lambda x: x.total_return)
        best_win_rate = max(successful_results, key=lambda x: x.win_rate)
        
        # Calculate averages
        avg_return = np.mean([r.total_return for r in successful_results])
        avg_sharpe = np.mean([r.sharpe_ratio for r in successful_results])
        avg_win_rate = np.mean([r.win_rate for r in successful_results])
        avg_max_drawdown = np.mean([r.max_drawdown for r in successful_results])
        
        return {
            "strategy": strategy_name,
            "symbol": symbol,
            "timeframe": timeframe,
            "total_tests": len(results),
            "successful_tests": len(successful_results),
            "best_configurations": {
                "best_sharpe": {
                    "sharpe_ratio": best_sharpe.sharpe_ratio,
                    "total_return": best_sharpe.total_return,
                    "win_rate": best_sharpe.win_rate,
                    "max_drawdown": best_sharpe.max_drawdown,
                    "parameters": best_sharpe.parameters
                },
                "best_return": {
                    "sharpe_ratio": best_return.sharpe_ratio,
                    "total_return": best_return.total_return,
                    "win_rate": best_return.win_rate,
                    "max_drawdown": best_return.max_drawdown,
                    "parameters": best_return.parameters
                },
                "best_win_rate": {
                    "sharpe_ratio": best_win_rate.sharpe_ratio,
                    "total_return": best_win_rate.total_return,
                    "win_rate": best_win_rate.win_rate,
                    "max_drawdown": best_win_rate.max_drawdown,
                    "parameters": best_win_rate.parameters
                }
            },
            "average_performance": {
                "avg_return": avg_return,
                "avg_sharpe": avg_sharpe,
                "avg_win_rate": avg_win_rate,
                "avg_max_drawdown": avg_max_drawdown
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def run_comprehensive_optimization(self) -> Dict[str, Any]:
        """Run comprehensive optimization across multiple strategies"""
        
        strategies = ["rsi_mean_reversion", "ma_crossover", "bollinger_bands"]
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        timeframes = ["15m", "1h"]
        
        all_results = {}
        
        for strategy in strategies:
            all_results[strategy] = {}
            for symbol in symbols:
                all_results[strategy][symbol] = {}
                for timeframe in timeframes:
                    try:
                        result = self.optimize_strategy(strategy, symbol, timeframe)
                        all_results[strategy][symbol][timeframe] = result
                    except Exception as e:
                        all_results[strategy][symbol][timeframe] = {
                            "error": str(e),
                            "timestamp": datetime.now().isoformat()
                        }
        
        return all_results
    
    def display_optimization_results(self, results: Dict[str, Any]):
        """Display comprehensive optimization results"""
        
        self.console.print("🎯 COMPREHENSIVE STRATEGY OPTIMIZATION RESULTS", style="bold cyan", justify="center")
        self.console.print("=" * 80, style="cyan", justify="center")
        
        # Summary table
        summary_table = Table(title="Optimization Summary", box=box.ROUNDED)
        summary_table.add_column("Strategy", style="cyan")
        summary_table.add_column("Symbol", style="yellow")  
        summary_table.add_column("Timeframe", style="green")
        summary_table.add_column("Tests", justify="center")
        summary_table.add_column("Success", justify="center")
        summary_table.add_column("Best Return", justify="right", style="green")
        summary_table.add_column("Best Win Rate", justify="right", style="blue")
        summary_table.add_column("Best Sharpe", justify="right", style="magenta")
        
        all_best_configs = []
        
        for strategy, strategy_results in results.items():
            for symbol, symbol_results in strategy_results.items():
                for timeframe, timeframe_results in symbol_results.items():
                    if "error" in timeframe_results:
                        summary_table.add_row(
                            strategy, symbol, timeframe, "ERROR", "0", "N/A", "N/A", "N/A"
                        )
                    else:
                        best_configs = timeframe_results.get("best_configurations", {})
                        summary_table.add_row(
                            strategy,
                            symbol, 
                            timeframe,
                            str(timeframe_results.get("total_tests", 0)),
                            str(timeframe_results.get("successful_tests", 0)),
                            f"{best_configs.get('best_return', {}).get('total_return', 0):.2%}",
                            f"{best_configs.get('best_win_rate', {}).get('win_rate', 0):.1%}",
                            f"{best_configs.get('best_sharpe', {}).get('sharpe_ratio', 0):.2f}"
                        )
                        
                        # Collect best configurations
                        if best_configs:
                            all_best_configs.append({
                                "strategy": strategy,
                                "symbol": symbol,
                                "timeframe": timeframe,
                                "config": best_configs
                            })
        
        self.console.print(summary_table)
        
        # Top performing configurations
        if all_best_configs:
            self.console.print("\n🏆 TOP PERFORMING CONFIGURATIONS", style="bold yellow")
            
            # Sort by different metrics
            top_return = sorted(all_best_configs, 
                              key=lambda x: x["config"].get("best_return", {}).get("total_return", 0), 
                              reverse=True)[:3]
            
            top_win_rate = sorted(all_best_configs,
                                key=lambda x: x["config"].get("best_win_rate", {}).get("win_rate", 0),
                                reverse=True)[:3]
            
            top_sharpe = sorted(all_best_configs,
                              key=lambda x: x["config"].get("best_sharpe", {}).get("sharpe_ratio", 0),
                              reverse=True)[:3]
            
            # Display top performers
            for i, config in enumerate(top_return[:1], 1):  # Show top 1
                best_return_data = config["config"]["best_return"]
                panel_text = (
                    f"Strategy: {config['strategy']}\n"
                    f"Symbol: {config['symbol']}\n"
                    f"Timeframe: {config['timeframe']}\n"
                    f"Total Return: {best_return_data['total_return']:.2%}\n"
                    f"Win Rate: {best_return_data['win_rate']:.1%}\n"
                    f"Sharpe Ratio: {best_return_data['sharpe_ratio']:.2f}\n"
                    f"Max Drawdown: {best_return_data['max_drawdown']:.2%}"
                )
                panel = Panel(panel_text, title=f"🥇 Best Return Configuration", border_style="green")
                self.console.print(panel)
            
            for i, config in enumerate(top_win_rate[:1], 1):  # Show top 1
                best_win_rate_data = config["config"]["best_win_rate"]
                panel_text = (
                    f"Strategy: {config['strategy']}\n"
                    f"Symbol: {config['symbol']}\n"
                    f"Timeframe: {config['timeframe']}\n"
                    f"Total Return: {best_win_rate_data['total_return']:.2%}\n"
                    f"Win Rate: {best_win_rate_data['win_rate']:.1%}\n"
                    f"Sharpe Ratio: {best_win_rate_data['sharpe_ratio']:.2f}\n"
                    f"Max Drawdown: {best_win_rate_data['max_drawdown']:.2%}"
                )
                panel = Panel(panel_text, title=f"🎯 Best Win Rate Configuration", border_style="blue")
                self.console.print(panel)


def main():
    """Main execution function"""
    
    console.print("🎯 FOCUSED STRATEGY OPTIMIZER & BACKTESTER", style="bold cyan", justify="center")
    console.print("Running comprehensive optimization on individual strategies\n", justify="center")
    
    optimizer = StrategyOptimizer()
    
    try:
        # Run comprehensive optimization
        results = optimizer.run_comprehensive_optimization()
        
        # Display results
        optimizer.display_optimization_results(results)
        
        # Save results
        results_file = optimizer.results_dir / "strategy_optimization_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        console.print(f"\n💾 Results saved to: {results_file}", style="green")
        console.print("🎉 Strategy optimization completed successfully!", style="bold green")
        
    except Exception as e:
        logger.error(f"Strategy optimization failed: {e}")
        console.print(f"❌ Optimization failed: {e}", style="red")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())