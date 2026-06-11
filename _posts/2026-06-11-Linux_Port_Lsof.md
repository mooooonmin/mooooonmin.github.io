---
title: Linux Port Lsof
category: l
date: 2026-06-11 00:00:00 +0900
tags: [linux, port, lsof, process, pid, spring-boot]
---

## 1. 포트 충돌 에러가 발생하는 상황

Spring Boot 서버를 실행했을 때 아래와 같은 에러가 발생할 수 있다.

```text
Port 8080 was already in use
```

이 메시지는 8080번 포트를 이미 다른 프로세스가 사용하고 있어서 새 Spring Boot 서버가 같은 포트로 실행되지 못했다는 의미로 해석할 수 있다.

Spring Boot 공식 문서는 독립 실행형 애플리케이션의 기본 HTTP 포트가 `8080`이고, `server.port` 설정으로 바꿀 수 있다고 설명한다. [1]
따라서 별도 설정 없이 Spring Boot 웹 애플리케이션을 실행하면 8080번 포트를 사용하려고 한다.

실무에서는 같은 서버에서 이전에 실행한 Spring Boot 프로세스가 아직 종료되지 않았거나, 다른 애플리케이션이 8080번 포트를 사용하고 있어서 이 에러를 자주 만난다.

---

## 2. 포트란?

포트(port)는 네트워크 통신에서 서비스를 구분하기 위해 사용하는 숫자이다.

RFC 7605는 포트 번호를 16비트 숫자라고 설명하고, 포트 번호가 호스트 안에서 전송 계층 연결을 구분하고 서비스를 식별하는 데 사용된다고 설명한다. [2]

16비트로 표현할 수 있는 값의 개수는 아래처럼 계산한다.

```text
2^16 = 65536
```

숫자는 0부터 시작하므로 가능한 포트 번호 범위는 아래와 같다.

```text
0 ~ 65535
```

입문 단계에서는 포트를 한 컴퓨터 안에서 실행 중인 서버 프로그램을 찾아가기 위한 번호라고 이해하면 된다.
예를 들어 Spring Boot 서버가 8080번 포트에서 대기하고 있다면, 클라이언트는 해당 서버에 접속할 때 8080번 포트를 목적지로 사용한다.

---

## 3. 포트 충돌이 발생하는 이유

하나의 서버 프로그램은 특정 IP 주소, 프로토콜, 포트 조합에 묶여서 요청을 기다린다.

예를 들어 어떤 Spring Boot 프로세스가 이미 8080번 포트에서 요청을 기다리고 있다고 해보자.
이 상태에서 다른 Spring Boot 서버나 Node.js 서버가 같은 주소와 같은 8080번 포트로 다시 실행되려고 하면 포트 충돌이 발생할 수 있다.

입문 단계에서는 아래처럼 기억하면 된다.

| 상황 | 결과 |
|---|---|
| 8080번 포트를 아무 프로세스도 사용하지 않음 | Spring Boot 서버 실행 가능 |
| 8080번 포트를 이미 다른 프로세스가 사용 중 | 같은 포트로 서버 실행 실패 가능 |

따라서 `Port 8080 was already in use` 에러를 만나면 먼저 8080번 포트를 어떤 프로세스가 사용 중인지 확인해야 한다.

---

## 4. 특정 포트 번호를 사용하는 프로세스 조회하기

특정 포트 번호를 사용하는 프로세스를 확인할 때 `lsof` 명령어를 사용할 수 있다.

```bash
sudo lsof -i:8080
```

`lsof`는 open file 목록을 출력하는 도구이다.
Linux에서는 네트워크 소켓도 파일처럼 다뤄지므로, `lsof`로 네트워크 포트를 사용하는 프로세스를 확인할 수 있다.

Linux man-pages의 `lsof(8)` 문서는 `lsof`를 open file을 나열하는 명령어로 설명한다. [3]
또한 `-i` 옵션은 지정한 Internet address와 일치하는 파일 목록을 선택한다고 설명한다. [3]

명령어는 아래처럼 읽으면 된다.

| 부분 | 의미 |
|---|---|
| `sudo` | 관리자 권한으로 명령어 실행 |
| `lsof` | 열린 파일을 조회 |
| `-i:8080` | Internet address 중 8080번 포트와 관련된 항목 조회 |

실습에서는 다른 사용자 또는 시스템 프로세스까지 확인해야 할 수 있으므로 `sudo`를 붙여 실행하는 편이 안전하다.

---

## 5. lsof 출력에서 봐야 할 항목

`sudo lsof -i:8080`을 실행하면 아래와 비슷한 출력이 나올 수 있다.

```text
COMMAND    PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
java    110225 ubuntu   12u  IPv6 123456      0t0  TCP *:8080 (LISTEN)
```

처음에는 모든 항목을 이해하려고 하기보다 `COMMAND`와 `PID`를 먼저 보면 된다.

| 항목 | 의미 |
|---|---|
| `COMMAND` | 프로세스와 연결된 명령 이름 |
| `PID` | 프로세스를 식별하기 위한 ID |
| `NAME` | 포트와 연결 상태 |

Linux man-pages의 `lsof(8)` 문서는 `COMMAND` 열이 프로세스와 연결된 UNIX command 이름을 담고, `PID` 열이 프로세스 ID 번호라고 설명한다. [3]

