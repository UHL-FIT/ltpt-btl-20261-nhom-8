from models.student_model import StudentModel
from models.subject_model import SubjectModel
from models.score_model import ScoreModel
from views.app_view import AppView
from utils.api_client import WeatherAPI
from utils.logger import setup_logger

logger = setup_logger("main_controller")

class MainController:
    """Controller chính điều phối toàn bộ ứng dụng"""
    def __init__(self):
        logger.info("Khởi tạo MainController...")
        
        # 1. Khởi tạo Models
        self.score_model = ScoreModel()
        self.student_model = StudentModel(self.score_model) # Truyền score_model để join GPA
        self.subject_model = SubjectModel()
        self.weather_api = WeatherAPI()

        # 2. Khởi tạo View chính
        self.app_view = AppView(self)
        self.current_frame_name = "dashboard"

    def run(self):
        """Khởi chạy ứng dụng"""
        logger.info("Chạy ứng dụng GUI...")
        self.switch_frame("dashboard")
        
        # Chạy tải API thời tiết ở background
        self.weather_api.fetch_weather_async(self.app_view.frames["dashboard"].update_weather)
        
        self.app_view.mainloop()

    def switch_frame(self, name):
        """Đổi sang frame khác theo tên"""
        logger.debug(f"Điều hướng sang màn hình: {name}")
        self.current_frame_name = name
        self.app_view.show_frame(name)

    def refresh_current_view(self):
        """Làm mới dữ liệu của view đang hiển thị"""
        self.app_view.show_frame(self.current_frame_name)
