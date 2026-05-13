import customtkinter as ctk
from tkinter import ttk, messagebox
from views.sub_windows import StudentSubWindow

class StudentView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Toolbar trên cùng ---
        self.toolbar = ctk.CTkFrame(self, height=50)
        self.toolbar.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.lbl_title = ctk.CTkLabel(self.toolbar, text="Danh sách Sinh viên", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.pack(side="left", padx=20, pady=10)

        # Nút chức năng (bên phải)
        self.btn_add = ctk.CTkButton(self.toolbar, text="➕ Thêm", width=80, command=self.on_add)
        self.btn_add.pack(side="right", padx=5, pady=10)

        self.btn_edit = ctk.CTkButton(self.toolbar, text="✏️ Sửa", width=80, command=self.on_edit)
        self.btn_edit.pack(side="right", padx=5, pady=10)

        self.btn_delete = ctk.CTkButton(self.toolbar, text="🗑️ Xóa", width=80, fg_color="#D9534F", hover_color="#C9302C", command=self.on_delete)
        self.btn_delete.pack(side="right", padx=5, pady=10)

        # --- Thanh Tìm kiếm ---
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=1, column=0, padx=20, pady=0, sticky="ew")
        
        self.search_var = ctk.StringVar()
        self.entry_search = ctk.CTkEntry(self.search_frame, textvariable=self.search_var, placeholder_text="Nhập Mã SV hoặc Tên để tìm...", width=300)
        self.entry_search.pack(side="left", padx=20, pady=10)
        
        self.btn_search = ctk.CTkButton(self.search_frame, text="🔍 Tìm kiếm", width=100, command=self.refresh_data)
        self.btn_search.pack(side="left", padx=5, pady=10)
        
        self.btn_clear = ctk.CTkButton(self.search_frame, text="Xóa lọc", width=80, fg_color="gray", hover_color="darkgray", command=self.clear_search)
        self.btn_clear.pack(side="left", padx=5, pady=10)

        # --- Bảng dữ liệu (Treeview) ---
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=30, fieldbackground="#2b2b2b", borderwidth=0)
        style.map("Treeview", background=[("selected", "#1f538d")])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", font=('Arial', 10, 'bold'))

        columns = ("MaSV", "HoTen", "GioiTinh", "NgaySinh", "Lop", "GPA", "XepLoai")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        
        self.tree.heading("MaSV", text="Mã SV")
        self.tree.heading("HoTen", text="Họ tên")
        self.tree.heading("GioiTinh", text="Giới tính")
        self.tree.heading("NgaySinh", text="Ngày sinh")
        self.tree.heading("Lop", text="Lớp")
        self.tree.heading("GPA", text="GPA")
        self.tree.heading("XepLoai", text="Xếp loại")

        self.tree.column("MaSV", width=80, anchor="center")
        self.tree.column("HoTen", width=180)
        self.tree.column("GioiTinh", width=80, anchor="center")
        self.tree.column("NgaySinh", width=100, anchor="center")
        self.tree.column("Lop", width=100, anchor="center")
        self.tree.column("GPA", width=60, anchor="center")
        self.tree.column("XepLoai", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # --- Footer Thống kê ---
        self.footer_frame = ctk.CTkFrame(self, height=30, fg_color="transparent")
        self.footer_frame.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.lbl_stats = ctk.CTkLabel(self.footer_frame, text="Tổng số: 0 sinh viên | GPA trung bình: 0.0", font=ctk.CTkFont(slant="italic"))
        self.lbl_stats.pack(side="left", padx=10)

    def clear_search(self):
        self.search_var.set("")
        self.refresh_data()

    def refresh_data(self):
        search_term = self.search_var.get().strip()
        df = self.controller.student_model.get_all_students_with_gpa(search_term)
        self.populate_table(df)

    def populate_table(self, df):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        for _, row in df.iterrows():
            # Formatting GPA
            gpa_str = f"{row['GPA']:.2f}" if row['GPA'] > 0 else "-"
            self.tree.insert("", "end", values=(
                row['MaSV'], row['HoTen'], row['GioiTinh'], 
                row['NgaySinh'], row['Lop'], gpa_str, row['XepLoai']
            ))
            
        # Cập nhật Footer
        total_students = len(df)
        avg_gpa = df[df['GPA'] > 0]['GPA'].mean() if total_students > 0 else 0
        avg_gpa_str = f"{avg_gpa:.2f}" if not pd.isna(avg_gpa) else "0.00"
        self.lbl_stats.configure(text=f"Tổng số: {total_students} sinh viên | GPA trung bình trường: {avg_gpa_str}")

    def on_add(self):
        StudentSubWindow(self.winfo_toplevel(), self.controller, mode="add")

    def on_edit(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn 1 dòng để sửa!")
            return
        if len(selected) > 1:
            messagebox.showwarning("Cảnh báo", "Chỉ được chọn 1 dòng để sửa!")
            return
            
        item = self.tree.item(selected[0])
        student_data = item['values']
        StudentSubWindow(self.winfo_toplevel(), self.controller, mode="edit", student_data=student_data)

    def on_delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn 1 dòng để xóa!")
            return
            
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa sinh viên này? Toàn bộ điểm liên quan cũng sẽ bị xóa."):
            item = self.tree.item(selected[0])
            ma_sv = item['values'][0]
            success = self.controller.student_model.delete_student(ma_sv)
            if success:
                messagebox.showinfo("Thành công", "Đã xóa sinh viên.")
                self.refresh_data()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa sinh viên.")
