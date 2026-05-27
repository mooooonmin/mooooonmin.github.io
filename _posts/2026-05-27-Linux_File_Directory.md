---
title: File과 Directory
category: f
date: 2026-05-27 00:00:00 +0900
tags: [linux, file, directory, path, pwd, cd, ls]
---

## 1. Linux에서 File과 Directory의 의미

Windows나 macOS에서 말하는 파일(file)과 폴더(folder)의 개념은 Linux에서는 조금 다르게 이해해야 한다.

Linux에서는 보통 폴더(folder)라는 표현보다 **디렉터리(directory)**라는 표현을 사용한다.
처음 공부할 때는 Windows의 폴더와 Linux의 디렉터리를 같은 개념으로 이해해도 된다.

앞으로 Linux 환경에서는 다음 표현에 익숙해지는 것이 좋다.

| 표현 | 의미 |
|---|---|
| 파일(file) | 텍스트 파일, 이미지 파일, 실행 파일처럼 데이터를 담는 항목 |
| 디렉터리(directory) | 파일과 다른 디렉터리를 담는 항목 |
| 경로(path) | 파일이나 디렉터리가 어디에 있는지 나타내는 주소 |

---

## 2. Linux에서는 많은 것을 File로 다룬다

Linux에서는 일반 파일뿐 아니라 디렉터리, 심볼릭 링크, 디바이스 파일, 소켓 같은 항목도 파일 시스템 안에서 파일의 한 종류로 다룬다.
Linux manual의 `inode(7)` 문서도 파일 타입으로 일반 파일, 디렉터리, 심볼릭 링크, 블록 디바이스, 문자 디바이스, FIFO, 소켓을 구분한다. [1]

처음에는 아래처럼만 구분해도 충분하다.

| 구분 | 설명 |
|---|---|
| 일반 파일 | 텍스트, 이미지, 동영상, 실행 파일처럼 일반적으로 말하는 파일 |
| 디렉터리 파일 | Windows의 폴더처럼 다른 파일을 담는 파일 |
| 특수 파일 | 심볼릭 링크, 디바이스 파일, 소켓 파일처럼 시스템이 특별한 방식으로 사용하는 파일 |

즉, Linux에서 "파일"이라는 말은 Windows에서 생각하는 일반 파일보다 더 넓은 의미로 쓰일 수 있다.

---

## 3. 현재 디렉터리 경로 조회하기

컴퓨터에서 경로(path)는 특정 파일이나 디렉터리가 어디에 있는지를 설명하는 주소다.
Linux 환경에서 현재 내가 위치한 경로를 확인할 때는 `pwd` 명령어를 사용한다.

```bash
pwd
```

`pwd`는 `print working directory`의 줄임말이다.
GNU Coreutils 문서에서도 `pwd`를 현재 디렉터리 이름을 출력하는 명령어로 설명한다. [2]

---

## 4. 디렉터리 이동하기

디렉터리를 이동할 때는 `cd` 명령어를 사용한다.

```bash
cd /var/log/apt
pwd
```

`cd`는 `change directory`의 줄임말이다.
Bash manual에서는 `cd`를 현재 작업 디렉터리를 변경하는 명령어로 설명한다. [3]

상위 디렉터리로 이동할 때는 `..`을 사용한다.

```bash
cd ..
pwd

cd ..
pwd
```

`..`은 현재 위치에서 한 단계 위의 디렉터리를 뜻한다.
최상위 디렉터리까지 올라간 뒤에는 더 이상 올라갈 상위 디렉터리가 없기 때문에 경로가 그대로 유지된다.

---

## 5. Linux의 기본 디렉터리 구조

Linux 파일 시스템의 가장 위에 있는 디렉터리는 `/`이며, 이를 **루트 디렉터리(root directory)**라고 부른다.
Filesystem Hierarchy Standard는 `/` 아래에 `/bin`, `/boot`, `/dev`, `/etc`, `/home`, `/opt`, `/tmp`, `/usr`, `/var` 같은 주요 디렉터리를 정의한다. [4]

Linux에서는 경로를 표현할 때 슬래시(`/`)를 사용한다.

```text
/var/log
```

위 경로는 루트 디렉터리(`/`) 아래의 `var` 디렉터리, 그 안의 `log` 디렉터리를 뜻한다.

대표적인 디렉터리는 아래처럼 이해할 수 있다.

| 디렉터리 | 의미 |
|---|---|
| `/` | 전체 파일 시스템의 시작점 |
| `/bin` | 기본 명령어 실행 파일이 있는 디렉터리 |
| `/boot` | 부팅에 필요한 파일이 있는 디렉터리 |
| `/home` | 일반 사용자의 홈 디렉터리가 있는 위치 |
| `/opt` | 추가 애플리케이션을 설치할 때 사용하는 디렉터리 |
| `/var` | 로그처럼 실행 중에 변하는 데이터가 저장되는 디렉터리 |

---

## 6. 현재 디렉터리 내부 조회하기

현재 디렉터리 안에 어떤 파일과 디렉터리가 있는지 확인할 때는 `ls` 명령어를 사용한다.

```bash
ls
```

GNU Coreutils 문서에서는 `ls`를 파일 정보를 나열하는 명령어로 설명한다. [2]

예를 들어 루트 디렉터리에서 `ls`를 실행하면 Linux의 기본 디렉터리 구조를 확인할 수 있다.

```bash
cd /
ls
```

`var` 디렉터리와 `log` 디렉터리로 이동하면서 내부 항목을 확인할 수도 있다.

```bash
cd var
ls

cd log
ls
```

만약 일반 파일을 디렉터리로 착각하고 `cd` 명령어로 이동하려고 하면 `Not a directory` 같은 오류가 발생할 수 있다.
이 메시지는 이동하려는 대상이 디렉터리가 아니라는 뜻이다.

```bash
cd btmp
```

---

## 핵심 정리

- Linux에서는 폴더보다 디렉터리(directory)라는 표현을 사용한다.
- Linux에서 파일(file)은 일반 파일뿐 아니라 디렉터리, 링크, 디바이스 파일 같은 항목까지 포함하는 넓은 개념으로 쓰일 수 있다.
- `pwd`는 현재 디렉터리 경로를 확인할 때 사용한다.
- `cd`는 디렉터리를 이동할 때 사용한다.
- `ls`는 현재 디렉터리 안의 항목을 확인할 때 사용한다.
- `/`는 Linux 파일 시스템의 최상위 디렉터리이며 루트 디렉터리라고 부른다.

---

## 출처

- [1] Linux man-pages, `inode(7)` - <https://man7.org/linux/man-pages/man7/inode.7.html>
- [2] GNU Coreutils Manual - <https://www.gnu.org/software/coreutils/manual/coreutils.html>
- [3] GNU Bash Reference Manual - <https://www.gnu.org/software/bash/manual/bash.html>
- [4] Filesystem Hierarchy Standard - <https://specifications.freedesktop.org/fhs/latest/rootRequirements.html>
