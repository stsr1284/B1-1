"""공식 집계본을 정제하고 시계열 분석·그래프·리포트를 생성한다."""

import argparse
from pathlib import Path

from transport_analysis.clean import clean_observations
from transport_analysis.io import read_aggregates, save_processed, write_json
from transport_analysis.metrics import summarize
from transport_analysis.plots import make_plots
from transport_analysis.report import render_report


def main() -> int:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=root / "data")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=root,
        help="별도 재현 위치. 그 아래 data/processed·outputs·REPORT를 생성",
    )
    args = parser.parse_args()
    try:
        print("[1/4] 원본 출처·집계본 해시 검증 및 정제")
        frame, sources = read_aggregates(args.data_dir)
        data, quality = clean_observations(frame)
        quality["source_count"] = len(sources["sources"])
        quality["source_rows"] = sum(s["raw_rows"] for s in sources["sources"])
        quality["trailing_empty_fields_removed"] = sum(
            s["trailing_empty_fields_removed"] for s in sources["sources"]
        )
        manifest = save_processed(data, args.data_dir, args.output_root / "data/processed")
        print("[2/4] 요일·월별 집계, 이동평균, 이상일 계산")
        stats, features = summarize(data)
        (args.output_root / "outputs").mkdir(parents=True, exist_ok=True)
        features.to_csv(
            args.output_root / "outputs/daily_metrics.csv",
            index=False,
            date_format="%Y-%m-%d",
            lineterminator="\n",
        )
        write_json(args.output_root / "outputs/quality.json", quality)
        write_json(args.output_root / "outputs/statistics.json", stats)
        print("[3/4] 그래프 4개 생성")
        make_plots(features, stats, args.output_root / "outputs/figures")
        print("[4/4] 실제 수치로 REPORT.md 생성")
        (args.output_root / "REPORT.md").write_text(
            render_report(stats, quality, sources, manifest), encoding="utf-8"
        )
        print(f"완료: {len(data):,}행 → {args.output_root / 'REPORT.md'}")
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"분석 실패: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
