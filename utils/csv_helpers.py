from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_csv_required(path: str | Path, required_columns: list[str]) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError("File CSV thiếu cột bắt buộc: " + ", ".join(missing))
    return df


def export_csv(path: str | Path, rows: list[dict], columns: list[str]) -> None:
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False, encoding="utf-8-sig")
