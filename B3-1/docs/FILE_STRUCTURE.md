# 파일 구조와 소유 책임

B3-1의 코드·데이터·결과와 B3-2 시드 파일은 생성·검증했다. 아래 B3-2 backend/frontend는 이후 구현할 구조다.

```text
B1-1/                         # repository root
|-- B3-1/
|   |-- AGENTS.md
|   |-- *.md                  # assignment and execution plan
|   |-- docs/
|   |   |-- CODE_CONVENTIONS.md
|   |   |-- ARCHITECTURE.md
|   |   |-- FILE_STRUCTURE.md
|   |   `-- COLLABORATION.md
|   |-- README.md
|   |-- REPORT.md
|   |-- analyze.py
|   |-- fetch_data.py
|   |-- verify.py
|   |-- requirements.txt
|   |-- requirements-dev.txt
|   |-- pyproject.toml        # Ruff/pytest configuration
|   |-- transport_analysis/
|   |   |-- __init__.py
|   |   |-- io.py
|   |   |-- clean.py
|   |   |-- metrics.py
|   |   |-- sources.py
|   |   |-- report.py
|   |   `-- plots.py
|   |-- data/
|   |   |-- raw/*.csv           # large official CSVs, Git ignored
|   |   |-- aggregated/      # daily totals per official file
|   |   |-- sources.json     # URLs, dates, hashes, row counts
|   |   `-- processed/
|   |       |-- observations.csv
|   |       `-- manifest.json
|   |-- outputs/
|   |   |-- quality.json
|   |   |-- statistics.json
|   |   |-- daily_metrics.csv
|   |   |-- verification.json
|   |   `-- figures/*.png
|   |-- tests/
|   `-- images/               # original assignment image
`-- B3-2/
    |-- AGENTS.md
    |-- *.md                  # assignment and service plan
    |-- data/seed/
    |   |-- observations.csv  # exact copy from B3-1
    |   `-- manifest.json     # exact copy from B3-1
    |-- backend/
    |   `-- scripts/import_data.py
    |-- frontend/
    `-- screenshots/
```

## 파일별 관리

| 대상 | 작성·생성 주체 | Git·제출 정책 |
|---|---|---|
| 과제문.md·images/ | 원문 추출 결과 | 원문 보존. 임의로 요구사항을 수정하지 않음 |
| 진행계획.md·docs/ | 작업 담당자 | 결정과 구현 상태가 바뀌면 갱신 |
| data/raw/ | 공식 자료 수집 | 원본 보존. 대용량 파일은 Git 제외. 출처·수집 코드·해시와 일별 집계본 포함 |
| data/processed/ | B3-1 분석 실행 | 재생성 가능한 기준 데이터와 manifest |
| outputs/ | B3-1 분석 실행 | 제출할 최종 통계·품질 결과·그래프 포함 |
| REPORT.md | 수치를 확인한 작성자 | 근거 검토 후 결론 작성. 이미지 경로는 상대 경로 |
| README.md | 작업 담당자 | 출처·환경·실행·검증·인계 방법 |
| B3-2/data/seed/ | 인계 작업 | 기준 데이터의 검증된 복사본. 수작업 수정 금지 |
| .env·서비스 계정 키 | 실행 환경 | Git 제외. 값 없는 설정 예시만 공유 |
| venv·캐시·임시 캡처 | 실행 도구 | 제출·Git에서 제외 |

B3-1과 B3-2는 각각 실행에 필요한 자료를 포함한다. 데이터 재배포가 제한되면 각 README에 같은 원본을 얻는 방법과 검증용 해시를 제공한다.

빈 폴더나 미구현 파일을 대량으로 만들지 않고, 해당 작업을 시작할 때 필요한 파일을 추가한다.
