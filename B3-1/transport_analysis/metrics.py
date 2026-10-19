"""계산만 수행하는 함수. 같은 입력은 같은 결과를 반환한다."""

import pandas as pd

from .clean import MODES


def daily_features(data: pd.DataFrame) -> pd.DataFrame:
    result = data.copy(deep=True).sort_values(["mode", "date"])
    result["weekday"] = result["date"].dt.dayofweek
    result["month"] = result["date"].dt.month
    result["weekend"] = result["weekday"] >= 5
    result["index"] = result["value"] / result.groupby("mode")["value"].transform("mean") * 100
    result["baseline"] = result.groupby(["mode", "month", "weekday"])["value"].transform("mean")
    # 전체 2025년을 사용하는 사후 탐색 기준. 온라인 이상 탐지/예측에 사용하지 않는다.
    result["deviation_pct"] = (
        result["value"] / result["baseline"].replace(0, float("nan")) - 1
    ) * 100
    result["rolling7"] = float("nan")
    for mode in MODES:
        mask = result["mode"] == mode
        series = result.loc[mask].set_index("date")["value"].asfreq("D")
        rolling = series.rolling(7, min_periods=7).mean()
        result.loc[mask, "rolling7"] = result.loc[mask, "date"].map(rolling).to_numpy()
    return result.reset_index(drop=True)


def summarize(data: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    enriched = daily_features(data)
    stats = {
        "period": {"start": "2025-01-01", "end": "2025-12-31"},
        "count": len(data),
        "modes": {},
        "anomaly_rule": "같은 월·요일 평균 대비 절대 편차 >= 30%. 사후 탐색, 인과·예측 아님",
    }
    for mode in MODES:
        part = enriched[enriched["mode"] == mode]
        weekend = float(part.loc[part["weekend"], "value"].mean())
        weekday = float(part.loc[~part["weekend"], "value"].mean())
        max_row, min_row = part.loc[part["value"].idxmax()], part.loc[part["value"].idxmin()]
        monthly = {str(m): float(v) for m, v in part.groupby("month")["value"].mean().items()}
        unusual = part.loc[part["deviation_pct"].abs() >= 30].copy()
        unusual["abs_deviation"] = unusual["deviation_pct"].abs()
        unusual = unusual.sort_values(["abs_deviation", "date"], ascending=[False, True]).head(5)
        stats["modes"][mode] = {
            "count": len(part),
            "total": int(part["value"].sum()),
            "average": float(part["value"].mean()),
            "minimum": {
                "date": min_row["date"].strftime("%Y-%m-%d"),
                "value": int(min_row["value"]),
            },
            "maximum": {
                "date": max_row["date"].strftime("%Y-%m-%d"),
                "value": int(max_row["value"]),
            },
            "weekday_average": weekday,
            "weekend_average": weekend,
            "weekend_change_pct": (weekend / weekday - 1) * 100 if weekday else None,
            "weekday_means": {
                str(k): float(v) for k, v in part.groupby("weekday")["value"].mean().items()
            },
            "monthly_daily_means": monthly,
            "monthly_peak_trough_ratio": max(monthly.values()) / min(monthly.values())
            if min(monthly.values())
            else None,
            "anomaly_count": int((part["deviation_pct"].abs() >= 30).sum()),
            "top_unusual": [
                {
                    "date": r.date.strftime("%Y-%m-%d"),
                    "value": int(r.value),
                    "baseline": float(r.baseline),
                    "deviation_pct": float(r.deviation_pct),
                }
                for r in unusual.itertuples()
            ],
        }
    residuals = enriched.pivot(index="date", columns="mode", values="deviation_pct")
    stats["joint_low_days"] = (
        residuals.index[(residuals <= -20).all(axis=1)].strftime("%Y-%m-%d").tolist()
    )
    return stats, enriched
