import logging
import sys
import os
from datetime import datetime


def setup_logger(name: str = "paper_polish") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler(
            f"logs/app_{datetime.now().strftime('%Y%m%d')}.log", encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()
