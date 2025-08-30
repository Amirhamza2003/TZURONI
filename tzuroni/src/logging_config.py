import logging
import os
from datetime import datetime
from typing import Optional


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Setup structured logging with file and console output"""
    
    # Create logs directory if it doesn't exist
    if log_file and not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logger = logging.getLogger("crowdwisdom")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "crowdwisdom") -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


class MetricsTracker:
    """Track performance metrics and errors"""
    
    def __init__(self):
        self.metrics = {
            "markets_collected": 0,
            "sites_scraped": 0,
            "errors": [],
            "processing_time": 0,
            "unified_products": 0
        }
    
    def log_error(self, error: Exception, context: str):
        """Log an error with context"""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        self.metrics["errors"].append(error_info)
        logger = get_logger()
        logger.error(f"Error in {context}: {error}")
    
    def log_metric(self, metric: str, value):
        """Log a metric"""
        if metric in self.metrics:
            if isinstance(self.metrics[metric], list):
                self.metrics[metric].append(value)
            else:
                self.metrics[metric] = value
    
    def get_summary(self) -> dict:
        """Get metrics summary"""
        return {
            "total_markets": self.metrics["markets_collected"],
            "sites_scraped": self.metrics["sites_scraped"],
            "unified_products": self.metrics["unified_products"],
            "error_count": len(self.metrics["errors"]),
            "processing_time_seconds": self.metrics["processing_time"]
        }
