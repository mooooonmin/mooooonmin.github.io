---
title: Tilde
category: t
date: 2026-05-28 00:00:20 +0900
tags: [linux, tilde, home-directory, path, cd, bash]
---

## 1. 경로에서 `~`가 보이는 상황

Linux 터미널에서 디렉터리를 이동하다 보면 현재 경로가 절대 경로로 표시될 때가 있다.

```bash
cd /var/log
cd /home
```

하지만 사용자의 홈 디렉터리로 이동하면 전체 경로 대신 물결 표시(`~`)가 보일 수 있다.

```bash
cd /home/ubuntu
```

여기서 `~`는 임의의 장식 문자가 아니라 **현재 사용자의 홈 디렉터리**를 뜻하는 표현이다.

---

## 2. 홈 디렉터리란?

Linux에서는 하나의 컴퓨터에 여러 사용자를 만들 수 있다.
각 사용자에게는 개인 작업 공간으로 사용할 디렉터리가 할당될 수 있는데, 이를 **홈 디렉터리(home directory)**라고 부른다.

예를 들어 사용자 이름이 `ubuntu`라면 홈 디렉터리는 보통 아래 경로다.

```text
/home/ubuntu
```

단, 모든 Linux 환경에서 홈 디렉터리가 반드시 `/home/{사용자명}` 형태라고 단정할 수는 없다.
GNU Bash 문서는 `~`가 `HOME` 셸 변수 값으로 확장된다고 설명한다. [1]
GNU C Library 문서도 `~`가 `HOME` 환경 변수의 값을 현재 사용자의 홈 디렉터리 이름으로 사용한다고 설명한다. [2]

---

## 3. `~`의 의미

경로에서 `~`는 현재 사용자의 홈 디렉터리를 짧게 표현한 것이다.

| 표현 | 의미 |
|---|---|
| `~` | 현재 사용자의 홈 디렉터리 |
| `~/memo.txt` | 현재 사용자의 홈 디렉터리 안에 있는 `memo.txt` |
| `~/project` | 현재 사용자의 홈 디렉터리 안에 있는 `project` 디렉터리 |

예를 들어 현재 사용자가 `ubuntu`이고 홈 디렉터리가 `/home/ubuntu`라면 아래 두 명령어는 같은 위치로 이동한다.

```bash
cd /home/ubuntu
cd ~
```

따라서 `~`는 긴 홈 디렉터리 경로를 짧게 쓰기 위한 표현으로 이해하면 된다.

---

## 4. 직접 확인하기

루트 디렉터리(`/`)에서 홈 디렉터리까지 직접 이동해보면 `~`의 의미를 확인할 수 있다.

```bash
cd /
ls

cd home
ls

cd ubuntu
pwd
```

이번에는 `~`를 사용해서 바로 홈 디렉터리로 이동해보자.

```bash
cd /
cd ~
pwd
```

두 경우 모두 같은 홈 디렉터리 경로가 출력된다면, 현재 환경에서 `~`가 그 홈 디렉터리를 가리킨다는 뜻이다.

---

## 5. `~`와 다른 경로 표현 비교

`~`는 절대 경로처럼 보이지 않지만, 셸에서 먼저 홈 디렉터리 경로로 바뀐 뒤 명령어에 전달된다.
이 과정을 **tilde expansion**이라고 부른다.

| 명령어 | 의미 |
|---|---|
| `cd ~` | 현재 사용자의 홈 디렉터리로 이동 |
| `cd ~/project` | 홈 디렉터리 안의 `project` 디렉터리로 이동 |
| `pwd` | 현재 디렉터리의 실제 경로 출력 |

Bash 문서는 따옴표로 감싸지 않은 `~` 접두어가 tilde expansion 대상이라고 설명한다. [1]
따라서 터미널에서 경로를 입력할 때 `~`는 사용자의 홈 디렉터리를 간단히 쓰는 방법으로 사용할 수 있다.

---

## 정리

- `~`는 현재 사용자의 홈 디렉터리를 의미한다.
- 사용자 이름이 `ubuntu`이고 홈 디렉터리가 `/home/ubuntu`라면 `~`는 `/home/ubuntu`처럼 사용할 수 있다.
- `cd ~`는 홈 디렉터리로 이동하는 명령어다.
- `~/project`는 홈 디렉터리 안의 `project` 디렉터리를 뜻한다.
- `~`가 실제 경로로 바뀌는 과정을 tilde expansion이라고 부른다.

---

## 출처

- [1] GNU Bash Reference Manual, Tilde Expansion - <https://www.gnu.org/software/bash/manual/html_node/Tilde-Expansion.html>
- [2] GNU C Library Manual, Tilde Expansion - <https://www.gnu.org/software/libc/manual/html_node/Tilde-Expansion.html>
