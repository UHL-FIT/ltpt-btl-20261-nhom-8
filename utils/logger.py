import logging
import os
from pathlib import Path

def setup_logger(name: str) -> logging.Logger:
    """
    Khởi tạo và cấu hình logger.
    Ghi log vào file data/app.log và in ra console.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # Đảm bảo thư mục data tồn tại
        log_dir = Path("data")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "app.log"

        # Định dạng log
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Ghi ra file
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # In ra console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
