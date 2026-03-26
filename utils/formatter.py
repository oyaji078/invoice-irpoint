from datetime import datetime
from typing import Optional


def format_idr(value: float) -> str:
    try:
        value_int = int(round(value))
    except Exception:
        value_int = 0
    return f"Rp {value_int:,}".replace(",", ".")


def format_date(date_str: str) -> str:
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%d %b %Y")
    except Exception:
        return date_str


def format_percent(value: Optional[float]) -> str:
    if value is None:
        return "0%"
    return f"{value:.0f}%"
