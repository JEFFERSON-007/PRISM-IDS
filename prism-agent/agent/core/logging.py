"""Agent Structured Logging Configuration."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
import structlog
from agent.core.config import agent_settings


def setup_agent_logging() -> None:
    """Initialize structured logging for PRISM Agent."""
    log_level = getattr(logging, agent_settings.LOG_LEVEL.upper(), logging.INFO)
    os.makedirs(agent_settings.LOG_DIR, exist_ok=True)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
        RotatingFileHandler(
            filename=os.path.join(agent_settings.LOG_DIR, "prism_agent.log"),
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        ),
    ]

    formatter = logging.Formatter("%(message)s")
    for handler in handlers:
        handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = handlers

    structlog.configure(
        processors=shared_processors + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_agent_logger(name: str = "prism_agent") -> structlog.stdlib.BoundLogger:
    """Return a contextual structlog logger."""
    return structlog.get_logger(name)
