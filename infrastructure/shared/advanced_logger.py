#!/usr/bin/env python3
"""
# 🚀 VIPER Trading Bot - Advanced Logging System
Ultra-sophisticated logging with deep introspection and context capture

Features:
- Advanced traceback capture with local variables
- Stack frame inspection and context analysis
- Real-time debugging with variable capture
- Memory usage tracking and leak detection
- Call graph tracing and profiling
- Rich formatting with colored output
- Interactive debugging capabilities
- Performance bottleneck detection
- Async operation tracing
- Thread-safe logging with correlation
"""

import os
import sys
import json
import logging
import time
import inspect
import threading
import traceback
import linecache
from datetime import datetime
from collections import defaultdict, deque
from contextlib import contextmanager
from typing import Dict, Any, List, Optional, Callable, Union
from functools import wraps
import asyncio

# Optional Redis import with graceful fallback
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


# Advanced dependencies (graceful fallbacks)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    from rich.console import Console
    from rich.traceback import Traceback
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import memory_profiler
    MEMORY_PROFILER_AVAILABLE = True
except ImportError:
    MEMORY_PROFILER_AVAILABLE = False


# Environment configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
SERVICE_NAME = os.getenv('SERVICE_NAME', 'unknown-service')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
RICH_LOGGING = os.getenv('RICH_LOGGING', 'true').lower() == 'true'


