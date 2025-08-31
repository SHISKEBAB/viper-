#!/usr/bin/env python3
"""
# Rocket VIPER Trading Bot - Enhanced Structured Logger
Unified logging utility for all microservices - Now with Advanced Features!

This module provides backward compatibility with the original StructuredLogger
while offering enhanced capabilities through the new AdvancedLogger system.

Features:
- 🚀 UPGRADED: Advanced traceback capture with local variables
- 🚀 UPGRADED: Root cause analysis for errors  
- 🚀 UPGRADED: Performance profiling integration
- 🚀 UPGRADED: Rich console formatting with colors
- 🚀 NEW: Call graph tracing and memory monitoring
- 🚀 NEW: Interactive debugging capabilities
- ✅ COMPATIBLE: Drop-in replacement for existing StructuredLogger
"""

import warnings
import os
from typing import Dict, Any

# Import the advanced logging system
try:
    from .advanced_logger import (
        AdvancedLogger,
        get_advanced_logger, 
        log_advanced_exception,
        performance_monitor,
        performance_trace,
        debug_variable,
        get_system_diagnostics
    )
    ADVANCED_LOGGER_AVAILABLE = True
except ImportError:
    ADVANCED_LOGGER_AVAILABLE = False
    warnings.warn("Advanced logger not available, falling back to basic logging", ImportWarning)

