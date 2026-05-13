import customtkinter as ctk
from tkinter import messagebox
from utils.helpers import validate_empty, validate_date, validate_score

class StudentSubWindow(ctk.CTkToplevel):
    def __init__(self, master, controller, mode="add", student_data=None):
        super().__init__(master)
        self.controller = controller
        self.mode = mode
        
        title = "Thêm Sinh viên" if mode == "add" else "Sửa Sinh viên"
        self.title(title)
        self.geometry("400x450")
        
        # Biến lưu trữ
        self.ma_sv_var = ctk.StringVar(value=student_data[0] if student_data else "")
        self.ho_ten_var = ctk.StringVar(value=student_data[1] if student_data else "")
        self.gioi_tinh_var = ctk.StringVar(value=student_data[2] if student_data else "Nam")
        self.ngay_sinh_var = ctk.StringVar(value=student_data[3] if student_data else "")
        self.lop_var = ctk.StringVar(value=student_data[4] if student_data else "")

        # Form Layout
        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Mã SV:").grid(row=0, column=0, padx=10, pady=15, sticky="w")
        self.entry_ma_sv = ctk.CTkEntry(frame, textvariable=self.ma_sv_var, width=200)
        self.entry_ma_sv.grid(row=0, column=1, padx=10, pady=15)
        if mode == "edit": self.entry_ma_sv.configure(state="disabled")

        ctk.CTkLabel(frame, text="Họ Tên:").grid(row=1, column=0, padx=10, pady=15, sticky="w")
        ctk.CTkEntry(frame, textvariable=self.ho_ten_var, width=200).grid(row=1, column=1, padx=10, pady=15)

        ctk.CTkLabel(frame, text="Giới tính:").grid(row=2, column=0, padx=10, pady=15, sticky="w")
        ctk.CTkComboBox(frame, values=["Nam", "Nữ"], variable=self.gioi_tinh_var, width=200).grid(row=2, column=1, padx=10, pady=15)

        ctk.CTkLabel(frame, text="Ngày sinh\n(dd/mm/yyyy):").grid(row=3, column=0, padx=10, pady=15, sticky="w")
        ctk.CTkEntry(frame, textvariable=self.ngay_sinh_var, width=200).grid(row=3, column=1, padx=10, pady=15)

        ctk.CTkLabel(frame, text="Lớp:").grid(row=4, column=0, padx=10, pady=15, sticky="w")
        ctk.CTkEntry(frame, textvariable=self.lop_var, width=200).grid(row=4, column=1, padx=10, pady=15)

        btn_save = ctk.CTkButton(self, text="💾 Lưu", command=self.save_data)
        btn_save.pack(pady=10)
        
        self.grab_set() # Block main window

    def save_data(self):
        ma_sv = self.ma_sv_var.get()
        ho_ten = self.ho_ten_var.get()
        gioi_tinh = self.gioi_tinh_var.get()
        ngay_sinh = self.ngay_sinh_var.get()
        lop = self.lop_var.get()

        # Validation
        if not validate_empty(ma_sv, ho_ten, ngay_sinh, lop):
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
            
        if not validate_date(ngay_sinh):
            messagebox.showwarning("Lỗi", "Ngày sinh sai định dạng (dd/mm/yyyy)!")
            return

        if self.mode == "add":
            success = self.controller.student_model.add_student(ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop)
            if success:
                messagebox.showinfo("Thành công", "Đã thêm sinh viên!")
                self.controller.refresh_current_view()
                self.destroy()
            else:
                messagebox.showerror("Lỗi", "Mã SV đã tồn tại hoặc lỗi CSDL!")
        else:
            success = self.controller.student_model.update_student(ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop)
            if success:
                messagebox.showinfo("Thành công", "Đã cập nhật sinh viên!")
                self.controller.refresh_current_view()
                self.destroy()
            else:
                messagebox.showerror("Lỗi", "Lỗi CSDL!")

class ScoreSubWindow(ctk.CTkToplevel):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        
        self.title("Nhập Điểm Sinh Viên")
        self.geometry("400x450")
        
        self.ma_sv_var = ctk.StringVar()
        self.ma_hp_var = ctk.StringVar()
        self.hoc_ky_var = ctk.StringVar(value="HK1")
        self.nam_hoc_var = ctk.StringVar(value="2024-2025")
        self.diem_var = ctk.StringVar()

        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Mã SV:").grid(row=0, column=0, padx=10, pady=15, sticky="w")
        ctk.CTkEntry(frame, textvariable=self.ma_sv_var, width=200).grid(row=0, column=1, padx=10, pady=15)

        # Combo box môn học (lấy từ CSDL)
        subjects_dict = self.controller.subject_model.get_subject_dict()
        subject_list = [f"{k} - {v}" for k, v in subjects_dict.items()]
        
        ctk.CTkLabel(frame, text="Môn học:").grid(row=1, column=0, padx=10, pady=15, sticky="w")
        combo = ctk.CTkComboBox(frame, values=subject_list, width=200)
        combo.grid(row=1, column=1, padx=10, pady=15)
        if subject_list: combo.set(subject_list[0])

        ctk.CTkLabel(frame, text="Học kỳ:").grid(row=2, column=0, padx=10, pady=15, sticky="w")
        ctk.CTkComboBox(frame, values=["HK1", "HK2"], variable=self.hoc_ky_var, width=200).grid(row=2, column=1, padx=10, pady=15)

        ctk.CTkLabel(frame, text="Năm học:").grid(row=3, column=0, padx=10, pady=15, sticky="w")
        ctk.CTkEntry(frame, textvariable=self.nam_hoc_var, width=200).grid(row=3, column=1, padx=10, pady=15)

        ctk.CTkLabel(frame, text="Điểm (0-10):").grid(row=4, column=0, padx=10, pady=15, sticky="w")
        ctk.CTkEntry(frame, textvariable=self.diem_var, width=200).grid(row=4, column=1, padx=10, pady=15)

        btn_save = ctk.CTkButton(self, text="💾 Lưu Điểm", command=lambda: self.save_data(combo.get()))
        btn_save.pack(pady=10)
        
        self.grab_set()

    def save_data(self, selected_subject):
        ma_sv = self.ma_sv_var.get()
        ma_hp = selected_subject.split(" - ")[0] if " - " in selected_subject else ""
        hoc_ky = self.hoc_ky_var.get()
        nam_hoc = self.nam_hoc_var.get()
        diem = self.diem_var.get()

        if not validate_empty(ma_sv, ma_hp, hoc_ky, nam_hoc, diem):
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
            
        if not validate_score(diem):
            messagebox.showwarning("Lỗi", "Điểm phải là số từ 0 đến 10!")
            return

        success = self.controller.score_model.add_or_update_score(ma_sv, ma_hp, hoc_ky, nam_hoc, float(diem))
        if success:
            messagebox.showinfo("Thành công", "Đã lưu điểm thành công!")
            self.controller.refresh_current_view()
            self.destroy()
        else:
            messagebox.showerror("Lỗi", "Không thể lưu điểm (Kiểm tra lại Mã SV đã tồn tại chưa).")
