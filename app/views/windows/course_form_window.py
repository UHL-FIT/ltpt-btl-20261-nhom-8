from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from app.utils.logger import get_logger


logger = get_logger(__name__)


class CourseFormWindow(ctk.CTkToplevel):
    """Cửa sổ nhập liệu để thêm hoặc sửa học phần."""

    def __init__(
        self,
        parent,
        database,
        title="Thêm học phần",
        course_data=None,
        on_save=None,
        course_id_editable=True,
    ):
        """Khởi tạo cửa sổ form học phần."""
        super().__init__(parent)
        self.database = database
        self.on_save = on_save
        self.course_data = course_data or {}
        self.course_id_editable = course_id_editable
        logger.info("Mở CourseFormWindow với chế độ: %s", title)

        self.title(title)
        self.geometry("480x380")
        self.minsize(480, 380)
        self.configure(fg_color="#F8FAFC")
        self.transient(parent)
        self.grab_set()

        self._center_window()
        self._create_widgets()
        self._fill_data()

    def _center_window(self):
        """Canh cửa sổ ra giữa màn hình."""
        self.update_idletasks()
        width = 480
        height = 380
        x = self.winfo_screenwidth() // 2 - width // 2
        y = self.winfo_screenheight() // 2 - height // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self):
        """Tạo toàn bộ giao diện của form học phần."""
        # Khung ngoài cùng có viền xanh.
        padding_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            border_width=2,
            border_color="#2F74FF",
        )
        padding_frame.pack(fill="both", expand=True)

        # Khung nội dung form.
        form_frame = ctk.CTkFrame(
            padding_frame,
            fg_color="transparent",
            corner_radius=16,
        )
        form_frame.pack(fill="both", expand=True, padx=25, pady=25)
        form_frame.grid_columnconfigure(1, weight=1)

        self.course_id_entry = self._create_entry_row(
            form_frame,
            0,
            "Mã học phần",
            "Ví dụ: HP001",
        )

        self.course_name_entry = self._create_entry_row(
            form_frame,
            1,
            "Tên học phần",
            "Ví dụ: Lập trình Python",
        )

        self.credits_entry = self._create_entry_row(
            form_frame,
            2,
            "Số tín chỉ",
            "Ví dụ: 3",
        )

        # Ô chọn học kỳ.
        ctk.CTkLabel(
            form_frame,
            text="Học kỳ",
            font=("Arial", 13, "bold"),
            text_color="#334155",
        ).grid(row=3, column=0, sticky="w", padx=(20, 14), pady=(14, 4))

        self.semester_combo = ctk.CTkComboBox(
            form_frame,
            values=["HK1", "HK2", "HK3", "HK4"],
            state="readonly",
            height=36,
            corner_radius=10,
            border_width=2,
            border_color="#2F74FF",
            fg_color="#F8FAFC",
            button_color="#2F74FF",
            button_hover_color="#0050DB",
        )
        self.semester_combo.grid(row=3, column=1, sticky="ew", padx=(0, 20), pady=(14, 4))

        # Khu vực nút chức năng.
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, columnspan=2, pady=(24, 18))

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Hủy",
            width=110,
            height=38,
            fg_color="#EA0000",
            hover_color="#B00000",
            corner_radius=10,
            command=self.destroy,
        )
        cancel_button.pack(side="left", padx=(10, 30))

        save_button = ctk.CTkButton(
            button_frame,
            text="Lưu",
            width=110,
            height=38,
            fg_color="#2F74FF",
            hover_color="#0050DB",
            corner_radius=10,
            command=self.submit_form,
        )
        save_button.pack(side="left")

    def _create_entry_row(self, parent, row, label_text, placeholder):
        """Tạo một dòng gồm nhãn và ô nhập."""
        ctk.CTkLabel(
            parent,
            text=label_text,
            font=("Arial", 13, "bold"),
            text_color="#334155",
        ).grid(row=row, column=0, sticky="w", padx=(20, 14), pady=(14, 4))

        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=36,
            corner_radius=10,
            border_width=2,
            border_color="#2F74FF",
            fg_color="#F8FAFC",
            text_color="#111827",
        )
        entry.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=(14, 4))
        return entry

    def _fill_data(self):
        """Điền dữ liệu có sẵn khi mở form ở chế độ sửa."""
        if not self.course_data:
            self.semester_combo.set("HK1")
            return

        self.course_id_entry.insert(0, self.course_data.get("course_id", ""))
        self.course_name_entry.insert(0, self.course_data.get("course_name", ""))
        self.credits_entry.insert(0, self.course_data.get("credits", ""))
        self.semester_combo.set(self.course_data.get("semester", "HK1"))

        if not self.course_id_editable:
            self.course_id_entry.configure(state="disabled")

    def _is_valid_course_id(self, value: str) -> bool:
        """Kiểm tra mã học phần phải có cả chữ và số."""
        value = value.strip()
        if not value or not value.isalnum():
            return False
        has_letter = any(char.isalpha() for char in value)
        has_digit = any(char.isdigit() for char in value)
        return has_letter and has_digit

    def _is_valid_course_name(self, value: str) -> bool:
        """Kiểm tra tên học phần chỉ gồm chữ cái và khoảng trắng."""
        value = value.strip()
        if not value:
            return False
        for part in value.split():
            if not part.isalpha():
                return False
        return True

    def _is_valid_credits(self, value: str) -> bool:
        """Kiểm tra số tín chỉ nằm trong khoảng hợp lệ."""
        if not value.isdigit():
            return False
        credits = int(value)
        return 1 <= credits <= 30

    def _is_valid_semester(self, value: str) -> bool:
        """Kiểm tra học kỳ có thuộc danh sách cho phép hay không."""
        return value in {"HK1", "HK2", "HK3", "HK4"}

    def _normalize_course_data(self, data):
        """Chuẩn hóa dữ liệu trước khi gửi xuống database."""
        return {
            "course_id": data["course_id"].strip().upper(),
            "course_name": " ".join(data["course_name"].strip().split()),
            "credits": data["credits"].strip(),
            "semester": data["semester"].strip().upper(),
        }

    def _validate_form(self, data, original_course_id=None):
        """Kiểm tra dữ liệu form trước khi lưu."""
        course_id = data["course_id"]
        course_name = data["course_name"]
        credits = data["credits"]
        semester = data["semester"]

        if not course_id:
            return False, "Mã học phần không được để trống."
        if not course_name:
            return False, "Tên học phần không được để trống."
        if not credits:
            return False, "Số tín chỉ không được để trống."
        if not semester:
            return False, "Học kỳ không được để trống."

        if not self._is_valid_course_id(course_id):
            return False, "Mã học phần phải có cả chữ và số, không chứa ký tự đặc biệt."
        if not self._is_valid_course_name(course_name):
            return False, "Tên học phần chỉ được chứa chữ cái và khoảng trắng."
        if not self._is_valid_credits(credits):
            return False, "Số tín chỉ phải là số nguyên dương từ 1 đến 30."
        if not self._is_valid_semester(semester):
            return False, "Học kỳ chỉ được là HK1, HK2, HK3 hoặc HK4."

        existing_course = self.database.fetch_course(course_id)
        original_course_id = str(original_course_id or "").strip().upper()
        if existing_course and course_id != original_course_id:
            return False, "Mã học phần đã tồn tại."

        return True, ""

    def submit_form(self):
        """Kiểm tra form rồi gửi dữ liệu cho hàm xử lý bên ngoài."""
        raw_data = {
            "course_id": self.course_id_entry.get().strip(),
            "course_name": self.course_name_entry.get().strip(),
            "credits": self.credits_entry.get().strip(),
            "semester": self.semester_combo.get().strip(),
        }

        original_course_id = self.course_data.get("course_id")
        is_valid, error_message = self._validate_form(raw_data, original_course_id)
        if not is_valid:
            messagebox.showwarning("Thiếu dữ liệu", error_message, parent=self)
            return

        data = self._normalize_course_data(raw_data)
        if self.on_save:
            self.on_save(data)
            logger.info("Đã lưu học phần qua CourseFormWindow: %s", data.get("course_id", ""))
        self.destroy()
