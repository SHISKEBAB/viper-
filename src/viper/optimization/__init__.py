"""
VIPER Optimization Module

Comprehensive strategy optimization focusing on entry points and optimal TP/SL settings.
This module provides advanced optimization capabilities for trading strategies.
"""

from .comprehensive_strategy_optimizer import (
    ComprehensiveStrategyOptimizer,
    OptimizationResult,
    comprehensive_optimizer
)

__all__ = [
    'ComprehensiveStrategyOptimizer',
    'OptimizationResult', 
    'comprehensive_optimizer'
]
