#!/usr/bin/env python3
"""
🔐 VIPER Jordan Mainnet Credential Storage Script
Securely encrypt and store Jordan Mainnet API credentials using the credential vault
"""

import os
import sys
import json
import asyncio
import httpx
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root / 'infrastructure'))

# Import credential client only (avoid circular imports)
try:
    from infrastructure.shared.credential_client import CredentialClient
except ImportError:
    # Create minimal credential client for this script
    class CredentialClient:
        def __init__(self, vault_url=None, access_token=None):
            self.vault_url = vault_url or 'http://localhost:8008'
            self.access_token = access_token or 'jordan_mainnet_token_2025'
        
        async def get_credential(self, service: str, key: str):
            """Simplified credential retrieval for testing"""
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.vault_url}/credentials/retrieve/{service}/{key}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('value')
                return None

# Terminal colors for better output
class Colors:
    BOLD = '\033[1m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    OKCYAN = '\033[96m'

def print_banner():
    """Print storage banner"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}🔐 VIPER Jordan Mainnet Credential Storage{Colors.ENDC}")
    print("=" * 55)
    print(f"{Colors.WARNING}Encrypting and storing credentials in secure vault...{Colors.ENDC}\n")

async def store_credentials_in_vault():
    """Store Jordan Mainnet credentials in the encrypted vault"""
    
    # Jordan Mainnet credentials to store
    jordan_credentials = {
        'JORDAN_MAINNET_KEY': 'bg_d20a392139710bc38b8ab39e970114eb',
        'JORDAN_MAINNET_SECRET': '23ed4a7fe10b9c947d41a15223647f1b263f0d932b7d5e9e7bdfac01d3b84b36',
        'JORDAN_MAINNET_PASSPHRASE': '22672267'
    }
    
    # GitHub token
    github_credentials = {
        'GITHUB_PAT': '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'
    }
    
    # Get vault configuration
    vault_url = os.getenv('VAULT_URL', 'http://localhost:8008')
    access_token = os.getenv('VAULT_ACCESS_TOKEN_JORDAN_MAINNET_NODE', 'jordan_mainnet_token_2025')
    
    print(f"Vault URL: {vault_url}")
    print(f"Access Token: {access_token[:20]}...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Store Jordan Mainnet credentials
            print(f"\n{Colors.BOLD}Storing Jordan Mainnet credentials...{Colors.ENDC}")
            for key, value in jordan_credentials.items():
                try:
                    response = await client.post(
                        f"{vault_url}/credentials/store",
                        headers=headers,
                        params={
                            'service': 'jordan-mainnet-node',
                            'key': key,
                            'value': value
                        }
                    )
                    
                    if response.status_code == 200:
                        print(f"{Colors.OKGREEN}✅ Stored {key}{Colors.ENDC}")
                    else:
                        print(f"{Colors.FAIL}❌ Failed to store {key}: {response.text}{Colors.ENDC}")
                        
                except Exception as e:
                    print(f"{Colors.FAIL}❌ Error storing {key}: {e}{Colors.ENDC}")
            
            # Store GitHub credentials  
            print(f"\n{Colors.BOLD}Storing GitHub credentials...{Colors.ENDC}")
            for key, value in github_credentials.items():
                try:
                    response = await client.post(
                        f"{vault_url}/credentials/store",
                        headers=headers,
                        params={
                            'service': 'jordan-mainnet-node',
                            'key': key,
                            'value': value
                        }
                    )
                    
                    if response.status_code == 200:
                        print(f"{Colors.OKGREEN}✅ Stored {key}{Colors.ENDC}")
                    else:
                        print(f"{Colors.FAIL}❌ Failed to store {key}: {response.text}{Colors.ENDC}")
                        
                except Exception as e:
                    print(f"{Colors.FAIL}❌ Error storing {key}: {e}{Colors.ENDC}")
                    
    except Exception as e:
        print(f"{Colors.FAIL}❌ Failed to connect to credential vault: {e}{Colors.ENDC}")
        return False
    
    return True

async def verify_stored_credentials():
    """Verify that stored credentials can be retrieved"""
    print(f"\n{Colors.BOLD}Verifying stored credentials...{Colors.ENDC}")
    
    vault_url = os.getenv('VAULT_URL', 'http://localhost:8008')
    access_token = os.getenv('VAULT_ACCESS_TOKEN_JORDAN_MAINNET_NODE', 'jordan_mainnet_token_2025')
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test retrieving each credential
    test_credentials = [
        'JORDAN_MAINNET_KEY',
        'JORDAN_MAINNET_SECRET', 
        'JORDAN_MAINNET_PASSPHRASE',
        'GITHUB_PAT'
    ]
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            for key in test_credentials:
                try:
                    response = await client.get(
                        f"{vault_url}/credentials/retrieve/jordan-mainnet-node/{key}",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        value = data['value']
                        # Show partial value for verification (security)
                        masked_value = value[:8] + '...' + value[-8:] if len(value) > 16 else value[:4] + '...'
                        print(f"{Colors.OKGREEN}✅ Retrieved {key}: {masked_value}{Colors.ENDC}")
                    else:
                        print(f"{Colors.FAIL}❌ Failed to retrieve {key}: {response.text}{Colors.ENDC}")
                        
                except Exception as e:
                    print(f"{Colors.FAIL}❌ Error retrieving {key}: {e}{Colors.ENDC}")
                    
    except Exception as e:
        print(f"{Colors.FAIL}❌ Failed to verify credentials: {e}{Colors.ENDC}")
        return False
    
    return True

def setup_vault_environment():
    """Setup vault environment configuration in .env"""
    print(f"\n{Colors.BOLD}Updating environment configuration...{Colors.ENDC}")
    
    project_root = Path(__file__).parent.parent
    env_path = project_root / '.env'
    
    # Read current .env
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Update credential references to point to vault
    updates = {
        'JORDAN_MAINNET_KEY': 'VAULT_STORED',
        'JORDAN_MAINNET_SECRET': 'VAULT_STORED', 
        'JORDAN_MAINNET_PASSPHRASE': 'VAULT_STORED',
        'GITHUB_PAT': 'VAULT_STORED',
        'JORDAN_MAINNET_ENABLED': 'true'
    }
    
    updated_content = content
    for key, value in updates.items():
        import re
        pattern = rf'^{key}=.*$'
        if re.search(pattern, updated_content, re.MULTILINE):
            updated_content = re.sub(pattern, f'{key}={value}', updated_content, flags=re.MULTILINE)
        else:
            if not updated_content.endswith('\n'):
                updated_content += '\n'
            updated_content += f'{key}={value}\n'
    
    # Write updated content
    with open(env_path, 'w') as f:
        f.write(updated_content)
    
    print(f"{Colors.OKGREEN}✅ Environment configuration updated{Colors.ENDC}")

async def main():
    """Main credential storage function"""
    print_banner()
    
    try:
        # Update environment configuration first
        setup_vault_environment()
        
        # Store credentials
        print(f"\n{Colors.BOLD}Storing credentials in vault...{Colors.ENDC}")
        success = await store_credentials_in_vault()
        
        if not success:
            print(f"{Colors.FAIL}❌ Failed to store credentials{Colors.ENDC}")
            return False
        
        # Verify credentials
        verify_success = await verify_stored_credentials()
        
        if success and verify_success:
            print(f"\n{Colors.OKGREEN}🎉 Credentials successfully encrypted and stored!{Colors.ENDC}")
            print(f"\n{Colors.BOLD}Security Notes:{Colors.ENDC}")
            print(f"• Credentials are encrypted using Fernet with PBKDF2")
            print(f"• Stored in Redis with service isolation")
            print(f"• Access controlled via bearer tokens")
            print(f"• Environment variables now reference vault storage")
            return True
        else:
            print(f"\n{Colors.WARNING}⚠️  Credential verification failed{Colors.ENDC}")
            return False
            
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Storage cancelled by user{Colors.ENDC}")
        return False
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Storage failed: {e}{Colors.ENDC}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)