from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from app.utils.csv_helpers import export_csv, read_csv_required
from app.views.detail_window import DetailWindow
from app.views.form_windows import CourseForm, ScoreForm, StudentForm
from app.views.ui_helpers import center_window, make_tree, replace_tree_rows


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
            return ["MaSV", "HoTen", "GioiTinh", "NgaySinh", "Lop"]
        if self.mode == "monhoc":
            return ["MaHocPhan", "TenHocPhan", "SoTinChi", "HocKyMacDinh"]
        return ["MaSV", "HoTen", "Lop", "GPA", "XepLoai"]

    def setup_ui(self) -> None:
        wrapper = ctk.CTkFrame(self.window)
        wrapper.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        ctk.CTkLabel(wrapper, text=self.title.upper(), font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=8, pady=(8, 10))

        toolbar = ctk.CTkFrame(wrapper)
        toolbar.pack(fill=tk.X, padx=8, pady=(0, 8))
        if self.mode != "bangdiem":
            ctk.CTkButton(toolbar, text="➕ Thêm", width=96, command=self.add_item).pack(side=tk.LEFT, padx=4, pady=8)
            ctk.CTkButton(toolbar, text="✏️ Sửa", width=96, command=self.edit_item).pack(side=tk.LEFT, padx=4, pady=8)
            ctk.CTkButton(toolbar, text="🗑️ Xóa", width=96, fg_color="#dc2626", hover_color="#b91c1c", command=self.delete_item).pack(side=tk.LEFT, padx=4, pady=8)
            ctk.CTkButton(toolbar, text="📥 Import CSV", width=120, command=self.import_csv).pack(side=tk.LEFT, padx=4, pady=8)
        else:
            ctk.CTkButton(toolbar, text="🔎 Xem chi tiết", width=120, command=self.open_detail).pack(side=tk.LEFT, padx=4, pady=8)
        
        ctk.CTkButton(toolbar, text="📤 Export CSV", width=120, command=self.export_csv).pack(side=tk.LEFT, padx=4, pady=8)
        ctk.CTkButton(toolbar, text="🔄 Làm mới", width=100, command=self.load_data).pack(side=tk.LEFT, padx=4, pady=8)

        self.search_entry = ctk.CTkEntry(toolbar, placeholder_text="Tìm kiếm...", width=220)
        self.search_entry.pack(side=tk.RIGHT, padx=4, pady=8)
        self.search_entry.bind("<KeyRelease>", lambda _: self.load_data())

        if self.mode == "bangdiem":
            filter_frame = ctk.CTkFrame(wrapper)
            filter_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
            self.class_filter = tk.StringVar(value="Tất cả")
            self.rank_filter = tk.StringVar(value="Tất cả")
            self.gpa_op = tk.StringVar(value=">=")

            class_box = ctk.CTkFrame(filter_frame, fg_color="transparent")
            class_box.pack(side=tk.LEFT, padx=6, pady=8)
            ctk.CTkLabel(class_box, text="Lớp", text_color="#334155", anchor="w").pack(fill=tk.X, pady=(0, 3))
            classes = ["Tất cả"] + sorted(list(set(r["Lop"] for r in self.context.sinhvien.list_all())))
            self.class_combo = ctk.CTkComboBox(class_box, variable=self.class_filter, values=classes, width=140, state="readonly", command=lambda _: self.load_data())
            self.class_combo.pack()

            rank_box = ctk.CTkFrame(filter_frame, fg_color="transparent")
            rank_box.pack(side=tk.LEFT, padx=6, pady=8)
            ctk.CTkLabel(rank_box, text="Xếp loại", text_color="#334155", anchor="w").pack(fill=tk.X, pady=(0, 3))
            self.rank_combo = ctk.CTkComboBox(rank_box, variable=self.rank_filter, values=["Tất cả", "Giỏi", "Khá", "Trung bình", "Yếu"], width=130, state="readonly", command=lambda _: self.load_data())
            self.rank_combo.pack()

            gpa_box = ctk.CTkFrame(filter_frame, fg_color="transparent")
            gpa_box.pack(side=tk.LEFT, padx=6, pady=8)
            ctk.CTkLabel(gpa_box, text="Điểm GPA", text_color="#334155", anchor="w").pack(fill=tk.X, pady=(0, 3))
            gpa_inner = ctk.CTkFrame(gpa_box, fg_color="transparent")
            gpa_inner.pack()
            ctk.CTkComboBox(gpa_inner, variable=self.gpa_op, values=[">=", "<="], width=70, state="readonly", command=lambda _: self.load_data()).pack(side=tk.LEFT)
            self.gpa_entry = ctk.CTkEntry(gpa_inner, width=70, placeholder_text="GPA...")
            self.gpa_entry.pack(side=tk.LEFT, padx=(4, 0))
            self.gpa_entry.bind("<KeyRelease>", lambda _: self.load_data())

            # Nút xóa lọc được căn chỉnh thẳng hàng
            ctk.CTkButton(filter_frame, text="Xóa lọc", width=90, height=28, command=self.clear_filters).pack(side=tk.LEFT, padx=8, pady=(30, 0))

        table_frame = ctk.CTkFrame(wrapper)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        # Chỉ hiện checkbox cho quản lý sinh viên và học phần, không hiện ở bảng điểm tổng quan
        use_checkbox = self.mode in {"sinhvien", "monhoc"}
        self.tree = make_tree(table_frame, self.columns, use_checkbox=use_checkbox)
        self.tree.bind("<Double-1>", lambda _event: self.open_detail() if self.mode == "bangdiem" else self.edit_item())

        self.stats_label = ctk.CTkLabel(wrapper, text="", anchor="w")
        self.stats_label.pack(fill=tk.X, padx=8, pady=(0, 8))

    def load_data(self) -> None:
        keyword = self.search_entry.get()
        if self.mode == "sinhvien":
            rows = self.context.sinhvien.search(keyword) if keyword else self.context.sinhvien.list_all()
        elif self.mode == "monhoc":
            rows = self.context.monhoc.search(keyword) if keyword else self.context.monhoc.list_all()
        else:
            # Lấy toàn bộ sinh viên kèm GPA tích lũy
            rows = self.context.bangdiem.student_overview(keyword=keyword)
            
            # Lọc theo Lớp
            cls = self.class_filter.get()
            if cls != "Tất cả":
                rows = [r for r in rows if r["Lop"] == cls]
            
            # Lọc theo Xếp loại
            rank_val = self.rank_filter.get()
            if rank_val != "Tất cả":
                rows = [r for r in rows if r["XepLoai"] == rank_val]
            
            # Lọc theo GPA
            gpa_v = self.gpa_entry.get().strip() if hasattr(self, "gpa_entry") else ""
            if gpa_v:
                try:
                    val = float(gpa_v)
                    op = self.gpa_op.get()
                    if op == ">=":
                        rows = [r for r in rows if r["GPA"] >= val]
                    else:
                        rows = [r for r in rows if r["GPA"] <= val]
                except ValueError:
                    pass

        replace_tree_rows(self.tree, self.columns, rows)
        self.current_rows = rows
        self.update_stats(rows)

    def update_stats(self, rows: list[dict]) -> None:
        if self.mode == "bangdiem":
            stats = self.context.bangdiem.statistics()
            self.stats_label.configure(text=f"Số sinh viên hiển thị: {len(rows)} | GPA TB Toàn hệ thống: {stats['gpa_trung_binh']} | Tổng đầu điểm: {stats['tong_diem']}")
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
        checked = self.checked_rows()
        if not checked:
            # Nếu không có checkbox nào được chọn, thử lấy dòng đang được select
            row = self.selected_row()
            if row:
                checked = [row]
            else:
                return

        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa {len(checked)} bản ghi đã chọn?", parent=self.window):
            return

        count = 0
        for row in checked:
            if self.mode == "sinhvien":
                if self.context.sinhvien.delete(row["MaSV"]):
                    count += 1
            elif self.mode == "monhoc":
                if self.context.monhoc.delete(row["MaHocPhan"]):
                    count += 1
            else:
                # Với bảng điểm, xóa toàn bộ điểm của sinh viên đó trong kỳ/năm đang lọc?
                # Yêu cầu người dùng mở chi tiết để xóa từng môn hoặc checkbox trong DetailWindow
                messagebox.showwarning("Thông báo", "Vui lòng mở chi tiết để quản lý điểm từng môn của sinh viên.", parent=self.window)
                return

        if count < len(checked):
            messagebox.showwarning("Kết quả", f"Chỉ xóa được {count}/{len(checked)} bản ghi.", parent=self.window)
        else:
            messagebox.showinfo("Thành công", f"Đã xóa {count} bản ghi.", parent=self.window)
        self.load_data()

    def open_detail(self) -> None:
        row = self.selected_row()
        if row:
            DetailWindow(self.window, self.context, row["MaSV"], None, None, self.load_data)

    def clear_filters(self) -> None:
        if self.mode == "bangdiem":
            self.class_filter.set("Tất cả")
            self.rank_filter.set("Tất cả")
            self.gpa_op.set(">=")
            self.gpa_entry.delete(0, tk.END)
        self.search_entry.delete(0, tk.END)
        self.load_data()

    def import_csv(self) -> None:
        path = filedialog.askopenfilename(title="Chọn file CSV", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], parent=self.window)
        if not path:
            return
        try:
            from app.utils.csv_helpers import read_csv_required
            if self.mode == "bangdiem":
                cols = ["MaSV", "HoTen", "Lop", "MaHocPhan", "TenHocPhan", "SoTinChi", "HocKy", "NamHoc", "Diem"]
                df = read_csv_required(path, cols)
                count = self.context.bangdiem.import_rows(df.to_dict("records"))
            else:
                df = read_csv_required(path, self.columns)
                count = self.model.import_rows(df.to_dict("records"))
            
            messagebox.showinfo("Thành công", f"Đã nhập thành công {count} bản ghi.", parent=self.window)
            self.load_data()
        except ValueError as e:
            messagebox.showerror("Lỗi cấu trúc/dữ liệu CSV", str(e), parent=self.window)
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Đã xảy ra lỗi không mong muốn: {str(e)}", parent=self.window)

    def export_csv(self) -> None:
        default_name = {"sinhvien": "sinhvien.csv", "monhoc": "monhoc.csv", "bangdiem": "bangdiem_tonghop.csv"}[self.mode]
        path = filedialog.asksaveasfilename(title="Xuất file CSV", defaultextension=".csv", initialfile=default_name, filetypes=[("CSV files", "*.csv")], parent=self.window)
        if not path:
            return
        try:
            from app.utils.csv_helpers import export_csv
            if self.mode == "sinhvien":
                cols = self.columns
                rows = self.context.sinhvien.list_all()
            elif self.mode == "monhoc":
                cols = self.columns
                rows = self.context.monhoc.list_all()
            else:
                # Xuất toàn bộ chi tiết điểm của tất cả sinh viên
                cols = ["MaSV", "HoTen", "Lop", "MaHocPhan", "TenHocPhan", "SoTinChi", "HocKy", "NamHoc", "Diem"]
                rows = self.context.bangdiem.list_records()
            
            export_csv(path, rows, cols)
            messagebox.showinfo("Thành công", f"Đã xuất file tại: {path}", parent=self.window)
        except Exception as e:
            messagebox.showerror("Lỗi export", str(e), parent=self.window)
