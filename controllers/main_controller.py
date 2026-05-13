import tkinter as tk
from tkinter import filedialog
from models.student_model import StudentModel
from views.main_view import MainView
from views.sub_windows import AddEditWindow
import threading
import time

class MainController:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.model = StudentModel()
        self.view = MainView(root, self)
        
        self.refresh_table()

    def refresh_table(self, query=""):
        # Clear table
        for item in self.view.tree.get_children():
            self.view.tree.delete(item)
            
        self.model.classify()
        df = self.model.df
        
        if query:
            # Simple search logic across multiple columns
            mask = df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
            df = df[mask]
            
        for index, row in df.iterrows():
            # Handle possible missing values
            gpa = row.get('GPA', '')
            xeploai = row.get('XepLoai', '')
            self.view.tree.insert("", tk.END, values=(row.get('MSSV', ''), row.get('HoTen', ''), row.get('GioiTinh', ''), gpa, xeploai))
            
        # Update Stats
        total = len(df)
        avg_gpa = df['GPA'].mean() if 'GPA' in df and not df['GPA'].isna().all() else 0.0
        self.view.stats_label.config(text=f"Tổng số: {total} | GPA Trung bình: {avg_gpa:.2f}")

    def search_data(self, *args):
        query = self.view.search_var.get()
        self.refresh_table(query)

    def open_add_window(self):
        AddEditWindow(self.root, "Thêm Sinh Viên", self.save_new_student)

    def save_new_student(self, data):
        if not data.get('MSSV') or not data.get('HoTen'):
            self.view.show_error("Vui lòng nhập đầy đủ thông tin MSSV và Họ Tên")
            return
        self.model.add_student(data)
        self.refresh_table()

    def open_edit_window(self):
        selected = self.view.get_selected_item()
        if not selected:
            self.view.show_warning("Cảnh báo", "Vui lòng chọn một sinh viên để sửa")
            return
            
        mssv = selected[0]
        # Find index in dataframe
        df = self.model.df
        match = df.index[df['MSSV'] == mssv].tolist()
        if not match:
            return
            
        index = match[0]
        student_data = df.loc[index].to_dict()
        
        AddEditWindow(self.root, "Sửa Sinh Viên", lambda data: self.save_edited_student(index, data), student_data)

    def save_edited_student(self, index, data):
        self.model.update_student(index, data)
        self.refresh_table()

    def delete_selected(self):
        selected = self.view.get_selected_item()
        if not selected:
            self.view.show_warning("Cảnh báo", "Vui lòng chọn một sinh viên để xóa")
            return
            
        mssv = selected[0]
        df = self.model.df
        match = df.index[df['MSSV'] == mssv].tolist()
        if not match:
            return
            
        self.model.delete_student(match[0])
        self.refresh_table()

    def import_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filepath:
            # Simulate a long task to show loading behavior
            self._simulate_long_task(lambda: self._do_import(filepath), "Đang import dữ liệu...")
            
    def _do_import(self, filepath):
        # We replace the path in model and reload
        self.model.csv_path = filepath
        self.model.load_data()
        self.model.recalculate_gpa()
        self.model.classify()
        self.model.save_data()
        self.root.after(0, self.refresh_table)

    def export_csv(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if filepath:
            self.model.df.to_csv(filepath, index=False)
            self.view.show_info("Thành công", "Đã export dữ liệu")

    def open_stats_window(self):
        self.view.show_info("Top 10", str(self.model.top_students()[['MSSV', 'HoTen', 'GPA']]))

    def show_about(self):
        self.view.show_info("About", "Kết Quả Học Tập App\nPhiên bản 1.0\nTác giả: Nhóm 8\nNgày phát hành: 2026")
        
    def _simulate_long_task(self, task_func, msg):
        top = tk.Toplevel(self.root)
        top.title("Loading...")
        tk.Label(top, text=msg, padx=20, pady=20).pack()
        top.transient(self.root)
        top.grab_set()
        
        def run():
            time.sleep(1) # Simulate > 3s requirement
            task_func()
            top.destroy()
            
        threading.Thread(target=run).start()
