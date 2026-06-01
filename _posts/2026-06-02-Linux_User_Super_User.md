---
title: User/Super User
category: u
date: 2026-06-02 00:00:20 +0900
tags: [linux, user, super-user, root, sudo, su, whoami, passwd]
---

## 1. 사용자 개념이 필요한 이유

`Permission denied` 에러가 발생한 원인을 분석하려면 사용자(user), 슈퍼 사용자(super user), 그룹(group)의 개념을 알아야 한다.
Linux의 권한은 "누가 이 파일이나 디렉터리에 접근하는가"를 기준으로 판단되기 때문이다.

입문 단계에서는 먼저 아래 두 계정을 구분하면 된다.

| 사용자 | 의미 |
|---|---|
| `ubuntu` | AWS EC2 Ubuntu 환경에서 자주 사용하는 일반 사용자 계정 |
| `root` | 시스템 관리 권한을 가진 슈퍼 사용자 계정 |

---

## 2. 사용자란?

컴퓨터 환경에서 사용자(user)는 컴퓨터에 접근하는 계정을 의미한다.
Windows나 macOS에서 여러 사용자 계정을 만들 수 있듯이, Linux에서도 여러 사용자 계정을 만들 수 있다.

사용자는 파일 소유자, 실행 권한, 홈 디렉터리, 로그인 셸 같은 정보와 연결된다.
이 정보는 시스템에서 권한을 판단할 때 사용된다.

---

## 3. 전체 사용자 계정 조회하기

Linux에서 로컬 사용자 계정 정보는 `/etc/passwd` 파일에서 확인할 수 있다.

```bash
cat /etc/passwd
```

Linux man-pages의 `passwd(5)` 문서는 `/etc/passwd`가 사용자 계정별로 한 줄씩 정보를 담고, 각 줄은 콜론(`:`)으로 구분된 필드로 구성된다고 설명한다. [1]

예시는 아래와 비슷하다.

```text
root:x:0:0:root:/root:/bin/bash
ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash
```

첫 번째 콜론(`:`) 왼쪽 값이 사용자 이름이다.

| 줄 예시 | 사용자 이름 |
|---|---|
| `root:x:0:0:root:/root:/bin/bash` | `root` |
| `ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash` | `ubuntu` |

시스템에는 `root`, `daemon`, `bin`, `sys`처럼 사용자가 직접 만들지 않은 계정도 존재할 수 있다.
처음에는 `root`와 `ubuntu`를 중심으로 이해하면 충분하다.

---

## 4. Linux 사용자 유형

입문 단계에서는 Linux 사용자를 크게 아래처럼 구분하면 된다.

| 유형 | 설명 | 예시 |
|---|---|---|
| 슈퍼 사용자 | 시스템 관리 권한을 가진 사용자 | `root` |
| 일반 사용자 | 허용된 범위 안에서 명령 실행과 파일 조작을 하는 사용자 | `ubuntu` |
| 시스템 사용자 | 서비스나 시스템 프로세스 실행을 위해 존재하는 사용자 | `daemon`, `bin`, `sys` |

처음에는 슈퍼 사용자와 일반 사용자를 구분하는 것이 중요하다.
즉, `ubuntu`는 일반 사용자이고 `root`는 슈퍼 사용자라는 점을 기억하면 된다.

---

## 5. 슈퍼 사용자란?

슈퍼 사용자(super user)는 시스템 관리 권한을 가진 계정이다.
일반적으로 `root` 계정이 슈퍼 사용자다.

Linux man-pages의 `passwd(5)` 문서는 `root` 로그인 계정을 privileged root login account, 즉 superuser로 설명한다. [1]
또한 `root`의 UID는 일반적으로 `0`이다.

```text
root:x:0:0:root:/root:/bin/bash
```

위 예시에서 세 번째 필드인 `0`이 UID다.
UID 0인 계정은 시스템에서 매우 강한 권한을 가진다.

