"""공식 파일 다운로드와 소스별 일별 승차/대여 집계 어댑터."""

import csv
import hashlib
import json
import re
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

DOWNLOAD_URL = "https://datafile.seoul.go.kr/bigfile/iot/inf/nio_download.do?&useCache=false"


def source_specs() -> list[dict]:
    """공식 파일 목록에서 확인한 2025년 파일 식별자."""
    specs = []
    for half, seq in [(1, 25), (2, 26)]:
        specs.append(
            {
                "mode": "bike",
                "inf_id": "OA-14994",
                "inf_seq": 1,
                "seq": seq,
                "file": f"bike_2025_h{half}.csv",
                "encoding": "cp949",
                "start": f"2025-{'01' if half == 1 else '07'}-01",
                "end": f"2025-{'06-30' if half == 1 else '12-31'}",
            }
        )
    for mode, inf_id, offset, encoding in [
        ("bus", "OA-12912", 141, "cp949"),
        ("subway", "OA-12914", 137, "utf-8-sig"),
    ]:
        for month in range(1, 13):
            import calendar

            specs.append(
                {
                    "mode": mode,
                    "inf_id": inf_id,
                    "inf_seq": 3,
                    "seq": offset + month,
                    "file": f"{mode}_2025_{month:02d}.csv",
                    "encoding": encoding,
                    "start": f"2025-{month:02d}-01",
                    "end": f"2025-{month:02d}-{calendar.monthrange(2025, month)[1]}",
                }
            )
    return specs


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def download(spec: dict, target: Path, opener=urlopen) -> None:
    """임시 파일로 받은 뒤 응답 종류·길이를 확인하고 원본으로 이동한다."""
    payload = urlencode(
        {"infId": spec["inf_id"], "infSeq": spec["inf_seq"], "seq": spec["seq"]}
    ).encode()
    partial = target.with_suffix(".part")
    try:
        with opener(DOWNLOAD_URL, data=payload, timeout=60) as response:
            expected = response.headers.get("Content-Length")
            with partial.open("wb") as output:
                first = response.read(1024 * 1024)
                if not first or b"<html" in first[:500].lower():
                    raise ValueError(f"CSV가 아닌 응답: {spec['file']}")
                output.write(first)
                while block := response.read(1024 * 1024):
                    output.write(block)
            if expected and partial.stat().st_size != int(expected):
                raise ValueError(f"다운로드 크기 불일치: {spec['file']}")
        partial.replace(target)
    finally:
        partial.unlink(missing_ok=True)


def aggregate_csv(path: Path, spec: dict) -> tuple[list[dict], dict]:
    """전 행을 검사한다. 승하차 합산·잘못된 행 건너뛰기·임의 보간은 하지 않는다."""
    counts, row_counts = Counter(), Counter()
    seen = set()
    raw_rows = trailing = 0
    with path.open(encoding=spec["encoding"], newline="") as stream:
        reader = csv.reader(stream)
        headers = next(reader)
        date_col = "대여일자" if spec["mode"] == "bike" else "사용일자"
        value_col = "대여건수" if spec["mode"] == "bike" else "승차총승객수"
        di, vi = headers.index(date_col), headers.index(value_col)
        for line, row in enumerate(reader, 2):
            raw_rows += 1
            if len(row) == len(headers) + 1 and row[-1] == "":
                row = row[:-1]
                trailing += 1
            if len(row) != len(headers):
                raise ValueError(f"{path.name}:{line} CSV 열 수 오류")
            fingerprint = hashlib.sha256(json.dumps(row, ensure_ascii=False).encode()).digest()
            if fingerprint in seen:
                raise ValueError(f"{path.name}:{line} 완전 중복 행")
            seen.add(fingerprint)
            raw_date = row[di].strip()
            if re.fullmatch(r"\d{8}", raw_date):
                raw_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
            day = date.fromisoformat(raw_date).isoformat()
            if not spec["start"] <= day <= spec["end"]:
                raise ValueError(f"{path.name}:{line} 파일 범위 밖 날짜 {day}")
            value = row[vi].strip()
            if not re.fullmatch(r"\d+", value):
                raise ValueError(f"{path.name}:{line} 결측/음수/잘못된 승차 값 {value!r}")
            counts[day] += int(value)
            row_counts[day] += 1
    expected_days = (date.fromisoformat(spec["end"]) - date.fromisoformat(spec["start"])).days + 1
    if len(counts) != expected_days:
        raise ValueError(f"{path.name}: 날짜 누락 {len(counts)}/{expected_days}")
    rows = [
        {"date": d, "mode": spec["mode"], "value": v, "source_rows": row_counts[d]}
        for d, v in sorted(counts.items())
    ]
    return rows, {
        "raw_rows": raw_rows,
        "columns": headers,
        "trailing_empty_fields_removed": trailing,
        "invalid_rows": 0,
        "exact_duplicate_rows": 0,
        "days": len(rows),
        "total": sum(counts.values()),
    }


def collect_one(spec: dict, root: Path, existing: dict) -> dict:
    raw = root / "raw" / spec["file"]
    if not raw.exists():
        download(spec, raw)
    digest = sha256(raw)
    previous = existing.get(spec["file"])
    if previous and previous["sha256"] != digest:
        raise ValueError(f"원본 해시 변경: {raw}; 출처 변경을 검토한 뒤 버전을 갱신하세요")
    # 공식 월별 CSV의 인코딩이 서로 달라 헤더로 판별하고, 이후 전체는 엄격하게 읽는다.
    spec = spec.copy()
    with raw.open("rb") as stream:
        header = stream.readline()
    try:
        header.decode("utf-8-sig")
        spec["encoding"] = "utf-8-sig"
    except UnicodeDecodeError:
        header.decode("cp949")
        spec["encoding"] = "cp949"
    rows, quality = aggregate_csv(raw, spec)
    aggregate = root / "aggregated" / spec["file"]
    with aggregate.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=["date", "mode", "value", "source_rows"], lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    return {
        **spec,
        **quality,
        "source_url": f"https://data.seoul.go.kr/dataList/{spec['inf_id']}/S/1/datasetView.do",
        "download_url": DOWNLOAD_URL,
        "downloaded_at": previous["downloaded_at"]
        if previous
        else datetime.fromtimestamp(raw.stat().st_mtime, timezone.utc).isoformat(),
        "sha256": digest,
        "bytes": raw.stat().st_size,
        "aggregate_sha256": sha256(aggregate),
        "license": "공공누리 제1유형: 서울특별시 출처 표시",
    }
