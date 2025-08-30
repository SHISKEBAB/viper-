#!/usr/bin/env python3
"""
📊 CONSOLIDATED OPTIMIZATION RESULTS GENERATOR
==============================================

This script consolidates all optimization results and generates a comprehensive
performance report with recommendations.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')

# Rich for beautiful output
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.layout import Layout

console = Console()
logger = logging.getLogger(__name__)


class ConsolidatedResultsGenerator:
    """Generates consolidated optimization results and recommendations"""
    
    def __init__(self):
        self.console = Console()
        self.project_root = Path("/home/runner/work/viper-/viper-")
        self.output_dir = self.project_root / "consolidated_optimization_results"
        self.output_dir.mkdir(exist_ok=True)
        
        # Results sources
        self.results_sources = [
            self.project_root / "optimization_results",
            self.project_root / "quick_optimization_results",
            Path("/tmp/optimization_results"),
            Path("/tmp/quick_optimization_results")
        ]
    
    def load_all_results(self) -> Dict[str, Any]:
        """Load all available optimization results"""
        
        all_results = {
            "comprehensive_optimization": {},
            "quick_optimization": {},
            "enhanced_multi_strategy": {},
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "sources_checked": [],
                "sources_loaded": []
            }
        }
        
        for source_dir in self.results_sources:
            if source_dir.exists():
                all_results["metadata"]["sources_checked"].append(str(source_dir))
                
                # Load comprehensive optimization results
                comp_file = source_dir / "comprehensive_optimization_results.json"
                if comp_file.exists():
                    try:
                        with open(comp_file, 'r') as f:
                            comp_data = json.load(f)
                        all_results["comprehensive_optimization"] = comp_data
                        all_results["metadata"]["sources_loaded"].append(str(comp_file))
                        self.console.print(f"✅ Loaded comprehensive results from {comp_file}")
                    except Exception as e:
                        logger.warning(f"Failed to load {comp_file}: {e}")
                
                # Load quick optimization results
                quick_file = source_dir / "quick_optimization_results.json"
                if quick_file.exists():
                    try:
                        with open(quick_file, 'r') as f:
                            quick_data = json.load(f)
                        all_results["quick_optimization"] = quick_data
                        all_results["metadata"]["sources_loaded"].append(str(quick_file))
                        self.console.print(f"✅ Loaded quick results from {quick_file}")
                    except Exception as e:
                        logger.warning(f"Failed to load {quick_file}: {e}")
        
        return all_results
    
    def analyze_consolidated_results(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze all optimization results comprehensively"""
        
        analysis = {
            "executive_summary": {},
            "strategy_performance_ranking": [],
            "best_configurations": {},
            "performance_metrics": {},
            "recommendations": [],
            "success_rates": {}
        }
        
        # Analyze comprehensive optimization results
        comp_results = all_results.get("comprehensive_optimization", {})
        if comp_results:
            # Extract multi-strategy backtest results
            multi_strategy = comp_results.get("backtest_results", {}).get("multi_strategy", {})
            if multi_strategy.get("success"):
                analysis_data = multi_strategy.get("analysis", {})
                
                if "strategy_rankings" in analysis_data:
                    analysis["strategy_performance_ranking"] = analysis_data["strategy_rankings"]
                
                if "overall_stats" in analysis_data:
                    analysis["performance_metrics"]["multi_strategy"] = analysis_data["overall_stats"]
                
                if "best_configurations" in analysis_data:
                    analysis["best_configurations"]["multi_strategy"] = analysis_data["best_configurations"]
        
        # Analyze quick optimization results
        quick_results = all_results.get("quick_optimization", {})
        if quick_results:
            quick_analysis = quick_results.get("analysis", {})
            
            if "strategy_summaries" in quick_analysis:
                analysis["performance_metrics"]["quick_strategies"] = quick_analysis["strategy_summaries"]
            
            if "overall_stats" in quick_analysis:
                overall_stats = quick_analysis["overall_stats"]
                if "best_overall" in overall_stats:
                    analysis["best_configurations"]["quick_optimization"] = overall_stats["best_overall"]
        
        # Calculate success rates
        total_optimizations = 0
        successful_optimizations = 0
        
        if comp_results:
            opt_results = comp_results.get("optimization_results", {})
            for category, result in opt_results.items():
                total_optimizations += 1
                if result.get("success", False):
                    successful_optimizations += 1
            
            backtest_results = comp_results.get("backtest_results", {})
            for category, result in backtest_results.items():
                total_optimizations += 1
                if result.get("success", False):
                    successful_optimizations += 1
        
        if quick_results and "optimization_results" in quick_results:
            # Count successful quick optimizations
            opt_data = quick_results["optimization_results"]
            for strategy, strategy_data in opt_data.items():
                for symbol, symbol_data in strategy_data.items():
                    for timeframe, timeframe_data in symbol_data.items():
                        total_optimizations += 1
                        if "error" not in timeframe_data:
                            successful_optimizations += 1
        
        success_rate = successful_optimizations / total_optimizations if total_optimizations > 0 else 0
        analysis["success_rates"] = {
            "total_optimizations": total_optimizations,
            "successful_optimizations": successful_optimizations,
            "success_rate": success_rate
        }
        
        # Generate executive summary
        analysis["executive_summary"] = self._generate_executive_summary(analysis, all_results)
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_comprehensive_recommendations(analysis, all_results)
        
        return analysis
    
    def _generate_executive_summary(self, analysis: Dict[str, Any], all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of optimization results"""
        
        summary = {
            "optimization_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_strategies_tested": 0,
            "total_configurations_tested": 0,
            "success_rate": analysis["success_rates"]["success_rate"],
            "best_performing_strategy": None,
            "highest_win_rate_achieved": 0.0,
            "highest_return_achieved": 0.0,
            "best_sharpe_ratio_achieved": 0.0
        }
        
        # Count strategies and configurations
        strategy_rankings = analysis.get("strategy_performance_ranking", [])
        if strategy_rankings:
            summary["total_strategies_tested"] = len(strategy_rankings)
            summary["best_performing_strategy"] = strategy_rankings[0]["strategy"]
            summary["highest_win_rate_achieved"] = max([s["avg_win_rate"] for s in strategy_rankings])
            summary["highest_return_achieved"] = max([s["avg_return"] for s in strategy_rankings])
            summary["best_sharpe_ratio_achieved"] = max([s["avg_sharpe"] for s in strategy_rankings])
        
        # Count configurations from quick optimization
        quick_results = all_results.get("quick_optimization", {})
        if quick_results and "optimization_results" in quick_results:
            config_count = 0
            for strategy_data in quick_results["optimization_results"].values():
                for symbol_data in strategy_data.values():
                    for timeframe_data in symbol_data.values():
                        if "total_tests" in timeframe_data:
                            config_count += timeframe_data["total_tests"]
            summary["total_configurations_tested"] = config_count
        
        return summary
    
    def _generate_comprehensive_recommendations(self, analysis: Dict[str, Any], 
                                              all_results: Dict[str, Any]) -> List[str]:
        """Generate comprehensive recommendations based on all results"""
        
        recommendations = []
        
        # Success rate recommendations
        success_rate = analysis["success_rates"]["success_rate"]
        if success_rate > 0.8:
            recommendations.append("🎉 Excellent optimization success rate (>80%) - system is performing well")
        elif success_rate > 0.6:
            recommendations.append("✅ Good optimization success rate (>60%) - minor improvements needed")
        elif success_rate > 0.4:
            recommendations.append("⚠️ Moderate optimization success rate - system needs attention")
        else:
            recommendations.append("❌ Low optimization success rate - significant improvements needed")
        
        # Strategy performance recommendations
        strategy_rankings = analysis.get("strategy_performance_ranking", [])
        if strategy_rankings:
            best_strategy = strategy_rankings[0]
            
            recommendations.append(f"🏆 Best performing strategy: {best_strategy['strategy'].replace('_', ' ').title()}")
            
            if best_strategy["avg_win_rate"] > 0.6:
                recommendations.append(f"🎯 Excellent win rate achieved: {best_strategy['avg_win_rate']:.1%}")
            elif best_strategy["avg_win_rate"] > 0.55:
                recommendations.append(f"✅ Target win rate achieved: {best_strategy['avg_win_rate']:.1%}")
            else:
                recommendations.append(f"📊 Win rate below target: {best_strategy['avg_win_rate']:.1%} - consider parameter adjustments")
            
            if best_strategy["avg_sharpe"] > 2.0:
                recommendations.append("📈 Outstanding risk-adjusted returns - excellent Sharpe ratio")
            elif best_strategy["avg_sharpe"] > 1.0:
                recommendations.append("📊 Good risk-adjusted returns")
            else:
                recommendations.append("⚡ Consider optimizing risk management for better Sharpe ratio")
        
        # Quick optimization insights
        quick_metrics = analysis.get("performance_metrics", {}).get("quick_strategies", {})
        if quick_metrics:
            # Find best performing quick strategy
            best_quick = max(quick_metrics.items(), key=lambda x: x[1]["avg_return"])
            recommendations.append(f"⚡ Quick optimization best: {best_quick[0].replace('_', ' ').title()} "
                                 f"({best_quick[1]['avg_return']:.2%} return)")
        
        # Configuration recommendations
        best_configs = analysis.get("best_configurations", {})
        if "quick_optimization" in best_configs:
            quick_best = best_configs["quick_optimization"]
            if "best_win_rate" in quick_best:
                best_wr = quick_best["best_win_rate"]
                recommendations.append(f"🎯 Highest win rate configuration: {best_wr['win_rate']:.1%} "
                                     f"({best_wr['strategy']} on {best_wr['symbol']})")
        
        # General recommendations
        recommendations.append("💡 Consider implementing the best performing configurations in live trading")
        recommendations.append("🔄 Re-run optimizations periodically to adapt to market conditions")
        recommendations.append("⚖️ Balance between high win rate and risk-adjusted returns")
        
        return recommendations
    
    def generate_consolidated_report(self) -> Dict[str, Any]:
        """Generate comprehensive consolidated report"""
        
        self.console.print("📊 LOADING AND ANALYZING ALL OPTIMIZATION RESULTS", style="bold cyan", justify="center")
        
        # Load all results
        all_results = self.load_all_results()
        
        # Analyze results
        analysis = self.analyze_consolidated_results(all_results)
        
        # Create final report
        final_report = {
            "optimization_report": {
                "title": "VIPER Comprehensive Strategy Optimization Report",
                "generated_at": datetime.now().isoformat(),
                "analysis": analysis,
                "raw_results": all_results
            }
        }
        
        return final_report
    
    def display_consolidated_results(self, report: Dict[str, Any]):
        """Display consolidated optimization results"""
        
        analysis = report["optimization_report"]["analysis"]
        
        # Header
        self.console.print("\n📊 CONSOLIDATED OPTIMIZATION RESULTS", style="bold cyan", justify="center")
        self.console.print("🚀 VIPER Strategy Optimization Report", style="bold yellow", justify="center")
        self.console.print("=" * 80, style="cyan", justify="center")
        
        # Executive Summary
        exec_summary = analysis.get("executive_summary", {})
        if exec_summary:
            summary_text = (
                f"Optimization Date: {exec_summary.get('optimization_date', 'Unknown')}\n"
                f"Total Strategies Tested: {exec_summary.get('total_strategies_tested', 0)}\n"
                f"Total Configurations Tested: {exec_summary.get('total_configurations_tested', 0)}\n"
                f"Overall Success Rate: {exec_summary.get('success_rate', 0):.1%}\n"
                f"Best Performing Strategy: {exec_summary.get('best_performing_strategy', 'Unknown')}\n"
                f"Highest Win Rate: {exec_summary.get('highest_win_rate_achieved', 0):.1%}\n"
                f"Highest Return: {exec_summary.get('highest_return_achieved', 0):.2%}\n"
                f"Best Sharpe Ratio: {exec_summary.get('best_sharpe_ratio_achieved', 0):.2f}"
            )
            
            exec_panel = Panel(summary_text, title="📈 Executive Summary", border_style="green")
            self.console.print(exec_panel)
        
        # Strategy Performance Ranking
        strategy_rankings = analysis.get("strategy_performance_ranking", [])
        if strategy_rankings:
            ranking_table = Table(title="🏆 Strategy Performance Rankings", box=box.ROUNDED)
            ranking_table.add_column("Rank", justify="center", style="bold")
            ranking_table.add_column("Strategy", style="cyan")
            ranking_table.add_column("Avg Return", justify="right", style="green")
            ranking_table.add_column("Win Rate", justify="right", style="yellow")
            ranking_table.add_column("Sharpe Ratio", justify="right", style="blue")
            ranking_table.add_column("Max Drawdown", justify="right", style="red")
            ranking_table.add_column("Total Trades", justify="center")
            ranking_table.add_column("Score", justify="right", style="magenta")
            
            for i, strategy in enumerate(strategy_rankings[:10], 1):  # Top 10
                ranking_table.add_row(
                    f"#{i}",
                    strategy["strategy"].replace("_", " ").title(),
                    f"{strategy['avg_return']:.2%}",
                    f"{strategy['avg_win_rate']:.1%}",
                    f"{strategy['avg_sharpe']:.2f}",
                    f"{strategy['avg_max_drawdown']:.2%}",
                    str(strategy.get('total_trades', 0)),
                    f"{strategy.get('composite_score', 0):.3f}"
                )
            
            self.console.print(ranking_table)
        
        # Performance Metrics Comparison
        perf_metrics = analysis.get("performance_metrics", {})
        if perf_metrics:
            self.console.print("\n📊 PERFORMANCE METRICS COMPARISON", style="bold yellow")
            
            # Multi-strategy metrics
            if "multi_strategy" in perf_metrics:
                multi_stats = perf_metrics["multi_strategy"]
                multi_panel = Panel(
                    f"Average Return: {multi_stats.get('avg_return', 0):.2%}\n"
                    f"Average Sharpe: {multi_stats.get('avg_sharpe', 0):.2f}\n"
                    f"Average Win Rate: {multi_stats.get('avg_win_rate', 0):.1%}\n"
                    f"Average Max Drawdown: {multi_stats.get('avg_max_drawdown', 0):.2%}",
                    title="🔀 Multi-Strategy Results",
                    border_style="blue"
                )
                self.console.print(multi_panel)
            
            # Quick strategy metrics
            if "quick_strategies" in perf_metrics:
                quick_table = Table(title="⚡ Quick Strategy Results", box=box.SIMPLE)
                quick_table.add_column("Strategy", style="cyan")
                quick_table.add_column("Avg Return", justify="right", style="green")
                quick_table.add_column("Avg Win Rate", justify="right", style="yellow")
                quick_table.add_column("Avg Sharpe", justify="right", style="blue")
                
                for strategy, metrics in perf_metrics["quick_strategies"].items():
                    quick_table.add_row(
                        strategy.replace("_", " ").title(),
                        f"{metrics['avg_return']:.2%}",
                        f"{metrics['avg_win_rate']:.1%}",
                        f"{metrics['avg_sharpe']:.2f}"
                    )
                
                self.console.print(quick_table)
        
        # Best Configurations
        best_configs = analysis.get("best_configurations", {})
        if best_configs:
            self.console.print("\n🏆 BEST CONFIGURATIONS", style="bold green")
            
            for source, configs in best_configs.items():
                if isinstance(configs, dict):
                    for config_type, config_data in configs.items():
                        if isinstance(config_data, dict) and "win_rate" in config_data:
                            config_panel = Panel(
                                f"Source: {source.replace('_', ' ').title()}\n"
                                f"Type: {config_type.replace('_', ' ').title()}\n"
                                f"Strategy: {config_data.get('strategy', 'Unknown')}\n"
                                f"Symbol: {config_data.get('symbol', 'Unknown')}\n"
                                f"Timeframe: {config_data.get('timeframe', 'Unknown')}\n"
                                f"Win Rate: {config_data.get('win_rate', 0):.1%}\n"
                                f"Total Return: {config_data.get('total_return', 0):.2%}\n"
                                f"Sharpe Ratio: {config_data.get('sharpe_ratio', 0):.2f}",
                                title=f"🎯 {config_type.replace('_', ' ').title()}",
                                border_style="green"
                            )
                            self.console.print(config_panel)
        
        # Recommendations
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            rec_text = "\n".join([f"• {rec}" for rec in recommendations])
            rec_panel = Panel(rec_text, title="🎯 Optimization Recommendations", border_style="yellow")
            self.console.print(rec_panel)
        
        return analysis
    
    def save_consolidated_report(self, report: Dict[str, Any]):
        """Save consolidated report to files"""
        
        # Save main JSON report
        main_report_file = self.output_dir / "consolidated_optimization_report.json"
        with open(main_report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Save executive summary
        analysis = report["optimization_report"]["analysis"]
        exec_summary = analysis.get("executive_summary", {})
        
        summary_file = self.output_dir / "executive_summary.txt"
        with open(summary_file, 'w') as f:
            f.write("VIPER STRATEGY OPTIMIZATION - EXECUTIVE SUMMARY\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Optimization Date: {exec_summary.get('optimization_date', 'Unknown')}\n")
            f.write(f"Total Strategies Tested: {exec_summary.get('total_strategies_tested', 0)}\n")
            f.write(f"Total Configurations Tested: {exec_summary.get('total_configurations_tested', 0)}\n")
            f.write(f"Overall Success Rate: {exec_summary.get('success_rate', 0):.1%}\n\n")
            
            f.write("BEST PERFORMANCE ACHIEVED:\n")
            f.write(f"Best Strategy: {exec_summary.get('best_performing_strategy', 'Unknown')}\n")
            f.write(f"Highest Win Rate: {exec_summary.get('highest_win_rate_achieved', 0):.1%}\n")
            f.write(f"Highest Return: {exec_summary.get('highest_return_achieved', 0):.2%}\n")
            f.write(f"Best Sharpe Ratio: {exec_summary.get('best_sharpe_ratio_achieved', 0):.2f}\n\n")
            
            f.write("RECOMMENDATIONS:\n")
            recommendations = analysis.get("recommendations", [])
            for i, rec in enumerate(recommendations, 1):
                f.write(f"{i}. {rec}\n")
        
        # Save detailed performance data
        perf_file = self.output_dir / "detailed_performance_data.json"
        performance_data = {
            "strategy_rankings": analysis.get("strategy_performance_ranking", []),
            "performance_metrics": analysis.get("performance_metrics", {}),
            "best_configurations": analysis.get("best_configurations", {}),
            "success_rates": analysis.get("success_rates", {})
        }
        
        with open(perf_file, 'w') as f:
            json.dump(performance_data, f, indent=2, default=str)
        
        self.console.print(f"\n💾 REPORTS SAVED:", style="bold green")
        self.console.print(f"📊 Main Report: {main_report_file}")
        self.console.print(f"📋 Executive Summary: {summary_file}")
        self.console.print(f"📈 Performance Data: {perf_file}")


def main():
    """Main execution function"""
    
    console.print("📊 CONSOLIDATED OPTIMIZATION RESULTS GENERATOR", style="bold cyan", justify="center")
    console.print("Generating comprehensive optimization report\n", justify="center")
    
    generator = ConsolidatedResultsGenerator()
    
    try:
        # Generate consolidated report
        report = generator.generate_consolidated_report()
        
        # Display results
        analysis = generator.display_consolidated_results(report)
        
        # Save report
        generator.save_consolidated_report(report)
        
        console.print("\n🎉 Consolidated optimization report generated successfully!", style="bold green")
        
        return 0
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        console.print(f"❌ Report generation failed: {e}", style="red")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())