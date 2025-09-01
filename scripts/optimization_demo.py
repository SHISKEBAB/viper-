#!/usr/bin/env python3
"""
🚀 VIPER STRATEGY OPTIMIZATION DEMO
Demonstration of enhanced entry point and TP/SL optimization

This script demonstrates the comprehensive optimization system with focus on:
- Entry point optimization with multi-factor analysis
- Dynamic TP/SL optimization based on market conditions
- Real-time performance feedback and adjustment
"""

import asyncio
import sys
import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_realistic_market_data(symbol: str = "BTCUSDT", days: int = 30) -> Dict[str, pd.DataFrame]:
    """Generate realistic market data for demonstration"""
    
    # Parameters for realistic crypto data
    base_price = 45000 if symbol == "BTCUSDT" else 2500
    volatility = 0.03  # 3% daily volatility
    trend = 0.0002    # Small upward trend
    
    # Generate hourly data
    hours = days * 24
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), periods=hours, freq='1H')
    
    # Random walk with trend and volatility
    price_changes = np.random.normal(trend/24, volatility/np.sqrt(24), hours)
    prices = [base_price]
    
    for change in price_changes[1:]:
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)
    
    # Generate OHLCV data
    data = []
    for i, (date, price) in enumerate(zip(dates, prices)):
        # Create realistic OHLCV from price
        volatility_factor = abs(np.random.normal(0, 0.01))
        
        open_price = prices[i-1] if i > 0 else price
        close_price = price
        
        high_range = max(open_price, close_price) * (1 + volatility_factor)
        low_range = min(open_price, close_price) * (1 - volatility_factor)
        
        high = np.random.uniform(max(open_price, close_price), high_range)
        low = np.random.uniform(low_range, min(open_price, close_price))
        
        # Volume with some correlation to price movement
        price_move = abs((close_price - open_price) / open_price)
        base_volume = np.random.uniform(800, 1200)
        volume = base_volume * (1 + price_move * 10)  # Higher volume on big moves
        
        data.append({
            'timestamp': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    # Generate multiple timeframes
    market_data = {
        '1h': df,
        '4h': df.resample('4H').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }),
        '1d': df.resample('1D').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })
    }
    
    # Remove any NaN rows
    for timeframe in market_data:
        market_data[timeframe] = market_data[timeframe].dropna()
    
    return market_data

def print_optimization_results(result):
    """Print optimization results in a formatted way"""
    
    print("\n" + "="*80)
    print("🎯 VIPER OPTIMIZATION RESULTS")
    print("="*80)
    
    # Basic info
    print(f"📊 Symbol: {result.symbol}")
    print(f"⏰ Timeframe: {result.timeframe}")
    print(f"🕐 Analysis Time: {result.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n🎯 ENTRY POINT OPTIMIZATION")
    print("-" * 40)
    print(f"💎 Entry Confidence: {result.entry_confidence:.1%}")
    print(f"⭐ Entry Quality: {result.entry_quality}")
    print(f"💰 Optimal Entry Price: ${result.optimal_entry_price:.2f}")
    
    # Entry factors breakdown
    if result.entry_factors:
        print("\n📈 Entry Factor Analysis:")
        for factor, score in result.entry_factors.items():
            bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
            print(f"   {factor.replace('_', ' ').title():.<25} {bar} {score:.1%}")
    
    print("\n🎯 TP/SL OPTIMIZATION")
    print("-" * 40)
    print("📊 Take Profit Levels:")
    for i, (level, allocation) in enumerate(zip(result.optimal_tp_levels, result.optimal_tp_allocations), 1):
        print(f"   TP{i}: {level:.1%} (Allocation: {allocation:.1%})")
    
    print(f"🛡️  Stop Loss Level: {result.optimal_sl_level:.1%}")
    print(f"📈 Trailing Stop: {result.trailing_stop_pct:.1%}")
    print(f"⚖️  Risk/Reward Ratio: 1:{result.risk_reward_ratio:.2f}")
    
    print("\n📊 PERFORMANCE EXPECTATIONS")
    print("-" * 40)
    print(f"🎯 Expected Win Rate: {result.expected_win_rate:.1%}")
    print(f"💹 Expected Profit Factor: {result.expected_profit_factor:.2f}")
    print(f"🏆 Optimization Score: {result.optimization_score:.1%}")
    
    print("\n🌍 MARKET CONDITION ANALYSIS")
    print("-" * 40)
    print(f"📊 Volatility Adjustment: {result.volatility_adjustment:.2f}x")
    print(f"📈 Trend Strength: {result.trend_strength:.1%}")
    print(f"📊 Volume Confirmation: {result.volume_confirmation:.1%}")
    
    # Performance interpretation
    print("\n🎭 INTERPRETATION")
    print("-" * 40)
    
    if result.optimization_score > 0.8:
        print("🌟 EXCELLENT - This is a high-quality setup with strong optimization scores!")
    elif result.optimization_score > 0.7:
        print("✅ GOOD - Solid optimization with good entry and TP/SL settings")
    elif result.optimization_score > 0.6:
        print("⚠️  MODERATE - Acceptable optimization, consider market conditions carefully")
    else:
        print("❌ POOR - Low optimization score, consider waiting for better conditions")
    
    if result.risk_reward_ratio > 3.0:
        print("🎯 Excellent risk/reward ratio - potential for strong profits")
    elif result.risk_reward_ratio > 2.0:
        print("👍 Good risk/reward balance")
    else:
        print("⚠️  Conservative risk/reward - prioritizes safety over profit")
        
    if result.expected_win_rate > 0.65:
        print("🎯 High probability setup - strong win rate expected")
    elif result.expected_win_rate > 0.55:
        print("✅ Balanced probability - good win rate potential")
    else:
        print("⚠️  Lower probability - requires careful risk management")
    
    print("="*80)

