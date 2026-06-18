---
title: Kafka Consumer Sequential Processing
category: k
date: 2026-06-18 00:00:10 +0900
tags: [kafka, consumer, partition, spring-kafka, concurrency]
---

## 1. Consumer가 메시지를 하나씩만 처리하는 현상

이전 글에서는 Consumer 코드에 아래 코드를 넣어 이메일 발송에 3초가 걸리는 상황을 만들었다.

```java
Thread.sleep(3000);
```

그리고 Kafka를 사용하면 API 서버는 Kafka에 메시지를 넣고 빠르게 응답할 수 있고, Consumer는 뒤에서 이메일 발송 작업을 처리한다고 설명했다.

이번에는 API 요청을 한 번만 보내지 않고 여러 번 연속으로 보내보자.

```text
API 요청 1
API 요청 2
API 요청 3
```

예상으로는 Consumer가 세 메시지를 동시에 처리해서 약 3초 뒤에 모두 끝날 것처럼 느껴질 수 있다.
하지만 현재 실습 설정에서는 Consumer가 메시지를 하나씩 처리하는 모습을 볼 수 있다.

---

## 2. API 요청 여러 번 보내보기

먼저 이전 실습에서 만든 Producer 서버와 Consumer 서버를 실행한다.

그리고 이메일 발송 API 요청을 세 번 연속으로 보낸다.

이때 Consumer가 요청을 정상적으로 처리할 수 있도록 실패를 유도하는 이메일 주소는 사용하지 않는다.
예를 들어 `fail@naver.com`처럼 실패 테스트용으로 쓰던 주소가 있다면 다른 이메일 주소로 바꿔 요청을 보낸다.

흐름은 아래와 같다.

```text
사용자 -> API 서버 -> Kafka email.send Topic
사용자 -> API 서버 -> Kafka email.send Topic
사용자 -> API 서버 -> Kafka email.send Topic
```

API 서버는 요청을 받을 때마다 Kafka에 메시지를 넣는다.
그러면 `email.send` Topic에는 이메일 발송 메시지가 3개 쌓인다.

---

## 3. Consumer 서버 로그 확인하기

Consumer 서버 로그를 확인해보면 메시지가 한 번에 모두 처리되지 않고 순서대로 처리되는 것을 볼 수 있다.

예를 들어 로그는 아래와 비슷하게 찍힐 수 있다.

```text
Kafka로부터 받아온 메시지: ...
이메일 발송 완료

Kafka로부터 받아온 메시지: ...
이메일 발송 완료

Kafka로부터 받아온 메시지: ...
이메일 발송 완료
```

Consumer 코드에는 `Thread.sleep(3000)`이 들어있다.
따라서 메시지 하나를 처리할 때마다 약 3초가 걸린다.

현재 실습 설정에서 메시지 3개를 하나씩 처리하면 전체 시간은 대략 아래처럼 계산된다.

```text
3초 + 3초 + 3초 = 9초
```

즉, 총 3개의 이메일 발송 메시지를 처리하는 데 약 9초가 걸릴 수 있다.

---

## 4. 왜 한 번에 하나씩 처리될까?

API 요청을 여러 번 보냈는데 Consumer가 하나씩 처리하는 이유는 Kafka Consumer의 병렬 처리 방식과 관련이 있다.

Spring Kafka 공식 문서는 `KafkaMessageListenerContainer`가 모든 메시지를 하나의 스레드에서 받는다고 설명한다. [1]
또한 `ConcurrentMessageListenerContainer`는 여러 `KafkaMessageListenerContainer`에 위임해 멀티 스레드 consumption을 제공한다고 설명한다. [1]

즉, Spring Kafka Consumer가 항상 자동으로 여러 메시지를 병렬 처리하는 것은 아니다.
listener container 설정과 Kafka Topic의 Partition 구조에 따라 실제 처리 병렬성이 달라진다.

