from __future__ import annotations

import sqlite3

from utils.database import Database
from utils.validation import require_text, validate_credit, validate_semester


class MonHocModel:
    columns = ["MaHocPhan", "TenHocPhan", "SoTinChi", "HocKyMacDinh"]

    def __init__(self, db: Database) -> None:
        self.db = db

    def add(self, ma_hp: str, ten_hp: str, so_tin_chi: str | int, hoc_ky_mac_dinh: str = "HK1") -> bool:
        ma_hp = require_text(ma_hp, "mã học phần").upper()
        ten_hp = require_text(ten_hp, "tên học phần")
        so_tin_chi = validate_credit(so_tin_chi)
        hoc_ky_mac_dinh = validate_semester(hoc_ky_mac_dinh)
        try:
            self.db.execute(
                "INSERT INTO MonHoc(MaHocPhan, TenHocPhan, SoTinChi, HocKyMacDinh) VALUES (?, ?, ?, ?)",
                (ma_hp, ten_hp, so_tin_chi, hoc_ky_mac_dinh),
            )
            return True
        except sqlite3.IntegrityError:
            return False

    def update(self, ma_hp: str, ten_hp: str, so_tin_chi: str | int, hoc_ky_mac_dinh: str = "HK1") -> bool:
        cur = self.db.execute(
            "UPDATE MonHoc SET TenHocPhan=?, SoTinChi=?, HocKyMacDinh=? WHERE MaHocPhan=?",
            (
                require_text(ten_hp, "tên học phần"),
                validate_credit(so_tin_chi),
                validate_semester(hoc_ky_mac_dinh),
                require_text(ma_hp, "mã học phần").upper(),
            ),
        )
        return cur.rowcount > 0

    def delete(self, ma_hp: str) -> bool:
        cur = self.db.execute("DELETE FROM MonHoc WHERE MaHocPhan=?", (ma_hp,))
        return cur.rowcount > 0

    def get(self, ma_hp: str) -> dict | None:
        return self.db.fetch_one("SELECT * FROM MonHoc WHERE MaHocPhan=?", (ma_hp,))

    def list_all(self) -> list[dict]:
        return self.db.fetch_all("SELECT * FROM MonHoc ORDER BY MaHocPhan")

    def search(self, keyword: str) -> list[dict]:
        pattern = f"%{keyword.strip()}%"
        return self.db.fetch_all(
            """
            SELECT * FROM MonHoc
            WHERE MaHocPhan LIKE ? OR TenHocPhan LIKE ? OR HocKyMacDinh LIKE ?
            ORDER BY MaHocPhan
            """,
            (pattern, pattern, pattern),
        )

    def import_rows(self, rows: list[dict]) -> tuple[int, int]:
        ok = failed = 0
        for row in rows:
            hoc_ky = row.get("HocKyMacDinh") or row.get("HocKy") or "HK1"
            if self.add(row.get("MaHocPhan", ""), row.get("TenHocPhan", ""), row.get("SoTinChi", ""), hoc_ky):
                ok += 1
            else:
                failed += 1
        return ok, failed
