import logging
import sys


def setup_logging(
    root_level: str = "DEBUG",
    stream_handler_level: str = "INFO",
    # file_handler_level: str = "DEBUG", TODO: to be added later
    fmt: str = "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
) -> None:
    """
    Configure logging for the entire NutriTrack application.
    Call once at app startup — in main.py or FastAPI lifespan.

    Args:
        root_level:           minimum level root logger captures (default: DEBUG)
        stream_handler_level: minimum level printed to terminal (default: INFO)
        fmt:                  log format string (default: timestamp + level + module + message)
    """

    # Setup stream handler
    formatter = logging.Formatter(fmt)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(getattr(logging, stream_handler_level.upper()))

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, root_level.upper()))

    ############################
    # Alternatives:
    #
    # 1) Another approach for fmt parameter if its definition is
    #      fmt: Optional[str] = None
    # default_fmt = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
    # formatter = logging.Formatter(fmt or default_fmt)
    #
    # 2) Logs into a file
    # file_handler = logging.FileHandler("app.log")
    # file_handler.setFormatter(formatter)
    # file_handler.setLevel(getattr(logging, "DEBUG"))


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger. Use __name__ as the name argument.

    Usage:
        logger = get_logger(__name__)
    """
    return logging.getLogger(name)
