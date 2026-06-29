---
title: Logback Appenders
category: l
date: 2026-06-30 00:00:00 +0900
tags: [logback, appender, consoleappender, fileappender, rollingfileappender]
---

## 1. Appender란 무엇일까?

Logback에서 Appender는 로그를 어디로 보낼지를 결정하는 출력 목적지라고 보면 된다.

Logback 공식 소개 문서는 Appender를 output destination으로 볼 수 있다고 설명한다. 콘솔, 파일 등 다양한 목적지용 appender가 존재한다. [1]

즉, 아래처럼 이해하면 된다.

```text
Logger가 로그를 만든다
Appender가 그 로그를 어디로 보낼지 결정한다
```

예를 들어 같은 로그라도

1. 콘솔 화면에 출력할 수도 있고
2. 파일에 저장할 수도 있고
3. 롤링 파일에 쌓을 수도 있다

이 차이를 만드는 것이 Appender이다.

---

## 2. Appender는 왜 필요할까?

로그는 남기는 것만으로 끝나지 않는다.
어디에 기록할지도 중요하다.

예를 들어 개발 중에는 콘솔이 편하지만, 운영 중 장애 분석에는 파일 저장이 더 중요할 수 있다.

즉, Appender는 로그의 "배송 목적지"를 정하는 역할이라고 보면 된다.

Logback 구조상 appender는 encoder와 함께 동작해, 로그 이벤트를 실제 출력 대상으로 내보낸다. [2]

---

## 3. ConsoleAppender

`ConsoleAppender`는 로그를 콘솔에 출력하는 appender이다.

Logback 공식 매뉴얼은 `ConsoleAppender`가 `System.out` 또는 `System.err`에 로그를 출력한다고 설명한다. 기본 대상은 `System.out`이다. [3]

즉, 우리가 개발할 때 IDE 화면이나 터미널 창에서 바로 보는 로그가 여기에 해당한다.

장점은 아래와 같다.

1. 실시간 확인이 쉽다.
2. 개발 중 디버깅이 편하다.
3. 서버 시작 직후 흐름을 보기 좋다.

하지만 단점도 있다.

1. 장기 보관에 약하다.
2. 과거 로그를 다시 찾기 어렵다.
3. 운영 환경에서는 콘솔 출력 비용이 부담될 수 있다.

Logback 공식 매뉴얼도 콘솔은 비교적 느리며, 특히 high volume production 시스템에서는 콘솔 로깅을 피하라고 경고한다. [3]

즉, `ConsoleAppender`는 개발 중에는 매우 유용하지만, 운영 환경의 주 저장 수단으로만 보기에는 한계가 있다.

---

## 4. FileAppender

`FileAppender`는 로그를 파일에 기록하는 appender이다.

Logback API 문서는 `FileAppender`가 로그 이벤트를 파일에 append한다고 설명한다. [4]

즉, 아래 같은 파일에 로그를 차곡차곡 쌓아둘 수 있다.

```text
app.log
spring.log
error.log
```

장점은 아래와 같다.

1. 과거 로그를 다시 볼 수 있다.
2. 검색하기 쉽다.
3. 서버 장애 분석에 유리하다.

다만 `FileAppender`만 계속 사용하면 파일 하나가 끝없이 커질 수 있다.

예를 들어 아래 문제가 생길 수 있다.

1. 로그 파일이 수 GB 이상 커짐
2. 열기 어려워짐
3. 디스크 용량 압박

그래서 운영 환경에서는 `FileAppender`보다 `RollingFileAppender`를 더 자주 사용한다.

---

## 5. RollingFileAppender

`RollingFileAppender`는 파일 로그를 남기면서, 일정 조건이 되면 기존 로그를 넘기고 새 파일로 바꿔주는 appender이다.

Logback API 문서는 `RollingFileAppender`가 `RollingPolicy`와 `TriggeringPolicy`에 따라 로그 파일을 백업하고 새 파일로 넘긴다고 설명한다. [5]

즉, 핵심은 아래 두 가지다.

1. 현재 로그를 쓰는 active file이 있다.
2. 특정 조건이 되면 rollover가 일어난다.

이때 조건은 고정이 아니다.

초안처럼 "매일 자정"으로만 이해하면 조금 좁다.
실제로는 rolling policy 설정에 따라

1. 매일
2. 매주
3. 매월
4. 파일 크기 기준
5. 시간 + 크기 기준

등으로 바뀔 수 있다.

Logback의 `TimeBasedRollingPolicy`는 하루, 주, 월 단위 등 시간 기준 rollover가 가능하다고 설명한다. [6]
또한 `SizeAndTimeBasedRollingPolicy`는 시간과 파일 크기를 함께 기준으로 사용할 수 있다. [7]

즉, `RollingFileAppender`는 "로그 파일이 계속 커지는 문제를 제어하기 위한 운영용 appender"라고 이해하면 된다.

