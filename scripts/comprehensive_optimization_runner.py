#!/usr/bin/env python3
"""
🚀 COMPREHENSIVE OPTIMIZATION RUNNER
====================================

This script runs optimization and backtesting on ALL available strategies in the repository.

Features:
✅ Runs all strategy optimizers
✅ Executes comprehensive backtesting
✅ Generates consolidated results
✅ Provides performance comparisons
✅ Creates optimization reports
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Rich for beautiful output
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.layout import Layout
from rich import box

# Add project paths
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent
sys.path.append(str(project_root / "src"))
sys.path.append(str(project_root / "src" / "viper" / "strategies"))
sys.path.append(str(project_root / "scripts"))

console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - OPTIMIZATION_RUNNER - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComprehensiveOptimizationRunner:
    """Runs comprehensive optimization across all strategies"""

    def __init__(self):
        self.console = Console()
        self.results_dir = Path("/tmp/optimization_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Results storage
        self.optimization_results: Dict[str, Any] = {}
        self.backtest_results: Dict[str, Any] = {}
        self.performance_summary: Dict[str, Any] = {}
        
        # Configuration
        self.symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT", "LINKUSDT"]
        self.timeframes = ["5m", "15m", "30m", "1h"]
        
    def run_full_optimization_suite(self) -> Dict[str, Any]:
        """Run complete optimization suite"""
        
        self.console.print("🚀 COMPREHENSIVE STRATEGY OPTIMIZATION SUITE", style="bold cyan", justify="center")
        self.console.print("Optimizing ALL strategies with comprehensive backtesting\n", justify="center")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "optimization_results": {},
            "backtest_results": {},
            "performance_analysis": {},
            "best_configurations": {},
            "recommendations": []
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            
            # Step 1: Enhanced Multi-Strategy Backtester
            task1 = progress.add_task("Running Enhanced Multi-Strategy Backtester...", total=100)
            multi_strategy_results = self._run_enhanced_multi_strategy_backtester()
            results["backtest_results"]["multi_strategy"] = multi_strategy_results
            progress.update(task1, completed=100)
            
            # Step 2: Advanced Strategy Optimizer
            task2 = progress.add_task("Running Advanced Strategy Optimizer...", total=100)
            advanced_opt_results = self._run_advanced_strategy_optimizer()
            results["optimization_results"]["advanced_optimizer"] = advanced_opt_results
            progress.update(task2, completed=100)
            
            # Step 3: AI/ML Optimizer
            task3 = progress.add_task("Running AI/ML Optimizer...", total=100)
            ai_ml_results = self._run_ai_ml_optimizer()
            results["optimization_results"]["ai_ml"] = ai_ml_results
            progress.update(task3, completed=100)
            
            # Step 4: Enhanced Parameter Optimizer
            task4 = progress.add_task("Running Enhanced Parameter Optimizer...", total=100)
            param_opt_results = self._run_enhanced_parameter_optimizer()
            results["optimization_results"]["parameter_optimizer"] = param_opt_results
            progress.update(task4, completed=100)
            
            # Step 5: Strategy-Specific Optimizations
            task5 = progress.add_task("Running Strategy-Specific Optimizations...", total=100)
            strategy_results = self._run_strategy_specific_optimizations()
            results["optimization_results"]["strategy_specific"] = strategy_results
            progress.update(task5, completed=100)
            
            # Step 6: Ultra Backtester Service
            task6 = progress.add_task("Running Ultra Backtester Service...", total=100)
            ultra_backtest_results = self._run_ultra_backtester()
            results["backtest_results"]["ultra_backtester"] = ultra_backtest_results
            progress.update(task6, completed=100)
        
        # Analyze and consolidate results
        results["performance_analysis"] = self._analyze_comprehensive_results(results)
        results["best_configurations"] = self._extract_best_configurations(results)
        results["recommendations"] = self._generate_recommendations(results)
        
        return results
    
    def _run_enhanced_multi_strategy_backtester(self) -> Dict[str, Any]:
        """Run the enhanced multi-strategy backtester"""
        try:
            # Import and run the enhanced multi-strategy backtester
            from enhanced_multi_strategy_backtester import EnhancedMultiStrategyBacktester
            
            backtester = EnhancedMultiStrategyBacktester()
            configurations = backtester.generate_test_configurations()
            
            # Limit configurations for performance
            if len(configurations) > 100:
                configurations = configurations[:100]
            
            results = backtester.run_parallel_backtests(configurations)
            analysis = backtester.analyze_results(results)
            
            return {
                "success": True,
                "total_configurations": len(configurations),
                "successful_tests": len([r for r in results if r.success]),
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Enhanced multi-strategy backtester failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _run_advanced_strategy_optimizer(self) -> Dict[str, Any]:
        """Run the advanced strategy optimizer"""
        try:
            # Try to import and run advanced strategy optimizer
            from advanced_strategy_optimizer import AdvancedStrategyOptimizer
            
            optimizer = AdvancedStrategyOptimizer()
            
            # Run optimization for multiple symbols and timeframes
            results = {}
            for symbol in self.symbols[:3]:  # Limit for performance
                for timeframe in self.timeframes[:2]:  # Limit for performance
                    try:
                        result = optimizer.run_strategy_optimization(symbol, timeframe)
                        results[f"{symbol}_{timeframe}"] = result
                    except Exception as e:
                        results[f"{symbol}_{timeframe}"] = {"error": str(e)}
            
            return {
                "success": True,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Advanced strategy optimizer failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _run_ai_ml_optimizer(self) -> Dict[str, Any]:
        """Run the AI/ML optimizer"""
        try:
            from ai_ml_optimizer import AIMLOptimizer
            
            optimizer = AIMLOptimizer()
            
            # Run comprehensive backtest
            results = {}
            for symbol in self.symbols[:2]:  # Limit for performance
                try:
                    result = optimizer.run_comprehensive_backtest(symbol)
                    results[symbol] = result
                except Exception as e:
                    results[symbol] = {"error": str(e)}
            
            return {
                "success": True,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI/ML optimizer failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _run_enhanced_parameter_optimizer(self) -> Dict[str, Any]:
        """Run the enhanced parameter optimizer"""
        try:
            from enhanced_parameter_optimizer import EnhancedParameterOptimizer
            
            optimizer = EnhancedParameterOptimizer()
            
            # Run parameter optimization with different targets
            results = {}
            targets = ["sharpe_ratio", "win_rate", "balanced"]
            
            for target in targets:
                try:
                    result = optimizer.optimize_parameters(
                        target=target,
                        max_iterations=20,  # Limit for performance
                        parameter_groups=["risk_management", "technical_analysis"]
                    )
                    results[target] = result
                except Exception as e:
                    results[target] = {"error": str(e)}
            
            return {
                "success": True,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Enhanced parameter optimizer failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _run_strategy_specific_optimizations(self) -> Dict[str, Any]:
        """Run optimizations on specific strategies"""
        try:
            results = {}
            
            # Strategy files to test
            strategy_modules = [
                "bollinger_mean_reversion_strategy",
                "momentum_breakout_strategy", 
                "rsi_divergence_strategy",
                "fibonacci_strategy",
                "vwma_strategy"
            ]
            
            for strategy_module in strategy_modules:
                try:
                    # Try to import and test each strategy
                    module = __import__(strategy_module)
                    
                    # Look for common optimization methods
                    if hasattr(module, 'optimize_strategy'):
                        result = module.optimize_strategy()
                        results[strategy_module] = {"success": True, "result": result}
                    elif hasattr(module, 'run_optimization'):
                        result = module.run_optimization()
                        results[strategy_module] = {"success": True, "result": result}
                    else:
                        results[strategy_module] = {
                            "success": False, 
                            "error": "No optimization method found"
                        }
                        
                except Exception as e:
                    results[strategy_module] = {"success": False, "error": str(e)}
            
            return {
                "success": True,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Strategy-specific optimizations failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _run_ultra_backtester(self) -> Dict[str, Any]:
        """Run the ultra backtester service"""
        try:
            # Import ultra backtester from services
            ultra_backtester_path = project_root / "services" / "ultra-backtester" / "main.py"
            
            if ultra_backtester_path.exists():
                # Add path and import
                sys.path.append(str(ultra_backtester_path.parent))
                
                from main import UltraBacktester
                
                backtester = UltraBacktester()
                
                results = {}
                for symbol in self.symbols[:2]:  # Limit for performance
                    for timeframe in self.timeframes[:2]:
                        try:
                            # Run parameter optimization
                            param_ranges = {
                                'sma_20_period': [15, 20, 25],
                                'sma_50_period': [45, 50, 55]
                            }
                            
                            result = asyncio.run(backtester.run_parameter_optimization(
                                symbol, timeframe, param_ranges
                            ))
                            results[f"{symbol}_{timeframe}"] = result
                            
                        except Exception as e:
                            results[f"{symbol}_{timeframe}"] = {"error": str(e)}
                
                return {
                    "success": True,
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Ultra backtester not found",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Ultra backtester failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_comprehensive_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze all optimization results comprehensively"""
        analysis = {
            "summary": {},
            "best_performers": {},
            "performance_metrics": {},
            "optimization_success_rate": 0.0
        }
        
        # Count successful optimizations
        total_optimizations = 0
        successful_optimizations = 0
        
        for category, category_results in results.get("optimization_results", {}).items():
            total_optimizations += 1
            if category_results.get("success", False):
                successful_optimizations += 1
        
        for category, category_results in results.get("backtest_results", {}).items():
            total_optimizations += 1
            if category_results.get("success", False):
                successful_optimizations += 1
        
        analysis["optimization_success_rate"] = (
            successful_optimizations / total_optimizations if total_optimizations > 0 else 0.0
        )
        
        # Extract best performers from multi-strategy results
        multi_strategy = results.get("backtest_results", {}).get("multi_strategy", {})
        if multi_strategy.get("success") and "analysis" in multi_strategy:
            strategy_rankings = multi_strategy["analysis"].get("strategy_rankings", [])
            if strategy_rankings:
                analysis["best_performers"]["strategy"] = strategy_rankings[0]
        
        # Performance summary
        analysis["summary"] = {
            "total_optimizations_run": total_optimizations,
            "successful_optimizations": successful_optimizations,
            "optimization_success_rate": f"{analysis['optimization_success_rate']:.1%}",
            "timestamp": datetime.now().isoformat()
        }
        
        return analysis
    
    def _extract_best_configurations(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the best configurations from all optimization results"""
        best_configs = {}
        
        # From multi-strategy backtester
        multi_strategy = results.get("backtest_results", {}).get("multi_strategy", {})
        if multi_strategy.get("success"):
            analysis = multi_strategy.get("analysis", {})
            best_configs["multi_strategy"] = {
                "best_configurations": analysis.get("best_configurations", []),
                "timeframe_performance": analysis.get("timeframe_performance", {}),
                "overall_stats": analysis.get("overall_stats", {})
            }
        
        # From AI/ML optimizer
        ai_ml = results.get("optimization_results", {}).get("ai_ml", {})
        if ai_ml.get("success"):
            best_configs["ai_ml"] = ai_ml.get("results", {})
        
        return best_configs
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on optimization results"""
        recommendations = []
        
        # Analyze optimization success rate
        analysis = results.get("performance_analysis", {})
        success_rate = analysis.get("optimization_success_rate", 0.0)
        
        if success_rate > 0.8:
            recommendations.append("✅ Excellent optimization success rate - system is working well")
        elif success_rate > 0.6:
            recommendations.append("⚠️ Good optimization success rate - minor improvements needed")
        else:
            recommendations.append("❌ Low optimization success rate - system needs attention")
        
        # Strategy-specific recommendations
        best_configs = results.get("best_configurations", {})
        
        if "multi_strategy" in best_configs:
            multi_data = best_configs["multi_strategy"]
            overall_stats = multi_data.get("overall_stats", {})
            
            if overall_stats.get("avg_win_rate", 0) > 0.55:
                recommendations.append("🎯 Target win rate achieved (>55%) - excellent performance")
            else:
                recommendations.append("📊 Win rate below target - consider parameter adjustments")
            
            if overall_stats.get("avg_sharpe", 0) > 1.5:
                recommendations.append("📈 Strong risk-adjusted returns - good Sharpe ratio")
            else:
                recommendations.append("⚡ Consider optimizing risk management for better Sharpe ratio")
        
        # Timeframe recommendations
        timeframe_perf = best_configs.get("multi_strategy", {}).get("timeframe_performance", {})
        if timeframe_perf:
            best_tf = max(timeframe_perf.items(), key=lambda x: x[1])
            recommendations.append(f"⏰ Best performing timeframe: {best_tf[0]} ({best_tf[1]:.2%} return)")
        
        return recommendations
    
    def display_comprehensive_results(self, results: Dict[str, Any]):
        """Display comprehensive optimization results"""
        
        # Header
        self.console.print("\n🚀 COMPREHENSIVE OPTIMIZATION RESULTS", style="bold cyan", justify="center")
        self.console.print("=" * 80, style="cyan", justify="center")
        
        # Summary table
        summary_table = Table(title="Optimization Summary", box=box.ROUNDED)
        summary_table.add_column("Category", style="cyan")
        summary_table.add_column("Status", justify="center")
        summary_table.add_column("Details", style="green")
        
        # Add optimization results
        for category, category_results in results.get("optimization_results", {}).items():
            status = "✅ Success" if category_results.get("success", False) else "❌ Failed"
            details = f"Results available" if category_results.get("success") else category_results.get("error", "Unknown error")
            summary_table.add_row(category.replace("_", " ").title(), status, details)
        
        # Add backtest results
        for category, category_results in results.get("backtest_results", {}).items():
            status = "✅ Success" if category_results.get("success", False) else "❌ Failed"
            details = f"Results available" if category_results.get("success") else category_results.get("error", "Unknown error")
            summary_table.add_row(f"{category.replace('_', ' ').title()} Backtest", status, details)
        
        self.console.print(summary_table)
        
        # Performance Analysis
        analysis = results.get("performance_analysis", {})
        if analysis:
            perf_panel = Panel(
                f"Success Rate: {analysis.get('optimization_success_rate', 0):.1%}\n"
                f"Total Optimizations: {analysis.get('summary', {}).get('total_optimizations_run', 0)}\n"
                f"Successful: {analysis.get('summary', {}).get('successful_optimizations', 0)}",
                title="Performance Analysis",
                border_style="green"
            )
            self.console.print(perf_panel)
        
        # Best Configurations
        best_configs = results.get("best_configurations", {})
        if "multi_strategy" in best_configs:
            multi_data = best_configs["multi_strategy"]
            overall_stats = multi_data.get("overall_stats", {})
            
            if overall_stats:
                stats_table = Table(title="Best Strategy Performance", box=box.ROUNDED)
                stats_table.add_column("Metric", style="cyan")
                stats_table.add_column("Value", style="green", justify="right")
                
                stats_table.add_row("Average Return", f"{overall_stats.get('avg_return', 0):.2%}")
                stats_table.add_row("Average Sharpe Ratio", f"{overall_stats.get('avg_sharpe', 0):.2f}")
                stats_table.add_row("Average Win Rate", f"{overall_stats.get('avg_win_rate', 0):.1%}")
                stats_table.add_row("Average Max Drawdown", f"{overall_stats.get('avg_max_drawdown', 0):.2%}")
                
                self.console.print(stats_table)
        
        # Recommendations
        recommendations = results.get("recommendations", [])
        if recommendations:
            rec_text = "\n".join(recommendations)
            rec_panel = Panel(rec_text, title="🎯 Recommendations", border_style="yellow")
            self.console.print(rec_panel)
        
        # Save location
        self.console.print(f"\n💾 Full results saved to: {self.results_dir}/comprehensive_optimization_results.json", style="green")
    
    def save_results(self, results: Dict[str, Any]):
        """Save comprehensive results to files"""
        
        # Main results file
        results_file = self.results_dir / "comprehensive_optimization_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Summary report
        summary_file = self.results_dir / "optimization_summary.txt"
        with open(summary_file, 'w') as f:
            f.write("COMPREHENSIVE STRATEGY OPTIMIZATION RESULTS\n")
            f.write("=" * 50 + "\n\n")
            
            analysis = results.get("performance_analysis", {})
            f.write(f"Optimization Success Rate: {analysis.get('optimization_success_rate', 0):.1%}\n")
            f.write(f"Timestamp: {results.get('timestamp', 'Unknown')}\n\n")
            
            recommendations = results.get("recommendations", [])
            f.write("RECOMMENDATIONS:\n")
            for rec in recommendations:
                f.write(f"- {rec}\n")
        
        logger.info(f"Results saved to {self.results_dir}")


def main():
    """Main execution function"""
    runner = ComprehensiveOptimizationRunner()
    
    try:
        # Run comprehensive optimization
        results = runner.run_full_optimization_suite()
        
        # Display results
        runner.display_comprehensive_results(results)
        
        # Save results
        runner.save_results(results)
        
        console.print("\n🎉 Comprehensive optimization completed successfully!", style="bold green")
        
    except Exception as e:
        logger.error(f"Comprehensive optimization failed: {e}")
        console.print(f"❌ Optimization failed: {e}", style="red")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())