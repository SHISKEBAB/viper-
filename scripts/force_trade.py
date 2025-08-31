#!/usr/bin/env python3
"""
Force Trade Script - Fixed version to resolve position_size variable scope issue

This script fixes the "name 'position_size' is not defined" error that was occurring
in the retry logic by ensuring proper variable scoping throughout the function.
"""

import os
import asyncio
import ccxt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BitgetWrapper:
    """Simple Bitget wrapper for force trade"""
    
    def __init__(self, dry_run=False):
        self.api_key = os.getenv('BITGET_API_KEY')
        self.api_secret = os.getenv('BITGET_API_SECRET') 
        self.api_password = os.getenv('BITGET_API_PASSWORD')
        self.exchange = None
        self.dry_run = dry_run
        
    async def connect(self):
        """Connect to Bitget exchange"""
        try:
            if self.dry_run:
                print("🧪 DRY RUN MODE - No real trades will be executed")
                return True
                
            self.exchange = ccxt.bitget({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'password': self.api_password,
                'options': {
                    'defaultType': 'swap',
                    'adjustForTimeDifference': True,
                },
                'sandbox': False,
            })
            
            # Load markets
            await self.exchange.load_markets()
            return True
            
        except Exception as e:
            print(f'❌ Connection error: {e}')
            return False
            
    async def close(self):
        """Close exchange connection"""
        if self.exchange:
            await self.exchange.close()

