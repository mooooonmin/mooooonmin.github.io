---
title: Kafka Async Performance
category: k
date: 2026-06-18 00:00:00 +0900
tags: [kafka, async, spring-kafka, consumer, performance]
---

## 1. 이전 글 복습

이전 글에서 REST API 방식과 메시지 큐를 활용한 방식을 비교했다.

REST API 방식만 사용하면 요청을 받은 서버가 모든 작업을 끝낸 뒤에 응답을 보낼 수 있다.
예를 들어 이메일 발송 처리에 3초가 걸린다면 사용자는 응답을 받기까지 3초 가까이 기다릴 수 있다.

반면 Kafka 같은 메시지 큐를 활용하면 오래 걸리는 작업을 Consumer에게 맡기고 API 서버는 더 빨리 응답할 수 있다.

흐름은 아래와 같다.

```text
사용자 -> API 서버 -> Kafka -> Consumer 서버
```

API 서버는 Kafka에 메시지를 넣고 사용자에게 응답한다.
Consumer 서버는 Kafka에서 메시지를 읽어 실제 이메일 발송 작업을 처리한다.

이번 글에서는 Consumer 쪽 작업이 오래 걸리는 상황을 만들어 Kafka 비동기 처리의 장점을 확인해본다.

---

## 2. Consumer 서버 코드 수정하기

이메일 발송을 처리하는 데 시간이 오래 걸리는 상황을 가정해보자.

아래 코드는 Consumer가 Kafka 메시지를 읽은 뒤 3초 동안 대기하도록 만든 예시이다.

```java
@Service
public class EmailSendConsumer {

    @KafkaListener(
            topics = "email.send",
            groupId = "email-send-group"
    )
    public void consume(String message) {
        System.out.println("Kafka로부터 받아온 메시지: " + message);

        EmailSendMessage emailSendMessage = EmailSendMessage.fromJson(message);

        // 실제 이메일 발송 로직은 생략
        try {
            Thread.sleep(3000); // 이메일 발송에 3초가 걸린다고 가정
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("이메일 발송 실패", e);
        }

        System.out.println("이메일 발송 완료");
    }
}
```

Spring Kafka 공식 문서는 `@KafkaListener` 어노테이션을 listener container의 listener로 동작할 bean method를 지정하는 데 사용한다고 설명한다. [1]
즉, 위 코드의 `consume()` 메서드는 `email.send` Topic에 들어온 메시지를 받아 처리하는 Consumer 메서드로 볼 수 있다.

코드를 수정했다면 Consumer 서버를 재실행한다.

---

## 3. Thread.sleep을 넣은 이유

실제 이메일 발송은 외부 메일 서버와 통신할 수 있고, 네트워크 상황이나 외부 서비스 상태에 따라 시간이 걸릴 수 있다.

이 글에서는 그런 상황을 단순하게 재현하기 위해 `Thread.sleep(3000)`을 사용한다.

```java
Thread.sleep(3000);
```

이 코드는 현재 스레드를 약 3초 동안 멈춘다.
따라서 Consumer가 메시지를 받은 뒤 이메일 발송 작업에 3초가 걸리는 것처럼 동작한다.

이때 중요한 점은 API 서버의 응답 시간과 Consumer의 실제 처리 시간이 분리된다는 것이다.

---

## 4. 이메일 발송 API 요청 보내보기

이제 이메일 발송 API를 호출한다고 가정해보자.

동기 방식이라면 API 서버가 이메일 발송 작업까지 끝낸 뒤 응답할 수 있다.

```text
사용자 요청 -> 이메일 발송 처리 3초 대기 -> 사용자 응답
```

하지만 Kafka를 활용한 비동기 방식에서는 API 서버가 Kafka에 메시지를 넣고 바로 응답할 수 있다.

```text
사용자 요청 -> Kafka에 메시지 저장 -> 사용자 응답
                                  \
                                   Consumer가 나중에 이메일 발송 처리
```

실습 환경에서는 이메일 발송 작업이 3초 걸리도록 만들어도 API 응답은 훨씬 빨리 돌아오는 것을 확인할 수 있다.
다만 응답 시간이 항상 25ms라는 뜻은 아니다.
응답 시간은 개발 환경, 서버 성능, 네트워크 상태, Kafka 상태, API 코드 구현에 따라 달라진다.

이 실습에서 확인해야 할 핵심은 아래이다.

```text
API 서버는 Consumer의 3초 작업이 끝날 때까지 기다리지 않는다.
```

---

## 5. Consumer 로그 확인하기

API 요청을 보낸 뒤 Consumer 서버 로그를 확인한다.

Consumer가 메시지를 받으면 먼저 아래 로그가 출력된다.

```text
Kafka로부터 받아온 메시지: ...
```

그 뒤 `Thread.sleep(3000)` 때문에 약 3초 후 아래 로그가 출력된다.

```text
이메일 발송 완료
```

