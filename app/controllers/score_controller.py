from __future__ import annotations

import csv

from app.utils.logger import get_logger


logger = get_logger(__name__)


class ScoreController:
    # Chuyen tu score_page.py - phan lay du lieu, xuat CSV va thao tac bang diem tong hop.
    def __init__(self, database):
        self.database = database
        logger.info("Khởi tạo ScoreController.")

    def fetch_scores(self):
        return self.database.fetch_scores()

    def export_csv(self, file_path):
        scores = self.database.fetch_scores()
        exported_rows = 0

        with open(file_path, "w", encoding="utf-8-sig", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([
                "Mã sinh viên",
                "Họ tên",
                "Lớp",
                "Điểm GPA",
                "Xếp loại",
                "Mã học phần",
                "Tên học phần",
                "Tín chỉ",
                "Học kỳ",
                "Năm học",
                "Điểm số",
            ])

            for score in scores:
                student_id, student_name, class_name, gpa, grade = score
                score_details = self.database.fetch_score_details(student_id)

                if not score_details:
                    writer.writerow([
                        student_id,
                        student_name,
                        class_name,
                        gpa,
                        grade,
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ])
                    exported_rows += 1
                    continue

                for detail in score_details:
                    _, course_id, course_name, credits, semester, school_year, score_value = detail
                    writer.writerow([
                        student_id,
                        student_name,
                        class_name,
                        gpa,
                        grade,
                        course_id,
                        course_name,
                        credits,
                        semester,
                        school_year,
                        score_value,
                    ])
                    exported_rows += 1

        logger.info("Đã xuất CSV bảng điểm tổng hợp: %s (%s dòng).", file_path, exported_rows)
        return exported_rows
