"""공식 CSV 26개 수집 및 검증된 일별 집계본 생성. API 키 불필요."""

import argparse
import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import URLError

from transport_analysis.sources import collect_one, source_specs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parent / "data")
    args = parser.parse_args()
    for folder in ("raw", "aggregated"):
        (args.data_dir / folder).mkdir(parents=True, exist_ok=True)
    manifest = args.data_dir / "sources.json"
    existing = (
        {s["file"]: s for s in json.loads(manifest.read_text())["sources"]}
        if manifest.exists()
        else {}
    )
    results = []
    try:
        with ThreadPoolExecutor(max_workers=3) as pool:
            tasks = {
                pool.submit(collect_one, spec, args.data_dir, existing): spec
                for spec in source_specs()
            }
            for task in as_completed(tasks):
                result = task.result()
                results.append(result)
                print(
                    f"[{len(results)}/26] {result['file']}: {result['raw_rows']:,}행 → {result['days']}일",
                    flush=True,
                )
        results.sort(key=lambda s: s["file"])
        manifest.write_text(
            json.dumps({"sources": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf8"
        )
    except (OSError, URLError, ValueError, KeyError, csv.Error) as exc:
        print(f"자료 수집 실패: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
