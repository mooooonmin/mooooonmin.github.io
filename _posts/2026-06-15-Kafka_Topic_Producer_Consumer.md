---
title: Kafka Topic Producer Consumer
category: k
date: 2026-06-15 00:00:20 +0900
tags: [kafka, topic, producer, consumer, message-queue]
---

## 1. Kafka의 기본 구성

Kafka의 기본 구성을 간단하게 표현하면 아래와 같다.

```text
Producer -> Kafka Topic -> Consumer
```

각 구성 요소의 의미는 아래처럼 정리할 수 있다.

| 구성 요소 | 의미 |
|---|---|
| Producer | Kafka에 메시지 또는 데이터를 전달하는 주체 |
| Consumer | Kafka에 저장된 메시지 또는 데이터를 읽어서 처리하는 주체 |
| Topic | Kafka에 넣을 메시지의 종류를 구분하는 개념 |

Apache Kafka 공식 문서는 Producer를 Kafka에 이벤트를 쓰는 클라이언트 애플리케이션, Consumer를 이벤트를 읽고 처리하는 클라이언트 애플리케이션으로 설명한다. [1]
또한 이벤트는 Topic에 정리되어 저장된다고 설명한다. [1]

입문 단계에서는 Topic을 카테고리처럼 이해하면 된다.

```text
이메일 발송 요청 Topic
주문 처리 요청 Topic
로그 저장 Topic
```

이렇게 Topic을 나누면 메시지의 종류별로 데이터를 구분해서 저장하고 처리할 수 있다.

---

## 2. Producer란?

Producer는 Kafka에 메시지를 전달하는 주체이다.

예를 들어 회원가입이 완료된 뒤 이메일을 보내야 한다고 해보자.
회원가입 서버는 아래와 같은 메시지를 만들 수 있다.

```text
USER1에게 가입 환영 이메일을 보내라.
```

그리고 이 메시지를 Kafka에 전달한다.
이때 메시지를 만들어 Kafka로 보내는 서버가 Producer이다.

흐름은 아래와 같다.

```text
회원가입 서버 -> Kafka
```

Kafka 공식 문서는 Producer API가 하나 이상의 Kafka Topic에 이벤트 스트림을 쓰는 역할을 한다고 설명한다. [2]
즉, Producer는 그냥 Kafka에 아무 곳으로 데이터를 던지는 것이 아니라 특정 Topic을 정해서 메시지를 보낸다.

```text
회원가입 서버 -> email-send Topic
```

---

## 3. Topic이란?

Topic은 Kafka에 저장할 메시지의 종류를 구분하는 개념이다.

예를 들어 서비스에서 여러 종류의 비동기 작업이 필요하다고 해보자.

```text
이메일 발송
문자 발송
주문 처리
로그 저장
```

이 작업들을 하나의 공간에 전부 섞어두면 어떤 메시지가 어떤 작업에 필요한지 구분하기 어렵다.
그래서 Kafka는 Topic이라는 단위로 메시지를 구분한다.

예를 들어 아래처럼 Topic을 만들 수 있다.

```text
email-send
sms-send
order-process
log-save
```

그러면 이메일 발송 메시지는 `email-send` Topic에 넣고, 주문 처리 메시지는 `order-process` Topic에 넣을 수 있다.

Kafka 공식 문서는 Topic을 파일 시스템의 폴더와 비슷하게 설명한다. [1]
입문자 관점에서는 Topic을 메시지의 카테고리라고 이해하면 된다.

---

## 4. Consumer란?

Consumer는 Kafka에 저장된 메시지를 읽어서 처리하는 주체이다.

예를 들어 `email-send` Topic에 아래 메시지가 들어있다고 해보자.

```text
USER1에게 가입 환영 이메일을 보내라.
```

이 메시지를 읽어서 실제 이메일 발송 로직을 실행하는 서버가 Consumer이다.

흐름은 아래와 같다.

```text
email-send Topic -> 이메일 발송 서버
```

