---
title: Kafka Partition Count CLI
category: k
date: 2026-06-19 00:00:10 +0900
tags: [kafka, partition, topic, cli, kafka-topics]
---

## 1. 특정 Topic의 Partition 수 조회하기

Topic에 설정된 Partition 수를 확인하려면 Topic 세부 정보를 조회하면 된다.

이전에 배웠던 `--describe` 옵션을 사용한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic email.send
```

출력은 아래와 비슷하다.

```text
Topic: email.send  TopicId: ...  PartitionCount: 1  ReplicationFactor: 1  Configs:
Topic: email.send  Partition: 0  Leader: 1  Replicas: 1  Isr: 1
```

여기서 먼저 확인할 값은 두 가지이다.

| 항목 | 의미 |
|---|---|
| `PartitionCount` | Topic이 가지고 있는 Partition의 총 개수 |
| `Partition` | Partition 번호 |

Partition 번호는 0부터 시작한다.

```text
Partition: 0
Partition: 1
Partition: 2
```

따라서 `PartitionCount: 3`이라면 Partition 번호는 보통 `0`, `1`, `2`로 표시된다.

---

## 2. 기본 Partition 수는 설정에 따라 달라진다

Topic을 생성할 때 `--partitions` 옵션을 주지 않으면 Kafka 브로커의 기본 설정값이 사용된다.

실습 환경에서는 보통 Partition이 1개로 생성된 것처럼 보일 수 있다.
하지만 Kafka에서 항상 무조건 1개로 생성된다고 외우면 안 된다.

Kafka 문서의 broker config에는 `num.partitions` 설정이 있으며, 이 값은 Topic별 Partition 수가 지정되지 않았을 때의 기본 Partition 수를 의미한다. [1]

입문 단계에서는 아래처럼 기억하면 된다.

```text
--partitions 옵션을 지정하면 그 값으로 생성된다.
--partitions 옵션을 생략하면 브로커 기본 설정값을 따른다.
```

---

## 3. Topic 생성할 때 Partition 수 설정하기

Topic을 생성할 때 Partition 수를 직접 지정하려면 `--partitions` 옵션을 사용한다.

기본 문법은 아래와 같다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server <Kafka 주소> \
  --create \
  --topic <Topic 이름> \
  --partitions <Partition 수>
```

예를 들어 Partition 3개를 가진 `test.topic` Topic을 만들려면 아래처럼 입력한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic test.topic \
  --partitions 3
```

Apache Kafka Quickstart도 Topic 생성 예시에서 `--partitions` 옵션을 사용해 Partition 수를 지정한다. [2]

---

## 4. Partition 수가 잘 설정됐는지 확인하기

Topic이 잘 생성됐는지 확인하려면 다시 `--describe` 옵션을 사용한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic test.topic
```

출력에 아래처럼 `PartitionCount: 3`이 보이면 Partition 3개로 생성된 것이다.

```text
Topic: test.topic  TopicId: ...  PartitionCount: 3  ReplicationFactor: 1  Configs:
Topic: test.topic  Partition: 0  Leader: 1  Replicas: 1  Isr: 1
Topic: test.topic  Partition: 1  Leader: 1  Replicas: 1  Isr: 1
Topic: test.topic  Partition: 2  Leader: 1  Replicas: 1  Isr: 1
```

그림으로 표현하면 아래와 같다.

```text
test.topic
├── Partition 0
├── Partition 1
└── Partition 2
```

---

## 5. 기존 Topic의 Partition 수 늘리기

이미 만들어진 Topic의 Partition 수를 늘릴 때는 `--alter`와 `--partitions` 옵션을 함께 사용한다.

기본 문법은 아래와 같다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server <Kafka 주소> \
  --alter \
  --topic <Topic 이름> \
  --partitions <변경할 최종 Partition 수>
```

여기서 중요한 점은 `<변경할 최종 Partition 수>`를 입력한다는 것이다.

예를 들어 기존 `test.topic`의 Partition 수가 3개이고, 이를 5개로 늘리고 싶다면 아래처럼 입력한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --alter \
  --topic test.topic \
  --partitions 5
```

Confluent 문서는 기존 Topic의 Partition 수를 늘릴 때 `kafka-topics.sh --alter --partitions <number>` 형식을 사용할 수 있다고 설명한다. [3]

---

## 6. Partition 수 증가 확인하기