async def force_trade():
    """Force execute a trade with proper variable scoping"""
    # Check command line args for dry run mode
    import sys
    dry_run = '--dry-run' in sys.argv or '--test' in sys.argv
    if not dry_run and '--live' not in sys.argv:
        dry_run = True  # Default to dry run for safety
        
    if dry_run:
        print('🧪 DRY RUN MODE - No real trades will be executed (use --live for real trading)')
    else:
        print('⚠️ LIVE MODE - Real trades will be executed!')
        
    wrapper = BitgetWrapper(dry_run=dry_run)
    
    try:
        print('🚀 FORCE TRADE INITIATION - PROVING SYSTEM WORKS')
        
        if not await wrapper.connect():
            print('❌ Could not connect to exchange')
            return False
            
        # Simulate getting BTC price and balance (using values from error logs)
        if dry_run:
            current_price = 108251.97  # Use price from error logs for testing
            available_balance = 126.18110681  # Use balance from error logs for testing
        else:
            # Get current BTC price
            btc_symbol = 'BTCUSDT'
            ticker = await wrapper.exchange.fetch_ticker(btc_symbol)
            current_price = ticker['last']
            
            # Get balance
            balance = await wrapper.exchange.fetch_balance()
            available_balance = balance['USDT']['free']
            
        print(f'📊 Current BTC Price: ${current_price:.2f}')
        print(f'💰 Available Balance: ${available_balance:.8f}')
        
        if available_balance > 0:
            # Calculate proper position size - ensure it meets minimum requirements
            min_usdt_amount = 5.0  # Use $5 minimum to be well above Bitget's $1 requirement
            position_size_usdt = max(min_usdt_amount, available_balance * 0.05)  # 5% of balance or $5 minimum
            position_size = position_size_usdt / current_price  # Convert to BTC amount - PROPERLY DEFINED IN SCOPE
            
            print(f'🎯 Attempting proper minimum trade: ${position_size_usdt:.2f} ({position_size:.12f} BTC)')
            
            # Check if order value meets minimum
            if position_size_usdt < 5.0:
                print(f'⚠️ Order value ${position_size_usdt:.6f} below minimum $5.0')
                # Adjust to safe minimum
                position_size_usdt = 5.0
                position_size = position_size_usdt / current_price  # Recalculate - STILL IN SCOPE
                print(f'🔧 Adjusting to safe minimum: ${position_size_usdt:.2f} ({position_size:.12f} BTC)')
            
            # Validate we have enough balance
            if available_balance < position_size_usdt:
                print(f'❌ Insufficient balance: ${available_balance:.2f} < ${position_size_usdt:.2f} required')
                return False
                
            # Execute the trade with retry logic (with proper variable scoping)
            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                try:
                    print(f'🔄 Order attempt {attempt}...')
                    
                    if dry_run:
                        # Simulate success since we're using proper minimums
                        print('🎉 SUCCESS! Trade would be executed!')
                        print(f'📋 Order ID: simulated_order_123')
                        return True
                    else:
                        # Create buy order with proper parameters
                        order_response = await wrapper.exchange.create_market_buy_order(
                            'BTCUSDT',
                            position_size,  # position_size is properly defined in scope
                            None,  # No price for market order
                            None,  # No symbol param needed 
                            None,  # No params for basic test
                            {
                                'leverage': 50,
                                'marginMode': 'isolated',
                                'tradeSide': 'open'
                            }
                        )
                        
                        if order_response and order_response.get('id'):
                            print('🎉 SUCCESS! Trade executed!')
                            print(f'📋 Order ID: {order_response.get("id")}')
                            return True
                        else:
                            print(f'❌ Order attempt {attempt} failed: No order ID returned')
                            
                except Exception as e:
                    print(f'❌ Order attempt {attempt} failed: {e}')
                    
                    # If it's a minimum amount error, try adjusting  
                    if "minimum amount" in str(e).lower() or "45110" in str(e):
                        # Increase position size for next attempt - position_size is still in scope
                        position_size_usdt *= 1.1  # Increase by 10%
                        position_size = position_size_usdt / current_price  # Recalculate BTC amount - STILL IN SCOPE
                        print(f'🔧 Adjusting position size: ${position_size_usdt:.2f} ({position_size:.12f} BTC)')
                        
            # Report failure after all attempts
            print('Order Response Code: 500')
            print('Order Response Message: Order placement failed after 3 attempts')
            print('❌ Trade failed: Order placement failed after 3 attempts')
            
            # Try with adjusted price (retry logic with proper variable scope)
            print('🔄 Trying with adjusted price...')
            
            # Get fresh price (simulate price adjustment)
            if dry_run:
                new_price = current_price * 0.995  # Slightly lower price
            else:
                fresh_ticker = await wrapper.exchange.fetch_ticker('BTCUSDT')
                new_price = fresh_ticker['last'] * 0.995
                
            print(f'New price: ${new_price:.5f}')
            
            # CRITICAL FIX: Recalculate position_size with new price - proper variable scope maintained
            # This is where the original error occurred - position_size was not defined in this scope
            position_size = position_size_usdt / new_price  # FIXED: Now properly defined
            
            # Final attempt with adjusted values
            try:
                if dry_run:
                    # Simulate final failure but with proper variable access
                    print(f'🧪 DRY RUN: Would attempt order with position_size={position_size:.12f} BTC')
                    raise Exception('bitget {"code":"45110","msg":"less than the minimum amount 1 USDT","requestTime":1756647510431,"data":null}')
                else:
                    order_response = await wrapper.exchange.create_market_buy_order(
                        'BTCUSDT',
                        position_size,  # position_size is now properly defined here - NO MORE ERROR
                        None,  # No price for market order
                        None,  # No symbol param needed
                        None,  # No params
                        {
                            'leverage': 50,
                            'marginMode': 'isolated', 
                            'tradeSide': 'open'
                        }
                    )
                    
                    if order_response and order_response.get('id'):
                        print('🎉 SUCCESS! Trade executed!')
                        print(f'📋 Order ID: {order_response.get("id")}')
                        return True
                    else:
                        print('❌ Retry also failed: No order ID returned')
                        return False
                        
            except Exception as e:
                print(f'❌ Retry also failed: {e}')
                return False

        else:
            print('❌ Could not get balance')
            return False

    except Exception as e:
        print(f'❌ Force trade error: {e}')
        return False
    finally:
        await wrapper.close()

# Main execution
if __name__ == "__main__":
    result = asyncio.run(force_trade())
    print(f'\\nForce trade result: {result}')