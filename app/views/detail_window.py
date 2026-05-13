from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from app.utils.csv_helpers import export_csv, read_csv_required
from app.utils.validation import classify_gpa
from app.views.form_windows import ScoreForm
from app.views.ui_helpers import center_window, make_tree, replace_tree_rows


class DetailWindow:
    columns = ["MaHocPhan", "TenHocPhan", "SoTinChi", "HocKy", "NamHoc", "Diem"]

    def __init__(self, parent, context, ma_sv: str, hoc_ky: str | None, nam_hoc: str | None, on_changed=None) -> None:
        self.parent = parent
        self.context = context
        self.ma_sv = ma_sv
        self.hoc_ky = hoc_ky
        self.nam_hoc = nam_hoc
        self.on_changed = on_changed or (lambda: None)
        self.window = ctk.CTkToplevel(parent)
        self.window.title(f"Chi tiết bảng điểm - {ma_sv}")
        self.window.geometry("900x560")
        self.window.transient(parent)
        self.setup_ui()
        self.load_data()
        center_window(self.window, parent)

    def setup_ui(self) -> None:
        wrapper = ctk.CTkFrame(self.window)
        wrapper.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.info_frame = ctk.CTkFrame(wrapper, fg_color="#eef6ff", corner_radius=8)
        self.info_frame.pack(fill=tk.X, padx=8, pady=(8, 12))
        self.info_frame.grid_columnconfigure(1, weight=1)
        self.info_labels: dict[str, ctk.CTkLabel] = {}
        info_rows = [
            ("MaSV", "Mã sinh viên:"),
            ("HoTen", "Tên sinh viên:"),
            ("Lop", "Lớp:"),
            ("GPA", "GPA (Tích lũy):"),
            ("XepLoai", "Xếp loại:"),
        ]
        for row, (key, title) in enumerate(info_rows):
            ctk.CTkLabel(
                self.info_frame,
                text=title,
                text_color="#0f766e",
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
            ).grid(row=row, column=0, sticky="w", padx=(18, 28))
            value_label = ctk.CTkLabel(
                self.info_frame,
                text="",
                text_color="#0f172a",
                font=ctk.CTkFont(size=13),
                anchor="w",
            )
            value_label.grid(row=row, column=1, sticky="ew", padx=(0, 18))
            self.info_labels[key] = value_label

        toolbar = ctk.CTkFrame(wrapper)
        toolbar.pack(fill=tk.X, padx=8, pady=(0, 8))
        ctk.CTkButton(toolbar, text="➕ Thêm môn", command=self.add_score).pack(side=tk.LEFT, padx=4, pady=8)
        ctk.CTkButton(toolbar, text="✏️ Sửa điểm", command=self.edit_score).pack(side=tk.LEFT, padx=4, pady=8)
        ctk.CTkButton(toolbar, text="🗑️ Xóa môn", fg_color="#dc2626", hover_color="#b91c1c", command=self.delete_score).pack(side=tk.LEFT, padx=4, pady=8)

        table_frame = ctk.CTkFrame(wrapper)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.tree = make_tree(table_frame, self.columns, use_checkbox=True)
        self.tree.bind("<Double-1>", lambda _event: self.edit_score())

    def load_data(self) -> None:
        student = self.context.sinhvien.get(self.ma_sv) or {}
        rows = self.context.bangdiem.list_records(self.ma_sv, self.hoc_ky, self.nam_hoc)
        gpa = self.context.bangdiem.calculate_gpa(self.ma_sv)
        
        self.info_labels["MaSV"].configure(text=self.ma_sv)
        self.info_labels["HoTen"].configure(text=student.get("HoTen", ""))
        self.info_labels["Lop"].configure(text=student.get("Lop", ""))
        self.info_labels["GPA"].configure(text=str(gpa))
        self.info_labels["XepLoai"].configure(text=classify_gpa(gpa))
        replace_tree_rows(self.tree, self.columns, rows)
        self.current_rows = rows
        self.on_changed()

    def selected_row(self) -> dict | None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một môn.", parent=self.window)
            return None
        # Lấy giá trị thực tế của các cột (bỏ qua cột "Chọn" nếu có)
        offset = 1 if "Chọn" in self.tree["columns"] else 0
        values = self.tree.item(selected[0], "values")[offset:]
        return dict(zip(self.columns, values))

    def checked_rows(self) -> list[dict]:
        checked = []
        if "Chọn" not in self.tree["columns"]:
            return []
        for item in self.tree.get_children():
            if self.tree.set(item, "Chọn") == "☑":
                values = self.tree.item(item, "values")[1:]
                checked.append(dict(zip(self.columns, values)))
        return checked

    def add_score(self) -> None:
        ScoreForm(
            self.window,
            self.context,
            "add",
            None,
            self.load_data,
            self.ma_sv,
            self.hoc_ky or "",
            self.nam_hoc or "",
            fixed_student=self.ma_sv,
        )

    def edit_score(self) -> None:
        row = self.selected_row()
        if row:
            old_key = (self.ma_sv, row["MaHocPhan"])
            ScoreForm(self.window, self.context, "edit", row, self.load_data, fixed_student=self.ma_sv, old_key=old_key)

    def delete_score(self) -> None:
        checked = self.checked_rows()
        if not checked:
            row = self.selected_row()
            if row:
                checked = [row]
            else:
                return

        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa {len(checked)} bản ghi đã chọn?", parent=self.window):
            return

        count = 0
        for row in checked:
            if self.context.bangdiem.delete(self.ma_sv, row["MaHocPhan"]):
                count += 1

        if count < len(checked):
            messagebox.showwarning("Kết quả", f"Chỉ xóa được {count}/{len(checked)} bản ghi.", parent=self.window)
        else:
            messagebox.showinfo("Thành công", f"Đã xóa {count} bản ghi điểm.", parent=self.window)
        self.load_data()
