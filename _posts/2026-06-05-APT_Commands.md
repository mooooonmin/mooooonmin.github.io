---
title: APT Commands
category: a
date: 2026-06-05 00:00:00 +0900
tags: [linux, ubuntu, apt, package-manager, install, update, purge]
---

## 1. APT 명령어를 사용하는 이유

현재 실습 환경이 Ubuntu라면 패키지 매니저로 `apt`를 사용한다.
`apt`는 Ubuntu에서 패키지를 설치, 업데이트, 삭제할 때 자주 사용하는 명령어다.

Ubuntu 공식 문서는 APT 명령이 새 소프트웨어 패키지 설치, 기존 패키지 업그레이드, 패키지 목록 갱신 등에 사용된다고 설명한다. [1]

이번 글에서는 자주 사용하는 `apt` 명령어 4가지를 정리한다.

| 작업 | 명령어 |
|---|---|
| 패키지 설치 | `sudo apt install [패키지명]` |
| 패키지 목록 최신화 | `sudo apt update` |
| 설치된 패키지 확인 | `sudo apt list --installed` |
| 패키지 삭제 | `sudo apt purge --auto-remove [패키지명]` |

---

## 2. 패키지 설치하기

패키지를 설치할 때는 `apt install`을 사용한다.

```bash
sudo apt install [패키지명]
```

예를 들어 Ubuntu 컴퓨터에 `nginx`를 설치하려면 아래처럼 입력한다.

```bash
sudo apt install nginx
```

이 명령어를 실행하면 APT는 패키지 저장소에서 `nginx` 패키지를 내려받아 설치한다.
여기서 패키지는 프로그램, 소프트웨어, 라이브러리 같은 설치 단위를 의미한다.

Ubuntu manpage의 `apt` 문법에도 `install pkg` 형태가 포함되어 있다. [2]

---

## 3. 패키지 목록 최신화하기

패키지를 설치하기 전에는 보통 패키지 목록을 최신화한다.

```bash
sudo apt update
```

패키지 목록 최신화란 현재 Ubuntu 컴퓨터가 알고 있는 설치 가능 패키지 목록을 최신 상태로 갱신하는 작업이다.

Ubuntu 컴퓨터는 내부적으로 패키지 저장소에서 어떤 소프트웨어를 설치할 수 있는지에 대한 목록을 가지고 있다.
예시로 표현하면 아래와 비슷한 목록이라고 생각하면 된다.

```text
mysql 7.68.0
nginx 2.15.2
curl 8.5.0
git 2.39.2
vim 9.0.1677
openssh-server 1:9.0p1-1
python3 3.10.12-1
gcc 12.3.0-1
make 4.3-4.1build1
docker.io 24.0.5-0ubuntu1~22.04.1
postgresql 14.10-0ubuntu0.22.04.1
```

실제 목록이 위와 같은 형태로만 보이는 것은 아니지만, 핵심은 현재 컴퓨터가 설치 가능한 패키지 이름과 버전 정보를 가지고 있다는 점이다.

패키지 저장소에는 새로운 패키지가 추가되거나 기존 패키지 버전이 변경될 수 있다.
하지만 내 Ubuntu 컴퓨터의 패키지 목록이 저장소와 실시간으로 자동 동기화되는 것은 아니다.

그래서 패키지를 설치하기 전에 아래 명령어로 목록을 최신화한다.

```bash
sudo apt update
```

Ubuntu 공식 튜토리얼도 `apt update`가 로컬 시스템의 APT 데이터베이스를 업데이트하고, 패키지 인덱스에서 최신 메타데이터를 가져온다고 설명한다. [3]

---

## 4. 설치된 패키지 확인하기

패키지를 설치한 뒤 실제로 잘 설치되었는지 확인하고 싶을 때가 있다.
이때는 `apt list --installed`를 사용할 수 있다.

현재 컴퓨터에 설치된 모든 패키지 목록을 출력하려면 아래처럼 입력한다.

