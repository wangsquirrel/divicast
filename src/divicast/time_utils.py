from __future__ import annotations

from datetime import datetime


def check_naive_datetime(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        raise ValueError(f"{dt} must be a naive datetime that has already been normalized ")
    return dt
