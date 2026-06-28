---
title: Log Line Fields
category: l
date: 2026-06-29 00:00:00 +0900
tags: [logging, spring-boot, timestamp, pid, thread, logger]
---

## 1. 로그 한 줄은 어떻게 읽어야 할까?

Spring Boot 로그를 보다 보면 한 줄 안에 정보가 많이 들어 있어서 처음에는 복잡해 보일 수 있다.

예를 들어 기본 콘솔 로그는 아래처럼 보일 수 있다.

```text
2026-06-29T10:15:00.123+09:00  INFO 12345 --- [nio-8080-exec-4] com.example.order.OrderService : order created
```

Spring Boot 공식 문서는 기본 로그 출력에 아래 항목들이 포함된다고 설명한다. [1]

1. Date and Time
2. Log Level
3. Process ID
4. `---` separator
5. Thread name
6. Logger name
7. Log message

즉, 기본 패턴 기준으로는 "7개 정도의 핵심 조각"으로 읽는 것이 가장 정확하다.

다만 실제 프로젝트에서는 로그 패턴을 커스터마이징할 수 있으므로, 애플리케이션 이름이나 추가 MDC 값이 더 들어갈 수도 있다. [2]

---

## 2. 시간(Timestamp)

예시:

```text
2026-06-29T10:15:00.123+09:00
```

이 값은 로그가 발생한 시각이다.

로그에서 가장 중요한 정보 중 하나다.
장애가 발생했을 때는 "언제 일어났는가"를 기준으로 다른 로그, 외부 API 호출, DB 기록, 모니터링 이벤트와 대조해야 하기 때문이다.

끝의 `+09:00`은 시간대(Time Zone)를 뜻한다.

즉:

```text
+09:00 = UTC보다 9시간 빠른 시간대 = 한국 표준시(KST)
```

Spring Boot 공통 설정 문서는 로그 날짜 포맷 기본값으로 offset이 포함된 ISO 형식을 보여준다. [3]

---

## 3. 로그 레벨(Log Level)

예시:

```text
INFO
```

로그 레벨은 이 로그가 얼마나 중요한지, 얼마나 심각한지 빠르게 파악하게 해준다.

예를 들어

1. `INFO`는 정상적인 주요 흐름
2. `WARN`은 잠재적 문제
3. `ERROR`는 실제 실패

처럼 해석할 수 있다.

즉, 로그를 읽을 때는 메시지 본문보다 먼저 레벨부터 보는 습관이 중요하다.

---

## 4. 프로세스 아이디(PID)

예시:

```text
12345
```

PID는 현재 이 로그를 남긴 프로세스의 식별 번호이다.

같은 서버에 여러 Java 프로세스가 떠 있을 수 있기 때문에, PID를 보면 어떤 프로세스가 이 로그를 남겼는지 구분할 수 있다.

Spring Boot 공식 문서도 기본 로그 출력 항목에 Process ID가 포함된다고 설명한다. [1]

즉, 아래 상황에서 유용하다.

1. 같은 서버에 여러 개의 Spring Boot 앱이 동시에 떠 있는 경우
2. 재시작 직후 PID가 바뀌었는지 확인할 때
3. 특정 PID의 프로세스 로그만 연결해서 볼 때

---

## 5. 구분선(Separator)

예시:

```text
---
```

이 값은 시각적인 구분선이다.

Spring Boot 공식 문서도 기본 로그 포맷에 `---` separator가 들어간다고 설명한다. [1]

이 구분선 앞쪽은 보통 메타데이터이고, 뒤쪽은 애플리케이션 내부 정보라고 보면 된다.

즉, 아래처럼 나눠 읽으면 편하다.

```text
[앞쪽] 시간 / 레벨 / PID
[가운데] ---
[뒤쪽] 스레드 / logger / 메시지
```

---

## 6. 스레드 이름(Thread Name)

예시:

```text
[nio-8080-exec-4]
```

대괄호 안의 값은 스레드 이름이다.

Spring Boot 공식 문서도 기본 로그 출력 항목에 thread name이 포함되며, 대괄호 안에 표시된다고 설명한다. [1]

서버는 동시에 여러 요청을 처리해야 하므로 여러 스레드가 함께 동작한다.

예를 들어

```text
nio-8080-exec-4
```

는 보통 Tomcat 요청 처리 스레드 이름이다.

