import customtkinter as ctk
from views.dashboard_view import DashboardView
from views.student_view import StudentView
from views.score_view import ScoreView
from views.stats_view import StatsView

class AppView(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        # Cấu hình cửa sổ
        self.title("Quản lý Kết quả Học tập (Nhóm 8 - OOP Version)")
        self.geometry("1100x700")
        self.minsize(900, 600)
        
        # Cấu hình grid chính
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="🎓 QL Sinh Viên", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        # Nút điều hướng
        self.nav_btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Trang chủ", command=lambda: self.controller.switch_frame("dashboard"))
        self.nav_btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        self.nav_btn_student = ctk.CTkButton(self.sidebar_frame, text="Quản lý Sinh viên", command=lambda: self.controller.switch_frame("student"))
        self.nav_btn_student.grid(row=2, column=0, padx=20, pady=10)

        self.nav_btn_score = ctk.CTkButton(self.sidebar_frame, text="Quản lý Điểm", command=lambda: self.controller.switch_frame("score"))
        self.nav_btn_score.grid(row=3, column=0, padx=20, pady=10)

        self.nav_btn_stats = ctk.CTkButton(self.sidebar_frame, text="Thống kê", command=lambda: self.controller.switch_frame("stats"))
        self.nav_btn_stats.grid(row=4, column=0, padx=20, pady=10)

        # Theme toggle
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Giao diện:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame, values=["Dark", "Light", "System"],
            command=self.change_appearance_mode_event
        )
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 20))
        self.appearance_mode_optionemenu.set("Dark")

        # --- Main Container ---
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Khởi tạo các View
        self.frames = {}
        
        self.frames["dashboard"] = DashboardView(self.main_container, self.controller)
        self.frames["student"] = StudentView(self.main_container, self.controller)
        self.frames["score"] = ScoreView(self.main_container, self.controller)
        self.frames["stats"] = StatsView(self.main_container, self.controller)

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, name):
        """Hiển thị frame mong muốn và cập nhật dữ liệu của nó"""
        frame = self.frames[name]
        frame.tkraise()
        
        # Cập nhật dữ liệu mỗi khi switch
        if hasattr(frame, "refresh_data"):
            frame.refresh_data()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        # Bắt buộc render lại biểu đồ nếu có thay đổi theme
        if hasattr(self.frames["stats"], "refresh_data"):
            self.frames["stats"].refresh_data()
