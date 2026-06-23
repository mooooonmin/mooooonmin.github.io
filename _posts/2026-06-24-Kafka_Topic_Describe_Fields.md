---
title: Kafka Topic Describe Fields
category: k
date: 2026-06-24 00:00:00 +0900
tags: [kafka, leader, replicas, isr, elr, topic]
---

## 1. 토픽 세부 정보는 왜 읽을 수 있어야 할까?

Kafka를 운영하다 보면 아래 명령어로 토픽 세부 정보를 자주 확인하게 된다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic email.send
```

이 명령어를 실행하면 `PartitionCount`, `ReplicationFactor`, `Partition`, `Leader`, `Replicas`, `Isr` 같은 값이 나온다.

입문 단계에서는 이 값들을 전부 깊게 이해할 필요는 없다.
아래 핵심 항목만 읽을 수 있어도 토픽 상태를 해석하는 데 충분하다.

1. `PartitionCount`
2. `ReplicationFactor`
3. `Partition`
4. `Leader`
5. `Replicas`
6. `Isr`

그리고 Kafka 4.x 계열에서는 환경에 따라 `ELR` 같은 추가 정보가 보일 수도 있다.

---

## 2. 예시 출력값

예를 들어 아래처럼 출력됐다고 가정하자.

```text
Topic: email.send  TopicId: ...  PartitionCount: 1  ReplicationFactor: 3
  Topic: email.send  Partition: 0  Leader: 2  Replicas: 2,3,1  Isr: 2,3,1
