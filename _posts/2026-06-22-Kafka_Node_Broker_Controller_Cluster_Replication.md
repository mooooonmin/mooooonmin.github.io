---
title: Kafka Node Broker Controller Cluster Replication
category: k
date: 2026-06-22 00:00:10 +0900
tags: [kafka, node, broker, controller, cluster, replication]
---

## 1. 왜 이 용어들을 알아야 할까?

Kafka의 고가용성을 이해하려면 아래 용어를 먼저 알아야 한다.

```text
node
broker
controller
cluster
replication
```

이 용어들은 Kafka가 장애 상황에서도 어떻게 계속 동작하는지 이해하는 데 직접 연결된다.

---

## 2. Node란?

Node는 Kafka가 실행되는 서버 단위를 뜻한다.

입문 단계에서는 아래처럼 생각하면 된다.

```text
Kafka가 설치되어 있고 Kafka 프로세스가 실행되는 서버 1대 = Node 1개
```

예를 들어 Kafka 서버가 1대만 있다면 아래 구조이다.

```text
Node 1
```

이 구조에서는 그 서버가 멈추면 Kafka 자체를 사용할 수 없게 될 수 있다.
메시지를 저장하거나 읽는 기능이 함께 멈추기 때문이다.

실무에서는 이런 위험을 줄이기 위해 Kafka 서버를 여러 대로 구성하는 편이 일반적이다.

---

## 3. Cluster란?

Cluster는 여러 대의 Kafka 서버가 함께 동작하는 집합을 의미한다.

Kafka 공식 문서는 Kafka가 서버와 클라이언트로 이루어진 분산 시스템이며, 여러 서버가 클러스터를 구성한다고 설명한다. [1]

예를 들어 아래와 같이 3대의 Node가 함께 동작하면 하나의 Kafka Cluster라고 볼 수 있다.

```text
Node 1
Node 2
Node 3
```

이 여러 Node는 서로 완전히 독립적으로 놀지 않는다.
데이터를 나누어 저장하고, 복제본을 유지하고, 장애가 생기면 다른 Node가 일부 역할을 이어받을 수 있다.

즉, Cluster는 여러 대의 서버가 함께 하나의 Kafka 시스템처럼 동작하는 구조이다.

---

## 4. Broker란?

Broker는 메시지를 저장하고 Producer와 Consumer의 요청을 처리하는 Kafka 서버 역할이다.

입문 단계에서는 아래처럼 이해하면 된다.

```text
Broker = 실제 데이터를 저장하고 읽기/쓰기 요청을 처리하는 역할
```

Kafka 공식 문서는 분산 시스템의 Kafka 서버를 broker라고 설명한다. [1]

예를 들어 Producer가 메시지를 Topic에 쓰거나 Consumer가 Topic에서 메시지를 읽을 때, 실제 요청을 처리하는 쪽이 Broker이다.

```text
Producer -> Broker
Consumer -> Broker
```

Broker는 아래 같은 일을 한다.

| 역할 | 설명 |
|---|---|
| 데이터 저장 | Topic의 Partition 데이터를 디스크에 저장 |
| 쓰기 처리 | Producer가 보내는 메시지를 저장 |
| 읽기 처리 | Consumer가 읽는 메시지를 전달 |
| 복제 협력 | 다른 Broker와 Partition 복제를 유지 |

---

## 5. Controller란?

Controller는 Kafka Cluster의 메타데이터와 전체 상태를 관리하는 역할이다.

입문 단계에서는 아래처럼 이해하면 된다.

```text
Broker = 실데이터 처리 담당
Controller = 클러스터 운영 상태 관리 담당
```

Kafka KRaft 공식 문서는 각 Kafka 서버가 `broker`, `controller`, `broker,controller` 역할 중 하나로 설정될 수 있다고 설명한다. [2]

즉, 현재 Kafka에서는 아래 세 가지 구성이 가능하다.

```text
process.roles=broker
process.roles=controller
process.roles=broker,controller
```

이 말은 Controller가 언제나 별도 서버에 따로 떠 있어야 한다는 뜻은 아니라는 것이다.
실습 환경에서는 Broker와 Controller 역할을 한 서버가 동시에 가질 수도 있다.

Controller는 보통 아래 같은 일을 맡는다.

| 역할 | 설명 |
|---|---|
| 메타데이터 관리 | Topic, Partition, Broker 정보 관리 |
| 리더 선출 관리 | 어떤 replica가 leader가 될지 관리 |
| 클러스터 상태 관리 | 어떤 Broker가 살아 있는지 확인 |

---

## 6. Broker와 Controller는 항상 9092, 9093 포트일까?

항상 그렇지는 않다.

실습 자료나 예제에서는 Broker listener를 `9092`, Controller listener를 `9093`으로 두는 경우가 많다.
하지만 Kafka 공식 문서 기준으로 listener와 역할은 설정값으로 정하는 것이다. [2]

즉, 아래 같은 예시는 흔하지만 고정 규칙은 아니다.

```text
Broker listener -> 9092
Controller listener -> 9093
```

