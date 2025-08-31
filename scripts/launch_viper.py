#!/usr/bin/env python3
"""
🚀 VIPER MASTER LAUNCH SYSTEM
One-command launcher for the complete VIPER trading system

This is the main entry point that provides:
- System validation and health checks
- Multiple launch modes (demo, live trading, monitoring)
- Comprehensive error handling and user guidance
- Integrated Docker service management
"""

import os
import sys
import subprocess
import time
from pathlib import Path

class ViperMasterLauncher:
    """Master launcher for the complete VIPER trading system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        
    def print_banner(self):
        """Print the main VIPER banner"""
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     🚀 VIPER MASTER LAUNCH SYSTEM                           ║
║                 AI-Powered Cryptocurrency Trading Platform                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  🔥 AI-Powered Entry Points   │  🎯 ML-Optimized TP/SL                       ║
║  📊 Real-Time Backtesting     │  ⚡ Live Parameter Optimization              ║
║  🛡️ Enterprise Risk Management │  🤖 Machine Learning Integration            ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """)
        
    def show_launch_menu(self):
        """Show available launch options"""
        print("🎯 Available Launch Options:")
        print("  1. 🎮 Demo Mode        - Safe demonstration with paper trading")
        print("  2. 🔍 System Check     - Comprehensive system validation")
        print("  3. 📊 Monitoring       - Real-time system monitoring dashboard")
        print("  4. 🚀 Live Trading     - Start live trading (REAL MONEY)")
        print("  5. ⚙️  Optimization    - Run system optimization routines")
        print("  6. 📈 Complete System  - Full AI/ML optimized trading system")
        print("  7. ❓ Help             - Show detailed usage information")
        print("  8. ❌ Exit             - Exit launcher")
        print()
        
    def launch_demo_mode(self):
        """Launch in demo mode"""
        print("🎮 Launching Demo Mode...")
        print("This will run a safe demonstration using paper trading")
        try:
            result = subprocess.run([sys.executable, "scripts/launch_integrated_system.py", "demo"])
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Demo launch failed: {e}")
            return False
            
    def launch_system_check(self):
        """Run comprehensive system check"""
        print("🔍 Running System Check...")
        try:
            result = subprocess.run([sys.executable, "scripts/launch_integrated_system.py", "diagnostics"])
            return result.returncode == 0
        except Exception as e:
            print(f"❌ System check failed: {e}")
            return False
            
    def launch_monitoring(self):
        """Launch monitoring dashboard"""
        print("📊 Launching Monitoring Dashboard...")
        try:
            result = subprocess.run([sys.executable, "scripts/launch_integrated_system.py", "monitor"])
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Monitoring launch failed: {e}")
            return False
            
    def launch_live_trading(self):
        """Launch live trading system"""
        print("🚀 Launching Live Trading System...")
        print("⚠️  WARNING: This will trade with REAL MONEY!")
        print()
        
        confirm = input("Are you sure you want to start live trading? (type 'yes' to confirm): ").strip().lower()
        if confirm != 'yes':
            print("❌ Live trading cancelled")
            return False
            
        try:
            result = subprocess.run([sys.executable, "start_trading.py"])
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Live trading launch failed: {e}")
            return False
            
    def launch_optimization(self):
        """Launch system optimization"""
        print("⚙️ Launching System Optimization...")
        try:
            result = subprocess.run([sys.executable, "scripts/launch_integrated_system.py", "optimize"])
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Optimization launch failed: {e}")
            return False
            
    def launch_complete_system(self):
        """Launch complete AI/ML system"""
        print("📈 Launching Complete AI/ML System...")
        print("This will start the full optimized trading system")
        try:
            result = subprocess.run([sys.executable, "scripts/launch_complete_system.py"])
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Complete system launch failed: {e}")
            return False
            
    def show_help(self):
        """Show detailed help information"""
        print("""
📖 VIPER TRADING SYSTEM - DETAILED HELP

🎮 Demo Mode:
   Safe paper trading demonstration. No real money involved.
   Perfect for testing and learning the system.

🔍 System Check:
   Comprehensive validation of all system components.
   Checks Docker services, API connections, and system health.

📊 Monitoring:
   Real-time dashboard showing system performance and trading activity.
   Access via web browser at http://localhost:8000

🚀 Live Trading:
   REAL MONEY trading with the VIPER system.
   Requires valid API keys and sufficient account balance.
   ⚠️  USE WITH CAUTION - YOU CAN LOSE MONEY!

⚙️ Optimization:
   Runs parameter optimization and system tuning routines.
   Improves trading performance based on historical data.

📈 Complete System:
   Full AI/ML optimized system with all advanced features.
   Maximum performance mode for experienced traders.

For more information, see the documentation in the docs/ folder.
        """)
        
    def run_interactive_launcher(self):
        """Run the interactive launcher"""
        self.print_banner()
        
        while True:
            self.show_launch_menu()
            
            try:
                choice = input("Select option (1-8): ").strip()
                
                if choice == '1':
                    self.launch_demo_mode()
                elif choice == '2':
                    self.launch_system_check()
                elif choice == '3':
                    self.launch_monitoring()
                elif choice == '4':
                    self.launch_live_trading()
                elif choice == '5':
                    self.launch_optimization()
                elif choice == '6':
                    self.launch_complete_system()
                elif choice == '7':
                    self.show_help()
                elif choice == '8':
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid option. Please select 1-8.")
                    
                print("\nPress Enter to continue...")
                input()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main entry point"""
    launcher = ViperMasterLauncher()
    
    # Check if a mode was provided as command line argument
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode in ['demo', 'check', 'monitor', 'trade', 'optimize', 'complete']:
            launcher.print_banner()
            if mode == 'demo':
                launcher.launch_demo_mode()
            elif mode == 'check':
                launcher.launch_system_check()
            elif mode == 'monitor':
                launcher.launch_monitoring()
            elif mode == 'trade':
                launcher.launch_live_trading()
            elif mode == 'optimize':
                launcher.launch_optimization()
            elif mode == 'complete':
                launcher.launch_complete_system()
        else:
            print(f"❌ Unknown mode: {mode}")
            print("Available modes: demo, check, monitor, trade, optimize, complete")
            return 1
    else:
        # Run interactive mode
        launcher.run_interactive_launcher()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())