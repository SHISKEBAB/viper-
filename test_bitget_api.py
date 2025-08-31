#!/usr/bin/env python3
"""
Test Bitget API connection and authentication
"""
import asyncio
import os
import sys
import time
import json
import hmac
import hashlib
import base64
import aiohttp
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.shared.bitget_auth import BitgetAuthenticator

async def test_bitget_api():
    """Test Bitget API connection"""
    print("🔍 Testing Bitget API connection...")

    # Use the exact keys you provided
    api_key = "bg_1798482dc3f4c38b5869ae8215b9b522"
    api_secret = "87a9c37eeb4ef456431649bba0268ebcbefe5a37c14cd3aed004551f686c4997"
    api_password = "22672267"

    print(f"Using API Key: {api_key}")
    print(f"Using API Secret: {api_secret[:10]}...")
    print(f"Using API Password: {api_password}")

    # Initialize authenticator with explicit credentials
    auth = BitgetAuthenticator(
        api_key=api_key,
        api_secret=api_secret,
        api_password=api_password
    )

    print(f"Authenticator API Key: {auth.api_key}")
    print(f"Authenticator API Secret: {auth.api_secret[:10]}...")
    print(f"Authenticator API Password: {auth.api_password}")

    # Test different endpoints to identify the exact issue
    import aiohttp
    import json

    print("\n🔍 Testing different endpoints...")

    # Test 1: Spot account (simpler endpoint)
    print("\n1. Testing Spot Account...")
    headers = auth.get_auth_headers('GET', '/api/spot/v1/account/assets')
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{auth.base_url}/api/spot/v1/account/assets", headers=headers) as response:
            result = await response.json()
            print(f"Spot Account Response: {result}")

    # Test 2: Futures account
    print("\n2. Testing Futures Account...")
    params = {'productType': 'umcbl'}
    headers = auth.get_auth_headers('GET', '/api/mix/v1/account/accounts', params=params)
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    url = f"{auth.base_url}/api/mix/v1/account/accounts?{query_string}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            result = await response.json()
            print(f"Futures Account Response: {result}")

    # Test 3: Debug signature generation for POST vs GET
    print("\n3. DEBUGGING SIGNATURE GENERATION...")

    # First, get Bitget server time to check for time sync issues
    print("   🔍 Checking Bitget server time...")
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.bitget.com/api/spot/v1/public/time") as response:
            time_result = await response.json()
            print(f"   Raw time response: {time_result}")
            
            # Handle different response formats
            if isinstance(time_result, dict):
                data_value = time_result.get('data', 0)
                if isinstance(data_value, str):
                    try:
                        server_time = int(data_value)
                    except ValueError:
                        server_time = int(time.time() * 1000)
                else:
                    server_time = int(data_value)
            elif isinstance(time_result, str):
                try:
                    server_time = int(time_result)
                except ValueError:
                    server_time = int(time.time() * 1000)
            elif isinstance(time_result, (int, float)):
                server_time = int(time_result)
            else:
                server_time = int(time.time() * 1000)
                
            local_time = int(time.time() * 1000)
            time_diff = server_time - local_time
            print(f"   Server time: {server_time}")
            print(f"   Local time: {local_time}")
            print(f"   Time difference: {time_diff} ms")
            if abs(time_diff) > 100:
                print(f"   ⚠️  WARNING: Time difference > 100ms may cause signature validation issues!")

    # Test a working GET request first
    print("\n   🔍 Testing GET request with V1 params...")
    get_params = {'productType': 'UMCBL'}
    start_time = int(time.time() * 1000)
    get_headers = auth.get_auth_headers('GET', '/api/mix/v1/account/account', params=get_params)
    header_time = int(time.time() * 1000)
    print(f"   GET Signature: {get_headers['ACCESS-SIGN'][:30]}...")
    print(f"   GET Timestamp: {get_headers['ACCESS-TIMESTAMP']}")
    print(f"   Header generation took: {header_time - start_time} ms")

    # Test with GET request
    async with aiohttp.ClientSession() as session:
        query_string = '&'.join([f"{k}={v}" for k, v in get_params.items()])
        url = f"{auth.base_url}/api/mix/v1/account/account?{query_string}"
        request_start = int(time.time() * 1000)
        async with session.get(url, headers=get_headers) as response:
            result = await response.json()
            request_end = int(time.time() * 1000)
            print(f"   GET Response: {result.get('code')} - {result.get('msg')}")
            print(f"   Request took: {request_end - request_start} ms")

    # Test with CORRECT USDT futures parameters
    print("\n   🔍 Testing POST request with CORRECT USDT futures parameters...")
    order_params = {
        'symbol': 'BTCUSDT',  # Remove _UMCBL suffix for USDT futures
        'productType': 'USDT-FUTURES',  # Use correct product type
        'marginCoin': 'USDT',
        'size': '1',
        'side': 'open_long',  # USDT futures: open_long, open_short, close_long, close_short
        'orderType': 'market',
        'leverage': '5',
        'marginMode': 'crossed'  # Required: cross or isolated margin mode
    }

    print(f"   Order params: {order_params}")

    # Use the CORRECT V2 API endpoint with V2 parameters
    post_headers = auth.get_auth_headers('POST', '/api/v2/mix/order/place-order', body=order_params)
    print(f"   POST Signature: {post_headers['ACCESS-SIGN'][:30]}...")
    print(f"   POST Timestamp: {post_headers['ACCESS-TIMESTAMP']}")

    # Send POST request using data=body_string (Bitget expects raw JSON string)
    print("   Sending POST request with V2 endpoint + V2 params...")
    body_string = json.dumps(order_params, separators=(',', ':'))
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{auth.base_url}/api/v2/mix/order/place-order", headers=post_headers, data=body_string) as response:
            result = await response.json()
            print(f"   POST Response: {result}")

            if result.get('code') == '00000':
                print("   ✅ SUCCESS: Order placed!")
            else:
                print(f"   ❌ FAILED: {result.get('code')} - {result.get('msg')}")

                # Detailed debugging
                print("\n   🔧 SIGNATURE DEBUGGING (V2 params):")
                timestamp = post_headers['ACCESS-TIMESTAMP']
                body_json = json.dumps(order_params, separators=(',', ':'))
                message = timestamp + 'POST' + '/api/v2/mix/order/place-order' + body_json
                print(f"   Message to sign: {message[:150]}...")
                print(f"   Message length: {len(message)}")
                print(f"   Body JSON: {body_json}")
                print(f"   Current time: {int(time.time() * 1000)}")
                print(f"   Timestamp diff: {int(time.time() * 1000) - int(timestamp)} ms")

                # Manual signature calculation for comparison
                manual_signature = auth.generate_signature(timestamp, 'POST', '/api/v2/mix/order/place-order', body_json)
                print(f"   Manual signature: {manual_signature[:30]}...")
                print(f"   Header signature: {post_headers['ACCESS-SIGN'][:30]}...")
                print(f"   Signatures match: {manual_signature == post_headers['ACCESS-SIGN']}")

    # Test 4: Try different POST request formats to find the correct one
    print("\n4. TESTING DIFFERENT POST REQUEST FORMATS...")

    order_params = {
        'symbol': 'BTCUSDT',  # Remove _UMCBL suffix for USDT futures
        'productType': 'USDT-FUTURES',  # Use correct product type
        'marginCoin': 'USDT',
        'size': '1',
        'side': 'buy',  # Try V1 side values: buy, sell
        'orderType': 'market',
        'leverage': '5',
        'marginMode': 'crossed'  # Required: cross or isolated margin mode
    }

    # Format 1: Using json=body (current method)
    print("   Format 1: Using json=body")
    headers1 = auth.get_auth_headers('POST', '/api/mix/v1/order/placeOrder', body=order_params)
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{auth.base_url}/api/mix/v1/order/placeOrder", headers=headers1, json=order_params) as response:
            result = await response.json()
            print(f"   Result: {result.get('code')} - {result.get('msg')}")

    # Format 2: Using data=json_string (like the main trader was doing)
    print("\n   Format 2: Using data=json_string")
    body_str = json.dumps(order_params, separators=(',', ':'))
    headers2 = auth.get_auth_headers('POST', '/api/mix/v1/order/placeOrder', body=body_str)  # Pass string instead of dict
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{auth.base_url}/api/mix/v1/order/placeOrder", headers=headers2, data=body_str) as response:
            result = await response.json()
            print(f"   Result: {result.get('code')} - {result.get('msg')}")

    # Format 3: Manual signature with json=body
    print("\n   Format 3: Manual signature with V2 json=body")
    timestamp = str(int(time.time() * 1000))
    body_json = json.dumps(order_params, separators=(',', ':'))
    message = timestamp + 'POST' + '/api/v2/mix/order/place-order' + body_json
    signature = hmac.new(
        auth.api_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    manual_sig = base64.b64encode(signature).decode('utf-8')

    manual_headers = {
        'ACCESS-KEY': auth.api_key,
        'ACCESS-SIGN': manual_sig,
        'ACCESS-TIMESTAMP': timestamp,
        'ACCESS-PASSPHRASE': auth.api_password,
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{auth.base_url}/api/mix/v1/order/placeOrder", headers=manual_headers, json=order_params) as response:
            result = await response.json()
            print(f"   Result: {result.get('code')} - {result.get('msg')}")

    # Format 4: Try without leverage (maybe it's causing issues)
    print("\n   Format 4: V2 without leverage parameter")
    simple_params = {
        'symbol': 'BTCUSDT',  # V2 format
        'productType': 'usdt-futures',  # V2 format
        'marginCoin': 'USDT',
        'size': '1',
        'side': 'buy',
        'orderType': 'market'
    }

    headers4 = auth.get_auth_headers('POST', '/api/mix/v1/order/placeOrder', body=simple_params)
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{auth.base_url}/api/mix/v1/order/placeOrder", headers=headers4, json=simple_params) as response:
            result = await response.json()
            print(f"   Result: {result.get('code')} - {result.get('msg')}")

if __name__ == "__main__":
    asyncio.run(test_bitget_api())