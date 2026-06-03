from __future__ import annotations

import csv
import re
from datetime import datetime

from app.utils.logger import get_logger


logger = get_logger(__name__)


class StudentController:
    # Chuyen tu student_page.py - phan CRUD, CSV va validation sinh vien.
    def __init__(self, database):
        self.database = database
        logger.info("Khởi tạo StudentController.")

    def fetch_students(self):
        return self.database.fetch_students()

    def create_student(self, data):
        self.database.insert_student(data)
        logger.info("Đã thêm sinh viên: %s", data.get("student_id", ""))

    def update_student(self, original_student_id, data):
        self.database.update_student(original_student_id, data)
        logger.info("Đã cập nhật sinh viên: %s", original_student_id)

    def delete_students(self, student_ids):
        for student_id in student_ids:
            self.database.delete_student(student_id)
        logger.info("Đã xóa %s sinh viên.", len(student_ids))

    def export_csv(self, file_path):
        students = self.database.fetch_students()
        with open(file_path, "w", encoding="utf-8-sig", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Mã sinh viên", "Họ tên", "Lớp", "Giới tính", "Ngày sinh", "Email"])
            for student in students:
                writer.writerow(student)
        logger.info("Đã xuất CSV sinh viên: %s (%s dòng).", file_path, len(students))
        return len(students)

    def import_csv(self, file_path):
        inserted_count = 0
        updated_count = 0
        skipped_rows = []
        logger.info("Bắt đầu nhập CSV sinh viên: %s", file_path)

        with open(file_path, "r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if not self._validate_student_csv_header(reader.fieldnames):
                return {
                    "ok": False,
                    "message": "File CSV sinh viên phải có các cột: student_id, student_name, class_name, gender, birth_date, email.",
                }

            for row_number, row in enumerate(reader, start=2):
                normalized_row = self._normalize_student_csv_row(row)
                is_valid, error_message = self._validate_student_csv_row(normalized_row)
                if not is_valid:
                    skipped_rows.append(f"Dòng {row_number}: {error_message}")
                    continue

                existing_student = self.database.fetch_student(normalized_row["student_id"])
                if existing_student:
                    self.database.update_student(normalized_row["student_id"], normalized_row)
                    updated_count += 1
                else:
                    self.database.insert_student(normalized_row)
                    inserted_count += 1

        return {
            "ok": True,
            "inserted_count": inserted_count,
            "updated_count": updated_count,
            "skipped_rows": skipped_rows,
        }

    # -----------------------------
    # CSV Validation
    # -----------------------------
    # Phan nay duoc chuyen tu student_page.py.

    def _is_valid_student_name(self, value: str) -> bool:
        value = value.strip()
        if not value:
            return False
        for part in value.split():
            if not part.isalpha():
                return False
        return True

    def _is_valid_alnum_with_letter_and_digit(self, value: str) -> bool:
        value = value.strip()
        if not value or not value.isalnum():
            return False
        has_letter = any(char.isalpha() for char in value)
        has_digit = any(char.isdigit() for char in value)
        return has_letter and has_digit

    def _is_valid_gmail(self, value: str) -> bool:
        return bool(re.fullmatch(r"[A-Za-z0-9._%+-]+@gmail\.com", value.strip()))

    def _is_valid_birth_date(self, value: str) -> bool:
        try:
            datetime.strptime(value, "%d/%m/%Y")
        except ValueError:
            return False
        return True

    def _validate_student_csv_header(self, fieldnames):
        if not fieldnames:
            return False
        normalized_fields = {str(field).strip().lower() for field in fieldnames}
        required_groups = [
            {"student_id", "mã sinh viên"},
            {"student_name", "họ tên"},
            {"class_name", "lớp"},
            {"gender", "giới tính"},
            {"birth_date", "ngày sinh"},
            {"email"},
        ]
        return all(any(field in normalized_fields for field in group) for group in required_groups)

    def _normalize_student_csv_row(self, row):
        normalized_row = {str(key).strip().lower(): value for key, value in row.items()}
        return {
            "student_id": str(normalized_row.get("student_id") or normalized_row.get("mã sinh viên", "")).strip().upper(),
            "student_name": str(normalized_row.get("student_name") or normalized_row.get("họ tên", "")).strip(),
            "class_name": str(normalized_row.get("class_name") or normalized_row.get("lớp", "")).strip().upper(),
            "gender": str(normalized_row.get("gender") or normalized_row.get("giới tính", "")).strip(),
            "birth_date": str(normalized_row.get("birth_date") or normalized_row.get("ngày sinh", "")).strip(),
            "email": str(normalized_row.get("email", "")).strip(),
        }

    def _validate_student_csv_row(self, data):
        """Kiểm tra dữ liệu từ file csv"""
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
            return False, "Mã sinh viên phải có cả chữ và số, không chứa ký tự đặc biệt hoặc khoảng trắng."
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
