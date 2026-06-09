---
title: Nohup Background
category: n
date: 2026-06-09 00:00:20 +0900
tags: [linux, nohup, background, foreground, process, spring-boot]
---

## 1. 포그라운드와 백그라운드란?

터미널 창을 끄더라도 프로그램이 계속 실행되도록 만들기 전에, 포그라운드(foreground)와 백그라운드(background)의 개념을 알아야 한다.

포그라운드는 내가 실행시킨 프로그램이 터미널 화면에서 직접 실행되고, 실행 내용이 화면에 출력되는 상태를 의미한다.
포그라운드 상태에서는 해당 프로그램이 터미널을 점유하고 있기 때문에 같은 터미널에서 다른 명령어를 입력하기 어렵다.

백그라운드는 내가 실행시킨 프로그램이 터미널 뒤쪽에서 계속 실행되는 상태를 의미한다.
백그라운드 상태에서는 터미널 입력창을 다시 사용할 수 있으므로, 같은 터미널에서 다른 명령어를 추가로 입력할 수 있다.

GNU Bash 매뉴얼은 명령어 뒤에 `&`를 붙이면 명령어를 백그라운드에서 실행한다고 설명한다. [1]

---

## 2. 포그라운드로 Spring Boot 실행하기

먼저 Spring Boot 서버를 포그라운드에서 실행해보자.

```bash
cd ~/linux-springboot/build/libs
java -jar linux-springboot-0.0.1-SNAPSHOT.jar
```

서버가 정상적으로 실행됐다면 브라우저에서 아래 주소로 접속해본다.

```text
http://{EC2 인스턴스의 Public IP 주소}:8080
```

이 방식으로 실행하면 Spring Boot 서버 로그가 터미널에 계속 출력된다.
그리고 같은 터미널에서 다른 명령어를 입력해도 바로 실행되지 않는다.

그 이유는 Spring Boot 서버가 포그라운드 상태로 실행되고 있기 때문이다.
서버를 실행한 상태에서 다른 작업도 하고 싶다면 서버를 백그라운드에서 실행해야 한다.

---

## 3. 실행 중인 서버 종료하기

포그라운드에서 실행 중인 Spring Boot 서버는 `Ctrl + c`로 종료할 수 있다.

```text
Ctrl + c
```

서버가 종료됐는지 확인하려면 브라우저에서 다시 접속해보면 된다.

```text
http://{EC2 인스턴스의 Public IP 주소}:8080
```

접속이 되지 않는다면 서버가 종료된 것이다.

---

## 4. 백그라운드로 Spring Boot 실행하기

프로그램을 백그라운드에서 실행하려면 명령어 뒤에 `&`를 붙인다.
하지만 터미널 연결을 끊은 뒤에도 계속 실행되도록 만들려면 `nohup`도 함께 사용하는 것이 일반적이다.

기본 형태는 아래와 같다.

```bash
nohup [프로그램을 실행하는 명령어] &
```

Spring Boot 서버를 실행하는 예시는 아래와 같다.

```bash
nohup java -jar linux-springboot-0.0.1-SNAPSHOT.jar &
```

이 명령어를 입력하고 `Enter`를 누르면 다시 명령어를 입력할 수 있는 상태가 된다.
서버는 백그라운드에서 계속 실행되고, 터미널은 다른 명령어를 받을 수 있게 된다.

GNU Coreutils 매뉴얼은 `nohup`을 hangup 신호에 영향을 받지 않게 명령어를 실행하는 도구로 설명한다. [2]
따라서 터미널 연결이 끊어졌을 때도 프로세스가 종료되지 않도록 만들고 싶을 때 `nohup`을 사용한다.

---

## 5. 서버가 실행 중인지 확인하기

백그라운드로 실행한 서버가 정상적으로 동작하는지는 두 가지 방식으로 확인할 수 있다.

### 브라우저로 확인하기

브라우저에서 서버 주소로 접속한다.

```text
http://{EC2 인스턴스의 Public IP 주소}:8080
```

접속이 정상적으로 된다면 Spring Boot 서버가 실행 중인 것이다.

### Linux 명령어로 확인하기

터미널에서는 `ps aux`와 `grep`을 함께 사용해서 Java 프로세스를 찾을 수 있다.

```bash
ps aux | grep java
```

출력 결과에 `linux-springboot-0.0.1-SNAPSHOT.jar`가 보인다면 Spring Boot 서버 프로세스가 실행 중인 것이다.

---

## 6. 터미널 창을 끈 뒤에도 실행되는지 확인하기

백그라운드 실행 상태를 확인한 뒤에는 터미널 창을 종료해본다.

그 다음 새 터미널을 열고 다시 프로세스를 확인한다.

```bash
ps aux | grep java
```

프로세스가 계속 조회된다면 터미널 창을 꺼도 서버가 종료되지 않고 계속 실행되고 있는 것이다.

브라우저에서도 다시 서버 주소로 접속해본다.

```text
http://{EC2 인스턴스의 Public IP 주소}:8080
```

접속이 정상적으로 된다면 `nohup`과 `&`를 사용한 백그라운드 실행이 제대로 적용된 것이다.

---

## 7. `nohup`과 `&`의 역할 구분하기

`nohup`과 `&`는 같이 쓰는 경우가 많지만 역할이 다르다.

| 구분 | 역할 |
|---|---|
| `nohup` | 터미널 연결이 끊겨도 명령어가 hangup 신호의 영향을 받지 않도록 실행한다. |
| `&` | 명령어를 백그라운드에서 실행해서 터미널 입력창을 다시 사용할 수 있게 한다. |

따라서 아래 명령어는 두 가지 의미를 함께 가진다.

```bash
nohup java -jar linux-springboot-0.0.1-SNAPSHOT.jar &
```

명령어 앞의 `nohup`은 터미널 종료 후에도 프로세스가 계속 실행되도록 돕는다.
명령어 뒤의 `&`는 프로세스를 백그라운드에서 실행하도록 만든다.

---

## 정리

포그라운드는 실행한 프로그램이 터미널을 점유하는 상태이다.
백그라운드는 프로그램이 터미널 뒤쪽에서 실행되어, 같은 터미널에서 다른 명령어를 입력할 수 있는 상태이다.

터미널 창을 끄더라도 서버가 계속 실행되도록 만들고 싶다면 `nohup`과 `&`를 함께 사용할 수 있다.

```bash
nohup [프로그램을 실행하는 명령어] &
```

Spring Boot 서버 예시는 아래와 같다.

```bash
nohup java -jar linux-springboot-0.0.1-SNAPSHOT.jar &
```

실행 후에는 `ps aux | grep java`로 서버 프로세스가 살아 있는지 확인할 수 있다.

```bash
ps aux | grep java
```

---

## 출처

[1] GNU Bash Manual, "Lists of Commands", <https://www.gnu.org/software/bash/manual/html_node/Lists.html>

[2] GNU Coreutils Manual, "nohup invocation", <https://www.gnu.org/software/coreutils/manual/html_node/nohup-invocation.html>
