import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StatsView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Toolbar ---
        self.toolbar = ctk.CTkFrame(self, height=50)
        self.toolbar.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.lbl_title = ctk.CTkLabel(self.toolbar, text="Thống kê Xếp loại & Top Sinh viên", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.pack(side="left", padx=20, pady=10)

        self.btn_refresh = ctk.CTkButton(self.toolbar, text="🔄 Làm mới Data", width=120, command=self.refresh_data)
        self.btn_refresh.pack(side="right", padx=20, pady=10)

        # --- Main Content ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1) # Bảng Top 10
        self.content_frame.grid_columnconfigure(1, weight=1) # Biểu đồ
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Bảng Top 10 GPA
        self.top_frame = ctk.CTkFrame(self.content_frame)
        self.top_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        ctk.CTkLabel(self.top_frame, text="🏆 Top 10 Sinh viên Xuất sắc nhất", font=ctk.CTkFont(weight="bold", size=16), text_color="#FFD700").pack(pady=10)
        
        columns = ("Rank", "MaSV", "HoTen", "GPA", "XepLoai")
        self.tree = ttk.Treeview(self.top_frame, columns=columns, show="headings")
        self.tree.heading("Rank", text="Top")
        self.tree.heading("MaSV", text="Mã SV")
        self.tree.heading("HoTen", text="Họ tên")
        self.tree.heading("GPA", text="GPA")
        self.tree.heading("XepLoai", text="Xếp loại")

        self.tree.column("Rank", width=50, anchor="center")
        self.tree.column("MaSV", width=80, anchor="center")
        self.tree.column("HoTen", width=150)
        self.tree.column("GPA", width=60, anchor="center")
        self.tree.column("XepLoai", width=80, anchor="center")

        # Đánh dấu màu nổi bật cho top 1, 2, 3
        self.tree.tag_configure("top1", background="#FFD700", foreground="black") # Vàng
        self.tree.tag_configure("top2", background="#C0C0C0", foreground="black") # Bạc
        self.tree.tag_configure("top3", background="#CD7F32", foreground="black") # Đồng

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Vùng vẽ biểu đồ
        self.chart_frame = ctk.CTkFrame(self.content_frame)
        self.chart_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        self.canvas_widget = None

    def refresh_data(self):
        # 1. Cập nhật bảng Top 10
        top_df = self.controller.score_model.get_top_students(limit=10)
        
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        rank = 1
        for _, row in top_df.iterrows():
            tags = ()
            if rank == 1: tags = ("top1",)
            elif rank == 2: tags = ("top2",)
            elif rank == 3: tags = ("top3",)
            
            self.tree.insert("", "end", values=(rank, row['MaSV'], row['HoTen'], f"{row['GPA']:.2f}", row['XepLoai']), tags=tags)
            rank += 1
            
        # 2. Cập nhật biểu đồ thống kê xếp loại
        class_stats = self.controller.score_model.get_classification_stats()
        self.draw_chart(class_stats)

    def draw_chart(self, class_stats):
        if self.canvas_widget:
            self.canvas_widget.destroy()

        if not class_stats:
            ctk.CTkLabel(self.chart_frame, text="Chưa có dữ liệu để vẽ biểu đồ").pack(pady=50)
            return

        labels = list(class_stats.keys())
        sizes = list(class_stats.values())
        
        # Gán màu cố định cho từng loại để nhìn biểu đồ chuyên nghiệp hơn
        color_map = {
            "Giỏi": "#2ecc71",       # Xanh lá
            "Khá": "#3498db",        # Xanh dương
            "Trung bình": "#f1c40f", # Vàng
            "Yếu": "#e74c3c"         # Đỏ
        }
        colors = [color_map.get(label, "#95a5a6") for label in labels]

        # Cấu hình Matplotlib sử dụng background tối/sáng tùy theo theme CustomTkinter
        is_dark = ctk.get_appearance_mode() == "Dark"
        bg_color = "#2b2b2b" if is_dark else "#ebebeb"
        text_color = "white" if is_dark else "black"

        fig, ax = plt.subplots(figsize=(4, 3), dpi=100, facecolor=bg_color)
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
            startangle=140, textprops={'color': text_color}
        )
        ax.axis('equal')  
        ax.set_title("Tỷ lệ Phân loại Học lực", color=text_color, pad=20, fontsize=14, fontweight='bold')

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)
