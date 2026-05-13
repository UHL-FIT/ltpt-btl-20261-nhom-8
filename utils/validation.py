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


def validate_school_year(value: str) -> str:
    text = require_text(value, "năm học")
    if not YEAR_RE.match(text):
        raise ValueError("Năm học phải có dạng 2024-2025.")
    return text.replace("–", "-")


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
