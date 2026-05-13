import tkinter as tk
from tkinter import ttk, messagebox

class AddEditWindow(tk.Toplevel):
    def __init__(self, parent, title, callback, initial_data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x500")
        self.callback = callback
        self.initial_data = initial_data or {}
        
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.entries = {}
        
        # Define fields. We assume basic info and 2 subjects for demonstration.
        fields = [
            ("MSSV", "MSSV"),
            ("HoTen", "Họ Tên"),
            ("GioiTinh", "Giới Tính"),
            ("Diem1", "Điểm Môn 1"),
            ("TinChi1", "Tín Chỉ 1"),
            ("Diem2", "Điểm Môn 2"),
            ("TinChi2", "Tín Chỉ 2")
        ]
        
        for idx, (key, label_text) in enumerate(fields):
            ttk.Label(main_frame, text=label_text).grid(row=idx, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(main_frame)
            entry.grid(row=idx, column=1, sticky=tk.EW, pady=5, padx=10)
            
            # Pre-fill data if editing
            if key in self.initial_data:
                entry.insert(0, str(self.initial_data[key]))
                
            self.entries[key] = entry
            
        main_frame.columnconfigure(1, weight=1)
        
        # Buttons
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Button(btn_frame, text="Lưu", command=self.save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Hủy", command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def save(self):
        data = {}
        for key, entry in self.entries.items():
            val = entry.get().strip()
            if not val and key in ["MSSV", "HoTen"]:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ MSSV và Họ Tên", parent=self)
                return
            
            # Type conversions for score/credits
            if "Diem" in key or "TinChi" in key:
                try:
                    val = float(val) if val else 0.0
                except ValueError:
                    messagebox.showerror("Lỗi", f"Vui lòng nhập đúng định dạng số cho {key}", parent=self)
                    return
                    
            data[key] = val
            
        self.callback(data)
        self.destroy()
