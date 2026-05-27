from __future__ import annotations

import csv

from app.utils.logger import get_logger


logger = get_logger(__name__)


class CourseController:
    # Chuyen tu course_page.py - phan CRUD, CSV va validation hoc phan.
    def __init__(self, database):
        self.database = database
        logger.info("Khởi tạo CourseController.")

    def fetch_courses(self):
        return self.database.fetch_courses()

    def create_course(self, data):
        self.database.insert_course(data)
        logger.info("Đã thêm học phần: %s", data.get("course_id", ""))

    def update_course(self, original_course_id, data):
        self.database.update_course(original_course_id, data)
        logger.info("Đã cập nhật học phần: %s", original_course_id)

    def delete_courses(self, course_ids):
        for course_id in course_ids:
            self.database.delete_course(course_id)
        logger.info("Đã xóa %s học phần.", len(course_ids))

    def export_csv(self, file_path):
        courses = self.database.fetch_courses()
        with open(file_path, "w", encoding="utf-8-sig", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Mã học phần", "Tên học phần", "Số tín chỉ", "Học kỳ"])
            for course in courses:
                writer.writerow(course)
        logger.info("Đã xuất CSV học phần: %s (%s dòng).", file_path, len(courses))
        return len(courses)

    def import_csv(self, file_path):
        inserted_count = 0
        updated_count = 0
        skipped_rows = []
        logger.info("Bắt đầu nhập CSV học phần: %s", file_path)

        with open(file_path, "r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if not self._validate_course_csv_header(reader.fieldnames):
                return {
                    "ok": False,
                    "message": "File CSV học phần phải có các cột: course_id, course_name, credits, semester.",
                }

            for row_number, row in enumerate(reader, start=2):
                normalized_row = self._normalize_course_csv_row(row)
                is_valid, error_message = self._validate_course_csv_row(normalized_row)
                if not is_valid:
                    skipped_rows.append(f"Dòng {row_number}: {error_message}")
                    continue

                existing_course = self.database.fetch_course(normalized_row["course_id"])
                if existing_course:
                    self.database.update_course(normalized_row["course_id"], normalized_row)
                    updated_count += 1
                else:
                    self.database.insert_course(normalized_row)
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
    # Phan nay duoc chuyen tu course_page.py.

    def _validate_course_csv_header(self, fieldnames):
        if not fieldnames:
            return False
        normalized_fields = {str(field).strip().lower() for field in fieldnames}
        required_groups = [
            {"course_id", "mã học phần"},
            {"course_name", "tên học phần"},
            {"credits", "số tín chỉ"},
            {"semester", "học kỳ"},
        ]
        return all(any(field in normalized_fields for field in group) for group in required_groups)

    def _normalize_course_csv_row(self, row):
        normalized_row = {str(key).strip().lower(): value for key, value in row.items()}
        return {
            "course_id": str(normalized_row.get("course_id") or normalized_row.get("mã học phần", "")).strip().upper(),
            "course_name": str(normalized_row.get("course_name") or normalized_row.get("tên học phần", "")).strip(),
            "credits": str(normalized_row.get("credits") or normalized_row.get("số tín chỉ", "")).strip(),
            "semester": str(normalized_row.get("semester") or normalized_row.get("học kỳ", "")).strip().upper(),
        }

    def _validate_course_csv_row(self, data):
        course_id = data["course_id"].strip()
        course_name = data["course_name"].strip()
        credits = data["credits"].strip()
        semester = data["semester"].strip()

        if not course_id:
            return False, "Mã học phần không được để trống."
        if not course_name:
            return False, "Tên học phần không được để trống."
        if not credits:
            return False, "Số tín chỉ không được để trống."
        if not semester:
            return False, "Học kỳ không được để trống."

        if not self._is_valid_alnum_with_letter_and_digit(course_id):
            return False, "Mã học phần phải có cả chữ và số, không chứa ký tự đặc biệt."
        if not self._is_valid_course_name(course_name):
            return False, "Tên học phần chỉ được chứa chữ cái và khoảng trắng."
        if not credits.isdigit() or int(credits) <= 0:
            return False, "Số tín chỉ phải là số nguyên dương."
        if semester not in ("HK1", "HK2", "HK3", "HK4"):
            return False, "Học kỳ chỉ được là HK1, HK2, HK3 hoặc HK4."

        return True, ""

    def _is_valid_alnum_with_letter_and_digit(self, value: str) -> bool:
        value = value.strip()
        if not value or not value.isalnum():
            return False
        has_letter = any(char.isalpha() for char in value)
        has_digit = any(char.isdigit() for char in value)
        return has_letter and has_digit

    def _is_valid_course_name(self, value: str) -> bool:
        value = value.strip()
        if not value:
            return False
        for part in value.split():
            if not part.isalpha():
                return False
        return True
