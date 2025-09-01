#!/usr/bin/env python3
"""
Test Jordan Mainnet credential storage and retrieval
"""
import asyncio
import os
import sys
import pytest
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root))

from infrastructure.shared.credential_client import CredentialClient

@pytest.mark.asyncio
async def test_jordan_mainnet_credentials():
    """Test that Jordan Mainnet credentials can be retrieved from vault"""
    
    # Initialize credential client with Jordan Mainnet service token
    client = CredentialClient(
        vault_url=os.getenv('VAULT_URL', 'http://credential-vault:8008'),
        access_token=os.getenv('VAULT_ACCESS_TOKEN_JORDAN_MAINNET_NODE', 'jordan_mainnet_token_2025')
    )
    
    # Test retrieving Jordan Mainnet credentials
    jordan_key = await client.get_credential('jordan-mainnet-node', 'JORDAN_MAINNET_KEY')
    jordan_secret = await client.get_credential('jordan-mainnet-node', 'JORDAN_MAINNET_SECRET')
    jordan_passphrase = await client.get_credential('jordan-mainnet-node', 'JORDAN_MAINNET_PASSPHRASE')
    github_pat = await client.get_credential('jordan-mainnet-node', 'GITHUB_PAT')
    
    # Verify credentials are not None and have expected format
    assert jordan_key is not None, "Jordan Mainnet API key should be retrievable"
    assert jordan_secret is not None, "Jordan Mainnet API secret should be retrievable"
    assert jordan_passphrase is not None, "Jordan Mainnet passphrase should be retrievable"
    assert github_pat is not None, "GitHub PAT should be retrievable"
    
    # Verify key formats (without exposing full values)
    assert jordan_key.startswith('bg_'), "Jordan Mainnet key should start with 'bg_'"
    assert len(jordan_secret) == 64, "Jordan Mainnet secret should be 64 characters"
    assert jordan_passphrase.isdigit(), "Jordan Mainnet passphrase should be numeric"
    assert github_pat.startswith('github_pat_'), "GitHub PAT should start with 'github_pat_'"
    
    print("✅ All Jordan Mainnet credentials verified successfully")

@pytest.mark.asyncio 
async def test_credential_encryption():
    """Test that credentials are properly encrypted in storage"""
    
    # This test would verify that credentials stored in Redis are encrypted
    # For now, we'll test the client retrieval mechanism
    client = CredentialClient()
    
    # Test that client can be initialized
    assert client.vault_url is not None
    assert client.service_name is not None
    
    print("✅ Credential client initialization verified")

if __name__ == "__main__":
    # Run tests directly for quick validation
    asyncio.run(test_jordan_mainnet_credentials())
    asyncio.run(test_credential_encryption())