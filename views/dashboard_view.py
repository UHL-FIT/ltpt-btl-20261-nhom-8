import customtkinter as ctk

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.controller = controller

        # Bố cục chính
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Container chứa các widget
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.container.grid_columnconfigure((0, 1), weight=1)

        # Tiêu đề
        self.title_label = ctk.CTkLabel(
            self.container, text="HỆ THỐNG QUẢN LÝ KẾT QUẢ HỌC TẬP", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(30, 20))

        # Khung thời tiết
        self.weather_frame = ctk.CTkFrame(self.container, fg_color=("gray85", "gray25"))
        self.weather_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        self.weather_label = ctk.CTkLabel(
            self.weather_frame, text="Đang tải dữ liệu thời tiết...", 
            font=ctk.CTkFont(size=14, slant="italic")
        )
        self.weather_label.pack(pady=10)

        # Các nút điều hướng lớn
        btn_font = ctk.CTkFont(size=18, weight="bold")
        
        self.btn_student = ctk.CTkButton(
            self.container, text="🧑‍🎓 Quản lý Sinh viên", font=btn_font, height=80,
            command=lambda: self.controller.switch_frame("student")
        )
        self.btn_student.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

        self.btn_score = ctk.CTkButton(
            self.container, text="📊 Quản lý Bảng điểm", font=btn_font, height=80,
            command=lambda: self.controller.switch_frame("score")
        )
        self.btn_score.grid(row=2, column=1, padx=20, pady=20, sticky="nsew")

        self.btn_stats = ctk.CTkButton(
            self.container, text="📈 Thống kê & Biểu đồ", font=btn_font, height=80,
            command=lambda: self.controller.switch_frame("stats")
        )
        self.btn_stats.grid(row=3, column=0, padx=20, pady=20, sticky="nsew")

        self.btn_about = ctk.CTkButton(
            self.container, text="ℹ️ Thông tin phần mềm", font=btn_font, height=80,
            command=self.show_about
        )
        self.btn_about.grid(row=3, column=1, padx=20, pady=20, sticky="nsew")

    def update_weather(self, success, data, error):
        if success:
            self.weather_label.configure(text=f"🌤️ Thời tiết hiện tại: {data}")
        else:
            self.weather_label.configure(text=f"⚠️ Lỗi tải thời tiết")

    def show_about(self):
        # Hiển thị thông tin
        from tkinter import messagebox
        messagebox.showinfo("About", "Phần mềm Quản lý Kết quả Học tập\nPhiên bản: 1.0.0\nTác giả: User & AI")
