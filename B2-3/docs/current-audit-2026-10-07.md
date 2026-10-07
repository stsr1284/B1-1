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

## 복구 후 직접 검사

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

이번 Python·Chrome 검사는 공급자 응답을 테스트로 대체했다. 새로운 실제 AI 호출이나 Vercel 재배포를 하지 않았다. 공개 배포·실제 AI·화면 증빙은 팀원 기록과 사용자 완료 확인에 근거한다. 언어 품질과 CEFR 정확도에 관한 기존 한계는 팀원 검증 기록에 유지했다.

## 최종 반영 상태

Levelly 실행 코드는 기존 `origin/main`의 `9530fc1`에 포함되어 있다. 이번 원문 추출·README·체크리스트·확인 기록 변경은 아직 커밋·푸시하지 않았다.

B2-1의 커밋 10개·브랜치 병합 조건은 [B2-1 체크리스트](../../B2-1/요구사항_체크리스트.md)에서 별도로 관리한다. B2-3 원문에는 커밋 10개 조건이 없다. 별도 학습자 실습과 선택 보너스를 이번 제출 정리의 남은 작업으로 추가하지 않는다.
