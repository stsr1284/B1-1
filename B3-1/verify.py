"""pandas 분석 코드와 독립적으로 표준 라이브러리로 결과·인계·링크 검증."""

import argparse
import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from statistics import mean


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual: float, expected: float, label: str) -> None:
    if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-9):
        raise ValueError(f"불일치 {label}: {actual} != {expected}")


def verify(root: Path, seed_dir: Path | None = None, raw: bool = False) -> dict:
    sources = json.loads((root / "data/sources.json").read_text())
    manifest = json.loads((root / "data/processed/manifest.json").read_text())
    stats = json.loads((root / "outputs/statistics.json").read_text())
    data = root / "data/processed/observations.csv"
    if digest(data) != manifest["dataset_sha256"]:
        raise ValueError("정제본 해시 불일치")
    if digest(root / "data/sources.json") != manifest["sources_sha256"]:
        raise ValueError("출처 manifest 해시 불일치")
    with data.open(newline="") as stream:
        records = list(csv.DictReader(stream))
    by_mode = defaultdict(list)
    source_values = {}
    for source in sources["sources"]:
        path = root / "data/aggregated" / source["file"]
        if digest(path) != source["aggregate_sha256"]:
            raise ValueError("집계본 해시 불일치")
        with path.open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        if sum(int(r["value"]) for r in rows) != source["total"]:
            raise ValueError("원본 집계 합계 불일치")
        if sum(int(r["source_rows"]) for r in rows) != source["raw_rows"]:
            raise ValueError("원본 집계 행 수 불일치")
        if raw:
            raw_path = root / "data/raw" / source["file"]
            if digest(raw_path) != source["sha256"]:
                raise ValueError("원본 SHA-256 불일치")
            counts = defaultdict(int)
            count_rows = 0
            with raw_path.open(encoding=source["encoding"], newline="") as stream:
                for r in csv.DictReader(stream):
                    day = r["대여일자"] if source["mode"] == "bike" else r["사용일자"]
                    if len(day) == 8:
                        day = f"{day[:4]}-{day[4:6]}-{day[6:]}"
                    counts[day] += int(
                        r["대여건수"] if source["mode"] == "bike" else r["승차총승객수"]
                    )
                    count_rows += 1
            if (
                counts != {r["date"]: int(r["value"]) for r in rows}
                or count_rows != source["raw_rows"]
            ):
                raise ValueError("원본 독립 재집계 불일치")
        for r in rows:
            key = (r["date"], r["mode"])
            if key in source_values:
                raise ValueError("집계 파일 간 중복 날짜")
            source_values[key] = int(r["value"])
    if len(records) != 1095 or len(source_values) != 1095:
        raise ValueError("2025년 3수단 1,095행 불충족")
    seen = set()
    for row in records:
        key = (row["date"], row["mode"])
        if key in seen or source_values[key] != int(row["value"]):
            raise ValueError("정제본과 공식 일별 집계본 불일치")
        seen.add(key)
        by_mode[row["mode"]].append((date.fromisoformat(row["date"]), int(row["value"])))
    deviations = defaultdict(dict)
    for mode, rows in by_mode.items():
        s = stats["modes"][mode]
        values = [v for _, v in rows]
        if s["count"] != 365 or s["total"] != sum(values):
            raise ValueError("건수·합계 불일치")
        close(s["average"], mean(values), mode + " average")
        weekday = mean([v for d, v in rows if d.weekday() < 5])
        weekend = mean([v for d, v in rows if d.weekday() >= 5])
        close(s["weekday_average"], weekday, mode + " weekday")
        close(s["weekend_average"], weekend, mode + " weekend")
        close(s["weekend_change_pct"], (weekend / weekday - 1) * 100, mode + " change")
        for month in range(1, 13):
            close(
                s["monthly_daily_means"][str(month)],
                mean([v for d, v in rows if d.month == month]),
                f"{mode} month {month}",
            )
        for day in range(7):
            close(
                s["weekday_means"][str(day)],
                mean([v for d, v in rows if d.weekday() == day]),
                f"{mode} weekday {day}",
            )
        for field, fn in [("minimum", min), ("maximum", max)]:
            value = fn(values)
            first = next(d.isoformat() for d, v in rows if v == value)
            if s[field] != {"date": first, "value": value}:
                raise ValueError("극값 불일치")
        groups = defaultdict(list)
        for d, v in rows:
            groups[(d.month, d.weekday())].append(v)
        for d, v in rows:
            deviations[mode][d.isoformat()] = (v / mean(groups[(d.month, d.weekday())]) - 1) * 100
        if s["anomaly_count"] != sum(abs(v) >= 30 for v in deviations[mode].values()):
            raise ValueError("이상일 개수 불일치")
        for row in s["top_unusual"]:
            close(row["deviation_pct"], deviations[mode][row["date"]], mode + " deviation")
    joint = sorted(d for d in deviations["bike"] if all(deviations[m][d] <= -20 for m in by_mode))
    if stats["joint_low_days"] != joint:
        raise ValueError("공동 감소 날짜 불일치")
    with (root / "outputs/daily_metrics.csv").open(newline="") as stream:
        features = list(csv.DictReader(stream))
    if len(features) != len(records):
        raise ValueError("일별 지표 행 수 불일치")
    observed = {(r["date"], r["mode"]): int(r["value"]) for r in records}
    from datetime import timedelta

    for r in features:
        day, mode = date.fromisoformat(r["date"]), r["mode"]
        window = [observed.get(((day - timedelta(days=i)).isoformat(), mode)) for i in range(7)]
        if None in window:
            if r["rolling7"] != "":
                raise ValueError("이동평균 시작 구간은 비어야 함")
        else:
            close(float(r["rolling7"]), mean(window), "rolling7")
        close(float(r["deviation_pct"]), deviations[mode][r["date"]], "daily deviation")
        close(float(r["index"]), int(r["value"]) / stats["modes"][mode]["average"] * 100, "index")
    links = re.findall(r"\]\(([^)]+)\)", (root / "REPORT.md").read_text())
    for link in links:
        if not link.startswith("https://") and not (root / link).exists():
            raise ValueError(f"리포트 내부 링크 없음: {link}")
    seed_status = "not_checked"
    if seed_dir:
        for name in ["observations.csv", "manifest.json"]:
            if (root / "data/processed" / name).read_bytes() != (seed_dir / name).read_bytes():
                raise ValueError(f"B3-2 인계 파일 불일치: {name}")
        seed_status = "byte_identical"
    result = {
        "status": "passed",
        "independent_calculation": "Python stdlib csv/statistics",
        "rows": len(records),
        "source_files": len(sources["sources"]),
        "report_links": "passed",
        "raw_csv_reaggregation": "passed (26 files)" if raw else "not_requested",
        "rolling7_and_daily_metrics": "passed (1095 rows)",
        "verified": [
            "source aggregate totals/rows",
            "all date/mode values",
            "mean/total/extrema",
            "weekday/monthly averages",
            "anomaly counts/deviations",
            "joint low dates",
        ],
        "b3_2_seed": seed_status,
        "dataset_sha256": manifest["dataset_sha256"],
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--seed-dir", type=Path)
    parser.add_argument("--raw", action="store_true", help="대용량 원본까지 독립 재집계")
    args = parser.parse_args()
    try:
        result = verify(args.root, args.seed_dir, args.raw)
        (args.root / "outputs/verification.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(f"검증 실패: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
