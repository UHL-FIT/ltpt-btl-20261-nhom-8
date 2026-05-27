import re

from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

# Import hàm get_logger từ app/utils/logger.py.
# CoursePage dùng logger này để ghi lại việc load dữ liệu, import CSV và thao tác học phần.
from app.utils.logger import get_logger

# Import CourseController từ app/controllers/course_controller.py.
# CoursePage dùng controller này để lấy dữ liệu và thao tác CSV/học phần.
from app.controllers.course_controller import CourseController
# Import CourseFormWindow từ app/views/windows/course_form_window.py.
# CoursePage mở form này khi người dùng thêm hoặc sửa học phần.
from app.views.windows.course_form_window import CourseFormWindow


logger = get_logger(__name__)


class CoursePage(ctk.CTkFrame):
    """Trang quản lý học phần: hiển thị, thêm, sửa, xóa và import/export CSV."""

    # Hàm tự đồng chạy để tạo khung chính
    def __init__(self, parent, database, controller: CourseController):
        """Khởi tạo trang học phần."""
        super().__init__(
            parent, 
            fg_color="#F8FAFC", 
            corner_radius=0
        )
        self.database = database
        # Controller được truyền từ app/controllers/app_controller.py.
        # Trang này dùng controller để làm việc với dữ liệu học phần.
        self.controller = controller
        self.sort_state = {}
        self.all_courses = []
        self._create_widgets()


    def _create_widgets(self):
        """Tạo toàn bộ giao diện của trang học phần."""
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
            text="Quản lý học phần",
            font=("Arial", 20, "bold"),
            text_color="#111827",
        )
        title_label.grid(row=0, column=0, sticky="w", padx=24, pady=(20, 12))

        # Khung thanh công cụ gồm ô tìm kiếm và các nút chức năng.
        toolbar_frame = ctk.CTkFrame(
            content_box, 
            fg_color="transparent"
        )
        toolbar_frame.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        toolbar_frame.grid_columnconfigure(0, weight=1)

        # Tạo ô nhập tìm kiếm
        self.search_entry = ctk.CTkEntry(
            toolbar_frame,
            placeholder_text="Tìm kiếm mã học phần, tên học phần, học kỳ...",
            height=32,
            corner_radius=10,
            border_width=2,
            border_color=accent,
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search_change)
        self.search_entry.bind("<Return>", self._on_search_change)

        # Tạo nút thêm
        add_button = ctk.CTkButton(
            toolbar_frame,
            text="Thêm",
            height=32,
            width=72,
            fg_color=accent,
            hover_color=accent_hover,
            corner_radius=10,
            command=self.add_course,
        )
        add_button.grid(row=0, column=1, padx=5)

        # Tạo nút sửa
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
            command=self.edit_course,
        )
        edit_button.grid(row=0, column=2, padx=5)

        # Tạo nút xóa
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
            command=self.delete_course,
        )
        delete_button.grid(row=0, column=3, padx=5)

        # Tạo nút import CSV
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

        # Tạo nút export CSV
        export_button = ctk.CTkButton(
            toolbar_frame,
            text="Xuất CSV",
            height=32,
            width=86,
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

        columns = ("select", "stt", "course_id", "course_name", "credits", "semester")

        # Tạo treeview (bảng) xem dữ liệu
        self.course_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
        )

        self._setup_treeview_style()
        self._setup_treeview_columns()
        self._setup_treeview_scrollbar(table_frame)

        # Lệnh gắn sự kiện chuột cho self.course_tree 
        # Khi người dùng nhấn chuột trái một lần vào course_tree, 
        # chương trình sẽ gọi hàm: toggle_checkbox (chuyển đổi trạng thái checkbox)
        self.course_tree.bind("<Button-1>", self.toggle_checkbox)
        # Khi người dùng nhấn đúp chuột trái vào course_tree, 
        # chương trình sẽ gọi hàm: _on_double_click
        self.course_tree.bind("<Double-1>", self._on_double_click)

        self.load_data()

    # Hàm tạo style (kiểu) cho treeview (bảng)
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

    # Hàm tạo cột cho treeview (bảng)
    def _setup_treeview_columns(self):
        """Khai báo tiêu đề và độ rộng cho các cột của bảng."""
        self.course_tree.heading("select", text="☐", anchor="center", command=self.toggle_all_checkboxes)
        self.course_tree.heading("stt", text="STT", anchor="center")
        self.course_tree.heading("course_id", text="Mã học phần", command=lambda: self.on_heading_click("course_id"))
        self.course_tree.heading("course_name", text="Tên học phần", command=lambda: self.on_heading_click("course_name"))
        self.course_tree.heading("credits", text="Số tín chỉ", command=lambda: self.on_heading_click("credits"))
        self.course_tree.heading("semester", text="Học kỳ", command=lambda: self.on_heading_click("semester"))

        self.course_tree.column("select", width=50, minwidth=50, anchor="center", stretch=False)
        self.course_tree.column("stt", width=60, minwidth=60, anchor="center", stretch=False)
        self.course_tree.column("course_id", width=140, minwidth=100, anchor="center")
        self.course_tree.column("course_name", width=260, minwidth=180, anchor="w")
        self.course_tree.column("credits", width=100, minwidth=80, anchor="center")
        self.course_tree.column("semester", width=100, minwidth=80, anchor="center")

    # Hàm tạo scrollbar (thanh cuộn) cho treeview (bảng)
    def _setup_treeview_scrollbar(self, table_frame):
        """Tạo thanh cuộn dọc cho bảng."""
        y_scrollbar = ctk.CTkScrollbar(
            table_frame,
            orientation="vertical",
            command=self.course_tree.yview,
            width=12,
            fg_color="#E5EDFF",
            button_color="#2F74FF",
            button_hover_color="#0050DB",
        )
        self.course_tree.configure(yscrollcommand=y_scrollbar.set)

        self.course_tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")

    # Hàm load dữ liệu
    def load_data(self):
        """Nạp dữ liệu học phần từ controller vào bảng."""
        # Gọi CourseController.fetch_courses() để lấy danh sách học phần từ database.
        courses = self.controller.fetch_courses()
        self.all_courses = list(courses)
        logger.info("Đã load %s học phần vào bảng.", len(self.all_courses))
        self._render_courses(self._filter_courses(self.all_courses, self.search_entry.get().strip()))

    # Hàm làm mới dữ liệu
    def refresh_data(self):
        """Làm mới bảng học phần."""
        for item in self.course_tree.get_children():
            self.course_tree.delete(item)
        self.load_data()

    # -------------------------------------------------- #
    # =============== Search / Filter ================== #
    # -------------------------------------------------- #

    def _on_search_change(self, event=None):
        """Lọc dữ liệu học phần theo nội dung đang nhập ở ô tìm kiếm."""
        query = self.search_entry.get().strip()
        filtered_courses = self._filter_courses(self.all_courses, query)
        self._render_courses(filtered_courses)
        logger.info(
            "Đã lọc học phần theo từ khóa '%s' (%s kết quả).",
            query if query else "(trống)",
            len(filtered_courses),
        )

    def _filter_courses(self, courses, query):
        """Lọc danh sách học phần theo từ khóa nhập vào."""
        if not query:
            return list(courses)

        normalized_query = query.casefold()
        filtered_courses = []
        for course in courses:
            searchable_text = " ".join(str(value) for value in course).casefold()
            if normalized_query in searchable_text:
                filtered_courses.append(course)
        return filtered_courses

    def _render_courses(self, courses):
        """Đổ danh sách học phần đã lọc lên Treeview."""
        for item in self.course_tree.get_children():
            self.course_tree.delete(item)

        for index, course in enumerate(courses, start=1):
            row = ("☐", str(index), *course)
            self.course_tree.insert("", "end", values=row)

        self.reindex_stt()
        self.sync_header_checkbox()

    # Hàm chuyển đổi trạng thái của checkbox
    def toggle_checkbox(self, event):
        """Đổi trạng thái checkbox của một dòng khi bấm vào cột đầu tiên."""
        row_id = self.course_tree.identify_row(event.y)
        column = self.course_tree.identify_column(event.x)
        if not row_id or column != "#1":
            return

        self.course_tree.selection_set(row_id)
        values = list(self.course_tree.item(row_id, "values"))
        values[0] = "☑" if values[0] == "☐" else "☐"
        self.course_tree.item(row_id, values=values)
        self.sync_header_checkbox()
        return "break"

    # Hàm chuyển đổi trạng thái của tất cả checkbox
    def toggle_all_checkboxes(self):
        """Chọn hoặc bỏ chọn tất cả checkbox trong bảng."""
        checked = self.are_all_rows_checked()
        new_mark = "☐" if checked else "☑"

        for row_id in self.course_tree.get_children():
            values = list(self.course_tree.item(row_id, "values"))
            values[0] = new_mark
            self.course_tree.item(row_id, values=values)

        self.sync_header_checkbox()

    def are_all_rows_checked(self):
        """Kiểm tra xem tất cả dòng đã được chọn hay chưa."""
        row_ids = self.course_tree.get_children()
        return bool(row_ids) and all(
            self.course_tree.item(row_id, "values")[0] == "☑"
            for row_id in row_ids
        )

    def sync_header_checkbox(self):
        """Đồng bộ trạng thái checkbox trên header."""
        self.course_tree.heading("select", text="☑" if self.are_all_rows_checked() else "☐")

    def on_heading_click(self, column_name):
        """Xử lý khi bấm vào tiêu đề cột để sắp xếp."""
        self.sort_rows(column_name)

    def sort_rows(self, column_name):
        """Sắp xếp dữ liệu theo cột đã chọn."""
        if column_name not in self.sort_state:
            self.sort_state[column_name] = False
        self.sort_state[column_name] = not self.sort_state[column_name]
        reverse = self.sort_state[column_name]

        rows = [self.course_tree.item(row_id, "values") for row_id in self.course_tree.get_children()]
        rows.sort(key=lambda values: self.get_sort_key(values, column_name), reverse=reverse)

        for row_id in self.course_tree.get_children():
            self.course_tree.delete(row_id)

        for row in rows:
            self.course_tree.insert("", "end", values=tuple(row))

        self.reindex_stt()
        self.sync_header_checkbox()

    def reindex_stt(self):
        """Đánh lại STT theo thứ tự dòng hiện tại."""
        for index, row_id in enumerate(self.course_tree.get_children(), start=1):
            values = list(self.course_tree.item(row_id, "values"))
            values[1] = str(index)
            self.course_tree.item(row_id, values=values)

    def get_sort_key(self, values, column_name):
        """Tạo khóa sắp xếp phù hợp với từng cột."""
        columns = {
            "stt": 1,
            "course_id": 2,
            "course_name": 3,
            "credits": 4,
            "semester": 5,
        }
        index = columns[column_name]
        value = values[index]

        if column_name in ("stt", "credits"):
            return int(value)
        if column_name == "semester":
            match = re.search(r"\d+", str(value))
            return int(match.group()) if match else 0
        return str(value).casefold()

    def add_course(self):
        """Mở form thêm học phần."""
        logger.info("Người dùng mở form thêm học phần.")
        self._open_course_form("Thêm học phần", on_save=self._create_course)

    def edit_course(self):
        """Mở form sửa học phần đã chọn."""
        selected_item = self.course_tree.selection()
        if not selected_item:
            logger.warning("Người dùng bấm Sửa học phần nhưng chưa chọn dòng nào.")
            messagebox.showwarning("Chưa chọn dữ liệu", "Chưa chọn học phần để sửa.", parent=self)
            return

        values = self.course_tree.item(selected_item[0], "values")
        course_data = {
            "course_id": values[2],
            "course_name": values[3],
            "credits": values[4],
            "semester": values[5],
        }
        self._open_course_form(
            "Sửa học phần",
            course_data,
            on_save=lambda data: self._update_course(values[2], data),
            course_id_editable=False,
        )

    def delete_course(self):
        """Xóa các học phần đang được chọn."""
        row_ids = self._get_rows_to_delete()
        if not row_ids:
            logger.warning("Người dùng bấm Xóa học phần nhưng chưa chọn dòng nào.")
            messagebox.showwarning("Chưa chọn dữ liệu", "Chưa chọn học phần để xóa.", parent=self)
            return

        if len(row_ids) > 1:
            confirm_text = f"Bạn có chắc muốn xóa {len(row_ids)} học phần đã chọn không?"
        else:
            confirm_text = "Bạn có chắc muốn xóa học phần đã chọn không?"

        if not messagebox.askyesno("Xác nhận xóa", confirm_text, parent=self):
            return

        course_ids = []
        for row_id in row_ids:
            values = self.course_tree.item(row_id, "values")
            course_ids.append(values[2])

        try:
            self.controller.delete_courses(course_ids)
            logger.info("Đã xóa %s học phần.", len(course_ids))
        except Exception as exc:
            logger.exception("Lỗi khi xóa học phần: %s", exc)
            messagebox.showerror("Lỗi xóa dữ liệu", f"Không thể xóa học phần:\n{exc}", parent=self)
            return
        self.refresh_data()
        self._refresh_stats_page()

    def _get_rows_to_delete(self):
        """Lấy danh sách dòng cần xóa, ưu tiên các checkbox đã tick."""
        checked_rows = []
        for row_id in self.course_tree.get_children():
            if self.course_tree.item(row_id, "values")[0] == "☑":
                checked_rows.append(row_id)
        if checked_rows:
            return checked_rows

        selected_rows = list(self.course_tree.selection())
        if selected_rows:
            return selected_rows

        return []

    def import_csv(self):
        """Nhập dữ liệu học phần từ file CSV."""
        file_path = filedialog.askopenfilename(
            title="Chọn file CSV học phần",
            filetypes=[("CSV files", "*.csv")],
            parent=self,
        )
        if not file_path:
            return

        try:
            result = self.controller.import_csv(file_path)
        except Exception as exc:
            logger.exception("Lỗi khi nhập CSV học phần: %s", exc)
            messagebox.showerror("Lỗi nhập CSV", f"Không thể nhập file CSV:\n{exc}", parent=self)
            return

        if not result["ok"]:
            logger.warning("Nhập CSV học phần thất bại: %s", result["message"])
            messagebox.showerror("Lỗi file CSV", result["message"], parent=self)
            return

        self.refresh_data()
        self._refresh_stats_page()
        logger.info(
            "Nhập CSV học phần thành công: thêm mới %s, cập nhật %s.",
            result["inserted_count"],
            result["updated_count"],
        )

        result_text = (
            f"Đã nhập thành công {result['inserted_count']} dòng mới và cập nhật {result['updated_count']} dòng học phần."
        )
        skipped_rows = result["skipped_rows"]
        if skipped_rows:
            result_text += "\n\nCác dòng bị bỏ qua:\n" + "\n".join(skipped_rows[:10])
            if len(skipped_rows) > 10:
                result_text += f"\n... và {len(skipped_rows) - 10} dòng khác."

        messagebox.showinfo("Kết quả nhập CSV", result_text, parent=self)

    def export_csv(self):
        """Xuất dữ liệu học phần ra file CSV."""
        file_path = filedialog.asksaveasfilename(
            title="Lưu file CSV học phần",
            initialfile="danh_sach_hoc_phan.csv",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            parent=self,
        )
        if not file_path:
            return

        try:
            count = self.controller.export_csv(file_path)
        except Exception as exc:
            logger.exception("Lỗi khi xuất CSV học phần: %s", exc)
            messagebox.showerror("Lỗi xuất CSV", f"Không thể xuất file CSV:\n{exc}", parent=self)
            return

        logger.info("Đã xuất %s học phần ra file CSV.", count)
        messagebox.showinfo("Xuất CSV", f"Đã xuất {count} học phần ra file CSV.", parent=self)

    def _open_course_form(self, title, course_data=None, on_save=None, course_id_editable=True):
        """Mở form thêm hoặc sửa học phần."""
        # Mở CourseFormWindow từ app/views/windows/course_form_window.py để nhập hoặc sửa dữ liệu.
        CourseFormWindow(
            self.winfo_toplevel(),
            self.database,
            title=title,
            course_data=course_data,
            on_save=on_save,
            course_id_editable=course_id_editable,
        )

    def _create_course(self, data):
        """Lưu học phần mới xuống database."""
        if not data.get("course_id"):
            return

        try:
            self.controller.create_course(data)
            logger.info("Đã thêm học phần mới: %s.", data.get("course_id"))
        except Exception as exc:
            logger.exception("Lỗi khi thêm học phần: %s", exc)
            messagebox.showerror("Lỗi dữ liệu", f"Không thể thêm học phần:\n{exc}", parent=self)
            return
        self.refresh_data()
        self._refresh_stats_page()

    def _update_course(self, original_course_id, data):
        """Cập nhật dữ liệu học phần đã chọn."""
        try:
            self.controller.update_course(original_course_id, data)
            logger.info("Đã sửa học phần: %s.", original_course_id)
        except Exception as exc:
            logger.exception("Lỗi khi sửa học phần: %s", exc)
            messagebox.showerror("Lỗi dữ liệu", f"Không thể sửa học phần:\n{exc}", parent=self)
            return
        self.refresh_data()
        self._refresh_stats_page()

    def _refresh_stats_page(self):
        """Yêu cầu cửa sổ chính làm mới trang thống kê."""
        main_window = self.winfo_toplevel()
        refresh_stats_page = getattr(main_window, "refresh_stats_page", None)
        if callable(refresh_stats_page):
            refresh_stats_page()

    def _on_double_click(self, event):
        """Bấm đúp vào dòng để mở nhanh form sửa."""
        row_id = self.course_tree.identify_row(event.y)
        column = self.course_tree.identify_column(event.x)
        if row_id and column != "#1":
            self.course_tree.selection_set(row_id)
            self.edit_course()