# Fallback to basic logging if advanced is not available
if not ADVANCED_LOGGER_AVAILABLE:
    import json
    import logging
    import time
    from datetime import datetime
    from collections import deque
    
    # Load environment variables
    REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
    SERVICE_NAME = os.getenv('SERVICE_NAME', 'unknown-service')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class StructuredLogger:
    """
    Enhanced Structured Logger with Advanced Features
    
    This class now uses the AdvancedLogger under the hood while maintaining
    full backward compatibility with existing code.
    """
    
    def __init__(self, service_name: str = None):
        if ADVANCED_LOGGER_AVAILABLE:
            # Use advanced logger
            self._logger = get_advanced_logger(service_name)
            self.service_name = self._logger.service_name
            self.correlation_id = self._logger.correlation_id
            self.trace_stack = self._logger.trace_stack
            self.is_connected = self._logger.is_connected
            
            # Show upgrade notice once
            if not getattr(self.__class__, '_upgrade_notice_shown', False):
                self._logger.info("🚀 Enhanced logging system activated with advanced features!")
                self.__class__._upgrade_notice_shown = True
        else:
            # Fallback to basic implementation
            self._init_basic_logger(service_name)
    
    def _init_basic_logger(self, service_name: str = None):
        """Initialize basic logger as fallback"""
        self.service_name = service_name or SERVICE_NAME
        self.redis_client = None
        self.log_buffer = deque(maxlen=1000)
        self.correlation_id = self._generate_correlation_id()
        self.trace_stack = []
        self.performance_metrics = {}
        self.error_counts = {}
        self.is_connected = False
        
        # Try to connect to Redis
        try:
            import redis
            self.redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
            self.redis_client.ping()
            self.is_connected = True
        except Exception:
            self.is_connected = False
        
        self._setup_standard_logging()
    
    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _setup_standard_logging(self):
        """Setup standard Python logging with structured format (basic fallback)"""
        if not ADVANCED_LOGGER_AVAILABLE:
            log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
            
            class StructuredFormatter(logging.Formatter):
                def format(self, record):
                    log_entry = {
                        'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                        'service': SERVICE_NAME,
                        'level': record.levelname,
                        'message': record.getMessage(),
                        'module': record.module,
                        'function': record.funcName,
                        'line': record.lineno,
                        'correlation_id': getattr(record, 'correlation_id', None),
                        'trace_id': getattr(record, 'trace_id', None),
                        'data': getattr(record, 'data', {})
                    }
                    return json.dumps(log_entry)
            
            self.logger = logging.getLogger(self.service_name)
            self.logger.setLevel(log_level)
            
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
            
            handler = logging.StreamHandler()
            handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(handler)

    def log(self, level: str, message: str, correlation_id: str = None,
            trace_id: str = None, data: Dict = None, **kwargs):
        """Enhanced log method - uses advanced logging if available"""
        if ADVANCED_LOGGER_AVAILABLE:
            # Use advanced logging
            self._logger.log(level, message, correlation_id, trace_id, data, **kwargs)
        else:
            # Fallback to basic logging
            self._basic_log(level, message, correlation_id, trace_id, data, **kwargs)
    
    def _basic_log(self, level: str, message: str, correlation_id: str = None,
                  trace_id: str = None, data: Dict = None, **kwargs):
        """Basic logging fallback implementation"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'service': self.service_name,
                'level': level.upper(),
                'message': message,
                'correlation_id': correlation_id or self.correlation_id,
                'trace_id': trace_id or (self.trace_stack[-1] if self.trace_stack else self.correlation_id),
                'data': data or {},
                **kwargs
            }
            
            self.log_buffer.append(log_entry)
            
            if level.upper() == 'ERROR':
                error_key = data.get('error_type', 'unknown') if data else 'unknown'
                self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
            
            if self.is_connected and self.redis_client:
                channel = f'logs:{self.service_name}'
                self.redis_client.publish(channel, json.dumps(log_entry))
            
            log_method = getattr(self.logger, level.lower(), self.logger.info)
            extra_data = {
                'correlation_id': log_entry['correlation_id'],
                'trace_id': log_entry['trace_id'],
                'data': log_entry['data']
            }
            log_method(message, extra=extra_data)
            
        except Exception as e:
            print(f"[{self.service_name}] {level.upper()}: {message} | Error: {e}")

    def _get_current_trace_id(self) -> str:
        """Get current trace ID from stack"""
        if ADVANCED_LOGGER_AVAILABLE:
            return self._logger._get_current_trace_id()
        return self.trace_stack[-1] if self.trace_stack else self.correlation_id

    def start_trace(self, operation: str) -> str:
        """Start a new trace for operation tracking - enhanced"""
        if ADVANCED_LOGGER_AVAILABLE:
            return self._logger.profiler.start_operation(operation)
        else:
            # Basic implementation
            trace_id = f"{operation}_{int(time.time() * 1000)}"
            self.trace_stack.append(trace_id)
            self.log('DEBUG', f'Starting operation: {operation}',
                    trace_id=trace_id,
                    data={'operation': operation, 'type': 'trace_start'})
            return trace_id

    def end_trace(self, trace_id: str, success: bool = True, data: Dict = None):
        """End a trace - enhanced"""
        if ADVANCED_LOGGER_AVAILABLE:
            return self._logger.profiler.end_operation(trace_id, data)
        else:
            # Basic implementation
            if self.trace_stack and self.trace_stack[-1] == trace_id:
                self.trace_stack.pop()
            
            self.log('DEBUG', f'Ending trace: {trace_id}',
                    trace_id=trace_id,
                    data={
                        'success': success,
                        'type': 'trace_end',
                        **(data or {})
                    })

    def trace_operation(self, operation: str):
        """Decorator for tracing operations - enhanced"""
        if ADVANCED_LOGGER_AVAILABLE:
            return self._logger.performance_decorator(operation)
        else:
            # Basic implementation
            def decorator(func):
                def wrapper(*args, **kwargs):
                    trace_id = self.start_trace(operation)
                    try:
                        result = func(*args, **kwargs)
                        self.end_trace(trace_id, success=True,
                                     data={'result_type': str(type(result).__name__)})
                        return result
                    except Exception as e:
                        self.end_trace(trace_id, success=False,
                                     data={'error': str(e), 'error_type': type(e).__name__})
                        raise
                return wrapper
            return decorator

    def info(self, message: str, correlation_id: str = None, data: Dict = None, **kwargs):
        """Log info level message - enhanced"""
        self.log('INFO', message, correlation_id, data=data, **kwargs)

    def debug(self, message: str, correlation_id: str = None, data: Dict = None, **kwargs):
        """Log debug level message - enhanced"""
        self.log('DEBUG', message, correlation_id, data=data, **kwargs)

    def warning(self, message: str, correlation_id: str = None, data: Dict = None, **kwargs):
        """Log warning level message - enhanced"""
        self.log('WARNING', message, correlation_id, data=data, **kwargs)

    def error(self, message: str, correlation_id: str = None, data: Dict = None, **kwargs):
        """Log error level message - enhanced with context capture"""
        self.log('ERROR', message, correlation_id, data=data, capture_context=True, **kwargs)

    def critical(self, message: str, correlation_id: str = None, data: Dict = None, **kwargs):
        """Log critical level message - enhanced with full context"""
        self.log('CRITICAL', message, correlation_id, data=data, capture_context=True, **kwargs)

    def performance_start(self, operation: str) -> str:
        """Start performance monitoring - enhanced"""
        if ADVANCED_LOGGER_AVAILABLE:
            return self._logger.profiler.start_operation(operation)
        else:
            # Basic implementation
            perf_id = f"perf_{operation}_{int(time.time() * 1000)}"
            self.performance_metrics[perf_id] = {
                'operation': operation,
                'start_time': time.time(),
                'start_memory': self._get_memory_usage()
            }
            return perf_id

    def performance_end(self, perf_id: str, data: Dict = None):
        """End performance monitoring - enhanced"""
        if ADVANCED_LOGGER_AVAILABLE:
            return self._logger.profiler.end_operation(perf_id, data)
        else:
            # Basic implementation
            if perf_id not in self.performance_metrics:
                return

            start_data = self.performance_metrics[perf_id]
            end_time = time.time()
            end_memory = self._get_memory_usage()

            perf_data = {
                'operation': start_data['operation'],
                'duration': end_time - start_data['start_time'],
                'memory_delta': end_memory - start_data['start_memory'],
                'start_memory': start_data['start_memory'],
                'end_memory': end_memory,
                'type': 'performance',
                **(data or {})
            }

            self.log('INFO', f'Performance: {start_data["operation"]}', data=perf_data)
            del self.performance_metrics[perf_id]

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0

    def log_request(self, method: str, endpoint: str, status_code: int,
                   duration: float, correlation_id: str = None, user_id: str = None):
        """Log HTTP request - enhanced"""
        if ADVANCED_LOGGER_AVAILABLE:
            self._logger.info(f'{method} {endpoint} -> {status_code}',
                    correlation_id=correlation_id,
                    data={
                        'method': method,
                        'endpoint': endpoint,
                        'status_code': status_code,
                        'duration': duration,
                        'user_id': user_id,
                        'type': 'http_request'
                    })
        else:
            # Basic implementation
            self.log('INFO', f'{method} {endpoint} -> {status_code}',
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
        """Log trading activity - enhanced"""
        trade_data = {
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'price': price,
            'order_type': order_type,
            'trade_value': amount * price,
            'type': 'trade'
        }
        
        if ADVANCED_LOGGER_AVAILABLE:
            with self._logger.performance_trace(f"trade_{side}_{symbol}"):
                self._logger.info(f'Trade: {side.upper()} {amount} {symbol} @ {price}',
                        correlation_id=correlation_id, data=trade_data)
        else:
            self.log('INFO', f'Trade: {side.upper()} {amount} {symbol} @ {price}',
                    correlation_id=correlation_id, data=trade_data)

    def log_error(self, error: Exception, context: str = "",
                 correlation_id: str = None, data: Dict = None):
        """Log exception with context - MASSIVELY ENHANCED"""
        if ADVANCED_LOGGER_AVAILABLE:
            # Use advanced exception logging
            return self._logger.log_exception(error, context, correlation_id, 
                                            capture_locals=True, analyze_cause=True, data=data)
        else:
            # Basic implementation
            error_data = {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context,
                'traceback': self._get_traceback(error),
                'type': 'exception',
                **(data or {})
            }

            self.log('ERROR', f'Exception in {context}: {str(error)}',
                    correlation_id=correlation_id, data=error_data)

    def _get_traceback(self, error: Exception) -> str:
        """Get formatted traceback - basic fallback"""
        import traceback
        return ''.join(traceback.format_exception(type(error), error, error.__traceback__))

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics - enhanced"""
        if ADVANCED_LOGGER_AVAILABLE:
            diagnostics = self._logger.get_diagnostics()
            return diagnostics.get('error_analytics', {})
        else:
            # Basic implementation
            return {
                'total_errors': sum(self.error_counts.values()),
                'error_types': self.error_counts.copy(),
                'timestamp': datetime.now().isoformat()
            }

    def get_log_summary(self) -> Dict[str, Any]:
        """Get log summary - enhanced"""
        if ADVANCED_LOGGER_AVAILABLE:
            return self._logger.get_diagnostics()
        else:
            # Basic implementation
            return {
                'service': self.service_name,
                'buffered_logs': len(self.log_buffer),
                'correlation_id': self.correlation_id,
                'active_traces': len(self.trace_stack),
                'performance_metrics': len(self.performance_metrics),
                'error_summary': self.get_error_summary(),
                'timestamp': datetime.now().isoformat()
            }

