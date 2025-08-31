#!/usr/bin/env python3
"""
# 🚀 VIPER Trading Bot - Logging System Migration Helper
Easy migration from old logging to advanced logging system

This module provides backward compatibility and easy migration paths
from the existing structured_logger.py to the new advanced_logger.py
"""

import warnings
from infrastructure.shared.advanced_logger import (
    AdvancedLogger,
    get_advanced_logger,
    log_advanced_exception,
    performance_monitor,
    performance_trace,
    debug_variable,
    get_system_diagnostics
)


class LegacyLoggerAdapter:
    """
    Adapter to maintain compatibility with existing StructuredLogger usage
    while providing enhanced functionality under the hood
    """
    
    def __init__(self, service_name: str = None):
        self.advanced_logger = get_advanced_logger(service_name)
        self._issue_deprecation_warning()
    
    def _issue_deprecation_warning(self):
        """Issue deprecation warning for old logging system"""
        warnings.warn(
            "StructuredLogger is deprecated. Please migrate to AdvancedLogger for better features. "
            "See infrastructure/shared/advanced_logger.py for documentation.",
            DeprecationWarning,
            stacklevel=3
        )
    
    # Legacy method compatibility
    def log(self, level: str, message: str, correlation_id: str = None,
            trace_id: str = None, data: dict = None, **kwargs):
        """Legacy log method - now using advanced logging"""
        self.advanced_logger.log(level, message, correlation_id, trace_id, data, **kwargs)
    
    def info(self, message: str, correlation_id: str = None, data: dict = None, **kwargs):
        """Legacy info method"""
        self.advanced_logger.info(message, correlation_id=correlation_id, data=data, **kwargs)
    
    def debug(self, message: str, correlation_id: str = None, data: dict = None, **kwargs):
        """Legacy debug method"""
        self.advanced_logger.debug(message, correlation_id=correlation_id, data=data, **kwargs)
    
    def warning(self, message: str, correlation_id: str = None, data: dict = None, **kwargs):
        """Legacy warning method"""
        self.advanced_logger.warning(message, correlation_id=correlation_id, data=data, **kwargs)
    
    def error(self, message: str, correlation_id: str = None, data: dict = None, **kwargs):
        """Legacy error method - now with advanced features"""
        self.advanced_logger.error(message, correlation_id=correlation_id, data=data, **kwargs)
    
    def critical(self, message: str, correlation_id: str = None, data: dict = None, **kwargs):
        """Legacy critical method"""
        self.advanced_logger.critical(message, correlation_id=correlation_id, data=data, **kwargs)
    
    def log_error(self, error: Exception, context: str = "", 
                 correlation_id: str = None, data: dict = None):
        """Legacy error logging - now with advanced traceback"""
        return self.advanced_logger.log_exception(error, context, correlation_id, data=data)
    
    def start_trace(self, operation: str) -> str:
        """Legacy trace start - enhanced version"""
        return self.advanced_logger.profiler.start_operation(operation)
    
    def end_trace(self, trace_id: str, success: bool = True, data: dict = None):
        """Legacy trace end"""
        return self.advanced_logger.profiler.end_operation(trace_id, data)
    
    def trace_operation(self, operation: str):
        """Legacy operation tracing - now performance monitored"""
        return self.advanced_logger.performance_decorator(operation)
    
    # Enhanced legacy methods
    def log_request(self, method: str, endpoint: str, status_code: int,
                   duration: float, correlation_id: str = None, user_id: str = None):
        """Enhanced request logging with performance context"""
        with self.advanced_logger.performance_trace(f"request_{method}_{endpoint}"):
            self.advanced_logger.info(f'{method} {endpoint} -> {status_code}',
                    correlation_id=correlation_id,
                    data={
                        'method': method,
                        'endpoint': endpoint,
                        'status_code': status_code,
                        'duration': duration,
                        'user_id': user_id,
                        'type': 'http_request'
                    })
    
    def log_trade(self, symbol: str, side: str, amount: float, price: float,
                 order_type: str, correlation_id: str = None):
        """Enhanced trade logging with context"""
        with self.advanced_logger.performance_trace(f"trade_{side}_{symbol}"):
            self.advanced_logger.info(f'Trade: {side.upper()} {amount} {symbol} @ {price}',
                    correlation_id=correlation_id,
                    data={
                        'symbol': symbol,
                        'side': side,
                        'amount': amount,
                        'price': price,
                        'order_type': order_type,
                        'trade_value': amount * price,
                        'type': 'trade'
                    })
    
    def get_error_summary(self):
        """Legacy error summary"""
        diagnostics = self.advanced_logger.get_diagnostics()
        return diagnostics.get('error_analytics', {})
    
    def get_log_summary(self):
        """Legacy log summary"""
        return self.advanced_logger.get_diagnostics()


# Create global instances for backward compatibility
logger = LegacyLoggerAdapter()

# Legacy convenience functions with deprecation warnings
def get_logger(service_name: str = None):
    """Legacy function - use get_advanced_logger instead"""
    warnings.warn(
        "get_logger is deprecated. Use get_advanced_logger for enhanced features.",
        DeprecationWarning,
        stacklevel=2
    )
    return LegacyLoggerAdapter(service_name)

def log_info(message: str, **kwargs):
    """Legacy convenience function"""
    logger.info(message, **kwargs)

def log_error(message: str, **kwargs):
    """Legacy convenience function"""
    logger.error(message, **kwargs)

def log_warning(message: str, **kwargs):
    """Legacy convenience function"""
    logger.warning(message, **kwargs)

def log_debug(message: str, **kwargs):
    """Legacy convenience function"""
    logger.debug(message, **kwargs)

def trace_operation(operation: str):
    """Legacy trace operation - now performance monitored"""
    return logger.trace_operation(operation)


# Migration guide
MIGRATION_GUIDE = """
# 🚀 Migration Guide: Structured Logger → Advanced Logger

## Quick Migration (Drop-in Replacement)
Replace imports:
```python
# OLD
from infrastructure.shared.structured_logger import get_logger, log_error

# NEW  
from infrastructure.shared.advanced_logger import get_advanced_logger, log_advanced_exception
```

## Enhanced Usage (Recommended)
```python
from infrastructure.shared.advanced_logger import (
    get_advanced_logger, 
    log_advanced_exception, 
    performance_monitor,
    performance_trace,
    debug_variable
)

# Enhanced logger
logger = get_advanced_logger('my-service')

# Advanced exception handling
try:
    risky_operation()
except Exception as e:
    log_advanced_exception(e, "risky_operation", capture_locals=True, analyze_cause=True)

# Performance monitoring
@performance_monitor("database_operation")
def query_database():
    return db.query("SELECT * FROM trades")

# Context tracing
with performance_trace("complex_calculation"):
    result = complex_calculation()

# Variable debugging
debug_variable("balance", current_balance, watch=True)
```

## Key Improvements
- 🔍 Advanced tracebacks with local variables
- 📊 Root cause analysis for errors
- 🎯 Performance profiling integration  
- 🎨 Rich console formatting
- 🔗 Call graph tracing
- 💾 Memory usage tracking
- 🧵 Thread-safe logging
- 🔄 Async operation support
"""

if __name__ == "__main__":
    print(MIGRATION_GUIDE)