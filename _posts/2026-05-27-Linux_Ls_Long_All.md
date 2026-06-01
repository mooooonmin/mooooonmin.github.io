---
title: ls -l/ls -a
category: l
date: 2026-05-27 00:00:10 +0900
tags: [linux, ls, file, directory, hidden-file, command]
---

## 1. 파일 종류 확인하기

Windows나 macOS에서는 아이콘 모양을 보고 일반 파일인지 디렉터리인지 쉽게 구분할 수 있다.
Linux에서는 `ls -l` 명령어를 사용하면 파일 종류를 확인할 수 있다.

```bash
ls -l
```

`ls -l`은 현재 디렉터리 내부 항목을 자세한 형식으로 보여준다.
GNU Coreutils 문서에서는 `-l` 옵션을 긴 형식(long format)으로 출력하는 옵션으로 설명한다. [1]

---

## 2. `ls -l` 결과에서 파일 종류 읽기

`ls -l`을 실행하면 각 줄의 맨 앞 한 글자로 파일 종류를 확인할 수 있다.

```text
drwxr-xr-x 2 ubuntu ubuntu 4096 May 27 09:00 test
-rw-r--r-- 1 ubuntu ubuntu   12 May 27 09:00 memo.txt
```

처음에는 아래 두 가지만 구분해도 충분하다.

| 첫 글자 | 파일 종류 | 의미 |
|---|---|---|
| `-` | 일반 파일 | 텍스트 파일, 실행 파일, 이미지 파일처럼 일반적으로 말하는 파일 |
| `d` | 디렉터리 | Windows나 macOS의 폴더처럼 다른 파일을 담는 항목 |

Linux man-pages의 `inode(7)` 문서도 파일 타입으로 일반 파일과 디렉터리를 구분한다. [2]
나머지 글자는 권한, 소유자, 파일 크기, 수정 시간 같은 추가 정보를 의미한다.

---

## 3. 숨김 파일 조회하기

Windows나 macOS에 숨김 파일이 있듯이 Linux에도 숨김 파일이 있다.
Linux에서는 파일명이 점(`.`)으로 시작하면 보통 숨김 파일처럼 다룬다.

예를 들면 아래와 같은 파일이 있다.

| 파일명 | 설명 |
|---|---|
| `.env` | 환경 변수나 설정 값을 저장할 때 자주 사용하는 파일 |
| `.gitignore` | Git에서 추적하지 않을 파일 목록을 적는 파일 |
| `.bashrc` | Bash 셸 설정 파일 |

일반 `ls` 명령어만 실행하면 점(`.`)으로 시작하는 파일은 기본 출력에서 제외된다.
숨김 파일까지 함께 보려면 `ls -a`를 사용한다.

```bash
ls -a
```

GNU Coreutils 문서에서는 `-a` 또는 `--all` 옵션을 점(`.`)으로 시작하는 항목도 무시하지 않는 옵션으로 설명한다. [3]

---

## 4. `ls`와 `ls -a` 비교하기

홈 디렉터리로 이동한 뒤 `ls`와 `ls -a`를 비교해보면 차이를 확인할 수 있다.

```bash
cd /home/ubuntu
ls
ls -a
```

`ls`에서는 보이지 않던 항목이 `ls -a`에서는 보일 수 있다.
이때 새로 보이는 항목 대부분은 파일명이 점(`.`)으로 시작하는 숨김 파일이다.

`ls -l`과 `ls -a`는 함께 사용할 수도 있다.

```bash
ls -la
```

위 명령어는 숨김 파일까지 포함해서 자세한 형식으로 출력한다.

---

## 핵심 정리

- `ls -l`은 현재 디렉터리 내부 항목을 자세한 형식으로 보여준다.
- `ls -l` 결과의 맨 앞 글자가 `-`이면 일반 파일이다.
- `ls -l` 결과의 맨 앞 글자가 `d`이면 디렉터리다.
- Linux에서는 점(`.`)으로 시작하는 파일명을 숨김 파일처럼 다룬다.
- `ls -a`는 숨김 파일까지 포함해서 조회한다.
- `ls -la`처럼 옵션을 조합하면 숨김 파일을 자세한 형식으로 확인할 수 있다.

---

## 출처

- [1] GNU Coreutils Manual, `ls` long format option - <https://www.gnu.org/software/coreutils/manual/coreutils.html>
- [2] Linux man-pages, `inode(7)` - <https://man7.org/linux/man-pages/man7/inode.7.html>
- [3] GNU Coreutils Manual, which files are listed - <https://www.gnu.org/software/coreutils/manual/html_node/Which-files-are-listed.html>
