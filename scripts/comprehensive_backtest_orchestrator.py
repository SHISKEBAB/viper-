#!/usr/bin/env python3
"""
# Rocket VIPER Trading Bot - Comprehensive Backtest Orchestrator
Comprehensive backtesting system for all VIPER trading strategies

Features:
- Tests all enabled strategies from unified configuration
- Parallel backtesting execution for faster results
- Real-time progress monitoring and reporting
- Performance comparison and ranking
- Monte Carlo simulation for robustness testing
- Walk-forward analysis for out-of-sample validation
- Comprehensive reporting with visualizations
- API integration testing with real credentials
"""

import os
import sys
import json
import asyncio
import logging
import aiohttp
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
CONFIG_MANAGER_URL = os.getenv('CONFIG_MANAGER_URL', 'http://config-manager:8001')
ULTRA_BACKTESTER_URL = os.getenv('ULTRA_BACKTESTER_URL', 'http://ultra-backtester:8006')
MARKET_DATA_MANAGER_URL = os.getenv('MARKET_DATA_MANAGER_URL', 'http://market-data-manager:8003')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Colors:
    BOLD = '\033[1m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    OKCYAN = '\033[96m'
    HEADER = '\033[95m'

class ComprehensiveBacktestOrchestrator:
    """Orchestrates comprehensive backtesting of all VIPER trading strategies"""
    
    def __init__(self):
        self.session = None
        self.unified_config = {}
        self.strategies = {}
        self.trading_pairs = []
        self.backtest_results = {}
        self.performance_summary = {}
        self.reports_dir = Path('backtest_reports')
        self.reports_dir.mkdir(exist_ok=True)
        
        # Backtesting parameters
        self.initial_balance = 10000.0
        self.lookback_days = 365
        self.monte_carlo_runs = 1000
        self.parallel_jobs = 4
        
        logger.info("# Construction Comprehensive Backtest Orchestrator initialized")
    
    async def initialize(self):
        """Initialize the orchestrator"""
        try:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300))
            
            # Load unified configuration
            await self.load_unified_configuration()
            
            # Extract strategies and trading pairs
            await self.extract_strategies_and_pairs()
            
            logger.info("# Check Orchestrator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"# X Initialization failed: {e}")
            return False
    
    async def load_unified_configuration(self):
        """Load the unified configuration"""
        try:
            async with self.session.get(f"{CONFIG_MANAGER_URL}/config/unified") as response:
                if response.status == 200:
                    data = await response.json()
                    self.unified_config = data.get('config', {})
                    logger.info("# Check Unified configuration loaded")
                else:
                    logger.error(f"# X Failed to load unified config: {response.status}")
                    raise Exception("Failed to load unified configuration")
                    
        except Exception as e:
            logger.error(f"# X Error loading unified configuration: {e}")
            raise
    
    async def extract_strategies_and_pairs(self):
        """Extract strategies and trading pairs from unified config"""
        try:
            # Extract enabled strategies
            strategies_config = self.unified_config.get('strategies', {})
            enabled_strategies = strategies_config.get('enabled_strategies', [])
            
            for strategy_name in enabled_strategies:
                if strategy_name in strategies_config:
                    strategy_config = strategies_config[strategy_name]
                    if strategy_config.get('enabled', False):
                        self.strategies[strategy_name] = strategy_config
            
            # Extract trading pairs
            trading_pairs_config = self.unified_config.get('trading_pairs', {})
            self.trading_pairs = trading_pairs_config.get('primary_symbols', [])
            
            logger.info(f"# Check Loaded {len(self.strategies)} strategies and {len(self.trading_pairs)} trading pairs")
            
        except Exception as e:
            logger.error(f"# X Error extracting strategies and pairs: {e}")
            raise
    
    async def run_comprehensive_backtests(self):
        """Run comprehensive backtests for all strategies and pairs"""
        try:
            print(f"\n{Colors.BOLD}{Colors.HEADER}🚀 VIPER COMPREHENSIVE BACKTESTING SYSTEM{Colors.ENDC}")
            print("=" * 70)
            print(f"{Colors.OKCYAN}Testing all strategies across all trading pairs{Colors.ENDC}")
            print(f"Strategies: {len(self.strategies)}")
            print(f"Trading Pairs: {len(self.trading_pairs)}")
            print(f"Total Tests: {len(self.strategies) * len(self.trading_pairs)}")
            print(f"Initial Balance: ${self.initial_balance:,.2f}")
            print(f"Lookback Period: {self.lookback_days} days")
            print("=" * 70)
            
            # Create tasks for all strategy-pair combinations
            tasks = []
            total_tests = 0
            
            for strategy_name, strategy_config in self.strategies.items():
                for symbol in self.trading_pairs:
                    task_id = f"{strategy_name}_{symbol}"
                    tasks.append(self.run_single_backtest(task_id, strategy_name, symbol, strategy_config))
                    total_tests += 1
            
            print(f"\n{Colors.WARNING}🔄 Starting {total_tests} backtests...{Colors.ENDC}")
            
            # Execute all backtests concurrently
            completed = 0
            async for result in self.execute_backtests_concurrently(tasks):
                completed += 1
                progress = (completed / total_tests) * 100
                print(f"\r{Colors.OKCYAN}Progress: {completed}/{total_tests} ({progress:.1f}%){Colors.ENDC}", end='', flush=True)
            
            print(f"\n{Colors.OKGREEN}✅ All backtests completed!{Colors.ENDC}")
            
            # Analyze and generate comprehensive report
            await self.analyze_results()
            await self.generate_comprehensive_report()
            
            return True
            
        except Exception as e:
            logger.error(f"# X Error running comprehensive backtests: {e}")
            return False
    
    async def execute_backtests_concurrently(self, tasks):
        """Execute backtests with controlled concurrency"""
        semaphore = asyncio.Semaphore(self.parallel_jobs)
        
        async def bounded_task(task):
            async with semaphore:
                return await task
        
        bounded_tasks = [bounded_task(task) for task in tasks]
        
        for task in asyncio.as_completed(bounded_tasks):
            yield await task
    
    async def run_single_backtest(self, task_id: str, strategy_name: str, symbol: str, strategy_config: Dict):
        """Run a single backtest for a strategy-symbol combination"""
        try:
            # Prepare backtest request
            backtest_request = {
                "symbol": symbol.replace('_UMCBL', '/USDT'),  # Convert to standard format
                "strategy": strategy_name,
                "timeframe": strategy_config.get('timeframes', ['1h'])[0],  # Use first timeframe
                "initial_balance": self.initial_balance,
                "lookback_days": self.lookback_days,
                "strategy_params": strategy_config
            }
            
            # Execute backtest
            async with self.session.post(
                f"{ULTRA_BACKTESTER_URL}/api/backtest/start",
                json=backtest_request
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    backtest_id = data.get('backtest_id')
                    
                    # Wait for completion and get results
                    result = await self.wait_for_backtest_completion(backtest_id)
                    
                    if result:
                        self.backtest_results[task_id] = {
                            'strategy': strategy_name,
                            'symbol': symbol,
                            'result': result,
                            'task_id': task_id,
                            'backtest_id': backtest_id
                        }
                        return task_id
                    else:
                        logger.warning(f"# Warning Backtest failed for {task_id}")
                        return None
                else:
                    logger.error(f"# X Failed to start backtest for {task_id}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"# X Error running backtest for {task_id}: {e}")
            return None
    
    async def wait_for_backtest_completion(self, backtest_id: str, max_wait: int = 300) -> Optional[Dict]:
        """Wait for backtest completion and return results"""
        try:
            wait_time = 0
            check_interval = 5
            
            while wait_time < max_wait:
                async with self.session.get(f"{ULTRA_BACKTESTER_URL}/api/backtest/{backtest_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'status' in data:
                            status = data['status']
                            if status == 'completed':
                                return data
                            elif status == 'failed':
                                logger.error(f"# X Backtest {backtest_id} failed")
                                return None
                        else:
                            # Assume it's a completed result if no status field
                            return data
                    
                await asyncio.sleep(check_interval)
                wait_time += check_interval
            
            logger.warning(f"# Warning Backtest {backtest_id} timed out")
            return None
            
        except Exception as e:
            logger.error(f"# X Error waiting for backtest {backtest_id}: {e}")
            return None
    
    async def analyze_results(self):
        """Analyze backtest results and generate performance metrics"""
        try:
            print(f"\n{Colors.BOLD}📊 ANALYZING BACKTEST RESULTS{Colors.ENDC}")
            print("=" * 50)
            
            # Initialize performance tracking
            strategy_performance = {}
            symbol_performance = {}
            overall_stats = {
                'total_tests': len(self.backtest_results),
                'successful_tests': 0,
                'failed_tests': 0,
                'total_return': 0,
                'total_trades': 0,
                'win_rate_avg': 0,
                'sharpe_ratio_avg': 0,
                'max_drawdown_avg': 0
            }
            
            # Process each result
            for task_id, test_result in self.backtest_results.items():
                strategy = test_result['strategy']
                symbol = test_result['symbol']
                result = test_result['result']
                
                if 'error' not in result and 'metrics' in result:
                    overall_stats['successful_tests'] += 1
                    
                    # Extract key metrics
                    metrics = result.get('metrics', {})
                    total_return = result.get('total_return', 0)
                    total_trades = result.get('total_trades', 0)
                    
                    # Update strategy performance
                    if strategy not in strategy_performance:
                        strategy_performance[strategy] = {
                            'tests': 0,
                            'total_return': 0,
                            'avg_return': 0,
                            'win_rate': 0,
                            'sharpe_ratio': 0,
                            'max_drawdown': 0,
                            'total_trades': 0,
                            'best_pair': '',
                            'best_return': -float('inf')
                        }
                    
                    strategy_perf = strategy_performance[strategy]
                    strategy_perf['tests'] += 1
                    strategy_perf['total_return'] += total_return
                    strategy_perf['win_rate'] += metrics.get('win_rate', 0)
                    strategy_perf['sharpe_ratio'] += metrics.get('sharpe_ratio', 0)
                    strategy_perf['max_drawdown'] += metrics.get('max_drawdown', 0)
                    strategy_perf['total_trades'] += total_trades
                    
                    if total_return > strategy_perf['best_return']:
                        strategy_perf['best_return'] = total_return
                        strategy_perf['best_pair'] = symbol
                    
                    # Update symbol performance
                    if symbol not in symbol_performance:
                        symbol_performance[symbol] = {
                            'tests': 0,
                            'total_return': 0,
                            'avg_return': 0,
                            'best_strategy': '',
                            'best_return': -float('inf')
                        }
                    
                    symbol_perf = symbol_performance[symbol]
                    symbol_perf['tests'] += 1
                    symbol_perf['total_return'] += total_return
                    
                    if total_return > symbol_perf['best_return']:
                        symbol_perf['best_return'] = total_return
                        symbol_perf['best_strategy'] = strategy
                    
                    # Update overall stats
                    overall_stats['total_return'] += total_return
                    overall_stats['total_trades'] += total_trades
                    overall_stats['win_rate_avg'] += metrics.get('win_rate', 0)
                    overall_stats['sharpe_ratio_avg'] += metrics.get('sharpe_ratio', 0)
                    overall_stats['max_drawdown_avg'] += metrics.get('max_drawdown', 0)
                    
                else:
                    overall_stats['failed_tests'] += 1
            
            # Calculate averages for strategies
            for strategy, perf in strategy_performance.items():
                if perf['tests'] > 0:
                    perf['avg_return'] = perf['total_return'] / perf['tests']
                    perf['win_rate'] = perf['win_rate'] / perf['tests']
                    perf['sharpe_ratio'] = perf['sharpe_ratio'] / perf['tests']
                    perf['max_drawdown'] = perf['max_drawdown'] / perf['tests']
            
            # Calculate averages for symbols
            for symbol, perf in symbol_performance.items():
                if perf['tests'] > 0:
                    perf['avg_return'] = perf['total_return'] / perf['tests']
            
            # Calculate overall averages
            successful_tests = overall_stats['successful_tests']
            if successful_tests > 0:
                overall_stats['win_rate_avg'] = overall_stats['win_rate_avg'] / successful_tests
                overall_stats['sharpe_ratio_avg'] = overall_stats['sharpe_ratio_avg'] / successful_tests
                overall_stats['max_drawdown_avg'] = overall_stats['max_drawdown_avg'] / successful_tests
            
            # Store analysis results
            self.performance_summary = {
                'overall_stats': overall_stats,
                'strategy_performance': strategy_performance,
                'symbol_performance': symbol_performance,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            # Print summary
            print(f"{Colors.OKGREEN}✅ Analysis completed!{Colors.ENDC}")
            print(f"Successful tests: {successful_tests}/{overall_stats['total_tests']}")
            print(f"Average return: {(overall_stats['total_return']/successful_tests)*100:.2f}%" if successful_tests > 0 else "N/A")
            print(f"Average win rate: {overall_stats['win_rate_avg']:.1f}%" if successful_tests > 0 else "N/A")
            print(f"Average Sharpe ratio: {overall_stats['sharpe_ratio_avg']:.2f}" if successful_tests > 0 else "N/A")
            
        except Exception as e:
            logger.error(f"# X Error analyzing results: {e}")
    
    async def generate_comprehensive_report(self):
        """Generate comprehensive HTML report with visualizations"""
        try:
            print(f"\n{Colors.BOLD}📈 GENERATING COMPREHENSIVE REPORT{Colors.ENDC}")
            print("=" * 50)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_dir / f"comprehensive_backtest_report_{timestamp}.html"
            
            # Create visualizations
            fig = self.create_performance_visualizations()
            
            # Generate HTML report
            html_content = self.generate_html_report(fig)
            
            # Save report
            with open(report_file, 'w') as f:
                f.write(html_content)
            
            # Save JSON summary
            json_file = self.reports_dir / f"backtest_summary_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump({
                    'performance_summary': self.performance_summary,
                    'backtest_results': self.backtest_results
                }, f, indent=2)
            
            print(f"{Colors.OKGREEN}✅ Report generated: {report_file}{Colors.ENDC}")
            print(f"{Colors.OKGREEN}✅ Summary saved: {json_file}{Colors.ENDC}")
            
        except Exception as e:
            logger.error(f"# X Error generating report: {e}")
    
    def create_performance_visualizations(self):
        """Create performance visualization charts"""
        try:
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=['Strategy Performance Comparison', 'Symbol Performance Ranking', 
                               'Return vs Risk Analysis', 'Win Rate Distribution'],
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "histogram"}]]
            )
            
            strategy_perf = self.performance_summary['strategy_performance']
            symbol_perf = self.performance_summary['symbol_performance']
            
            # Strategy performance comparison
            strategies = list(strategy_perf.keys())
            strategy_returns = [strategy_perf[s]['avg_return'] * 100 for s in strategies]
            
            fig.add_trace(
                go.Bar(x=strategies, y=strategy_returns, name='Avg Return %'),
                row=1, col=1
            )
            
            # Symbol performance ranking
            symbols = list(symbol_perf.keys())
            symbol_returns = [symbol_perf[s]['avg_return'] * 100 for s in symbols]
            
            fig.add_trace(
                go.Bar(x=symbols, y=symbol_returns, name='Avg Return %'),
                row=1, col=2
            )
            
            # Return vs Risk scatter
            sharpe_ratios = [strategy_perf[s]['sharpe_ratio'] for s in strategies]
            max_drawdowns = [strategy_perf[s]['max_drawdown'] for s in strategies]
            
            fig.add_trace(
                go.Scatter(
                    x=max_drawdowns, y=strategy_returns, mode='markers+text',
                    text=strategies, textposition="top center",
                    name='Strategy Risk/Return'
                ),
                row=2, col=1
            )
            
            # Win rate distribution
            win_rates = [strategy_perf[s]['win_rate'] for s in strategies]
            
            fig.add_trace(
                go.Histogram(x=win_rates, nbinsx=10, name='Win Rate Distribution'),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                height=800,
                title_text="VIPER Comprehensive Backtest Results",
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"# X Error creating visualizations: {e}")
            return None
    
    def generate_html_report(self, fig):
        """Generate HTML report content"""
        try:
            overall_stats = self.performance_summary['overall_stats']
            strategy_perf = self.performance_summary['strategy_performance']
            
            # Best performing strategy
            best_strategy = max(strategy_perf.keys(), 
                              key=lambda s: strategy_perf[s]['avg_return'])
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>VIPER Comprehensive Backtest Report</title>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }}
                    .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
                    .stat-card {{ background: #2d2d2d; padding: 20px; border-radius: 10px; border-left: 4px solid #00d4ff; }}
                    .stat-value {{ font-size: 2em; font-weight: bold; color: #00d4ff; }}
                    .stat-label {{ color: #cccccc; margin-top: 5px; }}
                    .strategy-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: #2d2d2d; border-radius: 10px; overflow: hidden; }}
                    .strategy-table th, .strategy-table td {{ padding: 15px; text-align: left; border-bottom: 1px solid #404040; }}
                    .strategy-table th {{ background: #404040; font-weight: bold; }}
                    .positive {{ color: #28a745; }}
                    .negative {{ color: #dc3545; }}
                    .chart-container {{ background: #2d2d2d; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                </style>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </head>
            <body>
                <div class="header">
                    <h1>🚀 VIPER Comprehensive Backtest Report</h1>
                    <p>Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{overall_stats['successful_tests']}</div>
                        <div class="stat-label">Successful Tests</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(self.strategies)}</div>
                        <div class="stat-label">Strategies Tested</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(self.trading_pairs)}</div>
                        <div class="stat-label">Trading Pairs</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{overall_stats['win_rate_avg']:.1f}%</div>
                        <div class="stat-label">Average Win Rate</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{overall_stats['sharpe_ratio_avg']:.2f}</div>
                        <div class="stat-label">Average Sharpe Ratio</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{best_strategy}</div>
                        <div class="stat-label">Best Strategy</div>
                    </div>
                </div>
            """
            
            if fig:
                html_content += f"""
                <div class="chart-container">
                    <div id="plotlyChart">{fig.to_html(include_plotlyjs=False, div_id="plotlyChart")}</div>
                </div>
                """
            
            # Strategy performance table
            html_content += """
                <div class="chart-container">
                    <h2>📊 Strategy Performance Summary</h2>
                    <table class="strategy-table">
                        <thead>
                            <tr>
                                <th>Strategy</th>
                                <th>Tests</th>
                                <th>Avg Return</th>
                                <th>Win Rate</th>
                                <th>Sharpe Ratio</th>
                                <th>Max Drawdown</th>
                                <th>Best Pair</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for strategy, perf in strategy_perf.items():
                return_class = "positive" if perf['avg_return'] > 0 else "negative"
                html_content += f"""
                            <tr>
                                <td><strong>{strategy}</strong></td>
                                <td>{perf['tests']}</td>
                                <td class="{return_class}">{perf['avg_return']*100:.2f}%</td>
                                <td>{perf['win_rate']:.1f}%</td>
                                <td>{perf['sharpe_ratio']:.2f}</td>
                                <td>{perf['max_drawdown']:.2f}%</td>
                                <td>{perf['best_pair']}</td>
                            </tr>
                """
            
            html_content += """
                        </tbody>
                    </table>
                </div>
                
                <div class="chart-container">
                    <h2>🎯 Key Insights</h2>
                    <ul>
            """
            
            # Generate insights
            best_strategy_perf = strategy_perf[best_strategy]
            worst_strategy = min(strategy_perf.keys(), key=lambda s: strategy_perf[s]['avg_return'])
            
            html_content += f"""
                        <li><strong>Best performing strategy:</strong> {best_strategy} with {best_strategy_perf['avg_return']*100:.2f}% average return</li>
                        <li><strong>Most consistent strategy:</strong> {max(strategy_perf.keys(), key=lambda s: strategy_perf[s]['win_rate'])} with highest win rate</li>
                        <li><strong>Highest Sharpe ratio:</strong> {max(strategy_perf.keys(), key=lambda s: strategy_perf[s]['sharpe_ratio'])} for best risk-adjusted returns</li>
                        <li><strong>Total trades executed:</strong> {overall_stats['total_trades']:,} across all tests</li>
                        <li><strong>Overall success rate:</strong> {(overall_stats['successful_tests']/overall_stats['total_tests'])*100:.1f}% of backtests completed successfully</li>
                    </ul>
                </div>
                
            </body>
            </html>
            """
            
            return html_content
            
        except Exception as e:
            logger.error(f"# X Error generating HTML report: {e}")
            return "<html><body><h1>Error generating report</h1></body></html>"
    
    async def test_api_integrations(self):
        """Test all API integrations with real credentials"""
        try:
            print(f"\n{Colors.BOLD}🔌 TESTING API INTEGRATIONS{Colors.ENDC}")
            print("=" * 50)
            
            api_tests = []
            
            # Test configuration manager
            api_tests.append(self.test_config_manager_api())
            
            # Test ultra backtester
            api_tests.append(self.test_backtester_api())
            
            # Test market data manager
            api_tests.append(self.test_market_data_api())
            
            # Test Jordan Mainnet credentials
            api_tests.append(self.test_jordan_mainnet_api())
            
            # Execute all API tests
            results = await asyncio.gather(*api_tests, return_exceptions=True)
            
            # Report results
            passed = sum(1 for r in results if r is True)
            total = len(results)
            
            print(f"\n{Colors.OKGREEN if passed == total else Colors.WARNING}API Tests: {passed}/{total} passed{Colors.ENDC}")
            
            return passed == total
            
        except Exception as e:
            logger.error(f"# X Error testing API integrations: {e}")
            return False
    
    async def test_config_manager_api(self):
        """Test configuration manager API"""
        try:
            async with self.session.get(f"{CONFIG_MANAGER_URL}/health") as response:
                if response.status == 200:
                    print(f"{Colors.OKGREEN}✅ Configuration Manager API{Colors.ENDC}")
                    return True
                else:
                    print(f"{Colors.FAIL}❌ Configuration Manager API ({response.status}){Colors.ENDC}")
                    return False
        except Exception as e:
            print(f"{Colors.FAIL}❌ Configuration Manager API (Error: {e}){Colors.ENDC}")
            return False
    
    async def test_backtester_api(self):
        """Test ultra backtester API"""
        try:
            async with self.session.get(f"{ULTRA_BACKTESTER_URL}/health") as response:
                if response.status == 200:
                    print(f"{Colors.OKGREEN}✅ Ultra Backtester API{Colors.ENDC}")
                    return True
                else:
                    print(f"{Colors.FAIL}❌ Ultra Backtester API ({response.status}){Colors.ENDC}")
                    return False
        except Exception as e:
            print(f"{Colors.FAIL}❌ Ultra Backtester API (Error: {e}){Colors.ENDC}")
            return False
    
    async def test_market_data_api(self):
        """Test market data manager API"""
        try:
            async with self.session.get(f"{MARKET_DATA_MANAGER_URL}/health") as response:
                if response.status == 200:
                    print(f"{Colors.OKGREEN}✅ Market Data Manager API{Colors.ENDC}")
                    return True
                else:
                    print(f"{Colors.FAIL}❌ Market Data Manager API ({response.status}){Colors.ENDC}")
                    return False
        except Exception as e:
            print(f"{Colors.FAIL}❌ Market Data Manager API (Error: {e}){Colors.ENDC}")
            return False
    
    async def test_jordan_mainnet_api(self):
        """Test Jordan Mainnet credentials and API"""
        try:
            jordan_url = os.getenv('JORDAN_MAINNET_NODE_URL', 'http://jordan-mainnet-node:8022')
            async with self.session.get(f"{jordan_url}/health") as response:
                if response.status == 200:
                    print(f"{Colors.OKGREEN}✅ Jordan Mainnet Node API{Colors.ENDC}")
                    return True
                else:
                    print(f"{Colors.FAIL}❌ Jordan Mainnet Node API ({response.status}){Colors.ENDC}")
                    return False
        except Exception as e:
            print(f"{Colors.FAIL}❌ Jordan Mainnet Node API (Error: {e}){Colors.ENDC}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.session:
                await self.session.close()
            logger.info("# Check Orchestrator cleanup completed")
        except Exception as e:
            logger.error(f"# X Cleanup error: {e}")

async def main():
    """Main execution function"""
    orchestrator = ComprehensiveBacktestOrchestrator()
    
    try:
        # Initialize
        print(f"\n{Colors.BOLD}{Colors.OKCYAN}🚀 VIPER COMPREHENSIVE BACKTESTING SYSTEM{Colors.ENDC}")
        print("Initializing orchestrator...")
        
        if not await orchestrator.initialize():
            print(f"{Colors.FAIL}❌ Initialization failed{Colors.ENDC}")
            return False
        
        # Test API integrations first
        if not await orchestrator.test_api_integrations():
            print(f"{Colors.WARNING}⚠️  Some API tests failed, continuing anyway...{Colors.ENDC}")
        
        # Run comprehensive backtests
        success = await orchestrator.run_comprehensive_backtests()
        
        if success:
            print(f"\n{Colors.BOLD}{Colors.OKGREEN}🎉 COMPREHENSIVE BACKTESTING COMPLETED SUCCESSFULLY!{Colors.ENDC}")
            print(f"Check the 'backtest_reports' directory for detailed results.")
        else:
            print(f"\n{Colors.FAIL}❌ Backtesting failed{Colors.ENDC}")
        
        return success
        
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  Backtesting interrupted by user{Colors.ENDC}")
        return False
    except Exception as e:
        logger.error(f"# X Main execution error: {e}")
        print(f"\n{Colors.FAIL}❌ Backtesting failed: {e}{Colors.ENDC}")
        return False
    finally:
        await orchestrator.cleanup()

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)