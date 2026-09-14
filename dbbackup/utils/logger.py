import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_logger(name: str = "dbbackup") -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        # Already configured (avoids duplicate handlers if called multiple times)
        return logger

    logger.setLevel(logging.INFO)

    log_dir = Path("./logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_dir / "dbbackup.log", maxBytes=1_000_000, backupCount=3
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger