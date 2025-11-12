import sys
import logging
import structlog
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: Path = None):
    """
    Configure structured logging for HyperCog
    
    CRITICAL: Never write to stdout in STDIO MCP servers
    All logs go to stderr or file
    """
    
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(log_level)),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.getLevelName(log_level))
        logging.root.addHandler(file_handler)
    
    return structlog.get_logger()
