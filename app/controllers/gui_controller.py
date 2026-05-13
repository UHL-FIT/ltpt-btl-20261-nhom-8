from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from app.models.bangdiem import BangDiemModel
from app.models.monhoc import MonHocModel
from app.models.sinhvien import SinhVienModel
from app.utils.database import Database, initialize_schema
from app.views.dashboard import Dashboard


class AppContext:
    def __init__(self, db_path: str | None = None) -> None:
        self.db = Database(db_path)
        initialize_schema(self.db)
        self.sinhvien = SinhVienModel(self.db)
        self.monhoc = MonHocModel(self.db)
        self.bangdiem = BangDiemModel(self.db)


def run_app() -> None:
    try:
        import customtkinter as ctk

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        root = ctk.CTk()
        root.title("Quản lý Kết quả Học tập - Nhóm 8")
        root.geometry("1180x760")
        root.minsize(980, 620)
        context = AppContext()
        Dashboard(root, context)
        root.mainloop()
    except Exception as exc:
        try:
            messagebox.showerror("Lỗi", f"Không thể khởi chạy ứng dụng: {exc}")
        except tk.TclError:
            print(f"Không thể khởi chạy ứng dụng: {exc}")
