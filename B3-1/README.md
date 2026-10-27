# B3-1 · 서울 지역별 대중교통 이동 변화 분석

**시간대별 행정동 OD로 어느 지역행 이동이 늘고 줄었는지 비교한다.** 주말·낮·저녁 이동은 관광·여가 방문 변화의 단서로 해석하며 관광객 수로 단정하지 않는다.

- 최종 결과: [REPORT.md](REPORT.md)
- 그래프 미리보기: [outputs/od_preview.html](outputs/od_preview.html)
- 검증·완료 여부: [요구사항 체크리스트](docs/COMPLETION_CHECKLIST.md)
- [분석 계획](docs/ANALYSIS_PLAN.md) · [데이터 사전](docs/DATA_DICTIONARY.md) · [과제 원문](과제문.md)

## 자료와 파일 구조

```text
B3-1/
├── 과제문.md / images/           원문 보존
├── REPORT.md                    최종 분석 리포트
├── run_od_analysis.py            이번 분석 실행 진입점
├── od_analysis/                 참조·정제·검증·분석·보고서 모듈
├── tests/od/                    결측·중복·코드 경계 사례 검증
├── data/
│   ├── raw/                     이번 분석 원본, 내용 불변
│   │   ├── transit_hourly_od/    2023~2026 공식 ZIP 66개
│   │   ├── locations/admin/     공식 행정동 마스터·월별 코드표
│   │   └── calendar/            2023~2026 공식 달력 페이지
│   ├── processed/transit_od/    원본과 분리한 집계·비교표
│   │   └── months/              재생성 가능한 월별 중간 Parquet
│   └── metadata/               현재 자료 출처·원본 해시·이동 기록
├── outputs/
│   ├── od_figures/              보고서용 PNG 4개
│   ├── od_validation/           이번 실행의 감사·독립 검산
│   └── od_preview.html          그래프 미리보기
├── docs/                        이번 분석 기준·체크리스트
└── tmp/                         과거 작업과 캐시, 제출 대상 아님
```

[OD 원본 확보 결과](data/TRANSIT_OD.md) · [사용/보관 데이터 구분](data/README.md)

주 분석은 월별 이름·코드가 유지된 서울 417개 동 중 별칭 충돌이 발견된 고덕1동과 일부 관측일에 기록이 없는 18개 동을 전 기간 제외한 **398개 동 사이 이동**이다. 보조 지표는 서울 밖 출발과 같은 동 내부 이동을 포함한다. 두 범위를 합산하지 않는다.

2023~2025 장기 비교 및 2025↔2026 **1~8월** 비교를 제공한다. 2026년 9~10월은 지역 코드 참조 범위 밖의 최근 탐색값이며, 10월은 21일까지의 부분 월이다.

## 재실행

Python 3.13 환경에서 검증한다. 그래프를 새로 그릴 때 한국어 폰트(AppleGothic, NanumGothic, Malgun Gothic 중 하나)가 필요하다. 저장된 PNG는 폰트 설치 없이 볼 수 있다. 패키지 버전은 [requirements-od.txt](requirements-od.txt)에 고정했다.

```bash
cd B1-1/B3-1  # 저장소를 내려받은 상위 폴더 기준
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-od.txt
# 원본이 없는 환경에서만 실행: 공식 목록 66개, 약 5.89GB
.venv/bin/python scripts/acquire_transit_hourly_od.py
# 원본 검증 -> 참조/중복 감사 -> 고정 패널 재계산 -> 분석 -> 그림/리포트 -> 독립 검산
.venv/bin/python run_od_analysis.py
# 경계 사례 테스트
.venv/bin/python -m unittest discover -s tests/od -v
```

원본 66ZIP 이외에 행정동 마스터·월별 코드표·달력 원본이 필요하다. 자동 수집 범위는 OD ZIP이며 참조 파일은 아래 방법으로 확보한다. 공식 자료가 개정되면 과거 스냅샷과 달라질 수 있으므로 [원본 목록](data/metadata/catalog.json)의 SHA-256과 대조한다. 불일치 파일로 기존 결과를 재현했다고 판단하지 않는다.

| 원본 | 확보 방법 | 저장 위치 |
|---|---|---|
| 시간대별 대중교통 OD | `scripts/acquire_transit_hourly_od.py` 실행. 포함된 `inventory.json`의 고정된 66개 다운로드 항목 사용 | `data/raw/transit_hourly_od/연도/` |
| 대중교통 행정동 마스터 | [OA-21234](https://data.seoul.go.kr/dataList/OA-21234/S/1/datasetView.do)의 CSV 다운로드. 요청 URL·POST 인자는 [수집 기록](data/metadata/transit_hourly_od/admin_master.json)에 있음 | `data/raw/locations/admin/transit_admin_master_20261027.csv` |
| 월별 행정동 코드표 | [서울 생활이동](https://data.seoul.go.kr/dataVisual/seoul/capitalRegionLivingMigration.do)에서 `admin_codes.zip` 다운로드. 요청 인자와 ZIP 내부 목록은 [참조 수집 기록](data/metadata/reference_sources.json)에 있음 | `data/raw/locations/admin/admin_codes.zip` |
| 공휴일 표 | [한국천문연구원 달력](https://astro.kasi.re.kr/kor/life/post/calendarData?search_year=2026)의 `search_year`를 2023~2026으로 바꿔 HTML 응답을 UTF-8로 보관. 후속 공지는 [달력 검증 기록](outputs/od_validation/calendar_sources.json) 참조 | `data/raw/calendar/calendar_data_연도.html` |

참조 원본이 없더라도 아래 소형 표 재생성 경로로 제출된 수치와 그림을 확인할 수 있다.

대용량 원본 없이 **제공한 소형 집계표로 그림·보고서만 재생성**하려면:

```bash
.venv/bin/python run_od_analysis.py --from-tables
```

이 모드는 원본 재검증과 동일하지 않다. 전체 재실행에는 원본/참조가 필요하다. 전체 원본을 디스크에 압축 해제하지 않으며, 파일 단위로 읽어 가공본만 생성한다. 이미 처리한 파일은 원본·참조·가공 해시가 일치할 때 재사용한다. 검증 과정에서 처음 별칭 충돌을 발견하면 고정 패널을 확정해 한 차례 재계산한다.

## 처리·해석 기준

- 원본 24일 공백은 0이나 보간값으로 채우지 않는다. 원본의 빈 시간 셀도 미상이다.
- 동일 행 중복은 한 번만 유지, 동일 OD 키의 값 충돌은 제외/기록한다. 지역 코드 자릿수를 임의 변환하지 않는다.
- 분석은 알려진 값의 합이다. 월×요일 가중치를 맞추고 공휴일·특별일을 분리한다. 이상일 포함/제외와 시간 구간 변경 결과를 함께 확인한다.
- 원본의 시간이 승차/하차 중 무엇인지는 미확정이므로 “원본 시간대의 해당 지역행 이동”이라고 표현한다.
- 관광객 수·인기 원인·상권 매출·접근성의 인과 효과를 증명하는 결과는 아니다.

이전 분석 코드·수집 스크립트·테스트·검증 로그는 `tmp/2026-10-28/legacy_submission_cleanup/`에 분리했다. 현재 실행은 `run_od_analysis.py`와 `od_analysis/`만 사용한다.

원본·보조 보관본·캐시·비밀 키는 Git에서 제외한다. 과제 제출에는 코드, 리포트, PNG, 소형 분석표, 출처·수집 방법과 검증 기록을 포함한다. GitHub 반영 상태는 [완료 체크리스트](docs/COMPLETION_CHECKLIST.md)를 따른다.
