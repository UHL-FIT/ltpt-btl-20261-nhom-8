from __future__ import annotations

from tkinter import ttk

import customtkinter as ctk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from app.utils.logger import get_logger


logger = get_logger(__name__)


class StatsPage(ctk.CTkFrame):
    """Trang thống kê số liệu và biểu đồ kết quả học tập."""

    def __init__(self, parent, database):
        """Khởi tạo trang thống kê."""
        super().__init__(parent, fg_color="#F8FAFC", corner_radius=0)
        self.database = database
        logger.info("Khởi tạo StatsPage.")

        # Biến giữ biểu đồ Matplotlib để không tạo lại nhiều lần.
        self.chart_canvas: FigureCanvasTkAgg | None = None
        self.chart_figure: Figure | None = None

        self._create_widgets()

    def _create_widgets(self):
        """Tạo toàn bộ giao diện của trang thống kê."""
        # gọi các hàm tạo giao diện
        self._create_stat_cards()
        # Gọi hàm tạo thẻ số liệu thống kê
        self._create_content_area()
        # Gọi hàm tạo phần nội dung bên dưới thẻ số liệu thống kê
        self.refresh_data()
        # Gọi hàm làm mới dữ liệu sau khi tạo xong các thành phần

    # Hàm tạo thẻ số liệu thống kê
    def _create_stat_cards(self):
        """Tạo 4 thẻ thống kê ở phía trên."""
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        # Tạo frame (khung) chứa 4 thẻ thống kê
        self.cards_frame.pack(fill="x", padx=30)
        # Sắp xếp vị trí của khung thẻ số liệu thống kê

        # Tạo một vòng lặp for để gán vị trí có từng thẻ
        for column in range(4):
            self.cards_frame.grid_columnconfigure(column, weight=1)

        # Thẻ tổng số sinh viên
        # Gọi hàm tạo thẻ và truyền tham số vào hàm tạo thẻ
        self.total_students_card = self._create_stat_card(
            self.cards_frame,
            0,
            "👥",
            "Sinh viên",
            "0",
            "#6366F1",
            (0, 10),
        )
        # Thẻ tổng số học phần
        # Gọi hàm tạo thẻ và truyền tham số vào hàm tạo thẻ
        self.total_courses_card = self._create_stat_card(
            self.cards_frame,
            1,
            "📖",
            "Học phần",
            "0",
            "#A855F7",
            (10, 10),
        )
        # Thẻ điểm CPA trung bình
        # Gọi hàm tạo thẻ và truyền tham số vào hàm tạo thẻ
        self.avg_cpa_card = self._create_stat_card(
            self.cards_frame,
            2,
            "🏆",
            "CPA trung bình",
            "0.00",
            "#10B981",
            (10, 10),
        )
        # Thẻ điểm CPA cao nhất
        # Gọi hàm tạo thẻ và truyền tham số vào hàm tạo thẻ
        self.max_cpa_card = self._create_stat_card(
            self.cards_frame,
            3,
            "⭐",
            "CPA cao nhất",
            "0.00",
            "#F59E0B",
            (10, 0),
        )

    # Hàm tạo vùng nội dung bên dưới khung của 4 thẻ số liệu thống kê
    # vùng nội dung bên dưới gồm 2 vùng, vùng bên trái chứa biểu đồ tròn
    # vùng bên phải chứa bảng top 10 sinh viên có điểm CPA cao nhất
    def _create_content_area(self):
        """Tạo vùng nội dung phía dưới gồm biểu đồ và bảng top 10."""
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=(18, 24))
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1, uniform="stats")
        self.content_frame.grid_columnconfigure(1, weight=1, uniform="stats")

        # Khung bên trái: biểu đồ tròn.
        self.chart_card = ctk.CTkFrame(
            self.content_frame,
            fg_color="white",
            corner_radius=16,
            border_width=2,
            border_color="#2F74FF",
        )
        self.chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Khung bên phải: bảng top 10 CPA.
        self.top10_card = ctk.CTkFrame(
            self.content_frame,
            fg_color="white",
            corner_radius=16,
            border_width=2,
            border_color="#2F74FF",
        )
        self.top10_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self._create_chart_card()
        self._create_top10_card()

    # Hàm tạo thẻ số liệu thống kê
    def _create_stat_card(self, parent, column, icon, title, value, accent, padx):
        """Tạo một thẻ thống kê nhỏ."""
        card = ctk.CTkFrame(
            parent,
            fg_color="white",
            height=140,
            corner_radius=16,
            border_width=2,
            border_color="#2F74FF",
        )
        card.grid(row=0, column=column, sticky="nsew", padx=padx, pady=10)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)

        icon_label = ctk.CTkLabel(card, text=icon, font=("Arial", 26), text_color=accent)
        icon_label.grid(row=0, column=0, sticky="n", padx=20, pady=(18, 2))

        title_label = ctk.CTkLabel(card, text=title, font=("Arial", 18), text_color="#64748B")
        title_label.grid(row=1, column=0, sticky="n", padx=20, pady=(0, 4))

        value_label = ctk.CTkLabel(card, text=value, font=("Arial", 32, "bold"), text_color=accent)
        value_label.grid(row=2, column=0, sticky="n", padx=20, pady=(0, 18))

        return {"card": card, "value_label": value_label}

    # Hàm tạo thẻ biểu đồ tròn
    def _create_chart_card(self):
        """Tạo phần tiêu đề và vùng hiển thị biểu đồ."""
        title_label = ctk.CTkLabel(
            self.chart_card,
            text="Phân loại CPA",
            font=("Arial", 18, "bold"),
            text_color="#111827",
        )
        title_label.pack(anchor="w", padx=18, pady=(16, 6))

        self.chart_host = ctk.CTkFrame(
            self.chart_card, 
            fg_color="transparent"
        )
        self.chart_host.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _create_top10_card(self):
        """Tạo phần tiêu đề và bảng top 10 sinh viên CPA cao nhất."""
        title_label = ctk.CTkLabel(
            self.top10_card,
            text="Top 10 CPA cao nhất",
            font=("Arial", 18, "bold"),
            text_color="#111827",
        )
        title_label.pack(anchor="w", padx=18, pady=(16, 6))

        # Tạo khung bảng top 10 sinh viên có CPA cao nhất
        table_frame = ctk.CTkFrame(
            self.top10_card, 
            fg_color="white", 
            corner_radius=0
        )
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = (
            "stt", 
            "student_id", 
            "student_name", 
            "class_name", 
            "cpa", 
            "grade"
        )
        self.top10_tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="headings"
        )

        self._setup_top10_treeview_style()
        self._setup_top10_treeview_columns()

        y_scrollbar = ctk.CTkScrollbar(
            table_frame,
            orientation="vertical",
            command=self.top10_tree.yview,
            width=12,
            fg_color="#E5EDFF",
            button_color="#2F74FF",
            button_hover_color="#0050DB",
        )
        self.top10_tree.configure(yscrollcommand=y_scrollbar.set)

        self.top10_tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")

    # Hàm tạo style cho treeview (table) top 10 sinh viên có CPA cao nhất
    def _setup_top10_treeview_style(self):
        """Cấu hình giao diện cho bảng top 10."""
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Stats.Treeview",
            background="white",
            foreground="#111827",
            rowheight=36,
            fieldbackground="white",
            borderwidth=1,
            relief="solid",
            font=("Arial", 11),
        )
        style.configure(
            "Stats.Treeview.Heading",
            background="#2F74FF",
            foreground="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padding=(8, 10),
        )
        style.map(
            "Stats.Treeview",
            background=[("selected", "#DBEAFE")],
            foreground=[("selected", "#111827")],
        )
        style.map("Stats.Treeview.Heading", background=[("active", "#0050DB")])

        self.top10_tree.configure(style="Stats.Treeview")
        self.top10_tree["show"] = "headings"
        self.top10_tree.tag_configure("odd", background="#F8FAFC")

    # Hàm tọa cột cho treeview (bảng) top 10 sinh viên có CPA cao nhất
    def _setup_top10_treeview_columns(self):
        """Khai báo tiêu đề và độ rộng cho các cột của bảng top 10."""
        self.top10_tree.heading("stt", text="STT", anchor="center")
        self.top10_tree.heading("student_id", text="Mã SV", anchor="center")
        self.top10_tree.heading("student_name", text="Tên sinh viên", anchor="center")
        self.top10_tree.heading("class_name", text="Lớp", anchor="center")
        self.top10_tree.heading("cpa", text="CPA", anchor="center")
        self.top10_tree.heading("grade", text="Xếp loại", anchor="center")

        self.top10_tree.column("stt", width=60, minwidth=60, anchor="center", stretch=False)
        self.top10_tree.column("student_id", width=100, minwidth=80, anchor="center")
        self.top10_tree.column("student_name", width=190, minwidth=150, anchor="w")
        self.top10_tree.column("class_name", width=90, minwidth=70, anchor="center")
        self.top10_tree.column("cpa", width=80, minwidth=70, anchor="center")
        self.top10_tree.column("grade", width=100, minwidth=80, anchor="center")

    # Hàm làm mới dữ liệu
    def refresh_data(self):
        """Lấy dữ liệu mới nhất từ database và cập nhật giao diện."""
        scores = self.database.fetch_scores()
        students = self.database.fetch_students()
        courses = self.database.fetch_courses()
        logger.info(
            "Làm mới StatsPage: %s sinh viên, %s học phần, %s bản ghi điểm.",
            len(students),
            len(courses),
            len(scores),
        )

        scored_rows = self._get_scored_rows(scores)
        cpas = self._get_cpa_array(scored_rows)

        self.total_students_card["value_label"].configure(text=str(len(students)))
        self.total_courses_card["value_label"].configure(text=str(len(courses)))
        self.avg_cpa_card["value_label"].configure(text=f"{cpas.mean():.2f}" if cpas.size else "0.00")
        self.max_cpa_card["value_label"].configure(text=f"{cpas.max():.2f}" if cpas.size else "0.00")

        self._render_chart(scored_rows)
        self._render_top10(scored_rows)


    def _get_scored_rows(self, scores):
        """Lọc ra các sinh viên đã có điểm để dùng cho biểu đồ và top 10."""
        scored_rows = []
        for row in scores:
            if row[4] != "Chưa có điểm":
                scored_rows.append(row)
        return scored_rows

    def _get_cpa_array(self, scored_rows):
        """Chuyển danh sách CPA sang mảng NumPy để tính trung bình và max."""
        if not scored_rows:
            return np.array([], dtype=float)

        cpa_values = []
        for row in scored_rows:
            cpa_values.append(float(row[3]))
        return np.array(cpa_values, dtype=float)

    def _render_chart(self, scored_rows):
        """Vẽ lại biểu đồ tròn phân loại CPA."""
        if self.chart_canvas is None:
            self.chart_figure = Figure(figsize=(5.4, 4.0), dpi=100)
            self.chart_canvas = FigureCanvasTkAgg(self.chart_figure, master=self.chart_host)
            self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)

        assert self.chart_figure is not None
        self.chart_figure.clear()
        axes = self.chart_figure.add_subplot(111)

        if not scored_rows:
            axes.text(
                0.5,
                0.5,
                "Không có dữ liệu điểm",
                ha="center",
                va="center",
                fontsize=13,
            )
            axes.axis("off")
        else:
            self._draw_grade_pie_chart(axes, scored_rows)

        assert self.chart_canvas is not None
        self.chart_canvas.draw()

    def _draw_grade_pie_chart(self, axes, scored_rows):
        """Vẽ pie chart theo nhóm xếp loại CPA."""
        grades = []
        for row in scored_rows:
            grades.append(row[4])

        grade_order = ["Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu"]
        labels = []
        counts = []
        for grade in grade_order:
            count = grades.count(grade)
            if count:
                labels.append(grade)
                counts.append(count)

        colors = ["#8B5CF6", "#2F74FF", "#10B981", "#F59E0B", "#EF4444"]
        explode = [0.02 for _ in counts]

        axes.pie(
            counts,
            labels=labels,
            autopct="%1.0f%%",
            startangle=90,
            colors=colors[: len(counts)],
            explode=explode,
            textprops={"fontsize": 10},
        )
        axes.axis("equal")

    def _render_top10(self, scored_rows):
        """Làm mới bảng top 10 CPA cao nhất."""
        for item in self.top10_tree.get_children():
            self.top10_tree.delete(item)

        top10 = sorted(scored_rows, key=lambda row: float(row[3]), reverse=True)[:10]
        for index, row in enumerate(top10, start=1):
            values = (index, row[0], row[1], row[2], f"{float(row[3]):.2f}", row[4])
            self.top10_tree.insert("", "end", values=values)
