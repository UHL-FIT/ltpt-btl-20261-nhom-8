import sqlite3
import os
from utils.logger import setup_logger

logger = setup_logger("database")

DB_PATH = "data/database.db"

def get_connection():
    # Đảm bảo thư mục data tồn tại
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)

def initialize_database():
    """Khởi tạo cấu trúc bảng nếu chưa tồn tại, và nạp dữ liệu mẫu."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Bảng SinhVien
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS SinhVien (
                MaSV TEXT PRIMARY KEY,
                HoTen TEXT NOT NULL,
                GioiTinh TEXT,
                NgaySinh TEXT,
                Lop TEXT
            )
        ''')

        # Bảng MonHoc
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS MonHoc (
                MaHocPhan TEXT PRIMARY KEY,
                TenHocPhan TEXT NOT NULL,
                SoTinChi INTEGER NOT NULL
            )
        ''')

        # Bảng BangDiem
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS BangDiem (
                MaSV TEXT,
                MaHocPhan TEXT,
                HocKy TEXT,
                NamHoc TEXT,
                Diem REAL,
                PRIMARY KEY (MaSV, MaHocPhan),
                FOREIGN KEY (MaSV) REFERENCES SinhVien(MaSV),
                FOREIGN KEY (MaHocPhan) REFERENCES MonHoc(MaHocPhan)
            )
        ''')
        
        conn.commit()
        
        # Kiểm tra xem có cần nạp dữ liệu mẫu không (dựa trên số lượng bản ghi)
        cursor.execute("SELECT COUNT(*) FROM MonHoc")
        count_mh = cursor.fetchone()[0]
        
        if count_mh == 0:
            logger.info("Bảng dữ liệu trống, tiến hành nạp dữ liệu mẫu...")
            _seed_dummy_data(cursor)
            conn.commit()
            logger.info("Nạp dữ liệu mẫu thành công.")
        else:
            logger.info("Cơ sở dữ liệu đã có dữ liệu sẵn.")
            
    except Exception as e:
        logger.error(f"Lỗi khởi tạo database: {e}")
    finally:
        conn.close()

def _seed_dummy_data(cursor):
    # Dữ liệu môn học cố định (từ plan.txt)
    mon_hocs = [
        ("MH001", "Toán cao cấp", 3),
        ("MH002", "Lập trình căn bản", 3),
        ("MH003", "Cơ sở dữ liệu", 3),
        ("MH004", "Tiếng Anh 1", 2)
    ]
    cursor.executemany("INSERT INTO MonHoc VALUES (?, ?, ?)", mon_hocs)

    # Sinh viên mẫu
    sinh_viens = [
        ("SV001", "Nguyen Van A", "Nam", "21/08/2005", "DH10TT02A"),
        ("SV002", "Nguyen Van B", "Nam", "15/09/2006", "DH10TT02B"),
        ("SV003", "Nguyen Van C", "Nữ", "01/07/2004", "DH10TT02E")
    ]
    cursor.executemany("INSERT INTO SinhVien VALUES (?, ?, ?, ?, ?)", sinh_viens)

    # Bảng điểm mẫu
    diems = [
        ("SV001", "MH001", "HK1", "2024-2025", 8.5),
        ("SV001", "MH002", "HK1", "2024-2025", 7.5),
        ("SV002", "MH003", "HK1", "2024-2025", 9.0),
        ("SV003", "MH004", "HK2", "2024-2025", 6.5)
    ]
    cursor.executemany("INSERT INTO BangDiem VALUES (?, ?, ?, ?, ?)", diems)

# Tự động gọi khởi tạo khi import module này
initialize_database()
