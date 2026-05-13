import pandas as pd
import numpy as np
import os

class StudentModel:
    """Model for managing student academic data.
    Data is stored in a CSV file with columns:
    ['MSSV', 'HoTen', 'GioiTinh', 'Mon1', 'TinChi1', 'Diem1', ..., 'MonN', 'TinChiN', 'DiemN']
    """

    def __init__(self, csv_path: str = None):
        # Default CSV path inside the project data folder
        if csv_path is None:
            csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'students.csv')
        self.csv_path = os.path.abspath(csv_path)
        self.df = pd.DataFrame()
        self.load_data()

    def load_data(self):
        """Load CSV data into a DataFrame. If file missing, create empty DataFrame with expected columns."""
        if os.path.exists(self.csv_path):
            self.df = pd.read_csv(self.csv_path)
        else:
            # Create an empty DataFrame with generic columns for demonstration
            self.df = pd.DataFrame(columns=['MSSV', 'HoTen', 'GioiTinh', 'GPA'])
        # Ensure GPA column exists
        if 'GPA' not in self.df.columns:
            self.df['GPA'] = np.nan

    def save_data(self):
        """Save the current DataFrame to CSV."""
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        self.df.to_csv(self.csv_path, index=False)

    def add_student(self, student_dict: dict):
        """Add a new student record. `student_dict` keys must match DataFrame columns."""
        self.df = pd.concat([self.df, pd.DataFrame([student_dict])], ignore_index=True)
        self.recalculate_gpa()
        self.save_data()

    def update_student(self, index: int, student_dict: dict):
        """Update an existing student at DataFrame index."""
        for key, value in student_dict.items():
            self.df.at[index, key] = value
        self.recalculate_gpa()
        self.save_data()

    def delete_student(self, index: int):
        """Delete a student record by index."""
        self.df = self.df.drop(index).reset_index(drop=True)
        self.save_data()

    def recalculate_gpa(self):
        """Calculate GPA for each student using vectorized NumPy operations.
        Expected columns: for each subject there are 'DiemX' and 'TinChiX' columns.
        GPA = sum(Diem*TinChi) / sum(TinChi).
        """
        # Identify score and credit columns by pattern
        score_cols = [col for col in self.df.columns if col.startswith('Diem')]
        credit_cols = [col for col in self.df.columns if col.startswith('TinChi')]
        if not score_cols or not credit_cols:
            # No detailed scores, cannot compute GPA
            self.df['GPA'] = np.nan
            return
        scores = self.df[score_cols].to_numpy(dtype=float)
        credits = self.df[credit_cols].to_numpy(dtype=float)
        weighted = np.nansum(scores * credits, axis=1)
        total_credits = np.nansum(credits, axis=1)
        gpa = np.divide(weighted, total_credits, out=np.full_like(weighted, np.nan), where=total_credits != 0)
        self.df['GPA'] = np.round(gpa, 2)

    def classify(self):
        """Add a 'XepLoai' column based on GPA thresholds.
        - GPA >= 8.0: 'Giỏi'
        - 6.5 <= GPA < 8.0: 'Khá'
        - 5.0 <= GPA < 6.5: 'Trung Bình'
        - otherwise: 'Yếu'
        """
        conditions = [
            (self.df['GPA'] >= 8.0),
            (self.df['GPA'] >= 6.5) & (self.df['GPA'] < 8.0),
            (self.df['GPA'] >= 5.0) & (self.df['GPA'] < 6.5)
        ]
        choices = ['Giỏi', 'Khá', 'Trung Bình']
        self.df['XepLoai'] = np.select(conditions, choices, default='Yếu')

    def top_students(self, n: int = 10):
        """Return top `n` students sorted by GPA descending."""
        return self.df.sort_values(by='GPA', ascending=False).head(n)