# Enhanced global logger instance with advanced features
if ADVANCED_LOGGER_AVAILABLE:
    logger = StructuredLogger()  # This will use AdvancedLogger under the hood
else:
    logger = StructuredLogger()  # Basic fallback

# Enhanced convenience functions
def get_logger(service_name: str = None) -> StructuredLogger:
    """Get a structured logger instance - now with advanced features"""
    return StructuredLogger(service_name)

def log_info(message: str, **kwargs):
    """Convenience function for info logging"""
    logger.info(message, **kwargs)

def log_error(message: str, **kwargs):
    """Convenience function for error logging - enhanced"""
    logger.error(message, **kwargs)

def log_warning(message: str, **kwargs):
    """Convenience function for warning logging"""
    logger.warning(message, **kwargs)

def log_debug(message: str, **kwargs):
    """Convenience function for debug logging"""
    logger.debug(message, **kwargs)

def trace_operation(operation: str):
    """Convenience decorator for tracing operations - enhanced"""
    return logger.trace_operation(operation)

# New advanced features (if available)
if ADVANCED_LOGGER_AVAILABLE:
    def log_advanced_error(error: Exception, context: str = "", **kwargs):
        """Advanced error logging with detailed traceback"""
        return log_advanced_exception(error, context, **kwargs)
    
    def performance_trace_context(operation_name: str, context: Dict = None):
        """Performance tracing context manager"""
        return performance_trace(operation_name, context)
    
    def monitor_performance(operation_name: str = None):
        """Performance monitoring decorator"""
        return performance_monitor(operation_name)
    
    def debug_var(var_name: str, var_value: Any, watch: bool = False):
        """Debug variable with watch capability"""
        return debug_variable(var_name, var_value, watch)
    
    def get_diagnostics() -> Dict[str, Any]:
        """Get comprehensive system diagnostics"""
        return get_system_diagnostics()