정확한 표현은 아래와 같다.

```text
포트는 환경과 설정에 따라 달라질 수 있다.
```

따라서 `9092`, `9093`은 자주 보는 예시라고 이해하는 것이 맞다.

---

## 7. Replication이란?

Replication은 Kafka가 데이터를 여러 서버에 복제해서 저장하는 방식이다.

Kafka 공식 문서는 Topic Partition의 이벤트 로그를 여러 서버에 복제한다고 설명한다. [3]

입문 단계에서는 아래처럼 이해하면 된다.

```text
Replication = Partition 복사본을 여러 Node에 저장하는 것
```

예를 들어 `email.send` Topic의 Partition 0이 있다고 해보자.

복제가 없다면 아래처럼 하나의 Broker에만 데이터가 있다.

```text
Node 1 -> email.send Partition 0
```

하지만 복제를 사용하면 아래처럼 여러 Node에 복사본이 생긴다.

```text
Node 1 -> email.send Partition 0
Node 2 -> email.send Partition 0 replica
Node 3 -> email.send Partition 0 replica
```

이 복제는 데이터 안정성과 가용성을 높이기 위해 사용된다.

---

## 8. Leader Replica와 Follower Replica

복제된 Partition들은 보통 Leader Replica와 Follower Replica로 나뉜다.

```text
Leader Replica = 실제 읽기/쓰기 요청을 직접 받는 복제본
Follower Replica = Leader를 따라가며 데이터를 복제하는 복제본
```

Confluent 문서는 모든 write와 read가 partition leader로 가고, follower는 leader를 수동적으로 복제한다고 설명한다. [3]

즉, Producer와 Consumer는 보통 아래처럼 Leader Replica와 직접 통신한다.

```text
Producer -> Leader Replica
Consumer -> Leader Replica
```

Follower Replica는 아래처럼 Leader의 데이터를 계속 따라간다.

```text
Leader Replica -> Follower Replica들
```

만약 Leader가 있는 Broker에 장애가 생기면, Kafka는 다른 replica를 새 Leader로 승격시켜 계속 처리할 수 있다.
이 때문에 복제는 Kafka 고가용성의 핵심이다.

---

## 9. Replication Factor란?

Replication Factor는 Partition 복제본 개수를 의미한다.

예를 들어 Replication Factor가 3이라면, 하나의 Partition에 대해 총 3개의 replica가 존재한다.

```text
Replication Factor = 3
-> Partition 원본 1개 + 복제본 포함 총 3개 replica
```

Apache Kafka 공식 소개 문서는 운영에서 흔한 설정 예시로 replication factor 3을 언급한다. [1]

입문 단계에서는 아래처럼 기억하면 된다.

```text
Replication Factor가 클수록 장애 대응 여지가 커진다.
대신 저장 공간과 네트워크 비용도 더 든다.
```

실무에서는 2 또는 3을 많이 사용한다는 설명은 흔하지만, 실제 적정 값은 장애 허용 수준과 인프라 비용에 따라 달라진다.

---

## 10. 왜 여러 Node와 Replication이 필요한가?

Kafka 서버가 1대이고 복제도 없다면 장애 상황은 단순하다.

```text
Node 1 장애
-> 메시지 저장 불가
-> 메시지 읽기 불가
-> 서비스 장애 가능
```

반면 여러 Node와 Replication이 있으면 일부 장애가 나도 계속 처리할 가능성이 커진다.

```text
Node 1 장애
-> 다른 Node에 replica 존재
-> 다른 replica가 leader 승격 가능
-> 서비스 지속 가능
```

즉, Kafka의 고가용성은 아래 요소가 함께 만들어낸다.

| 요소 | 역할 |
|---|---|
| 여러 Node | 단일 서버 장애 위험 완화 |
| Cluster | 여러 서버가 함께 동작 |
| Broker | 실제 데이터 저장/요청 처리 |
| Controller | 클러스터 상태와 리더 선출 관리 |
| Replication | 장애 시에도 데이터와 서비스 지속 가능성 확보 |

---

## 정리

Node는 Kafka가 실행되는 서버 단위이다.
Cluster는 여러 Kafka 서버가 함께 동작하는 집합이다.

Broker는 메시지를 저장하고 요청을 처리하는 역할이다.
Controller는 클러스터 상태와 메타데이터를 관리하는 역할이다.

Replication은 Topic Partition을 여러 서버에 복제하는 방식이다.
Leader Replica는 실제 읽기/쓰기 요청을 받고, Follower Replica는 Leader를 따라 데이터를 복제한다.

Kafka의 고가용성은 여러 Node, Cluster 구성, Controller 관리, Replication 구조를 함께 사용해서 만든다.

---

## 출처

1. Apache Kafka, "Introduction", https://kafka.apache.org/documentation/
2. Apache Kafka, "KRaft - Process Roles", https://kafka.apache.org/41/operations/kraft/
3. Confluent Documentation, "Kafka Replication", https://docs.confluent.io/kafka/design/replication.html
