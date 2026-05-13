from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_csv_required(path: str | Path, expected_columns: list[str]) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    actual_columns = list(df.columns)
    
    if actual_columns != expected_columns:
        raise ValueError(
            f"File CSV không đúng định dạng chuẩn.\n\n"
            f"Yêu cầu các cột (theo thứ tự): {', '.join(expected_columns)}\n"
            f"Thực tế: {', '.join(actual_columns)}"
        )
    return df


def export_csv(path: str | Path, rows: list[dict], columns: list[str]) -> None:
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False, encoding="utf-8-sig")


def generate_template_csv(path: str | Path, columns: list[str], sample_rows: list[dict] | None = None) -> None:
    export_csv(path, sample_rows or [], columns)
