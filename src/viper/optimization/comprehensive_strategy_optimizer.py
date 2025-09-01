#!/usr/bin/env python3
"""
🚀 COMPREHENSIVE STRATEGY OPTIMIZER
Full focus on entry points and optimal TP/SL settings as requested

This module combines:
- Enhanced entry point optimization with multi-factor analysis
- Dynamic TP/SL optimization based on market conditions
- Real-time performance feedback and adjustment
- Advanced risk-reward optimization
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import json
from pathlib import Path

# Internal imports
from ..core.advanced_tp_manager import MCPTakeProfitOptimizer, advanced_tp_optimizer
from ..execution.optimized_trade_entry_system import OptimizedTradeEntrySystem, get_optimized_entry_system
from ..strategies.strategy_optimizer_enhanced import SuperiorStrategyOptimizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OptimizationResult:
    """Comprehensive optimization result"""
    symbol: str
    timeframe: str
    strategy_type: str
    
    # Entry optimization results
    entry_confidence: float
    entry_quality: str
    optimal_entry_price: float
    entry_factors: Dict[str, float]
    
    # TP/SL optimization results
    optimal_tp_levels: List[float]
    optimal_tp_allocations: List[float]
    optimal_sl_level: float
    trailing_stop_pct: float
    risk_reward_ratio: float
    
    # Performance metrics
    expected_win_rate: float
    expected_profit_factor: float
    optimization_score: float
    
    # Market condition factors
    volatility_adjustment: float
    trend_strength: float
    volume_confirmation: float
    
    created_at: datetime
    
class ComprehensiveStrategyOptimizer:
    """
    Comprehensive optimizer focusing on entry points and optimal TP/SL settings
    """
    
    def __init__(self):
        self.entry_system = get_optimized_entry_system()
        self.tp_optimizer = advanced_tp_optimizer
        self.strategy_optimizer = SuperiorStrategyOptimizer()
        
        # Results storage
        self.optimization_results: List[OptimizationResult] = []
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Configuration
        self.optimization_config = {
            'min_confidence_threshold': 0.7,
            'min_risk_reward': 2.0,
            'max_risk_reward': 6.0,
            'volatility_lookback_periods': 20,
            'performance_history_limit': 100,
            'reoptimize_frequency_hours': 4
        }
        
        logger.info("🎯 Comprehensive Strategy Optimizer initialized - Full focus on entries and TP/SL")
        
    async def optimize_strategy_comprehensive(self, symbol: str, timeframe: str, 
                                            market_data: Dict[str, pd.DataFrame],
                                            current_price: float,
                                            account_balance: float,
                                            recent_performance: Optional[Dict[str, Any]] = None) -> OptimizationResult:
        """
        Perform comprehensive strategy optimization focusing on entry points and TP/SL settings
        """
        
        logger.info(f"🚀 Starting comprehensive optimization for {symbol} {timeframe}")
        
        try:
            # Step 1: Analyze current market conditions
            market_conditions = await self._analyze_market_conditions(symbol, market_data, current_price)
            
            # Step 2: Optimize entry points with enhanced analysis
            entry_optimization = await self._optimize_entry_points(
                symbol, market_data, current_price, account_balance, market_conditions
            )
            
            # Step 3: Optimize TP/SL levels dynamically
            tpsl_optimization = await self._optimize_tp_sl_levels(
                symbol, market_conditions, recent_performance, entry_optimization
            )
            
            # Step 4: Calculate comprehensive optimization score
            optimization_score = self._calculate_comprehensive_score(
                entry_optimization, tpsl_optimization, market_conditions
            )
            
            # Step 5: Create optimization result
            result = OptimizationResult(
                symbol=symbol,
                timeframe=timeframe,
                strategy_type="comprehensive_optimized",
                
                # Entry results
                entry_confidence=entry_optimization['confidence'],
                entry_quality=entry_optimization['quality'],
                optimal_entry_price=entry_optimization['entry_price'],
                entry_factors=entry_optimization['factors'],
                
                # TP/SL results
                optimal_tp_levels=tpsl_optimization['levels'],
                optimal_tp_allocations=tpsl_optimization['allocations'],
                optimal_sl_level=tpsl_optimization['stop_loss'],
                trailing_stop_pct=tpsl_optimization['trailing_pct'],
                risk_reward_ratio=tpsl_optimization['risk_reward'],
                
                # Performance metrics
                expected_win_rate=self._estimate_win_rate(entry_optimization, tpsl_optimization),
                expected_profit_factor=self._estimate_profit_factor(tpsl_optimization),
                optimization_score=optimization_score,
                
                # Market factors
                volatility_adjustment=market_conditions['volatility_adjustment'],
                trend_strength=market_conditions['trend_strength'],
                volume_confirmation=market_conditions['volume_confirmation'],
                
                created_at=datetime.now()
            )
            
            # Store result
            self.optimization_results.append(result)
            
            logger.info(f"✅ Optimization complete - Score: {optimization_score:.3f}, "
                      f"Expected Win Rate: {result.expected_win_rate:.1%}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Optimization failed for {symbol}: {e}")
            return self._create_fallback_result(symbol, timeframe, current_price)
    
    async def _analyze_market_conditions(self, symbol: str, market_data: Dict[str, pd.DataFrame],
                                       current_price: float) -> Dict[str, Any]:
        """Analyze current market conditions for optimization"""
        
        try:
            conditions = {}
            
            # Get primary timeframe data
            primary_df = list(market_data.values())[0] if market_data else None
            if primary_df is None or len(primary_df) < 20:
                return self._default_market_conditions()
                
            # Volatility analysis
            returns = primary_df['close'].pct_change().dropna()
            volatility = returns.rolling(self.optimization_config['volatility_lookback_periods']).std().iloc[-1]
            conditions['volatility'] = volatility
            conditions['volatility_adjustment'] = min(2.0, max(0.5, volatility / 0.02))
            
            # Trend strength analysis
            sma_20 = primary_df['close'].rolling(20).mean().iloc[-1]
            sma_50 = primary_df['close'].rolling(50).mean().iloc[-1] if len(primary_df) >= 50 else sma_20
            
            trend_strength = abs(current_price - sma_20) / current_price
            conditions['trend_strength'] = min(1.0, trend_strength * 10)  # Scale to 0-1
            
            # Volume analysis
            avg_volume = primary_df['volume'].rolling(20).mean().iloc[-1]
            current_volume = primary_df['volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            conditions['volume_ratio'] = volume_ratio
            conditions['volume_confirmation'] = min(1.0, max(0.3, volume_ratio / 1.5))
            
            # Price momentum
            momentum_5 = primary_df['close'].pct_change(5).iloc[-1]
            momentum_10 = primary_df['close'].pct_change(10).iloc[-1]
            conditions['momentum_5'] = momentum_5
            conditions['momentum_10'] = momentum_10
            
            # Market phase identification
            if abs(momentum_5) > volatility * 2:
                conditions['market_phase'] = 'breakout'
            elif trend_strength > 0.02:
                conditions['market_phase'] = 'trending'
            elif volatility < 0.015:
                conditions['market_phase'] = 'consolidation'
            else:
                conditions['market_phase'] = 'normal'
                
            return conditions
            
        except Exception as e:
            logger.warning(f"Market condition analysis failed: {e}")
            return self._default_market_conditions()
    
    async def _optimize_entry_points(self, symbol: str, market_data: Dict[str, pd.DataFrame],
                                   current_price: float, account_balance: float,
                                   market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize entry points with enhanced analysis"""
        
        try:
            # Get optimized entry signals
            entry_signals = await self.entry_system.analyze_optimal_entries(
                symbol, market_data, current_price, account_balance
            )
            
            if not entry_signals:
                return self._default_entry_optimization(current_price)
                
            # Select best signal
            best_signal = entry_signals[0]  # Already sorted by confidence
            
            # Enhanced entry analysis
            entry_factors = {
                'base_confidence': best_signal.confidence_score,
                'timeframe_confluence': best_signal.timeframe_confluence,
                'volume_confirmation': best_signal.volume_confirmation,
                'market_structure': best_signal.market_structure_score,
                'momentum_alignment': market_conditions.get('momentum_5', 0) * 10,  # Scale to factor
                'trend_alignment': market_conditions.get('trend_strength', 0.5)
            }
            
            # Market condition adjustments
            volatility_adj = market_conditions.get('volatility_adjustment', 1.0)
            if market_conditions.get('market_phase') == 'breakout':
                confidence_boost = 1.15
            elif market_conditions.get('market_phase') == 'trending':
                confidence_boost = 1.1
            else:
                confidence_boost = 1.0
                
            # Adjust confidence for market conditions
            adjusted_confidence = min(0.95, best_signal.confidence_score * confidence_boost / volatility_adj)
            
            return {
                'confidence': adjusted_confidence,
                'quality': self.entry_system._determine_entry_quality(adjusted_confidence),
                'entry_price': best_signal.entry_price,
                'direction': best_signal.direction,
                'factors': entry_factors,
                'original_signal': best_signal
            }
            
        except Exception as e:
            logger.warning(f"Entry optimization failed: {e}")
            return self._default_entry_optimization(current_price)
    
    async def _optimize_tp_sl_levels(self, symbol: str, market_conditions: Dict[str, Any],
                                   recent_performance: Optional[Dict[str, Any]],
                                   entry_optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize TP/SL levels dynamically based on conditions"""
        
        try:
            # Use recent performance or defaults
            if recent_performance is None:
                recent_performance = {'win_rate': 0.55, 'profit_factor': 1.5}
                
            # Dynamic TP optimization
            tp_config = self.tp_optimizer.optimize_tp_levels_dynamically(
                symbol, market_conditions, recent_performance
            )
            
            # Calculate optimal stop loss based on volatility and entry confidence
            base_sl = 0.015  # 1.5% base
            volatility = market_conditions.get('volatility', 0.02)
            volatility_multiplier = max(0.7, min(1.8, volatility / 0.02))
            
            # Adjust SL based on entry confidence
            confidence = entry_optimization.get('confidence', 0.5)
            confidence_multiplier = 1.2 - (confidence * 0.4)  # Higher confidence = tighter SL
            
            optimal_sl = base_sl * volatility_multiplier * confidence_multiplier
            optimal_sl = max(0.008, min(0.04, optimal_sl))  # Cap between 0.8% and 4%
            
            # Calculate risk-reward ratios
            avg_tp = np.average(tp_config['levels'], weights=tp_config['allocations'])
            risk_reward = avg_tp / optimal_sl
            
            # Ensure minimum risk-reward ratio
            if risk_reward < self.optimization_config['min_risk_reward']:
                scale_factor = self.optimization_config['min_risk_reward'] / risk_reward
                tp_config['levels'] = [level * scale_factor for level in tp_config['levels']]
                risk_reward = self.optimization_config['min_risk_reward']
            
            # Cap maximum risk-reward ratio
            if risk_reward > self.optimization_config['max_risk_reward']:
                scale_factor = self.optimization_config['max_risk_reward'] / risk_reward
                tp_config['levels'] = [level * scale_factor for level in tp_config['levels']]
                risk_reward = self.optimization_config['max_risk_reward']
            
            return {
                'levels': tp_config['levels'],
                'allocations': tp_config['allocations'],
                'stop_loss': optimal_sl,
                'trailing_pct': tp_config['trailing_pct'],
                'risk_reward': risk_reward,
                'tp_level_type': tp_config['tp_level'].value,
                'optimization_score': tp_config.get('optimization_score', 0.7)
            }
            
        except Exception as e:
            logger.warning(f"TP/SL optimization failed: {e}")
            return self._default_tpsl_optimization()
    
    def _calculate_comprehensive_score(self, entry_optimization: Dict[str, Any],
                                     tpsl_optimization: Dict[str, Any],
                                     market_conditions: Dict[str, Any]) -> float:
        """Calculate comprehensive optimization score"""
        
        try:
            # Entry score (40% weight)
            entry_score = entry_optimization.get('confidence', 0.5) * 0.4
            
            # TP/SL score (35% weight)
            tpsl_score = tpsl_optimization.get('optimization_score', 0.5) * 0.35
            
            # Risk-reward score (15% weight)
            rr_ratio = tpsl_optimization.get('risk_reward', 2.0)
            rr_score = min(1.0, (rr_ratio - 1.0) / 4.0) * 0.15  # Normalize 1-5 range to 0-1
            
            # Market condition score (10% weight)
            market_score = (
                market_conditions.get('volume_confirmation', 0.5) * 0.5 +
                min(1.0, market_conditions.get('trend_strength', 0.5)) * 0.5
            ) * 0.1
            
            total_score = entry_score + tpsl_score + rr_score + market_score
            
            return min(1.0, total_score)
            
        except Exception:
            return 0.5
    
    def _estimate_win_rate(self, entry_optimization: Dict[str, Any],
                          tpsl_optimization: Dict[str, Any]) -> float:
        """Estimate expected win rate based on optimization"""
        
        try:
            base_win_rate = 0.55  # Base 55%
            
            # Entry quality adjustment
            confidence = entry_optimization.get('confidence', 0.5)
            entry_adjustment = (confidence - 0.5) * 0.4  # Max ±20% adjustment
            
            # Risk-reward adjustment (tighter stops may reduce win rate slightly)
            rr_ratio = tpsl_optimization.get('risk_reward', 2.0)
            if rr_ratio > 3.0:
                rr_adjustment = -0.05  # Slightly lower win rate for very high RR
            elif rr_ratio < 2.0:
                rr_adjustment = 0.05   # Higher win rate for conservative RR
            else:
                rr_adjustment = 0
                
            estimated_win_rate = base_win_rate + entry_adjustment + rr_adjustment
            return max(0.4, min(0.8, estimated_win_rate))
            
        except Exception:
            return 0.55
    
    def _estimate_profit_factor(self, tpsl_optimization: Dict[str, Any]) -> float:
        """Estimate expected profit factor"""
        
        try:
            # Base profit factor from risk-reward ratio
            rr_ratio = tpsl_optimization.get('risk_reward', 2.0)
            base_pf = rr_ratio * 0.6  # Conservative estimate
            
            # Adjustment for TP level distribution
            allocations = tpsl_optimization.get('allocations', [0.33, 0.33, 0.34])
            
            # Front-loaded allocations may improve profit factor
            front_weight = allocations[0] if allocations else 0.33
            if front_weight > 0.4:
                pf_adjustment = 1.1
            elif front_weight < 0.2:
                pf_adjustment = 1.05
            else:
                pf_adjustment = 1.0
                
            return min(3.5, base_pf * pf_adjustment)
            
        except Exception:
            return 1.8
    
    def _default_market_conditions(self) -> Dict[str, Any]:
        """Default market conditions fallback"""
        return {
            'volatility': 0.02,
            'volatility_adjustment': 1.0,
            'trend_strength': 0.5,
            'volume_ratio': 1.0,
            'volume_confirmation': 0.7,
            'momentum_5': 0.0,
            'momentum_10': 0.0,
            'market_phase': 'normal'
        }
    
    def _default_entry_optimization(self, current_price: float) -> Dict[str, Any]:
        """Default entry optimization fallback"""
        return {
            'confidence': 0.6,
            'quality': 'GOOD',
            'entry_price': current_price,
            'direction': 'buy',
            'factors': {
                'base_confidence': 0.6,
                'timeframe_confluence': 0.5,
                'volume_confirmation': 0.6,
                'market_structure': 0.5,
                'momentum_alignment': 0.5,
                'trend_alignment': 0.5
            }
        }
    
    def _default_tpsl_optimization(self) -> Dict[str, Any]:
        """Default TP/SL optimization fallback"""
        return {
            'levels': [0.02, 0.045, 0.08],
            'allocations': [0.3, 0.4, 0.3],
            'stop_loss': 0.018,
            'trailing_pct': 0.012,
            'risk_reward': 2.5,
            'tp_level_type': 'MODERATE',
            'optimization_score': 0.6
        }
    
    def _create_fallback_result(self, symbol: str, timeframe: str, current_price: float) -> OptimizationResult:
        """Create fallback optimization result"""
        return OptimizationResult(
            symbol=symbol,
            timeframe=timeframe,
            strategy_type="fallback",
            
            entry_confidence=0.6,
            entry_quality="GOOD",
            optimal_entry_price=current_price,
            entry_factors={},
            
            optimal_tp_levels=[0.02, 0.045, 0.08],
            optimal_tp_allocations=[0.3, 0.4, 0.3],
            optimal_sl_level=0.018,
            trailing_stop_pct=0.012,
            risk_reward_ratio=2.5,
            
            expected_win_rate=0.55,
            expected_profit_factor=1.8,
            optimization_score=0.6,
            
            volatility_adjustment=1.0,
            trend_strength=0.5,
            volume_confirmation=0.7,
            
            created_at=datetime.now()
        )
    
    def get_optimization_report(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive optimization report"""
        
        results = self.optimization_results
        if symbol:
            results = [r for r in results if r.symbol == symbol]
            
        if not results:
            return {"error": "No optimization results available"}
        
        # Calculate aggregate metrics
        avg_confidence = np.mean([r.entry_confidence for r in results])
        avg_win_rate = np.mean([r.expected_win_rate for r in results])
        avg_rr_ratio = np.mean([r.risk_reward_ratio for r in results])
        avg_optimization_score = np.mean([r.optimization_score for r in results])
        
        # Quality distribution
        quality_dist = {}
        for result in results:
            quality = result.entry_quality
            quality_dist[quality] = quality_dist.get(quality, 0) + 1
            
        # Top performing results
        top_results = sorted(results, key=lambda r: r.optimization_score, reverse=True)[:5]
        
        return {
            "total_optimizations": len(results),
            "symbols_analyzed": len(set(r.symbol for r in results)),
            "average_metrics": {
                "entry_confidence": avg_confidence,
                "expected_win_rate": avg_win_rate,
                "risk_reward_ratio": avg_rr_ratio,
                "optimization_score": avg_optimization_score
            },
            "quality_distribution": quality_dist,
            "top_results": [
                {
                    "symbol": r.symbol,
                    "timeframe": r.timeframe,
                    "confidence": r.entry_confidence,
                    "win_rate": r.expected_win_rate,
                    "rr_ratio": r.risk_reward_ratio,
                    "score": r.optimization_score
                }
                for r in top_results
            ]
        }

# Global optimizer instance
comprehensive_optimizer = ComprehensiveStrategyOptimizer()

async def main():
    """Example usage of comprehensive optimizer"""
    
    # Generate sample market data
    dates = pd.date_range(start='2024-01-01', periods=200, freq='1H')
    sample_data = pd.DataFrame({
        'open': np.random.uniform(95, 105, 200),
        'high': np.random.uniform(100, 110, 200),
        'low': np.random.uniform(90, 100, 200),
        'close': np.random.uniform(95, 105, 200),
        'volume': np.random.uniform(1000, 2000, 200)
    }, index=dates)
    
    market_data = {
        '1h': sample_data,
        '4h': sample_data.resample('4H').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
        })
    }
    
    # Run optimization
    result = await comprehensive_optimizer.optimize_strategy_comprehensive(
        symbol="BTCUSDT",
        timeframe="1h", 
        market_data=market_data,
        current_price=100.0,
        account_balance=1000.0
    )
    
    # Display results
    print("🎯 COMPREHENSIVE OPTIMIZATION RESULTS")
    print("=" * 50)
    print(f"Symbol: {result.symbol}")
    print(f"Entry Confidence: {result.entry_confidence:.1%}")
    print(f"Entry Quality: {result.entry_quality}")
    print(f"Optimal Entry: ${result.optimal_entry_price:.2f}")
    print(f"TP Levels: {[f'{tp:.1%}' for tp in result.optimal_tp_levels]}")
    print(f"TP Allocations: {[f'{alloc:.1%}' for alloc in result.optimal_tp_allocations]}")
    print(f"Stop Loss: {result.optimal_sl_level:.1%}")
    print(f"Risk/Reward: {result.risk_reward_ratio:.2f}")
    print(f"Expected Win Rate: {result.expected_win_rate:.1%}")
    print(f"Optimization Score: {result.optimization_score:.1%}")
    print("=" * 50)
    
    # Get report
    report = comprehensive_optimizer.get_optimization_report()
    print("\n📊 OPTIMIZATION REPORT")
    print(json.dumps(report, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())