else:
    # Fallback functions
    def log_advanced_error(error: Exception, context: str = "", **kwargs):
        """Fallback advanced error logging"""
        logger.log_error(error, context, **kwargs)
    
    def performance_trace_context(operation_name: str, context: Dict = None):
        """Fallback performance tracing"""
        return logger.start_trace(operation_name)
    
    def monitor_performance(operation_name: str = None):
        """Fallback performance monitoring"""
        return logger.trace_operation(operation_name or "unknown_operation")
    
    def debug_var(var_name: str, var_value: Any, watch: bool = False):
        """Fallback variable debugging"""
        logger.debug(f"Variable {var_name}: {var_value}", data={'variable_debug': True})
    
    def get_diagnostics() -> Dict[str, Any]:
        """Fallback diagnostics"""
        return logger.get_log_summary()

# Example usage in services:
"""
from shared.structured_logger import get_logger, log_info, log_error, trace_operation

# Get service-specific logger
logger = get_logger('my-service')

# Basic logging
log_info("Service started", data={'version': '1.0.0'})

# Error logging
try:
    risky_operation()
except Exception as e:
    log_error("Operation failed", error=e, context="risky_operation")

# Performance tracing
@trace_operation("database_query")
def query_database():
    return db.query("SELECT * FROM trades")

# Request logging
logger.log_request("POST", "/orders", 200, 0.125, correlation_id="abc123")

# Trade logging
logger.log_trade("BTC/USDT", "buy", 0.001, 45000, "market")
"""
