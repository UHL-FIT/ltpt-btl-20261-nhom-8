from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from views.ui_helpers import center_window


class BaseForm:
    def __init__(self, parent, title: str, on_saved) -> None:
        self.parent = parent
        self.on_saved = on_saved
        self.window = ctk.CTkToplevel(parent)
        self.window.title(title)
        self.window.geometry("460x420")
        self.window.transient(parent)
        self.window.grab_set()
        self.fields: dict[str, tk.StringVar] = {}

    def add_entry(self, frame, row: int, label: str, name: str, value: str = "") -> None:
        ctk.CTkLabel(frame, text=label).grid(row=row, column=0, sticky="w", padx=12, pady=8)
        var = tk.StringVar(value=value)
        ctk.CTkEntry(frame, textvariable=var).grid(row=row, column=1, sticky="ew", padx=12, pady=8)
        self.fields[name] = var

    def add_combo(self, frame, row: int, label: str, name: str, values: list[str], value: str = "") -> None:
        ctk.CTkLabel(frame, text=label).grid(row=row, column=0, sticky="w", padx=12, pady=8)
        var = tk.StringVar(value=value or (values[0] if values else ""))
        ctk.CTkComboBox(frame, values=values, variable=var, state="readonly").grid(row=row, column=1, sticky="ew", padx=12, pady=8)
        self.fields[name] = var

    def add_readonly_entry(self, frame, row: int, label: str, name: str, value: str = "") -> None:
        ctk.CTkLabel(frame, text=label).grid(row=row, column=0, sticky="w", padx=12, pady=8)
        var = tk.StringVar(value=value)
        entry = ctk.CTkEntry(frame, textvariable=var, state="disabled")
        entry.grid(row=row, column=1, sticky="ew", padx=12, pady=8)
        self.fields[name] = var

    def values(self) -> dict:
        return {key: var.get().strip() for key, var in self.fields.items()}

    def buttons(self, frame, save_command) -> None:
        row = len(self.fields) + 1
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(20, 8))
        ctk.CTkButton(button_frame, text="Lưu", command=save_command).pack(side=tk.LEFT)
        ctk.CTkButton(button_frame, text="Hủy", fg_color="#64748b", command=self.window.destroy).pack(side=tk.RIGHT)
        center_window(self.window, self.parent)


class StudentForm(BaseForm):
    def __init__(self, parent, model, mode: str, data: dict | None, on_saved) -> None:
        super().__init__(parent, "Thêm sinh viên" if mode == "add" else "Sửa sinh viên", on_saved)
        self.model = model
        self.mode = mode
        data = data or {}
        frame = ctk.CTkFrame(self.window)
        frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)
        frame.grid_columnconfigure(1, weight=1)
        self.add_entry(frame, 0, "Mã SV", "MaSV", data.get("MaSV", ""))
        self.add_entry(frame, 1, "Họ tên", "HoTen", data.get("HoTen", ""))
        self.add_combo(frame, 2, "Giới tính", "GioiTinh", ["Nam", "Nữ", "Khác"], data.get("GioiTinh", "Nam"))
        self.add_entry(frame, 3, "Ngày sinh", "NgaySinh", data.get("NgaySinh", ""))
        self.add_entry(frame, 4, "Lớp", "Lop", data.get("Lop", ""))
        if mode == "edit":
            self.fields["MaSV"].set(data["MaSV"])
        self.buttons(frame, self.save)

    def save(self) -> None:
        try:
            v = self.values()
            ok = self.model.add(**self._kwargs(v)) if self.mode == "add" else self.model.update(**self._kwargs(v))
            if not ok:
                messagebox.showerror("Lỗi", "Mã sinh viên đã tồn tại hoặc không tìm thấy bản ghi.", parent=self.window)
                return
            self.on_saved()
            self.window.destroy()
        except ValueError as exc:
            messagebox.showerror("Dữ liệu không hợp lệ", str(exc), parent=self.window)

    @staticmethod
    def _kwargs(v: dict) -> dict:
        return {"ma_sv": v["MaSV"], "ho_ten": v["HoTen"], "gioi_tinh": v["GioiTinh"], "ngay_sinh": v["NgaySinh"], "lop": v["Lop"]}


