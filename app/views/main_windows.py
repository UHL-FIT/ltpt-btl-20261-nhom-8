import customtkinter as ctk

from app.utils.logger import get_logger
from app.views.header import Header
from app.views.sidebar import Sidebar
from app.views.pages.about_page import AboutPage
from app.views.pages.course_page import CoursePage
from app.views.pages.dashboard_page import DashboardPage
from app.views.pages.score_page import ScorePage
from app.views.pages.stats_page import StatsPage
from app.views.pages.student_page import StudentPage


logger = get_logger(__name__)


class MainWindow(ctk.CTk):
    """Cửa sổ chính của ứng dụng."""

    def __init__(self, database, controllers):
        """Khởi tạo cửa sổ chính và dựng toàn bộ giao diện."""
        super().__init__()
        logger.info("Khởi động cửa sổ chính MainWindow.")

        self.title("Ứng dụng quản lý kết quả học tập")
        self.minsize(1200, 700)
        self.configure(fg_color="#F8FAFC")

        self.database = database
        self.controllers = controllers
        self.pages = {}
        self.sidebar_collapsed = False

        self._create_layout()
        logger.info("Khởi tạo layout cho MainWindow.")
        self._create_pages()
        logger.info("Khởi tạo trang cho MainWindow.")
        self.show_page("dashboard")
        logger.info("Hiển thị trang cho MainWindow.")
        self.after(0, lambda: self.state("zoomed"))
        logger.info("Áp dụng chế độ toàn màn hình cho MainWindow.")

    def _create_layout(self):
        """Tạo khung bố cục chính gồm sidebar, header và vùng nội dung."""
        self.sidebar = Sidebar(self, self.show_page)
        self.sidebar.pack(side="left", fill="y")

        self.main_area = ctk.CTkFrame(
            self,
            fg_color="#F2F9FF",
            corner_radius=0,
        )
        self.main_area.pack(side="right", fill="both", expand=True)

        self.header = Header(self.main_area, self.toggle_sidebar)
        self.header.pack(side="top", fill="x")

        self.content_frame = ctk.CTkFrame(
            self.main_area,
            fg_color="#F8FAFC",
            corner_radius=0,
        )
        self.content_frame.pack(side="bottom", fill="both", expand=True)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def _create_pages(self):
        """Khởi tạo các trang nội dung và đặt chồng lên nhau."""
        self.pages["dashboard"] = DashboardPage(
            self.content_frame,
            self.database,
            self.show_page,
        )
        logger.info("Khởi tạo trang dashboard từ MainWindow.")
        self.pages["scores"] = ScorePage(
            self.content_frame,
            self.database,
            self.controllers["score"],
        )
        self.pages["students"] = StudentPage(
            self.content_frame,
            self.database,
            self.controllers["student"],
        )
        self.pages["courses"] = CoursePage(
            self.content_frame,
            self.database,
            self.controllers["course"],
        )
        self.pages["stats"] = StatsPage(self.content_frame, self.database)
        self.pages["about"] = AboutPage(self.content_frame)

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def toggle_sidebar(self):
        """Thu gọn hoặc mở rộng sidebar để giữ lại dải icon điều hướng."""
        self.sidebar_collapsed = not self.sidebar_collapsed
        self.sidebar.set_collapsed(self.sidebar_collapsed)
        if self.sidebar_collapsed:
            logger.info("Đã thu gọn sidebar.")
        else:
            logger.info("Đã mở rộng sidebar.")

    def refresh_stats_page(self):
        """Làm mới trang thống kê nếu trang này có hỗ trợ refresh."""
        stats_page = self.pages.get("stats")
        if stats_page and hasattr(stats_page, "refresh_data"):
            stats_page.refresh_data()

    def refresh_score_page(self):
        """Làm mới trang bảng điểm nếu trang này có hỗ trợ refresh."""
        score_page = self.pages.get("scores")
        if score_page and hasattr(score_page, "refresh_data"):
            score_page.refresh_data()

    def get_page_title(self, page_name):
        """Lấy tiêu đề hiển thị trên header theo tên trang."""
        titles = {
            "dashboard": "Dashboard",
            "students": "Quản lý sinh viên",
            "courses": "Quản lý học phần",
            "scores": "Quản lý bảng điểm",
            "stats": "Thống kê số liệu",
            "about": "Giới thiệu",
        }
        return titles.get(page_name, "Ứng dụng")

    def show_page(self, page_name):
        """Hiển thị trang được chọn ở vùng nội dung chính."""
        if page_name not in self.pages:
            logger.warning("Yêu cầu mở trang không hợp lệ: %s", page_name)
            return

        if page_name == "scores":
            self.refresh_score_page()
        elif page_name == "stats":
            self.refresh_stats_page()

        page = self.pages[page_name]
        page.tkraise()
        logger.info("Đã chuyển sang trang: %s", page_name)

        self.sidebar.set_active_button(page_name)
        self.header.set_title(self.get_page_title(page_name))
