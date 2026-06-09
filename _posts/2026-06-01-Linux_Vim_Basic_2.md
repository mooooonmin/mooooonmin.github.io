---
title: Vim Basic 2
category: v
date: 2026-06-01 00:00:30 +0900
tags: [linux, vim, vi, editor, quit, swap-file, recovery]
---

## 1. 저장하지 않고 강제 종료하기

기존에 만든 `app.txt` 파일을 다시 열어보자.

```bash
vi app.txt
```

파일 내용을 일부 수정한 뒤 저장하지 않고 종료하려고 Normal mode에서 아래 명령어를 입력하면 오류가 발생할 수 있다.

```vim
:q
```

Vim은 파일을 수정했지만 저장하지 않은 상태에서 그냥 종료하지 않는다.
이때 아래와 비슷한 메시지가 보일 수 있다.

```text
No write since last change (add ! to override)
```

의미는 다음과 같다.

```text
마지막 변경 이후 파일을 저장하지 않았다.
저장하지 않고 종료하려면 !를 붙여서 강제로 실행하라.
```

저장하지 않고 강제로 종료하려면 Normal mode에서 아래 명령어를 입력한다.

```vim
:q!
```

Vim 사용자 매뉴얼도 `:q!`를 변경 사항을 버리고 종료하는 명령으로 설명한다. [1]

---

## 2. `:q`, `:q!`, `:wq` 구분하기

Vim 종료 명령은 상황에 따라 다르게 사용한다.

| 명령어 | 의미 | 사용 상황 |
|---|---|---|
| `:q` | 그냥 종료 | 수정한 내용이 없을 때 |
| `:q!` | 저장하지 않고 강제 종료 | 수정 내용을 버리고 종료할 때 |
| `:wq` | 저장하고 종료 | 수정 내용을 저장한 뒤 종료할 때 |

처음에는 위 세 가지 명령어만 확실히 구분해도 충분하다.
중요한 기준은 **수정 내용을 저장할 것인지 버릴 것인지**다.

---

## 3. Vim이 비정상 종료되면 생기는 일

파일을 수정하던 중 터미널이 끊기거나 창을 강제로 닫으면 Vim이 정상적으로 종료되지 않을 수 있다.
그 뒤 같은 파일을 다시 열면 Vim이 swap file을 발견했다는 경고 화면을 보여줄 수 있다.

예를 들어 `app.txt`를 편집하던 중 비정상 종료되었다면 아래와 비슷한 파일이 남을 수 있다.

```text
.app.txt.swp
```

Vim 공식 recovery 문서는 Vim이 변경 내용을 swap file에 저장하며, 원본 파일과 swap file을 이용해 작업 내용을 복구할 수 있다고 설명한다. [2]

---

## 4. swap file 경고 화면의 주요 선택지

swap file 경고 화면에는 여러 선택지가 나온다.
입문 단계에서는 아래 세 가지만 먼저 알아두면 된다.

```text
[O]pen Read-Only, (E)dit anyway, (R)ecover, (D)elete it, (Q)uit, (A)bort
```

| 선택지 | 의미 |
|---|---|
| `R` | 이전에 편집하던 내용을 복구한다 |
| `D` | swap file을 삭제하고 기존 파일을 연다 |
| `Q` | 아무 작업도 하지 않고 Vim을 종료한다 |

상황별로는 아래처럼 선택하면 된다.

| 상황 | 선택 |
|---|---|
| 아무 작업도 하고 싶지 않을 때 | `Q` |
| 이전 편집 내용을 버리고 기존 파일을 열고 싶을 때 | `D` |
| 이전 편집 내용을 복구하고 이어서 수정하고 싶을 때 | `R` |

---

## 5. 복구한 뒤 해야 할 일

`R`을 선택하면 Vim이 swap file을 바탕으로 이전 편집 내용을 복구한다.
복구된 내용을 확인한 뒤 저장하려면 아래 명령어를 입력한다.

```vim
:wq
```

복구를 완료했다면 남아 있는 swap file을 삭제해야 할 수 있다.
예를 들어 같은 디렉터리에 `.app.txt.swp`가 남아 있다면 아래처럼 확인하고 삭제할 수 있다.

```bash
ls -a
rm -rf .app.txt.swp
```

단, swap file을 삭제하기 전에는 복구가 끝났고 더 이상 필요하지 않은 파일인지 확인해야 한다.

---

## 6. swap file이 생기는 이유

swap file은 Vim이 편집 중인 내용을 임시로 저장하기 위해 만드는 파일이다.
Vim 공식 recovery 문서는 swap file이 변경 사항을 저장하고, Vim이나 컴퓨터가 비정상 종료되었을 때 복구에 사용할 수 있다고 설명한다. [2]

이 파일은 보통 숨김 파일 형태로 보인다.
따라서 일반 `ls`만으로는 보이지 않을 수 있고, 숨김 파일까지 보려면 `ls -a`를 사용한다.

```bash
ls -a
```

`app.txt`를 편집하다가 비정상 종료되었다면 같은 디렉터리에서 `.app.txt.swp` 같은 파일을 확인할 수 있다.

---

## 정리

- `:q`는 수정한 내용이 없을 때 Vim을 종료하는 명령이다.
- 수정한 내용을 저장하지 않고 종료하려면 `:q!`를 사용한다.
- 수정한 내용을 저장하고 종료하려면 `:wq`를 사용한다.
- Vim이 비정상 종료되면 `.swp` 확장자를 가진 swap file이 남을 수 있다.
- swap file 경고에서 `R`은 복구, `D`는 swap file 삭제, `Q`는 종료를 의미한다.
- 복구가 끝난 뒤에는 남은 swap file이 필요 없는지 확인하고 삭제해야 한다.

---

## 출처

- [1] Vim User Manual, quit and throw things away - <https://vimhelp.org/usr_21.txt.html>
- [2] Vim Reference Manual, recovery and swap files - <https://vimhelp.org/recover.txt.html>
- [3] Vim Reference Manual, editing and quitting - <https://vimhelp.org/editing.txt.html>
