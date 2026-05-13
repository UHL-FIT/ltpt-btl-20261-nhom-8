from __future__ import annotations

import re


YEAR_RE = re.compile(r"^\d{4}[-–]\d{4}$")


def require_text(value: str, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"Vui lòng nhập {field_name}.")
    return text


def validate_credit(value: str | int) -> int:
    try:
        credit = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Số tín chỉ phải là số nguyên.") from exc
    if credit < 1 or credit > 4:
        raise ValueError("Số tín chỉ phải nằm trong khoảng 1 đến 4.")
    return credit


def validate_score(value: str | float) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Điểm phải là số.") from exc
    if score < 0 or score > 10:
        raise ValueError("Điểm phải nằm trong khoảng 0 đến 10.")
    return score


def validate_semester(value: str) -> str:
    text = require_text(value, "học kỳ").upper().replace(" ", "")
    if text not in {"HK1", "HK2"}:
        raise ValueError("Học kỳ chỉ được là HK1 hoặc HK2.")
    return text


import datetime


def validate_school_year(value: str) -> str:
    text = require_text(value, "năm học").replace("–", "-")
    if not YEAR_RE.match(text):
        raise ValueError("Năm học phải có dạng YYYY-YYYY (ví dụ: 2024-2025).")
    parts = text.split("-")
    y1, y2 = int(parts[0]), int(parts[1])
    if y2 != y1 + 1:
        raise ValueError("Năm học không hợp lệ. Hai năm phải liên tiếp tăng dần (ví dụ: 2024-2025).")
    
    current_year = datetime.datetime.now().year
    if y1 > current_year:
        raise ValueError(f"Năm học không được vượt quá năm hiện tại ({current_year}).")
    
    return text


def validate_enrollment_age(school_year: str, birth_date_str: str) -> None:
    # school_year: YYYY-YYYY, birth_date_str: DD/MM/YYYY
    try:
        y1 = int(school_year.split("-")[0])
        birth_year = int(birth_date_str.split("/")[-1])
        if y1 < birth_year + 17:
            raise ValueError(
                f"Năm bắt đầu học phần ({y1}) không được nhỏ hơn năm sinh + 17 ({birth_year + 17}).\n"
                f"Sinh viên sinh năm {birth_year} chỉ có thể học từ năm học {birth_year + 17}-{birth_year + 18} trở đi."
            )
    except (ValueError, IndexError):
        pass  # Nếu định dạng sai, các validator khác sẽ bắt được sau


def validate_birth_date(value: str) -> str:
    text = require_text(value, "ngày sinh")
    
    # Kiểm tra định dạng cơ bản bằng Regex (chỉ cho phép số và /)
    if not re.match(r"^\d{2}/\d{2}/\d{4}$", text):
        raise ValueError("Vui lòng nhập ngày sinh đúng định dạng dd/mm/yyyy (ví dụ: 11/08/2006).")
    
    try:
        # Kiểm tra tính hợp lệ của lịch (ví dụ không có ngày 31/02)
        birth_date = datetime.datetime.strptime(text, "%d/%m/%Y")
    except ValueError:
        raise ValueError("Ngày sinh không hợp lệ (ngày không tồn tại trong lịch).")
    
    # Kiểm tra độ tuổi
    today = datetime.datetime.now()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    if birth_date > today:
        raise ValueError("Ngày sinh không được lớn hơn ngày hiện tại.")
    
    if age < 17 or age > 100:
        raise ValueError(f"Tuổi sinh viên không hợp lệ ({age} tuổi). Tuổi phải từ 17 đến 100.")
        
    return text


def classify_gpa(gpa: float) -> str:
    if gpa <= 0:
        return "Chưa có điểm"
    if gpa >= 8.0:
        return "Giỏi"
    if gpa >= 6.5:
        return "Khá"
    if gpa >= 5.0:
        return "Trung bình"
    return "Yếu"
