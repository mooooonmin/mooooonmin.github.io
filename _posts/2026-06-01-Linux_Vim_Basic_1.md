---
title: Vim 기본 사용법 1
category: v
date: 2026-06-01 00:00:20 +0900
tags: [linux, vim, vi, editor, insert-mode, normal-mode]
---

## 1. Vim으로 파일 열기

Linux에서 터미널 기반 편집기로 파일을 열 때 `vi` 또는 `vim` 명령어를 사용할 수 있다.

```bash
vi app.txt
vim app.txt
```

`vi app.txt` 또는 `vim app.txt`는 `app.txt` 파일을 연다.
파일이 이미 있으면 기존 파일을 열고, 파일이 없으면 새 파일을 작성할 수 있는 상태로 열린다.

처음 실습할 때는 아래처럼 입력하면 된다.

```bash
vi app.txt
```

---

## 2. Vim에서 바로 입력이 안 되는 이유

Vim 화면이 열린 뒤 `qwer` 같은 문자를 입력해보면 일반 메모장처럼 바로 글자가 입력되지 않을 수 있다.
이유는 Vim에는 여러 모드가 있고, 처음 열렸을 때는 보통 텍스트 입력 모드가 아니기 때문이다.

입문 단계에서는 아래 두 가지 모드만 먼저 이해하면 된다.

| 모드 | 의미 |
|---|---|
| Normal mode | 이동, 삭제, 저장, 종료 같은 명령을 입력하는 모드 |
| Insert mode | 실제 텍스트를 입력하는 모드 |

Vim 공식 사용자 매뉴얼도 Vim을 막 시작하면 Normal mode에 있다고 설명한다. [1]
따라서 Vim을 열자마자 글자를 입력하려면 먼저 Insert mode로 전환해야 한다.

---

## 3. Insert mode로 바꾸기

텍스트를 입력하려면 키보드에서 `i`를 누른다.

```text
i
```

`i`는 Insert mode로 들어가는 명령이다.
Vim 공식 사용자 매뉴얼도 `i` 명령을 입력하면 Insert mode로 들어간다고 설명한다. [1]

화면 왼쪽 아래에 `-- INSERT --` 또는 `INSERT` 같은 문구가 보이면 Insert mode로 전환된 것이다.
이 상태에서는 키보드로 입력한 글자가 파일 내용으로 작성된다.

예를 들어 아래처럼 아무 텍스트나 입력해볼 수 있다.

```text
qwer
```

---

## 4. Normal mode로 돌아가기

작성한 글을 저장하거나 Vim을 종료하려면 먼저 Normal mode로 돌아가야 한다.
Insert mode에서 Normal mode로 돌아갈 때는 `Esc`를 누른다.

```text
Esc
```

Vim reference manual도 `<Esc>`가 Insert mode 또는 Replace mode를 끝내고 Normal mode로 돌아간다고 설명한다. [2]

`Esc`를 누르면 왼쪽 아래에 보이던 `INSERT` 문구가 사라진다.
이 상태가 Vim에 명령을 입력할 수 있는 Normal mode다.

---

## 5. 저장하고 종료하기

작성한 내용을 저장하고 Vim을 종료하려면 Normal mode에서 아래 명령어를 입력한 뒤 Enter를 누른다.

```vim
:wq
```

`w`는 write, `q`는 quit로 이해하면 된다.
즉, `:wq`는 파일을 저장하고 종료하는 명령이다.

작업 흐름은 아래 순서로 기억하면 된다.

1. `i`를 눌러 Insert mode로 들어간다.
2. 텍스트를 작성한다.
3. `Esc`를 눌러 Normal mode로 돌아간다.
4. `:wq`를 입력하고 Enter를 누른다.

저장된 파일이 있는지 확인하려면 터미널에서 아래 명령어를 실행한다.

```bash
ls
```

---

## 6. 파일 다시 열기와 수정하기

방금 저장한 파일을 다시 열 때도 같은 명령어를 사용한다.

```bash
vi app.txt
```

파일이 존재하면 Vim은 기존 파일 내용을 연다.
내용을 수정하려면 다시 `i`를 눌러 Insert mode로 전환한 뒤 원하는 내용을 수정하면 된다.

수정한 내용을 저장하고 종료하는 흐름도 동일하다.

1. `i`를 눌러 Insert mode로 전환한다.
2. 파일 내용을 수정한다.
3. `Esc`를 눌러 Normal mode로 돌아간다.
4. `:wq`를 입력하고 Enter를 누른다.

---

## 7. 저장하지 않고 그냥 종료하기

파일을 수정하지 않았거나, 저장할 내용이 없어서 그냥 종료하고 싶다면 Normal mode에서 아래 명령어를 입력한다.

```vim
:q
```

`:q`는 quit, 즉 종료 명령이다.
단, 파일을 수정한 상태라면 Vim이 저장하지 않은 변경 사항이 있다고 알려주며 종료를 막을 수 있다.
이 경우 저장하려면 `:wq`를 사용하고, 저장하지 않고 강제로 종료하려면 `:q!`를 사용한다.

입문 단계에서는 먼저 아래 두 명령어를 확실히 구분하면 된다.

| 명령어 | 의미 |
|---|---|
| `:wq` | 저장하고 종료 |
| `:q` | 수정한 내용이 없을 때 그냥 종료 |

---

## 핵심 정리

- `vi app.txt` 또는 `vim app.txt`로 파일을 열 수 있다.
- Vim은 처음 열렸을 때 보통 Normal mode로 시작한다.
- 텍스트를 입력하려면 `i`를 눌러 Insert mode로 들어간다.
- 저장이나 종료 명령을 입력하려면 `Esc`를 눌러 Normal mode로 돌아간다.
- `:wq`는 저장하고 종료하는 명령이다.
- `:q`는 수정한 내용이 없을 때 그냥 종료하는 명령이다.

---

## 출처

- [1] Vim User Manual, first steps in Vim - <https://vimhelp.org/usr_02.txt.html>
- [2] Vim Reference Manual, Insert mode - <https://vimhelp.org/insert.txt.html>
- [3] Vim Quick Reference, writing and quitting - <https://vimhelp.org/quickref.txt.html>
