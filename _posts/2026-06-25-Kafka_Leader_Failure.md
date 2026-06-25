---
title: Kafka Leader Failure
category: k
date: 2026-06-25 00:00:10 +0900
tags: [kafka, leader, isr, broker, failover, replication]
---

## 1. 리더 파티션에 장애가 나면 어떻게 될까?

Kafka를 복제 구조로 운영하는 가장 큰 이유 중 하나는, leader replica가 있는 Broker에 장애가 나더라도 다른 replica가 leader 역할을 이어받을 수 있게 만들기 위해서이다.

Apache Kafka 공식 문서는 partition마다 하나의 leader와 여러 follower가 있고, leader가 실패하면 follower 중 하나가 자동으로 새 leader가 된다고 설명한다. [1]

또한 Kafka 공식 설계 문서는 ISR(In-Sync Replicas) 안에 있는 replica만 leader 후보가 될 수 있다고 설명한다. [2]

즉, 입문 단계에서는 아래처럼 이해하면 된다.

```text
리더 파티션에 장애가 나면
ISR 안에 있던 follower replica 중 하나가 새 leader가 된다.
```

---

## 2. 먼저 leader가 누구인지 확인하기

현재 `email.send` 토픽의 leader를 확인한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic email.send
```

예를 들어 아래처럼 보였다고 가정하자.

```text
Topic: email.send  Partition: 0  Leader: 1  Replicas: 1,2,3  Isr: 1,2,3
```

이 경우 1번 Broker가 leader이고, 2번과 3번 Broker는 follower replica를 가지고 있다고 해석할 수 있다.

---

## 3. leader가 있는 Broker를 종료해보기

이제 leader가 있는 1번 Broker에 장애가 난 상황을 가정한다.

포그라운드에서 실행 중이었다면 `Ctrl + C`로 종료한다.

```bash
bin/kafka-server-start.sh config/server.properties
```

처럼 실행했던 Broker라면 해당 터미널에서 종료하면 된다.

Apache Kafka 공식 운영 문서는 broker가 종료되거나 장애가 나면, cluster가 이를 감지하고 그 broker가 leader이던 partition들의 새 leader를 자동으로 선출한다고 설명한다. [3]

---

## 4. 다시 leader를 조회해보기

1번 Broker가 종료됐으므로, 살아 있는 다른 Broker 주소로 토픽 정보를 조회해야 한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:19092 \
  --describe \
  --topic email.send
```

이제 예를 들어 아래처럼 보일 수 있다.

```text
Topic: email.send  Partition: 0  Leader: 2  Replicas: 1,2,3  Isr: 2,3
```

이 출력은 아래 의미를 가진다.

1. `Leader: 2`
   - 원래 1번 Broker가 leader였는데, 이제 2번 Broker가 새 leader가 됐다.
2. `Replicas: 1,2,3`
   - 원래 복제본 배치 자체는 여전히 1, 2, 3번 Broker를 대상으로 한다.
3. `Isr: 2,3`
   - 1번 Broker는 현재 동기화 상태 replica 집합에서 빠졌다.

Apache Kafka 공식 모니터링 문서는 broker가 내려가면 ISR이 줄어들고(shrink), broker가 다시 올라와 충분히 따라잡으면 ISR이 다시 늘어난다(expand)고 설명한다. [4]

즉, 여기서 `Isr`에 1번 Broker가 빠졌다는 것은 아래 가능성 중 하나를 의미한다.

1. Broker가 실제로 종료됐다.
2. 네트워크 문제가 생겼다.
3. leader 데이터를 아직 충분히 따라잡지 못했다.

---

## 5. Kafka 서버 1대가 고장나도 메시지를 넣고 읽을 수 있을까?

이제 살아 있는 Broker 주소를 사용해 producer와 consumer를 실행해본다.

메시지 넣기:

```bash
bin/kafka-console-producer.sh \
  --bootstrap-server localhost:19092 \
  --topic email.send
```

입력:

```text
test
```

메시지 조회:

```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:19092 \
  --topic email.send \
  --from-beginning
```

정상적으로 `test`가 들어가고 읽히면, 1대 장애가 났어도 cluster 전체가 바로 멈추지는 않았다는 뜻이다.

이게 가능한 이유는 아래와 같다.

1. replication factor가 3으로 잡혀 있다.
2. leader가 죽었을 때 ISR 안의 다른 follower가 새 leader가 됐다.
3. producer와 consumer는 살아 있는 Broker를 bootstrap 주소로 사용해 계속 동작할 수 있다.

