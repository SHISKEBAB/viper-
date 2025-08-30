#!/usr/bin/env python3
"""
🚀 MASTER OPTIMIZATION RUNNER
=============================

Single script to run complete strategy optimization and backtesting suite.

Usage:
    python master_optimization_runner.py [--quick] [--full] [--summary-only]

Options:
    --quick      : Run quick optimization only (faster)
    --full       : Run full comprehensive optimization (slower)
    --summary-only : Display summary of existing results only
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Rich for beautiful output
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def run_optimization_suite(mode: str = "quick"):
    """Run the optimization suite based on mode"""
    
    console.print("🚀 MASTER OPTIMIZATION RUNNER", style="bold cyan", justify="center")
    console.print(f"Running {mode} optimization mode\n", justify="center")
    
    project_root = Path("/home/runner/work/viper-/viper-")
    scripts_dir = project_root / "scripts"
    
    if mode == "quick":
        scripts_to_run = [
            ("Quick Strategy Optimizer", "quick_strategy_optimizer.py"),
            ("Consolidated Results Generator", "consolidated_results_generator.py"),
            ("Optimized Config Generator", "optimized_config_generator.py"),
            ("Optimization Summary", "optimization_summary.py")
        ]
    elif mode == "full":
        scripts_to_run = [
            ("Comprehensive Optimization Runner", "comprehensive_optimization_runner.py"),
            ("Quick Strategy Optimizer", "quick_strategy_optimizer.py"),
            ("Consolidated Results Generator", "consolidated_results_generator.py"),
            ("Optimized Config Generator", "optimized_config_generator.py"),
            ("Optimization Summary", "optimization_summary.py")
        ]
    else:  # summary-only
        scripts_to_run = [
            ("Optimization Summary", "optimization_summary.py")
        ]
    
    results = {}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        for i, (name, script) in enumerate(scripts_to_run):
            task = progress.add_task(f"Running {name}...")
            
            script_path = scripts_dir / script
            if not script_path.exists():
                console.print(f"❌ Script not found: {script}", style="red")
                results[name] = {"success": False, "error": "Script not found"}
                continue
            
            try:
                # Run the script
                result = subprocess.run([
                    sys.executable, str(script_path)
                ], cwd=str(project_root), capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    console.print(f"✅ {name} completed successfully")
                    results[name] = {"success": True, "output": result.stdout}
                else:
                    console.print(f"❌ {name} failed: {result.stderr}")
                    results[name] = {"success": False, "error": result.stderr}
                    
            except subprocess.TimeoutExpired:
                console.print(f"⏰ {name} timed out")
                results[name] = {"success": False, "error": "Timeout"}
            except Exception as e:
                console.print(f"❌ {name} failed: {e}")
                results[name] = {"success": False, "error": str(e)}
            
            progress.remove_task(task)
    
    return results


def display_final_summary(results: Dict[str, Any]):
    """Display final summary of all optimization work"""
    
    console.print("\n🎉 MASTER OPTIMIZATION COMPLETE", style="bold green", justify="center")
    console.print("=" * 60, style="green", justify="center")
    
    # Results table
    from rich.table import Table
    from rich import box
    
    results_table = Table(title="Script Execution Results", box=box.ROUNDED)
    results_table.add_column("Script", style="cyan")
    results_table.add_column("Status", justify="center")
    results_table.add_column("Details", style="yellow")
    
    for script_name, result in results.items():
        status = "✅ Success" if result["success"] else "❌ Failed"
        details = "Completed successfully" if result["success"] else result.get("error", "Unknown error")
        results_table.add_row(script_name, status, details)
    
    console.print(results_table)
    
    # Success rate
    successful = sum(1 for r in results.values() if r["success"])
    total = len(results)
    success_rate = successful / total if total > 0 else 0
    
    summary_text = (
        f"Scripts Executed: {total}\n"
        f"Successful: {successful}\n"
        f"Success Rate: {success_rate:.1%}\n"
        f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    summary_panel = Panel(summary_text, title="📊 Execution Summary", border_style="green")
    console.print(summary_panel)


def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description="VIPER Master Optimization Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick optimization only")
    parser.add_argument("--full", action="store_true", help="Run full comprehensive optimization")
    parser.add_argument("--summary-only", action="store_true", help="Display summary only")
    
    args = parser.parse_args()
    
    # Determine mode
    if args.full:
        mode = "full"
    elif args.summary_only:
        mode = "summary-only"
    else:
        mode = "quick"  # Default
    
    try:
        # Run optimization suite
        results = run_optimization_suite(mode)
        
        # Display final summary
        display_final_summary(results)
        
        console.print("\n🎯 All optimization work completed!", style="bold green")
        console.print("📁 Check the generated files in the project directories for detailed results.", style="yellow")
        
        return 0
        
    except Exception as e:
        console.print(f"❌ Master optimization failed: {e}", style="red")
        return 1


if __name__ == "__main__":
    sys.exit(main())