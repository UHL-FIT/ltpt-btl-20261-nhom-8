import customtkinter as ctk

from app.utils.logger import get_logger


logger = get_logger(__name__)


class Header(ctk.CTkFrame):

    def __init__(self, parent, menu_callback=None):
        """Khởi tạo thanh header và gắn callback cho nút menu."""
        super().__init__(
            parent,
            height=60,
            fg_color="white",
            border_width=2,
            border_color="#eaeaea",
            corner_radius=0,
        )

        self.pack_propagate(False)
        self.menu_callback = menu_callback
        logger.info("Khởi tạo Header.")

        self.create_widgets()

    def set_title(self, title):
        """Cập nhật tiêu đề đang hiển thị trên header."""
        self.title_label.configure(text=title)
        logger.info("Cập nhật tiêu đề header: %s", title)

    def create_widgets(self):
        """Tạo các widget con của header."""
        # Nút menu dùng để ẩn/hiện sidebar.
        self.menu_button = ctk.CTkButton(
            self,
            text="☰",
            width=45,
            height=40,
            font=("Arial", 20, "bold"),
            fg_color="transparent",
            hover_color="#E2E8F0",
            text_color="#111827",
            command=self.menu_callback,
        )
        self.menu_button.pack(side="left", padx=(20, 10))

        # Tiêu đề trang hiện tại.
        self.title_label = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=("Arial", 24, "bold"),
            text_color="#111827",
        )
        self.title_label.pack(side="left")