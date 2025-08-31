"""
VIPER Trading Strategies Package

This package contains various trading strategies for the VIPER system:

- fibonacci_strategy: Advanced Fibonacci retracement strategy with golden ratio entries
- golden_ratio_pullback_strategy: Elite pullback strategy focused on golden ratio levels (0.618, 0.786)
- vwma_strategy: Volume Weighted Moving Average strategy
- scalping_grid_strategy: Grid-based scalping strategy
- enhanced_technical_optimizer: Enhanced technical analysis with multiple indicators
- And more...
"""

# Import main strategy modules for easy access
try:
    from .fibonacci_strategy import FibonacciStrategy, get_fibonacci_strategy
except ImportError:
    pass

try:
    from .golden_ratio_pullback_strategy import (
        GoldenRatioPullbackStrategy, 
        get_golden_ratio_pullback_strategy,
        PullbackQuality,
        MarketRegime,
        PullbackSetup,
        PullbackSignal,
        GoldenLevel
    )
except ImportError:
    pass

__all__ = [
    'FibonacciStrategy',
    'get_fibonacci_strategy',
    'GoldenRatioPullbackStrategy',
    'get_golden_ratio_pullback_strategy',
    'PullbackQuality',
    'MarketRegime',
    'PullbackSetup', 
    'PullbackSignal',
    'GoldenLevel'
]
