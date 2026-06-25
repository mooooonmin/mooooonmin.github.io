---
title: Kafka Follower Write
category: k
date: 2026-06-25 00:00:00 +0900
tags: [kafka, leader, follower, producer, broker, replication]
---

## 1. 팔로워 파티션이 있는 노드에 메시지를 넣으면 어떻게 될까?

먼저 아래 설명을 떠올려보자.

```text
리더 파티션은 프로듀서나 컨슈머가 직접적으로 메시지를 쓰고 읽는 파티션이다.
팔로워 파티션은 프로듀서나 컨슈머가 직접적으로 메시지를 쓰고 읽지 않는다.
```

그러면 이런 의문이 생긴다.

```text
팔로워 파티션이 있는 노드 주소로 producer를 연결하면 메시지 전송이 실패하는 걸까?
```

결론부터 말하면, 보통은 실패하지 않는다.

다만 정확한 표현은 아래와 같다.

```text
프로듀서는 follower replica 자체에 직접 쓰는 것이 아니다.
아무 broker에 먼저 붙어도 metadata를 조회한 뒤 실제 leader broker로 전송한다.
```

Apache Kafka 공식 문서는 producer의 `bootstrap.servers`를 "초기 연결을 맺고 클러스터 전체 broker 정보를 발견하기 위한 주소 목록"이라고 설명한다. 이 목록은 전체 broker를 다 적을 필요가 없고, 클라이언트가 이후 전체 cluster metadata를 자동으로 관리한다고 설명한다. [1]

또한 Kafka 공식 설계 문서는 producer가 partition의 leader broker로 직접 데이터를 보낸다고 설명한다. 그리고 Kafka의 모든 노드는 어떤 broker가 leader인지에 대한 metadata 요청에 응답할 수 있다고 설명한다. [2]

즉, 입문자 관점에서는 아래처럼 이해하면 된다.

1. producer는 아무 broker 하나에 먼저 접속할 수 있다.
2. 그 broker에게 leader 정보가 누구인지 묻는다.
3. 실제 메시지는 leader broker로 보낸다.

---

## 2. 먼저 리더 파티션 확인하기

현재 `email.send` 토픽의 leader가 누구인지 먼저 확인한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic email.send
```

예를 들어 아래처럼 나왔다고 가정하자.

```text
Topic: email.send  Partition: 0  Leader: 1  Replicas: 1,2,3  Isr: 1,2,3
```

그러면 1번 Broker가 leader replica를 가지고 있고, 2번과 3번 Broker는 follower replica를 가지고 있다고 해석할 수 있다.

여기서 주의할 점은 "19092 포트에 붙는다 = follower replica에 직접 쓴다"가 아니라는 점이다.
19092는 2번 Broker에 접속하는 것이고, producer는 이 Broker를 통해 cluster metadata를 확인한 뒤 실제 leader로 메시지를 보낼 수 있다.

---

## 3. follower replica가 있는 Broker 주소로 producer 실행해보기

이제 2번 Broker 포트로 producer를 실행해본다.

```bash
bin/kafka-console-producer.sh \
  --bootstrap-server localhost:19092 \
  --topic email.send
```

그리고 메시지를 하나 입력한다.

```text
follower-message-1
```

메시지가 정상적으로 들어갔다면, 이것은 19092에 접속했기 때문이 아니라 19092를 통해 leader 정보를 알아낸 뒤 실제 leader broker로 전송됐기 때문이다.

Kafka 공식 설계 문서는 중간 라우팅 계층 없이 producer가 leader broker로 직접 데이터를 보낸다고 설명한다. [2]

---

## 4. 각 Broker 포트에서 메시지 조회해보기

이제 각 Broker 포트로 consumer를 실행해 메시지가 잘 보이는지 확인한다.

Node 1:

```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic email.send \
  --from-beginning
```

Node 2:

```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:19092 \
  --topic email.send \
  --from-beginning
```

Node 3:

```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:29092 \
  --topic email.send \
  --from-beginning