단, 이것은 "Kafka 서버 1대가 죽어도 무조건 아무 문제 없다"는 뜻은 아니다.
replication factor, ISR 상태, `min.insync.replicas`, producer `acks` 설정에 따라 실제 내구성과 가용성은 달라질 수 있다.

이번 실습에서는 입문 관점에서 "Broker 1대 장애 시에도 기본적인 read/write가 계속 가능한 구조"만 확인하면 충분하다.

---

## 6. 왜 여러 대를 운영할까?

Kafka 서버를 1대만 운영하면 그 1대가 leader이자 follower 복제 대상 전부를 동시에 맡게 되므로, 그 서버가 죽는 순간 해당 데이터 처리가 멈출 수 있다.

반면 Kafka 서버를 여러 대 운영하면,

```text
한 대 장애 = 나머지 replica가 leader를 이어받을 여지
```

가 생긴다.

Apache Kafka 공식 소개 문서도 Kafka cluster가 fault-tolerant하며, 어떤 서버가 실패해도 다른 서버가 계속 서비스를 이어갈 수 있도록 설계됐다고 설명한다. [5]

물론 3대 모두 동시에 멈추거나, leader가 죽었는데 ISR에 선출 가능한 replica가 전혀 없으면 가용성이 깨질 수 있다.

즉, 서버 수를 늘린다고 장애가 완전히 사라지는 것은 아니지만, 단일 장애 지점을 줄일 수는 있다.

---

## 7. 종료했던 Broker를 다시 복구해보기

이제 아까 종료했던 Broker를 다시 실행한다.

1번 Broker를 내렸다면 아래처럼 다시 올린다.

```bash
bin/kafka-server-start.sh config/server.properties
```

Broker가 다시 올라왔다고 해서 즉시 ISR에 복귀하는 것은 아니다.
follower replica는 leader의 로그를 다시 충분히 따라잡아야 한다.

Kafka 공식 모니터링 문서는 내려갔던 broker가 다시 올라오면, replica가 fully caught up 된 뒤 ISR이 다시 확장된다고 설명한다. [4]

---

## 8. 복구가 끝났는지 확인하기

다시 토픽 세부 정보를 확인한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:19092 \
  --describe \
  --topic email.send
```

예를 들어 아래처럼 보이면

```text
Topic: email.send  Partition: 0  Leader: 2  Replicas: 1,2,3  Isr: 1,2,3
```

1번 Broker가 다시 ISR에 합류했다는 뜻이다.

이 상태는 아래를 의미한다.

1. 1번 Broker 프로세스가 다시 살아났다.
2. leader가 가진 데이터를 1번 Broker가 다시 따라잡았다.
3. 현재 1, 2, 3번 Broker가 모두 in-sync 상태다.

추가로 아까 장애가 났던 1번 Broker 주소로도 메시지 조회가 되는지 볼 수 있다.

```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic email.send \
  --from-beginning
```

`test` 메시지가 정상적으로 조회된다면, 복구된 Broker도 metadata와 replica 동기화 측면에서 다시 cluster에 합류했다고 해석할 수 있다.

---

## 정리

Kafka에서 leader partition이 있는 Broker에 장애가 나면, ISR 안에 있던 follower replica 중 하나가 새 leader로 승격될 수 있다.

핵심만 다시 정리하면 아래와 같다.

1. 장애 전에는 `Leader: 1`, `Isr: 1,2,3`처럼 보일 수 있다.
2. 1번 Broker를 내리면 `Leader: 2`, `Isr: 2,3`처럼 바뀔 수 있다.
3. 살아 있는 Broker 주소로는 계속 메시지를 넣고 읽을 수 있다.
4. 내려갔던 Broker가 복구되고 충분히 catch-up 되면 `Isr: 1,2,3`으로 다시 확장될 수 있다.

즉, Kafka 서버를 여러 대 운영하면 특정 Broker 장애가 전체 서비스 중단으로 바로 이어지지 않도록 완충할 수 있다.

---

## 출처

1. Apache Kafka, "Introduction", https://kafka.apache.org/082/getting-started/introduction/
2. Apache Kafka, "Design - Replication and ISR", https://kafka.apache.org/090/design/design/
3. Apache Kafka, "Basic Kafka Operations - Graceful shutdown", https://kafka.apache.org/41/operations/basic-kafka-operations/
4. Apache Kafka, "Monitoring - ISR shrink and expand", https://kafka.apache.org/082/operations/monitoring/
5. Apache Kafka, "Documentation - Introduction", https://kafka.apache.org/documentation/