class AdvancedTracebackCapture:
    """Advanced traceback capture with local variables and context"""
    
    @staticmethod
    def capture_detailed_traceback(exception: Exception, max_frames: int = 20, 
                                 capture_locals: bool = True) -> Dict[str, Any]:
        """Capture comprehensive traceback information"""
        try:
            tb_info = {
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'exception_args': getattr(exception, 'args', []),
                'frames': [],
                'summary': '',
                'root_cause_analysis': {}
            }
            
            # Get the traceback
            tb = exception.__traceback__
            frame_count = 0
            
            while tb is not None and frame_count < max_frames:
                frame = tb.tb_frame
                frame_info = {
                    'filename': frame.f_code.co_filename,
                    'function_name': frame.f_code.co_name,
                    'line_number': tb.tb_lineno,
                    'source_line': linecache.getline(frame.f_code.co_filename, tb.tb_lineno).strip(),
                    'locals': {},
                    'globals_subset': {},
                    'arguments': {}
                }
                
                # Capture local variables if requested
                if capture_locals:
                    frame_info['locals'] = AdvancedTracebackCapture._safe_capture_locals(frame.f_locals)
                    frame_info['globals_subset'] = AdvancedTracebackCapture._safe_capture_globals(frame.f_globals)
                    frame_info['arguments'] = AdvancedTracebackCapture._extract_function_args(frame)
                
                # Add context lines around the error
                frame_info['context_lines'] = AdvancedTracebackCapture._get_context_lines(
                    frame.f_code.co_filename, tb.tb_lineno, context_size=3
                )
                
                tb_info['frames'].append(frame_info)
                tb = tb.tb_next
                frame_count += 1
            
            # Generate summary and analysis
            tb_info['summary'] = AdvancedTracebackCapture._generate_summary(tb_info)
            tb_info['root_cause_analysis'] = AdvancedTracebackCapture._analyze_root_cause(tb_info)
            
            return tb_info
            
        except Exception as e:
            # Fallback to basic traceback if advanced capture fails
            return {
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'basic_traceback': ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__)),
                'capture_error': str(e)
            }
    
    @staticmethod
    def _safe_capture_locals(local_vars: Dict) -> Dict[str, str]:
        """Safely capture local variables, handling non-serializable objects"""
        safe_locals = {}
        for name, value in local_vars.items():
            try:
                # Skip private variables and dangerous objects
                if name.startswith('_') or name in ['self', 'cls']:
                    continue
                    
                # Try to represent the value safely
                if isinstance(value, (str, int, float, bool, type(None))):
                    safe_locals[name] = value
                elif isinstance(value, (list, tuple)) and len(value) < 10:
                    safe_locals[name] = str(value)[:200] + "..." if len(str(value)) > 200 else str(value)
                elif isinstance(value, dict) and len(value) < 10:
                    safe_locals[name] = str(value)[:200] + "..." if len(str(value)) > 200 else str(value)
                else:
                    safe_locals[name] = f"<{type(value).__name__}: {str(value)[:50]}...>"
            except Exception:
                safe_locals[name] = f"<{type(value).__name__}: repr_failed>"
        
        return safe_locals
    
    @staticmethod
    def _safe_capture_globals(global_vars: Dict) -> Dict[str, str]:
        """Safely capture relevant global variables"""
        safe_globals = {}
        relevant_globals = ['__name__', '__file__', '__package__']
        
        for name in relevant_globals:
            if name in global_vars:
                try:
                    safe_globals[name] = str(global_vars[name])
                except Exception:
                    safe_globals[name] = f"<{type(global_vars[name]).__name__}: repr_failed>"
        
        return safe_globals
    
    @staticmethod
    def _extract_function_args(frame) -> Dict[str, Any]:
        """Extract function arguments from frame"""
        try:
            args_info = inspect.getargvalues(frame)
            function_args = {}
            
            for arg_name in args_info.args:
                if arg_name in args_info.locals:
                    value = args_info.locals[arg_name]
                    try:
                        if isinstance(value, (str, int, float, bool, type(None))):
                            function_args[arg_name] = value
                        else:
                            function_args[arg_name] = f"<{type(value).__name__}>"
                    except Exception:
                        function_args[arg_name] = "<repr_failed>"
            
            return function_args
        except Exception:
            return {}
    
    @staticmethod
    def _get_context_lines(filename: str, line_number: int, context_size: int = 3) -> Dict[str, str]:
        """Get context lines around the error"""
        try:
            context = {}
            start_line = max(1, line_number - context_size)
            end_line = line_number + context_size + 1
            
            for i in range(start_line, end_line):
                line_content = linecache.getline(filename, i).rstrip()
                if line_content:
                    marker = " >>> " if i == line_number else "     "
                    context[f"line_{i}"] = f"{marker}{line_content}"
            
            return context
        except Exception:
            return {}
    
    @staticmethod
    def _generate_summary(tb_info: Dict) -> str:
        """Generate human-readable summary of the error"""
        frames = tb_info.get('frames', [])
        if not frames:
            return f"Error: {tb_info['exception_type']}: {tb_info['exception_message']}"
        
        last_frame = frames[-1]
        first_frame = frames[0]
        
        summary = f"[{tb_info['exception_type']}] {tb_info['exception_message']}\n"
        summary += f"Origin: {os.path.basename(first_frame['filename'])}:{first_frame['line_number']} in {first_frame['function_name']}()\n"
        summary += f"Error: {os.path.basename(last_frame['filename'])}:{last_frame['line_number']} in {last_frame['function_name']}()\n"
        summary += f"Stack depth: {len(frames)} frames"
        
        return summary
    
    @staticmethod
    def _analyze_root_cause(tb_info: Dict) -> Dict[str, Any]:
        """Analyze potential root causes of the error"""
        analysis = {
            'potential_causes': [],
            'recommendations': [],
            'error_patterns': [],
            'risk_level': 'unknown'
        }
        
        exception_type = tb_info.get('exception_type', '')
        exception_msg = tb_info.get('exception_message', '')
        frames = tb_info.get('frames', [])
        
        # Analyze common error patterns
        if exception_type == 'KeyError':
            analysis['potential_causes'].append('Missing dictionary key or configuration value')
            analysis['recommendations'].append('Check configuration files and default values')
            analysis['risk_level'] = 'medium'
            
        elif exception_type == 'AttributeError':
            analysis['potential_causes'].append('Object method/attribute not found or None object')
            analysis['recommendations'].append('Add null checks and validate object initialization')
            analysis['risk_level'] = 'medium'
            
        elif exception_type == 'ConnectionError':
            analysis['potential_causes'].append('Network connectivity or service unavailability')
            analysis['recommendations'].append('Implement retry logic and connection pooling')
            analysis['risk_level'] = 'high'
            
        elif exception_type == 'ValueError':
            analysis['potential_causes'].append('Invalid data format or out-of-range values')
            analysis['recommendations'].append('Add input validation and data sanitization')
            analysis['risk_level'] = 'medium'
            
        elif exception_type in ['ZeroDivisionError', 'ArithmeticError']:
            analysis['potential_causes'].append('Mathematical operation with invalid values')
            analysis['recommendations'].append('Add validation for mathematical operations')
            analysis['risk_level'] = 'high'
        
        # Analyze stack depth
        if len(frames) > 15:
            analysis['error_patterns'].append('Deep call stack - possible recursion issue')
            analysis['risk_level'] = 'high'
        
        # Look for async patterns
        async_frames = [f for f in frames if 'async' in f.get('source_line', '').lower()]
        if async_frames:
            analysis['error_patterns'].append('Async operation involved - check await patterns')
        
        return analysis


