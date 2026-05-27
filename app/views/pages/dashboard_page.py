import customtkinter as ctk

from app.utils.logger import get_logger


logger = get_logger(__name__)


class DashboardPage(ctk.CTkFrame):
    """Trang tổng quan của ứng dụng."""

    def __init__(self, parent, database, show_page_callback):
        """Khởi tạo trang Dashboard và tạo toàn bộ giao diện."""
        super().__init__(parent, fg_color="#F8FAFC", corner_radius=0)
        self.database = database
        self.show_page_callback = show_page_callback
        logger.info("Khoi tao DashboardPage.")

        self._create_widgets()

    def _create_widgets(self):
        """Tạo khung cuộn và gắn toàn bộ nội dung vào bên trong."""
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#F8FAFC",
            corner_radius=0,
            scrollbar_fg_color="#D8E6FF",
            scrollbar_button_color="#2F74FF",
            scrollbar_button_hover_color="#0050DB",
        )
        self.scroll_frame.pack(fill="both", expand=True)
        self.scroll_frame._scrollbar.configure(width=12)

        self._create_title_section()
        self._create_navigation_cards()
        self._create_statistics_cards()

    def _create_title_section(self):
        """Tạo phần tiêu đề ở phía trên cùng."""
        title_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="#2F74FF",
            height=110,
            corner_radius=0,
        )
        title_frame.pack(fill="x", pady=(0, 20))
        title_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            title_frame,
            text="Tổng quan hệ thống",
            font=("Arial", 28, "bold"),
            text_color="#FFFFFF",
            fg_color="transparent",
            anchor="w",
        )
        title_label.pack(anchor="w", padx=30, pady=(25, 2))

        content_label = ctk.CTkLabel(
            title_frame,
            text="Theo dõi nhanh các chức năng và số liệu chính của hệ thống",
            font=("Arial", 12),
            text_color="#FFFFFF",
            fg_color="transparent",
            anchor="w",
        )
        content_label.pack(anchor="w", padx=30, pady=(0, 0))

    def _create_navigation_cards(self):
        """Tạo các thẻ điều hướng đến từng trang chức năng."""
        cards_button_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        cards_button_frame.pack(fill="x", padx=30, pady=(0, 20))

        for col in range(3):
            cards_button_frame.grid_columnconfigure(col, weight=1, uniform="card_button")

        self._create_navigation_card(
            cards_button_frame,
            0,
            0,
            "💯",
            "Quản lý bảng điểm",
            "Nhập điểm, lọc học kỳ, xem chi tiết GPA",
            "scores",
        )
        self._create_navigation_card(
            cards_button_frame,
            0,
            1,
            "🎓",
            "Quản lý sinh viên",
            "Thêm, sửa, xóa, import/export danh sách",
            "students",
        )
        self._create_navigation_card(
            cards_button_frame,
            0,
            2,
            "📘",
            "Quản lý học phần",
            "Quản lý môn học và số tín chỉ",
            "courses",
        )
        self._create_navigation_card(
            cards_button_frame,
            1,
            0,
            "📈",
            "Thống kê & biểu đồ",
            "GPA trung bình, xếp loại, top sinh viên",
            "stats",
        )
        self._create_navigation_card(
            cards_button_frame,
            1,
            1,
            "ℹ️",
            "Thông tin",
            "Phiên bản, tác giả, hướng dẫn sử dụng",
            "about",
        )

    def _create_navigation_card(self, parent, row, column, icon, title, content, page_name):
        """Tạo một thẻ chức năng để mở trang tương ứng."""
        card_button = ctk.CTkFrame(
            parent,
            fg_color="white",
            height=170,
            corner_radius=16,
            border_width=2,
            border_color="#2F74FF",
        )
        card_button.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        card_button.grid_propagate(False)

        icon_label = ctk.CTkLabel(
            card_button,
            text=icon,
            font=("Arial", 50),
            text_color="#2F74FF",
        )
        icon_label.pack(anchor="w", padx=20, pady=(20, 6))

        title_label = ctk.CTkLabel(
            card_button,
            text=title,
            font=("Arial", 16, "bold"),
            text_color="#111827",
        )
        title_label.pack(anchor="w", padx=20, pady=(0, 2))

        content_label = ctk.CTkLabel(
            card_button,
            text=content,
            font=("Arial", 13),
            text_color="#616161",
            wraplength=260,
            justify="left",
        )
        content_label.pack(anchor="w", padx=20, pady=(0, 12))

        button_card = ctk.CTkButton(
            card_button,
            text="Truy cập",
            height=40,
            width=120,
            font=("Arial", 14, "bold"),
            fg_color="#2F74FF",
            hover_color="#0050DB",
            text_color="white",
            corner_radius=10,
            command=lambda: self._open_page(page_name),
        )
        button_card.pack(anchor="w", padx=20, pady=(0, 15))

    def _open_page(self, page_name):
        """Mở trang được chọn từ thẻ điều hướng."""
        logger.info("Nguoi dung chon trang tu Dashboard: %s", page_name)
        self.show_page_callback(page_name)

    def _create_statistics_cards(self):
        """Tạo 4 thẻ thống kê ở phía dưới."""
        cards_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30, pady=(10, 20))

        for col in range(4):
            cards_frame.grid_columnconfigure(col, weight=1, uniform="stat_card")

        students_count, courses_count, best_gpa, avg_gpa = self._get_dashboard_stats()

        self._create_stat_card(cards_frame, 0, 0, "👥", "Sinh viên", str(students_count), "#6366F1")
        self._create_stat_card(cards_frame, 0, 1, "📘", "Học phần", str(courses_count), "#A855F7")
        self._create_stat_card(cards_frame, 0, 2, "🏆", "GPA Cao Nhất", f"{best_gpa:.2f}", "#10B981")
        self._create_stat_card(cards_frame, 0, 3, "⭐", "GPA Trung Bình", f"{avg_gpa:.2f}", "#F59E0B")

    def _get_dashboard_stats(self):
        """Lấy các số liệu cần hiển thị trên Dashboard."""
        students_count = len(self.database.fetch_students())
        courses_count = len(self.database.fetch_courses())

        scores = self.database.fetch_scores()
        scored_rows = []
        for score in scores:
            if score[4] != "Chưa có điểm":
                scored_rows.append(score)

        best_gpa = 0.0
        avg_gpa = 0.0
        if scored_rows:
            total_gpa = 0.0
            for score in scored_rows:
                gpa_value = float(score[3])
                total_gpa += gpa_value
                if gpa_value > best_gpa:
                    best_gpa = gpa_value
            avg_gpa = total_gpa / len(scored_rows)

        return students_count, courses_count, best_gpa, avg_gpa

    def _create_stat_card(self, parent, row, column, icon, title, value, color):
        """Tạo một thẻ thống kê nhỏ."""
        card = ctk.CTkFrame(
            parent,
            fg_color="white",
            height=140,
            corner_radius=16,
            border_width=2,
            border_color="#2F74FF",
        )
        card.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        card.grid_propagate(False)

        icon_label = ctk.CTkLabel(card, text=icon, font=("Arial", 26), text_color=color)
        icon_label.pack(padx=20, pady=(18, 2))

        title_label = ctk.CTkLabel(card, text=title, font=("Arial", 18), text_color="#64748B")
        title_label.pack(padx=20, pady=(0, 4))

        value_label = ctk.CTkLabel(card, text=value, font=("Arial", 32, "bold"), text_color=color)
        value_label.pack(padx=20, pady=(0, 18))
