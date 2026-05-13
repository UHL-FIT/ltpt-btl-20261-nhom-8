from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from app.views.about_window import AboutWindow
from app.views.manage_window import ManageWindow
from app.views.stats_window import StatsWindow


class Dashboard:
    def __init__(self, root: ctk.CTk, context) -> None:
        self.root = root
        self.context = context
        self.setup_ui()

    def setup_ui(self) -> None:
        wrapper = ctk.CTkFrame(self.root, corner_radius=0)
        wrapper.pack(fill=tk.BOTH, expand=True)
        header = ctk.CTkFrame(wrapper, fg_color="#283cd3", corner_radius=0)
        header.pack(fill=tk.X)
        ctk.CTkLabel(
            header,
            text="ỨNG DỤNG QUẢN LÝ KẾT QUẢ HỌC TẬP",
            text_color="white",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(anchor="w", padx=28, pady=(24, 6))
        ctk.CTkLabel(header, text="Nhóm 8 - Desktop app MVC, SQLite, GPA tự động", text_color="#d1fae5").pack(
            anchor="w", padx=28, pady=(0, 24)
        )

        body = ctk.CTkFrame(wrapper, fg_color="#f8fafc", corner_radius=0)
        body.pack(fill=tk.BOTH, expand=True)
        body.grid_columnconfigure((0, 1, 2), weight=1)

        tiles = [
            ("📊", "Quản lý bảng điểm", "Nhập điểm, lọc học kỳ, xem chi tiết GPA", lambda: ManageWindow(self.root, self.context, "bangdiem")),
            ("🧑‍🎓", "Quản lý sinh viên", "Thêm, sửa, xóa, import/export danh sách", lambda: ManageWindow(self.root, self.context, "sinhvien")),
            ("📚", "Quản lý học phần", "Quản lý môn học và số tín chỉ", lambda: ManageWindow(self.root, self.context, "monhoc")),
            ("📈", "Thống kê & biểu đồ", "GPA trung bình, xếp loại, top sinh viên", lambda: StatsWindow(self.root, self.context)),
            ("ℹ️", "About", "Phiên bản, tác giả, hướng dẫn sử dụng", lambda: AboutWindow(self.root)),
        ]
        for i, (icon, title, desc, command) in enumerate(tiles):
            card = ctk.CTkFrame(body, border_width=1, border_color="#dbe4ef", fg_color="white", corner_radius=8)
            card.grid(row=i // 3, column=i % 3, sticky="nsew", padx=18, pady=18)
            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=34)).pack(anchor="w", padx=18, pady=(18, 2))
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=18)
            ctk.CTkLabel(card, text=desc, wraplength=260, justify="left", text_color="#475569").pack(anchor="w", padx=18, pady=(6, 18))
            ctk.CTkButton(card, text="Mở", command=command, width=120).pack(anchor="w", padx=18, pady=(0, 18))

        stats = self.context.bangdiem.statistics()
        footer = ctk.CTkFrame(wrapper, fg_color="#e2e8f0", corner_radius=0)
        footer.pack(fill=tk.X)
        text = (
            f"Sinh viên: {stats['tong_sinh_vien']}    "
            f"Học phần: {stats['tong_mon_hoc']}    "
            f"Điểm đã nhập: {stats['tong_diem']}    "
            f"GPA TB: {stats['gpa_trung_binh']}"
        )
        ctk.CTkLabel(footer, text=text, text_color="#0f172a").pack(anchor="w", padx=28, pady=10)