class AdvancedPerformanceProfiler:
    """Advanced performance profiling and monitoring"""
    
    def __init__(self):
        self.active_operations = {}
        self.performance_history = deque(maxlen=1000)
        self.memory_snapshots = deque(maxlen=100)
        self.call_graph = defaultdict(list)
        
    def start_operation(self, operation_name: str, context: Dict = None) -> str:
        """Start tracking an operation"""
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        
        start_info = {
            'operation_name': operation_name,
            'start_time': time.time(),
            'start_memory': self._get_memory_usage(),
            'context': context or {},
            'thread_id': threading.get_ident(),
            'call_stack': self._get_call_stack()
        }
        
        self.active_operations[operation_id] = start_info
        return operation_id
    
    def end_operation(self, operation_id: str, result_data: Dict = None) -> Dict[str, Any]:
        """End tracking an operation"""
        if operation_id not in self.active_operations:
            return {}
        
        start_info = self.active_operations[operation_id]
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        performance_data = {
            'operation_name': start_info['operation_name'],
            'duration': end_time - start_info['start_time'],
            'memory_delta': end_memory - start_info['start_memory'],
            'start_memory': start_info['start_memory'],
            'end_memory': end_memory,
            'thread_id': start_info['thread_id'],
            'context': start_info['context'],
            'result_data': result_data or {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to history
        self.performance_history.append(performance_data)
        
        # Update call graph
        if start_info['call_stack']:
            caller = start_info['call_stack'][0] if start_info['call_stack'] else 'unknown'
            self.call_graph[caller].append(start_info['operation_name'])
        
        # Clean up
        del self.active_operations[operation_id]
        
        return performance_data
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                return process.memory_info().rss / 1024 / 1024
            except Exception:
                pass
        return 0.0
    
    def _get_call_stack(self, max_depth: int = 10) -> List[str]:
        """Get current call stack"""
        try:
            stack = []
            frame = inspect.currentframe()
            
            # Skip the current frame and profiler frames
            for _ in range(3):
                if frame:
                    frame = frame.f_back
            
            count = 0
            while frame and count < max_depth:
                function_name = frame.f_code.co_name
                filename = os.path.basename(frame.f_code.co_filename)
                line_number = frame.f_lineno
                stack.append(f"{filename}:{line_number}:{function_name}")
                frame = frame.f_back
                count += 1
            
            return stack
        except Exception:
            return []
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics"""
        if not self.performance_history:
            return {}
        
        # Calculate statistics
        durations = [op['duration'] for op in self.performance_history]
        memory_deltas = [op['memory_delta'] for op in self.performance_history]
        
        return {
            'total_operations': len(self.performance_history),
            'active_operations': len(self.active_operations),
            'avg_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'avg_memory_delta': sum(memory_deltas) / len(memory_deltas),
            'max_memory_delta': max(memory_deltas),
            'call_graph_size': len(self.call_graph),
            'timestamp': datetime.now().isoformat()
        }


class AdvancedLogger:
    """Advanced logging system with deep introspection and context capture"""
    
    def __init__(self, service_name: str = None, enable_rich: bool = None):
        self.service_name = service_name or SERVICE_NAME
        self.enable_rich = enable_rich if enable_rich is not None else (RICH_AVAILABLE and RICH_LOGGING)
        
        # Core components
        self.redis_client = None
        self.log_buffer = deque(maxlen=2000)  # Larger buffer for advanced logging
        self.correlation_id = self._generate_correlation_id()
        self.trace_stack = []
        self.profiler = AdvancedPerformanceProfiler()
        
        # Advanced features
        self.error_analytics = defaultdict(list)
        self.debug_breakpoints = set()
        self.variable_watchlist = {}
        self.async_traces = {}
        self.thread_local = threading.local()
        
        # Rich console if available
        if self.enable_rich and RICH_AVAILABLE:
            self.console = Console()
            self.rich_traceback = True
        else:
            self.console = None
            self.rich_traceback = False
        
        # Initialize connections and setup
        self._setup_redis_connection()
        self._setup_python_logging()
        self._setup_exception_hooks()
    
    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID"""
        import uuid
        return str(uuid.uuid4())[:12]  # Longer ID for better uniqueness
    
    def _setup_redis_connection(self):
        """Setup Redis connection for centralized logging"""
        if not REDIS_AVAILABLE:
            self.is_connected = False
            self._fallback_log("WARNING", "Redis not available - using local logging only")
            return
            
        try:
            self.redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
            self.redis_client.ping()
            self.is_connected = True
        except Exception as e:
            self.is_connected = False
            self._fallback_log("WARNING", f"Redis connection failed: {e}")
    
    def _setup_python_logging(self):
        """Setup enhanced Python logging integration"""
        log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
        
        class AdvancedFormatter(logging.Formatter):
            def __init__(self, logger_instance):
                super().__init__()
                self.logger_instance = logger_instance
            
            def format(self, record):
                # Enhanced formatting with context
                log_entry = {
                    'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                    'service': self.logger_instance.service_name,
                    'level': record.levelname,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno,
                    'thread_id': threading.get_ident(),
                    'correlation_id': getattr(record, 'correlation_id', self.logger_instance.correlation_id),
                    'trace_id': getattr(record, 'trace_id', None),
                    'data': getattr(record, 'data', {}),
                    'performance_context': getattr(record, 'performance_context', {})
                }
                
                if self.logger_instance.enable_rich:
                    # Rich formatting for console
                    return self._rich_format(log_entry)
                else:
                    return json.dumps(log_entry, indent=2 if DEBUG_MODE else None)
            
            def _rich_format(self, log_entry: Dict) -> str:
                """Format log entry for rich console output"""
                level = log_entry['level']
                timestamp = log_entry['timestamp'].split('T')[1][:8]  # HH:MM:SS
                
                # Color coding
                level_colors = {
                    'DEBUG': 'bright_black',
                    'INFO': 'bright_blue',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'bright_red'
                }
                
                color = level_colors.get(level, 'white')
                
                return f"[{color}]{timestamp} {level:8} [{log_entry['service']}] {log_entry['message']}[/]"
        
        # Setup logger
        self.logger = logging.getLogger(f"advanced_{self.service_name}")
        self.logger.setLevel(log_level)
        
        # Clear existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Add advanced handler
        if self.enable_rich and RICH_AVAILABLE:
            # Rich console handler
            from rich.logging import RichHandler
            handler = RichHandler(console=self.console, rich_tracebacks=True)
        else:
            handler = logging.StreamHandler()
            handler.setFormatter(AdvancedFormatter(self))
        
        self.logger.addHandler(handler)
    
    def _setup_exception_hooks(self):
        """Setup global exception hooks for automatic error capture"""
        original_excepthook = sys.excepthook
        
        def advanced_excepthook(exc_type, exc_value, exc_traceback):
            """Enhanced exception hook that captures detailed context"""
            if exc_type != KeyboardInterrupt:  # Don't capture Ctrl+C
                self.critical("Unhandled exception caught by global hook",
                            data={'exception': exc_value, 'advanced_traceback': True})
            
            # Call original hook
            original_excepthook(exc_type, exc_value, exc_traceback)
        
        sys.excepthook = advanced_excepthook
    
    def _fallback_log(self, level: str, message: str):
        """Fallback logging when advanced features fail"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] {level} [{self.service_name}] {message}")
    
    # Enhanced logging methods
    def log(self, level: str, message: str, correlation_id: str = None,
            trace_id: str = None, data: Dict = None, capture_context: bool = False,
            **kwargs):
        """Enhanced log method with optional context capture"""
        try:
            # Generate comprehensive log entry
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'service': self.service_name,
                'level': level.upper(),
                'message': message,
                'correlation_id': correlation_id or self.correlation_id,
                'trace_id': trace_id or self._get_current_trace_id(),
                'thread_id': threading.get_ident(),
                'data': data or {},
                **kwargs
            }
            
            # Add context if requested or if it's an error
            if capture_context or level.upper() in ['ERROR', 'CRITICAL']:
                log_entry['context'] = self._capture_current_context()
            
            # Add performance context if available
            if hasattr(self.thread_local, 'current_operation'):
                log_entry['performance_context'] = self.thread_local.current_operation
            
            # Store in buffer
            self.log_buffer.append(log_entry)
            
            # Update analytics
            if level.upper() in ['ERROR', 'CRITICAL']:
                self._update_error_analytics(log_entry)
            
            # Send to centralized logging
            self._send_to_centralized_logger(log_entry)
            
            # Log to Python logging system
            self._log_to_python_logging(log_entry)
            
            # Rich console output if enabled
            if self.enable_rich and level.upper() in ['ERROR', 'CRITICAL']:
                self._rich_error_display(log_entry)
        
        except Exception as e:
            self._fallback_log("ERROR", f"Advanced logging failed: {e} | Original: {message}")
    
    def _capture_current_context(self) -> Dict[str, Any]:
        """Capture current execution context"""
        try:
            frame = inspect.currentframe()
            # Skip logging frames
            for _ in range(4):
                if frame:
                    frame = frame.f_back
            
            if not frame:
                return {}
            
            context = {
                'filename': frame.f_code.co_filename,
                'function': frame.f_code.co_name,
                'line_number': frame.f_lineno,
                'source_line': linecache.getline(frame.f_code.co_filename, frame.f_lineno).strip(),
                'local_variables': AdvancedTracebackCapture._safe_capture_locals(frame.f_locals),
                'function_args': AdvancedTracebackCapture._extract_function_args(frame)
            }
            
            return context
        except Exception:
            return {}
    
    def _update_error_analytics(self, log_entry: Dict):
        """Update error analytics and patterns"""
        try:
            error_key = log_entry.get('data', {}).get('error_type', 'unknown')
            self.error_analytics[error_key].append({
                'timestamp': log_entry['timestamp'],
                'message': log_entry['message'],
                'context': log_entry.get('context', {})
            })
        except Exception:
            pass
    
    def _send_to_centralized_logger(self, log_entry: Dict):
        """Send to centralized logging service"""
        if self.is_connected and self.redis_client:
            try:
                channel = f'logs:{self.service_name}:advanced'
                self.redis_client.publish(channel, json.dumps(log_entry))
            except Exception:
                pass
    
    def _log_to_python_logging(self, log_entry: Dict):
        """Log to Python logging system"""
        try:
            log_method = getattr(self.logger, log_entry['level'].lower(), self.logger.info)
            extra_data = {
                'correlation_id': log_entry['correlation_id'],
                'trace_id': log_entry['trace_id'],
                'data': log_entry['data'],
                'performance_context': log_entry.get('performance_context', {})
            }
            log_method(log_entry['message'], extra=extra_data)
        except Exception as e:
            self._fallback_log("ERROR", f"Python logging failed: {e}")
    
    def _rich_error_display(self, log_entry: Dict):
        """Display rich error information"""
        if not (self.console and RICH_AVAILABLE):
            return
        
        try:
            # Create rich panel for errors
            error_panel = Panel(
                f"[red]{log_entry['message']}[/red]\n"
                f"[dim]Service: {log_entry['service']}[/dim]\n"
                f"[dim]Correlation ID: {log_entry['correlation_id']}[/dim]",
                title=f"[red]🚨 {log_entry['level']}[/red]",
                border_style="red"
            )
            
            self.console.print(error_panel)
            
            # Display context if available
            if 'context' in log_entry and log_entry['context']:
                context = log_entry['context']
                if 'local_variables' in context and context['local_variables']:
                    var_table = Table(title="Local Variables")
                    var_table.add_column("Variable", style="cyan")
                    var_table.add_column("Value", style="white")
                    
                    for var_name, var_value in context['local_variables'].items():
                        var_table.add_row(var_name, str(var_value))
                    
                    self.console.print(var_table)
        
        except Exception:
            pass
    
    def _get_current_trace_id(self) -> str:
        """Get current trace ID"""
        return self.trace_stack[-1] if self.trace_stack else self.correlation_id
    
    # Enhanced error logging with advanced traceback
    def log_exception(self, exception: Exception, context: str = "", 
                     correlation_id: str = None, capture_locals: bool = True,
                     analyze_cause: bool = True, data: Dict = None) -> str:
        """Log exception with advanced traceback and analysis"""
        try:
            # Capture detailed traceback
            detailed_tb = AdvancedTracebackCapture.capture_detailed_traceback(
                exception, capture_locals=capture_locals
            )
            
            # Create comprehensive error data
            error_data = {
                'error_type': type(exception).__name__,
                'error_message': str(exception),
                'context': context,
                'detailed_traceback': detailed_tb,
                'memory_usage': self.profiler._get_memory_usage(),
                'thread_id': threading.get_ident(),
                'call_stack': self.profiler._get_call_stack(),
                'timestamp': datetime.now().isoformat(),
                'type': 'advanced_exception',
                **(data or {})  # Merge additional data
            }
            
            # Add analysis if requested
            if analyze_cause:
                error_data['analysis'] = detailed_tb.get('root_cause_analysis', {})
            
            # Log with advanced features
            self.log('ERROR', f'Advanced Exception in {context}: {str(exception)}',
                    correlation_id=correlation_id, data=error_data, capture_context=True)
            
            # Display rich traceback if available
            if self.rich_traceback and RICH_AVAILABLE:
                self._display_rich_traceback(exception, detailed_tb)
            
            return detailed_tb.get('summary', str(exception))
            
        except Exception as e:
            # Ultimate fallback
            self._fallback_log("ERROR", f"Advanced exception logging failed: {e} | Original: {str(exception)}")
            return str(exception)
    
    def _display_rich_traceback(self, exception: Exception, detailed_tb: Dict):
        """Display beautiful rich traceback"""
        if not (self.console and RICH_AVAILABLE):
            return
        
        try:
            # Create rich traceback
            rich_tb = Traceback.from_exception(
                type(exception), exception, exception.__traceback__,
                show_locals=True
            )
            self.console.print(rich_tb)
            
            # Show analysis if available
            analysis = detailed_tb.get('root_cause_analysis', {})
            if analysis.get('potential_causes'):
                analysis_panel = Panel(
                    "\n".join([
                        "[yellow]Potential Causes:[/yellow]",
                        *[f"• {cause}" for cause in analysis['potential_causes']],
                        "",
                        "[green]Recommendations:[/green]",
                        *[f"• {rec}" for rec in analysis.get('recommendations', [])]
                    ]),
                    title="[yellow]🔍 Root Cause Analysis[/yellow]",
                    border_style="yellow"
                )
                self.console.print(analysis_panel)
        
        except Exception:
            pass
    
    # Performance monitoring integration
    @contextmanager
    def performance_trace(self, operation_name: str, context: Dict = None):
        """Context manager for performance tracing"""
        operation_id = self.profiler.start_operation(operation_name, context)
        start_time = time.time()
        
        try:
            self.thread_local.current_operation = {
                'operation_id': operation_id,
                'operation_name': operation_name,
                'start_time': start_time
            }
            
            yield operation_id
            
        except Exception as e:
            # Log exception with performance context
            perf_data = self.profiler.end_operation(operation_id, {'exception': str(e)})
            self.log_exception(e, f"performance_trace:{operation_name}", 
                             data={'performance_data': perf_data})
            raise
        
        finally:
            # Clean up and record performance
            perf_data = self.profiler.end_operation(operation_id)
            if hasattr(self.thread_local, 'current_operation'):
                delattr(self.thread_local, 'current_operation')
            
            # Log performance if significant
            if perf_data.get('duration', 0) > 1.0:  # Log operations > 1 second
                self.info(f"Performance: {operation_name} completed",
                         data={'performance_data': perf_data, 'type': 'performance'})
    
    def performance_decorator(self, operation_name: str = None):
        """Decorator for automatic performance tracing"""
        def decorator(func):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    with self.performance_trace(op_name, {'args_count': len(args), 'kwargs_count': len(kwargs)}):
                        return await func(*args, **kwargs)
                return async_wrapper
            else:
                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    with self.performance_trace(op_name, {'args_count': len(args), 'kwargs_count': len(kwargs)}):
                        return func(*args, **kwargs)
                return sync_wrapper
        
        return decorator
    
    # Standard logging methods with enhancements
    def debug(self, message: str, **kwargs):
        """Debug level logging"""
        self.log('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Info level logging"""
        self.log('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Warning level logging"""
        self.log('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Error level logging with context capture"""
        kwargs['capture_context'] = kwargs.get('capture_context', True)
        self.log('ERROR', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Critical level logging with full context capture"""
        kwargs['capture_context'] = True
        self.log('CRITICAL', message, **kwargs)
    
    # Debug and inspection utilities
    def debug_variable(self, var_name: str, var_value: Any, watch: bool = False):
        """Debug a specific variable"""
        try:
            var_info = {
                'name': var_name,
                'value': str(var_value)[:500],  # Limit size
                'type': type(var_value).__name__,
                'size': len(str(var_value)) if hasattr(var_value, '__len__') else 'N/A',
                'memory_size': sys.getsizeof(var_value) if hasattr(sys, 'getsizeof') else 'N/A'
            }
            
            if watch:
                self.variable_watchlist[var_name] = var_info
            
            self.debug(f"Variable Debug: {var_name}", data={'variable_info': var_info, 'type': 'variable_debug'})
            
        except Exception as e:
            self.error(f"Failed to debug variable {var_name}: {e}")
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get comprehensive diagnostic information"""
        try:
            return {
                'service_info': {
                    'service_name': self.service_name,
                    'correlation_id': self.correlation_id,
                    'uptime': time.time() - getattr(self, '_start_time', time.time()),
                    'thread_id': threading.get_ident()
                },
                'logging_stats': {
                    'total_logs': len(self.log_buffer),
                    'error_count': len([log for log in self.log_buffer if log.get('level') == 'ERROR']),
                    'active_traces': len(self.trace_stack),
                    'redis_connected': self.is_connected
                },
                'performance_stats': self.profiler.get_performance_summary(),
                'error_analytics': {
                    error_type: len(occurrences) 
                    for error_type, occurrences in self.error_analytics.items()
                },
                'memory_info': {
                    'current_usage_mb': self.profiler._get_memory_usage(),
                    'snapshots_count': len(self.profiler.memory_snapshots)
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': f"Failed to generate diagnostics: {e}"}


# Global advanced logger instance
advanced_logger = AdvancedLogger()

# Enhanced convenience functions
def get_advanced_logger(service_name: str = None, enable_rich: bool = None) -> AdvancedLogger:
    """Get an advanced logger instance"""
    return AdvancedLogger(service_name, enable_rich)

def log_advanced_exception(exception: Exception, context: str = "", **kwargs) -> str:
    """Convenience function for advanced exception logging"""
    return advanced_logger.log_exception(exception, context, **kwargs)

def performance_trace(operation_name: str, context: Dict = None):
    """Convenience function for performance tracing"""
    return advanced_logger.performance_trace(operation_name, context)

def performance_monitor(operation_name: str = None):
    """Convenience decorator for performance monitoring"""
    return advanced_logger.performance_decorator(operation_name)

def debug_variable(var_name: str, var_value: Any, watch: bool = False):
    """Convenience function for variable debugging"""
    return advanced_logger.debug_variable(var_name, var_value, watch)

def get_system_diagnostics() -> Dict[str, Any]:
    """Get comprehensive system diagnostics"""
    return advanced_logger.get_diagnostics()

# Async utilities
async def async_log_exception(exception: Exception, context: str = "", **kwargs) -> str:
    """Async version of exception logging"""
    return await asyncio.get_event_loop().run_in_executor(
        None, lambda: log_advanced_exception(exception, context, **kwargs)
    )

# Example usage documentation
__usage_examples__ = """
# Basic usage
from infrastructure.shared.advanced_logger import get_advanced_logger, log_advanced_exception, performance_monitor

logger = get_advanced_logger('my-service')

# Advanced exception logging
try:
    risky_operation()
except Exception as e:
    summary = log_advanced_exception(e, "risky_operation", 
                                   capture_locals=True, analyze_cause=True)

# Performance monitoring
@performance_monitor("database_query")
def query_database():
    return db.query("SELECT * FROM trades")

# Context-aware logging
with logger.performance_trace("complex_calculation"):
    result = complex_calculation()

# Variable debugging
debug_variable("user_balance", balance, watch=True)

# Get system diagnostics
diagnostics = get_system_diagnostics()
"""