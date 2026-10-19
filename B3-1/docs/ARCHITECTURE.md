# 교통 분석 아키텍처와 공통 데이터 계약

2026-10-19 사용자 선택: 기온 대신 2025년 따릉이·버스·지하철 이용량. 과제 원문과 용어 설명 원문은 보존한다.

## 1. 선택 이유

공식 CSV의 인코딩·컬럼·규모가 다르다. 소스별 어댑터에서 차이를 처리하고 계산은 네트워크 없는 순수 함수로 구성한다. B3-1은 데이터 파이프라인과 Functional Core / Imperative Shell을 사용한다. 상태 없는 계산을 불필요한 클래스로 감싸지 않는다. 원본을 매번 읽는 대신 검증된 파일별 일별 집계본도 보관해 재현 비용을 줄인다.

## 2. 책임과 인터페이스

| 구성 | 입력 → 출력·책임 |
|---|---|
| fetch_data.py / sources.py | 공식 식별자 → 원본 CSV·일별 집계·출처 manifest. 날짜·수치·행 구조·완전 중복 검증 |
| analyze.py | 경로 옵션 → 정제·계산·출력 순서 조정. 실패 종료 코드 1 |
| io.py | 경로 → 해시 확인된 집계본. JSON/CSV 직렬화·해시·버전 기록 |
| clean.py | 집계본 → date/mode/value/memo 계약 데이터·품질 기록. 누락·상충 중복·음수는 오류 |
| metrics.py | 정제 DataFrame → 통계·요일/월별 집계·7일 이동평균·월×요일 편차. 입력 수정·입출력 없음 |
| plots.py / report.py | 계산 결과 → PNG / REPORT.md. 관찰·가설·한계 분리 |
| verify.py | 정제본·결과 → 표준 라이브러리 독립 재계산·리포트 링크·B3-2 인계 검사 |

## 3. 의존성 방향

```text
fetch_data -> sources -> public HTTP / raw files
                  |
             daily aggregates + sources.json
                  |
analyze -> io -> clean -> metrics -> plots/report
                  |                    |
            observations.csv       REPORT + PNG + JSON
                  |
             manifest/hash
                  |
             B3-2 seed (same bytes)

B3-2 Router -> Service -> Repository / AI protocols
                              ^              ^
                       Firestore/Fake    OpenAI/Stub
```

위쪽 화살표는 처리 흐름, 아래쪽은 코드 의존성을 나타낸다. B3-2 실행 코드는 B3-1 Python 모듈을 직접 가져오지 않는다.

## 4. 실제·테스트 구현 연결

B3-1 CLI가 파일 입출력과 계산 함수를 연결한다. 실행용 모의 데이터 모드는 두지 않고 테스트에서만 명시적인 작은 fixture를 사용한다. 다운로드 함수는 HTTP 응답을 주입받을 수 있게 해 네트워크 실패·HTML 오류 응답을 검사한다. B3-2는 구현 단계에서 Protocol과 DI로 Firestore/OpenAI 구현과 메모리 Fake/고정 응답 Stub을 연결한다. 앱 시작점에서 선택하며 테스트 통과를 실제 연결 완료로 표시하지 않는다.

## 5. 데이터 계약과 검증 방법

| 필드 | 계약 |
|---|---|
| date | YYYY-MM-DD, 2025-01-01~2025-12-31 |
| mode | bike / bus / subway |
| value | 0 이상의 정수. bike=대여 건수, bus/subway=승차 건수 |
| memo | 문자열, 빈 문자열 허용 |

기본 키는 (date, mode). 기대 범위는 365일×3수단=1,095행이다. 결측을 0으로 채우지 않고 누락되면 분석을 중단한다. 수단별 100점 이상도 확인한다. 승차와 하차를 더하지 않는다. 집계 키 중복은 같은 값이어도 중단해 원인을 확인한다. 극단적인 값은 자동 삭제하지 않고 월×요일 평균 대비 편차를 기록한다.

sources.json에는 공식 URL·POST 인자·수집 UTC 시각·원본 SHA-256/크기/행 수·인코딩·집계본 SHA-256·CSV 끝 빈 필드 보정 건수를 기록한다. manifest.json에는 schema_version·dataset_id·기간·수단별 개수·sources.json과 정제본 해시를 기록한다. 날짜·수단·정수는 정확히, 계산 소수는 절대 오차 1e-9 이내로 비교한다.

각 수단의 평균·합계·극값·기간을 따로 계산한다. 월별 비교는 월 길이 차이를 피하도록 일평균을 사용한다. 상대 규모는 수단별 연평균=100 지수로 비교한다. 7일 이동평균은 결측 없는 7개 달력 날짜다. 이상일 기준은 같은 월·요일 평균 대비 증감률이며 전체 기간을 사용하는 사후 탐색이다. 예측이나 인과 효과로 표현하지 않는다. 서울시 자료의 서비스 범위가 서로 다르므로 고유 이용자 수·행정구역 내 수송분담률로 해석하지 않는다.

CSV와 manifest를 B3-2/data/seed로 그대로 복사해 해시·전수 행을 대조한다. DB 도입 시 dataset_id+mode+date를 ID로 하고 최초 통계도 비교한다. 재적재로 사용자 변경을 덮어쓰지 않고 충돌을 알린다. 자료·정제 규칙 변경 시 버전을 올린다.

검증: 입력 경계 pytest → 독립 통계 재계산 → 별도 출력 위치에서 재실행 → 그래프 눈으로 확인 → 원문 불변 확인. B3-2 실제 DB·AI·배포 검증은 B3-2 구현 단계에서 수행한다.
