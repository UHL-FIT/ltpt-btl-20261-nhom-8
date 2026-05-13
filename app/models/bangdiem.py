from __future__ import annotations

import sqlite3

import numpy as np
import pandas as pd

from app.utils.database import Database
from app.utils.validation import classify_gpa, require_text, validate_school_year, validate_score, validate_semester


class BangDiemModel:
    columns = ["MaSV", "MaHocPhan", "HocKy", "NamHoc", "Diem"]

    def __init__(self, db: Database) -> None:
        self.db = db

    def add(self, ma_sv: str, ma_hp: str, hoc_ky: str, nam_hoc: str, diem: str | float) -> bool:
        try:
            self.db.execute(
                "INSERT INTO BangDiem(MaSV, MaHocPhan, HocKy, NamHoc, Diem) VALUES (?, ?, ?, ?, ?)",
                (
                    require_text(ma_sv, "mã sinh viên").upper(),
                    require_text(ma_hp, "mã học phần").upper(),
                    validate_semester(hoc_ky),
                    validate_school_year(nam_hoc),
                    validate_score(diem),
                ),
            )
            return True
        except sqlite3.IntegrityError:
            return False

    def update(self, old_key: tuple[str, str], ma_sv: str, ma_hp: str, hoc_ky: str, nam_hoc: str, diem: str | float) -> bool:
        try:
            cur = self.db.execute(
                """
                UPDATE BangDiem
                SET MaSV=?, MaHocPhan=?, HocKy=?, NamHoc=?, Diem=?
                WHERE MaSV=? AND MaHocPhan=?
                """,
                (
                    require_text(ma_sv, "mã sinh viên").upper(),
                    require_text(ma_hp, "mã học phần").upper(),
                    validate_semester(hoc_ky),
                    validate_school_year(nam_hoc),
                    validate_score(diem),
                    *old_key,
                ),
            )
            return cur.rowcount > 0
        except sqlite3.IntegrityError:
            return False

    def delete(self, ma_sv: str, ma_hp: str) -> bool:
        cur = self.db.execute(
            "DELETE FROM BangDiem WHERE MaSV=? AND MaHocPhan=?",
            (ma_sv, ma_hp),
        )
        return cur.rowcount > 0

    def list_records(self, ma_sv: str | None = None, hoc_ky: str | None = None, nam_hoc: str | None = None) -> list[dict]:
        sql = """
            SELECT bd.MaSV, sv.HoTen, sv.Lop, bd.MaHocPhan, mh.TenHocPhan, mh.SoTinChi,
                   bd.HocKy, bd.NamHoc, bd.Diem
            FROM BangDiem bd
            JOIN SinhVien sv ON sv.MaSV = bd.MaSV
            JOIN MonHoc mh ON mh.MaHocPhan = bd.MaHocPhan
            WHERE 1=1
        """
        params: list[str] = []
        if ma_sv:
            sql += " AND bd.MaSV=?"
            params.append(ma_sv)
        if hoc_ky:
            sql += " AND bd.HocKy=?"
            params.append(hoc_ky)
        if nam_hoc:
            sql += " AND bd.NamHoc=?"
            params.append(nam_hoc)
        sql += " ORDER BY bd.NamHoc, bd.HocKy, bd.MaSV, bd.MaHocPhan"
        return self.db.fetch_all(sql, params)

    def list_years(self) -> list[str]:
        rows = self.db.fetch_all("SELECT DISTINCT NamHoc FROM BangDiem ORDER BY NamHoc DESC")
        return [row["NamHoc"] for row in rows]

    def calculate_gpa(self, ma_sv: str) -> float:
        rows = self.list_records(ma_sv=ma_sv)  # Luôn lấy toàn bộ môn học
        if not rows:
            return 0.0
        df = pd.DataFrame(rows)
        total_credits = pd.to_numeric(df["SoTinChi"]).sum()
        if total_credits <= 0:
            return 0.0
        weighted = (pd.to_numeric(df["Diem"]) * pd.to_numeric(df["SoTinChi"])).sum()
        return round(float(weighted / total_credits), 2)

    def student_overview(self, hoc_ky: str | None = None, nam_hoc: str | None = None, keyword: str = "") -> list[dict]:
        students = self.db.fetch_all("SELECT MaSV, HoTen, Lop FROM SinhVien ORDER BY MaSV")
        keyword_lower = keyword.strip().lower()
        all_data = []
        for sv in students:
            gpa = self.calculate_gpa(sv["MaSV"])  # GPA tích lũy
            row = {**sv, "GPA": gpa, "XepLoai": classify_gpa(gpa)}
            all_data.append(row)

        # Tính toán xếp hạng dựa trên GPA tích lũy
        ranked_list = sorted([r for r in all_data if r["GPA"] > 0], key=lambda r: r["GPA"], reverse=True)
        rank_map = {}
        for i, r in enumerate(ranked_list, 1):
            rank_map[r["MaSV"]] = i

        rows = []
        for row in all_data:
            row["Hang"] = rank_map.get(row["MaSV"], "--")
            haystack = " ".join(str(v) for v in row.values()).lower()
            if not keyword_lower or keyword_lower in haystack:
                rows.append(row)
        return rows

    def get_student_rank(self, ma_sv: str) -> str:
        overview = self.student_overview()
        for row in overview:
            if row["MaSV"] == ma_sv:
                return str(row["Hang"])
        return "--"

    def statistics(self) -> dict:
        students = self.student_overview() # Thống kê trên toàn bộ dữ liệu
        gpas = [row["GPA"] for row in students if row["GPA"] > 0]
        gender_rows = self.db.fetch_all("SELECT GioiTinh, COUNT(*) AS SoLuong FROM SinhVien GROUP BY GioiTinh")
        classifications = {"Giỏi": 0, "Khá": 0, "Trung bình": 0, "Yếu": 0, "Chưa có điểm": 0}
        for row in students:
            classifications[row["XepLoai"]] = classifications.get(row["XepLoai"], 0) + 1
        return {
            "tong_sinh_vien": len(students),
            "tong_mon_hoc": (self.db.fetch_one("SELECT COUNT(*) AS n FROM MonHoc") or {"n": 0})["n"],
            "tong_diem": (self.db.fetch_one("SELECT COUNT(*) AS n FROM BangDiem") or {"n": 0})["n"],
            "gpa_trung_binh": round(float(np.mean(gpas)), 2) if gpas else 0.0,
            "gioi_tinh": {row["GioiTinh"]: row["SoLuong"] for row in gender_rows},
            "xep_loai": classifications,
            "top_gpa": sorted([r for r in students if r["GPA"] > 0], key=lambda r: r["GPA"], reverse=True)[:10],
        }

    def import_rows(self, rows: list[dict], target_ma_sv: str | None = None) -> int:
        # Lấy danh sách mã HP và Mã SV hiện có để kiểm tra nhanh
        existing_courses = {r["MaHocPhan"] for r in self.db.fetch_all("SELECT MaHocPhan FROM MonHoc")}
        existing_students = {r["MaSV"] for r in self.db.fetch_all("SELECT MaSV FROM SinhVien")}
        
        clean_data = []
        for i, row in enumerate(rows, 1):
            try:
                ma_sv = require_text(row.get("MaSV", ""), "mã sinh viên").upper()
                # Kiểm tra khớp mã sinh viên nếu đang import trong Chi tiết bảng điểm
                if target_ma_sv and ma_sv != target_ma_sv.upper():
                    raise ValueError(f"Mã sinh viên '{ma_sv}' không khớp với sinh viên đang chọn '{target_ma_sv}' (Cột MaSV)")
                
                # Kiểm tra sinh viên có tồn tại trong hệ thống không
                if ma_sv not in existing_students:
                    raise ValueError(f"Mã sinh viên '{ma_sv}' không tồn tại trong danh mục quản lý sinh viên (Cột MaSV)")

                ma_hp = require_text(row.get("MaHocPhan", ""), "mã học phần").upper()
                # Kiểm tra học phần có tồn tại không
                if ma_hp not in existing_courses:
                    raise ValueError(f"Mã học phần '{ma_hp}' không tồn tại trong danh mục quản lý học phần (Cột MaHocPhan)")

                hoc_ky = validate_semester(row.get("HocKy", ""))
                nam_hoc = validate_school_year(row.get("NamHoc", ""))
                diem = validate_score(row.get("Diem", ""))
                
                clean_data.append((ma_sv, ma_hp, hoc_ky, nam_hoc, diem))
            except ValueError as e:
                raise ValueError(f"Dòng {i}: {str(e)}")

        count = 0
        for data in clean_data:
            try:
                self.db.execute(
                    "INSERT INTO BangDiem(MaSV, MaHocPhan, HocKy, NamHoc, Diem) VALUES (?, ?, ?, ?, ?)",
                    data,
                )
                count += 1
            except sqlite3.IntegrityError:
                # Nếu đã tồn tại bản ghi (MaSV, MaHocPhan) thì bỏ qua hoặc báo lỗi tùy nhu cầu
                # Ở đây ta bỏ qua để tiếp tục nhập các dòng khác
                continue
        return count
