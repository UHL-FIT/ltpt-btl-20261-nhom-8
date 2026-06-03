from __future__ import annotations

from tkinter import messagebox, ttk

import customtkinter as ctk

from app.utils.logger import get_logger

# Import ScoreEntryWindow từ app/views/windows/score_entry_window.py.
# ScoreDetailWindow mở form này khi người dùng thêm hoặc sửa điểm chi tiết.
from app.views.windows.score_entry_window import ScoreEntryWindow


logger = get_logger(__name__)


class ScoreDetailWindow(ctk.CTkToplevel):
    """Cửa sổ hiển thị chi tiết bảng điểm của một sinh viên."""

    def __init__(self, parent, database, student_info, on_change=None):
        """Khởi tạo cửa sổ chi tiết bảng điểm."""
        super().__init__(parent)
        self.database = database
        self.student_info = student_info
        self.on_change = on_change
        self.sort_state = {}
        logger.info("Mở ScoreDetailWindow cho sinh viên: %s", student_info.get("student_id", ""))

        self.title("Xem chi tiết bảng điểm")
        self.geometry("1120x760")
        self.minsize(850, 600)
        self.configure(fg_color="#F8FAFC")
        self.transient(parent)
        self.lift()
        self.focus_force()
        self.grab_set()

        self._center_window()
        self._create_widgets()
        self.refresh_data()

    def _center_window(self):
        """Canh cửa sổ vào giữa màn hình."""
        self.update_idletasks()
        width = 850
        height = 600
        x = self.winfo_screenwidth() // 2 - width // 2
        y = self.winfo_screenheight() // 2 - height // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self):
        """Tạo toàn bộ giao diện của cửa sổ chi tiết."""
        padding_content = 25

        # Khung ngoài cùng.
        content = ctk.CTkFrame(
            self,
            fg_color="#F8FAFC",
            corner_radius=6,
            border_width=2,
            border_color="#2F74FF",
        )
        content.pack(fill="both", expand=True)
        content.grid_rowconfigure(2, weight=1)
        content.grid_columnconfigure(0, weight=1)

        # Khung thông tin sinh viên.
        self.student_frame = ctk.CTkFrame(
            content,
            fg_color="white",
            corner_radius=14,
            border_width=2,
            border_color="#2F74FF",
            height=118,
        )
        self.student_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=padding_content,
            pady=(padding_content, 14),
        )
        self.student_frame.grid_propagate(False)
        for column in range(5):
            self.student_frame.grid_columnconfigure(column, weight=1)

        self._create_student_info_block(self.student_frame, 0, "Mã sinh viên")
        self._create_student_info_block(self.student_frame, 1, "Tên sinh viên")
        self._create_student_info_block(self.student_frame, 2, "Lớp")
        self._create_student_info_block(self.student_frame, 3, "CPA tích lũy")
        self._create_student_info_block(self.student_frame, 4, "Xếp loại")

        # Thanh nút chức năng.
        toolbar = ctk.CTkFrame(content, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=padding_content, pady=(0, 12))

        add_button = ctk.CTkButton(
            toolbar,
            text="Thêm điểm",
            height=34,
            width=110,
            fg_color="#2F74FF",
            hover_color="#0050DB",
            corner_radius=10,
            command=self.add_score,
        )
        add_button.pack(side="left", padx=(0, 8))

        edit_button = ctk.CTkButton(
            toolbar,
            text="Sửa điểm",
            height=34,
            width=100,
            fg_color="transparent",
            text_color="#2F74FF",
            border_width=2,
            border_color="#2F74FF",
            hover_color="#EAF2FF",
            corner_radius=10,
            command=self.edit_score,
        )
        edit_button.pack(side="left", padx=8)

        delete_button = ctk.CTkButton(
            toolbar,
            text="Xóa điểm",
            height=34,
            width=100,
            fg_color="transparent",
            text_color="#2F74FF",
            border_width=2,
            border_color="#2F74FF",
            hover_color="#EAF2FF",
            corner_radius=10,
            command=self.delete_score,
        )
        delete_button.pack(side="left", padx=8)

        # Bảng điểm chi tiết.
        table_frame = ctk.CTkFrame(
            content,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#D7E3FF",
        )
        table_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=padding_content,
            pady=(0, padding_content),
        )
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = (
            "select",
            "stt",
            "course_id",
            "course_name",
            "credits",
            "semester",
            "school_year",
            "score",
        )

        self.setup_treeview_style()
        self.score_tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Custom.Treeview")

        self._setup_treeview_columns()

        y_scrollbar = ctk.CTkScrollbar(
            table_frame,
            orientation="vertical",
            command=self.score_tree.yview,
            width=12,
            fg_color="#E5EDFF",
            button_color="#2F74FF",
            button_hover_color="#0050DB",
        )
        self.score_tree.configure(yscrollcommand=y_scrollbar.set)

        self.score_tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")

        self.score_tree.bind("<Button-1>", self.toggle_checkbox)
        self.score_tree.bind("<Double-1>", self._on_double_click)

    def _setup_treeview_columns(self):
        """Thiết lập tiêu đề và độ rộng các cột của bảng."""
        self.score_tree.heading("select", text="☐", anchor="center", command=self.toggle_all_checkboxes)
        self.score_tree.heading("stt", text="STT", anchor="center")
        self.score_tree.heading("course_id", text="Mã học phần")
        self.score_tree.heading("course_name", text="Tên học phần")
        self.score_tree.heading("credits", text="Tín chỉ")
        self.score_tree.heading("semester", text="Học kỳ")
        self.score_tree.heading("school_year", text="Năm học")
        self.score_tree.heading("score", text="Điểm số")

        self.score_tree.column("select", width=64, minwidth=64, anchor="center", stretch=False)
        self.score_tree.column("stt", width=64, minwidth=64, anchor="center", stretch=False)
        self.score_tree.column("course_id", width=120, minwidth=90, anchor="center")
        self.score_tree.column("course_name", width=240, minwidth=170, anchor="w")
        self.score_tree.column("credits", width=90, minwidth=70, anchor="center")
        self.score_tree.column("semester", width=90, minwidth=70, anchor="center")
        self.score_tree.column("school_year", width=120, minwidth=90, anchor="center")
        self.score_tree.column("score", width=100, minwidth=80, anchor="center")

    def _create_student_info_block(self, parent, column, label_text):
        """Tạo một ô thông tin ở khung phía trên."""
        block = ctk.CTkFrame(parent, fg_color="transparent", height=70)
        block.grid(row=0, column=column, padx=15, pady=24, sticky="nsew")
        block.grid_propagate(False)
        block.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(block, text=label_text, font=("Arial", 12, "bold"), text_color="#64748B")
        label.pack(anchor="center", pady=(0, 6))

        value = ctk.CTkLabel(block, text="-", font=("Arial", 15, "bold"), text_color="#111827")
        value.pack(anchor="center")

        if not hasattr(self, "info_labels"):
            self.info_labels = {}
        self.info_labels[label_text] = value

    def setup_treeview_style(self):
        """Cấu hình giao diện cho Treeview."""
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Custom.Treeview",
            background="white",
            foreground="#111827",
            rowheight=42,
            fieldbackground="white",
            borderwidth=1,
            relief="solid",
            font=("Arial", 11),
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#2F74FF",
            foreground="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padding=(8, 12),
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", "#DBEAFE")],
            foreground=[("selected", "#111827")],
        )
        style.map("Custom.Treeview.Heading", background=[("active", "#0050DB")])

    def refresh_data(self):
        """Lấy dữ liệu mới nhất và đổ lại vào bảng."""
        for item in self.score_tree.get_children():
            self.score_tree.delete(item)

        details = self.database.fetch_score_details(self.student_info["student_id"])
        logger.info(
            "Làm mới ScoreDetailWindow cho %s: %s bản ghi điểm.",
            self.student_info["student_id"],
            len(details),
        )
        self._update_student_info()

        for index, detail in enumerate(details, start=1):
            row = ("☐", str(index), *detail[1:])
            self.score_tree.insert("", "end", iid=str(detail[0]), values=row)

        self.reindex_stt()
        self.sync_header_checkbox()

    def _update_student_info(self):
        """Cập nhật khối thông tin sinh viên phía trên."""
        student = self.database.fetch_student(self.student_info["student_id"])
        if student:
            _, student_name, class_name, _, _, _ = student
        else:
            student_name = self.student_info.get("student_name", "-")
            class_name = self.student_info.get("class_name", "-")

        summary_row = next(
            (row for row in self.database.fetch_scores() if row[0] == self.student_info["student_id"]),
            None,
        )
        if summary_row:
            cpa_value = summary_row[3]
            grade = summary_row[4]
        else:
            cpa_value = 0.0
            grade = "Chưa có điểm"

        self.info_labels["Mã sinh viên"].configure(text=self.student_info["student_id"])
        self.info_labels["Tên sinh viên"].configure(text=student_name)
        self.info_labels["Lớp"].configure(text=class_name)
        if grade == "Chưa có điểm":
            self.info_labels["CPA tích lũy"].configure(text="Chưa có điểm")
        else:
            self.info_labels["CPA tích lũy"].configure(text=f"{float(cpa_value):.2f}")
        self.info_labels["Xếp loại"].configure(text=grade)

    def toggle_checkbox(self, event):
        """Đổi trạng thái checkbox của một dòng khi bấm vào cột đầu tiên."""
        row_id = self.score_tree.identify_row(event.y)
        column = self.score_tree.identify_column(event.x)
        if not row_id or column != "#1":
            return

        self.score_tree.selection_set(row_id)
        values = list(self.score_tree.item(row_id, "values"))
        values[0] = "☑" if values[0] == "☐" else "☐"
        self.score_tree.item(row_id, values=values)
        self.sync_header_checkbox()
        return "break"

    def toggle_all_checkboxes(self):
        """Chọn hoặc bỏ chọn tất cả checkbox trong bảng."""
        checked = self.are_all_rows_checked()
        new_mark = "☐" if checked else "☑"
        for row_id in self.score_tree.get_children():
            values = list(self.score_tree.item(row_id, "values"))
            values[0] = new_mark
            self.score_tree.item(row_id, values=values)
        self.sync_header_checkbox()

    def are_all_rows_checked(self):
        """Kiểm tra xem tất cả dòng đã được chọn hay chưa."""
        row_ids = self.score_tree.get_children()
        return bool(row_ids) and all(self.score_tree.item(row_id, "values")[0] == "☑" for row_id in row_ids)

    def sync_header_checkbox(self):
        """Đồng bộ trạng thái checkbox trên header."""
        self.score_tree.heading("select", text="☑" if self.are_all_rows_checked() else "☐", anchor="center")

    def reindex_stt(self):
        """Đánh lại STT theo thứ tự dòng hiện tại."""
        for index, row_id in enumerate(self.score_tree.get_children(), start=1):
            values = list(self.score_tree.item(row_id, "values"))
            values[1] = str(index)
            self.score_tree.item(row_id, values=values)

    def add_score(self):
        """Mở form thêm điểm cho sinh viên."""
        # Mở ScoreEntryWindow từ app/views/windows/score_entry_window.py để nhập điểm mới.
        ScoreEntryWindow(
            self,
            self.database,
            self.student_info["student_id"],
            title="Thêm điểm",
            on_save=self._create_score_detail,
        )

    def edit_score(self):
        """Mở form sửa điểm của dòng đang chọn."""
        selected_item = self.score_tree.selection()
        if not selected_item:
            return

        detail = self.database.fetch_score_detail(int(selected_item[0]))
        if not detail:
            return

        detail_data = {
            "course_id": detail[2],
            "course_name": detail[3],
            "credits": str(detail[4]),
            "semester": detail[5],
            "school_year": detail[6],
            "score": str(detail[7]),
        }
        # Mở ScoreEntryWindow từ app/views/windows/score_entry_window.py để sửa điểm chi tiết.
        ScoreEntryWindow(
            self,
            self.database,
            self.student_info["student_id"],
            title="Sửa điểm",
            detail_data=detail_data,
            on_save=lambda data: self._update_score_detail(detail[0], data),
            detail_editable=False,
        )

    def delete_score(self):
        """Xóa một hoặc nhiều dòng điểm đang được chọn."""
        row_ids = self._get_rows_to_delete()
        if not row_ids:
            return

        if len(row_ids) > 1:
            confirm_text = f"Bạn có chắc muốn xóa {len(row_ids)} điểm đã chọn không?"
        else:
            confirm_text = "Bạn có chắc muốn xóa điểm đã chọn không?"

        if not messagebox.askyesno("Xác nhận xóa", confirm_text, parent=self):
            return

        for row_id in row_ids:
            self.database.delete_score_detail(int(row_id))

        self.refresh_data()
        if self.on_change:
            self.on_change()

    def _on_double_click(self, event):
        """Bấm đúp vào dòng để mở nhanh form sửa điểm."""
        row_id = self.score_tree.identify_row(event.y)
        column = self.score_tree.identify_column(event.x)
        if row_id and column != "#1":
            self.score_tree.selection_set(row_id)
            self.edit_score()

    def _create_score_detail(self, data):
        """Lưu điểm chi tiết mới xuống database."""
        self.database.insert_score_detail(data)
        self.refresh_data()
        if self.on_change:
            self.on_change()

    def _update_score_detail(self, detail_id, data):
        """Cập nhật điểm chi tiết đã chọn."""
        self.database.update_score_detail(detail_id, data)
        self.refresh_data()
        if self.on_change:
            self.on_change()

    def _get_rows_to_delete(self):
        """Lấy danh sách dòng cần xóa, ưu tiên các checkbox đã tick."""
        checked_rows = []
        for row_id in self.score_tree.get_children():
            if self.score_tree.item(row_id, "values")[0] == "☑":
                checked_rows.append(row_id)
        if checked_rows:
            return checked_rows

        selected_rows = list(self.score_tree.selection())
        if selected_rows:
            return selected_rows

        return []