```

세 Broker 주소 어디로 조회하든 메시지가 보일 수 있다.

이 역시 "consumer가 follower replica에서 직접 읽었다"는 뜻으로 단순 해석하면 안 된다.
consumer도 `bootstrap-server`로 cluster metadata를 알아내고, partition leader에 연결해서 읽는 것이 기본 동작이다.

Apache Kafka 공식 문서는 consumer의 `bootstrap.servers`도 producer와 마찬가지로 초기 연결 및 전체 broker 발견용이라고 설명한다. [3]

---

## 5. 왜 이런 일이 가능한 걸까?

이 현상을 이해하려면 `bootstrap-server`의 의미를 정확히 구분해야 한다.

`bootstrap-server`는 아래 역할만 한다.

```text
클러스터에 처음 접속하기 위한 시작점
```

즉, 아래 두 문장은 다르다.

1. `19092`에 접속했다
2. `19092`에 있는 follower replica에 직접 썼다

실제로 맞는 설명은 1번이고, 2번은 틀린 설명이다.

Kafka 공식 producer 설정 문서는 `bootstrap.servers`가 초기 연결을 위한 목록이며, 클라이언트가 전체 broker를 자동으로 발견한다고 설명한다. [1]

Kafka 공식 설계 문서는 모든 쓰기가 leader로 간다고 설명한다. [4]

이 두 문장을 합치면 아래 결론이 나온다.

```text
bootstrap-server를 follower broker로 줘도,
producer는 metadata를 확인한 뒤 leader broker로 직접 쓴다.
```

---

## 6. 그럼 "팔로워 파티션에는 직접 메시지를 못 넣는다"는 말은 틀린 걸까?

틀린 말은 아니다.

다만 더 정확하게 표현해야 한다.

입문 설명을 아래처럼 보정하면 된다.

```text
팔로워 replica는 클라이언트가 직접 쓰기 대상으로 사용하는 replica가 아니다.
프로듀서는 leader replica로 쓰기를 수행하고,
팔로워 replica는 leader의 로그를 복제한다.
```

즉, producer가 follower broker 주소로 접속할 수는 있어도, follower replica 자체에 기록하는 것은 아니다.

Apache Kafka 공식 설계 문서는 non-failure 상황에서 partition마다 하나의 leader와 여러 follower가 있고, 모든 쓰기는 leader로 간다고 설명한다. [4]

---

## 7. 실습 결과를 어떻게 해석해야 할까?

이번 실습에서 확인한 것은 아래와 같다.

1. leader가 아닌 Broker 주소를 `bootstrap-server`로 줘도 producer 실행이 가능했다.
2. 메시지가 정상적으로 들어갔다.
3. 각 Broker 주소에서 메시지 조회가 가능했다.

이 결과를 정확히 해석하면 아래와 같다.

```text
producer는 follower replica에 직접 쓴 것이 아니다.
초기 접속은 follower broker로 했지만,
metadata를 통해 leader를 찾은 뒤 leader broker로 전송했다.
그 뒤 leader의 로그가 follower replica로 복제됐다.
```

---

## 정리

팔로워 파티션이 있는 노드 주소로 producer를 실행해도 메시지 전송은 보통 성공한다.

하지만 그것은 follower replica에 직접 쓴 것이 아니라, 해당 broker를 bootstrap 용도로 사용한 뒤 leader broker로 실제 쓰기가 수행되기 때문이다.

핵심만 다시 정리하면 아래와 같다.

1. `bootstrap-server`는 초기 접속점이다.
2. producer는 metadata를 조회해 leader broker를 찾는다.
3. 실제 쓰기는 leader replica로 간다.
4. follower replica는 leader의 데이터를 복제한다.
5. 따라서 follower broker 주소로 접속이 성공해도, follower replica에 직접 쓴 것은 아니다.

---

## 출처

1. Apache Kafka, "Producer Configs - bootstrap.servers", https://kafka.apache.org/43/configuration/producer-configs/
2. Apache Kafka, "Design - Load balancing and metadata", https://kafka.apache.org/43/design/design/
3. Apache Kafka, "Consumer Configs - bootstrap.servers", https://kafka.apache.org/41/configuration/consumer-configs/
4. Apache Kafka, "Design - Replication", https://kafka.apache.org/43/design/design/
