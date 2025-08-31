"""
Jordan Mainnet Node Service

A blockchain node service for Jordan Mainnet integration with the VIPER trading system.
Provides blockchain data access, smart contract interaction, and network monitoring via MCP.
"""

__version__ = "1.0.0"
__author__ = "VIPER Trading System"
__description__ = "Jordan Mainnet Node Service for blockchain operations"

from .main import JordanMainnetNode

__all__ = ["JordanMainnetNode"]