```

이 출력값을 한 줄씩 해석해보면 된다.

---

## 3. `PartitionCount`란?

`PartitionCount`는 해당 토픽이 가지고 있는 전체 파티션 개수이다.

예를 들어

```text
PartitionCount: 1
```

이라고 나오면 이 토픽은 파티션이 1개라는 뜻이다.

만약

```text
PartitionCount: 3
```

이라고 나오면 이 토픽은 파티션이 3개라는 뜻이다.

Kafka에서는 토픽이 여러 파티션으로 나뉘고, 각 파티션 단위로 메시지가 저장되고 복제된다.

---

## 4. `ReplicationFactor`란?

`ReplicationFactor`는 해당 토픽 파티션의 복제본 수를 의미한다.

예를 들어

```text
ReplicationFactor: 3
```

이라고 나오면 각 파티션이 3개 Broker에 복제된다는 뜻이다.

Apache Kafka 공식 문서는 replication factor가 토픽별로 설정되는 복제 개수라고 설명한다. [1]

즉, 서버가 3대 있을 때 `ReplicationFactor: 3`이면 해당 파티션의 원본과 복제본이 3대 Broker에 분산되어 저장되는 구조라고 이해하면 된다.

---

## 5. `Partition`이란?

`Partition`은 해당 줄이 설명하고 있는 파티션 번호이다.

예를 들어

```text
Partition: 0
```

이라고 나오면 0번 파티션의 상태를 보여주고 있다는 뜻이다.

Kafka 파티션 번호는 보통 0부터 시작한다.

만약 파티션이 3개라면 아래처럼 나올 수 있다.

```text
Partition: 0
Partition: 1
Partition: 2
```

즉, 토픽 세부 정보 출력은 보통 파티션별 상태를 한 줄씩 보여준다고 이해하면 된다.

---

## 6. `Leader`란?

`Leader`는 해당 파티션의 leader replica를 가지고 있는 Broker id이다.

예를 들어

```text
Leader: 2
```

라고 나오면 2번 Broker가 이 파티션의 leader라는 뜻이다.

Apache Kafka 공식 문서는 leader를 해당 파티션에 대한 모든 읽기와 쓰기를 담당하는 노드라고 설명한다. [2]

즉, Producer가 메시지를 넣고 Consumer가 읽어갈 때 직접 상대하는 대상은 leader이다.

이전 글에서 설명했던 복습 내용을 짧게 정리하면 아래와 같다.

1. leader partition은 읽기/쓰기를 직접 처리한다.
2. follower replica는 leader의 데이터를 복제한다.
3. leader에 장애가 생기면 follower 중 하나가 새 leader가 될 수 있다.

따라서 `Leader`는 "현재 이 파티션의 대표 역할을 하는 Broker 번호"라고 이해하면 된다.

---

## 7. `Replicas`란?

`Replicas`는 해당 파티션을 복제해서 가지고 있도록 배정된 전체 Broker id 목록이다.

예를 들어

```text
Replicas: 2,3,1
```

이라고 나오면 이 파티션 복제본이 2번, 3번, 1번 Broker에 배치되어 있다는 뜻이다.

Apache Kafka 공식 문서는 replicas를 "이 파티션의 로그를 복제하는 노드 목록"이라고 설명한다. 그리고 leader인지 여부나 현재 살아 있는지 여부와는 별개라고 설명한다. [2]

즉, `Replicas`는 현재 동기화 상태가 어떤지를 보여주는 값이 아니라, 원래 이 파티션 복제본을 가지도록 설정된 전체 대상 목록이다.

---

## 8. `Isr`란?

`Isr`은 `In-Sync Replicas`의 줄임말이다.

즉, leader와 동기화가 맞는 복제본 목록을 의미한다.

예를 들어

```text
Isr: 2,3,1
```

이라고 나오면 2번, 3번, 1번 Broker가 모두 leader를 따라잡은 정상 동기 상태라는 뜻이다.

Apache Kafka 공식 문서는 ISR을 replicas 목록의 부분집합으로, 현재 살아 있고 leader를 따라잡은 replica 집합이라고 설명한다. [2]

즉, `Replicas`와 `Isr`의 차이는 아래처럼 정리하면 된다.

| 항목 | 의미 |
|---|---|
| `Replicas` | 원래 복제본을 가지도록 배정된 전체 Broker 목록 |
| `Isr` | 그중 현재 살아 있고 leader와 동기화가 맞는 Broker 목록 |

---

## 9. `Replicas`와 `Isr`는 왜 다를 수 있을까?

아래처럼 출력될 수도 있다.

```text
Replicas: 2,3,1
Isr: 2,3
```

이 경우는 1번 Broker도 원래는 복제본을 가지고 있어야 하지만, 현재는 leader를 충분히 따라잡지 못했거나 장애 상태라서 ISR에 포함되지 못한 것이다.

Apache Kafka 공식 모니터링 문서는 Broker가 내려가면 ISR이 줄어들고, 다시 살아나서 충분히 따라잡으면 ISR이 다시 늘어난다고 설명한다. [3]

즉, 아래처럼 이해하면 된다.

1. `Replicas`는 원래 멤버 목록
2. `Isr`는 현재 정상 동기화 멤버 목록

운영 중에는 `Isr`가 줄어드는지 여부를 보는 것이 중요하다.

---

## 10. `ELR`는 무엇일까?

환경에 따라 `ELR` 또는 `Eligible Leader Replicas` 관련 정보가 보일 수 있다.

이 개념은 Kafka 4.0에서 들어온 비교적 새로운 개념이다.

Apache Kafka 업그레이드 문서는 KRaft controller가 ISR에는 없지만 데이터 손실 없이 leader가 될 수 있는 replica를 추적하며, 이를 `Eligible Leader Replicas (ELR)`라고 설명한다. [4]

또한 Kafka ELR 문서는 ELR가 활성화되면 topic describe나 Admin API에서 관련 필드를 볼 수 있다고 설명한다. [5]

입문 단계에서는 ELR를 아래 정도로만 이해하면 충분하다.

```text
ELR = 현재 ISR은 아니지만, 특정 조건에서 안전하게 leader 후보가 될 수 있도록 관리되는 replica 정보
```

다만 대부분의 입문 실습에서는 `Leader`, `Replicas`, `Isr`를 읽을 수 있는 것만으로 충분하다.

---

## 11. 입문자 입장에서 어디까지만 보면 될까?

실제로는 출력값에 더 많은 정보가 나올 수 있다.

예를 들어

1. `TopicId`
2. `LeaderEpoch`
3. `ELR`
4. `LastKnownElr`
5. `OfflineReplicas`

같은 값이 보일 수 있다.

하지만 입문 단계에서는 아래만 우선 보면 된다.

1. `PartitionCount`로 파티션 수 확인
2. `ReplicationFactor`로 복제 수 확인
3. `Leader`로 현재 대표 Broker 확인
4. `Replicas`로 전체 복제 대상 확인
5. `Isr`로 현재 정상 동기화 Broker 확인

이 5가지만 읽을 수 있어도 토픽 상태 해석의 대부분이 가능하다.

---

## 정리

Kafka 토픽 세부 정보 출력값에서 가장 중요한 항목은 `PartitionCount`, `ReplicationFactor`, `Partition`, `Leader`, `Replicas`, `Isr`이다.

핵심만 다시 정리하면 아래와 같다.

1. `PartitionCount` = 토픽의 전체 파티션 수
2. `ReplicationFactor` = 파티션 복제본 수
3. `Partition` = 지금 보고 있는 파티션 번호
4. `Leader` = 읽기/쓰기를 직접 처리하는 Broker id
5. `Replicas` = 복제본이 배치된 전체 Broker id 목록
6. `Isr` = 현재 leader와 동기화가 맞는 Broker id 목록

그리고 `ELR`는 Kafka 4.x에서 등장한 추가 개념이지만, 입문 단계에서는 보조 개념으로만 이해해도 충분하다.

---

## 출처

1. Apache Kafka, "Design - Replication", https://kafka.apache.org/090/design/design/
2. Apache Kafka, "Quick Start", https://kafka.apache.org/11/getting-started/quickstart/
3. Apache Kafka, "Monitoring - ISR shrink/expand", https://kafka.apache.org/082/operations/monitoring/
4. Apache Kafka, "Upgrading to 4.0 - Eligible Leader Replicas", https://kafka.apache.org/41/getting-started/upgrade/
5. Apache Kafka, "Eligible Leader Replicas", https://kafka.apache.org/41/operations/eligible-leader-replicas/
