import logging
import sys


def setup_logger(name: str = "KanbanApp", level: int = logging.INFO) -> logging.Logger:
    """Khởi tạo logger chuẩn hóa cho hệ thống Backend Kanban."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)

        # Định dạng log chuyên nghiệp
        dinh_dang = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(dinh_dang)
        logger.addHandler(console_handler)

        logger.propagate = False

    return logger


logger = setup_logger()