```bash
sudo apt list --installed
```

설치된 패키지 중 특정 패키지만 찾고 싶다면 `grep`과 함께 사용할 수 있다.

```bash
sudo apt list --installed | grep [패키지명]
```

예를 들어 `nginx`가 설치되어 있는지 확인하려면 아래처럼 입력한다.

```bash
sudo apt list --installed | grep nginx
```

`grep`은 출력 결과에서 특정 문자열이 포함된 줄만 골라 보여주는 명령어다.
아직 `grep`을 자세히 배우지 않았다면 지금은 아래 패턴을 통째로 기억해두면 된다.

```bash
sudo apt list --installed | grep [패키지명]
```

Ubuntu manpage의 `apt` 문법에도 `list` 명령이 포함되어 있고, Ubuntu 공식 문서도 패키지 목록을 확인하는 흐름에서 `apt list`를 사용한다. [2][1]

---

## 5. 패키지 삭제하기

패키지를 삭제할 때는 `apt purge`를 사용할 수 있다.

```bash
sudo apt purge --auto-remove [패키지명]
```

예를 들어 `nginx`를 삭제하려면 아래처럼 입력한다.

```bash
sudo apt purge --auto-remove nginx
```

`apt remove`와 `apt purge`는 둘 다 패키지를 제거할 때 사용하지만 차이가 있다.

| 명령어 | 의미 |
|---|---|
| `apt remove` | 패키지는 제거하지만 설정 파일은 남길 수 있다. |
| `apt purge` | 패키지와 관련 설정 파일까지 제거한다. |

Ubuntu 공식 문서는 `apt remove`에 `--purge` 옵션을 추가하면 패키지 설정 파일도 제거한다고 설명한다. [1]
Ubuntu manpage의 `apt` 문법에도 `remove`, `purge`가 함께 언급되어 있다. [2]

`--auto-remove`는 더 이상 필요하지 않은 의존 패키지도 함께 제거할 때 사용한다.
그래서 패키지를 깔끔하게 삭제하고 싶을 때 아래 형태를 자주 사용한다.

```bash
sudo apt purge --auto-remove [패키지명]
```

---

## 6. 자주 사용하는 순서

처음에는 아래 순서만 기억해도 충분하다.

패키지를 설치할 때는 먼저 목록을 최신화하고, 그 다음 설치한다.

```bash
sudo apt update
sudo apt install [패키지명]
```

설치가 잘 되었는지 확인할 때는 아래 명령어를 사용한다.

```bash
sudo apt list --installed | grep [패키지명]
```

패키지를 삭제할 때는 아래 명령어를 사용한다.

```bash
sudo apt purge --auto-remove [패키지명]
```

실습 단계에서는 이 4가지 명령어를 자주 사용하게 된다.

---

## 핵심 정리

Ubuntu 환경에서는 패키지 매니저로 `apt`를 주로 사용한다.
자주 사용하는 명령어는 아래 4가지다.

| 작업 | 명령어 |
|---|---|
| 패키지 설치 | `sudo apt install [패키지명]` |
| 패키지 목록 최신화 | `sudo apt update` |
| 설치된 패키지 확인 | `sudo apt list --installed \| grep [패키지명]` |
| 패키지 삭제 | `sudo apt purge --auto-remove [패키지명]` |

패키지를 설치하기 전에는 `sudo apt update`로 패키지 목록을 최신화하는 습관을 들이는 것이 좋다.
패키지를 깔끔하게 삭제하고 싶다면 `apt remove`보다 `apt purge --auto-remove`를 사용할 수 있다.

---

## 출처

[1] Ubuntu Server Documentation, "Install and manage packages", <https://ubuntu.com/server/docs/package-management/>

[2] Ubuntu Manpage, "apt - command-line interface", <https://manpages.ubuntu.com/manpages/jammy/man8/apt.8.html>

[3] Ubuntu Server Documentation, "Managing your software", <https://ubuntu.com/server/docs/tutorial/managing-software/>

