---
title: Kafka Partition
category: k
date: 2026-06-19 00:00:00 +0900
tags: [kafka, partition, topic, consumer-group, concurrency]
---

## 1. 파티션이란?

파티션(Partition)은 Kafka Topic을 나누는 단위이다.

입문 단계에서는 아래처럼 이해하면 된다.

```text
Topic = 메시지를 저장하는 큰 공간
Partition = Topic 안에 나뉘어 있는 메시지 저장 공간
```

예를 들어 `email.send` Topic에 Partition이 3개 있다면 아래처럼 볼 수 있다.

```text
email.send Topic
├── Partition 0
├── Partition 1
└── Partition 2
```

Kafka에서 Partition은 병렬 처리와 처리량에 큰 영향을 주는 핵심 개념이다.
Partition이 여러 개 있으면 Consumer Group 안의 여러 Consumer가 서로 다른 Partition을 맡아 병렬로 처리할 수 있기 때문이다.

Apache Kafka 공식 문서는 Topic이 여러 Partition으로 나뉘며, 같은 event key를 가진 이벤트는 같은 Partition에 기록된다고 설명한다. [1]

---

## 2. 왜 Partition이 필요한가?

이전 글에서는 Consumer가 메시지를 하나씩 처리하는 현상을 봤다.

Consumer 코드에 아래 코드가 들어있었다.

```java
Thread.sleep(3000);
```

그래서 메시지 하나를 처리하는 데 약 3초가 걸렸다.

메시지 3개를 하나의 Consumer가 순서대로 처리하면 아래처럼 총 9초 정도 걸릴 수 있다.

```text
3초 + 3초 + 3초 = 9초
```

하지만 메시지를 나누어 여러 Consumer가 병렬로 처리할 수 있다면 처리 시간이 줄어들 수 있다.

```text
Consumer 1 -> 메시지 A 처리
Consumer 2 -> 메시지 B 처리
Consumer 3 -> 메시지 C 처리
```

Kafka에서 이런 병렬 처리의 기본 단위가 Partition이다.

---

## 3. 각 Topic은 하나 이상의 Partition으로 구성된다

Kafka Topic은 하나 이상의 Partition으로 구성된다.

Topic을 생성할 때 Partition 수를 지정할 수 있다.

예를 들어 Partition 3개를 가진 `email.send` Topic을 만들려면 아래처럼 `--partitions` 옵션을 사용할 수 있다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic email.send \
  --partitions 3
```

Kafka Quickstart도 Topic을 생성할 때 `--partitions` 옵션을 사용해 Partition 수를 지정하는 예시를 보여준다. [2]

반대로 `--partitions` 옵션을 생략하면 Partition 수는 브로커의 기본 설정에 따라 결정된다.
실습용 기본 설정에서는 보통 1개로 보일 수 있지만, 항상 1개라고 외우면 안 된다.

정확히는 Kafka 브로커의 `num.partitions` 설정값이 기본 Partition 수에 영향을 준다. [3]

---

## 4. Producer가 메시지를 보내면 Partition에 저장된다

Producer가 특정 Topic에 메시지를 보내면 Kafka는 그 메시지를 Topic 안의 어떤 Partition에 저장한다.

```text
Producer -> email.send Topic -> Partition 0
Producer -> email.send Topic -> Partition 1
Producer -> email.send Topic -> Partition 2
```

다만 메시지가 무조건 완벽하게 균등하게 분산된다고 단정하면 안 된다.
어떤 Partition으로 갈지는 메시지 key와 Producer partitioner 정책에 영향을 받는다.

Apache Kafka 공식 문서는 같은 key를 가진 이벤트가 같은 Partition에 기록된다고 설명한다. [1]
즉, key를 사용하면 같은 종류의 메시지를 같은 Partition으로 보내 순서를 유지하는 데 활용할 수 있다.

입문 단계에서는 아래처럼 이해하면 된다.

```text
Partition이 여러 개 있으면 메시지를 저장할 수 있는 공간이 여러 개 생긴다.
이 공간들을 기반으로 병렬 처리 가능성이 생긴다.
```

대형 마트에 계산대가 여러 개 있으면 손님을 여러 줄로 나누어 처리할 수 있는 것과 비슷하다.
Partition이 여러 개 있으면 Consumer도 여러 Partition을 나누어 처리할 수 있다.

---

## 5. 하나의 Partition은 같은 Consumer Group 안에서 하나의 Consumer에게만 할당된다

Kafka Consumer Group에서 중요한 규칙이 있다.

```text
같은 Consumer Group 안에서는 하나의 Partition을 동시에 여러 Consumer가 함께 처리하지 않는다.
```

Confluent 문서는 각 Partition이 특정 시점에 각 Consumer Group 안에서 정확히 하나의 Consumer에 의해 소비된다고 설명한다. [4]

정상적인 구조는 아래와 같다.

```text
Consumer Group: email-send-group

Partition 0 -> Consumer 1
Partition 1 -> Consumer 2
Partition 2 -> Consumer 3
```

잘못 이해하기 쉬운 구조는 아래이다.

```text
Consumer Group: email-send-group

