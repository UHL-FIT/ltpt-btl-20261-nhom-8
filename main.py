import customtkinter as ctk
import sys
import os

# Đảm bảo đường dẫn module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.main_controller import MainController
from utils.logger import setup_logger

logger = setup_logger("main")
__version__ = "1.0.0"

if __name__ == "__main__":
    logger.info(f"=== Khởi chạy Phần mềm Quản lý Kết quả Học tập v{__version__} ===")
    
    # Thiết lập cấu hình mặc định cho CustomTkinter
    ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    
    try:
        # Khởi tạo và chạy controller
        app = MainController()
        app.run()
    except Exception as e:
        logger.error(f"Lỗi nghiêm trọng khi khởi chạy ứng dụng: {e}", exc_info=True)
