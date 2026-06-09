---
title: Permission Denied
category: p
date: 2026-06-02 00:00:10 +0900
tags: [linux, permission, permission-denied, sudo, directory, chmod]
---

## 1. Permission denied 에러가 나는 상황

Linux에서 특정 디렉터리에 접근하려고 할 때 `Permission denied` 에러를 만날 수 있다.

예를 들어 아래처럼 `/var/log` 디렉터리에서 `amazon` 디렉터리에 접근한다고 가정해보자.

```bash
cd /var/log
ls -al
cd amazon
```

대부분의 디렉터리는 `cd`로 접근할 수 있지만, 어떤 디렉터리는 아래와 같은 에러가 발생할 수 있다.

```text
Permission denied
```

이 에러는 말 그대로 현재 사용자에게 해당 경로에 접근할 권한이 없다는 뜻이다.

---

## 2. 무조건 `sudo`를 붙이면 안 되는 이유

`Permission denied`가 발생했을 때 `sudo`를 붙이면 해결되는 경우가 있다.

```bash
sudo ls /var/log/amazon
```

하지만 원인을 모른 채 모든 명령어 앞에 `sudo`를 붙이는 습관은 좋지 않다.
권한 문제가 왜 발생했는지 이해하지 못하면, 파일 소유자나 권한 설정을 디버깅해야 할 때 원인을 찾기 어려워진다.

먼저 아래 세 가지를 확인해야 한다.

| 확인할 것 | 의미 |
|---|---|
| 현재 사용자 | 어떤 사용자로 명령어를 실행 중인지 |
| 파일 소유자 | 해당 파일이나 디렉터리를 누가 소유하는지 |
| 권한 | 현재 사용자에게 읽기, 쓰기, 실행 권한이 있는지 |

---

## 3. `ls -al`로 권한 확인하기

권한을 확인할 때는 `ls -al`을 사용한다.

```bash
ls -al
```

GNU Coreutils 문서는 `ls -l`이 파일 타입, 권한, 소유자, 그룹, 크기, 시간 정보 등을 출력한다고 설명한다. [1]

예를 들어 아래와 같은 결과가 나왔다고 가정해보자.

```text
drwx------ 2 root root 4096 Jun  2 09:00 amazon
```

이 줄은 아래처럼 나누어 볼 수 있다.

| 부분 | 의미 |
|---|---|
| `d` | 디렉터리 |
| `rwx------` | 권한 |
| `root` | 소유자 |
| `root` | 소유 그룹 |
| `amazon` | 이름 |

즉, `amazon`은 `root` 사용자가 소유한 디렉터리이고, 권한은 소유자에게만 열려 있는 상태로 볼 수 있다.

---

## 4. 권한 문자 읽기

Linux 권한은 보통 `r`, `w`, `x`로 표시된다.

| 문자 | 파일에서 의미 | 디렉터리에서 의미 |
|---|---|---|
| `r` | 파일 내용을 읽을 수 있음 | 디렉터리 안의 이름 목록을 읽을 수 있음 |
| `w` | 파일 내용을 수정할 수 있음 | 디렉터리 안에서 생성, 삭제, 이름 변경을 할 수 있음 |
| `x` | 파일을 실행할 수 있음 | 디렉터리 안으로 들어가거나 내부 항목에 접근할 수 있음 |

GNU Coreutils 문서는 파일마다 접근 종류를 제어하는 file mode bit가 있고, 디렉터리에서 execute 권한은 그 디렉터리 안의 파일에 접근하는 의미라고 설명한다. [2][3]

디렉터리에 들어가려면 특히 `x` 권한이 중요하다.
디렉터리에 `x` 권한이 없으면 `cd`로 들어가려고 할 때 `Permission denied`가 발생할 수 있다.

---

## 5. 권한 묶음 이해하기

권한은 세 묶음으로 나뉜다.

```text
rwxr-x---
```

왼쪽부터 순서대로 소유자, 그룹, 그 외 사용자 권한이다.

| 위치 | 대상 | 예시 |
|---|---|---|
| 첫 번째 세 글자 | 소유자(user) | `rwx` |
| 두 번째 세 글자 | 그룹(group) | `r-x` |
| 세 번째 세 글자 | 그 외 사용자(others) | `---` |

예를 들어 아래 권한을 보자.

```text
drwx------
```

맨 앞의 `d`는 디렉터리라는 뜻이고, 그 뒤 `rwx------`는 소유자만 읽기, 쓰기, 접근 권한을 가진다는 뜻이다.
현재 사용자가 소유자도 아니고 해당 그룹에도 포함되어 있지 않다면 접근이 거부될 수 있다.

---

## 6. Permission denied를 만났을 때 확인 순서

`Permission denied`가 발생하면 바로 `sudo`를 붙이기 전에 아래 순서로 확인한다.

1. 현재 위치와 접근하려는 경로를 확인한다.
2. `ls -al`로 대상 디렉터리의 소유자와 권한을 확인한다.
3. 현재 사용자가 소유자인지, 그룹에 포함되는지 확인한다.
4. 디렉터리에 접근할 `x` 권한이 있는지 확인한다.
5. 필요한 경우에만 `sudo`를 사용한다.

예시는 아래와 같다.

```bash
pwd
ls -al /var/log
cd /var/log/amazon
```

접근이 막히면 권한 정보를 다시 확인한다.

```bash
ls -ld /var/log/amazon
```

`ls -ld`는 디렉터리 내부 목록이 아니라 디렉터리 자체의 정보를 확인할 때 사용한다.

---

## 7. `sudo`는 언제 사용할까?

`sudo`는 현재 사용자 권한으로 할 수 없는 작업을 관리자 권한으로 실행해야 할 때 사용한다.
예를 들어 시스템 로그 디렉터리처럼 일반 사용자에게 접근 권한이 제한된 경로를 확인해야 할 때 사용할 수 있다.

```bash
sudo ls -al /var/log/amazon
```

하지만 `sudo`는 권한 제한을 우회하는 강한 도구다.
따라서 먼저 왜 권한이 없는지 확인하고, 필요한 작업인지 판단한 뒤 사용하는 것이 좋다.

---

## 정리

- `Permission denied`는 현재 사용자에게 대상 파일이나 디렉터리에 접근할 권한이 없을 때 발생한다.
- `ls -al`로 파일 타입, 권한, 소유자, 그룹 정보를 확인할 수 있다.
- 디렉터리에 들어가려면 디렉터리에 대한 `x` 권한이 필요하다.
- 권한은 소유자, 그룹, 그 외 사용자 기준으로 나뉜다.
- `sudo`를 붙이기 전에 현재 사용자, 소유자, 그룹, 권한을 먼저 확인해야 한다.
- `sudo`는 원인을 확인한 뒤 필요한 경우에만 사용하는 것이 좋다.

---

## 출처

- [1] GNU Coreutils Manual, `ls` long format information - <https://www.gnu.org/s/coreutils/manual/html_node/What-information-is-listed.html>
- [2] GNU Coreutils Manual, file permissions - <https://www.gnu.org/software/coreutils/manual/html_node/File-permissions.html>
- [3] GNU Coreutils Manual, mode structure - <https://www.gnu.org/s/coreutils/manual/html_node/Mode-Structure.html>
