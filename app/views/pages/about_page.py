import os
from pathlib import Path

import customtkinter as ctk
from tkinter import messagebox

from app.utils.logger import get_logger


logger = get_logger(__name__)


class AboutPage(ctk.CTkFrame):
    """Trang giới thiệu ứng dụng và mở file hướng dẫn sử dụng."""

    def __init__(self, parent):
        """Khởi tạo trang About."""
        super().__init__(parent, fg_color="#F8FAFC", corner_radius=0)
        logger.info("Khởi tạo AboutPage.")
        self._create_widgets()

    def _create_widgets(self):
        """Tạo toàn bộ giao diện của trang giới thiệu."""
        content_box = ctk.CTkFrame(
            self,
            fg_color="#f3f5ff",
            corner_radius=16,
            border_width=2,
            border_color="#2F74FF",
        )
        content_box.pack(fill="both", expand=True, padx=30, pady=30)
        content_box.grid_columnconfigure(0, weight=1)
        content_box.grid_rowconfigure(0, weight=1)
        content_box.grid_rowconfigure(1, weight=0)

        body_frame = ctk.CTkFrame(content_box, fg_color="transparent")
        body_frame.grid(row=0, column=0, sticky="nsew", padx=28, pady=(24, 12))
        body_frame.grid_columnconfigure(0, weight=1)

        self._create_header_section(body_frame)
        self._create_info_section(body_frame)
        self._create_note_section(body_frame)
        self._create_tutorial_button(body_frame)
        self._create_footer_section(content_box)

    def _create_header_section(self, parent):
        """Tạo phần tiêu đề ở đầu trang."""
        icon_label = ctk.CTkLabel(
            parent,
            text="🎓",
            font=("Arial", 80),
            text_color="#2F74FF",
        )
        icon_label.pack(anchor="center", pady=(12, 6))

        heading_label = ctk.CTkLabel(
            parent,
            text="HỆ THỐNG QUẢN LÝ VÀ PHÂN TÍCH KẾT QUẢ HỌC TẬP",
            font=("Arial", 22, "bold"),
            text_color="#2F74FF",
        )
        heading_label.pack(anchor="center", pady=(0, 10))

    def _create_info_section(self, parent):
        """Tạo đoạn mô tả ngắn về ứng dụng."""
        info_text = (
            "Phiên bản: 1.0.0\n"
            "Ứng dụng dùng để phục vụ việc quản lý, theo dõi và phân tích\n"
            "tiến độ học tập của sinh viên một cách chuyên nghiệp và hiệu quả.\n"
            "Sử dụng công nghệ Python, NumPy, Pandas, CustomTkinter, Matplotlib và SQLite."
        )
        info_label = ctk.CTkLabel(
            parent,
            text=info_text,
            font=("Arial", 14),
            text_color="#6A6A6A",
            justify="center",
        )
        info_label.pack(anchor="center", pady=(18, 16))

    def _create_note_section(self, parent):
        """Tạo khung ghi chú về nhóm phát triển."""
        note_box = ctk.CTkFrame(
            parent,
            fg_color="#E0EBFF",
            corner_radius=12,
            border_width=2,
            border_color="#2F74FF",
        )
        note_box.pack(fill="x", padx=24, pady=(12, 10))
        note_box.grid_columnconfigure(0, weight=1)

        note_title = ctk.CTkLabel(
            note_box,
            text="PHÁT TRIỂN BỞI NHÓM 8",
            font=("Arial", 16, "bold"),
            text_color="#111827",
        )
        note_title.pack(anchor="center", pady=(18, 8))

        note_text = (
            "· Quản lý dữ liệu: Thành viên A\n\n"
            "· Giao diện & UX: Thành viên B\n\n"
            "· Phân tích & Thống kê: Thành viên C\n\n"
            "· Kiểm thử & Tài liệu: Thành viên D"
        )
        note_label = ctk.CTkLabel(
            note_box,
            text=note_text,
            font=("Arial", 14),
            text_color="#626262",
            justify="left",
        )
        note_label.pack(anchor="center", padx=24, pady=(0, 18))

    def _create_tutorial_button(self, parent):
        """Tạo nút mở file hướng dẫn sử dụng PDF."""
        button_tutorial = ctk.CTkButton(
            parent,
            text="📑 Tải hướng dẫn sử dụng (PDF)",
            height=30,
            width=50,
            fg_color="#2F74FF",
            hover_color="#0043C8",
            command=self.open_tutorial_pdf,
        )
        button_tutorial.pack(anchor="center", pady=(20, 0))

    def _create_footer_section(self, parent):
        """Tạo phần chân trang ở cuối khung giới thiệu."""
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 18))

        copyright_label = ctk.CTkLabel(
            footer_frame,
            text="© 2026 Nhóm 8 - Bài tập lớn Lập trình Python",
            font=("Arial", 12),
            text_color="#AEAEAE",
            justify="center",
        )
        copyright_label.pack()

    def _get_tutorial_pdf_path(self):
        """Trả về đường dẫn file PDF hướng dẫn sử dụng."""
        return (
            Path(__file__).resolve().parents[2]
            / "docs"
            / "Huong_Dan_Su_Dung_Ket_Qua_Hoc_Tap_App.pdf"
        )

    def open_tutorial_pdf(self):
        """Mở file PDF hướng dẫn sử dụng."""
        pdf_path = self._get_tutorial_pdf_path()

        if not pdf_path.exists():
            logger.error("Không tìm thấy file hướng dẫn: %s", pdf_path)
            messagebox.showerror(
                "Không tìm thấy file",
                f"Không tìm thấy file hướng dẫn tại:\n{pdf_path}",
                parent=self,
            )
            return

        try:
            os.startfile(pdf_path)  # type: ignore[attr-defined]
            logger.info("Đã mở file hướng dẫn: %s", pdf_path)
        except Exception as exc:
            logger.error("Không thể mở file hướng dẫn %s: %s", pdf_path, exc)
            messagebox.showerror(
                "Không thể mở file",
                f"Không thể mở file hướng dẫn:\n{exc}",
                parent=self,
            )
