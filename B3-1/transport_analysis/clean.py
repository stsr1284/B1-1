"""일별 집계본에 대한 공통 데이터 계약. 오류를 보간·0으로 숨기지 않는다."""

import numpy as np
import pandas as pd

MODES = ("bike", "bus", "subway")
START, END = "2025-01-01", "2025-12-31"


def clean_observations(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    required = {"date", "mode", "value"}
    if not required <= set(frame.columns):
        raise ValueError(f"필수 컬럼 누락: {sorted(required - set(frame.columns))}")
    data = frame.copy(deep=True)
    if data[list(required)].isna().any().any():
        raise ValueError("날짜·수단·값 결측")
    if not data["date"].astype(str).str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
        raise ValueError("날짜는 YYYY-MM-DD여야 합니다")
    data["date"] = pd.to_datetime(data["date"], format="%Y-%m-%d", errors="raise")
    if set(data["mode"]) != set(MODES):
        raise ValueError("bike/bus/subway 세 수단이 모두 필요합니다")
    if data.duplicated(["date", "mode"]).any():
        raise ValueError("날짜·수단 중복: 합산하지 않고 원인 확인 필요")
    values = pd.to_numeric(data["value"], errors="raise")
    if not np.isfinite(values).all() or (values < 0).any() or (values % 1 != 0).any():
        raise ValueError("이용량은 유한한 0 이상의 정수여야 합니다")
    data["value"] = values.astype("int64")
    expected = pd.date_range(START, END, freq="D")
    for mode in MODES:
        actual = pd.DatetimeIndex(data.loc[data["mode"] == mode, "date"]).sort_values()
        if not actual.equals(expected):
            raise ValueError(f"{mode}: 2025년 날짜 누락 또는 범위 초과")
    data["memo"] = ""
    data = (
        data[["date", "mode", "value", "memo"]].sort_values(["date", "mode"]).reset_index(drop=True)
    )
    flags = {}
    for mode in MODES:
        subset = data[data["mode"] == mode]
        q1, q3 = subset["value"].quantile([0.25, 0.75])
        lower, upper = float(q1 - 1.5 * (q3 - q1)), float(q3 + 1.5 * (q3 - q1))
        unusual = subset[(subset["value"] < lower) | (subset["value"] > upper)]
        flags[mode] = {
            "lower": lower,
            "upper": upper,
            "count": len(unusual),
            "dates": unusual["date"].dt.strftime("%Y-%m-%d").tolist(),
            "action": "유지",
        }
    quality = {
        "input_rows": len(frame),
        "output_rows": len(data),
        "days_per_mode": 365,
        "missing_dates": 0,
        "missing_values": 0,
        "duplicate_keys": 0,
        "negative_values": 0,
        "imputed_rows": 0,
        "removed_rows": 0,
        "zero_values": int((data["value"] == 0).sum()),
        "iqr_flags": flags,
        "policy": "IQR 탐색 후보는 원본과 대조하고 유지. 교통 수요 극값을 오류로 단정하지 않음",
    }
    return data, quality
