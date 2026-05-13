import re
from datetime import datetime

def validate_empty(*args) -> bool:
    """Kiểm tra xem có bất kỳ chuỗi nào bị rỗng không."""
    for arg in args:
        if not arg or str(arg).strip() == "":
            return False
    return True

def validate_date(date_str: str) -> bool:
    """Kiểm tra định dạng ngày (dd/mm/yyyy)."""
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def validate_score(score_str: str) -> bool:
    """Kiểm tra điểm số có phải là số thực từ 0 đến 10 hay không."""
    try:
        score = float(score_str)
        return 0.0 <= score <= 10.0
    except ValueError:
        return False
