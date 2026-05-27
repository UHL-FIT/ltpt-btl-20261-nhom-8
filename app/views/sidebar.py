import customtkinter as ctk

from app.utils.logger import get_logger


logger = get_logger(__name__)


class Sidebar(ctk.CTkFrame):
    """Thanh điều hướng bên trái của cửa sổ chính."""

    def __init__(self, parent, show_page_callback):
        """Khởi tạo sidebar và tạo các nút điều hướng."""
        super().__init__(
            parent,
            width=220,
            fg_color="#00023a",
            corner_radius=0,
        )
        self.pack_propagate(False)

        self.show_page_callback = show_page_callback
        self.buttons: dict[str, ctk.CTkButton] = {}
        self.button_texts: dict[str, tuple[str, str]] = {}
        self.is_collapsed = False
        self.expanded_width = 220
        self.collapsed_width = 72

        logger.info("Khởi tạo Sidebar.")
        self.create_widgets()

    def create_widgets(self):
        """Tạo phần tiêu đề và các nút điều hướng."""
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.pack(anchor="w", padx=20, pady=(30, 25))

        self.title_main = ctk.CTkLabel(
            self.title_frame,
            text="🎓 ACADEMIC",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white",
        )
        self.title_main.pack(anchor="w")

        self.title_sub = ctk.CTkLabel(
            self.title_frame,
            text="MANAGER SYSTEM",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#CBD5E1",
        )
        self.title_sub.pack(anchor="w")

        self.create_button("dashboard", "💻 Dashboard", "💻")
        self.create_button("scores", "💯 Bảng điểm", "💯")
        self.create_button("students", "🎓 Sinh viên", "🎓")
        self.create_button("courses", "📚 Học phần", "📚")
        self.create_button("stats", "📈 Thống kê", "📈")
        self.create_button("about", "ⓘ Giới thiệu", "ⓘ")

    def create_button(self, page_name, expanded_text, collapsed_text):
        """Tạo một nút điều hướng cho từng trang."""
        button = ctk.CTkButton(
            self,
            text=expanded_text,
            height=42,
            corner_radius=10,
            font=("Arial", 14),
            fg_color="transparent",
            hover_color="#475569",
            text_color="white",
            anchor="w",
            command=lambda: self._handle_page_change(page_name),
        )
        button.pack(padx=20, pady=2, fill="x")

        self.buttons[page_name] = button
        self.button_texts[page_name] = (expanded_text, collapsed_text)
        logger.info("Đã tạo nút sidebar: %s", page_name)

    def set_active_button(self, active_page):
        """Đánh dấu nút của trang hiện tại."""
        for page_name, button in self.buttons.items():
            if page_name == active_page:
                button.configure(fg_color="#6366F1")
            else:
                button.configure(fg_color="transparent")
        logger.info("Đã đổi trạng thái nút sidebar sang: %s", active_page)

    def set_collapsed(self, collapsed: bool):
        """Thu gọn hoặc mở rộng sidebar nhưng vẫn giữ dải icon điều hướng."""
        self.is_collapsed = collapsed

        if collapsed:
            self.configure(width=self.collapsed_width)
            self.title_frame.pack_configure(anchor="center", padx=0, pady=(18, 16))
            self.title_main.configure(text="🎓", font=ctk.CTkFont(size=24, weight="bold"))
            self.title_sub.pack_forget()

            for page_name, button in self.buttons.items():
                _, collapsed_text = self.button_texts[page_name]
                button.configure(
                    text=collapsed_text,
                    width=52,
                    font=("Arial", 18, "bold"),
                    anchor="center",
                )
                button.pack_configure(padx=10, pady=2)

            logger.info("Sidebar đã thu gọn.")
        else:
            self.configure(width=self.expanded_width)
            self.title_frame.pack_configure(anchor="w", padx=20, pady=(30, 25))
            self.title_main.configure(text="🎓 ACADEMIC", font=ctk.CTkFont(size=22, weight="bold"))
            if not self.title_sub.winfo_ismapped():
                self.title_sub.pack(anchor="w")

            for page_name, button in self.buttons.items():
                expanded_text, _ = self.button_texts[page_name]
                button.configure(
                    text=expanded_text,
                    width=180,
                    font=("Arial", 14),
                    anchor="w",
                )
                button.pack_configure(padx=20, pady=2)

            logger.info("Sidebar đã mở rộng.")

    def _handle_page_change(self, page_name):
        """Gọi callback chuyển trang và ghi log."""
        logger.info("Người dùng chọn trang từ Sidebar: %s", page_name)
        self.show_page_callback(page_name)