위 예시에서는 `java` 프로세스가 8080번 포트를 사용하고 있고, PID는 `110225`이다.
Spring Boot 서버는 Java 애플리케이션이므로 `COMMAND`에 `java`가 보이면 Spring Boot 프로세스일 가능성이 있다.

다만 `COMMAND`만 보고 확정하면 안 된다.
정확히 어떤 명령어로 실행된 프로세스인지 확인하려면 `ps aux`로 전체 실행 명령을 확인한다.

---

## 6. PID로 정확한 실행 명령어 확인하기

`lsof` 출력에서 PID를 확인했다면 `ps aux`와 `grep`으로 해당 프로세스의 전체 실행 명령어를 확인할 수 있다.

```bash
ps aux | grep 110225
```

Linux man-pages의 `ps(1)` 문서는 `ps`가 현재 프로세스의 스냅샷을 보고한다고 설명한다. [4]

예시 출력은 아래와 비슷하다.

```text
ubuntu 110225  2.1  8.3 3456788 169000 ? Sl 10:20 0:05 java -jar linux-springboot-0.0.1-SNAPSHOT.jar
```

이 출력에서 `java -jar linux-springboot-0.0.1-SNAPSHOT.jar`가 보이면, 해당 PID가 Spring Boot 실행 프로세스라는 것을 더 명확하게 확인할 수 있다.

흐름은 아래와 같다.

| 단계 | 명령어 | 확인하는 값 |
|---|---|---|
| 1 | `sudo lsof -i:8080` | 8080번 포트를 사용하는 PID |
| 2 | `ps aux | grep [PID]` | 해당 PID의 전체 실행 명령어 |

---

## 7. 특정 포트 번호를 사용하는 프로세스 종료하기

8080번 포트를 사용 중인 프로세스가 종료해도 되는 대상이라고 확인했다면 `kill` 명령어로 종료 요청을 보낼 수 있다.

```bash
kill 110225
```

Linux man-pages의 `kill(1)` 문서는 `kill` 명령어가 지정한 프로세스 또는 프로세스 그룹에 시그널을 보낸다고 설명한다. [5]
따라서 `kill [PID]`는 해당 PID의 프로세스에 종료 요청 시그널을 보내는 명령어라고 이해하면 된다.

종료 후에는 다시 `lsof`로 포트가 비었는지 확인한다.

```bash
sudo lsof -i:8080
```

아무 출력이 없다면 현재 8080번 포트를 사용하는 프로세스가 조회되지 않은 것이다.

주의할 점은 `kill`을 실행하기 전에 반드시 PID가 어떤 프로세스인지 확인해야 한다는 것이다.
확실하지 않은 시스템 프로세스나 다른 사용자의 중요한 프로세스를 종료하면 서비스 장애가 발생할 수 있다.

---

## 8. Spring Boot 서버 다시 실행하기

8080번 포트를 비웠다면 원하는 Spring Boot 서버를 다시 실행한다.

```bash
cd ~/linux-springboot/build/libs
nohup java -jar linux-springboot-0.0.1-SNAPSHOT.jar &
```

실행 후 8080번 포트에서 프로세스가 떠 있는지 확인한다.

```bash
sudo lsof -i:8080
```

로그도 함께 확인한다.

```bash
cat nohup.out
```

이번에는 `Port 8080 was already in use` 메시지가 보이지 않고 Spring Boot가 정상적으로 시작됐다는 로그가 보이면 포트 충돌 문제가 해결된 것이다.

---

## 정리

`Port 8080 was already in use`는 8080번 포트를 이미 다른 프로세스가 사용 중일 때 발생할 수 있는 에러이다.

포트 사용 프로세스는 아래 명령어로 확인한다.

```bash
sudo lsof -i:8080
```

`lsof` 출력에서 `PID`를 확인한 뒤, 정확한 실행 명령어는 아래처럼 확인한다.

```bash
ps aux | grep [PID]
```

종료해도 되는 프로세스라고 확인한 경우에만 아래처럼 종료 요청을 보낸다.

```bash
kill [PID]
```

마지막으로 다시 `sudo lsof -i:8080`과 `cat nohup.out`으로 포트 사용 상태와 Spring Boot 로그를 확인한다.

---

## 출처

[1] Spring Boot Reference Documentation, "Embedded Web Servers - Change the HTTP Port", 확인일: 2026-06-11, <https://docs.spring.io/spring-boot/how-to/webserver.html>

[2] IETF RFC 7605, "Recommendations on Using Assigned Transport Port Numbers", Section 5, 확인일: 2026-06-11, <https://datatracker.ietf.org/doc/html/rfc7605#section-5>

[3] Linux man-pages, "lsof(8) - Linux manual page", 확인일: 2026-06-11, <https://man7.org/linux/man-pages/man8/lsof.8.html>

[4] Linux man-pages, "ps(1) - Linux manual page", 확인일: 2026-06-11, <https://man7.org/linux/man-pages/man1/ps.1.html>

[5] Linux man-pages, "kill(1) - Linux manual page", 확인일: 2026-06-11, <https://man7.org/linux/man-pages/man1/kill.1.html>