슈퍼 사용자는 거의 모든 파일을 조작하고 대부분의 명령을 실행할 수 있다.
따라서 실수로 중요한 시스템 파일을 삭제하거나 설정을 바꿀 위험도 있다.
평소에는 일반 사용자로 작업하고, 꼭 필요한 경우에만 관리자 권한을 사용하는 것이 좋다.

---

## 6. 현재 사용자 확인하기

현재 어떤 사용자로 접속해 있는지는 두 가지 방식으로 확인할 수 있다.

첫 번째는 터미널 프롬프트를 보는 방법이다.

```text
ubuntu@ip-172-31-24-185:~$
```

`@` 왼쪽의 `ubuntu`가 현재 사용자 이름이다.

두 번째는 `whoami` 명령어를 사용하는 방법이다.

```bash
whoami
```

GNU Coreutils 문서는 `whoami`가 현재 유효 사용자 이름을 출력한다고 설명한다. [2]

예를 들어 `ubuntu` 사용자로 접속 중이면 아래처럼 출력될 수 있다.

```text
ubuntu
```

---

## 7. 슈퍼 사용자로 전환하기

슈퍼 사용자 권한이 필요한 작업을 해야 할 때는 `sudo` 또는 `su`를 사용할 수 있다.

아래 명령어는 현재 사용자가 `sudo` 권한을 가지고 있을 때 `root` 사용자 셸로 전환하는 방식이다.

```bash
sudo su
```

`su` 명령어는 다른 사용자로 전환하는 명령어다.
Linux man-pages의 `su(1)` 문서는 `su`가 로그인 세션 중 다른 사용자로 전환하는 데 사용된다고 설명한다. [3]

슈퍼 사용자로 전환되면 프롬프트의 마지막 문자가 `$`에서 `#`로 바뀌는 경우가 많다.

| 프롬프트 | 의미 |
|---|---|
| `$` | 일반 사용자로 명령 입력 중인 상태 |
| `#` | 슈퍼 사용자 권한으로 명령 입력 중인 상태 |

`#` 표시는 현재 강한 권한으로 작업 중임을 알려주는 신호로 이해하면 된다.

---

## 8. 일반 사용자로 전환하기

다른 사용자로 전환하려면 `su 사용자명` 형태를 사용할 수 있다.

```bash
su ubuntu
```

위 명령어는 `ubuntu` 사용자로 전환하라는 뜻이다.

다만 실제 환경에서는 사용자 암호 설정, `sudo` 권한, 로그인 셸 설정 등에 따라 동작이 달라질 수 있다.
AWS EC2 같은 환경에서는 일반적으로 `ubuntu` 사용자로 접속한 뒤 필요한 명령에 `sudo`를 붙이는 흐름을 많이 사용한다.

현재 어떤 사용자로 바뀌었는지 확인하려면 다시 `whoami`를 입력한다.

```bash
whoami
```

---

## 핵심 정리

- 사용자(user)는 Linux에 접근하는 계정이다.
- `/etc/passwd` 파일에서 로컬 사용자 계정 정보를 확인할 수 있다.
- `/etc/passwd` 각 줄의 첫 번째 콜론 왼쪽 값이 사용자 이름이다.
- `root`는 일반적으로 슈퍼 사용자이며 UID가 0이다.
- `ubuntu`는 AWS EC2 Ubuntu 환경에서 자주 사용하는 일반 사용자 계정이다.
- 현재 사용자는 프롬프트의 `@` 왼쪽 값이나 `whoami` 명령어로 확인할 수 있다.
- `sudo su`는 슈퍼 사용자 셸로 전환할 때 사용할 수 있다.
- 슈퍼 사용자 권한은 강력하므로 필요한 경우에만 사용해야 한다.

---

## 출처

- [1] Linux man-pages, `passwd(5)` - <https://man7.org/linux/man-pages/man5/passwd.5.html>
- [2] GNU Coreutils Manual, `whoami` invocation - <https://www.gnu.org/s/coreutils/manual/html_node/whoami-invocation.html>
- [3] Linux man-pages, `su(1)` - <https://man7.org/linux/man-pages/man1/su.1.html>