async def run_optimization_demo():
    """Run the optimization demonstration"""
    
    print("🚀 VIPER STRATEGY OPTIMIZATION DEMO")
    print("Focus: Entry Points & Optimal TP/SL Settings")
    print("=" * 60)
    
    try:
        # Import the comprehensive optimizer
        from viper.optimization import comprehensive_optimizer
        
        # Demo parameters
        symbols = ["BTCUSDT", "ETHUSDT"]
        timeframes = ["1h", "4h"]
        
        results = []
        
        for symbol in symbols:
            print(f"\n🔍 Analyzing {symbol}...")
            
            # Generate market data
            market_data = generate_realistic_market_data(symbol, days=30)
            current_price = market_data['1h']['close'].iloc[-1]
            account_balance = 10000.0  # $10k demo balance
            
            # Simulate recent performance (could be from database)
            recent_performance = {
                'win_rate': np.random.uniform(0.45, 0.75),  # 45-75% win rate
                'profit_factor': np.random.uniform(1.2, 2.5),  # 1.2-2.5 profit factor
                'total_trades': np.random.randint(50, 200),
                'avg_return_per_trade': np.random.uniform(0.008, 0.025)
            }
            
            for timeframe in timeframes:
                print(f"   ⏰ Optimizing {timeframe} timeframe...")
                
                # Run comprehensive optimization
                result = await comprehensive_optimizer.optimize_strategy_comprehensive(
                    symbol=symbol,
                    timeframe=timeframe,
                    market_data=market_data,
                    current_price=current_price,
                    account_balance=account_balance,
                    recent_performance=recent_performance
                )
                
                results.append(result)
                
                # Print results for this optimization
                print_optimization_results(result)
                
                # Small delay for demo effect
                await asyncio.sleep(0.5)
        
        # Generate comprehensive report
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE OPTIMIZATION REPORT")
        print("="*80)
        
        report = comprehensive_optimizer.get_optimization_report()
        
        print(f"📈 Total Optimizations: {report['total_optimizations']}")
        print(f"🎯 Symbols Analyzed: {report['symbols_analyzed']}")
        
        print(f"\n📊 Average Performance Metrics:")
        metrics = report['average_metrics']
        print(f"   Entry Confidence: {metrics['entry_confidence']:.1%}")
        print(f"   Expected Win Rate: {metrics['expected_win_rate']:.1%}")
        print(f"   Risk/Reward Ratio: {metrics['risk_reward_ratio']:.2f}")
        print(f"   Optimization Score: {metrics['optimization_score']:.1%}")
        
        print(f"\n⭐ Entry Quality Distribution:")
        for quality, count in report['quality_distribution'].items():
            percentage = (count / report['total_optimizations']) * 100
            print(f"   {quality}: {count} ({percentage:.1f}%)")
        
        print(f"\n🏆 Top Performing Optimizations:")
        for i, result in enumerate(report['top_results'], 1):
            print(f"   {i}. {result['symbol']} {result['timeframe']} - "
                  f"Score: {result['score']:.1%}, "
                  f"Win Rate: {result['win_rate']:.1%}, "
                  f"RR: {result['rr_ratio']:.2f}")
        
        print("\n✅ OPTIMIZATION DEMO COMPLETED SUCCESSFULLY!")
        print("The system has demonstrated comprehensive optimization of:")
        print("  • Entry point analysis with multi-factor scoring")
        print("  • Dynamic TP/SL level optimization")
        print("  • Market condition adaptation")
        print("  • Risk-reward optimization")
        print("  • Performance prediction")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you run this script from the correct directory with VIPER modules available")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")

def main():
    """Main demo function"""
    print("Starting VIPER Strategy Optimization Demo...")
    asyncio.run(run_optimization_demo())

if __name__ == "__main__":
    main()