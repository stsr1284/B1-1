"""해시로 출처 연결을 확인하고 분석 입력·결과를 직렬화한다."""

import json
from pathlib import Path

import pandas as pd

from .sources import sha256, source_specs


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


def read_aggregates(data_dir: Path) -> tuple[pd.DataFrame, dict]:
    sources = json.loads((data_dir / "sources.json").read_text(encoding="utf-8"))
    if {s["file"] for s in sources["sources"]} != {s["file"] for s in source_specs()}:
        raise ValueError("공식 원본 26개에 대한 집계본이 필요합니다")
    frames = []
    for source in sources["sources"]:
        path = data_dir / "aggregated" / source["file"]
        if sha256(path) != source["aggregate_sha256"]:
            raise ValueError(f"집계본 해시 불일치: {path.name}")
        frame = pd.read_csv(path, dtype={"date": str, "mode": str})
        if int(frame["value"].sum()) != source["total"]:
            raise ValueError(f"원본 합계와 집계본 불일치: {path.name}")
        frames.append(frame)
    return pd.concat(frames, ignore_index=True), sources


def save_processed(data: pd.DataFrame, data_dir: Path, processed_dir: Path) -> dict:
    processed_dir.mkdir(parents=True, exist_ok=True)
    path = processed_dir / "observations.csv"
    data.to_csv(path, index=False, date_format="%Y-%m-%d", lineterminator="\n")
    digest = sha256(path)
    manifest = {
        "schema_version": "2.0",
        "dataset_id": "seoul-public-mobility-2025-v1",
        "period_start": "2025-01-01",
        "period_end": "2025-12-31",
        "timezone": "Asia/Seoul",
        "unit": "건",
        "row_count": len(data),
        "mode_counts": {str(k): int(v) for k, v in data.groupby("mode").size().items()},
        "primary_key": ["date", "mode"],
        "dataset_sha256": digest,
        "sources_sha256": sha256(data_dir / "sources.json"),
        "scope": "서울시 공개 자료 전체 서비스 범위. 지하철 수도권 역 및 서울버스 시외 정류장 포함 가능",
        "value_definitions": {
            "bike": "따릉이 대여 건수",
            "bus": "서울버스 승차 건수",
            "subway": "공개 지하철 승차 건수",
        },
    }
    write_json(processed_dir / "manifest.json", manifest)
    return manifest
