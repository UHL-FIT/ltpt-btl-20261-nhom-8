from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np

# Import hàm get_logger từ app/utils/logger.py.
# File database.py dùng logger này để ghi lại quá trình khởi tạo và lỗi SQLite.
from app.utils.logger import get_logger


logger = get_logger(__name__)


class AppDatabase:
    def __init__(self, db_path: str | Path | None = None):
        """Khởi tạo đối tượng quản lý database và chuẩn bị đường dẫn file SQLite."""
        default_path = Path(__file__).parent.parent / "data" / "app_data.db"
        self.db_path = Path(db_path) if db_path is not None else default_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Khởi tạo database tại %s", self.db_path)
        try:
            self._initialize()
        except Exception:
            logger.exception("Lỗi khi khởi tạo database tại %s", self.db_path)
            raise

    def _connect(self) -> sqlite3.Connection:
        """Mở một kết nối SQLite tới file database hiện tại."""
        return sqlite3.connect(self.db_path)

    def _initialize(self) -> None:
        """Tạo bảng, cập nhật cấu trúc cũ và nạp dữ liệu mẫu ban đầu."""
        # Gọi hàm để kết nối tới database (sqlite)
        with self._connect() as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    student_name TEXT NOT NULL,
                    class_name TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    birth_date TEXT NOT NULL,
                    email TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS courses (
                    course_id TEXT PRIMARY KEY,
                    course_name TEXT NOT NULL,
                    credits INTEGER NOT NULL,
                    semester TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS scores (
                    score_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL UNIQUE,
                    student_name TEXT NOT NULL,
                    class_name TEXT NOT NULL,
                    score REAL NOT NULL,
                    grade TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS score_details (
                    score_detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    course_id TEXT NOT NULL,
                    course_name TEXT NOT NULL,
                    credits INTEGER NOT NULL,
                    semester TEXT NOT NULL,
                    school_year TEXT NOT NULL,
                    score REAL NOT NULL,
                    UNIQUE(student_id, course_id, school_year)
                );

                CREATE TABLE IF NOT EXISTS app_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
            logger.info("Đã tạo hoặc kiểm tra xong cấu trúc bảng SQLite.")


            # Nếu không có database thì sẽ tạo lại database nhưng do database mới tạo
            # chưa có dữ liệu nên gọi hàm _seed_default_data(conn) nếu bảng chưa có dữ liệu
            self._seed_default_data(conn)

            self._rebuild_score_summaries(conn)

            conn.commit()
            logger.info("Đã khởi tạo database và đồng bộ dữ liệu ban đầu thành công.")

    def _seed_default_data(self, conn: sqlite3.Connection) -> None:
        """Nạp dữ liệu mẫu nếu database còn trống."""
        seeded_row = conn.execute(
            "SELECT value FROM app_meta WHERE key = ?",
            ("seeded",),
        ).fetchone()
        if seeded_row and seeded_row[0] == "1":
            return

        has_existing_data = any(
            conn.execute(f"SELECT 1 FROM {table} LIMIT 1").fetchone() is not None
            for table in ("students", "courses", "score_details")
        )
        if has_existing_data:
            conn.execute(
                "INSERT OR REPLACE INTO app_meta (key, value) VALUES (?, ?)",
                ("seeded", "1"),
            )
            return

        conn.executemany(
            """
            INSERT INTO students (
                student_id, student_name, class_name, gender, birth_date, email
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                ("SV001", "Nguyễn Văn A", "CNTT01", "Nam", "01/01/2005", "sv001@gmail.com"),
                ("SV002", "Trần Thị B", "CNTT01", "Nữ", "12/03/2005", "sv002@gmail.com"),
                ("SV003", "Lê Văn C", "CNTT02", "Nam", "05/06/2004", "sv003@gmail.com"),
                ("SV004", "Phạm Văn D", "CNTT03", "Nam", "22/08/2004", "sv004@gmail.com"),
            ],
        )

        conn.executemany(
            """
            INSERT INTO courses (
                course_id, course_name, credits, semester
            ) VALUES (?, ?, ?, ?)
            """,
            [
                ("HP001", "Lập trình Python", 3, "HK1"),
                ("HP002", "Cơ sở dữ liệu", 3, "HK1"),
                ("HP003", "Toán cao cấp", 2, "HK2"),
                ("HP004", "Mạng máy tính", 3, "HK2"),
            ],
        )

        conn.executemany(
            """
            INSERT INTO score_details (
                student_id, course_id, course_name, credits, semester, school_year, score
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("SV001", "HP001", "Lập trình Python", 3, "HK1", "2024-2025", 8.5),
                ("SV001", "HP002", "Cơ sở dữ liệu", 3, "HK1", "2024-2025", 7.8),
                ("SV002", "HP002", "Cơ sở dữ liệu", 3, "HK1", "2024-2025", 7.2),
                ("SV002", "HP003", "Toán cao cấp", 2, "HK2", "2024-2025", 6.9),
                ("SV003", "HP003", "Toán cao cấp", 2, "HK2", "2024-2025", 6.8),
                ("SV003", "HP004", "Mạng máy tính", 3, "HK2", "2024-2025", 7.5),
                ("SV004", "HP001", "Lập trình Python", 3, "HK1", "2024-2025", 9.0),
                ("SV004", "HP004", "Mạng máy tính", 3, "HK2", "2024-2025", 8.7),
            ],
        )

        conn.execute(
            "INSERT OR REPLACE INTO app_meta (key, value) VALUES (?, ?)",
            ("seeded", "1"),
        )

    def fetch_students(self) -> list[tuple[str, str, str, str, str, str]]:
        """Lấy danh sách sinh viên từ bảng students."""
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT student_id, student_name, class_name, gender, birth_date, email
                FROM students
                ORDER BY student_id
                """
            )
            return [tuple(row) for row in cursor.fetchall()]

    def fetch_courses(self) -> list[tuple[str, str, int, str]]:
        """Lấy danh sách học phần từ bảng courses."""
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT course_id, course_name, credits, semester
                FROM courses
                ORDER BY course_id
                """
            )
            return [tuple(row) for row in cursor.fetchall()]

    def fetch_course(self, course_id: str) -> tuple[str, str, int, str] | None:
        """Lấy một học phần theo mã học phần."""
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT course_id, course_name, credits, semester
                FROM courses
                WHERE course_id = ?
                """,
                (course_id,),
            )
            row = cursor.fetchone()
            return tuple(row) if row else None

    def fetch_scores(self) -> list[tuple[str, str, str, float, str]]:
        """Lấy bảng điểm tổng hợp theo sinh viên từ bảng scores."""
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT student_id, student_name, class_name, score, grade
                FROM scores
                ORDER BY student_id
                """
            )
            return [tuple(row) for row in cursor.fetchall()]

    def fetch_student(self, student_id: str) -> tuple[str, str, str, str, str, str] | None:
        """Lấy một sinh viên theo mã sinh viên."""
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT student_id, student_name, class_name, gender, birth_date, email
                FROM students
                WHERE student_id = ?
                """,
                (student_id,),
            )
            row = cursor.fetchone()
            return tuple(row) if row else None

    def fetch_score_details(self, student_id: str) -> list[tuple[int, str, str, int, str, str, float]]:
        """Lấy danh sách điểm chi tiết của một sinh viên."""
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT score_detail_id, course_id, course_name, credits, semester, school_year, score
                FROM score_details
                WHERE student_id = ?
                ORDER BY school_year, course_id
                """,
                (student_id,),
            )
            return [tuple(row) for row in cursor.fetchall()]

    def fetch_score_detail(self, score_detail_id: int) -> tuple[int, str, str, str, int, str, str, float] | None:
        """Lấy một bản ghi điểm chi tiết theo ID."""
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT score_detail_id, student_id, course_id, course_name, credits, semester, school_year, score
                FROM score_details
                WHERE score_detail_id = ?
                """,
                (score_detail_id,),
            )
            row = cursor.fetchone()
            return tuple(row) if row else None

    def delete_student(self, student_id: str) -> None:
        """Xóa sinh viên và các dữ liệu liên quan."""
        with self._connect() as conn:
            conn.execute("DELETE FROM score_details WHERE student_id = ?", (student_id,))
            conn.execute("DELETE FROM scores WHERE student_id = ?", (student_id,))
            conn.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            conn.commit()

    def insert_student(self, student_data: dict[str, str]) -> None:
        """Thêm một sinh viên mới vào bảng students."""
        student_id = student_data["student_id"].upper()
        class_name = student_data["class_name"].upper()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO students (
                    student_id, student_name, class_name, gender, birth_date, email
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    student_id,
                    student_data["student_name"],
                    class_name,
                    student_data["gender"],
                    student_data["birth_date"],
                    student_data["email"],
                ),
            )
            self._rebuild_score_summary(conn, student_id)
            conn.commit()

    def update_student(self, original_student_id: str, student_data: dict[str, str]) -> None:
        """Cập nhật thông tin sinh viên và đồng bộ dữ liệu liên quan."""
        student_id = original_student_id.upper()
        class_name = student_data["class_name"].upper()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE students
                SET student_name = ?, class_name = ?, gender = ?, birth_date = ?, email = ?
                WHERE student_id = ?
                """,
                (
                    student_data["student_name"],
                    class_name,
                    student_data["gender"],
                    student_data["birth_date"],
                    student_data["email"],
                    student_id,
                ),
            )
            conn.execute(
                """
                UPDATE score_details
                SET student_id = ?
                WHERE student_id = ?
                """,
                (
                    student_id,
                    student_id,
                ),
            )
            conn.execute(
                """
                UPDATE scores
                SET student_name = ?, class_name = ?
                WHERE student_id = ?
                """,
                (
                    student_data["student_name"],
                    class_name,
                    student_id,
                ),
            )
            self._rebuild_score_summary(conn, student_id)
            conn.commit()

    def delete_course(self, course_id: str) -> None:
        """Xóa học phần và cập nhật lại các bảng liên quan."""
        with self._connect() as conn:
            student_ids = [
                row[0]
                for row in conn.execute(
                    "SELECT DISTINCT student_id FROM score_details WHERE course_id = ?",
                    (course_id,),
                ).fetchall()
            ]
            conn.execute("DELETE FROM score_details WHERE course_id = ?", (course_id,))
            conn.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
            for student_id in student_ids:
                self._rebuild_score_summary(conn, student_id)
            conn.commit()

    def insert_course(self, course_data: dict[str, str]) -> None:
        """Thêm một học phần mới vào bảng courses."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO courses (
                    course_id, course_name, credits, semester
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    course_data["course_id"],
                    course_data["course_name"],
                    int(course_data["credits"]),
                    course_data["semester"],
                ),
            )
            conn.commit()

    def update_course(self, original_course_id: str, course_data: dict[str, str]) -> None:
        """Cập nhật học phần và đồng bộ tên/số tín chỉ trong điểm chi tiết."""
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE courses
                SET course_name = ?, credits = ?, semester = ?
                WHERE course_id = ?
                """,
                (
                    course_data["course_name"],
                    int(course_data["credits"]),
                    course_data["semester"],
                    original_course_id,
                ),
            )
            conn.execute(
                """
                UPDATE score_details
                SET course_name = ?, credits = ?, semester = ?
                WHERE course_id = ?
                """,
                (
                    course_data["course_name"],
                    int(course_data["credits"]),
                    course_data["semester"],
                    original_course_id,
                ),
            )
            student_ids = [
                row[0]
                for row in conn.execute(
                    "SELECT DISTINCT student_id FROM score_details WHERE course_id = ?",
                    (original_course_id,),
                ).fetchall()
            ]
            for student_id in student_ids:
                self._rebuild_score_summary(conn, student_id)
            conn.commit()

    def insert_score_detail(self, detail_data: dict[str, str]) -> None:
        """Thêm một bản ghi điểm chi tiết cho sinh viên."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO score_details (
                    student_id, course_id, course_name, credits, semester, school_year, score
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    detail_data["student_id"],
                    detail_data["course_id"],
                    detail_data["course_name"],
                    int(detail_data["credits"]),
                    detail_data["semester"],
                    detail_data["school_year"],
                    float(detail_data["score"]),
                ),
            )
            self._rebuild_score_summary(conn, detail_data["student_id"])
            conn.commit()

    def update_score_detail(self, score_detail_id: int, detail_data: dict[str, str]) -> None:
        """Cập nhật một bản ghi điểm chi tiết."""
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE score_details
                SET course_id = ?, course_name = ?, credits = ?, semester = ?, school_year = ?, score = ?
                WHERE score_detail_id = ?
                """,
                (
                    detail_data["course_id"],
                    detail_data["course_name"],
                    int(detail_data["credits"]),
                    detail_data["semester"],
                    detail_data["school_year"],
                    float(detail_data["score"]),
                    score_detail_id,
                ),
            )
            self._rebuild_score_summary(conn, detail_data["student_id"])
            conn.commit()

    def delete_score_detail(self, score_detail_id: int) -> None:
        """Xóa một bản ghi điểm chi tiết và tính lại CPA."""
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT student_id FROM score_details WHERE score_detail_id = ?",
                (score_detail_id,),
            )
            row = cursor.fetchone()
            student_id = row[0] if row else None
            conn.execute("DELETE FROM score_details WHERE score_detail_id = ?", (score_detail_id,))
            if student_id:
                self._rebuild_score_summary(conn, student_id)
            conn.commit()

    def _rebuild_score_summaries(self, conn: sqlite3.Connection) -> None:
        """Tính lại toàn bộ bảng scores từ dữ liệu score_details."""
        conn.execute("DELETE FROM scores")
        student_ids = [row[0] for row in conn.execute("SELECT student_id FROM students ORDER BY student_id")]
        for student_id in student_ids:
            self._rebuild_score_summary(conn, student_id)

    def _rebuild_score_summary(self, conn: sqlite3.Connection, student_id: str) -> None:
        """Tính lại CPA và xếp loại cho một sinh viên."""
        student = conn.execute(
            """
            SELECT student_name, class_name
            FROM students
            WHERE student_id = ?
            """,
            (student_id,),
        ).fetchone()
        if not student:
            conn.execute("DELETE FROM scores WHERE student_id = ?", (student_id,))
            return

        student_name, class_name = student
        details = conn.execute(
            """
            SELECT credits, score
            FROM score_details
            WHERE student_id = ?
            """,
            (student_id,),
        ).fetchall()

        if not details:
            cpa = 0.0
            grade = "Chưa có điểm"
        else:
            credits = np.array([float(row[0]) for row in details], dtype=float)
            scores = np.array([float(row[1]) for row in details], dtype=float)
            total_credits = credits.sum()
            # Công thức tính điểm cpa
            cpa = float(np.dot(credits, scores) / total_credits) if total_credits else 0.0
            grade = self._grade_from_cpa(cpa)
        conn.execute(
            """
            INSERT INTO scores (student_id, student_name, class_name, score, grade)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(student_id) DO UPDATE SET
                student_name = excluded.student_name,
                class_name = excluded.class_name,
                score = excluded.score,
                grade = excluded.grade
            """,
            (student_id, student_name, class_name, round(cpa, 2), grade),
        )

    def _grade_from_cpa(self, cpa: float) -> str:
        """Xếp loại học tập dựa trên CPA."""
        conditions = [
            cpa >= 9.0,
            cpa >= 8.0,
            cpa >= 6.0,
            cpa >= 5.0,
        ]
        choices = ["Xuất sắc", "Giỏi", "Khá", "Trung bình"]
        return str(np.select(conditions, choices, default="Yếu"))
