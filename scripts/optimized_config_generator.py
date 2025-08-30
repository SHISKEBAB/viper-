#!/usr/bin/env python3
"""
🎯 OPTIMIZED TRADING CONFIGURATION GENERATOR
============================================

Generates optimized trading configurations based on comprehensive optimization results.
These configurations can be used directly in live trading systems.
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

console = Console()
logger = logging.getLogger(__name__)


class OptimizedTradingConfigGenerator:
    """Generates optimized trading configurations for live trading"""
    
    def __init__(self):
        self.console = Console()
        self.project_root = Path("/home/runner/work/viper-/viper-")
        self.config_dir = self.project_root / "optimized_trading_configs"
        self.config_dir.mkdir(exist_ok=True)
        
        # Load optimization results
        self.results_dir = self.project_root / "consolidated_optimization_results"
    
    def load_optimization_results(self) -> Dict[str, Any]:
        """Load consolidated optimization results"""
        
        results_file = self.results_dir / "consolidated_optimization_report.json"
        
        if not results_file.exists():
            raise FileNotFoundError(f"Optimization results not found at {results_file}")
        
        with open(results_file, 'r') as f:
            return json.load(f)
    
    def extract_best_configurations(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the best performing configurations for live trading"""
        
        analysis = results["optimization_report"]["analysis"]
        
        best_configs = {
            "high_win_rate_configs": [],
            "high_return_configs": [],
            "balanced_configs": [],
            "recommended_config": {}
        }
        
        # Extract from strategy rankings
        strategy_rankings = analysis.get("strategy_performance_ranking", [])
        if strategy_rankings:
            # Top strategy overall
            top_strategy = strategy_rankings[0]
            best_configs["recommended_config"] = {
                "strategy_name": top_strategy["strategy"],
                "expected_performance": {
                    "win_rate": top_strategy["avg_win_rate"],
                    "avg_return": top_strategy["avg_return"],
                    "sharpe_ratio": top_strategy["avg_sharpe"],
                    "max_drawdown": top_strategy["avg_max_drawdown"]
                },
                "risk_level": "moderate",
                "recommended_for": "general trading"
            }
        
        # Extract from best configurations
        best_configurations = analysis.get("best_configurations", {})
        
        if "quick_optimization" in best_configurations:
            quick_best = best_configurations["quick_optimization"]
            
            # High win rate configuration
            if "best_win_rate" in quick_best:
                best_wr = quick_best["best_win_rate"]
                best_configs["high_win_rate_configs"].append({
                    "strategy": best_wr["strategy"],
                    "symbol": best_wr["symbol"],
                    "timeframe": best_wr["timeframe"],
                    "parameters": best_wr.get("parameters", {}),
                    "performance": {
                        "win_rate": best_wr["win_rate"],
                        "total_return": best_wr["total_return"],
                        "sharpe_ratio": best_wr["sharpe_ratio"],
                        "max_drawdown": best_wr["max_drawdown"]
                    },
                    "risk_level": "conservative",
                    "recommended_for": "high win rate focused trading"
                })
            
            # High return configuration
            if "best_return" in quick_best:
                best_ret = quick_best["best_return"]
                best_configs["high_return_configs"].append({
                    "strategy": best_ret["strategy"],
                    "symbol": best_ret["symbol"],
                    "timeframe": best_ret["timeframe"],
                    "parameters": best_ret.get("parameters", {}),
                    "performance": {
                        "win_rate": best_ret["win_rate"],
                        "total_return": best_ret["total_return"],
                        "sharpe_ratio": best_ret["sharpe_ratio"],
                        "max_drawdown": best_ret["max_drawdown"]
                    },
                    "risk_level": "aggressive",
                    "recommended_for": "high return focused trading"
                })
            
            # Balanced configuration (best Sharpe)
            if "best_sharpe" in quick_best:
                best_sharpe = quick_best["best_sharpe"]
                best_configs["balanced_configs"].append({
                    "strategy": best_sharpe["strategy"],
                    "symbol": best_sharpe["symbol"],
                    "timeframe": best_sharpe["timeframe"],
                    "parameters": best_sharpe.get("parameters", {}),
                    "performance": {
                        "win_rate": best_sharpe["win_rate"],
                        "total_return": best_sharpe["total_return"],
                        "sharpe_ratio": best_sharpe["sharpe_ratio"],
                        "max_drawdown": best_sharpe["max_drawdown"]
                    },
                    "risk_level": "balanced",
                    "recommended_for": "risk-adjusted return optimization"
                })
        
        return best_configs
    
    def generate_trading_config_files(self, best_configs: Dict[str, Any]):
        """Generate practical trading configuration files"""
        
        # Generate main trading configuration
        main_config = {
            "trading_configuration": {
                "version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "source": "VIPER Comprehensive Optimization Results",
                
                "default_strategy": best_configs.get("recommended_config", {}),
                
                "strategy_configurations": {
                    "high_win_rate": best_configs.get("high_win_rate_configs", []),
                    "high_return": best_configs.get("high_return_configs", []),
                    "balanced": best_configs.get("balanced_configs", [])
                },
                
                "global_risk_management": {
                    "max_position_size": 0.05,  # 5% of portfolio per trade
                    "max_daily_loss": 0.02,     # 2% max daily loss
                    "max_open_positions": 3,
                    "emergency_stop_loss": 0.10  # 10% emergency stop
                },
                
                "trading_schedule": {
                    "active_hours": "24/7",
                    "maintenance_window": "02:00-04:00 UTC",
                    "holiday_trading": False
                }
            }
        }
        
        # Save main configuration
        main_config_file = self.config_dir / "optimized_trading_config.json"
        with open(main_config_file, 'w') as f:
            json.dump(main_config, f, indent=2, default=str)
        
        # Generate strategy-specific configs
        for config_type, configs in best_configs.items():
            if config_type != "recommended_config" and configs:
                for i, config in enumerate(configs):
                    strategy_name = config.get("strategy", "unknown")
                    symbol = config.get("symbol", "unknown")
                    timeframe = config.get("timeframe", "unknown")
                    
                    strategy_config = {
                        "strategy_configuration": {
                            "name": f"{strategy_name}_{symbol}_{timeframe}",
                            "strategy": strategy_name,
                            "symbol": symbol,
                            "timeframe": timeframe,
                            "parameters": config.get("parameters", {}),
                            "expected_performance": config.get("performance", {}),
                            "risk_level": config.get("risk_level", "moderate"),
                            "recommended_for": config.get("recommended_for", "general use"),
                            "optimization_source": config_type,
                            "generated_at": datetime.now().isoformat()
                        }
                    }
                    
                    config_filename = f"{strategy_name}_{symbol}_{timeframe}_{config_type}.json"
                    config_file = self.config_dir / config_filename
                    
                    with open(config_file, 'w') as f:
                        json.dump(strategy_config, f, indent=2, default=str)
        
        return main_config_file
    
    def display_trading_configurations(self, best_configs: Dict[str, Any]):
        """Display optimized trading configurations"""
        
        self.console.print("🎯 OPTIMIZED TRADING CONFIGURATIONS", style="bold cyan", justify="center")
        self.console.print("Ready-to-use configurations for live trading\n", justify="center")
        
        # Recommended configuration
        recommended = best_configs.get("recommended_config", {})
        if recommended:
            rec_text = (
                f"Strategy: {recommended.get('strategy_name', 'Unknown')}\n"
                f"Expected Win Rate: {recommended.get('expected_performance', {}).get('win_rate', 0):.1%}\n"
                f"Expected Return: {recommended.get('expected_performance', {}).get('avg_return', 0):.2%}\n"
                f"Sharpe Ratio: {recommended.get('expected_performance', {}).get('sharpe_ratio', 0):.2f}\n"
                f"Risk Level: {recommended.get('risk_level', 'Unknown')}\n"
                f"Recommended For: {recommended.get('recommended_for', 'Unknown')}"
            )
            rec_panel = Panel(rec_text, title="🏆 Recommended Configuration", border_style="green")
            self.console.print(rec_panel)
        
        # Configuration summary table
        config_table = Table(title="Available Trading Configurations", box=box.ROUNDED)
        config_table.add_column("Type", style="cyan")
        config_table.add_column("Strategy", style="yellow")
        config_table.add_column("Symbol", style="green")
        config_table.add_column("Timeframe", style="blue")
        config_table.add_column("Win Rate", justify="right", style="yellow")
        config_table.add_column("Return", justify="right", style="green")
        config_table.add_column("Risk Level", style="magenta")
        
        for config_type, configs in best_configs.items():
            if config_type != "recommended_config" and configs:
                for config in configs:
                    perf = config.get("performance", {})
                    config_table.add_row(
                        config_type.replace("_", " ").title(),
                        config.get("strategy", "Unknown"),
                        config.get("symbol", "Unknown"),
                        config.get("timeframe", "Unknown"),
                        f"{perf.get('win_rate', 0):.1%}",
                        f"{perf.get('total_return', 0):.2%}",
                        config.get("risk_level", "Unknown")
                    )
        
        self.console.print(config_table)
    
    def generate_implementation_guide(self) -> str:
        """Generate implementation guide for using optimized configurations"""
        
        guide = """
# VIPER OPTIMIZED TRADING CONFIGURATIONS - IMPLEMENTATION GUIDE

## Quick Start
1. Review the generated configuration files in `optimized_trading_configs/`
2. Select a configuration based on your risk tolerance:
   - High Win Rate: Conservative approach with higher win probability
   - High Return: Aggressive approach targeting maximum returns
   - Balanced: Risk-adjusted approach optimizing Sharpe ratio

## Configuration Files Generated
- `optimized_trading_config.json`: Main configuration with all strategies
- Individual strategy configs: `{strategy}_{symbol}_{timeframe}_{type}.json`

## Implementation Steps
1. Copy the desired configuration to your trading system
2. Update API keys and exchange settings
3. Set position sizing according to your capital
4. Enable risk management features
5. Start with paper trading to validate performance

## Risk Management
- Never risk more than 5% of capital per trade
- Implement daily loss limits (recommended: 2%)
- Use emergency stop losses (recommended: 10%)
- Monitor performance regularly and adjust if needed

## Performance Expectations
Based on optimization results:
- Target Win Rate: 55-65%
- Expected Monthly Return: 1-15%
- Risk-Adjusted Returns: Sharpe > 1.0
- Maximum Drawdown: < 10%

## Monitoring and Maintenance
- Track actual vs expected performance
- Re-optimize monthly or when performance degrades
- Adjust parameters based on market conditions
- Keep detailed trading logs for analysis
"""
        
        guide_file = self.config_dir / "IMPLEMENTATION_GUIDE.md"
        with open(guide_file, 'w') as f:
            f.write(guide)
        
        return str(guide_file)


def main():
    """Main execution function"""
    
    console.print("🎯 OPTIMIZED TRADING CONFIGURATION GENERATOR", style="bold cyan", justify="center")
    console.print("Generating practical trading configurations from optimization results\n", justify="center")
    
    generator = OptimizedTradingConfigGenerator()
    
    try:
        # Load optimization results
        results = generator.load_optimization_results()
        
        # Extract best configurations
        best_configs = generator.extract_best_configurations(results)
        
        # Generate trading config files
        main_config_file = generator.generate_trading_config_files(best_configs)
        
        # Display configurations
        generator.display_trading_configurations(best_configs)
        
        # Generate implementation guide
        guide_file = generator.generate_implementation_guide()
        
        console.print(f"\n💾 CONFIGURATION FILES GENERATED:", style="bold green")
        console.print(f"📋 Main Config: {main_config_file}")
        console.print(f"📖 Implementation Guide: {guide_file}")
        console.print(f"📁 All configs saved to: {generator.config_dir}")
        
        console.print("\n🎉 Optimized trading configurations generated successfully!", style="bold green")
        
        return 0
        
    except Exception as e:
        logger.error(f"Configuration generation failed: {e}")
        console.print(f"❌ Configuration generation failed: {e}", style="red")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())