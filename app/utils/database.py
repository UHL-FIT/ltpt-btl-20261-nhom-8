from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable


def get_app_root() -> Path:
    return Path(__file__).resolve().parents[2]


class Database:
    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path == ":memory:":
            self.db_path = Path(":memory:")
            connect_target = ":memory:"
        else:
            # Đường dẫn mặc định là app/data/ketqua_hoc_tap_app.db
            self.db_path = Path(db_path) if db_path else get_app_root() / "app" / "data" / "ketqua_hoc_tap_app.db"
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            connect_target = self.db_path
        self.connection = sqlite3.connect(connect_target)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode = MEMORY")
        self.connection.execute("PRAGMA temp_store = MEMORY")
        self.connection.execute("PRAGMA foreign_keys = ON")

    def execute(self, sql: str, params: Iterable = ()) -> sqlite3.Cursor:
        try:
            cur = self.connection.execute(sql, tuple(params))
            self.connection.commit()
            return cur
        except Exception:
            self.connection.rollback()
            raise

    def executemany(self, sql: str, rows: Iterable[Iterable]) -> None:
        try:
            self.connection.executemany(sql, rows)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def fetch_all(self, sql: str, params: Iterable = ()) -> list[dict]:
        cur = self.connection.execute(sql, tuple(params))
        return [dict(row) for row in cur.fetchall()]

    def fetch_one(self, sql: str, params: Iterable = ()) -> dict | None:
        cur = self.connection.execute(sql, tuple(params))
        row = cur.fetchone()
        return dict(row) if row else None

    def close(self) -> None:
        self.connection.close()


def initialize_schema(db: Database) -> None:
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS SinhVien (
            MaSV TEXT PRIMARY KEY,
            HoTen TEXT NOT NULL,
            GioiTinh TEXT NOT NULL,
            NgaySinh TEXT NOT NULL,
            Lop TEXT NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS MonHoc (
            MaHocPhan TEXT PRIMARY KEY,
            TenHocPhan TEXT NOT NULL,
            SoTinChi INTEGER NOT NULL CHECK (SoTinChi BETWEEN 1 AND 4),
            HocKyMacDinh TEXT DEFAULT 'HK1' CHECK (HocKyMacDinh IN ('HK1', 'HK2'))
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS BangDiem (
            MaSV TEXT NOT NULL,
            MaHocPhan TEXT NOT NULL,
            HocKy TEXT NOT NULL CHECK (HocKy IN ('HK1', 'HK2')),
            NamHoc TEXT NOT NULL,
            Diem REAL NOT NULL CHECK (Diem BETWEEN 0 AND 10),
            PRIMARY KEY (MaSV, MaHocPhan),
            FOREIGN KEY (MaSV) REFERENCES SinhVien(MaSV) ON DELETE CASCADE,
            FOREIGN KEY (MaHocPhan) REFERENCES MonHoc(MaHocPhan) ON DELETE CASCADE
        )
        """
    )
