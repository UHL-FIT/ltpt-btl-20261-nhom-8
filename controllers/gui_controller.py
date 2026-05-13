from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from models.bangdiem import BangDiemModel
from models.monhoc import MonHocModel
from models.sinhvien import SinhVienModel
from utils.database import Database, initialize_schema
from utils.logger import setup_logger
from views.dashboard import Dashboard


logger = setup_logger("gui_controller")


class AppContext:
    def __init__(self, db_path: str | None = None) -> None:
        self.db = Database(db_path)
        initialize_schema(self.db)
        self.sinhvien = SinhVienModel(self.db)
        self.monhoc = MonHocModel(self.db)
        self.bangdiem = BangDiemModel(self.db)
        self.seed_if_empty()

    def seed_if_empty(self) -> None:
        if self.sinhvien.list_all() or self.monhoc.list_all():
            return
        for row in [
            ("SV001", "Nguyen Van A", "Nam", "21/08/2005", "DH10TT02A"),
            ("SV002", "Nguyen Van B", "Nam", "15/09/2006", "DH10TT02B"),
            ("SV003", "Nguyen Thi C", "Nữ", "01/07/2004", "DH10TT02E"),
        ]:
            self.sinhvien.add(*row)
        for row in [
            ("MH001", "Toán cao cấp", 3, "HK1"),
            ("MH002", "Lập trình căn bản", 3, "HK1"),
            ("MH003", "Cơ sở dữ liệu", 3, "HK2"),
            ("MH004", "Tiếng Anh 1", 2, "HK2"),
        ]:
            self.monhoc.add(*row)
        for row in [
            ("SV001", "MH001", "HK1", "2024-2025", 8.5),
            ("SV001", "MH002", "HK1", "2024-2025", 7.5),
            ("SV002", "MH001", "HK1", "2024-2025", 6.8),
        ]:
            self.bangdiem.add(*row)


def chay_ung_dung() -> None:
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
        logger.exception("Không thể khởi chạy GUI")
        try:
            messagebox.showerror("Lỗi", f"Không thể khởi chạy ứng dụng: {exc}")
        except tk.TclError:
            print(f"Không thể khởi chạy ứng dụng: {exc}")
