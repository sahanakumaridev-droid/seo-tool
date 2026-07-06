"""
logging_config.py — Structured logging with JSON output
Integrates with Sentry for error tracking
"""
import logging
import json
import sys
from datetime import datetime, timezone
from config import settings

# Try to import json logger, fall back to standard logging if not available
try:
    from pythonjsonlogger import jsonlogger
    HAS_JSON_LOGGER = True
except ImportError:
    HAS_JSON_LOGGER = False


# Custom JSON formatter
class CustomJsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        if hasattr(record, 'request_id'):
            log_obj['request_id'] = record.request_id
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


def setup_logging():
    """Configure structured logging with JSON output."""
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # JSON handler for stdout
    json_handler = logging.StreamHandler(sys.stdout)
    if HAS_JSON_LOGGER:
        from pythonjsonlogger import jsonlogger
        json_handler.setFormatter(jsonlogger.JsonFormatter())
    else:
        json_handler.setFormatter(CustomJsonFormatter())
    root_logger.addHandler(json_handler)
    
    # Sentry integration (if enabled)
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                integrations=[
                    FastApiIntegration(),
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=0.1,
                environment=settings.ENVIRONMENT,
            )
        except Exception as e:
            root_logger.warning(f"Sentry initialization failed: {e}")
    
    return root_logger


# Get logger instance
logger = logging.getLogger(__name__)