---

## 6. 왜 실무에서는 RollingFileAppender를 많이 쓸까?

운영 로그는 보통 오래 남겨야 하지만, 파일 하나에 무한정 쌓을 수는 없다.

예를 들어 `FileAppender`만 쓰면 아래 문제가 생길 수 있다.

1. 1년치 로그가 파일 하나에 몰림
2. 파일 검색 속도 저하
3. 디스크 사용량 급증
4. 관리 난이도 증가

반면 `RollingFileAppender`를 쓰면

1. 파일을 날짜별로 나눌 수 있고
2. 일정 크기마다 끊을 수 있고
3. 오래된 파일을 자동 삭제할 수도 있다

Logback 관련 문서는 `maxHistory` 설정을 통해 오래된 archive 파일을 자동으로 제거할 수 있다고 설명한다. [8]

즉, 운영 환경에서는 아래 흐름이 자연스럽다.

```text
콘솔 = 실시간 확인
롤링 파일 = 운영 보관
```

그래서 실무에서는 단순 `FileAppender`보다 `RollingFileAppender`를 선호하는 경우가 많다.

다만 "대부분 반드시 이것만 쓴다"처럼 단정할 수는 없다.
요즘은 중앙 로그 수집 시스템에 바로 보내는 구조도 많기 때문이다.

즉, 더 정확한 표현은 아래이다.

```text
파일 기반 운영 로그가 필요할 때는 RollingFileAppender가 매우 흔한 선택지다.
```

---

## 7. 간단히 비교하면

세 가지를 비교하면 아래와 같다.

| 종류 | 출력 위치 | 장점 | 단점 |
|---|---|---|---|
| `ConsoleAppender` | 콘솔 | 실시간 확인이 쉽다 | 장기 보관에 약하다 |
| `FileAppender` | 단일 로그 파일 | 파일 보관이 가능하다 | 파일이 계속 커질 수 있다 |
| `RollingFileAppender` | 롤링되는 로그 파일 | 보관과 용량 관리를 함께 할 수 있다 | 설정이 조금 더 복잡하다 |

입문 단계에서는 이 정도만 구분해도 충분하다.

---

## 8. 실무 관점에서 어떻게 고르면 될까?

아주 단순하게 정리하면 아래처럼 선택할 수 있다.

1. 개발 중:
   - `ConsoleAppender`
2. 간단한 파일 저장이 필요할 때:
   - `FileAppender`
3. 운영 환경에서 로그 보관과 용량 관리가 모두 필요할 때:
   - `RollingFileAppender`

물론 실제 운영에서는 아래 조합이 많다.

1. 콘솔 출력도 같이 켜둔다.
2. 파일은 롤링되게 저장한다.
3. 수집기가 파일을 읽어 중앙 로그 시스템으로 보낸다.

즉, appender는 하나만 쓰는 것이 아니라 여러 개를 함께 붙이는 것도 가능하다.

---

## 정리

Logback의 Appender는 로그를 어디로 출력할지를 결정하는 구성 요소이다.

핵심만 정리하면 아래와 같다.

1. `ConsoleAppender`는 콘솔에 로그를 보여준다.
2. `FileAppender`는 로그를 파일에 누적 저장한다.
3. `RollingFileAppender`는 조건에 따라 로그 파일을 나누고 교체한다.
4. `RollingFileAppender`의 rollover 기준은 매일 자정 고정이 아니라 rolling policy 설정에 따라 달라진다.
5. 운영 환경에서는 파일 용량 관리와 보관을 위해 rolling 방식이 자주 사용된다.

즉, Appender를 이해하면 "로그를 어떻게 남길지"를 설계할 수 있게 된다.

---

## 출처

1. Logback Short Introduction, https://logback.qos.ch/shortIntro.html
2. Logback Manual, "Encoders", https://logback.qos.ch/manual/encoders.html
3. Logback Manual, "Appenders - ConsoleAppender", https://logback.qos.ch/manual/appenders.html
4. Logback API, "FileAppender", https://logback.qos.ch/apidocs/ch.qos.logback.core/ch/qos/logback/core/FileAppender.html
5. Logback API, "RollingFileAppender", https://logback.qos.ch/apidocs/ch.qos.logback.core/ch/qos/logback/core/rolling/RollingFileAppender.html
6. Logback API, "TimeBasedRollingPolicy", https://logback.qos.ch/apidocs-1.3.x/ch/qos/logback/core/rolling/TimeBasedRollingPolicy.html
7. Logback API, "SizeAndTimeBasedRollingPolicy", https://logback.qos.ch/apidocs/ch.qos.logback.core/ch/qos/logback/core/rolling/SizeAndTimeBasedRollingPolicy.html
8. Logback, "Reasons to prefer logback over log4j 1.x", https://logback.qos.ch/reasonsToSwitch.html