즉, 8080 포트로 들어온 요청을 처리하던 4번 실행 스레드 정도로 이해할 수 있다.

이 값은 아래 상황에서 중요하다.

1. 같은 시각에 여러 요청이 섞여 들어올 때
2. 특정 요청 흐름만 따라가고 싶을 때
3. 동일 스레드 안에서 발생한 예외를 추적할 때

다만 실제 운영에서는 비동기 처리, 스레드 풀 재사용, 분산 추적 등을 함께 봐야 하므로 "문제가 난 요청은 해당 스레드만 보면 된다"라고 단정하면 과할 수 있다.
입문 단계에서는 요청 처리 단서를 주는 값이라고 이해하면 충분하다.

---

## 7. 클래스명 또는 로거 이름(Logger Name)

예시:

```text
com.example.order.OrderService
```

Spring Boot 공식 문서는 이 값을 logger name이라고 설명하며, 보통 source class name이라고 덧붙인다. [1]

즉, 입문자 입장에서는 "로그를 남긴 위치를 가리키는 클래스명 비슷한 값"으로 이해하면 된다.

실제로는 항상 정확한 클래스명이 아니라

1. 패키지명을 포함한 logger 이름
2. 줄여서 표시된 logger 이름
3. 직접 지정한 logger 이름

일 수 있다.

그래도 보통은 "어느 코드 위치에서 로그를 남겼는지"를 찾는 데 가장 직접적인 단서가 된다.

---

## 8. 로그 메시지(Log Message)

예시:

```text
order created
```

콜론 `:` 뒤쪽이 실제 로그 메시지 본문이다.

즉, 앞부분이 "누가, 언제, 어떤 수준으로 남겼는지"라면, 뒤쪽 메시지는 "무슨 일이 있었는지"를 설명한다.

로그를 읽을 때는 보통 아래 순서가 효율적이다.

1. 시간 확인
2. 레벨 확인
3. logger/class 확인
4. 메시지 본문 확인

이 순서로 보면 로그 해석 속도가 빨라진다.

---

## 9. 애플리케이션 이름은 항상 들어갈까?

이 부분은 주의가 필요하다.

애플리케이션 이름은 Spring Boot 기본 콘솔 로그의 필수 기본 조각은 아니다.

Spring Boot 공식 문서가 설명하는 기본 로그 출력 항목에는 app name이 따로 고정 필드로 포함되어 있지 않다. [1]
대신 MDC를 추가하거나, 로그 패턴을 바꾸거나, structured logging을 쓰면 애플리케이션 이름 같은 값이 들어갈 수 있다. [2]

예를 들어 structured logging을 사용할 때는 `spring.application.name`이 JSON의 service name으로 반영될 수 있다. [2]

즉, 애플리케이션 이름은 아래처럼 이해하는 편이 정확하다.

```text
기본 콘솔 패턴에 항상 있는 필드는 아님
프로젝트 설정이나 로그 수집 방식에 따라 추가될 수 있음
```

MSA 환경에서 여러 서비스 로그가 한 곳에 모이는 경우에는 애플리케이션 이름, 서비스 이름, trace id 같은 값이 함께 있으면 출처를 구분하는 데 매우 유용하다.

---

## 정리

Spring Boot 기본 로그 한 줄은 보통 아래 항목들로 읽으면 된다.

1. 시간(Timestamp)
2. 로그 레벨(Log Level)
3. 프로세스 아이디(PID)
4. 구분선(`---`)
5. 스레드 이름(Thread Name)
6. 로거 이름 또는 클래스명(Logger Name)
7. 로그 메시지(Log Message)

그리고 애플리케이션 이름은 기본 콘솔 로그에 항상 고정으로 들어가는 값이 아니라, 설정에 따라 추가될 수 있는 정보로 보는 것이 정확하다.

즉, 로그를 읽을 때는 먼저 시간, 레벨, 스레드, logger를 보고, 마지막에 메시지 본문을 해석하는 습관을 들이면 된다.

---

## 출처

1. Spring Boot 2 Logging Reference, "Log format", https://docs.spring.io/spring-boot/docs/2.0.0.M5/reference/html/boot-features-logging.html
2. Spring Boot Reference, "Logging", https://docs.spring.io/spring-boot/reference/features/logging.html
3. Spring Boot Common Application Properties, "logging.pattern.dateformat", https://docs.spring.io/spring-boot/appendix/application-properties/index.html