현재 실습에서는 Consumer가 한 번에 하나씩 메시지를 처리하는 것처럼 보인다.
이 현상은 다음 개념과 연결된다.

```text
Partition
Consumer Group
Consumer concurrency
```

---

## 5. Spring Boot 요청 처리와 Kafka Consumer 처리는 다르다

여기서 헷갈리기 쉬운 점이 있다.

Spring Boot 서버는 일반적인 HTTP 요청을 여러 개 받을 수 있다.
그래서 API 요청 3개를 빠르게 연속으로 보내면 API 서버는 각 요청을 받아 Kafka에 메시지를 넣을 수 있다.

하지만 Kafka Consumer가 Topic에서 메시지를 읽어 처리하는 방식은 별도의 설정과 Kafka 구조를 따른다.

```text
HTTP 요청 처리 병렬성 != Kafka Consumer 처리 병렬성
```

HTTP 요청을 여러 개 받을 수 있다고 해서 Kafka Consumer도 자동으로 여러 메시지를 동시에 처리하는 것은 아니다.

Kafka Consumer의 처리 병렬성을 이해하려면 Partition 개념을 알아야 한다.

---

## 6. Partition과 관련된 이유

Kafka Topic은 Partition으로 나뉠 수 있다.

Apache Kafka 공식 Introduction 문서는 Topic이 여러 Partition으로 나뉘고, 같은 event key를 가진 이벤트는 같은 Partition에 쓰인다고 설명한다. [2]

Consumer Group 관점에서는 Partition이 병렬 처리의 중요한 기준이 된다.
Confluent의 Kafka Consumer 설계 문서는 Consumer Group 안에서 각 Partition은 어느 한 시점에 정확히 하나의 Consumer가 소비한다고 설명한다. [3]

이 말은 병렬 처리 수준이 Partition 구조와 Consumer Group 구성에 영향을 받는다는 뜻이다.

입문 단계에서는 아래처럼 이해하면 된다.

```text
Partition이 1개이고 Consumer 처리 스레드도 1개라면
메시지가 하나씩 처리되는 것처럼 보일 수 있다.
```

정확한 내용은 다음 글에서 Partition을 배우면서 이어서 정리한다.

---

## 7. 이번 글에서 확인한 현상

이번 글에서 확인한 것은 아래이다.

1. API 요청을 3번 연속으로 보낸다.
2. API 서버는 Kafka에 메시지를 3개 넣는다.
3. Consumer는 메시지를 하나씩 처리한다.
4. 메시지 하나당 3초가 걸리면 총 9초 정도 걸릴 수 있다.

이 현상은 Kafka Consumer가 무조건 느리다는 뜻이 아니다.
현재 실습 설정에서 Consumer 처리 병렬성이 1로 보이는 상황이라고 이해해야 한다.

Kafka Consumer 처리 성능을 높이려면 Partition과 Consumer concurrency를 함께 이해해야 한다.

---

## 정리

Consumer 코드에 `Thread.sleep(3000)`이 들어있는 상태에서 API 요청을 3번 연속으로 보내면, 현재 실습 설정에서는 Consumer가 메시지를 하나씩 처리하는 모습을 볼 수 있다.

메시지 하나당 3초가 걸리고 3개를 순서대로 처리하면 총 9초 정도 걸릴 수 있다.

이 현상은 Kafka의 Partition, Consumer Group, Spring Kafka listener concurrency와 관련이 있다.
다음 글에서는 Kafka의 중요한 개념인 Partition이 무엇인지 알아본다.

---

## 출처

1. Spring for Apache Kafka, "Message Listener Containers", https://docs.spring.io/spring-kafka/reference/kafka/receiving-messages/message-listener-container.html
2. Apache Kafka, "Introduction - Main Concepts and Terminology", https://kafka.apache.org/intro/
3. Confluent Documentation, "Kafka Consumer Design: Consumers, Consumer Groups, and Offsets", https://docs.confluent.io/kafka/design/consumer-design.html
