---
title: Log File Output
category: l
date: 2026-06-29 00:00:10 +0900
tags: [logging, logback, spring-boot, file-output, console]
---

## 1. 로그를 파일로 왜 남겨야 할까?

애플리케이션 로그는 콘솔로만 보고 끝낼 수도 있고, 파일로 저장해서 나중에 다시 볼 수도 있다.

운영 환경에서는 보통 "지금 화면에 보이는 로그"보다 "나중에 다시 확인할 수 있는 로그"가 더 중요하다.

예를 들어 아래 상황을 생각해볼 수 있다.

1. 새벽에 장애가 발생했다.
2. 아침에 출근해서 원인을 확인해야 한다.
3. 그때는 이미 서버가 재시작돼 있다.

이때 로그가 파일로 남아 있지 않으면 원인 추적이 매우 어려워진다.

Spring Boot 공식 문서는 기본적으로 로그를 콘솔에 출력하며, 필요하면 파일 출력도 사용할 수 있다고 설명한다. [1]

즉, 입문 단계에서는 아래처럼 이해하면 된다.

```text
콘솔 로그 = 지금 바로 보기 좋음
파일 로그 = 나중에 다시 보기 좋음
```

---

## 2. 콘솔 로그

콘솔 로그는 애플리케이션이 실행 중인 터미널이나 IDE 화면에 바로 출력되는 로그다.

장점은 명확하다.

1. 실시간으로 바로 볼 수 있다.
2. 개발 중 디버깅이 쉽다.
3. 서버 실행 직후 흐름을 확인하기 좋다.

예를 들어 Spring Boot를 IDE에서 실행하면 `INFO`, `WARN`, `ERROR` 로그가 콘솔에 바로 찍힌다.

하지만 콘솔 로그만으로는 한계가 있다.

1. IDE를 닫으면 지난 로그를 계속 보기 어렵다.
2. 서버가 재시작되면 예전 출력이 남지 않을 수 있다.
3. 터미널 버퍼를 넘어간 로그는 놓칠 수 있다.

정확히 말하면 "콘솔에 찍힌 로그가 물리적으로 사라진다"기보다, 별도 수집이나 파일 저장이 없으면 지속적으로 보관되지 않는다는 뜻이다.

즉, 콘솔 로그는 실시간 확인에는 좋지만, 과거 이력을 장기 보관하는 수단으로는 부족하다.

---

## 3. 로그 파일로 저장

지난 로그를 활용하려면 로그를 파일로 저장해야 한다.

보통 아래처럼 `.log` 파일 형태로 서버나 로컬 컴퓨터 디스크에 보관한다.

```text
app.log
spring.log
error.log
```

파일 로그의 장점은 아래와 같다.

| 장점 | 설명 |
|---|---|
| 과거 추적 가능 | 장애가 난 뒤에도 이전 로그를 다시 볼 수 있다 |
| 검색 용이 | `grep`, `rg`, `less` 등으로 필요한 로그를 찾기 쉽다 |
| 백업/수집 가능 | 로그 수집 시스템으로 전달하기 쉽다 |
| 감사 기록 | 특정 시점의 이벤트 이력을 남길 수 있다 |

Spring Boot 공식 문서는 로그 출력 파일이 `logging.file.name` 또는 `logging.file.path` 속성으로 지정된다고 설명한다. [2]

즉, 파일 로그는 "지난 기록을 다시 볼 수 있게 만드는 저장 방식"이라고 이해하면 된다.

---

## 4. Spring Boot에서 파일 로그 켜기

Spring Boot에서는 아래처럼 설정할 수 있다.

### 4-1. 특정 파일명 지정

```yaml
logging:
  file:
    name: logs/app.log
```

이렇게 하면 `logs/app.log` 파일로 로그를 남길 수 있다.

### 4-2. 디렉터리만 지정

```yaml
logging:
  file:
    path: logs
```

이 경우 Spring Boot는 해당 경로에 기본 로그 파일을 생성한다.

Spring Boot API 문서는 `logging.file.name`이 없고 `logging.file.path`만 있으면 그 디렉터리에 `spring.log`가 기록된다고 설명한다. [2]

즉:

```text
name = 파일명까지 직접 지정
path = 디렉터리만 지정, 기본 파일명은 spring.log
```

---

## 5. 콘솔 로그와 파일 로그는 같이 쓸 수 있을까?

가능하다.

