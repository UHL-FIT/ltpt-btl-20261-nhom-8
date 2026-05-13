from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from app.views.ui_helpers import center_window
from app.views.ui_helpers import make_tree, replace_tree_rows


class StatsWindow:
    def __init__(self, parent, context) -> None:
        self.parent = parent
        self.context = context
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Thống kê & biểu đồ")
        self.window.geometry("1040x680")
        self.window.transient(parent)
        self.setup_ui()
        self.load_data()
        center_window(self.window, parent)

    def setup_ui(self) -> None:
        wrapper = ctk.CTkFrame(self.window)
        wrapper.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        ctk.CTkLabel(wrapper, text="THỐNG KÊ & BIỂU ĐỒ", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=8, pady=(8, 10))

        filter_frame = ctk.CTkFrame(wrapper)
        filter_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
        ctk.CTkLabel(filter_frame, text="Thống kê dựa trên dữ liệu tích lũy toàn bộ", text_color="#64748b").pack(side=tk.LEFT, padx=12, pady=8)
        ctk.CTkButton(filter_frame, text="Xuất biểu đồ", width=120, command=self.export_chart).pack(side=tk.RIGHT, padx=4, pady=8)

        self.cards = ctk.CTkFrame(wrapper)
        self.cards.pack(fill=tk.X, padx=8, pady=(0, 8))
        self.labels = {}
        for title in ["Sinh viên", "Học phần", "Điểm đã nhập", "GPA trung bình"]:
            card = ctk.CTkFrame(self.cards, border_width=1, border_color="#dbe4ef", fg_color="white", corner_radius=8)
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=4)
            ctk.CTkLabel(card, text=title, text_color="#64748b").pack(anchor="w", padx=14, pady=(10, 0))
            label = ctk.CTkLabel(card, text="--", font=ctk.CTkFont(size=22, weight="bold"))
            label.pack(anchor="w", padx=14, pady=(0, 10))
            self.labels[title] = label

        content_frame = ctk.CTkFrame(wrapper, fg_color="transparent")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        chart_frame = ctk.CTkFrame(content_frame)
        chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(chart_frame, text="Phân bố xếp loại", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=12, pady=(10, 0))
        self.figure = Figure(figsize=(4.8, 4.6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        top_frame = ctk.CTkFrame(content_frame)
        top_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        ctk.CTkLabel(top_frame, text="Top 10 sinh viên xuất sắc nhất", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=12, pady=(10, 8))
        self.top_columns = ["Hang", "MaSV", "HoTen", "Lop", "GPA", "XepLoai"]
        self.top_tree = make_tree(top_frame, self.top_columns)

    def load_data(self) -> None:
        stats = self.context.bangdiem.statistics()
        self.labels["Sinh viên"].configure(text=str(stats["tong_sinh_vien"]))
        self.labels["Học phần"].configure(text=str(stats["tong_mon_hoc"]))
        self.labels["Điểm đã nhập"].configure(text=str(stats["tong_diem"]))
        self.labels["GPA trung bình"].configure(text=str(stats["gpa_trung_binh"]))
        self.draw(stats)
        self.load_top_table(stats["top_gpa"])

    def draw(self, stats: dict) -> None:
        self.figure.clear()
        ax1 = self.figure.add_subplot(111)
        labels = list(stats["xep_loai"].keys())
        values = list(stats["xep_loai"].values())
        if sum(values):
            ax1.pie(values, labels=labels, autopct="%1.0f%%", startangle=90)
        else:
            ax1.text(0.5, 0.5, "Chưa có dữ liệu", ha="center", va="center")
        ax1.set_title("Phân bố xếp loại")
        self.figure.tight_layout()
        self.canvas.draw()

    def load_top_table(self, top_rows: list[dict]) -> None:
        rows = []
        for index, row in enumerate(top_rows[:10], start=1):
            rows.append(
                {
                    "Hang": index,
                    "MaSV": row.get("MaSV", ""),
                    "HoTen": row.get("HoTen", ""),
                    "Lop": row.get("Lop", ""),
                    "GPA": row.get("GPA", ""),
                    "XepLoai": row.get("XepLoai", ""),
                }
            )
        replace_tree_rows(self.top_tree, self.top_columns, rows)

    def export_chart(self) -> None:
        path = filedialog.asksaveasfilename(title="Lưu biểu đồ", defaultextension=".png", filetypes=[("PNG", "*.png")], parent=self.window)
        if path:
            self.figure.savefig(path)
            messagebox.showinfo("Thành công", "Đã xuất biểu đồ.", parent=self.window)
