from __future__ import annotations

import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from app.utils.database import get_app_root
from app.views.ui_helpers import center_window


class AboutWindow:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.window = ctk.CTkToplevel(parent)
        self.window.title("About")
        self.window.geometry("560x430")
        self.window.transient(parent)
        self.setup_ui()
        center_window(self.window, parent)

    def setup_ui(self) -> None:
        wrapper = ctk.CTkFrame(self.window)
        wrapper.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)
        ctk.CTkLabel(wrapper, text="Quản lý Kết quả Học tập", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(10, 6), padx=12)
        info = (
            "Phiên bản: 1.0.0\n"
            "Tác giả: Nhóm 8\n"
            "Ngày phát hành: 06/05/2026\n"
            "Công nghệ: Python, CustomTkinter, SQLite, Pandas, NumPy, Matplotlib\n\n"
            "Ứng dụng quản lý sinh viên, học phần, bảng điểm, tính GPA tự động theo học kỳ/năm học, "
            "hỗ trợ import/export CSV và thống kê trực quan."
        )
        ctk.CTkLabel(wrapper, text=info, justify="left", wraplength=500).pack(anchor="w", padx=12, pady=12)
        ctk.CTkButton(wrapper, text="Mở hướng dẫn sử dụng", command=self.open_guide).pack(anchor="w", padx=12, pady=(10, 6))
        ctk.CTkButton(wrapper, text="Đóng", fg_color="#64748b", command=self.window.destroy).pack(anchor="e", padx=12, pady=(20, 10))

    def open_guide(self) -> None:
        guide = get_app_root() / "assets" / "docs" / "HUONG_DAN.md"
        try:
            os.startfile(guide)  # type: ignore[attr-defined]
        except Exception as exc:
            messagebox.showerror("Lỗi", f"Không thể mở hướng dẫn: {exc}", parent=self.window)
