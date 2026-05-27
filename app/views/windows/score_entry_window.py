from __future__ import annotations

import re
from datetime import date
from tkinter import messagebox

import customtkinter as ctk

from app.utils.logger import get_logger


logger = get_logger(__name__)


class ScoreEntryWindow(ctk.CTkToplevel):
    """Cửa sổ nhập liệu để thêm hoặc sửa điểm chi tiết."""

    def __init__(
        self,
        parent,
        database,
        student_id: str,
        title="Nhập điểm",
        detail_data=None,
        on_save=None,
        detail_editable=True,
    ):
        """Khởi tạo cửa sổ nhập điểm."""
        super().__init__(parent)
        self.parent_window = parent
        self.database = database
        self.student_id = student_id
        self.detail_data = detail_data or {}
        self.on_save = on_save
        self.detail_editable = detail_editable
        logger.info("Mở ScoreEntryWindow với chế độ: %s", title)

        self.course_options = self._build_course_options()

        self.title(title)
        self.geometry("520x420")
        self.minsize(480, 420)
        self.configure(fg_color="#F8FAFC")
        self.transient(parent)
        self.lift()
        self.focus_force()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        self._center_window()
        self._create_widgets()
        self._fill_data()

    def _build_course_options(self):
        """Tạo danh sách học phần có thể chọn."""
        options = []
        self.course_map = {}
        selected_course_id = self.detail_data.get("course_id", "")
        taken_course_ids = self._get_taken_course_ids()

        for course_id, course_name, credits, semester in self.database.fetch_courses():
            if course_id in taken_course_ids and course_id != selected_course_id:
                continue

            display = f"{course_id} - {course_name}"
            options.append(display)
            self.course_map[display] = {
                "course_id": course_id,
                "course_name": course_name,
                "credits": str(credits),
                "semester": semester,
            }

        return options

    def _get_taken_course_ids(self):
        """Lấy các học phần sinh viên đã có điểm."""
        taken_course_ids = set()
        if not self.database:
            return taken_course_ids

        for detail in self.database.fetch_score_details(self.student_id):
            taken_course_ids.add(detail[1])

        if self.detail_data:
            current_course_id = self.detail_data.get("course_id", "")
            if current_course_id:
                taken_course_ids.discard(current_course_id)

        return taken_course_ids

    def _center_window(self):
        """Canh cửa sổ vào giữa màn hình."""
        self.update_idletasks()
        width = 480
        height = 420
        x = self.winfo_screenwidth() // 2 - width // 2
        y = self.winfo_screenheight() // 2 - height // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self):
        """Tạo toàn bộ giao diện của form điểm."""
        # Khung ngoài cùng có viền xanh.
        padding_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            border_width=2,
            border_color="#2F74FF",
            corner_radius=6,
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

        ctk.CTkLabel(
            form_frame,
            text="Mã học phần",
            font=("Arial", 13, "bold"),
            text_color="#2F74FF",
        ).grid(row=0, column=0, sticky="w", padx=(20, 14), pady=(14, 4))

        self.course_combo = ctk.CTkComboBox(
            form_frame,
            values=self.course_options,
            state="readonly",
            height=36,
            corner_radius=10,
            border_width=2,
            border_color="#2F74FF",
            fg_color="#F8FAFC",
            button_color="#2F74FF",
            button_hover_color="#0050DB",
            command=self._on_course_change,
        )
        self.course_combo.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=(14, 4))

        self.credits_entry = self._create_readonly_row(form_frame, 1, "Tín chỉ")
        self.semester_entry = self._create_readonly_row(form_frame, 2, "Học kỳ")

        self.school_year_entry = self._create_entry_row(
            form_frame,
            3,
            "Năm học",
            "Ví dụ: 2024-2025",
        )
        self.score_entry = self._create_entry_row(
            form_frame,
            4,
            "Điểm số",
            "Ví dụ: 8.5",
        )

        # Khu vực nút chức năng.
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, columnspan=2, pady=(24, 18))

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Hủy",
            width=110,
            height=38,
            text_color="#ffffff",
            fg_color="#EA0000",
            hover_color="#B00000",
            corner_radius=10,
            command=self.close_window,
        )
        cancel_button.pack(side="left", padx=(10, 30))

        save_button = ctk.CTkButton(
            button_frame,
            text="Lưu",
            width=110,
            height=38,
            text_color="#ffffff",
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

    def _create_readonly_row(self, parent, row, label_text):
        """Tạo một dòng chỉ đọc."""
        entry = self._create_entry_row(parent, row, label_text, "")
        entry.configure(state="readonly")
        return entry

    def _fill_data(self):
        """Điền dữ liệu có sẵn khi mở form ở chế độ sửa."""
        if not self.course_options:
            self.course_combo.set("")
            self.course_combo.configure(state="disabled")
            self._set_readonly_text(self.credits_entry, "")
            self._set_readonly_text(self.semester_entry, "")
            return

        if self.detail_data:
            display = f"{self.detail_data.get('course_id', '')} - {self.detail_data.get('course_name', '')}"
            if display in self.course_map:
                self.course_combo.set(display)
            else:
                self.course_combo.set(self.course_options[0])

            self.school_year_entry.insert(0, self.detail_data.get("school_year", ""))
            self.score_entry.insert(0, self.detail_data.get("score", ""))
            self._sync_course_fields(self.course_combo.get())

            if not self.detail_editable:
                self.course_combo.configure(state="disabled")
        else:
            self.course_combo.set(self.course_options[0])
            self._sync_course_fields(self.course_combo.get())

    def _on_course_change(self, value):
        """Cập nhật tín chỉ và học kỳ khi đổi học phần."""
        self._sync_course_fields(value)

    def _sync_course_fields(self, value):
        """Đổ thông tin học phần vào các ô chỉ đọc."""
        course = self.course_map.get(value)
        if not course:
            return

        self._set_readonly_text(self.credits_entry, course["credits"])
        self._set_readonly_text(self.semester_entry, course["semester"])

    def _set_readonly_text(self, entry, value):
        """Ghi text vào ô readonly."""
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, value)
        entry.configure(state="readonly")

    def _is_valid_school_year(self, value: str) -> bool:
        """Kiểm tra năm học đúng định dạng và không vượt quá năm hiện tại."""
        value = value.strip()
        match = re.fullmatch(r"(\d{4})-(\d{4})", value)
        if not match:
            return False

        start_year = int(match.group(1))
        end_year = int(match.group(2))
        current_year = date.today().year

        if end_year != start_year + 1:
            return False
        if start_year > current_year:
            return False
        if end_year > current_year:
            return False

        return True

    def _is_valid_score(self, value: str) -> bool:
        """Kiểm tra điểm số phải là số từ 0 đến 10."""
        try:
            score = float(value.strip())
        except ValueError:
            return False
        return 0 <= score <= 10

    def _validate_form(self, data: dict[str, str]) -> tuple[bool, str]:
        """Kiểm tra toàn bộ form trước khi lưu."""
        course_id = data["course_id"].strip()
        school_year = data["school_year"].strip()
        score = data["score"].strip()

        if not course_id:
            return False, "Bạn phải chọn một học phần."
        if not school_year:
            return False, "Năm học không được để trống."
        if not self._is_valid_school_year(school_year):
            return False, "Năm học phải đúng định dạng YYYY-YYYY và năm sau phải bằng năm trước cộng 1."
        if not score:
            return False, "Điểm số không được để trống."
        if not self._is_valid_score(score):
            return False, "Điểm số phải là số từ 0 đến 10."

        return True, ""

    def submit_form(self):
        """Kiểm tra form rồi gửi dữ liệu cho hàm xử lý bên ngoài."""
        course = self.course_map.get(self.course_combo.get())
        if not course:
            logger.warning("Chưa chọn hoặc chọn sai học phần trong ScoreEntryWindow.")
            messagebox.showwarning("Thiếu hoặc sai dữ liệu", "Bạn phải chọn một học phần.", parent=self)
            return

        if self.on_save:
            data = {
                "student_id": self.student_id,
                "course_id": course["course_id"],
                "course_name": course["course_name"],
                "credits": course["credits"],
                "semester": course["semester"],
                "school_year": self.school_year_entry.get().strip(),
                "score": self.score_entry.get().strip(),
            }
            is_valid, message = self._validate_form(data)
            if not is_valid:
                logger.warning("Validate score form thất bại: %s", message)
                messagebox.showwarning("Thiếu hoặc sai dữ liệu", message, parent=self)
                return

            self.on_save(data)
            logger.info(
                "Đã lưu điểm qua ScoreEntryWindow: %s - %s",
                data.get("student_id", ""),
                data.get("course_id", ""),
            )
        self.close_window()

    def close_window(self):
        """Đóng form và trả lại quyền thao tác cho cửa sổ cha."""
        try:
            self.grab_release()
        except Exception:
            pass

        if self.parent_window and self.parent_window.winfo_exists():
            try:
                self.parent_window.grab_set()
                self.parent_window.lift()
                self.parent_window.focus_force()
            except Exception:
                pass

        self.destroy()



