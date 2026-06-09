# 작업 흐름 가이드

이 문서는 새 포스트를 작성하거나 기존 포스트와 화면 구성을 수정한 뒤 검증하고 커밋하는 기준을 정리한다.

## 1. 새 포스트 작성 흐름

1. `_posts`에 새 마크다운 파일을 추가한다.
2. 파일명은 `YYYY-MM-DD-title.md` 형식으로 작성한다.
3. front matter는 아래 순서를 지킨다.

```yaml
---
title: 제목
category: 분류값
date: YYYY-MM-DD HH:MM:SS +0900
tags: [tag1, tag2]
---
```

4. 같은 날짜의 포스트가 여러 개면 시간을 초 단위로 다르게 둔다.
   예: `00:00:00`, `00:00:10`, `00:00:20`
5. 일반 포스트는 큰 섹션만 `## 1. 제목` 형식으로 번호를 붙인다.
6. 하위 섹션은 번호 없이 `### 하위 제목`을 사용한다.
7. 마지막 요약 섹션은 `## 정리`로 작성한다.

## 2. 자동 생성 파일 규칙

아래 파일과 디렉터리는 스크립트가 자동으로 갱신한다.

- `README.md`
- `category/**`
- 포스트의 시간 정규화
- 포스트의 A-Z, 0-9 카테고리 정규화

따라서 위 파일을 수동으로 오래 유지보수하지 않는다. 필요한 변경은 원본 포스트나 생성 스크립트를 수정한 뒤 검증 명령으로 반영한다.

## 3. 로컬 검증

빠른 검증은 아래 명령으로 실행한다.

```powershell
python scripts/validate_all.py
```

화면 렌더링까지 포함하려면 아래 명령을 실행한다.

```powershell
python scripts/validate_all.py --include-smoke
```

브라우저 스모크 테스트는 `_site`의 주요 화면을 데스크톱/모바일 viewport로 확인한다.

- 홈
- 태그
- 카테고리 대표 페이지
- 카테고리 페이지네이션
- 코드블록이 있는 포스트
- Linux 명령어 포스트

## 4. 커밋 전 확인

커밋 전에는 최소한 아래 조건을 만족해야 한다.

- `python scripts/validate_all.py` 통과
- 화면이나 CSS를 수정했다면 `python scripts/validate_all.py --include-smoke` 통과
- `git status --short`에서 의도한 파일만 변경됨
- `scripts/__pycache__/` 같은 생성물이 커밋 대상에 없음

## 5. 커밋 메시지 형식

커밋 제목은 변경 범위를 먼저 적는다.

```text
docs(posts): add linux process article
ci(validate): add unified validation runner
fix(theme): improve dark pagination contrast
```

본문은 아래 형식을 유지한다.

```text
변경 이유를 한 문단으로 작성한다.

추가/수정:
- 영역
  - 실제 변경 내용

결과:
- 변경 후 기대되는 효과

검증:
- 실행한 검증 명령과 결과
```

## 6. 푸시 후 확인

커밋 후에는 원격 `main`에 푸시하고 GitHub Actions 결과를 확인한다.

- `Update README Index` workflow가 success인지 확인한다.
- 실패하면 실패한 step을 먼저 확인한다.
- 자동 생성 파일이 변경되었으면 workflow가 `[skip ci]` 커밋을 추가로 만들 수 있다.
