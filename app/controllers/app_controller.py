"""Điểm khởi động của ứng dụng và nơi ghép database với các controller."""

from app.controllers.course_controller import CourseController
from app.controllers.score_controller import ScoreController
from app.controllers.student_controller import StudentController
from app.models.database import AppDatabase
from app.utils.logger import get_logger
from app.views.main_windows import MainWindow


logger = get_logger(__name__)


def run_app():
    """Khởi tạo database, controller và cửa sổ chính của ứng dụng."""
    # Khởi tạo đối quản lý database
    database = AppDatabase()
    logger.info("Đã khởi tạo database dùng chung cho ứng dụng.")

    
    controllers = {
        "student": StudentController(database),
        "course": CourseController(database),
        "score": ScoreController(database),
    }
    logger.info("Đã tạo xong các controller: student, course, score.")

    app = MainWindow(database, controllers)
    logger.info("Đã tạo cửa sổ chính MainWindow và sẵn sàng chạy ứng dụng.")
    app.mainloop()
