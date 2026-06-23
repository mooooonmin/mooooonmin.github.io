---
title: Kafka Three Node Verification
category: k
date: 2026-06-23 00:00:10 +0900
tags: [kafka, replication, isr, broker, cluster, topic]
---

## 1. Kafka 서버 3대가 잘 연동됐는지 어떻게 확인할까?

Kafka 서버 3대가 정말 서로 잘 연동됐는지 확인하려면, 서버 개수에 맞게 토픽의 레플리케이션을 만들어보는 방법이 가장 직관적이다.

Apache Kafka 공식 문서는 토픽을 만들 때 `replication-factor`로 메시지 복제본 수를 지정할 수 있다고 설명한다. 또한 replication factor가 3이면 각 메시지가 3개 서버에 복제된다고 설명한다. [1]

즉, Kafka 서버가 3대 있는 상태에서 아래처럼 토픽을 만들었을 때

```bash
--replication-factor 3
```

토픽 세부 정보에서 복제본이 3개 서버에 모두 잡혀 있으면, 3대 서버가 클러스터로 연결되어 있다고 해석할 수 있다.

---

## 2. 실습 전에 먼저 할 일

기존 Producer, Consumer 서버가 실행 중이라면 먼저 종료한다.

이유는 기존 메시지나 토픽 상태가 남아 있으면, 지금 만들 레플리케이션 실습 결과를 보기 헷갈릴 수 있기 때문이다.

---

## 3. 기존 토픽 삭제하기

기존 `email.send` 토픽이 남아 있다면 먼저 삭제한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic email.send
```

그리고 토픽이 잘 삭제됐는지 전체 목록으로 확인한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --list
```

목록에서 `email.send`가 보이지 않으면 삭제된 것이다.

---

## 4. 파티션 1개, 레플리케이션 3개로 토픽 생성하기

이제 레플리케이션이 3개인 새 토픽을 만든다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic email.send \
  --partitions 1 \
  --replication-factor 3
```

이 명령어의 의미는 아래와 같다.

| 옵션 | 의미 |
|---|---|
| `--topic email.send` | `email.send`라는 이름의 토픽 생성 |
| `--partitions 1` | 파티션을 1개만 생성 |
| `--replication-factor 3` | 그 파티션의 복제본을 3개 서버에 배치 |

Apache Kafka 공식 문서는 replication factor가 메시지를 몇 개 서버에 복제할지를 결정한다고 설명한다. [1]

---

## 5. 토픽 세부 정보 조회하기

이제 Node 1의 Broker 포트로 토픽 세부 정보를 확인한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic email.send
```

출력에서는 아래 항목을 보면 된다.

```text
Topic: email.send
Partition: 0
Leader: ...
Replicas: 1,2,3
Isr: 1,2,3
```

여기서 의미는 아래와 같다.

| 항목 | 의미 |
|---|---|
| `Leader` | 해당 파티션의 읽기/쓰기 요청을 직접 처리하는 Broker |
| `Replicas` | 해당 파티션을 복제해서 가지고 있는 전체 Broker 목록 |
| `Isr` | 현재 살아 있고 leader를 따라잡은 in-sync replica 목록 |

Apache Kafka Quick Start 문서는

1. `leader`는 읽기/쓰기를 담당하는 노드이고,
2. `replicas`는 해당 파티션 로그를 복제하는 노드 목록이며,
3. `isr`은 그중 현재 살아 있고 leader를 따라잡은 replica 집합

이라고 설명한다. [2]

따라서 `Replicas`와 `Isr`에 3개의 Broker 번호가 모두 보이면, 적어도 현재 시점에서는 3대 Kafka 서버가 정상적으로 복제 구성을 이루고 있다고 볼 수 있다.

---

## 6. 왜 `Replicas`와 `Isr`를 같이 봐야 할까?

`Replicas`에 3개가 있다고 해서 항상 현재 정상 상태라는 뜻은 아니다.

이유는 `Replicas`는 원래 복제 대상으로 배정된 Broker 목록이고, `Isr`은 현재 실제로 leader를 따라잡은 정상 복제본 목록이기 때문이다.

Apache Kafka 설계 문서는 ISR을 "leader를 따라잡은(in-sync) replica 집합"이라고 설명한다. Broker가 내려가면 ISR이 줄어들고, 다시 따라잡으면 ISR이 늘어난다. [3]

즉, 아래처럼 보이면

```text
Replicas: 1,2,3
Isr: 1,2
```

3개 Broker에 복제는 배정됐지만, 현재는 그중 1개가 동기 상태를 따라오지 못하고 있다는 뜻이다.

반대로 아래처럼 보이면

```text
Replicas: 1,2,3
Isr: 1,2,3
```

현재 3개 Broker가 모두 정상적으로 동기화되고 있다는 뜻이다.

---

## 7. 다른 Broker 포트로도 같은 토픽이 보이는지 확인하기

이번에는 다른 Kafka Broker 포트로도 같은 토픽 세부 정보를 조회해본다.

Node 2:

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:19092 \
  --describe \
  --topic email.send
```

Node 3:

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:29092 \
  --describe \
  --topic email.send
```

두 명령어에서도 동일하게 `email.send` 토픽의 세부 정보가 조회되면, 클러스터 메타데이터가 3개 Broker에서 공통으로 보인다는 뜻이다.

그리고 각 조회 결과에서도 `Replicas`, `Isr`가 3개 Broker를 가리키고 있다면 3대 Kafka 서버가 서로 연동되어 같은 토픽 복제 구성을 공유하고 있다고 해석할 수 있다.

---

## 8. 이 실습 결과를 어떻게 해석하면 될까?

이번 실습에서 확인한 사실은 아래와 같다.

1. `replication-factor 3`으로 토픽 생성이 성공했다.
2. `Replicas`에 3개 Broker가 표시됐다.
3. `Isr`에도 3개 Broker가 표시됐다.
4. 다른 Broker 포트로 조회해도 같은 토픽 정보가 보였다.

이 4가지를 합치면 다음처럼 해석할 수 있다.

```text
Kafka Broker 3대가 하나의 클러스터로 연결되어 있다.
토픽 파티션 복제본이 3대 Broker에 배치되어 있다.
현재 3대 Broker가 모두 in-sync 상태다.
```

---

## 정리

Kafka 서버 3대가 잘 연동됐는지 확인하려면, 토픽을 `replication-factor 3`으로 만들고 `--describe` 결과에서 `Replicas`와 `Isr`를 확인하면 된다.

핵심은 아래와 같다.

1. 기존 토픽을 삭제한다.
2. `--partitions 1 --replication-factor 3`으로 새 토픽을 만든다.
3. `--describe` 결과에서 `Replicas: 1,2,3`이 보이는지 확인한다.
4. `Isr: 1,2,3`도 함께 보이는지 확인한다.
5. 다른 Broker 포트에서도 같은 토픽 정보가 조회되는지 확인한다.

다음 글에서는 여기서 한 단계 더 나아가, 실제로 Broker 하나에 장애가 났을 때 leader와 replica가 어떻게 바뀌는지 이어서 확인해볼 수 있다.

---

## 출처

1. Apache Kafka, "Basic Kafka Operations", https://kafka.apache.org/42/operations/basic-kafka-operations/
2. Apache Kafka, "Quick Start", https://kafka.apache.org/11/getting-started/quickstart/
3. Apache Kafka, "Design - Replication and ISR", https://kafka.apache.org/43/design/design/
