#!/usr/bin/env python3
"""
🚀 VIPER Trading System - Quick 50X Leverage Pairs List
Simple utility to get the list of pairs supporting 50x leverage

Usage:
    python get_50x_pairs.py                  # Print pairs list
    python get_50x_pairs.py --format json    # JSON format
    python get_50x_pairs.py --with-leverage  # Include leverage levels
"""

import json
import argparse


def get_50x_leverage_pairs():
    """Get list of pairs supporting 50x+ leverage with their maximum leverage"""
    return {
        # High leverage pairs (75x+)
        'BTC/USDT:USDT': 125,
        'ETH/USDT:USDT': 100,
        'BNB/USDT:USDT': 75,
        'SOL/USDT:USDT': 75,
        'ADA/USDT:USDT': 75,
        'DOGE/USDT:USDT': 75,
        'XRP/USDT:USDT': 75,
        'LTC/USDT:USDT': 75,
        'BCH/USDT:USDT': 75,
        
        # Standard 50x leverage pairs
        'MATIC/USDT:USDT': 50,
        'LINK/USDT:USDT': 50,
        'UNI/USDT:USDT': 50,
        'AVAX/USDT:USDT': 50,
        'DOT/USDT:USDT': 50,
        'NEAR/USDT:USDT': 50,
        'FTM/USDT:USDT': 50,
        'ATOM/USDT:USDT': 50,
        'ETC/USDT:USDT': 50,
    }


def get_pairs_by_leverage_tier():
    """Get pairs organized by leverage tiers"""
    pairs = get_50x_leverage_pairs()
    
    tiers = {
        'ultra_high': [],  # 100x+
        'high': [],        # 75x-99x
        'standard': []     # 50x-74x
    }
    
    for symbol, max_leverage in pairs.items():
        if max_leverage >= 100:
            tiers['ultra_high'].append((symbol, max_leverage))
        elif max_leverage >= 75:
            tiers['high'].append((symbol, max_leverage))
        else:
            tiers['standard'].append((symbol, max_leverage))
    
    return tiers


def main():
    parser = argparse.ArgumentParser(
        description='🚀 Quick 50X Leverage Pairs List',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--format', 
        choices=['text', 'json', 'python'],
        default='text',
        help='Output format'
    )
    
    parser.add_argument(
        '--with-leverage', 
        action='store_true',
        help='Include leverage levels'
    )
    
    parser.add_argument(
        '--tiers', 
        action='store_true',
        help='Group by leverage tiers'
    )
    
    parser.add_argument(
        '--symbols-only', 
        action='store_true',
        help='Output only symbol names'
    )

    args = parser.parse_args()
    
    pairs_data = get_50x_leverage_pairs()
    
    if args.tiers:
        tiers = get_pairs_by_leverage_tier()
        if args.format == 'json':
            print(json.dumps(tiers, indent=2))
        else:
            print("🚀 50X+ LEVERAGE PAIRS BY TIER")
            print("=" * 50)
            
            print(f"\n🏆 ULTRA HIGH LEVERAGE (100x+): {len(tiers['ultra_high'])} pairs")
            for symbol, leverage in sorted(tiers['ultra_high'], key=lambda x: x[1], reverse=True):
                print(f"  • {symbol:<20} | {leverage}x")
                
            print(f"\n🔥 HIGH LEVERAGE (75x+): {len(tiers['high'])} pairs")
            for symbol, leverage in sorted(tiers['high'], key=lambda x: x[1], reverse=True):
                print(f"  • {symbol:<20} | {leverage}x")
                
            print(f"\n⚡ STANDARD 50X LEVERAGE: {len(tiers['standard'])} pairs")
            for symbol, leverage in sorted(tiers['standard'], key=lambda x: x[1], reverse=True):
                print(f"  • {symbol:<20} | {leverage}x")
                
    elif args.symbols_only:
        symbols = list(pairs_data.keys())
        if args.format == 'json':
            print(json.dumps(symbols, indent=2))
        elif args.format == 'python':
            print("VIPER_50X_PAIRS = [")
            for symbol in symbols:
                print(f"    '{symbol}',")
            print("]")
        else:
            for symbol in symbols:
                print(symbol)
                
    elif args.with_leverage:
        if args.format == 'json':
            print(json.dumps(pairs_data, indent=2))
        elif args.format == 'python':
            print("VIPER_50X_LEVERAGE_MAP = {")
            for symbol, leverage in sorted(pairs_data.items(), key=lambda x: x[1], reverse=True):
                print(f"    '{symbol}': {leverage},")
            print("}")
        else:
            print("🚀 50X+ LEVERAGE PAIRS WITH MAX LEVERAGE")
            print("=" * 50)
            for symbol, leverage in sorted(pairs_data.items(), key=lambda x: x[1], reverse=True):
                print(f"{symbol:<25} | {leverage}x")
                
    else:
        # Default: simple list
        if args.format == 'json':
            print(json.dumps(list(pairs_data.keys()), indent=2))
        elif args.format == 'python':
            print("# VIPER 50x Leverage Pairs")
            print("pairs_50x = [")
            for symbol in pairs_data.keys():
                print(f"    '{symbol}',")
            print("]")
        else:
            print("🚀 PAIRS SUPPORTING 50X+ LEVERAGE")
            print("-" * 40)
            for symbol in pairs_data.keys():
                print(f"• {symbol}")
                
    print(f"\nTotal: {len(pairs_data)} pairs support 50x+ leverage")


if __name__ == "__main__":
    main()