Spring Boot 공식 문서도 콘솔 출력과 optional file output이 함께 가능하다고 설명한다. [1]

즉, 아래 방식이 가장 흔하다.

1. 콘솔에는 실시간으로 출력
2. 파일에는 같은 로그를 계속 저장

이렇게 하면 개발 중에는 화면으로 바로 보고, 장애 분석 때는 파일을 다시 열어서 확인할 수 있다.

실무에서는 여기에 더해

1. 로그 수집기(Filebeat, Fluent Bit 등)
2. 중앙 로그 저장소(ELK, Loki, Datadog 등)

까지 붙이는 경우가 많다.

---

## 6. 로깅 프레임워크 - Logback

Spring Boot를 기본 설정으로 쓰면 보통 Logback이 로깅 구현체로 사용된다.

Spring Boot 공식 문서는 starter를 사용할 때 기본적으로 Logback이 사용된다고 설명한다. [1]

Logback 공식 문서는 Logback이 인기 있던 log4j 1.x 프로젝트의 successor로 의도되었고, log4j의 설계자인 Ceki Gülcü가 만들었다고 설명한다. [3]

즉, Logback은 아래처럼 이해하면 된다.

```text
Spring Boot에서 기본으로 많이 쓰는 자바 로깅 구현체
log4j 1.x의 후속 방향으로 설계된 프레임워크
```

여기서 주의할 점은 "모든 자바 프로젝트에서 무조건 가장 많이 쓰인다"처럼 단정하는 표현은 피하는 것이 맞다.
자바 생태계에는 Logback, Log4j2, JUL 등 여러 선택지가 있기 때문이다.

---

## 7. Logback은 무슨 역할을 할까?

Logback은 로그를 어디에, 어떤 형식으로, 어떤 기준으로 남길지 제어한다.

예를 들어 아래 같은 일을 담당한다.

1. 콘솔에 출력할지
2. 파일에 저장할지
3. 어떤 패턴으로 보여줄지
4. 어떤 레벨 이상만 남길지
5. 파일을 언제 롤링할지

Logback 공식 문서는 logback-core, logback-classic, logback-access 구조를 설명하며, logback-classic이 SLF4J API를 구현한다고 설명한다. [4]

입문 단계에서는 복잡한 내부 구조까지 외울 필요는 없다.
아래 정도로 이해하면 충분하다.

```text
SLF4J = 로그를 남기는 표준 인터페이스 쪽
Logback = 그 로그를 실제로 출력하고 저장하는 구현체 쪽
```

---

## 8. 파일 로그가 있으면 무조건 안전할까?

그렇지는 않다.

파일 로그도 아래 문제가 있을 수 있다.

1. 디스크 용량이 꽉 찰 수 있다.
2. 로그 파일이 너무 커질 수 있다.
3. 서버 장애로 디스크 자체를 잃을 수 있다.
4. 여러 서버 로그를 한 번에 보기 어렵다.

그래서 운영 환경에서는 보통 아래를 함께 고려한다.

1. 로그 롤링
2. 보관 주기
3. 압축
4. 중앙 로그 수집

즉, 파일 로그는 기본 저장 수단으로 매우 중요하지만, 운영 완성형은 아니다.

---

## 정리

로그는 콘솔로만 볼 수도 있지만, 장애 분석과 운영 이력 확인을 위해서는 파일로 저장하는 것이 중요하다.

핵심만 정리하면 아래와 같다.

1. 콘솔 로그는 실시간 확인에 좋다.
2. 파일 로그는 지난 이력을 다시 확인하는 데 좋다.
3. Spring Boot에서는 `logging.file.name` 또는 `logging.file.path`로 파일 로그를 켤 수 있다.
4. Spring Boot 기본 로깅 구현체는 보통 Logback이다.
5. Logback은 log4j 1.x의 후속 방향으로 Ceki Gülcü가 설계한 로깅 프레임워크다.

즉, 개발 중에는 콘솔 로그를 보고, 운영 관점에서는 파일 로그까지 남겨두는 습관이 필요하다.

---

## 출처

1. Spring Boot Reference, "Logging", https://docs.spring.io/spring-boot/reference/features/logging.html
2. Spring Boot API, "LogFile", https://docs.spring.io/spring-boot/api/java/org/springframework/boot/logging/LogFile.html
3. Logback Manual, "Introduction", https://logback.qos.ch/manual/introduction.html
4. Logback Manual, "Architecture", https://logback.qos.ch/manual/architecture.html
