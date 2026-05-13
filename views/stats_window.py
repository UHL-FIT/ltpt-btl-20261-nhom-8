from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from views.ui_helpers import center_window


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
        self.year_var = tk.StringVar(value="Tất cả")
        years = ["Tất cả"] + (self.context.bangdiem.list_years() or ["2024-2025", "2025-2026"])
        ctk.CTkComboBox(filter_frame, values=years, variable=self.year_var, width=150, state="readonly", command=lambda _: self.load_data()).pack(side=tk.LEFT, padx=4, pady=8)
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

        chart_frame = ctk.CTkFrame(wrapper)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.figure = Figure(figsize=(9, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def selected_semester(self) -> str | None:
        return None

    def selected_year(self) -> str | None:
        return None if self.year_var.get() == "Tất cả" else self.year_var.get()

    def load_data(self) -> None:
        stats = self.context.bangdiem.statistics(self.selected_semester(), self.selected_year())
        self.labels["Sinh viên"].configure(text=str(stats["tong_sinh_vien"]))
        self.labels["Học phần"].configure(text=str(stats["tong_mon_hoc"]))
        self.labels["Điểm đã nhập"].configure(text=str(stats["tong_diem"]))
        self.labels["GPA trung bình"].configure(text=str(stats["gpa_trung_binh"]))
        self.draw(stats)

    def draw(self, stats: dict) -> None:
        self.figure.clear()
        ax1 = self.figure.add_subplot(121)
        labels = list(stats["xep_loai"].keys())
        values = list(stats["xep_loai"].values())
        if sum(values):
            ax1.pie(values, labels=labels, autopct="%1.0f%%", startangle=90)
        else:
            ax1.text(0.5, 0.5, "Chưa có dữ liệu", ha="center", va="center")
        ax1.set_title("Phân bố xếp loại")

        ax2 = self.figure.add_subplot(122)
        top = stats["top_gpa"]
        if top:
            names = [r["HoTen"] for r in top][::-1]
            gpas = [r["GPA"] for r in top][::-1]
            ax2.barh(names, gpas, color="#0f766e")
            ax2.set_xlim(0, 10)
        else:
            ax2.text(0.5, 0.5, "Chưa có dữ liệu", ha="center", va="center")
        ax2.set_title("Top GPA")
        ax2.set_xlabel("GPA")
        self.figure.tight_layout()
        self.canvas.draw()

    def export_chart(self) -> None:
        path = filedialog.asksaveasfilename(title="Lưu biểu đồ", defaultextension=".png", filetypes=[("PNG", "*.png")], parent=self.window)
        if path:
            self.figure.savefig(path)
            messagebox.showinfo("Thành công", "Đã xuất biểu đồ.", parent=self.window)
