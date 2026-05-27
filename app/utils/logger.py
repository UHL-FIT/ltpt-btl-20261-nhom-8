from __future__ import annotations

import logging
from pathlib import Path


_LOGGER_CACHE: dict[str, logging.Logger] = {}


def get_logger(name: str) -> logging.Logger:
    """Lấy logger dùng chung cho toàn dự án.

    Logger sẽ ghi log ra file `app/logs/app.log`.
    Nếu thư mục logs chưa có thì tự tạo.
    """
    if name in _LOGGER_CACHE:
        return _LOGGER_CACHE[name]

    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                "%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(file_handler)

    _LOGGER_CACHE[name] = logger
    return logger
