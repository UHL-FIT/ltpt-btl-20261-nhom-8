from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from models.bangdiem import BangDiemModel
from models.monhoc import MonHocModel
from models.sinhvien import SinhVienModel
from utils.csv_helpers import export_csv, read_csv_required
from utils.database import Database, initialize_schema
from utils.validation import classify_gpa, validate_credit, validate_score


class ModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_path = None
        self.db = Database(":memory:")
        initialize_schema(self.db)
        self.sv = SinhVienModel(self.db)
        self.mh = MonHocModel(self.db)
        self.bd = BangDiemModel(self.db)
        self.sv.add("SV001", "Nguyen Van A", "Nam", "21/08/2005", "DH10TT02A")
        self.sv.add("SV002", "Nguyen Thi B", "Nữ", "15/09/2006", "DH10TT02B")
        self.mh.add("MH001", "Toán cao cấp", 3, "HK1")
        self.mh.add("MH002", "Lập trình căn bản", 2, "HK1")
        self.mh.add("MH003", "Cơ sở dữ liệu", 4, "HK2")

    def tearDown(self) -> None:
        self.db.close()

    def test_student_course_crud(self) -> None:
        self.assertFalse(self.sv.add("SV001", "Trùng", "Nam", "01/01/2000", "A"))
        self.assertTrue(self.sv.update("SV001", "Nguyen Van A Updated", "Nam", "21/08/2005", "DH10TT02A"))
        self.assertEqual(self.sv.get("SV001")["HoTen"], "Nguyen Van A Updated")
        self.assertTrue(self.mh.update("MH001", "Toán cao cấp 1", 3, "HK1"))
        self.assertEqual(self.mh.get("MH001")["SoTinChi"], 3)

    def test_score_validation_and_unique_key(self) -> None:
        self.assertTrue(self.bd.add("SV001", "MH001", "HK1", "2024-2025", 8.5))
        self.assertFalse(self.bd.add("SV001", "MH001", "HK1", "2024-2025", 9.0))
        with self.assertRaises(ValueError):
            self.bd.add("SV001", "MH002", "HK1", "2024-2025", 11)
        with self.assertRaises(ValueError):
            validate_credit(5)
        with self.assertRaises(ValueError):
            validate_score(-1)

    def test_weighted_gpa_by_semester_year(self) -> None:
        self.bd.add("SV001", "MH001", "HK1", "2024-2025", 8.0)
        self.bd.add("SV001", "MH002", "HK1", "2024-2025", 7.0)
        self.bd.add("SV001", "MH003", "HK2", "2024-2025", 5.0)
        self.assertEqual(self.bd.calculate_gpa("SV001", "HK1", "2024-2025"), 7.6)
        self.assertEqual(self.bd.calculate_gpa("SV001", "HK2", "2024-2025"), 5.0)
        self.assertEqual(classify_gpa(self.bd.calculate_gpa("SV002")), "Chưa có điểm")

    def test_delete_cascade(self) -> None:
        self.bd.add("SV001", "MH001", "HK1", "2024-2025", 8.0)
        self.assertTrue(self.sv.delete("SV001"))
        self.assertEqual(self.bd.list_records("SV001"), [])


class CsvTestCase(unittest.TestCase):
    def test_csv_read_required_and_export_utf8_sig(self) -> None:
        tmp_path = Path(__file__).resolve().parent / "_tmp_csv"
        shutil.rmtree(tmp_path, ignore_errors=True)
        tmp_path.mkdir(parents=True, exist_ok=True)
        try:
            path = tmp_path / "sinhvien.csv"
            rows = [
                {
                    "MaSV": "SV001",
                    "HoTen": "Nguyen Van A",
                    "GioiTinh": "Nam",
                    "NgaySinh": "01/01/2000",
                    "Lop": "A",
                }
            ]
            export_csv(path, rows, ["MaSV", "HoTen", "GioiTinh", "NgaySinh", "Lop"])
            self.assertTrue(path.read_bytes().startswith(b"\xef\xbb\xbf"))
            df = read_csv_required(path, ["MaSV", "HoTen"])
            self.assertEqual(df.iloc[0]["MaSV"], "SV001")
            with self.assertRaises(ValueError):
                read_csv_required(path, ["CotKhongTonTai"])
        finally:
            shutil.rmtree(tmp_path, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
