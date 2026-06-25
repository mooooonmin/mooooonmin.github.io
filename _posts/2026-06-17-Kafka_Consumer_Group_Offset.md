---
title: Kafka Consumer Group Offset
category: k
date: 2026-06-17 00:00:10 +0900
tags: [kafka, consumer-group, offset, consumer, cli]
---

## 1. 메시지를 어디까지 읽었는지 기억하기

`kafka-console-consumer.sh`에 `--from-beginning` 옵션을 붙이면 Topic에 있는 메시지를 처음부터 읽을 수 있다.

```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic email.send \
  --from-beginning
```

하지만 실제 서비스에서는 매번 처음부터 메시지를 읽으면 안 된다.
이미 처리한 메시지를 다시 처리하면 이메일이 중복 발송되거나 주문 처리 로직이 중복 실행될 수 있기 때문이다.

그래서 Kafka에서는 Consumer Group과 Offset을 활용해 어디까지 읽었는지를 관리한다.

Apache Kafka 공식 Operations 문서는 `kafka-consumer-groups.sh` 도구로 Consumer Group 안의 Consumer 위치와 log 끝에서 얼마나 뒤처져 있는지를 확인할 수 있다고 설명한다. [1]

---

## 2. 용어 정리

이번 글에서 사용할 용어는 아래와 같다.

| 용어 | 의미 |
|---|---|
| Consumer | Kafka의 메시지를 읽고 처리하는 주체 |
| Consumer Group | 1개 이상의 Consumer를 하나의 그룹으로 묶은 단위 |
| Offset | Partition 안에서 메시지의 위치를 나타내는 번호 |
| CURRENT-OFFSET | Consumer Group이 다음에 읽을 위치로 볼 수 있는 현재 offset |

Offset은 0부터 시작한다.
다만 정확히 말하면 Offset은 Topic 전체에서 하나만 증가하는 번호가 아니라 Partition 안에서 증가하는 번호이다.

입문 실습에서는 이해를 쉽게 하기 위해 `email.send` Topic에 Partition이 1개 있다고 생각하고 설명한다.

```text
offset 0 -> hello1
offset 1 -> hello2
offset 2 -> hello3
offset 3 -> hello4
```

이 상태에서 Consumer Group이 `hello1`부터 `hello4`까지 읽었다면 다음에 읽을 위치는 offset 4가 된다.

```text
CURRENT-OFFSET = 4
```

---

## 3. Consumer Group을 지정해서 메시지 읽기

Consumer Group을 지정하려면 `kafka-console-consumer.sh`에 `--group` 옵션을 추가한다.

```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic email.send \
  --from-beginning \
  --group email-send-group
```

여기서 `email-send-group`은 Consumer Group 이름이다.

만약 `email-send-group`이라는 Consumer Group이 기존에 없다면 새 Consumer Group으로 동작한다.
그리고 이 Consumer Group은 메시지를 어디까지 읽었는지를 offset으로 기록한다.

`--from-beginning`은 이 Consumer Group에 아직 기록된 offset이 없을 때 처음 메시지부터 읽게 하는 옵션으로 이해하면 된다.
이미 이 Consumer Group에 기록된 offset이 있다면 그 위치부터 이어서 읽는다.

메시지가 출력되면 바로 종료하지 말고 잠시 기다린 뒤 `Ctrl + C`로 종료한다.
Console Consumer는 offset을 주기적으로 commit할 수 있으므로, 너무 빨리 종료하면 offset 조회 결과가 기대와 다를 수 있다. [3]

---

## 4. Consumer Group 전체 조회하기

생성된 Consumer Group 목록을 확인하려면 `kafka-consumer-groups.sh`에 `--list` 옵션을 사용한다.

```bash
bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --list
```

정상적으로 Consumer Group이 만들어졌다면 목록에 아래 값이 보인다.

```text
email-send-group
```

Apache Kafka 공식 Operations 문서도 Consumer Group 목록을 조회할 때 `kafka-consumer-groups.sh --bootstrap-server ... --list` 명령어를 사용한다. [1]

---

## 5. Consumer Group 세부 정보 조회하기

특정 Consumer Group의 세부 정보를 확인하려면 `--describe` 옵션을 사용한다.

```bash
bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group email-send-group \
  --describe
```

출력에는 아래와 같은 항목이 포함된다.

```text
TOPIC       PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
email.send  0          4               4               0
```

각 항목은 아래처럼 이해하면 된다.

| 항목 | 의미 |
|---|---|
| `TOPIC` | Consumer Group이 읽는 Topic |
| `PARTITION` | Topic 안의 Partition 번호 |
| `CURRENT-OFFSET` | Consumer Group이 현재 기록해둔 offset 위치 |
| `LOG-END-OFFSET` | 해당 Partition의 마지막 다음 위치 |
| `LAG` | 아직 처리하지 못한 메시지 개수 |