Partition 0 -> Consumer 1
Partition 0 -> Consumer 2
```

같은 Consumer Group 안에서 여러 Consumer가 하나의 Partition을 동시에 나누어 처리하는 구조로 이해하면 안 된다.

이 규칙 덕분에 Partition 안의 메시지 순서를 지킬 수 있다.

---

## 6. 하나의 Consumer가 여러 Partition을 처리할 수 있다

반대로 하나의 Consumer가 여러 Partition을 처리하는 것은 가능하다.

예를 들어 Partition은 3개인데 Consumer가 1개만 있다면 아래처럼 한 Consumer가 여러 Partition을 맡을 수 있다.

```text
Consumer Group: email-send-group

Partition 0 -> Consumer 1
Partition 1 -> Consumer 1
Partition 2 -> Consumer 1
```

Consumer가 2개이고 Partition이 3개라면 아래처럼 나뉠 수도 있다.

```text
Consumer Group: email-send-group

Partition 0 -> Consumer 1
Partition 1 -> Consumer 2
Partition 2 -> Consumer 1
```

즉, Consumer 수가 Partition 수보다 적으면 어떤 Consumer는 여러 Partition을 처리할 수 있다.

---

## 7. 하나의 Partition 안에서는 메시지를 순서대로 읽는다

Partition 안의 메시지는 offset 순서를 가진다.

```text
Partition 0
offset 0 -> hello1
offset 1 -> hello2
offset 2 -> hello3
```

Apache Kafka 공식 문서는 특정 topic-partition을 읽는 Consumer가 해당 Partition의 이벤트를 쓰인 순서와 같은 순서로 읽는다고 설명한다. [5]

예를 들어 Consumer 1이 Partition 0을 처리하고 있다면, Consumer 1은 offset 0 메시지를 읽고 그 다음 offset 1 메시지를 읽는다.

```text
offset 0 처리 -> offset 1 처리 -> offset 2 처리
```

같은 Partition 안에서 offset 0과 offset 1을 동시에 병렬 처리한다고 이해하면 안 된다.
Partition 단위로 순서를 보장하기 위해 같은 Partition 안의 메시지는 순서가 중요하다.

---

## 8. 이전 글의 현상과 연결하기

이전 글에서 API 요청을 3번 연속으로 보냈는데 Consumer가 메시지를 하나씩 처리하는 현상을 봤다.

그 이유는 현재 실습 구조에서 Consumer가 처리할 수 있는 병렬성이 충분히 열려 있지 않았기 때문이다.

입문 단계에서는 아래처럼 연결해서 이해하면 된다.

```text
Partition이 1개
Consumer 처리 병렬성도 1
-> 메시지가 하나씩 처리되는 것처럼 보임
```

Spring Boot가 HTTP 요청을 여러 개 받을 수 있다고 해서 Kafka Consumer가 자동으로 여러 메시지를 병렬 처리하는 것은 아니다.

Kafka Consumer 병렬 처리는 Partition 수, Consumer Group 안의 Consumer 수, Spring Kafka listener concurrency 설정과 함께 봐야 한다.

---

## 9. Partition 특징 정리

Partition의 핵심 특징은 아래와 같다.

| 특징 | 설명 |
|---|---|
| Topic은 하나 이상의 Partition으로 구성된다 | Partition 수는 Topic 생성 옵션이나 브로커 기본 설정에 따라 정해진다 |
| Producer 메시지는 특정 Partition에 저장된다 | key와 partitioner 정책에 따라 Partition이 선택된다 |
| 같은 Consumer Group 안에서 하나의 Partition은 하나의 Consumer에게만 할당된다 | 여러 Consumer가 같은 Partition을 동시에 나누어 처리하지 않는다 |
| 하나의 Consumer가 여러 Partition을 처리할 수 있다 | Consumer 수가 Partition 수보다 적으면 한 Consumer가 여러 Partition을 맡을 수 있다 |
| Partition 안에서는 순서가 중요하다 | 같은 Partition의 메시지는 offset 순서대로 읽힌다 |

---

## 정리

Partition은 Kafka Topic을 나누는 단위이다.
Partition은 Kafka에서 병렬 처리와 메시지 처리량에 큰 영향을 주는 핵심 개념이다.

같은 Consumer Group 안에서는 하나의 Partition이 하나의 Consumer에게만 할당된다.
반대로 하나의 Consumer가 여러 Partition을 처리할 수는 있다.

또한 같은 Partition 안에서는 메시지 순서가 중요하다.
그래서 Partition을 이해해야 Kafka Consumer가 왜 하나씩 처리되는 것처럼 보였는지, 어떻게 병렬 처리 성능을 높일 수 있는지 이해할 수 있다.

다음 글에서는 실습을 통해 Partition의 특징을 직접 확인한다.

---

## 출처

1. Apache Kafka, "Introduction - Main Concepts and Terminology", https://kafka.apache.org/intro/
2. Apache Kafka, "Quickstart - Create a topic to store your events", https://kafka.apache.org/quickstart/
3. Apache Kafka, "Configuration - Broker Configs: num.partitions", https://kafka.apache.org/documentation/#brokerconfigs_num.partitions
4. Confluent Documentation, "Kafka Consumer Design: Consumers, Consumer Groups, and Offsets", https://docs.confluent.io/kafka/design/consumer-design.html
5. Apache Kafka, "Documentation - Introduction", https://kafka.apache.org/documentation/