Kafka 공식 문서는 Consumer API가 하나 이상의 Topic을 구독하고, 그 Topic에 생성된 이벤트 스트림을 읽고 처리하는 역할을 한다고 설명한다. [2]

즉, Consumer는 Kafka에 저장된 메시지를 가져와 실제 작업을 처리한다.

---

## 5. 전체 흐름

Producer, Topic, Consumer를 합치면 전체 흐름은 아래와 같다.

```text
Producer -> Topic -> Consumer
```

조금 더 구체적인 예시로 보면 아래와 같다.

```text
회원가입 서버 -> email-send Topic -> 이메일 발송 서버
```

과정을 하나씩 보면 아래와 같다.

1. 사용자가 회원가입을 완료한다.
2. 회원가입 서버가 이메일 발송 메시지를 만든다.
3. 회원가입 서버는 메시지를 `email-send` Topic에 넣는다.
4. 이메일 발송 서버는 `email-send` Topic을 읽는다.
5. 이메일 발송 서버는 메시지 내용을 보고 실제 이메일을 발송한다.

여기서 회원가입 서버는 Producer이고, `email-send`는 Topic이고, 이메일 발송 서버는 Consumer이다.

---

## 6. Kafka는 Topic별로 메시지를 저장한다

Producer가 Kafka로 메시지를 보내면 Kafka는 메시지를 Topic별로 구분해서 저장한다.

```text
email-send Topic
- USER1에게 가입 환영 이메일 보내기
- USER2에게 비밀번호 재설정 이메일 보내기

order-process Topic
- 주문 1번 결제 확인하기
- 주문 2번 배송 준비하기
```

Consumer는 자신이 처리해야 하는 Topic의 메시지를 읽어서 작업한다.

예를 들어 이메일 발송 서버는 `email-send` Topic을 읽고, 주문 처리 서버는 `order-process` Topic을 읽는다.

```text
email-send Topic -> 이메일 발송 서버
order-process Topic -> 주문 처리 서버
```

이렇게 Topic을 기준으로 메시지를 나누면 각 서버가 자신이 처리해야 할 메시지만 읽을 수 있다.

---

## 7. Producer와 Consumer는 서로 직접 연결되지 않는다

Kafka를 사용할 때 중요한 특징은 Producer와 Consumer가 서로 직접 연결되지 않는다는 점이다.

```text
Producer -> Kafka -> Consumer
```

Producer는 Consumer가 누구인지 몰라도 Kafka에 메시지를 넣을 수 있다.
Consumer도 Producer가 누구인지 몰라도 Kafka에서 메시지를 읽어 처리할 수 있다.

Apache Kafka 공식 문서는 Producer와 Consumer가 서로 완전히 분리되어 있고, 이 점이 Kafka의 확장성에 중요한 설계 요소라고 설명한다. [1]

이 구조 덕분에 Producer 서버와 Consumer 서버를 따로 늘리거나 줄일 수 있다.
또한 Consumer 처리 속도가 잠시 느려져도 Producer는 Kafka에 메시지를 계속 넣을 수 있다.

---

## 정리

Kafka의 기본 구성은 Producer, Topic, Consumer이다.

Producer는 Kafka에 메시지를 넣는 주체이다.
Topic은 메시지의 종류를 구분하는 카테고리이다.
Consumer는 Kafka의 메시지를 읽어서 실제 작업을 처리하는 주체이다.

전체 흐름은 아래처럼 기억하면 된다.

```text
Producer -> Topic -> Consumer
```

글로만 보면 Kafka에 대한 감을 잡기 어려울 수 있다.
다음 단계에서는 지금까지 배운 Producer, Topic, Consumer 개념을 가지고 직접 Kafka 실습을 진행하면 된다.

---

## 출처

1. Apache Kafka, "Introduction - Main Concepts and Terminology", https://kafka.apache.org/intro/
2. Apache Kafka, "Introduction - Kafka APIs", https://kafka.apache.org/intro/
