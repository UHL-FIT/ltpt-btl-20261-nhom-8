import pandas as pd
import numpy as np
from models.database import get_connection

class ScoreModel:
    """Model xử lý bảng điểm và thống kê GPA dùng Numpy/Pandas"""
    
    def get_all_scores(self, search_term="") -> pd.DataFrame:
        """Lấy toàn bộ bảng điểm, hỗ trợ tìm kiếm"""
        conn = get_connection()
        query = '''
            SELECT b.MaSV, s.HoTen, b.MaHocPhan, m.TenHocPhan, m.SoTinChi, b.HocKy, b.NamHoc, b.Diem
            FROM BangDiem b
            JOIN SinhVien s ON b.MaSV = s.MaSV
            JOIN MonHoc m ON b.MaHocPhan = m.MaHocPhan
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()

        if search_term and not df.empty:
            search_term = search_term.lower()
            df = df[
                df['MaSV'].str.lower().str.contains(search_term) |
                df['TenHocPhan'].str.lower().str.contains(search_term)
            ]
        return df

    def add_or_update_score(self, ma_sv, ma_hp, hoc_ky, nam_hoc, diem) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "REPLACE INTO BangDiem (MaSV, MaHocPhan, HocKy, NamHoc, Diem) VALUES (?, ?, ?, ?, ?)",
                (ma_sv, ma_hp, hoc_ky, nam_hoc, diem)
            )
            conn.commit()
            return True
        except Exception as e:
            return False
        finally:
            conn.close()

    def delete_score(self, ma_sv, ma_hp) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM BangDiem WHERE MaSV=? AND MaHocPhan=?", (ma_sv, ma_hp))
            conn.commit()
            return True
        except Exception as e:
            return False
        finally:
            conn.close()

    def _classify_gpa(self, gpa: float) -> str:
        if gpa >= 8.0:
            return "Giỏi"
        elif gpa >= 6.5:
            return "Khá"
        elif gpa >= 5.0:
            return "Trung bình"
        else:
            return "Yếu"

    def calculate_gpa(self) -> pd.DataFrame:
        """Tính GPA và phân loại cho toàn bộ sinh viên"""
        df = self.get_all_scores()
        if df.empty:
            return pd.DataFrame(columns=['MaSV', 'HoTen', 'TongTinChi', 'GPA', 'XepLoai'])
            
        def calc(group):
            diem_arr = group['Diem'].values
            tin_chi_arr = group['SoTinChi'].values
            tong_tc = np.sum(tin_chi_arr)
            gpa = np.sum(diem_arr * tin_chi_arr) / tong_tc if tong_tc > 0 else 0.0
            xep_loai = self._classify_gpa(gpa)
            return pd.Series({'TongTinChi': tong_tc, 'GPA': round(gpa, 2), 'XepLoai': xep_loai})
            
        gpa_df = df.groupby(['MaSV', 'HoTen']).apply(calc).reset_index()
        return gpa_df

    def get_top_students(self, limit=10) -> pd.DataFrame:
        """Lấy Top sinh viên có GPA cao nhất"""
        df = self.calculate_gpa()
        if not df.empty:
            df = df.sort_values(by='GPA', ascending=False).head(limit)
        return df

    def get_classification_stats(self) -> dict:
        """Thống kê số lượng sinh viên theo từng phân loại (Giỏi, Khá, TB, Yếu)"""
        df = self.calculate_gpa()
        if df.empty:
            return {}
        stats = df['XepLoai'].value_counts().to_dict()
        return stats

    def import_scores_from_csv(self, file_path) -> tuple:
        try:
            df_import = pd.read_csv(file_path)
            required_cols = {'MaSV', 'MaHocPhan', 'HocKy', 'NamHoc', 'Diem'}
            if not required_cols.issubset(set(df_import.columns)):
                return False, "File CSV không đúng định dạng cột."
            
            conn = get_connection()
            cursor = conn.cursor()
            for _, row in df_import.iterrows():
                cursor.execute(
                    "REPLACE INTO BangDiem (MaSV, MaHocPhan, HocKy, NamHoc, Diem) VALUES (?, ?, ?, ?, ?)",
                    (row['MaSV'], row['MaHocPhan'], row['HocKy'], row['NamHoc'], row['Diem'])
                )
            conn.commit()
            conn.close()
            return True, f"Đã nhập thành công {len(df_import)} bản ghi."
        except Exception as e:
            return False, str(e)
