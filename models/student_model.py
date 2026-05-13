import pandas as pd
from models.database import get_connection

class StudentModel:
    """Model xử lý các thao tác với bảng SinhVien"""
    
    def __init__(self, score_model=None):
        self.score_model = score_model

    def get_all_students(self) -> pd.DataFrame:
        conn = get_connection()
        query = "SELECT * FROM SinhVien"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def _get_first_name(self, full_name):
        """Tách tên từ họ tên (từ cuối cùng)"""
        if not isinstance(full_name, str) or not full_name.strip():
            return ""
        return full_name.strip().split()[-1].lower()

    def get_all_students_with_gpa(self, search_term="") -> pd.DataFrame:
        """Lấy danh sách sinh viên kèm GPA, hỗ trợ tìm kiếm và sắp xếp Alphabet"""
        # 1. Lấy danh sách SV
        df_students = self.get_all_students()
        if df_students.empty:
            return pd.DataFrame(columns=['MaSV', 'HoTen', 'GioiTinh', 'NgaySinh', 'Lop', 'GPA', 'XepLoai'])

        # 2. Lấy danh sách GPA (nếu đã tiêm score_model)
        if self.score_model:
            df_gpa = self.score_model.calculate_gpa()
            if not df_gpa.empty:
                # Merge SinhVien với GPA qua MaSV
                df_gpa = df_gpa[['MaSV', 'GPA', 'XepLoai']]
                df_students = pd.merge(df_students, df_gpa, on='MaSV', how='left')
                
        # Fill NaN cho GPA và XepLoai nếu sinh viên chưa có điểm
        if 'GPA' not in df_students.columns:
            df_students['GPA'] = 0.0
            df_students['XepLoai'] = "Chưa có"
        else:
            df_students['GPA'] = df_students['GPA'].fillna(0.0)
            df_students['XepLoai'] = df_students['XepLoai'].fillna("Chưa có")

        # 3. Lọc theo search_term
        if search_term:
            search_term = search_term.lower()
            df_students = df_students[
                df_students['MaSV'].str.lower().str.contains(search_term) |
                df_students['HoTen'].str.lower().str.contains(search_term)
            ]

        # 4. Sắp xếp Alphabet theo Tên
        if not df_students.empty:
            df_students['Ten'] = df_students['HoTen'].apply(self._get_first_name)
            df_students = df_students.sort_values(by=['Ten', 'HoTen']).drop(columns=['Ten'])

        return df_students

    def add_student(self, ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO SinhVien (MaSV, HoTen, GioiTinh, NgaySinh, Lop) VALUES (?, ?, ?, ?, ?)",
                (ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop)
            )
            conn.commit()
            return True
        except Exception as e:
            return False
        finally:
            conn.close()

    def update_student(self, ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE SinhVien SET HoTen=?, GioiTinh=?, NgaySinh=?, Lop=? WHERE MaSV=?",
                (ho_ten, gioi_tinh, ngay_sinh, lop, ma_sv)
            )
            conn.commit()
            return True
        except Exception as e:
            return False
        finally:
            conn.close()

    def delete_student(self, ma_sv) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM SinhVien WHERE MaSV=?", (ma_sv,))
            cursor.execute("DELETE FROM BangDiem WHERE MaSV=?", (ma_sv,))
            conn.commit()
            return True
        except Exception as e:
            return False
        finally:
            conn.close()
