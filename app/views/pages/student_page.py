import csv
import re
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

# Import hàm get_logger từ app/utils/logger.py.
# StudentPage dùng logger này để ghi lại việc load dữ liệu, import CSV và thao tác sinh viên.
from app.utils.logger import get_logger

# Import StudentController từ app/controllers/student_controller.py.
# StudentPage dùng controller này để lấy dữ liệu và thao tác CSV/sinh viên.
from app.controllers.student_controller import StudentController
# Import StudentFormWindow từ app/views/windows/student_form_window.py.
# StudentPage mở form này khi người dùng thêm hoặc sửa sinh viên.
from app.views.windows.student_form_window import StudentFormWindow


logger = get_logger(__name__)


class StudentPage(ctk.CTkFrame):
    """Trang quản lý sinh viên: hiển thị, thêm, sửa, xóa và import/export CSV."""

    def __init__(self, parent, database, controller: StudentController):
        """Khởi tạo trang sinh viên."""
        super().__init__(parent, fg_color="#F8FAFC", corner_radius=0)
        self.database = database
        # Controller được truyền từ app/controllers/app_controller.py.
        # Trang này dùng controller để làm việc với dữ liệu sinh viên.
        self.controller = controller
        self.sort_state = {}
        self.all_students = []
        self._create_widgets()

    def _create_widgets(self):
        """Tạo toàn bộ giao diện của trang sinh viên."""
        accent = "#2F74FF"
        accent_hover = "#0050DB"
        outline_hover = "#EAF2FF"

        # Khung nội dung chính.
        content_box = ctk.CTkFrame(
            self,
            fg_color="#F4F8FF",
            corner_radius=16,
            border_width=2,
            border_color=accent,
        )
        content_box.pack(fill="both", expand=True, padx=16, pady=16)
        content_box.grid_rowconfigure(2, weight=1)
        content_box.grid_columnconfigure(0, weight=1)

        # Tiêu đề trang.
        title_label = ctk.CTkLabel(
            content_box,
            text="Quản lý sinh viên",
            font=("Arial", 20, "bold"),
            text_color="#111827",
        )
        title_label.grid(row=0, column=0, sticky="w", padx=24, pady=(20, 12))

        # Thanh công cụ gồm ô tìm kiếm và các nút chức năng.
        toolbar_frame = ctk.CTkFrame(content_box, fg_color="transparent")
        toolbar_frame.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        toolbar_frame.grid_columnconfigure(0, weight=1)

        # Ô tìm kiếm
        self.search_entry = ctk.CTkEntry(
            toolbar_frame,
            placeholder_text="Tìm kiếm mã sinh viên, họ tên, lớp...",
            height=32,
            corner_radius=10,
            border_width=2,
            border_color=accent,
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search_change)
        self.search_entry.bind("<Return>", self._on_search_change)

        add_button = ctk.CTkButton(
            toolbar_frame,
            text="Thêm",
            height=32,
            width=72,
            fg_color=accent,
            hover_color=accent_hover,
            corner_radius=10,
            command=self.add_student,
        )
        add_button.grid(row=0, column=1, padx=5)

        edit_button = ctk.CTkButton(
            toolbar_frame,
            text="Sửa",
            height=32,
            width=64,
            fg_color="transparent",
            text_color=accent,
            hover_color=outline_hover,
            border_width=2,
            border_color=accent,
            corner_radius=10,
            command=self.edit_student,
        )
        edit_button.grid(row=0, column=2, padx=5)

        delete_button = ctk.CTkButton(
            toolbar_frame,
            text="Xóa",
            height=32,
            width=64,
            fg_color="transparent",
            text_color=accent,
            hover_color=outline_hover,
            border_width=2,
            border_color=accent,
            corner_radius=10,
            command=self.delete_student,
        )
        delete_button.grid(row=0, column=3, padx=5)

        import_button = ctk.CTkButton(
            toolbar_frame,
            text="Nhập CSV",
            height=32,
            width=88,
            fg_color="transparent",
            text_color=accent,
            hover_color=outline_hover,
            border_width=2,
            border_color=accent,
            corner_radius=10,
            command=self.import_csv,
        )
        import_button.grid(row=0, column=4, padx=5)

        export_button = ctk.CTkButton(
            toolbar_frame,
            text="Xuất CSV",
            height=32,
            width=88,
            fg_color="transparent",
            text_color=accent,
            hover_color=outline_hover,
            border_width=2,
            border_color=accent,
            corner_radius=10,
            command=self.export_csv,
        )
        export_button.grid(row=0, column=5, padx=5)

        # Khung bảng Treeview.
        table_frame = ctk.CTkFrame(
            content_box,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#D7E3FF",
        )
        table_frame.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 20))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = (
            "select",
            "stt",
            "student_id",
            "student_name",
            "class_name",
            "gender",
            "birth_date",
            "email",
        )

        self.student_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
        )

        self._setup_treeview_style()
        self._setup_treeview_columns()
        self._setup_treeview_scrollbar(table_frame)

        self.student_tree.bind("<Button-1>", self.toggle_checkbox)
        self.student_tree.bind("<Double-1>", self._on_double_click)
        self.load_data()

    # Tạo style cho treeview
    def _setup_treeview_style(self):
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

    def _setup_treeview_columns(self):
        """Khai báo tiêu đề và độ rộng cho các cột của bảng."""
        self.student_tree.heading("select", text="☐", anchor="center", command=self.toggle_all_checkboxes)
        self.student_tree.heading("stt", text="STT", anchor="center")
        self.student_tree.heading("student_id", text="Mã SV", command=lambda: self.on_heading_click("student_id"))
        self.student_tree.heading("student_name", text="Họ tên", command=lambda: self.on_heading_click("student_name"))
        self.student_tree.heading("class_name", text="Lớp", command=lambda: self.on_heading_click("class_name"))
        self.student_tree.heading("gender", text="Giới tính", command=lambda: self.on_heading_click("gender"))
        self.student_tree.heading("birth_date", text="Ngày sinh", command=lambda: self.on_heading_click("birth_date"))
        self.student_tree.heading("email", text="email", command=lambda: self.on_heading_click("email"))

        self.student_tree.column("select", width=50, minwidth=50, anchor="center", stretch=False)
        self.student_tree.column("stt", width=60, minwidth=60, anchor="center", stretch=False)
        self.student_tree.column("student_id", width=120, minwidth=90, anchor="center")
        self.student_tree.column("student_name", width=220, minwidth=160, anchor="w")
        self.student_tree.column("class_name", width=120, minwidth=90, anchor="center")
        self.student_tree.column("gender", width=100, minwidth=80, anchor="center")
        self.student_tree.column("birth_date", width=120, minwidth=90, anchor="center")
        self.student_tree.column("email", width=140, minwidth=110, anchor="center")

    def _setup_treeview_scrollbar(self, table_frame):
        """Tạo thanh cuộn dọc cho bảng."""
        y_scrollbar = ctk.CTkScrollbar(
            table_frame,
            orientation="vertical",
            command=self.student_tree.yview,
            width=12,
            fg_color="#E5EDFF",
            button_color="#2F74FF",
            button_hover_color="#0050DB",
        )
        self.student_tree.configure(yscrollcommand=y_scrollbar.set)

        self.student_tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")

    def load_data(self):
        """Nạp dữ liệu sinh viên từ controller vào bảng."""
        # Gọi StudentController.fetch_students() để lấy danh sách sinh viên từ database.
        students = self.controller.fetch_students()
        self.all_students = list(students)
        logger.info("Đã load %s sinh viên vào bảng.", len(self.all_students))
        self._render_students(self._filter_students(self.all_students, self.search_entry.get().strip()))

    def refresh_data(self):
        """Làm mới bảng sinh viên."""
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        self.load_data()

    # -------------------------------------------------- #
    # =============== Search / Filter ================== #
    # -------------------------------------------------- #

    def _on_search_change(self, event=None):
        """Lọc dữ liệu sinh viên theo nội dung đang nhập ở ô tìm kiếm."""
        query = self.search_entry.get().strip()
        filtered_students = self._filter_students(self.all_students, query)
        self._render_students(filtered_students)
        logger.info(
            "Đã lọc sinh viên theo từ khóa '%s' (%s kết quả).",
            query if query else "(trống)",
            len(filtered_students),
        )

    def _filter_students(self, students, query):
        """Lọc danh sách sinh viên theo từ khóa nhập vào."""
        if not query:
            return list(students)

        normalized_query = query.casefold()
        filtered_students = []
        for student in students:
            searchable_text = " ".join(str(value) for value in student).casefold()
            if normalized_query in searchable_text:
                filtered_students.append(student)
        return filtered_students

    def _render_students(self, students):
        """Đổ danh sách sinh viên đã lọc lên Treeview."""
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        for index, student in enumerate(students, start=1):
            row = ("☐", str(index), *student)
            self.student_tree.insert("", "end", values=row)

        self.reindex_stt()
        self.sync_header_checkbox()

    def toggle_checkbox(self, event):
        """Đổi trạng thái checkbox của một dòng khi bấm vào cột đầu tiên."""
        row_id = self.student_tree.identify_row(event.y)
        column = self.student_tree.identify_column(event.x)

        if not row_id or column != "#1":
            return

        self.student_tree.selection_set(row_id)
        values = list(self.student_tree.item(row_id, "values"))
        values[0] = "☑" if values[0] == "☐" else "☐"
        self.student_tree.item(row_id, values=values)
        self.sync_header_checkbox()
        return "break"

    def toggle_all_checkboxes(self):
        """Chọn hoặc bỏ chọn tất cả checkbox trong bảng."""
        checked = self.are_all_rows_checked()
        new_mark = "☐" if checked else "☑"

        for row_id in self.student_tree.get_children():
            values = list(self.student_tree.item(row_id, "values"))
            values[0] = new_mark
            self.student_tree.item(row_id, values=values)

        self.sync_header_checkbox()

    def are_all_rows_checked(self):
        """Kiểm tra xem tất cả dòng đã được chọn hay chưa."""
        row_ids = self.student_tree.get_children()
        return bool(row_ids) and all(
            self.student_tree.item(row_id, "values")[0] == "☑"
            for row_id in row_ids
        )

    def sync_header_checkbox(self):
        """Đồng bộ trạng thái checkbox trên header."""
        self.student_tree.heading("select", text="☑" if self.are_all_rows_checked() else "☐")

    def on_heading_click(self, column_name):
        """Xử lý khi bấm vào tiêu đề cột để sắp xếp."""
        self.sort_rows(column_name)

    def sort_rows(self, column_name):
        """Sắp xếp dữ liệu theo cột đã chọn."""
        if column_name not in self.sort_state:
            self.sort_state[column_name] = False
        self.sort_state[column_name] = not self.sort_state[column_name]
        reverse = self.sort_state[column_name]

        rows = [self.student_tree.item(row_id, "values") for row_id in self.student_tree.get_children()]
        rows.sort(key=lambda values: self.get_sort_key(values, column_name), reverse=reverse)

        for row_id in self.student_tree.get_children():
            self.student_tree.delete(row_id)

        for row in rows:
            self.student_tree.insert("", "end", values=tuple(row))

        self.reindex_stt()
        self.sync_header_checkbox()

    def reindex_stt(self):
        """Đánh lại STT theo thứ tự dòng hiện tại."""
        for index, row_id in enumerate(self.student_tree.get_children(), start=1):
            values = list(self.student_tree.item(row_id, "values"))
            values[1] = str(index)
            self.student_tree.item(row_id, values=values)

    def get_sort_key(self, values, column_name):
        """Tạo khóa sắp xếp phù hợp với từng cột."""
        columns = {
            "stt": 1,
            "student_id": 2,
            "student_name": 3,
            "class_name": 4,
            "gender": 5,
            "birth_date": 6,
            "email": 7,
        }
        index = columns[column_name]
        value = values[index]

        if column_name == "stt":
            return int(value)
        if column_name == "birth_date":
            day, month, year = value.split("/")
            return int(year), int(month), int(day)
        return str(value).casefold()

    def add_student(self):
        """Mở form thêm sinh viên."""
        logger.info("Người dùng mở form thêm sinh viên.")
        self._open_student_form("Thêm sinh viên", on_save=self._create_student)

    def edit_student(self):
        """Mở form sửa sinh viên đã chọn."""
        selected_item = self.student_tree.selection()
        if not selected_item:
            logger.warning("Người dùng bấm Sửa sinh viên nhưng chưa chọn dòng nào.")
            messagebox.showwarning("Chưa chọn dữ liệu", "Chưa chọn sinh viên để sửa.", parent=self)
            return

        values = self.student_tree.item(selected_item[0], "values")
        student_data = {
            "student_id": values[2],
            "student_name": values[3],
            "class_name": values[4],
            "gender": values[5],
            "birth_date": values[6],
            "email": values[7],
        }
        self._open_student_form(
            "Sửa sinh viên",
            student_data,
            on_save=lambda data: self._update_student(values[2], data),
            student_id_editable=False,
        )

    def delete_student(self):
        """Xóa các sinh viên đang được chọn."""
        row_ids = self._get_rows_to_delete()
        if not row_ids:
            logger.warning("Người dùng bấm Xóa sinh viên nhưng chưa chọn dòng nào.")
            messagebox.showwarning("Chưa chọn dữ liệu", "Chưa chọn sinh viên để xóa.", parent=self)
            return

        if len(row_ids) > 1:
            confirm_text = f"Bạn có chắc muốn xóa {len(row_ids)} sinh viên đã chọn không?"
        else:
            confirm_text = "Bạn có chắc muốn xóa sinh viên đã chọn không?"

        if not messagebox.askyesno("Xác nhận xóa", confirm_text, parent=self):
            return

        student_ids = []
        for row_id in row_ids:
            values = self.student_tree.item(row_id, "values")
            student_ids.append(values[2])

        try:
            self.controller.delete_students(student_ids)
            logger.info("Đã xóa %s sinh viên.", len(student_ids))
        except Exception as exc:
            logger.exception("Lỗi khi xóa sinh viên: %s", exc)
            messagebox.showerror("Lỗi xóa dữ liệu", f"Không thể xóa sinh viên:\n{exc}", parent=self)
            return

        self.refresh_data()
        self._refresh_stats_page()
        self._refresh_score_page()

    def _get_rows_to_delete(self):
        """Lấy danh sách dòng cần xóa."""
        checked_rows = []
        for row_id in self.student_tree.get_children():
            if self.student_tree.item(row_id, "values")[0] == "☑":
                checked_rows.append(row_id)
        if checked_rows:
            return checked_rows

        selected_rows = list(self.student_tree.selection())
        if selected_rows:
            return selected_rows

        return []

    def import_csv(self):
        """Nhập dữ liệu sinh viên từ file CSV."""
        file_path = filedialog.askopenfilename(
            title="Chọn file CSV sinh viên",
            filetypes=[("CSV files", "*.csv")],
            parent=self,
        )
        if not file_path:
            return

        try:
            result = self.controller.import_csv(file_path)
        except Exception as exc:
            logger.exception("Lỗi khi nhập CSV sinh viên: %s", exc)
            messagebox.showerror("Lỗi nhập CSV", f"Không thể nhập file CSV:\n{exc}", parent=self)
            return

        if not result["ok"]:
            logger.warning("Nhập CSV sinh viên thất bại: %s", result["message"])
            messagebox.showerror("Lỗi file CSV", result["message"], parent=self)
            return

        self.refresh_data()
        self._refresh_stats_page()
        self._refresh_score_page()
        logger.info(
            "Nhập CSV sinh viên thành công: thêm mới %s, cập nhật %s.",
            result["inserted_count"],
            result["updated_count"],
        )

        result_text = (
            f"Đã nhập thành công {result['inserted_count']} dòng mới và cập nhật {result['updated_count']} dòng sinh viên."
        )
        skipped_rows = result["skipped_rows"]
        if skipped_rows:
            result_text += "\n\nCác dòng bị bỏ qua:\n" + "\n".join(skipped_rows[:10])
            if len(skipped_rows) > 10:
                result_text += f"\n... và {len(skipped_rows) - 10} dòng khác."

        messagebox.showinfo("Kết quả nhập CSV", result_text, parent=self)

    def export_csv(self):
        """Xuất dữ liệu sinh viên ra file CSV."""
        file_path = filedialog.asksaveasfilename(
            title="Lưu file CSV sinh viên",
            initialfile="danh_sach_sinh_vien.csv",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            parent=self,
        )
        if not file_path:
            return

        try:
            count = self.controller.export_csv(file_path)
        except Exception as exc:
            logger.exception("Lỗi khi xuất CSV sinh viên: %s", exc)
            messagebox.showerror("Lỗi xuất CSV", f"Không thể xuất file CSV:\n{exc}", parent=self)
            return

        logger.info("Đã xuất %s sinh viên ra file CSV.", count)
        messagebox.showinfo("Xuất CSV", f"Đã xuất {count} sinh viên ra file CSV.", parent=self)


    # -------------------------------------------------- #
    # =============== Validation ======================= #
    # -------------------------------------------------- #
    
    def _is_valid_student_name(self, value: str) -> bool:
        """Kiểm tra tên sinh viên chỉ gồm chữ và khoảng trắng."""
        value = value.strip()
        if not value:
            return False
        for part in value.split():
            if not part.isalpha():
                return False
        return True

    def _is_valid_alnum_with_letter_and_digit(self, value: str) -> bool:
        """Kiểm tra chuỗi phải có cả chữ và số, không có ký tự đặc biệt."""
        value = value.strip()
        if not value or not value.isalnum():
            return False
        has_letter = any(char.isalpha() for char in value)
        has_digit = any(char.isdigit() for char in value)
        return has_letter and has_digit

    def _is_valid_gmail(self, value: str) -> bool:
        """Kiểm tra email đúng định dạng Gmail."""
        return bool(re.fullmatch(r"[A-Za-z0-9._%+-]+@gmail\.com", value.strip()))

    def _is_valid_birth_date(self, value: str) -> bool:
        """Kiểm tra ngày sinh đúng định dạng dd/mm/yyyy."""
        try:
            datetime.strptime(value, "%d/%m/%Y")
        except ValueError:
            return False
        return True
    
    # -------------------------------------------------- #
    # =============== Validation ======================= #
    # -------------------------------------------------- #

    def _refresh_stats_page(self):
        """Yêu cầu cửa sổ chính làm mới trang thống kê."""
        main_window = self.winfo_toplevel()
        refresh_stats_page = getattr(main_window, "refresh_stats_page", None)
        if callable(refresh_stats_page):
            refresh_stats_page()

    def _refresh_score_page(self):
        """Yêu cầu cửa sổ chính làm mới trang bảng điểm."""
        main_window = self.winfo_toplevel()
        refresh_score_page = getattr(main_window, "refresh_score_page", None)
        if callable(refresh_score_page):
            refresh_score_page()

    def _open_student_form(self, title, student_data=None, on_save=None, student_id_editable=True):
        """Mở form thêm hoặc sửa sinh viên."""
        # Mở StudentFormWindow từ app/views/windows/student_form_window.py để nhập hoặc sửa dữ liệu.
        StudentFormWindow(
            self.winfo_toplevel(),
            self.database,
            title=title,
            student_data=student_data,
            on_save=on_save,
            student_id_editable=student_id_editable,
        )

    def _create_student(self, data):
        """Lưu sinh viên mới xuống database."""
        if not data.get("student_id"):
            return

        try:
            self.controller.create_student(data)
            logger.info("Đã thêm sinh viên mới: %s.", data.get("student_id"))
        except Exception as exc:
            logger.exception("Lỗi khi thêm sinh viên: %s", exc)
            messagebox.showerror("Lỗi dữ liệu", f"Không thể thêm sinh viên:\n{exc}", parent=self)
            return
        self.refresh_data()
        self._refresh_stats_page()
        self._refresh_score_page()

    def _update_student(self, original_student_id, data):
        """Cập nhật dữ liệu sinh viên đã chọn."""
        try:
            self.controller.update_student(original_student_id, data)
            logger.info("Đã sửa sinh viên: %s.", original_student_id)
        except Exception as exc:
            logger.exception("Lỗi khi sửa sinh viên: %s", exc)
            messagebox.showerror("Lỗi dữ liệu", f"Không thể sửa sinh viên:\n{exc}", parent=self)
            return
        self.refresh_data()
        self._refresh_stats_page()
        self._refresh_score_page()

    def _on_double_click(self, event):
        """Bấm đúp vào dòng để mở nhanh form sửa."""
        row_id = self.student_tree.identify_row(event.y)
        column = self.student_tree.identify_column(event.x)
        if row_id and column != "#1":
            self.student_tree.selection_set(row_id)
            self.edit_student()
