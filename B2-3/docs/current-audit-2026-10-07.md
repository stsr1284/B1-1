# Levelly 제출본 확인 기록

확인일: 2026-10-07. 제출 서비스: **Levelly — 영어를, 나의 속도로**.

## 제출 기준

팀원이 완료한 영어 학습 서비스의 코드·배포·화면·AI 코딩 증빙을 하나의 제출본으로 유지한다. 사용자가 팀원의 배포·스크린샷 완료 및 별도 실습 제외를 확인했다. 제공받은 A1-3.zip은 완성 프로젝트이며, 과제 참고 예시 템플릿으로 판단한 이전 검토를 정정한다. 과제 예시는 반려동물 서비스 “멍냥케어”다.

서비스 이름·대상·목적·기능을 임의로 변경했던 로컬 수정을 되돌렸다. 기존 Vercel 배포는 변경하지 않았다. 되돌린 작업 파일은 저장소 밖 `/private/tmp/codyssey-devread-reverted-2026-10-07`에 보관했고 해당 화면과 검사 자료를 최종 증빙에서 제외했다.

## 코드와 증빙의 일치

다음 5개 파일을 제공 ZIP에서 직접 읽어 현재 파일과 바이트 단위로 비교했으며 모두 일치했다.

| 실행 파일 | 제공 ZIP과 일치 |
|---|---|
| public/index.html | 확인 |
| public/css/style.css | 확인 |
| public/js/app.js | 확인 |
| api/rewrite.py | 확인 |
| services/coach.py | 확인 |

Python·Node 프로젝트 설정과 기존 테스트를 원래 Levelly 버전으로 복구했다. 기획서도 원래 영어 학습 목적과 A1~B2 변환 기능을 설명한다. README의 현재 제출 저장소 주소는 `stsr1284/B1-1`, 브랜치는 `main`으로 정정했다.

팀원 제출 증빙은 그대로 유지했다.

- [서비스 기획서](service-plan.md)
- [팀원 배포·실제 AI 검증 기록](verification.md)
- [데스크톱 화면](evidence/desktop.png), [모바일 화면](evidence/mobile.png)
- [실제 AI 데스크톱](evidence/ai-live-desktop.png), [실제 AI 모바일](evidence/ai-live-mobile.png)
- [실제 API 검사 자료](evidence/live-api-checks.json)
- [AI 코딩 도구 대화 발췌](evidence/ai-coding-log.md)

## 복구 직후 직접 검사 기록

| 검사 | 실행 방법 | 결과 |
|---|---|---|
| Python 입력·응답·HTTP·오류 처리 | Python 3.13.1 환경에서 `python -m unittest discover -s tests -v` | 16개 통과 |
| JavaScript 문법 | `node --check public/js/app.js` | 통과 |
| 브라우저 통합 검사 | 로컬 Flask 서버에서 기존 `node tests/browser.cjs`, Chrome·Playwright 사용 | 통과 |
| 반응형 | 브라우저 검사 390·768·1440px | 가로 넘침 없음 |
| 사용자 흐름 | 입력 경계·샘플·네 탭·키보드·요청 중 원문 편집 | 통과, 탭 변경 시 추가 호출 없음 |
| 실패 처리 | 429·502·504·잘못된 JSON·부분 응답·30초 타임아웃 | 안내·버튼 복구 통과 |
| 출력 안전성 | HTML 형태 응답을 텍스트로 표시 | 스크립트 실행 없음 |
| 키 관리 | `.env.local` Git 제외·비밀 환경 파일 추적 여부·현재 키 문자열의 B2-3 파일 검색 | 제외 확인, 추적 0개, 비환경 파일 노출 0건 |

복구 직후 Python·Chrome 검사는 공급자 응답을 테스트로 대체했으며 당시에는 새로운 실제 AI 호출이나 Vercel 재배포를 하지 않았다. 당시 공개 배포·실제 AI·화면 판정은 팀원 기록과 사용자 완료 확인에 근거했다. 아래 재검증에서는 공개 URL과 실제 AI를 직접 호출했다. 언어 품질과 CEFR 정확도에 관한 기존 한계는 팀원 검증 기록에 유지했다.

