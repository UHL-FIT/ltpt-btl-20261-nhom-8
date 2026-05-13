from __future__ import annotations

import sqlite3

from app.utils.database import Database
from app.utils.validation import require_text, validate_birth_date


class SinhVienModel:
    columns = ["MaSV", "HoTen", "GioiTinh", "NgaySinh", "Lop"]

    def __init__(self, db: Database) -> None:
        self.db = db

    def add(self, ma_sv: str, ho_ten: str, gioi_tinh: str, ngay_sinh: str, lop: str) -> bool:
        ma_sv = require_text(ma_sv, "mã sinh viên").upper()
        ho_ten = require_text(ho_ten, "họ tên")
        gioi_tinh = require_text(gioi_tinh, "giới tính")
        ngay_sinh = validate_birth_date(ngay_sinh)
        lop = require_text(lop, "lớp")
        try:
            self.db.execute(
                "INSERT INTO SinhVien(MaSV, HoTen, GioiTinh, NgaySinh, Lop) VALUES (?, ?, ?, ?, ?)",
                (ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop),
            )
            return True
        except sqlite3.IntegrityError:
            return False

    def update(self, ma_sv: str, ho_ten: str, gioi_tinh: str, ngay_sinh: str, lop: str) -> bool:
        ma_sv = require_text(ma_sv, "mã sinh viên").upper()
        cur = self.db.execute(
            "UPDATE SinhVien SET HoTen=?, GioiTinh=?, NgaySinh=?, Lop=? WHERE MaSV=?",
            (
                require_text(ho_ten, "họ tên"),
                require_text(gioi_tinh, "giới tính"),
                validate_birth_date(ngay_sinh),
                require_text(lop, "lớp"),
                ma_sv,
            ),
        )
        return cur.rowcount > 0

    def delete(self, ma_sv: str) -> bool:
        cur = self.db.execute("DELETE FROM SinhVien WHERE MaSV=?", (ma_sv,))
        return cur.rowcount > 0

    def get(self, ma_sv: str) -> dict | None:
        return self.db.fetch_one("SELECT * FROM SinhVien WHERE MaSV=?", (ma_sv,))

    def list_all(self) -> list[dict]:
        return self.db.fetch_all("SELECT * FROM SinhVien ORDER BY MaSV")

    def search(self, keyword: str) -> list[dict]:
        pattern = f"%{keyword.strip()}%"
        return self.db.fetch_all(
            """
            SELECT * FROM SinhVien
            WHERE MaSV LIKE ? OR HoTen LIKE ? OR Lop LIKE ? OR GioiTinh LIKE ?
            ORDER BY MaSV
            """,
            (pattern, pattern, pattern, pattern),
        )

    def import_rows(self, rows: list[dict]) -> int:
        clean_data = []
        for i, row in enumerate(rows, 1):
            try:
                ma_sv = require_text(row.get("MaSV", ""), "mã sinh viên").upper()
                ho_ten = require_text(row.get("HoTen", ""), "họ tên")
                gioi_tinh = require_text(row.get("GioiTinh", ""), "giới tính")
                ngay_sinh = validate_birth_date(row.get("NgaySinh", ""))
                lop = require_text(row.get("Lop", ""), "lớp")
                clean_data.append((ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop))
            except ValueError as e:
                raise ValueError(f"Lỗi tại dòng {i}: {str(e)}")

        count = 0
        for data in clean_data:
            try:
                self.db.execute(
                    "INSERT INTO SinhVien(MaSV, HoTen, GioiTinh, NgaySinh, Lop) VALUES (?, ?, ?, ?, ?)",
                    data,
                )
                count += 1
            except sqlite3.IntegrityError:
                continue  # Bỏ qua nếu trùng mã nhưng không dừng cả quá trình nếu đã pass validation
        return count
