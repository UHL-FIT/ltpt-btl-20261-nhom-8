import pandas as pd
from models.database import get_connection

class SubjectModel:
    """Model xử lý thông tin bảng MonHoc"""
    
    def get_all_subjects(self) -> pd.DataFrame:
        """Lấy danh sách môn học cố định"""
        conn = get_connection()
        query = "SELECT * FROM MonHoc"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_subject_dict(self) -> dict:
        """Trả về dict ánh xạ MaHocPhan -> Tên (để hiển thị combobox)"""
        df = self.get_all_subjects()
        return pd.Series(df.TenHocPhan.values, index=df.MaHocPhan).to_dict()