Partition 수가 5개로 늘었는지 확인한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic test.topic
```

출력에 아래처럼 `PartitionCount: 5`가 보이면 변경된 것이다.

```text
Topic: test.topic  TopicId: ...  PartitionCount: 5  ReplicationFactor: 1  Configs:
Topic: test.topic  Partition: 0  Leader: 1  Replicas: 1  Isr: 1
Topic: test.topic  Partition: 1  Leader: 1  Replicas: 1  Isr: 1
Topic: test.topic  Partition: 2  Leader: 1  Replicas: 1  Isr: 1
Topic: test.topic  Partition: 3  Leader: 1  Replicas: 1  Isr: 1
Topic: test.topic  Partition: 4  Leader: 1  Replicas: 1  Isr: 1
```

그림으로 표현하면 아래와 같다.

```text
test.topic
├── Partition 0
├── Partition 1
├── Partition 2
├── Partition 3
└── Partition 4
```

---

## 7. 기존 Topic의 Partition 수 줄이기

이번에는 Partition 수를 5개에서 3개로 줄여보자.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --alter \
  --topic test.topic \
  --partitions 3
```

이 명령어는 실패한다.

Kafka는 기존 Topic의 Partition 수를 줄이는 기능을 지원하지 않는다.
Apache Kafka 공식 Operations 문서도 Topic의 Partition 수를 줄이는 것을 현재 지원하지 않는다고 설명한다. [4]

즉, 아래 흐름은 가능하다.

```text
3개 -> 5개
```

하지만 아래 흐름은 불가능하다.

```text
5개 -> 3개
```

---

## 8. 왜 Partition 수를 줄일 수 없을까?

Partition에는 이미 메시지가 저장되어 있을 수 있다.

예를 들어 Partition 3과 Partition 4에 메시지가 들어있는 상태에서 Partition 수를 5개에서 3개로 줄인다고 해보자.

```text
test.topic
├── Partition 0
├── Partition 1
├── Partition 2
├── Partition 3  <- 메시지 있음
└── Partition 4  <- 메시지 있음
```

Partition 3과 Partition 4를 없애려면 그 안의 데이터를 어떻게 처리할지 결정해야 한다.
데이터를 옮기는 과정에서도 메시지 순서, key 기반 분배, Consumer offset 같은 문제가 생길 수 있다.

Apache Kafka 공식 Operations 문서는 Partition을 추가해도 기존 데이터의 Partitioning은 변경되지 않으며, Kafka가 데이터를 자동으로 재분배하지 않는다고 설명한다. [4]
Confluent 문서도 key가 있는 메시지의 경우 Partition 수를 늘리면 같은 key가 매핑되는 Partition이 달라질 수 있어 주의해야 한다고 설명한다. [3]

따라서 Partition 수는 늘릴 수는 있지만 줄일 수는 없다고 이해하면 된다.

---

## 9. Partition 수를 줄이고 싶다면?

이미 만들어진 Topic의 Partition 수를 줄이고 싶다면 기존 Topic을 직접 줄이는 방식은 사용할 수 없다.

대신 아래와 같은 방식이 필요하다.

1. 원하는 Partition 수로 새 Topic을 만든다.
2. 기존 Topic의 데이터를 새 Topic으로 옮긴다.
3. Producer와 Consumer가 새 Topic을 사용하도록 변경한다.
4. 더 이상 필요하지 않은 기존 Topic을 정리한다.

이 과정은 단순하지 않다.
운영 중인 서비스에서는 데이터 마이그레이션, Consumer offset, 메시지 순서, 장애 대응까지 고려해야 한다.

그래서 처음 Topic을 만들 때 Partition 수를 신중하게 정하는 것이 중요하다.

---

## 10. 명령어 정리

특정 Topic의 Partition 수를 조회한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic email.send
```

Partition 3개를 가진 Topic을 생성한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic test.topic \
  --partitions 3
```

생성 결과를 확인한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic test.topic
```

기존 Topic의 Partition 수를 5개로 늘린다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --alter \
  --topic test.topic \
  --partitions 5
```

변경 결과를 확인한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic test.topic
```

---

## 정리

Topic의 Partition 수는 `kafka-topics.sh --describe`로 조회할 수 있다.
Topic을 생성할 때는 `--partitions` 옵션으로 Partition 수를 지정할 수 있다.

기존 Topic의 Partition 수는 `--alter --partitions <최종 Partition 수>`로 늘릴 수 있다.
하지만 Kafka는 기존 Topic의 Partition 수를 줄이는 기능을 지원하지 않는다.

Partition 수를 줄여야 한다면 원하는 Partition 수의 새 Topic을 만들고 데이터를 마이그레이션하는 방식으로 접근해야 한다.

---

## 출처

1. Apache Kafka, "Configuration - Broker Configs: num.partitions", https://kafka.apache.org/documentation/#brokerconfigs_num.partitions
2. Apache Kafka, "Quickstart - Create a topic to store your events", https://kafka.apache.org/quickstart/
3. Confluent Documentation, "Choose and Change the Partition Count in Kafka", https://docs.confluent.io/kafka/operations-tools/partition-determination.html
4. Apache Kafka, "Basic Kafka Operations", https://kafka.apache.org/10/operations/basic-kafka-operations/
