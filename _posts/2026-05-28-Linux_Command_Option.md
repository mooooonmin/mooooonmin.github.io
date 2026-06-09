---
title: Option
category: o
date: 2026-05-28 00:00:00 +0900
tags: [linux, command, option, ls, shell]
---

## 1. Linux 명령어의 공통 패턴

Linux 명령어를 계속 배우다 보면 반복해서 등장하는 패턴이 있다.
그중 하나가 **옵션(option)**이다.

이전에 아래와 같은 명령어를 사용했다.

```bash
ls
ls -l
ls -a
```

세 명령어는 모두 `ls`를 사용하지만, 뒤에 붙는 값에 따라 동작이 달라진다.

| 명령어 | 의미 |
|---|---|
| `ls` | 현재 디렉터리 내부 항목 조회 |
| `ls -l` | 현재 디렉터리 내부 항목을 자세한 형식으로 조회 |
| `ls -a` | 숨김 파일까지 포함해서 조회 |

여기서 `-l`, `-a`처럼 명령어 뒤에 붙어서 동작을 바꾸는 값을 **옵션(option)**이라고 부른다.
GNU Coreutils 문서도 `ls` 명령어의 `-l`, `-a`, `--all` 같은 값을 옵션으로 설명한다. [1]

---

## 2. 옵션의 기본 형태

Linux 명령어 옵션은 보통 짧은 옵션(short option)과 긴 옵션(long option)으로 나뉜다.

| 구분 | 형태 | 예시 |
|---|---|---|
| short option | 하이픈 한 개(`-`)로 시작 | `-a`, `-l`, `-r` |
| long option | 하이픈 두 개(`--`)로 시작 | `--all`, `--help`, `--version` |

예를 들어 `ls -a`와 `ls --all`은 같은 의미로 사용할 수 있다.
GNU Coreutils 문서는 `-a`와 `--all`을 모두 점(`.`)으로 시작하는 항목을 숨기지 않는 옵션으로 설명한다. [2]

```bash
ls -a
ls --all
```

위 두 명령어는 숨김 파일까지 포함해서 현재 디렉터리 내부 항목을 조회한다.

---

## 3. 여러 옵션 함께 사용하기

하나의 명령어에서 여러 옵션을 함께 사용할 수 있다.

```bash
ls -l -a
ls -l --all
```

short option끼리는 묶어서 한 번에 쓸 수도 있다.

```bash
ls -a -l
ls -al
ls -la
```

위 명령어들은 모두 숨김 파일까지 포함해서 자세한 형식으로 조회한다.

```bash
ls -al
```

즉, `ls -al`은 아래 의미를 합친 명령어다.

| 부분 | 의미 |
|---|---|
| `ls` | 현재 디렉터리 내부 항목 조회 |
| `-a` | 숨김 파일까지 포함 |
| `-l` | 자세한 형식으로 출력 |

---

## 4. 옵션은 명령어마다 다르다

옵션은 모든 명령어에서 같은 의미로 동작하지 않는다.
`ls`에서 `-a`가 숨김 파일을 보여준다고 해서, 다른 명령어에서도 `-a`가 같은 의미로 동작한다고 볼 수는 없다.

아래처럼 명령어마다 옵션의 의미는 달라질 수 있다.

```bash
rm -rf file-name
ps -al
kill -9 PID
```

따라서 정확한 옵션 의미는 해당 명령어의 공식 문서나 manual page를 확인해야 한다.
Linux man-pages의 `ls(1)` 문서도 `ls`에서 사용할 수 있는 옵션을 별도로 나열한다. [3]

---

## 정리

- 옵션(option)은 명령어의 동작을 바꾸기 위해 붙이는 값이다.
- `-a`, `-l`처럼 하이픈 한 개로 시작하는 옵션을 short option이라고 부른다.
- `--all`, `--help`처럼 하이픈 두 개로 시작하는 옵션을 long option이라고 부른다.
- short option은 `ls -al`처럼 묶어서 사용할 수 있다.
- 옵션의 의미는 명령어마다 다르기 때문에 정확한 의미는 공식 문서를 확인해야 한다.

---

## 출처

- [1] GNU Coreutils Manual, `ls` invocation - <https://www.gnu.org/software/coreutils/manual/html_node/ls-invocation.html>
- [2] GNU Coreutils Manual, which files are listed - <https://www.gnu.org/software/coreutils/manual/html_node/Which-files-are-listed.html>
- [3] Linux man-pages, `ls(1)` - <https://man7.org/linux/man-pages/man1/ls.1.html>