## 최종 반영 상태

Levelly 실행 코드는 `9530fc1`, 원문 추출·README·체크리스트·복구 확인 기록은 `0b746ed`에 포함되어 푸시되었다. 재검증 당시 로컬 HEAD와 실제 원격 main은 `4040137`로 일치했다. 이번 재검증 문서를 이후 제출 커밋·main 병합 대상에 포함했다.

B2-1의 커밋 10개·브랜치 병합 조건은 [B2-1 체크리스트](../../B2-1/요구사항_체크리스트.md)에서 별도로 관리한다. B2-3 원문에는 커밋 10개 조건이 없다. 별도 학습자 실습과 선택 보너스를 이번 제출 정리의 남은 작업으로 추가하지 않는다.

## 현재 공개 배포 직접 재검증: 2026-10-07

원문·현재 코드·기획서·README·제출 PNG를 다시 대조하고 [공개 서비스](https://levelly-english-coach.vercel.app)에 로그인 없이 접속했다. 이번 점검에서 실행 코드·Vercel 설정을 수정하거나 재배포하지 않았다.

| 검사 | 직접 확인 결과 |
|---|---|
| 공개 접속 및 코드 일치 | /, /css/style.css, /js/app.js 모두 HTTP 200. 내려받은 내용이 현재 로컬 HTML·CSS·JS와 바이트 단위로 일치 |
| 실제 AI 입출력 | 영어 샘플 277자 POST → HTTP 200, A1·A2·B1·B2 결과. 이번 요청 3.39초, 네 레벨의 본문·한국어 설명·수정 목록 형식 검증 통과 |
| 공개 API 빈 입력 | HTTP 400, INVALID_INPUT |
| 비공개 파일 접근 | /.env.local 및 /services/coach.py HTTP 404 |
| Python 검사 | Python 3.13.1의 unittest 16개 재실행 통과 |
| 공개 URL Chrome 검사 | 390·768·1440px 레이아웃, 입력·샘플·네 탭·키보드·요청 중 편집·오류·타임아웃·출력 안전성 통과 |
| API 중복 호출 | 탭 전환 시 추가 호출 없음. 브라우저 오류 검사는 응답을 대체했으며 실제 AI 추가 호출 없음 |
| 제출 5종 | 공개 URL·GitHub 코드·README·Levelly 기획서·데스크톱/모바일/AI 화면 및 코딩 도구 로그 존재 |
| 화면 일치 | 실제 AI 데스크톱·모바일 PNG를 직접 열어 Levelly 이름·기능·3개 섹션을 확인. 현재 증빙을 다른 서비스 화면으로 대체하지 않음 |
| 키 관리 | 현재 설정된 키가 추적 파일 및 과제 Git 이력에 등장하지 않음. 비밀 환경 파일의 Git 추적 이력 0개 |

실제 HTTP 검사 기록은 `/private/tmp/codyssey-assignment-reaudit/b2-3-public-checks.json`, 실제 AI 응답은 같은 폴더의 `b2-3-public-live-response.json`에 있다. 브라우저 통합 검사는 기존 `tests/browser.cjs`를 공개 URL 대상으로 실행했다. 브라우저 실패 검사의 대체 응답과 실제 AI POST 성공을 구분했다.

현재 확인 범위에서 필수 기능·바닐라 프론트·Python 백엔드·제출 패키지 위반은 발견하지 않았다. 공개 서버의 프론트 내용 일치와 백엔드 응답은 직접 확인했지만 Vercel 관리자 화면의 현재 저장소 연동 설정은 새로 조회하지 않았다. GitHub→Vercel 연동 이력은 기존 팀원 기록에 근거한다. 개인 설명 능력·키 폐기 수행 능력과 CEFR 언어 품질 전체를 이번 기능 검사로 인증하지 않는다.
