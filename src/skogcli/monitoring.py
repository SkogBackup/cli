"""
Monitoring and logging configuration for SkogCLI.

This module provides structured logging, error tracking, and performance monitoring
for the SkogAI CLI application.
"""

import os
import sys
import time
from typing import Any, Dict, Optional

import structlog
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
COMMAND_COUNTER = Counter('skogcli_commands_total', 'Total number of commands executed', ['command', 'status'])
COMMAND_DURATION = Histogram('skogcli_command_duration_seconds', 'Command execution time', ['command'])
ERROR_COUNTER = Counter('skogcli_errors_total', 'Total number of errors', ['error_type'])

def setup_logging(log_level: str = "INFO", json_logs: bool = False) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output logs in JSON format
    """
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def setup_sentry(dsn: Optional[str] = None) -> None:
    """
    Configure Sentry for error tracking.
    
    Args:
        dsn: Sentry DSN. If None, will try to get from SENTRY_DSN env var
    """
    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        
        dsn = dsn or os.getenv("SENTRY_DSN")
        if not dsn:
            return
            
        sentry_logging = LoggingIntegration(
            level=structlog.stdlib.logging.INFO,
            event_level=structlog.stdlib.logging.ERROR
        )
        
        sentry_sdk.init(
            dsn=dsn,
            integrations=[sentry_logging],
            traces_sample_rate=0.1,
            environment=os.getenv("ENVIRONMENT", "development"),
        )
        
    except ImportError:
        pass

def setup_metrics_server(port: int = 8000) -> None:
    """
    Start Prometheus metrics server.
    
    Args:
        port: Port to serve metrics on
    """
    try:
        start_http_server(port)
        logger = structlog.get_logger()
        logger.info("Metrics server started", port=port)
    except Exception as e:
        logger = structlog.get_logger()
        logger.warning("Failed to start metrics server", error=str(e))

class MetricsContext:
    """Context manager for tracking command metrics."""
    
    def __init__(self, command_name: str):
        self.command_name = command_name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        COMMAND_DURATION.labels(command=self.command_name).observe(duration)
        
        if exc_type is None:
            COMMAND_COUNTER.labels(command=self.command_name, status="success").inc()
        else:
            COMMAND_COUNTER.labels(command=self.command_name, status="error").inc()
            ERROR_COUNTER.labels(error_type=exc_type.__name__).inc()

def log_command_execution(command: str, args: Dict[str, Any]) -> None:
    """Log command execution with structured data."""
    logger = structlog.get_logger()
    logger.info(
        "Command executed",
        command=command,
        args=args,
        user=os.getenv("USER"),
        cwd=os.getcwd(),
    )

def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log error with context information."""
    logger = structlog.get_logger()
    logger.error(
        "Error occurred",
        error=str(error),
        error_type=type(error).__name__,
        context=context or {},
        exc_info=True,
    )

# Initialize logging on module import
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    json_logs=os.getenv("JSON_LOGS", "false").lower() == "true"
)

# Initialize Sentry if configured
setup_sentry()

# Start metrics server if enabled
if os.getenv("ENABLE_METRICS", "false").lower() == "true":
    metrics_port = int(os.getenv("METRICS_PORT", "8000"))
    setup_metrics_server(metrics_port)