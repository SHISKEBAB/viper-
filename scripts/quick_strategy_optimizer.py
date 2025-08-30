#!/usr/bin/env python3
"""
⚡ QUICK STRATEGY OPTIMIZER & BACKTESTER
=========================================

Fast optimization and backtesting with optimized parameter combinations.

Features:
✅ Quick parameter optimization
✅ Multiple strategy testing
✅ Performance analysis
✅ Best configuration identification
"""

import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QuickBacktestResult:
    """Quick backtest result"""
    strategy: str
    symbol: str
    timeframe: str
    parameters: Dict[str, Any]
    total_return: float
    sharpe_ratio: float
    win_rate: float
    max_drawdown: float
    total_trades: int
    profit_factor: float
    success: bool = True


class QuickStrategyOptimizer:
    """Quick strategy optimizer for fast results"""
    
    def __init__(self):
        self.console = Console()
        self.results_dir = Path("/tmp/quick_optimization_results")
        self.results_dir.mkdir(exist_ok=True)
    
    def generate_quick_data(self, symbol: str, timeframe: str, days: int = 30) -> pd.DataFrame:
        """Generate quick market data for testing"""
        
        # Shorter period for faster testing
        if timeframe == "15m":
            periods = days * 96  # 96 periods per day for 15m
        elif timeframe == "1h":
            periods = days * 24
        elif timeframe == "4h":
            periods = days * 6
        else:
            periods = days * 24
        
        # Base prices
        base_prices = {
            "BTCUSDT": 45000,
            "ETHUSDT": 2800,
            "ADAUSDT": 0.45
        }
        
        base_price = base_prices.get(symbol, 100)
        
        # Generate realistic price movement
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, periods)
        price_levels = base_price * np.cumprod(1 + returns)
        
        # Generate OHLC
        data = []
        start_time = datetime.now() - timedelta(days=days)
        
        for i in range(periods):
            close = price_levels[i]
            open_price = close * (1 + np.random.normal(0, 0.002))
            high = max(open_price, close) * (1 + np.random.uniform(0, 0.008))
            low = min(open_price, close) * (1 - np.random.uniform(0, 0.008))
            volume = np.random.uniform(50000, 200000)
            
            if timeframe == "15m":
                timestamp = start_time + timedelta(minutes=i*15)
            elif timeframe == "1h":
                timestamp = start_time + timedelta(hours=i)
            elif timeframe == "4h":
                timestamp = start_time + timedelta(hours=i*4)
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
    
    def quick_rsi_strategy(self, df: pd.DataFrame, rsi_period: int = 14, 
                          oversold: int = 30, overbought: int = 70) -> pd.DataFrame:
        """Quick RSI mean reversion strategy"""
        
        df = df.copy()
        
        # Calculate RSI
        df['rsi'] = talib.RSI(df['close'].values, timeperiod=rsi_period)
        
        # Generate signals
        df['signal'] = 0
        df.loc[df['rsi'] < oversold, 'signal'] = 1   # Buy
        df.loc[df['rsi'] > overbought, 'signal'] = -1  # Sell
        
        # Generate positions
        df['position'] = df['signal'].shift(1).fillna(0)
        
        return df
    
    def quick_ma_crossover(self, df: pd.DataFrame, fast_period: int = 10, 
                          slow_period: int = 30) -> pd.DataFrame:
        """Quick moving average crossover strategy"""
        
        df = df.copy()
        
        # Calculate moving averages
        df['sma_fast'] = talib.SMA(df['close'].values, timeperiod=fast_period)
        df['sma_slow'] = talib.SMA(df['close'].values, timeperiod=slow_period)
        
        # Generate signals
        df['signal'] = 0
        df.loc[df['sma_fast'] > df['sma_slow'], 'signal'] = 1   # Buy
        df.loc[df['sma_fast'] < df['sma_slow'], 'signal'] = -1  # Sell
        
        # Generate positions
        df['position'] = df['signal'].shift(1).fillna(0)
        
        return df
    
    def quick_bollinger_strategy(self, df: pd.DataFrame, bb_period: int = 20, 
                                bb_std: float = 2.0) -> pd.DataFrame:
        """Quick Bollinger Bands strategy"""
        
        df = df.copy()
        
        # Calculate Bollinger Bands
        upper, middle, lower = talib.BBANDS(
            df['close'].values,
            timeperiod=bb_period,
            nbdevup=bb_std,
            nbdevdn=bb_std,
            matype=0
        )
        
        df['bb_upper'] = upper
        df['bb_middle'] = middle
        df['bb_lower'] = lower
        
        # Generate signals
        df['signal'] = 0
        df.loc[df['close'] < df['bb_lower'], 'signal'] = 1   # Buy below lower band
        df.loc[df['close'] > df['bb_upper'], 'signal'] = -1  # Sell above upper band
        
        # Generate positions
        df['position'] = df['signal'].shift(1).fillna(0)
        
        return df
    
    def calculate_quick_performance(self, df: pd.DataFrame, stop_loss: float = 0.03, 
                                  take_profit: float = 0.06) -> Dict[str, float]:
        """Calculate performance metrics quickly"""
        
        # Calculate returns
        df['price_return'] = df['close'].pct_change()
        df['strategy_return'] = df['position'] * df['price_return']
        
        # Apply transaction costs
        df['position_change'] = df['position'].diff().abs()
        df['transaction_costs'] = df['position_change'] * 0.001  # 0.1% per trade
        df['net_return'] = df['strategy_return'] - df['transaction_costs']
        
        # Performance metrics
        total_return = (1 + df['net_return']).prod() - 1
        
        daily_returns = df['net_return'].dropna()
        if len(daily_returns) > 0 and daily_returns.std() > 0:
            sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        # Drawdown
        cumulative = (1 + daily_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Trade analysis
        positions = df['position'].values
        trades = []
        current_position = 0
        entry_price = 0
        
        for i, position in enumerate(positions):
            if position != current_position:
                if current_position != 0:  # Closing position
                    exit_price = df['close'].iloc[i]
                    trade_return = (exit_price - entry_price) / entry_price * current_position
                    trades.append(trade_return)
                
                if position != 0:  # Opening position
                    entry_price = df['close'].iloc[i]
                
                current_position = position
        
        if trades:
            winning_trades = len([t for t in trades if t > 0])
            total_trades = len(trades)
            win_rate = winning_trades / total_trades
            
            winning_amounts = [t for t in trades if t > 0]
            losing_amounts = [t for t in trades if t <= 0]
            
            if losing_amounts:
                profit_factor = sum(winning_amounts) / abs(sum(losing_amounts))
            else:
                profit_factor = float('inf') if winning_amounts else 0
        else:
            win_rate = 0
            total_trades = 0
            profit_factor = 0
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'max_drawdown': max_drawdown,
            'total_trades': total_trades,
            'profit_factor': profit_factor
        }
    
    def optimize_single_strategy(self, strategy_name: str, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Optimize a single strategy with quick parameter sweep"""
        
        self.console.print(f"⚡ Quick optimizing {strategy_name} for {symbol} on {timeframe}")
        
        # Generate market data
        df = self.generate_quick_data(symbol, timeframe)
        
        results = []
        
        # Define parameter ranges (smaller for speed)
        if strategy_name == "rsi_mean_reversion":
            param_combinations = [
                {'rsi_period': 14, 'oversold': 25, 'overbought': 75, 'stop_loss': 0.03, 'take_profit': 0.06},
                {'rsi_period': 14, 'oversold': 30, 'overbought': 70, 'stop_loss': 0.02, 'take_profit': 0.08},
                {'rsi_period': 21, 'oversold': 30, 'overbought': 70, 'stop_loss': 0.03, 'take_profit': 0.10},
                {'rsi_period': 21, 'oversold': 25, 'overbought': 75, 'stop_loss': 0.05, 'take_profit': 0.12},
            ]
        elif strategy_name == "ma_crossover":
            param_combinations = [
                {'fast_period': 10, 'slow_period': 30, 'stop_loss': 0.03, 'take_profit': 0.06},
                {'fast_period': 5, 'slow_period': 20, 'stop_loss': 0.02, 'take_profit': 0.08},
                {'fast_period': 15, 'slow_period': 50, 'stop_loss': 0.04, 'take_profit': 0.10},
            ]
        elif strategy_name == "bollinger_bands":
            param_combinations = [
                {'bb_period': 20, 'bb_std': 2.0, 'stop_loss': 0.03, 'take_profit': 0.06},
                {'bb_period': 25, 'bb_std': 2.5, 'stop_loss': 0.02, 'take_profit': 0.08},
                {'bb_period': 30, 'bb_std': 1.5, 'stop_loss': 0.04, 'take_profit': 0.10},
            ]
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        # Test each parameter combination
        for params in param_combinations:
            try:
                # Run strategy
                if strategy_name == "rsi_mean_reversion":
                    strategy_df = self.quick_rsi_strategy(
                        df, params['rsi_period'], params['oversold'], params['overbought']
                    )
                elif strategy_name == "ma_crossover":
                    strategy_df = self.quick_ma_crossover(
                        df, params['fast_period'], params['slow_period']
                    )
                elif strategy_name == "bollinger_bands":
                    strategy_df = self.quick_bollinger_strategy(
                        df, params['bb_period'], params['bb_std']
                    )
                
                # Calculate performance
                performance = self.calculate_quick_performance(
                    strategy_df, params['stop_loss'], params['take_profit']
                )
                
                result = QuickBacktestResult(
                    strategy=strategy_name,
                    symbol=symbol,
                    timeframe=timeframe,
                    parameters=params,
                    total_return=performance['total_return'],
                    sharpe_ratio=performance['sharpe_ratio'],
                    win_rate=performance['win_rate'],
                    max_drawdown=performance['max_drawdown'],
                    total_trades=performance['total_trades'],
                    profit_factor=performance['profit_factor'],
                    success=True
                )
                
                results.append(result)
                
            except Exception as e:
                logger.warning(f"Parameter combination failed: {e}")
                results.append(QuickBacktestResult(
                    strategy=strategy_name,
                    symbol=symbol,
                    timeframe=timeframe,
                    parameters=params,
                    total_return=0,
                    sharpe_ratio=0,
                    win_rate=0,
                    max_drawdown=-1,
                    total_trades=0,
                    profit_factor=0,
                    success=False
                ))
        
        # Analyze results
        successful_results = [r for r in results if r.success and r.total_trades > 0]
        
        if not successful_results:
            return {
                "error": "No successful backtests",
                "total_tests": len(results)
            }
        
        # Find best configurations
        best_return = max(successful_results, key=lambda x: x.total_return)
        best_sharpe = max(successful_results, key=lambda x: x.sharpe_ratio)
        best_win_rate = max(successful_results, key=lambda x: x.win_rate)
        
        # Calculate statistics
        avg_return = np.mean([r.total_return for r in successful_results])
        avg_sharpe = np.mean([r.sharpe_ratio for r in successful_results])
        avg_win_rate = np.mean([r.win_rate for r in successful_results])
        
        return {
            "strategy": strategy_name,
            "symbol": symbol,
            "timeframe": timeframe,
            "total_tests": len(results),
            "successful_tests": len(successful_results),
            "best_configurations": {
                "best_return": {
                    "total_return": best_return.total_return,
                    "sharpe_ratio": best_return.sharpe_ratio,
                    "win_rate": best_return.win_rate,
                    "max_drawdown": best_return.max_drawdown,
                    "parameters": best_return.parameters
                },
                "best_sharpe": {
                    "total_return": best_sharpe.total_return,
                    "sharpe_ratio": best_sharpe.sharpe_ratio,
                    "win_rate": best_sharpe.win_rate,
                    "max_drawdown": best_sharpe.max_drawdown,
                    "parameters": best_sharpe.parameters
                },
                "best_win_rate": {
                    "total_return": best_win_rate.total_return,
                    "sharpe_ratio": best_win_rate.sharpe_ratio,
                    "win_rate": best_win_rate.win_rate,
                    "max_drawdown": best_win_rate.max_drawdown,
                    "parameters": best_win_rate.parameters
                }
            },
            "average_performance": {
                "avg_return": avg_return,
                "avg_sharpe": avg_sharpe,
                "avg_win_rate": avg_win_rate
            }
        }
    
    def run_quick_optimization(self) -> Dict[str, Any]:
        """Run quick optimization on multiple strategies"""
        
        strategies = ["rsi_mean_reversion", "ma_crossover", "bollinger_bands"]
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        timeframes = ["15m", "1h"]
        
        all_results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            
            total_combinations = len(strategies) * len(symbols) * len(timeframes)
            task = progress.add_task("Optimizing strategies...", total=total_combinations)
            
            for strategy in strategies:
                all_results[strategy] = {}
                for symbol in symbols:
                    all_results[strategy][symbol] = {}
                    for timeframe in timeframes:
                        try:
                            result = self.optimize_single_strategy(strategy, symbol, timeframe)
                            all_results[strategy][symbol][timeframe] = result
                        except Exception as e:
                            all_results[strategy][symbol][timeframe] = {
                                "error": str(e)
                            }
                        progress.advance(task)
        
        return all_results
    
    def analyze_comprehensive_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze results across all strategies"""
        
        all_successful = []
        strategy_summaries = {}
        
        for strategy, strategy_results in results.items():
            strategy_performances = []
            
            for symbol, symbol_results in strategy_results.items():
                for timeframe, timeframe_results in symbol_results.items():
                    if "error" not in timeframe_results:
                        best_configs = timeframe_results.get("best_configurations", {})
                        
                        # Collect performance data
                        for config_type, config_data in best_configs.items():
                            performance_data = {
                                "strategy": strategy,
                                "symbol": symbol, 
                                "timeframe": timeframe,
                                "config_type": config_type,
                                **config_data
                            }
                            all_successful.append(performance_data)
                            strategy_performances.append(performance_data)
            
            # Strategy summary
            if strategy_performances:
                strategy_summaries[strategy] = {
                    "avg_return": np.mean([p['total_return'] for p in strategy_performances]),
                    "avg_sharpe": np.mean([p['sharpe_ratio'] for p in strategy_performances]),
                    "avg_win_rate": np.mean([p['win_rate'] for p in strategy_performances]),
                    "avg_max_drawdown": np.mean([p['max_drawdown'] for p in strategy_performances]),
                    "total_configurations": len(strategy_performances)
                }
        
        # Overall best performers
        if all_successful:
            best_overall_return = max(all_successful, key=lambda x: x['total_return'])
            best_overall_sharpe = max(all_successful, key=lambda x: x['sharpe_ratio'])
            best_overall_win_rate = max(all_successful, key=lambda x: x['win_rate'])
            
            overall_stats = {
                "total_configurations_tested": len(all_successful),
                "avg_return": np.mean([p['total_return'] for p in all_successful]),
                "avg_sharpe": np.mean([p['sharpe_ratio'] for p in all_successful]),
                "avg_win_rate": np.mean([p['win_rate'] for p in all_successful]),
                "best_overall": {
                    "best_return": best_overall_return,
                    "best_sharpe": best_overall_sharpe,
                    "best_win_rate": best_overall_win_rate
                }
            }
        else:
            overall_stats = {"error": "No successful configurations found"}
        
        return {
            "strategy_summaries": strategy_summaries,
            "overall_stats": overall_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def display_results(self, results: Dict[str, Any], analysis: Dict[str, Any]):
        """Display optimization results"""
        
        self.console.print("⚡ QUICK STRATEGY OPTIMIZATION RESULTS", style="bold cyan", justify="center")
        self.console.print("=" * 60, style="cyan", justify="center")
        
        # Strategy summary table
        summary_table = Table(title="Strategy Performance Summary", box=box.ROUNDED)
        summary_table.add_column("Strategy", style="cyan")
        summary_table.add_column("Avg Return", justify="right", style="green")
        summary_table.add_column("Avg Sharpe", justify="right", style="blue")
        summary_table.add_column("Avg Win Rate", justify="right", style="yellow")
        summary_table.add_column("Avg Max DD", justify="right", style="red")
        summary_table.add_column("Configs", justify="center")
        
        strategy_summaries = analysis.get("strategy_summaries", {})
        for strategy, summary in strategy_summaries.items():
            summary_table.add_row(
                strategy.replace("_", " ").title(),
                f"{summary['avg_return']:.2%}",
                f"{summary['avg_sharpe']:.2f}",
                f"{summary['avg_win_rate']:.1%}",
                f"{summary['avg_max_drawdown']:.2%}",
                str(summary['total_configurations'])
            )
        
        self.console.print(summary_table)
        
        # Best overall performers
        overall_stats = analysis.get("overall_stats", {})
        if "error" not in overall_stats:
            best_overall = overall_stats.get("best_overall", {})
            
            if "best_return" in best_overall:
                best_return = best_overall["best_return"]
                return_panel = Panel(
                    f"Strategy: {best_return['strategy']}\n"
                    f"Symbol: {best_return['symbol']}\n"
                    f"Timeframe: {best_return['timeframe']}\n"
                    f"Total Return: {best_return['total_return']:.2%}\n"
                    f"Win Rate: {best_return['win_rate']:.1%}\n"
                    f"Sharpe Ratio: {best_return['sharpe_ratio']:.2f}",
                    title="🏆 Best Return Configuration",
                    border_style="green"
                )
                self.console.print(return_panel)
            
            if "best_win_rate" in best_overall:
                best_wr = best_overall["best_win_rate"]
                win_rate_panel = Panel(
                    f"Strategy: {best_wr['strategy']}\n"
                    f"Symbol: {best_wr['symbol']}\n"
                    f"Timeframe: {best_wr['timeframe']}\n"
                    f"Win Rate: {best_wr['win_rate']:.1%}\n"
                    f"Total Return: {best_wr['total_return']:.2%}\n"
                    f"Sharpe Ratio: {best_wr['sharpe_ratio']:.2f}",
                    title="🎯 Best Win Rate Configuration",
                    border_style="blue"
                )
                self.console.print(win_rate_panel)


def main():
    """Main execution function"""
    
    console.print("⚡ QUICK STRATEGY OPTIMIZER & BACKTESTER", style="bold cyan", justify="center")
    console.print("Fast optimization and backtesting for trading strategies\n", justify="center")
    
    optimizer = QuickStrategyOptimizer()
    
    try:
        # Run optimization
        results = optimizer.run_quick_optimization()
        
        # Analyze results
        analysis = optimizer.analyze_comprehensive_results(results)
        
        # Display results
        optimizer.display_results(results, analysis)
        
        # Save results
        output_data = {
            "optimization_results": results,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
        results_file = optimizer.results_dir / "quick_optimization_results.json"
        with open(results_file, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        console.print(f"\n💾 Results saved to: {results_file}", style="green")
        console.print("⚡ Quick optimization completed successfully!", style="bold green")
        
        return 0
        
    except Exception as e:
        logger.error(f"Quick optimization failed: {e}")
        console.print(f"❌ Optimization failed: {e}", style="red")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())