from app.controllers.app_controller import run_app

from app.utils.logger import get_logger


logger = get_logger(__name__)
# Import hàm run_app từ app/controllers/app_controller.py.
# File main.py dùng hàm này để khởi động toàn bộ ứng dụng.

if __name__ == "__main__":
    logger.info("Khởi chạy file main.py.")
    run_app()
# Chỉ khi chạy trực tiếp main.py thì app mới được khởi động.
# Nếu file này được import từ file khác thì khối if bên trên sẽ không chạy.