import logging
import logging.config

LOG_LEVEL = "INFO"  # Could be from settings

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "level": LOG_LEVEL,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "level": LOG_LEVEL,
            "handlers": ["default"],
            "propagate": True,
        },
    },
}


def force_all_loggers_to_use_root_handler():
    """Force all existing loggers to use the root handler configuration."""
    for _, logger in logging.root.manager.loggerDict.items():
        if isinstance(logger, logging.Logger):
            logger.handlers = []
            logger.propagate = True


def get_logger(service_name: str) -> logging.Logger:
    """
    Get a configured logger for the given service.

    Args:
        service_name: Name of the service/module

    Returns:
        Configured logger instance
    """
    logging.config.dictConfig(LOGGING_CONFIG)
    force_all_loggers_to_use_root_handler()
    logger = logging.getLogger(service_name)
    return logger