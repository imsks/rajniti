"""
Structured logging configuration for the Rajniti application.
"""
import logging
import logging.config
import sys
from typing import Dict, Any
import structlog


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """Setup structured logging for the application."""
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    
    # Configure structlog
    if log_format == "json":
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    else:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.dev.ConsoleRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a configured logger instance."""
    return structlog.get_logger(name)


class RequestLogger:
    """Logger for HTTP requests."""
    
    def __init__(self):
        self.logger = get_logger("rajniti.requests")
    
    def log_request(self, method: str, url: str, status_code: int, duration: float, **kwargs):
        """Log HTTP request details."""
        self.logger.info(
            "HTTP request completed",
            method=method,
            url=url,
            status_code=status_code,
            duration_ms=round(duration * 1000, 2),
            **kwargs
        )
    
    def log_error(self, method: str, url: str, error: str, **kwargs):
        """Log HTTP request errors."""
        self.logger.error(
            "HTTP request failed",
            method=method,
            url=url,
            error=error,
            **kwargs
        )


class DatabaseLogger:
    """Logger for database operations."""
    
    def __init__(self):
        self.logger = get_logger("rajniti.database")
    
    def log_query(self, operation: str, table: str, duration: float, **kwargs):
        """Log database query details."""
        self.logger.info(
            "Database query executed",
            operation=operation,
            table=table,
            duration_ms=round(duration * 1000, 2),
            **kwargs
        )
    
    def log_error(self, operation: str, table: str, error: str, **kwargs):
        """Log database errors."""
        self.logger.error(
            "Database operation failed",
            operation=operation,
            table=table,
            error=error,
            **kwargs
        )


class ScraperLogger:
    """Logger for scraping operations."""
    
    def __init__(self):
        self.logger = get_logger("rajniti.scraper")
    
    def log_scrape_start(self, scraper: str, url: str, **kwargs):
        """Log scraping start."""
        self.logger.info(
            "Scraping started",
            scraper=scraper,
            url=url,
            **kwargs
        )
    
    def log_scrape_success(self, scraper: str, url: str, items_scraped: int, duration: float, **kwargs):
        """Log successful scraping."""
        self.logger.info(
            "Scraping completed successfully",
            scraper=scraper,
            url=url,
            items_scraped=items_scraped,
            duration_ms=round(duration * 1000, 2),
            **kwargs
        )
    
    def log_scrape_error(self, scraper: str, url: str, error: str, attempt: int = 1, **kwargs):
        """Log scraping errors."""
        self.logger.error(
            "Scraping failed",
            scraper=scraper,
            url=url,
            error=error,
            attempt=attempt,
            **kwargs
        )
    
    def log_retry(self, scraper: str, url: str, attempt: int, max_attempts: int, **kwargs):
        """Log retry attempts."""
        self.logger.warning(
            "Retrying scraping operation",
            scraper=scraper,
            url=url,
            attempt=attempt,
            max_attempts=max_attempts,
            **kwargs
        )
