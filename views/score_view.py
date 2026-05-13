import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import threading
import pandas as pd
from views.sub_windows import ScoreSubWindow

class ScoreView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Toolbar trên cùng ---
        self.toolbar = ctk.CTkFrame(self, height=50)
        self.toolbar.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.lbl_title = ctk.CTkLabel(self.toolbar, text="Quản lý Bảng điểm", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.pack(side="left", padx=20, pady=10)

        # Nút chức năng
        self.btn_add = ctk.CTkButton(self.toolbar, text="➕ Nhập Điểm", width=100, command=self.on_add)
        self.btn_add.pack(side="right", padx=5, pady=10)
        
        self.btn_delete = ctk.CTkButton(self.toolbar, text="🗑️ Xóa", width=80, fg_color="#D9534F", hover_color="#C9302C", command=self.on_delete)
        self.btn_delete.pack(side="right", padx=5, pady=10)

        self.btn_export = ctk.CTkButton(self.toolbar, text="📤 Export CSV", width=100, command=self.on_export)
        self.btn_export.pack(side="right", padx=5, pady=10)

        self.btn_import = ctk.CTkButton(self.toolbar, text="📥 Import CSV", width=100, command=self.on_import)
        self.btn_import.pack(side="right", padx=5, pady=10)

        # --- Dashboard Tìm kiếm ---
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=1, column=0, padx=20, pady=0, sticky="ew")
        
        self.search_var = ctk.StringVar()
        self.entry_search = ctk.CTkEntry(self.search_frame, textvariable=self.search_var, placeholder_text="Nhập Mã SV hoặc Tên môn để tìm...", width=300)
        self.entry_search.pack(side="left", padx=20, pady=10)
        
        self.btn_search = ctk.CTkButton(self.search_frame, text="🔍 Tìm kiếm", width=100, command=self.refresh_data)
        self.btn_search.pack(side="left", padx=5, pady=10)
        
        self.btn_clear = ctk.CTkButton(self.search_frame, text="Xóa lọc", width=80, fg_color="gray", hover_color="darkgray", command=self.clear_search)
        self.btn_clear.pack(side="left", padx=5, pady=10)

        # Nhãn thống kê
        self.lbl_total = ctk.CTkLabel(self.search_frame, text="Tổng số bản ghi: 0", font=ctk.CTkFont(weight="bold"))
        self.lbl_total.pack(side="right", padx=20, pady=10)

        # --- Bảng dữ liệu ---
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        columns = ("MaSV", "HoTen", "MaHocPhan", "TenHocPhan", "HocKy", "NamHoc", "Diem")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        
        self.tree.heading("MaSV", text="Mã SV")
        self.tree.heading("HoTen", text="Họ tên")
        self.tree.heading("MaHocPhan", text="Mã HP")
        self.tree.heading("TenHocPhan", text="Tên HP")
        self.tree.heading("HocKy", text="Học kỳ")
        self.tree.heading("NamHoc", text="Năm học")
        self.tree.heading("Diem", text="Điểm")

        self.tree.column("MaSV", width=80, anchor="center")
        self.tree.column("HoTen", width=150)
        self.tree.column("MaHocPhan", width=80, anchor="center")
        self.tree.column("TenHocPhan", width=150)
        self.tree.column("HocKy", width=80, anchor="center")
        self.tree.column("NamHoc", width=100, anchor="center")
        self.tree.column("Diem", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def clear_search(self):
        self.search_var.set("")
        self.refresh_data()

    def refresh_data(self):
        search_term = self.search_var.get().strip()
        df = self.controller.score_model.get_all_scores(search_term)
        self.populate_table(df)

    def populate_table(self, df):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=(
                row['MaSV'], row['HoTen'], row['MaHocPhan'], 
                row['TenHocPhan'], row['HocKy'], row['NamHoc'], row['Diem']
            ))
            
        self.lbl_total.configure(text=f"Tổng số bản ghi điểm: {len(df)}")

    def on_add(self):
        ScoreSubWindow(self.winfo_toplevel(), self.controller)

    def on_delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn 1 dòng để xóa!")
            return
            
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa bản ghi điểm này?"):
            item = self.tree.item(selected[0])
            ma_sv = item['values'][0]
            ma_hp = item['values'][2]
            success = self.controller.score_model.delete_score(ma_sv, ma_hp)
            if success:
                messagebox.showinfo("Thành công", "Đã xóa điểm.")
                self.refresh_data()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa điểm.")

    def on_export(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", 
            filetypes=[("CSV files", "*.csv")],
            title="Lưu file CSV"
        )
        if file_path:
            # Export tất cả không phân biệt đang search hay không
            df = self.controller.score_model.get_all_scores("")
            df_export = df[['MaSV', 'MaHocPhan', 'HocKy', 'NamHoc', 'Diem']]
            df_export.to_csv(file_path, index=False)
            messagebox.showinfo("Thành công", "Đã xuất dữ liệu ra CSV.")

    def on_import(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")],
            title="Chọn file CSV để nhập"
        )
        if not file_path: return

        loading = ctk.CTkToplevel(self)
        loading.title("Đang xử lý")
        loading.geometry("300x100")
        loading.attributes("-topmost", True)
        ctk.CTkLabel(loading, text="Đang nhập dữ liệu từ CSV, vui lòng chờ...").pack(pady=20)
        
        def task():
            success, msg = self.controller.score_model.import_scores_from_csv(file_path)
            self.after(0, loading.destroy)
            if success:
                self.after(0, lambda: messagebox.showinfo("Thành công", msg))
                self.after(0, self.refresh_data)
            else:
                self.after(0, lambda: messagebox.showerror("Lỗi", f"Import thất bại:\n{msg}"))

        threading.Thread(target=task, daemon=True).start()