사용자 입장에서는 API 응답을 먼저 받는다.
Consumer는 그 뒤 Kafka 메시지를 읽고 실제 이메일 발송 작업을 처리한다.

이 구조가 Kafka를 활용한 비동기 처리의 핵심이다.

---

## 6. 비동기 처리의 성능 이점

비동기 처리를 사용하면 오래 걸리는 작업을 요청-응답 흐름에서 분리할 수 있다.

예를 들어 이메일 발송 작업이 3초 걸린다고 해보자.

동기 처리에서는 사용자가 3초 가까이 기다릴 수 있다.

```text
요청 -> 이메일 발송 3초 -> 응답
```

비동기 처리에서는 API 서버가 Kafka에 메시지를 넣은 뒤 응답하고, Consumer가 뒤에서 이메일을 처리한다.

```text
요청 -> Kafka에 메시지 저장 -> 응답
                         \
                          이메일 발송 3초
```

이 때문에 사용자 입장에서는 응답이 더 빠르게 느껴질 수 있다.

Apache Kafka 공식 Introduction 문서는 Producer와 Consumer가 서로 완전히 분리되어 있고, 이 점이 Kafka의 높은 확장성을 위한 핵심 설계 요소라고 설명한다. [2]
이런 분리 구조 덕분에 요청을 받는 서버와 실제 작업을 처리하는 Consumer를 나누어 운영할 수 있다.

---

## 7. 비동기 처리의 한계

Kafka를 활용한 비동기 처리는 빠르게 응답할 수 있다는 장점이 있다.
하지만 중요한 한계도 있다.

API 서버는 Kafka에 메시지를 넣은 뒤 사용자에게 먼저 응답한다.
그러면 Consumer가 실제 이메일 발송을 성공했는지 API 응답 시점에는 알 수 없다.

예를 들어 아래 상황이 가능하다.

```text
1. API 서버가 Kafka에 이메일 발송 메시지를 넣는다.
2. API 서버가 사용자에게 성공 응답을 보낸다.
3. Consumer가 메시지를 읽는다.
4. 잘못된 이메일 주소나 외부 메일 서버 오류 때문에 이메일 발송에 실패한다.
```

이때 이미 사용자에게는 응답을 보낸 상태이다.
따라서 동기 방식처럼 "이메일 발송 성공 여부"를 즉시 확인하고 응답하기 어렵다.

즉, 비동기 처리는 빠른 응답을 얻는 대신 실제 작업의 최종 성공 여부를 별도로 관리해야 한다.

---

## 8. 실패 처리를 보완하는 방법

비동기 처리에서는 Consumer가 실패했을 때를 대비해야 한다.

대표적인 보완 방법은 아래와 같다.

| 방법 | 의미 |
|---|---|
| Retry | 실패한 메시지를 다시 처리해보는 방식 |
| Dead Letter Topic | 여러 번 실패한 메시지를 별도 Topic에 보관하는 방식 |

Confluent 문서는 Kafka Dead Letter Queue를 downstream consumer가 처리하지 못한 메시지를 보내는 별도 Kafka Topic으로 설명한다. [3]
Spring Cloud Stream Kafka Binder 문서도 에러가 난 record를 DLQ Topic으로 보내려면 DLQ 기능을 활성화해야 한다고 설명한다. [4]

실제 서비스에서는 실패한 메시지를 무한히 반복 처리하지 않도록 재시도 횟수를 제한하고, 계속 실패하는 메시지는 Dead Letter Topic에 따로 보관하는 방식이 자주 사용된다.

---

## 정리

Kafka를 사용하면 오래 걸리는 작업을 Consumer에게 맡기고 API 서버는 빠르게 응답할 수 있다.
이메일 발송처럼 시간이 걸릴 수 있는 작업을 비동기로 분리하면 사용자 입장에서는 응답이 빨라진 것처럼 느낄 수 있다.

하지만 비동기 처리는 Consumer의 실제 처리 성공 여부를 API 응답 시점에 바로 알기 어렵다는 한계가 있다.
그래서 실제 서비스에서는 retry와 Dead Letter Topic 같은 실패 처리 전략을 함께 설계해야 한다.

다음 글에서는 실패한 메시지를 재시도하는 방법과 Dead Letter Topic을 활용하는 방법을 이어서 다룬다.

---

## 출처

1. Spring for Apache Kafka, "@KafkaListener Annotation", https://docs.spring.io/spring-kafka/reference/kafka/receiving-messages/listener-annotation.html
2. Apache Kafka, "Introduction - Main Concepts and Terminology", https://kafka.apache.org/intro/
3. Confluent, "Apache Kafka Dead Letter Queue: A Comprehensive Guide", https://www.confluent.io/learn/kafka-dead-letter-queue/
4. Spring Cloud Stream, "Dead-Letter Topic Processing", https://docs.spring.io/spring-cloud-stream/reference/kafka/kafka-binder/dlq.html
