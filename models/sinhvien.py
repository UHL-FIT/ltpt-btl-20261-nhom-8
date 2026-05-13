from __future__ import annotations

import sqlite3

from utils.database import Database
from utils.validation import require_text


class SinhVienModel:
    columns = ["MaSV", "HoTen", "GioiTinh", "NgaySinh", "Lop"]

    def __init__(self, db: Database) -> None:
        self.db = db

    def add(self, ma_sv: str, ho_ten: str, gioi_tinh: str, ngay_sinh: str, lop: str) -> bool:
        ma_sv = require_text(ma_sv, "mã sinh viên").upper()
        ho_ten = require_text(ho_ten, "họ tên")
        gioi_tinh = require_text(gioi_tinh, "giới tính")
        ngay_sinh = require_text(ngay_sinh, "ngày sinh")
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
                require_text(ngay_sinh, "ngày sinh"),
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

    def import_rows(self, rows: list[dict]) -> tuple[int, int]:
        ok = failed = 0
        for row in rows:
            if self.add(row.get("MaSV", ""), row.get("HoTen", ""), row.get("GioiTinh", ""), row.get("NgaySinh", ""), row.get("Lop", "")):
                ok += 1
            else:
                failed += 1
        return ok, failed
