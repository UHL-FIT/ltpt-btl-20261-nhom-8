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
        accent = "#2F74FF"
        """Tạo các thẻ điều hướng đến từng trang chức năng."""
        navigation_card_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        navigation_card_frame.pack(fill="x", padx=30, pady=(0, 20))

        for col in range(3):
            navigation_card_frame.grid_columnconfigure(col, weight=1, uniform="navigation_button")

        self._create_navigation_card(
            navigation_card_frame,
            0,
            0,
            "💯",
            "Quản lý bảng điểm",
            "Nhập điểm, lọc học kỳ, xem chi tiết CPA",
            "scores",
            accent
        )
        self._create_navigation_card(
            navigation_card_frame,
            0,
            1,
            "🎓",
            "Quản lý sinh viên",
            "Thêm, sửa, xóa, import/export danh sách",
            "students",
            accent
        )
        self._create_navigation_card(
            navigation_card_frame,
            0,
            2,
            "📘",
            "Quản lý học phần",
            "Quản lý môn học và số tín chỉ",
            "courses",
            accent
        )
        self._create_navigation_card(
            navigation_card_frame,
            1,
            0,
            "📈",
            "Thống kê & biểu đồ",
            "CPA trung bình, xếp loại, top sinh viên",
            "stats",
            accent
        )
        self._create_navigation_card(
            navigation_card_frame,
            1,
            1,
            "ℹ️",
            "Thông tin",
            "Phiên bản, tác giả, hướng dẫn sử dụng",
            "about",
            accent
        )

    def _create_navigation_card(self, parent, row, column, icon, title, content, page_name, accent):
        """Tạo một thẻ chức năng để mở trang tương ứng."""
        navigation_button = ctk.CTkFrame(
            parent,
            fg_color="white",
            height=170,
            corner_radius=16,
            border_width=2,
            border_color="#2F74FF",
        )
        navigation_button.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        navigation_button.grid_propagate(False)

        icon_label = ctk.CTkLabel(
            navigation_button,
            text=icon,
            font=("Arial", 50),
            text_color="#2F74FF",
        )
        icon_label.pack(anchor="w", padx=20, pady=(20, 6))

        title_label = ctk.CTkLabel(
            navigation_button,
            text=title,
            font=("Arial", 16, "bold"),
            text_color="#111827",
        )
        title_label.pack(anchor="w", padx=20, pady=(0, 2))

        content_label = ctk.CTkLabel(
            navigation_button,
            text=content,
            font=("Arial", 13),
            text_color="#616161",
            wraplength=260,
            justify="left",
        )
        content_label.pack(anchor="w", padx=20, pady=(0, 12))

        button_card = ctk.CTkButton(
            navigation_button,
            text="Truy cập",
            height=40,
            width=120,
            font=("Arial", 14, "bold"),
            fg_color= accent,
            hover_color="#0050DB",
            text_color="white",
            corner_radius=10,
            command=lambda: self.show_page_callback(page_name),
        )
        button_card.pack(anchor="w", padx=20, pady=(0, 15))

    def _create_statistics_cards(self):
        """Tạo 4 thẻ thống kê ở phía dưới."""
        cards_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30, pady=(10, 20))

        for col in range(4):
            cards_frame.grid_columnconfigure(col, weight=1, uniform="stat_card")

        students_count, courses_count, best_cpa, avg_cpa = self._get_dashboard_stats()

        self._create_stat_card(cards_frame, 0, 0, "👥", "Sinh viên", str(students_count), "#6366F1")
        self._create_stat_card(cards_frame, 0, 1, "📘", "Học phần", str(courses_count), "#A855F7")
        self._create_stat_card(cards_frame, 0, 2, "🏆", "CPA Cao Nhất", f"{best_cpa:.2f}", "#10B981")
        self._create_stat_card(cards_frame, 0, 3, "⭐", "CPA Trung Bình", f"{avg_cpa:.2f}", "#F59E0B")

    def _get_dashboard_stats(self):
        """Lấy các số liệu cần hiển thị trên Dashboard."""
        students_count = len(self.database.fetch_students())
        courses_count = len(self.database.fetch_courses())

        scores = self.database.fetch_scores()
        logger.info("Lấy dữ liệu bảng scores từ database.py trong models và gán cho biến scores")
        scored_rows = [] # Tạo một biến  danh sách rỗng để chứa điểm được lấy từ bảng scores
        # Tạo một vòng lặp duyệt qua từng dòng của bảng 
        for score in scores:
            # Dòng nào có cột score[4] là cột grade 
            # nếu grade khác "Chưa có điểm" thì mới thêm vào scored_rows
            # Tức là chỉ thêm điểm của những sinh viên đã có điểm vào scored_rows
            if score[4] != "Chưa có điểm":
                scored_rows.append(score)

        best_cpa = 0.0
        avg_cpa = 0.0
        if scored_rows:
            total_cpa = 0.0
            # vòng lặp lấy điểm CPA cao nhất và tính trung bình CPA
            for score in scored_rows:
                cpa_value = float(score[3])
                total_cpa += cpa_value
                if cpa_value > best_cpa:
                    best_cpa = cpa_value
            avg_cpa = total_cpa / len(scored_rows)

        return students_count, courses_count, best_cpa, avg_cpa

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
