---
title: Tail Follow Log
category: t
date: 2026-06-12 00:00:10 +0900
tags: [linux, tail, log, auth-log, realtime, monitoring]
---

## 1. 로그를 실시간으로 확인해야 하는 이유

Linux에서 실행하는 프로그램은 실행 내용이나 에러를 로그 파일에 기록하는 경우가 많다.

예를 들어 Spring Boot 서버를 백그라운드에서 실행하면 `nohup.out`이나 직접 지정한 로그 파일에 로그가 쌓일 수 있다.
또한 Ubuntu 서버에서는 로그인, `sudo`, 원격 접속 같은 인증 관련 이벤트가 별도 로그 파일에 기록될 수 있다.

이미 쌓인 로그를 확인할 때는 `cat`, `less`, `vi` 같은 명령어를 사용할 수 있다.
하지만 서버를 운영하다 보면 지금 이 순간 로그가 어떻게 추가되는지 실시간으로 확인해야 할 때가 있다.

이때 사용하는 명령어가 `tail -f`이다.

---

## 2. auth.log 파일 확인하기

Ubuntu에서 인증 관련 로그를 확인할 때 `/var/log/auth.log` 파일을 볼 수 있다.

Ubuntu Community Help Wiki는 Authorization Log가 사용자 로그인, `sudo`, `sshd` 원격 로그인 같은 인증 시스템 사용을 추적하며, `/var/log/auth.log`에서 접근할 수 있다고 설명한다. [1]

먼저 `/var/log` 디렉터리로 이동한다.

```bash
cd /var/log
```

파일 목록을 확인한다.

```bash
ls
```

`auth.log` 파일이 있다면 내용을 확인할 수 있다.

```bash
cat auth.log
```

다만 로그 파일은 양이 많을 수 있다.
`cat auth.log`는 파일 전체를 한 번에 출력하므로, 로그가 매우 많으면 터미널 출력이 길어져 보기 불편할 수 있다.

그럴 때는 `vi`로 열어서 페이지 단위로 이동하며 확인할 수 있다.

```bash
vi auth.log
```

`vi` 안에서는 아래 키로 이동할 수 있다.

| 키 | 의미 |
|---|---|
| `Ctrl + f` | 다음 화면으로 이동 |
| `Ctrl + b` | 이전 화면으로 이동 |

---

## 3. tail 기본 동작

`tail`은 파일의 마지막 부분을 출력할 때 사용하는 명령어이다.

GNU Coreutils 문서는 `tail`이 각 파일의 마지막 부분을 출력하며, 기본적으로 마지막 10줄을 출력한다고 설명한다. [2]

예를 들어 아래 명령어는 `auth.log` 파일의 마지막 10줄을 출력한다.

```bash
tail auth.log
```

로그 파일은 보통 오래된 로그가 위에 있고, 새 로그가 아래에 추가된다.
따라서 최근 로그만 빠르게 보고 싶을 때는 `cat`보다 `tail`이 더 편하다.

---

## 4. tail -f로 실시간 로그 확인하기

로그가 새로 추가되는 모습을 실시간으로 확인하려면 `-f` 옵션을 사용한다.

```bash
tail -f auth.log
```

GNU Coreutils 문서는 `-f` 또는 `--follow` 옵션이 파일 끝에서 더 많은 문자를 계속 읽으려고 반복한다고 설명한다. [2]
즉 파일이 계속 커지는 상황을 따라가며 새로 추가되는 내용을 출력한다.

정리하면 아래와 같다.

| 명령어 | 의미 |
|---|---|
| `tail auth.log` | `auth.log`의 마지막 10줄 출력 |
| `tail -f auth.log` | 마지막 10줄 출력 후, 새로 추가되는 로그를 계속 출력 |

`tail -f auth.log`를 실행한 상태에서 다른 터미널이나 새 브라우저 창으로 Ubuntu 서버에 접속해보면, 접속 관련 로그가 추가되는 모습을 실시간으로 확인할 수 있다.

실시간 확인을 멈추려면 아래 키를 누른다.

```text
Ctrl + c
```

---

## 5. auth.log가 바로 보이지 않을 때

환경에 따라 `/var/log/auth.log` 파일이 없거나, 현재 사용자 권한으로 읽을 수 없을 수 있다.

먼저 파일이 있는지 확인한다.

```bash
ls -l /var/log/auth.log
```

권한 문제로 읽을 수 없다면 `sudo`를 붙여 확인할 수 있다.

```bash
sudo tail -f /var/log/auth.log
```

다만 모든 Linux 배포판이 인증 로그를 같은 파일에 저장하는 것은 아니다.
Ubuntu Community Help Wiki는 Authorization Log의 경로로 `/var/log/auth.log`를 설명하지만, 실제 로그 저장 방식은 배포판과 로깅 설정에 따라 달라질 수 있다. [1]

따라서 실습 환경에서 파일이 없다면 먼저 `/var/log` 안의 로그 파일 목록을 확인해야 한다.

```bash
ls /var/log
```

---

## 6. 애플리케이션 로그에도 사용할 수 있다

`tail -f`는 `auth.log`뿐 아니라 직접 만든 로그 파일에도 사용할 수 있다.

예를 들어 Spring Boot 서버 로그를 `result.log`에 저장하도록 실행했다면 아래처럼 실시간으로 확인할 수 있다.

```bash
tail -f result.log
```

`nohup.out`에 로그가 쌓이고 있다면 아래처럼 확인한다.

```bash
tail -f nohup.out
```

새 로그가 파일 아래쪽에 계속 추가되는 구조라면 `tail -f`로 실시간 확인이 가능하다.

---

## 7. 실무에서 자주 쓰는 흐름

로그를 확인할 때는 보통 아래 순서로 진행한다.

1. 로그 파일이 있는 디렉터리로 이동한다.
2. `ls`로 파일 이름을 확인한다.
3. 기존 로그를 간단히 확인한다.
4. `tail -f`로 새 로그가 쌓이는지 실시간으로 확인한다.

예시는 아래와 같다.

```bash
cd /var/log
ls
tail auth.log
tail -f auth.log
```

애플리케이션 로그라면 아래처럼 확인할 수 있다.

```bash
ls
tail result.log
tail -f result.log
```

로그를 실시간으로 보면서 다른 터미널에서 요청을 보내면, 요청 시점에 어떤 로그가 새로 추가되는지 확인하기 쉽다.

---

## 정리

`tail`은 파일의 마지막 부분을 출력하는 명령어이다.

```bash
tail auth.log
```

`tail -f`는 파일의 마지막 10줄을 출력한 뒤, 파일에 새로 추가되는 내용을 계속 출력한다.

```bash
tail -f auth.log
```

Ubuntu 인증 로그를 실시간으로 보고 싶다면 아래처럼 사용할 수 있다.

```bash
sudo tail -f /var/log/auth.log
```

Spring Boot 같은 애플리케이션 로그도 파일에 쌓이고 있다면 같은 방식으로 확인할 수 있다.

```bash
tail -f nohup.out
tail -f result.log
```

실시간 로그 확인을 멈추려면 `Ctrl + c`를 누른다.

---

## 출처

[1] Ubuntu Community Help Wiki, "LinuxLogFiles", 확인일: 2026-06-12, <https://help.ubuntu.com/community/LinuxLogFiles>

[2] GNU Coreutils Manual, "tail invocation", 확인일: 2026-06-12, <https://www.gnu.org/software/coreutils/manual/html_node/tail-invocation.html>
