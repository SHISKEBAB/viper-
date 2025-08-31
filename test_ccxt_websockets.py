#!/usr/bin/env python3
"""
Test CCXT WebSocket functionality with Bitget
"""

import ccxt
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_ccxt_websockets():
    """Test CCXT websocket capabilities"""
    
    # Create exchange instance
    exchange = ccxt.bitget({
        'apiKey': os.getenv('BITGET_API_KEY'),
        'secret': os.getenv('BITGET_API_SECRET'),
        'password': os.getenv('BITGET_API_PASSWORD'),
        'options': {
            'defaultType': 'swap',
        },
        'sandbox': False,
    })
    
    print("🔗 Testing CCXT WebSocket connections...")
    
    try:
        # Test ticker websocket
        print("📊 Testing ticker WebSocket...")
        symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
        
        for i in range(5):  # Test for 5 iterations
            tickers = await exchange.watch_tickers(symbols)
            print(f"📡 Iteration {i+1}: Received {len(tickers)} tickers")
            
            for symbol, ticker in tickers.items():
                price = ticker.get('last', 'N/A')
                print(f"   {symbol}: ${price}")
            
            await asyncio.sleep(2)
        
        print("✅ CCXT WebSocket test completed successfully!")
        
    except Exception as e:
        print(f"❌ WebSocket test error: {e}")
    
    finally:
        # Close exchange connections
        if hasattr(exchange, 'close'):
            await exchange.close()

def main():
    """Run websocket test"""
    print("🚀 CCXT WebSocket Functionality Test")
    print("=" * 50)
    
    # Check API credentials
    if not all([os.getenv('BITGET_API_KEY'), os.getenv('BITGET_API_SECRET'), os.getenv('BITGET_API_PASSWORD')]):
        print("❌ Missing API credentials!")
        return
    
    # Run async test
    asyncio.run(test_ccxt_websockets())

if __name__ == "__main__":
    main()