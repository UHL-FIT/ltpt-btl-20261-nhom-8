from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from utils.csv_helpers import export_csv, read_csv_required
from utils.validation import classify_gpa
from views.detail_window import DetailWindow
from views.form_windows import CourseForm, ScoreForm, StudentForm
from views.ui_helpers import center_window, make_tree, replace_tree_rows


class ManageWindow:
    def __init__(self, parent, context, mode: str) -> None:
        self.parent = parent
        self.context = context
        self.mode = mode
        self.window = ctk.CTkToplevel(parent)
        self.window.title(self.title)
        self.window.geometry("1120x680")
        self.window.minsize(940, 560)
        self.window.transient(parent)
        self.columns = self.get_columns()
        self.setup_ui()
        self.load_data()
        center_window(self.window, parent)

    @property
    def title(self) -> str:
        return {"sinhvien": "Quản lý sinh viên", "monhoc": "Quản lý học phần", "bangdiem": "Quản lý bảng điểm"}[self.mode]

    def get_columns(self) -> list[str]:
        if self.mode == "sinhvien":
            return ["MaSV", "HoTen", "GioiTinh", "NgaySinh", "Lop", "GPA", "XepLoai"]
        if self.mode == "monhoc":
            return ["MaHocPhan", "TenHocPhan", "SoTinChi", "HocKyMacDinh"]
        return ["MaSV", "HoTen", "Lop", "GPA", "XepLoai"]

    def setup_ui(self) -> None:
        wrapper = ctk.CTkFrame(self.window)
        wrapper.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        ctk.CTkLabel(wrapper, text=self.title.upper(), font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=8, pady=(8, 10))

        toolbar = ctk.CTkFrame(wrapper)
        toolbar.pack(fill=tk.X, padx=8, pady=(0, 8))
        ctk.CTkButton(toolbar, text="➕ Thêm", width=96, command=self.add_item).pack(side=tk.LEFT, padx=4, pady=8)
        ctk.CTkButton(toolbar, text="✏️ Sửa", width=96, command=self.edit_item).pack(side=tk.LEFT, padx=4, pady=8)
        ctk.CTkButton(toolbar, text="🗑️ Xóa", width=96, fg_color="#dc2626", hover_color="#b91c1c", command=self.delete_item).pack(side=tk.LEFT, padx=4, pady=8)
        if self.mode == "bangdiem":
            ctk.CTkButton(toolbar, text="🔎 Xem chi tiết", width=120, command=self.open_detail).pack(side=tk.LEFT, padx=4, pady=8)
        ctk.CTkButton(toolbar, text="📥 Import CSV", width=120, command=self.import_csv).pack(side=tk.LEFT, padx=4, pady=8)
        ctk.CTkButton(toolbar, text="📤 Export CSV", width=120, command=self.export_csv).pack(side=tk.LEFT, padx=4, pady=8)
        ctk.CTkButton(toolbar, text="🔄 Làm mới", width=100, command=self.load_data).pack(side=tk.LEFT, padx=4, pady=8)

        self.search_var = tk.StringVar()
        ctk.CTkEntry(toolbar, textvariable=self.search_var, placeholder_text="Tìm kiếm...", width=220).pack(side=tk.RIGHT, padx=4, pady=8)
        self.search_var.trace_add("write", lambda *_: self.load_data())

        if self.mode == "bangdiem":
            filter_frame = ctk.CTkFrame(wrapper)
            filter_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
            self.student_filter = tk.StringVar(value="Tất cả")
            self.year_filter = tk.StringVar(value="Tất cả")

            student_filter_box = ctk.CTkFrame(filter_frame, fg_color="transparent")
            student_filter_box.pack(side=tk.LEFT, padx=6, pady=8)
            ctk.CTkLabel(student_filter_box, text="Sinh viên", text_color="#334155", anchor="w").pack(fill=tk.X, pady=(0, 3))
            self.student_combo = ctk.CTkComboBox(student_filter_box, variable=self.student_filter, values=self.student_options(), width=260, state="readonly", command=lambda _: self.load_data())
            self.student_combo.pack()

            year_filter_box = ctk.CTkFrame(filter_frame, fg_color="transparent")
            year_filter_box.pack(side=tk.LEFT, padx=6, pady=8)
            ctk.CTkLabel(year_filter_box, text="Năm học", text_color="#334155", anchor="w").pack(fill=tk.X, pady=(0, 3))
            self.year_combo = ctk.CTkComboBox(year_filter_box, variable=self.year_filter, values=self.year_options(), width=150, state="readonly", command=lambda _: self.load_data())
            self.year_combo.pack()

            ctk.CTkButton(filter_frame, text="Xóa lọc", width=90, command=self.clear_filters).pack(side=tk.LEFT, padx=8, pady=(30, 8))

        table_frame = ctk.CTkFrame(wrapper)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.tree = make_tree(table_frame, self.columns)
        self.tree.bind("<Double-1>", lambda _event: self.open_detail() if self.mode == "bangdiem" else self.edit_item())

        self.stats_label = ctk.CTkLabel(wrapper, text="", anchor="w")
        self.stats_label.pack(fill=tk.X, padx=8, pady=(0, 8))

    def student_options(self) -> list[str]:
        return ["Tất cả"] + [f"{r['MaSV']} - {r['HoTen']}" for r in self.context.sinhvien.list_all()]

    def year_options(self) -> list[str]:
        years = self.context.bangdiem.list_years()
        return ["Tất cả"] + (years if years else ["2024-2025", "2025-2026"])

    def selected_filter_code(self) -> str | None:
        value = getattr(self, "student_filter", tk.StringVar(value="Tất cả")).get()
        return None if value == "Tất cả" else value.split(" - ", 1)[0]

    def selected_semester(self) -> str | None:
        return None

    def selected_year(self) -> str | None:
        value = getattr(self, "year_filter", tk.StringVar(value="Tất cả")).get()
        return None if value == "Tất cả" else value

    def load_data(self) -> None:
        keyword = self.search_var.get() if hasattr(self, "search_var") else ""
        if self.mode == "sinhvien":
            base = self.context.sinhvien.search(keyword) if keyword else self.context.sinhvien.list_all()
            rows = []
            for row in base:
                gpa = self.context.bangdiem.calculate_gpa(row["MaSV"])
                rows.append({**row, "GPA": gpa, "XepLoai": classify_gpa(gpa)})
        elif self.mode == "monhoc":
            rows = self.context.monhoc.search(keyword) if keyword else self.context.monhoc.list_all()
        else:
            rows = self.context.bangdiem.student_overview(self.selected_semester(), self.selected_year(), keyword)
            if self.selected_filter_code():
                rows = [row for row in rows if row["MaSV"] == self.selected_filter_code()]
            self.refresh_filter_values()
        replace_tree_rows(self.tree, self.columns, rows)
        self.current_rows = rows
        self.update_stats(rows)

    def refresh_filter_values(self) -> None:
        if not hasattr(self, "student_combo"):
            return
        self.student_combo.configure(values=self.student_options())
        self.year_combo.configure(values=self.year_options())

    def update_stats(self, rows: list[dict]) -> None:
        if self.mode == "bangdiem":
            stats = self.context.bangdiem.statistics(self.selected_semester(), self.selected_year())
            self.stats_label.configure(text=f"Số sinh viên hiển thị: {len(rows)} | GPA TB: {stats['gpa_trung_binh']} | Điểm đã nhập: {stats['tong_diem']}")
        else:
            self.stats_label.configure(text=f"Tổng bản ghi hiển thị: {len(rows)}")

    def selected_row(self) -> dict | None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng.", parent=self.window)
            return None
        if len(selected) > 1:
            messagebox.showwarning("Cảnh báo", "Chỉ được chọn một dòng cho thao tác này.", parent=self.window)
            return None
        values = self.tree.item(selected[0], "values")
        return dict(zip(self.columns, values))

    def add_item(self) -> None:
        if self.mode == "sinhvien":
            StudentForm(self.window, self.context.sinhvien, "add", None, self.load_data)
        elif self.mode == "monhoc":
            CourseForm(self.window, self.context.monhoc, "add", None, self.load_data)
        else:
            ScoreForm(self.window, self.context, "add", None, self.load_data, self.selected_filter_code() or "", self.selected_semester() or "", self.selected_year() or "")

    def edit_item(self) -> None:
        row = self.selected_row()
        if not row:
            return
        if self.mode == "sinhvien":
            data = self.context.sinhvien.get(row["MaSV"])
            StudentForm(self.window, self.context.sinhvien, "edit", data, self.load_data)
        elif self.mode == "monhoc":
            data = self.context.monhoc.get(row["MaHocPhan"])
            CourseForm(self.window, self.context.monhoc, "edit", data, self.load_data)
        else:
            self.open_detail()

    def delete_item(self) -> None:
        row = self.selected_row()
        if not row or not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa dữ liệu đã chọn?", parent=self.window):
            return
        if self.mode == "sinhvien":
            ok = self.context.sinhvien.delete(row["MaSV"])
        elif self.mode == "monhoc":
            ok = self.context.monhoc.delete(row["MaHocPhan"])
        else:
            DetailWindow(self.window, self.context, row["MaSV"], self.selected_semester(), self.selected_year(), self.load_data)
            return
        if not ok:
            messagebox.showerror("Lỗi", "Không thể xóa bản ghi.", parent=self.window)
        self.load_data()

    def open_detail(self) -> None:
        row = self.selected_row()
        if row:
            DetailWindow(self.window, self.context, row["MaSV"], self.selected_semester(), self.selected_year(), self.load_data)

    def clear_filters(self) -> None:
        self.student_filter.set("Tất cả")
        self.year_filter.set("Tất cả")
        self.load_data()

    def import_csv(self) -> None:
        path = filedialog.askopenfilename(title="Chọn file CSV", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], parent=self.window)
        if not path:
            return
        try:
            if self.mode == "sinhvien":
                df = read_csv_required(path, ["MaSV", "HoTen", "GioiTinh", "NgaySinh", "Lop"])
                ok, failed = self.context.sinhvien.import_rows(df.to_dict("records"))
            elif self.mode == "monhoc":
                df = read_csv_required(path, ["MaHocPhan", "TenHocPhan", "SoTinChi"])
                ok, failed = self.context.monhoc.import_rows(df.to_dict("records"))
            else:
                df = read_csv_required(path, ["MaSV", "MaHocPhan", "HocKy", "NamHoc", "Diem"])
                ok, failed = self.context.bangdiem.import_rows(df.to_dict("records"))
            messagebox.showinfo("Import CSV", f"Đã import {ok} dòng. Bỏ qua/lỗi {failed} dòng.", parent=self.window)
            self.load_data()
        except Exception as exc:
            messagebox.showerror("Lỗi import", str(exc), parent=self.window)

    def export_csv(self) -> None:
        default_name = {"sinhvien": "sinhvien.csv", "monhoc": "monhoc.csv", "bangdiem": "bangdiem_tongquan.csv"}[self.mode]
        path = filedialog.asksaveasfilename(title="Lưu CSV", defaultextension=".csv", initialfile=default_name, filetypes=[("CSV files", "*.csv")], parent=self.window)
        if not path:
            return
        try:
            rows = self.context.bangdiem.list_records(self.selected_filter_code(), self.selected_semester(), self.selected_year()) if self.mode == "bangdiem" else self.current_rows
            columns = list(rows[0].keys()) if rows else self.columns
            export_csv(path, rows, columns)
            messagebox.showinfo("Export CSV", f"Đã lưu file:\n{os.path.basename(path)}", parent=self.window)
        except Exception as exc:
            messagebox.showerror("Lỗi export", str(exc), parent=self.window)
