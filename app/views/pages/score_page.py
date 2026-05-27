from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

# Import hàm get_logger từ app/utils/logger.py.
# ScorePage dùng logger này để ghi lại việc load bảng điểm, xem chi tiết và xuất CSV.
from app.utils.logger import get_logger

# Import ScoreController từ app/controllers/score_controller.py.
# ScorePage dùng controller này để lấy dữ liệu bảng điểm và xuất CSV.
from app.controllers.score_controller import ScoreController
# Import ScoreDetailWindow từ app/views/windows/score_detail_window.py.
# ScorePage mở cửa sổ này khi người dùng xem chi tiết bảng điểm.
from app.views.windows.score_detail_window import ScoreDetailWindow


logger = get_logger(__name__)


class ScorePage(ctk.CTkFrame):
    """Trang quản lý bảng điểm tổng hợp của sinh viên."""

    def __init__(self, parent, database, controller: ScoreController):
        """Khởi tạo trang bảng điểm."""
        super().__init__(parent, fg_color="#F8FAFC", corner_radius=0)
        self.database = database
        # Controller được truyền từ app/controllers/app_controller.py.
        # Trang này dùng controller để làm việc với dữ liệu bảng điểm tổng hợp.
        self.controller = controller
        self.sort_state = {}
        self.all_scores = []
        self._create_widgets()

    def _create_widgets(self):
        """Tạo toàn bộ giao diện của trang bảng điểm."""
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
            text="Quản lý bảng điểm",
            font=("Arial", 20, "bold"),
            text_color="#111827",
        )
        title_label.grid(row=0, column=0, sticky="w", padx=24, pady=(20, 12))

        # Thanh công cụ.
        toolbar_frame = ctk.CTkFrame(content_box, fg_color="transparent")
        toolbar_frame.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        toolbar_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            toolbar_frame,
            placeholder_text="Tìm kiếm mã sinh viên, tên sinh viên, học phần...",
            height=32,
            corner_radius=10,
            border_width=2,
            border_color=accent,
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search_change)
        self.search_entry.bind("<Return>", self._on_search_change)

        # Nút xem chi tiết
        button_see_details = ctk.CTkButton(
            toolbar_frame,
            text="Xem chi tiết",
            height=32,
            width=92,
            fg_color=accent,
            hover_color=accent_hover,
            corner_radius=10,
            command=self.see_details,
        )
        button_see_details.grid(row=0, column=1, padx=5)

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
        export_button.grid(row=0, column=2, padx=5)

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

        columns = ("stt", "student_id", "student_name", "class_name", "score", "grade")

        self.score_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
        )

        self._setup_treeview_style()
        self._setup_treeview_columns()
        self._setup_treeview_scrollbar(table_frame)

        self.score_tree.bind("<Double-1>", self._on_double_click)
        self.load_data()

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
        self.score_tree.heading("stt", text="STT", anchor="center")
        self.score_tree.heading("student_id", text="Mã SV", command=lambda: self.on_heading_click("student_id"))
        self.score_tree.heading("student_name", text="Họ Tên", command=lambda: self.on_heading_click("student_name"))
        self.score_tree.heading("class_name", text="Lớp", command=lambda: self.on_heading_click("class_name"))
        self.score_tree.heading("score", text="Điểm GPA", command=lambda: self.on_heading_click("score"))
        self.score_tree.heading("grade", text="Xếp loại", command=lambda: self.on_heading_click("grade"))

        self.score_tree.column("stt", width=60, minwidth=60, anchor="center", stretch=False)
        self.score_tree.column("student_id", width=120, minwidth=90, anchor="center")
        self.score_tree.column("student_name", width=220, minwidth=160, anchor="w")
        self.score_tree.column("class_name", width=220, minwidth=160, anchor="center")
        self.score_tree.column("score", width=100, minwidth=80, anchor="center")
        self.score_tree.column("grade", width=120, minwidth=90, anchor="center")

    def _setup_treeview_scrollbar(self, table_frame):
        """Tạo thanh cuộn dọc cho bảng."""
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

    def load_data(self):
        """Nạp dữ liệu bảng điểm từ controller vào Treeview."""
        # Gọi ScoreController.fetch_scores() để lấy dữ liệu bảng điểm từ database.
        scores = self.controller.fetch_scores()
        self.all_scores = list(scores)
        logger.info("Đã load %s dòng bảng điểm vào bảng.", len(self.all_scores))
        self._render_scores(self._filter_scores(self.all_scores, self.search_entry.get().strip()))

    def refresh_data(self):
        """Làm mới bảng điểm."""
        for item in self.score_tree.get_children():
            self.score_tree.delete(item)
        logger.info("Đã làm mới dữ liệu bảng điểm.")
        self.load_data()

    # -------------------------------------------------- #
    # =============== Search / Filter ================== #
    # -------------------------------------------------- #

    def _on_search_change(self, event=None):
        """Lọc dữ liệu bảng điểm theo nội dung đang nhập ở ô tìm kiếm."""
        query = self.search_entry.get().strip()
        filtered_scores = self._filter_scores(self.all_scores, query)
        self._render_scores(filtered_scores)
        logger.info(
            "Đã lọc bảng điểm theo từ khóa '%s' (%s kết quả).",
            query if query else "(trống)",
            len(filtered_scores),
        )

    def _filter_scores(self, scores, query):
        """Lọc danh sách bảng điểm theo từ khóa nhập vào."""
        if not query:
            return list(scores)

        normalized_query = query.casefold()
        filtered_scores = []
        for score in scores:
            searchable_text = " ".join(str(value) for value in score).casefold()
            if normalized_query in searchable_text:
                filtered_scores.append(score)
        return filtered_scores

    def _render_scores(self, scores):
        """Đổ danh sách bảng điểm đã lọc lên Treeview."""
        for item in self.score_tree.get_children():
            self.score_tree.delete(item)

        for index, score in enumerate(scores, start=1):
            score_value = "Chưa có điểm" if score[4] == "Chưa có điểm" else score[3]
            row = (str(index), score[0], score[1], score[2], score_value, score[4])
            self.score_tree.insert("", "end", values=row)

        self.reindex_stt()

    def on_heading_click(self, column_name):
        """Xử lý khi bấm vào tiêu đề cột để sắp xếp."""
        self.sort_rows(column_name)

    def sort_rows(self, column_name):
        """Sắp xếp dữ liệu theo cột đã chọn."""
        if column_name not in self.sort_state:
            self.sort_state[column_name] = False
        self.sort_state[column_name] = not self.sort_state[column_name]
        reverse = self.sort_state[column_name]

        rows = [self.score_tree.item(row_id, "values") for row_id in self.score_tree.get_children()]
        rows.sort(key=lambda values: self.get_sort_key(values, column_name), reverse=reverse)

        for row_id in self.score_tree.get_children():
            self.score_tree.delete(row_id)

        for row in rows:
            self.score_tree.insert("", "end", values=tuple(row))

        self.reindex_stt()

    def reindex_stt(self):
        """Đánh lại STT theo thứ tự dòng hiện tại."""
        for index, row_id in enumerate(self.score_tree.get_children(), start=1):
            values = list(self.score_tree.item(row_id, "values"))
            values[0] = str(index)
            self.score_tree.item(row_id, values=values)

    def get_sort_key(self, values, column_name):
        """Tạo khóa sắp xếp phù hợp với từng cột."""
        columns = {
            "stt": 0,
            "student_id": 1,
            "student_name": 2,
            "class_name": 3,
            "score": 4,
            "grade": 5,
        }
        index = columns[column_name]
        value = values[index]

        if column_name == "stt":
            return int(value)
        if column_name == "score":
            if value == "Chưa có điểm":
                return -1.0
            try:
                return float(value)
            except ValueError:
                return 0.0
        if column_name == "grade":
            grade_order = {
                "Xuất sắc": 4,
                "Giỏi": 3,
                "Khá": 2,
                "Trung bình": 1,
                "Yếu": 0,
                "Chưa có điểm": -1,
            }
            return grade_order.get(value, -1)
        return str(value).casefold()

    def see_details(self):
        """Mở cửa sổ xem chi tiết của sinh viên đang chọn."""
        selected_item = self.score_tree.selection()
        if not selected_item:
            logger.warning("Người dùng bấm xem chi tiết nhưng chưa chọn dòng nào.")
            messagebox.showwarning("Chưa chọn dữ liệu", "Chưa chọn dòng nào để xem chi tiết.", parent=self)
            return

        values = self.score_tree.item(selected_item[0], "values")
        student_info = {
            "student_id": values[1],
            "student_name": values[2],
            "class_name": values[3],
        }
        # Mở ScoreDetailWindow từ app/views/windows/score_detail_window.py để xem chi tiết bảng điểm.
        logger.info("Đang mở chi tiết bảng điểm của sinh viên: %s.", student_info["student_id"])
        ScoreDetailWindow(
            self.winfo_toplevel(),
            self.database,
            student_info,
            on_change=self._refresh_after_score_change,
        )

    def _on_double_click(self, event):
        """Bấm đúp vào dòng để mở nhanh cửa sổ chi tiết."""
        row_id = self.score_tree.identify_row(event.y)
        column = self.score_tree.identify_column(event.x)
        if row_id and column != "#1":
            self.score_tree.selection_set(row_id)
            self.see_details()

    def export_csv(self):
        """Xuất dữ liệu bảng điểm ra file CSV."""
        file_path = filedialog.asksaveasfilename(
            title="Lưu file CSV bảng điểm",
            initialfile="bang_diem_tong_hop.csv",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            parent=self,
        )
        if not file_path:
            return

        try:
            exported_rows = self.controller.export_csv(file_path)
        except Exception as exc:
            logger.exception("Lỗi khi xuất CSV bảng điểm: %s", exc)
            messagebox.showerror("Lỗi xuất CSV", f"Không thể xuất file CSV:\n{exc}", parent=self)
            return

        logger.info("Đã xuất %s dòng bảng điểm ra file CSV.", exported_rows)
        messagebox.showinfo(
            "Xuất CSV",
            f"Đã xuất {exported_rows} dòng bảng điểm ra file CSV.",
            parent=self,
        )

    def _refresh_after_score_change(self):
        """Làm mới bảng điểm và yêu cầu dashboard/statistics cập nhật lại."""
        self.refresh_data()
        main_window = self.winfo_toplevel()
        refresh_stats_page = getattr(main_window, "refresh_stats_page", None)
        if callable(refresh_stats_page):
            refresh_stats_page()
        logger.info("Đã refresh bảng điểm và thống kê sau khi thay đổi điểm.")
