from __future__ import annotations

import calendar
import re
from datetime import date, datetime
from tkinter import messagebox, ttk

import customtkinter as ctk

from app.utils.logger import get_logger


logger = get_logger(__name__)


class DatePickerWindow(ctk.CTkToplevel):
    """Cửa sổ nhỏ để chọn ngày sinh."""

    def __init__(self, parent, on_select):
        """Khởi tạo cửa sổ chọn ngày."""
        super().__init__(parent)
        self.on_select = on_select

        self.title("Chọn ngày sinh")
        self.resizable(False, False)
        self.configure(fg_color="#F8FAFC")
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()

        self._center_window()
        self._create_widgets()

    def _center_window(self):
        """Canh cửa sổ vào giữa màn hình."""
        self.update_idletasks()
        width = 400
        height = 300
        x = self.winfo_screenwidth() // 2 - width // 2
        y = self.winfo_screenheight() // 2 - height // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self):
        """Tạo giao diện cho hộp chọn ngày."""
        body = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=16,
            border_width=1,
            border_color="#D7E3FF",
        )
        body.pack(fill="both", expand=True, padx=18, pady=16)
        body.grid_columnconfigure((0, 1, 2), weight=1)

        today = date.today()
        years = [str(year) for year in range(today.year - 16, today.year - 50 - 1, -1)]
        months = [f"{month:02d}" for month in range(1, 13)]

        # Ba cột chọn ngày, tháng, năm.
        ctk.CTkLabel(body, text="Ngày", font=("Arial", 13, "bold"), text_color="#334155").grid(
            row=0, column=0, sticky="w", padx=(18, 10), pady=(18, 8)
        )
        ctk.CTkLabel(body, text="Tháng", font=("Arial", 13, "bold"), text_color="#334155").grid(
            row=0, column=1, sticky="w", padx=(10, 10), pady=(18, 8)
        )
        ctk.CTkLabel(body, text="Năm", font=("Arial", 13, "bold"), text_color="#334155").grid(
            row=0, column=2, sticky="w", padx=(10, 18), pady=(18, 8)
        )

        self.day_box = ttk.Combobox(body, state="readonly", width=10)
        self.month_box = ttk.Combobox(body, values=months, state="readonly", width=10)
        self.year_box = ttk.Combobox(body, values=years, state="readonly", width=12)
        self.day_box.grid(row=1, column=0, sticky="ew", padx=(18, 10), pady=(0, 16))
        self.month_box.grid(row=1, column=1, sticky="ew", padx=(10, 10), pady=(0, 16))
        self.year_box.grid(row=1, column=2, sticky="ew", padx=(10, 18), pady=(0, 16))

        self.day_box.bind("<<ComboboxSelected>>", self._on_month_or_year_change)
        self.month_box.bind("<<ComboboxSelected>>", self._on_month_or_year_change)
        self.year_box.bind("<<ComboboxSelected>>", self._on_month_or_year_change)

        self.month_box.set(f"{today.month:02d}")
        self.year_box.set(str(today.year - 16))
        self._update_day_values(preferred_day=today.day)

        hint_label = ctk.CTkLabel(
            body,
            text="Ngày sẽ tự đổi theo tháng và năm đã chọn",
            font=("Arial", 11),
            text_color="#64748B",
        )
        hint_label.grid(row=2, column=0, columnspan=3, pady=(0, 14))

        button_frame = ctk.CTkFrame(body, fg_color="transparent")
        button_frame.grid(row=3, column=0, columnspan=3, pady=(6, 18))

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Hủy",
            width=90,
            height=34,
            fg_color="#64748B",
            hover_color="#475569",
            corner_radius=10,
            command=self.destroy,
        )
        cancel_button.pack(side="left", padx=(10, 30))

        select_button = ctk.CTkButton(
            button_frame,
            text="Chọn",
            width=90,
            height=34,
            fg_color="#2F74FF",
            hover_color="#0050DB",
            corner_radius=10,
            command=self._confirm,
        )
        select_button.pack(side="left")

    def _on_month_or_year_change(self, _event=None):
        """Cập nhật lại danh sách ngày khi đổi tháng hoặc năm."""
        current_day = int(self.day_box.get()) if self.day_box.get().isdigit() else 1
        self._update_day_values(preferred_day=current_day)

    def _update_day_values(self, preferred_day=1):
        """Tính số ngày hợp lệ theo tháng và năm đang chọn."""
        month_text = self.month_box.get() or "01"
        year_text = self.year_box.get() or str(date.today().year)
        month = int(month_text)
        year = int(year_text)
        max_day = calendar.monthrange(year, month)[1]
        days = [f"{day:02d}" for day in range(1, max_day + 1)]
        self.day_box.configure(values=days)
        self.day_box.set(f"{min(preferred_day, max_day):02d}")

    def _confirm(self):
        """Trả ngày đã chọn về form sinh viên."""
        value = f"{self.day_box.get()}/{self.month_box.get()}/{self.year_box.get()}"
        self.on_select(value)
        self.destroy()