Apache Kafka 공식 Operations 문서는 Consumer Group 위치를 확인하는 출력 예시로 `CURRENT-OFFSET`, `LOG-END-OFFSET`, `LAG` 항목을 보여준다. [1]

`CURRENT-OFFSET`이 4이고 `LOG-END-OFFSET`도 4라면, 현재 저장된 메시지를 모두 읽은 상태로 이해할 수 있다.

```text
offset 0 -> hello1 읽음
offset 1 -> hello2 읽음
offset 2 -> hello3 읽음
offset 3 -> hello4 읽음

CURRENT-OFFSET = 4
```

즉, 다음에 읽을 메시지가 있다면 offset 4부터 읽게 된다.

---

## 6. 메시지를 추가로 넣기

이제 Consumer Group이 안 읽은 메시지부터 읽는지 확인해보자.

먼저 `email.send` Topic에 새 메시지를 하나 넣는다.

```bash
bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic email.send
```

Producer 입력 상태가 되면 아래 메시지를 입력한다.

```text
hello5
```

입력을 마쳤다면 `Ctrl + C`로 종료한다.

이제 Topic의 메시지는 아래처럼 있다고 볼 수 있다.

```text
offset 0 -> hello1
offset 1 -> hello2
offset 2 -> hello3
offset 3 -> hello4
offset 4 -> hello5
```

---

## 7. 같은 Consumer Group으로 다시 읽기

이전에 사용했던 Consumer Group으로 다시 메시지를 읽어본다.

```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic email.send \
  --group email-send-group \
  --from-beginning
```

이때 이미 `email-send-group`은 offset 4까지 위치를 기록해둔 상태이다.
따라서 `hello1`부터 `hello4`까지 다시 출력하지 않고, 새로 들어온 `hello5`부터 읽는다.

```text
hello5
```

이것이 Consumer Group과 Offset을 사용하는 이유이다.

Consumer Group은 어디까지 읽었는지를 기억하고, 다음에 실행될 때 아직 처리하지 않은 메시지부터 이어서 처리할 수 있다.

---

## 8. CURRENT-OFFSET 다시 확인하기

`hello5`까지 읽은 뒤 Consumer Group 세부 정보를 다시 조회한다.

```bash
bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group email-send-group \
  --describe
```

예상 출력은 아래와 비슷하다.

```text
TOPIC       PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
email.send  0          5               5               0
```

`hello5`는 offset 4인 메시지이다.
이 메시지를 읽었기 때문에 다음에 읽을 위치는 offset 5가 된다.

```text
offset 0 -> hello1 읽음
offset 1 -> hello2 읽음
offset 2 -> hello3 읽음
offset 3 -> hello4 읽음
offset 4 -> hello5 읽음

CURRENT-OFFSET = 5
```

이제 이 Consumer Group은 다음 메시지가 들어오면 offset 5부터 읽는다.

---

## 9. 왜 Consumer Group이 필요한가?

실제 서비스에서는 똑같은 요청을 중복해서 처리하면 문제가 생길 수 있다.

예를 들어 이메일 발송 메시지를 매번 처음부터 읽으면 이미 보낸 이메일을 다시 보낼 수 있다.
주문 처리 메시지를 중복해서 처리하면 주문 상태가 꼬일 수도 있다.

그래서 서비스에서는 보통 Consumer Group을 지정해서 메시지를 읽는다.

Consumer Group을 사용하면 Kafka가 해당 그룹의 처리 위치를 offset으로 관리할 수 있다.
Consumer가 재시작되더라도 마지막으로 commit된 offset을 기준으로 이어서 처리할 수 있다. [3]

---

## 정리

Consumer Group은 1개 이상의 Consumer를 하나의 그룹으로 묶은 단위이다.
Offset은 Partition 안에서 메시지의 위치를 나타내는 번호이다.

Consumer Group은 어디까지 메시지를 읽었는지를 offset으로 기록한다.
이 덕분에 Consumer Group에 속한 Consumer는 이미 처리한 메시지를 계속 처음부터 다시 읽지 않고, 다음 메시지부터 이어서 처리할 수 있다.

Consumer Group 목록 조회는 `kafka-consumer-groups.sh --list`를 사용한다.
Consumer Group의 offset 상태 조회는 `kafka-consumer-groups.sh --describe --group <그룹명>`을 사용한다.

---

## 출처

1. Apache Kafka, "Basic Kafka Operations - Checking consumer position / Managing consumer groups", https://kafka.apache.org/41/operations/basic-kafka-operations/
2. Apache Kafka, "Introduction - Main Concepts and Terminology", https://kafka.apache.org/intro/
3. Confluent Documentation, "Kafka Consumer - Offset management configuration", https://docs.confluent.io/platform/current/clients/consumer.html
