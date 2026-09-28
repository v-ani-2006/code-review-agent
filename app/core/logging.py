import logging
import sys
from app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configure and return the application-wide root logger with a clean console handler."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Define a clean, structured log format
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    # Console Handler: streams log records directly to standard output (sys.stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Application Logger
    app_logger = logging.getLogger(settings.APP_NAME)
    app_logger.setLevel(log_level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if not app_logger.handlers:
        app_logger.addHandler(console_handler)

    # Ensure logs propagate or stay clean
    app_logger.propagate = False

    return app_logger


# Global logger instance ready for import across the codebase
logger = setup_logging()