class StudentFormWindow(ctk.CTkToplevel):
    """Cửa sổ nhập liệu để thêm hoặc sửa sinh viên."""

    def __init__(
        self,
        parent,
        database,
        title="Thêm sinh viên",
        student_data=None,
        on_save=None,
        student_id_editable=True,
    ):
        """Khởi tạo form sinh viên."""
        super().__init__(parent)
        self.database = database
        self.on_save = on_save
        self.student_data = student_data or {}
        self.student_id_editable = student_id_editable
        logger.info("Mở StudentFormWindow với chế độ: %s", title)

        self.title(title)
        self.geometry("480x500")
        self.minsize(480, 480)
        self.configure(fg_color="#F8FAFC")
        self.transient(parent)
        self.grab_set()

        self._center_window()
        self._create_widgets()
        self._fill_data()

    def _center_window(self):
        """Canh cửa sổ form vào giữa màn hình."""
        self.update_idletasks()
        width = 480
        height = 480
        x = self.winfo_screenwidth() // 2 - width // 2
        y = self.winfo_screenheight() // 2 - height // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self):
        """Tạo toàn bộ giao diện của form sinh viên."""
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

        self.student_id_entry = self._create_entry_row(
            form_frame,
            0,
            "Mã sinh viên",
            "Ví dụ: SV001",
        )
        self.student_name_entry = self._create_entry_row(
            form_frame,
            1,
            "Họ tên",
            "Ví dụ: Nguyễn Văn A",
        )
        self.class_name_entry = self._create_entry_row(
            form_frame,
            2,
            "Lớp",
            "Ví dụ: CNTT01",
        )

        # Ô chọn giới tính.
        ctk.CTkLabel(
            form_frame,
            text="Giới tính",
            font=("Arial", 13, "bold"),
            text_color="#334155",
        ).grid(row=3, column=0, sticky="w", padx=(20, 14), pady=(14, 4))

        self.gender_combo = ctk.CTkComboBox(
            form_frame,
            values=["Nam", "Nữ"],
            state="readonly",
            height=36,
            corner_radius=10,
            border_width=2,
            border_color="#2F74FF",
            fg_color="#F8FAFC",
            button_color="#2F74FF",
            button_hover_color="#0050DB",
        )
        self.gender_combo.grid(row=3, column=1, sticky="ew", padx=(0, 20), pady=(14, 4))

        # Ô chọn ngày sinh.
        ctk.CTkLabel(
            form_frame,
            text="Ngày sinh",
            font=("Arial", 13, "bold"),
            text_color="#334155",
        ).grid(row=4, column=0, sticky="w", padx=(20, 14), pady=(14, 4))

        birth_date_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        birth_date_frame.grid(row=4, column=1, sticky="ew", padx=(0, 20), pady=(14, 4))
        birth_date_frame.grid_columnconfigure(0, weight=1)

        self.birth_date_entry = ctk.CTkEntry(
            birth_date_frame,
            placeholder_text="dd/mm/yyyy",
            height=36,
            corner_radius=10,
            border_width=2,
            border_color="#2F74FF",
            fg_color="#F8FAFC",
            text_color="#111827",
        )
        self.birth_date_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.birth_date_entry.configure(state="readonly")

        date_button = ctk.CTkButton(
            birth_date_frame,
            text="Chọn",
            width=74,
            height=36,
            fg_color="#2F74FF",
            hover_color="#0050DB",
            corner_radius=10,
            command=self.open_date_picker,
        )
        date_button.grid(row=0, column=1)

        self.email_entry = self._create_entry_row(
            form_frame,
            5,
            "Email",
            "Ví dụ: sv001@gmail.com",
        )

        # Khu vực nút chức năng.
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=6, column=0, columnspan=2, pady=(24, 18))

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
        if not self.student_data:
            self.gender_combo.set("Nam")
            return

        self.student_id_entry.insert(0, self.student_data.get("student_id", ""))
        self.student_name_entry.insert(0, self.student_data.get("student_name", ""))
        self.class_name_entry.insert(0, self.student_data.get("class_name", ""))
        self.gender_combo.set(self.student_data.get("gender", "Nam"))
        self._set_readonly_text(self.birth_date_entry, self.student_data.get("birth_date", ""))
        self.email_entry.insert(0, self.student_data.get("email", ""))

        if not self.student_id_editable:
            self.student_id_entry.configure(state="disabled")

    def open_date_picker(self):
        """Mở cửa sổ chọn ngày sinh."""
        logger.info("Người dùng mở DatePickerWindow trong StudentFormWindow.")
        DatePickerWindow(self, self.set_birth_date)

    def set_birth_date(self, value):
        """Nhận ngày sinh từ date picker và ghi vào ô readonly."""
        self._set_readonly_text(self.birth_date_entry, value)

    def _set_readonly_text(self, entry, value):
        """Ghi text vào ô readonly."""
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, value)
        entry.configure(state="readonly")

    def _is_valid_student_name(self, value: str) -> bool:
        """Kiểm tra tên sinh viên chỉ gồm chữ và khoảng trắng."""
        value = value.strip()
        if not value:
            return False
        for part in value.split():
            if not part.isalpha():
                return False
        return True

    def _is_valid_alnum_with_letter_and_digit(self, value: str) -> bool:
        """Kiểm tra chuỗi phải có cả chữ và số, không có ký tự đặc biệt."""
        value = value.strip()
        if not value or not value.isalnum():
            return False
        has_letter = any(char.isalpha() for char in value)
        has_digit = any(char.isdigit() for char in value)
        return has_letter and has_digit

    def _is_valid_gmail(self, value: str) -> bool:
        """Kiểm tra email đúng định dạng Gmail."""
        return bool(re.fullmatch(r"[A-Za-z0-9._%+-]+@gmail\.com", value.strip()))

    def _is_valid_birth_date(self, value: str) -> bool:
        """Kiểm tra ngày sinh đúng định dạng dd/mm/yyyy."""
        try:
            datetime.strptime(value, "%d/%m/%Y")
        except ValueError:
            return False
        return True

    def _is_duplicate_student_id(self, value: str) -> bool:
        """Kiểm tra mã sinh viên có bị trùng trong database hay không."""
        if not self.database:
            return False

        existing_student = self.database.fetch_student(value)
        if not existing_student:
            return False

        original_student_id = self.student_data.get("student_id", "").strip().upper()
        return value != original_student_id

    def _validate_form(self, data: dict[str, str]) -> tuple[bool, str]:
        """Kiểm tra toàn bộ form và trả về kết quả hợp lệ."""
        student_id = data["student_id"].strip()
        student_name = data["student_name"].strip()
        class_name = data["class_name"].strip()
        gender = data["gender"].strip()
        birth_date = data["birth_date"].strip()
        email = data["email"].strip()

        if not student_id:
            return False, "Mã sinh viên không được để trống."
        if not student_name:
            return False, "Tên sinh viên không được để trống."
        if not class_name:
            return False, "Tên lớp không được để trống."
        if not gender:
            return False, "Giới tính không được để trống."
        if not birth_date:
            return False, "Ngày sinh không được để trống."
        if not email:
            return False, "Email không được để trống."

        if not self._is_valid_alnum_with_letter_and_digit(student_id):
            return False, "Mã sinh viên phải có cả chữ và số, không chứa ký tự đặc biệt."
        if self._is_duplicate_student_id(student_id):
            return False, "Mã sinh viên đã tồn tại, vui lòng nhập mã khác."
        if not self._is_valid_student_name(student_name):
            return False, "Tên sinh viên chỉ được chứa chữ cái và khoảng trắng."
        if not self._is_valid_alnum_with_letter_and_digit(class_name):
            return False, "Tên lớp phải có cả chữ và số, không chứa ký tự đặc biệt."
        if gender not in ("Nam", "Nữ"):
            return False, "Giới tính chỉ được là Nam hoặc Nữ."
        if not self._is_valid_birth_date(birth_date):
            return False, "Ngày sinh phải có định dạng dd/mm/yyyy."
        if not self._is_valid_gmail(email):
            return False, "Email phải có định dạng đúng và kết thúc bằng @gmail.com."

        return True, ""

    def submit_form(self):
        """Kiểm tra form rồi gửi dữ liệu cho hàm xử lý bên ngoài."""
        if not self.on_save:
            self.destroy()
            return

        student_id = self.student_id_entry.get().strip().upper()
        student_name = self.student_name_entry.get().strip()
        class_name = self.class_name_entry.get().strip().upper()
        gender = self.gender_combo.get().strip()
        birth_date = self.birth_date_entry.get().strip()
        email = self.email_entry.get().strip()

        data = {
            "student_id": student_id,
            "student_name": student_name,
            "class_name": class_name,
            "gender": gender,
            "birth_date": birth_date,
            "email": email,
        }

        is_valid, message = self._validate_form(data)
        if not is_valid:
            messagebox.showwarning("Thiếu hoặc sai dữ liệu", message, parent=self)
            return

        self.on_save(data)
        logger.info("Đã lưu sinh viên qua StudentFormWindow: %s", data.get("student_id", ""))
        self.destroy()
