# B3-1 · 서울 이동 패턴 분석

2025년 따릉이 대여·서울버스 승차·공개 지하철 승차를 비교하는 Python 시계열 분석 과제다. 공식 CSV 26개, 15,165,733행을 검증하고 **365일×3수단=1,095행**으로 정리했다.

- 결과: [REPORT.md](REPORT.md) — 질문 3개, 분석 기법 4종, 그래프 4개, 인사이트 3개와 한계.
- 과제 기준: [과제 원문](과제문.md), [실행 계획·완료 체크리스트](진행계획.md).
- 설계: [아키텍처](docs/ARCHITECTURE.md), [코드 규칙](docs/CODE_CONVENTIONS.md), [파일 구조](docs/FILE_STRUCTURE.md), [협업 규칙](docs/COLLABORATION.md).
- 학습 자료: [소프트웨어 설계 용어 원문](docs/SOFTWARE_DESIGN_TERMS.md). 이 자료의 기온 예시는 당시 대화 기록이며 현재 주제는 교통이다.

GitHub 제출: [작업 브랜치의 B3-1](https://github.com/stsr1284/B1-1/tree/codex/b3-1-transport-analysis/B3-1). 2026-10-19 제출 커밋 `d1a7c24`의 원격 반영과 대표 결과 파일 일치를 확인했다.

## 실행

검증 환경: Python 3.13.1, pandas 3.0.6, Matplotlib 3.11.2. Python 3.12 이상이 필요하다. B3-2 원문의 최소 Python 3.10 이상 조건도 충족하는 환경이다.

B3-1 폴더에서 실행한다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python analyze.py
```

저장소에 포함한 일별 집계본으로 실행하므로 API 키·로그인·네트워크 없이 그래프와 리포트를 재생성할 수 있다. 필수 입력이 없거나 해시·계약이 맞지 않으면 오류를 출력하고 종료 코드 1로 끝난다.

공식 원본부터 다시 확인하려면 다음을 실행한다. 약 1.7GB를 받으며 `data/raw/`는 Git에서 제외한다. 기존 원본은 재사용하고 해시가 바뀌면 자동 덮어쓰기 대신 오류로 알린다.

```bash
python fetch_data.py
python analyze.py
python verify.py --raw --seed-dir ../B3-2/data/seed
```

공식 다운로드는 API 키 없는 파일 서비스다. 파일 식별자가 변경되면 각 공식 페이지의 파일명·기간을 확인한 뒤 수집 설정과 데이터 버전을 함께 갱신한다. 원본이 수정되어 과거 해시와 다르면 그 변경을 숨기지 않는다.

## 데이터와 계산 기준

| 항목 | 기준 |
|---|---|
| 출처 | 서울특별시 열린데이터광장. 공공누리 제1유형, 출처 표시 |
| 기간 | 2025-01-01~2025-12-31, 한국 날짜 기준 |
| 관측값 | 따릉이=대여 건수, 버스·지하철=승차 건수. 하차를 더하지 않음 |
| 공간 범위 | 각 공식 자료 전체 서비스 범위. 서울 밖 지하철역·버스 정류장도 포함될 수 있음 |
| 정제 | UTF-8/CP949 실제 헤더 판별, 빈 끝 필드만 보정, 전체 행의 날짜·숫자·중복 검사 |
| 누락·이상값 | 누락·음수·키 중복은 오류. IQR 극값은 표시·유지, 임의 보간·삭제 없음 |
| 비교 | 요일 평균, 월별 일평균, 7일 이동평균, 월×요일 평균 대비 편차 |
| 해석 한계 | 고유 인구·수송분담률·개인 환승·인과 효과를 나타내지 않음 |

공식 원본: [따릉이](https://data.seoul.go.kr/dataList/OA-14994/F/1/datasetView.do), [버스](https://data.seoul.go.kr/dataList/OA-12912/S/1/datasetView.do), [지하철](https://data.seoul.go.kr/dataList/OA-12914/F/1/datasetView.do).

원본 메타데이터·해시: [sources.json](data/sources.json). 파일별 일별 합계: `data/aggregated/`. 정제본과 계약: [observations.csv](data/processed/observations.csv), [manifest.json](data/processed/manifest.json).

## 검증

```bash
python -m pip install -r requirements-dev.txt
ruff check .
ruff format --check .
python -m pytest -q
python verify.py --seed-dir ../B3-2/data/seed
python analyze.py --output-root /tmp/b3-1-reproduce
```

- 단위 테스트: 날짜 누락·음수/무한대/결측·중복·이동평균 공백·승차만 집계·CSV 구조·다운로드 실패 확인.
- 독립 검증: pandas 계산과 별개로 Python 표준 라이브러리 `csv`·`statistics`로 수단별 합계/평균/극값, 월·요일 평균, 이상일·공동 감소일, 7일 이동평균을 전수 대조한다.
- `--raw`: 공식 원본 26개의 SHA-256과 날짜별 합계를 별도 `DictReader` 집계로 재확인한다.
- 별도 출력 재현: 정제 CSV·manifest·통계 JSON·리포트·PNG의 바이트 일치를 확인한다. 결과 수치는 무작위성·외부 AI 호출에 의존하지 않는다.
- 그래프: 영어 표기로 폰트 환경 차이를 줄이고, 리포트에 한국어 해설을 붙였다. 축·단위·범례·잘림을 직접 확인한다.
- 증거: [verification.json](outputs/verification.json), [품질 결과](outputs/quality.json), [통계](outputs/statistics.json), [일별 계산값](outputs/daily_metrics.csv).

실제 확인(2026-10-19): pytest **22개 통과**, Ruff 검사·포맷 통과, 공식 원본 26개 독립 재집계 통과, 그래프 4개 눈으로 확인, 별도 재실행 산출물 10개 바이트 일치.

## B3-2 인계

```text
public CSV -> checked daily aggregates -> observations.csv
                                             |
                                      exact copy + hash
                                             |
                                       B3-2/data/seed
                                             |
                                    future Firestore + AI
```

`observations.csv`와 `manifest.json`을 B3-2/data/seed에 동일하게 전달한다. 기본 키는 (date, mode), 시드 문서 ID는 dataset_id+mode+date를 사용하도록 설계했다. 현재 B3-2는 계획·초기 자료 단계다. DB 적재·AI·배포를 완료한 것으로 보지 않는다.

## 학습자가 설명할 핵심

| 항목 | 이 과제에서 설명할 내용 |
|---|---|
| 분석 질문 | 요일 차이·월별 변화·평소와 다른 날짜를 왜 비교했는가 |
| 정제 | 결측과 0의 차이, 완전 중복과 노선/정류장별 별도 관측의 차이 |
| 트렌드·계절성·노이즈 | 7일 평균의 장기 흐름, 반복 요일, 월별 패턴과 잔차. 1년으로 반복 계절성 확정 불가 |
| 분석 방법 | 이동평균의 첫 6일이 빈 이유, 월 합계 대신 일평균을 쓴 이유 |
| 관찰·가설 | 수치로 확인한 주말 감소와 통근·날씨 등 미검증 원인 해석을 구분 |
| AI 검증 | 생성 코드를 독립 재계산·테스트로 확인하고 본인이 근거와 한계를 설명 |

개인 설명 능력은 사용자가 직접 확인해야 한다. 코드 검사가 통과했다는 이유로 학습 목표를 자동 완료 처리하지 않는다. 선택 보너스인 대시보드·분해/예측은 이번 필수 범위에 포함하지 않았다.
