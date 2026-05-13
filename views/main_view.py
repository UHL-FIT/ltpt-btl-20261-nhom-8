import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

class MainView:
    def __init__(self, root: tk.Tk, controller):
        self.root = root
        self.controller = controller
        
        self.setup_ui()
        
    def setup_ui(self):
        # Toolbar / Buttons
        self.toolbar_frame = ttk.Frame(self.root, padding=10)
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Button(self.toolbar_frame, text="Thêm", command=self.controller.open_add_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.toolbar_frame, text="Sửa", command=self.controller.open_edit_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.toolbar_frame, text="Xóa", command=self.controller.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.toolbar_frame, text="Import CSV", command=self.controller.import_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.toolbar_frame, text="Export CSV", command=self.controller.export_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.toolbar_frame, text="Thống Kê", command=self.controller.open_stats_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.toolbar_frame, text="About", command=self.controller.show_about).pack(side=tk.LEFT, padx=5)
        
        # Search Frame
        self.search_frame = ttk.Frame(self.root, padding=10)
        self.search_frame.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(self.search_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.controller.search_data)
        ttk.Entry(self.search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Table
        self.table_frame = ttk.Frame(self.root, padding=10)
        self.table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        columns = ("MSSV", "HoTen", "GioiTinh", "GPA", "XepLoai")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.W)
            
        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Stats Label
        self.stats_frame = ttk.Frame(self.root, padding=10)
        self.stats_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.stats_label = ttk.Label(self.stats_frame, text="Tổng số: 0 | GPA Trung bình: 0.0")
        self.stats_label.pack(side=tk.LEFT)

    def get_selected_item(self):
        selection = self.tree.selection()
        if not selection:
            return None
        return self.tree.item(selection[0], "values")

    def show_error(self, message: str):
        messagebox.showerror("Lỗi", message)
        
    def show_info(self, title: str, message: str):
        messagebox.showinfo(title, message)
        
    def show_warning(self, title: str, message: str):
        messagebox.showwarning(title, message)