class CourseForm(BaseForm):
    def __init__(self, parent, model, mode: str, data: dict | None, on_saved) -> None:
        super().__init__(parent, "Thêm học phần" if mode == "add" else "Sửa học phần", on_saved)
        self.model = model
        self.mode = mode
        data = data or {}
        frame = ctk.CTkFrame(self.window)
        frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)
        frame.grid_columnconfigure(1, weight=1)
        self.add_entry(frame, 0, "Mã học phần", "MaHocPhan", data.get("MaHocPhan", ""))
        self.add_entry(frame, 1, "Tên học phần", "TenHocPhan", data.get("TenHocPhan", ""))
        self.add_entry(frame, 2, "Số tín chỉ", "SoTinChi", data.get("SoTinChi", ""))
        self.add_combo(frame, 3, "Học kỳ mặc định", "HocKyMacDinh", ["HK1", "HK2"], data.get("HocKyMacDinh", "HK1"))
        self.buttons(frame, self.save)

    def save(self) -> None:
        try:
            v = self.values()
            ok = self.model.add(v["MaHocPhan"], v["TenHocPhan"], v["SoTinChi"], v["HocKyMacDinh"]) if self.mode == "add" else self.model.update(v["MaHocPhan"], v["TenHocPhan"], v["SoTinChi"], v["HocKyMacDinh"])
            if not ok:
                messagebox.showerror("Lỗi", "Mã học phần đã tồn tại hoặc không tìm thấy bản ghi.", parent=self.window)
                return
            self.on_saved()
            self.window.destroy()
        except ValueError as exc:
            messagebox.showerror("Dữ liệu không hợp lệ", str(exc), parent=self.window)


class ScoreForm(BaseForm):
    def __init__(
        self,
        parent,
        context,
        mode: str,
        data: dict | None,
        on_saved,
        default_student: str = "",
        default_semester: str = "",
        default_year: str = "",
        fixed_student: str | None = None,
    ) -> None:
        super().__init__(parent, "Nhập điểm" if mode == "add" else "Sửa điểm", on_saved)
        self.context = context
        self.mode = mode
        self.data = data or {}
        self.fixed_student = fixed_student
        self.old_key = (
            self.data.get("MaSV", ""),
            self.data.get("MaHocPhan", ""),
            self.data.get("HocKy", ""),
            self.data.get("NamHoc", ""),
        )
        students = [f"{r['MaSV']} - {r['HoTen']}" for r in context.sinhvien.list_all()]
        courses = [f"{r['MaHocPhan']} - {r['TenHocPhan']}" for r in context.monhoc.list_all()]
        frame = ctk.CTkFrame(self.window)
        frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)
        frame.grid_columnconfigure(1, weight=1)
        row = 0
        if not self.fixed_student:
            self.add_combo(frame, row, "Sinh viên", "MaSV", students, self._pick_label(students, self.data.get("MaSV") or default_student))
            row += 1
        self.add_combo(frame, row, "Học phần", "MaHocPhan", courses, self._pick_label(courses, self.data.get("MaHocPhan")))
        row += 1
        self.add_readonly_entry(frame, row, "Tín chỉ", "SoTinChi", "")
        row += 1
        self.add_combo(frame, row, "Học kỳ", "HocKy", ["HK1", "HK2"], self.data.get("HocKy") or default_semester or "HK1")
        row += 1
        self.add_entry(frame, row, "Năm học", "NamHoc", self.data.get("NamHoc") or default_year or "2024-2025")
        row += 1
        self.add_entry(frame, row, "Điểm", "Diem", self.data.get("Diem", ""))
        self.fields["MaHocPhan"].trace_add("write", lambda *_: self.update_course_info())
        self.update_course_info()
        self.buttons(frame, self.save)

    @staticmethod
    def _pick_label(options: list[str], code: str | None) -> str:
        if not code:
            return options[0] if options else ""
        for option in options:
            if option.startswith(code):
                return option
        return options[0] if options else ""

    @staticmethod
    def _code(value: str) -> str:
        return value.split(" - ", 1)[0].strip()

    def update_course_info(self) -> None:
        course = self.context.monhoc.get(self._code(self.fields["MaHocPhan"].get()))
        if course:
            self.fields["SoTinChi"].set(str(course["SoTinChi"]))

    def save(self) -> None:
        try:
            v = self.values()
            ma_sv = self.fixed_student or self._code(v["MaSV"])
            args = (ma_sv, self._code(v["MaHocPhan"]), v["HocKy"], v["NamHoc"], v["Diem"])
            ok = self.context.bangdiem.add(*args) if self.mode == "add" else self.context.bangdiem.update(self.old_key, *args)
            if not ok:
                messagebox.showerror("Lỗi", "Bản ghi điểm bị trùng hoặc không tìm thấy dữ liệu liên quan.", parent=self.window)
                return
            self.on_saved()
            self.window.destroy()
        except ValueError as exc:
            messagebox.showerror("Dữ liệu không hợp lệ", str(exc), parent=self.window)
