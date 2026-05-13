import logging
from pathlib import Path


def get_app_root() -> Path:
    return Path(__file__).resolve().parents[1]


def setup_logger(name: str = "ketqua_hoc_tap") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    log_dir = get_app_root() / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "app.log"

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
