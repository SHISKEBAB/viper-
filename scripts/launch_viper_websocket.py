#!/usr/bin/env python3
"""
VIPER Trading System Launcher
Choose between REST API or WebSocket implementations
"""

import os
import sys
import subprocess
from pathlib import Path

def show_menu():
    """Display trading system options"""
    print("🚀 VIPER Trading System Launcher")
    print("=" * 50)
    print("1. Enhanced REST Trader (with WebSocket real-time data)")
    print("2. Pure WebSocket Trader (CCXT WebSocket only)")
    print("3. Test CCXT WebSocket functionality")
    print("4. Exit")
    print("=" * 50)
    
    choice = input("Select trading mode (1-4): ").strip()
    return choice

def launch_enhanced_rest_trader():
    """Launch the enhanced REST trader with WebSocket integration"""
    print("🔄 Starting Enhanced REST Trader with WebSocket data...")
    print("💰 Using $1 margin × 50x leverage = $50 notional as requested")
    print("📡 Real-time data via CCXT WebSocket feeds")
    
    try:
        subprocess.run([sys.executable, "run_live_trader.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running enhanced REST trader: {e}")
    except KeyboardInterrupt:
        print("🛑 Enhanced REST trader stopped by user")

def launch_websocket_trader():
    """Launch the pure WebSocket trader"""
    print("🔄 Starting Pure WebSocket Trader...")
    print("💰 Using $1 margin × 50x leverage = $50 notional as requested")
    print("📡 100% WebSocket-based trading with CCXT")
    
    try:
        subprocess.run([sys.executable, "run_live_trader_websocket.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running WebSocket trader: {e}")
    except KeyboardInterrupt:
        print("🛑 WebSocket trader stopped by user")

def test_websockets():
    """Test WebSocket functionality"""
    print("🔄 Testing CCXT WebSocket functionality...")
    
    try:
        subprocess.run([sys.executable, "test_ccxt_websockets.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error testing WebSockets: {e}")
    except KeyboardInterrupt:
        print("🛑 WebSocket test stopped by user")

def check_requirements():
    """Check if required modules are installed"""
    try:
        import ccxt
        print(f"✅ CCXT installed: v{ccxt.__version__}")
        
        # Check websocket support
        exchange = ccxt.bitget()
        ws_methods = [m for m in dir(exchange) if 'watch' in m.lower()]
        print(f"✅ WebSocket methods available: {len(ws_methods)}")
        
        return True
    except ImportError:
        print("❌ CCXT not installed. Run: pip install ccxt>=4.1.63")
        return False

def main():
    """Main launcher"""
    print("🎯 VIPER Trading System with CCXT WebSocket Integration")
    print()
    
    # Check requirements
    if not check_requirements():
        return
    
    # Check API credentials
    if not all([os.getenv('BITGET_API_KEY'), os.getenv('BITGET_API_SECRET'), os.getenv('BITGET_API_PASSWORD')]):
        print("⚠️ Warning: Missing API credentials in .env file")
        print("   Please set BITGET_API_KEY, BITGET_API_SECRET, BITGET_API_PASSWORD")
        print()
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            launch_enhanced_rest_trader()
        elif choice == '2':
            launch_websocket_trader()
        elif choice == '3':
            test_websockets()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-4.")
        
        print("\n" + "=" * 50 + "\n")

if __name__ == "__main__":
    main()