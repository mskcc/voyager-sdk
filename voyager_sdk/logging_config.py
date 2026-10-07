import logging
import os
import sys

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"


def setup_logging(verbosity=0):
    """
    Configure the root "voyager_sdk" logger.
    Level resolution: VOYAGER_LOG_LEVEL env var if set, otherwise
    0 -> WARNING, 1 (-v) -> INFO, 2+ (-vv) -> DEBUG.
    Logs go to stderr so they don't mix with command output on stdout.
    """
    env_level = os.environ.get("VOYAGER_LOG_LEVEL")
    if env_level:
        level = logging.getLevelName(env_level.upper())
        if not isinstance(level, int):
            level = logging.WARNING
    elif verbosity >= 2:
        level = logging.DEBUG
    elif verbosity == 1:
        level = logging.INFO
    else:
        level = logging.WARNING

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger = logging.getLogger("voyager_sdk")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
