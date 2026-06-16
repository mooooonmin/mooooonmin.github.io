---
title: Kafka Produce Consume CLI
category: k
date: 2026-06-17 00:00:00 +0900
tags: [kafka, producer, consumer, cli, message]
---

## 1. Kafka에 메시지 넣기

Producer는 Kafka로 메시지를 보내는 역할을 한다.
실제 서비스에서는 Spring Boot 같은 백엔드 서버가 Producer 역할을 할 수 있다.

하지만 Kafka를 처음 배울 때는 백엔드 코드를 작성하지 않고 CLI 명령어로도 메시지를 넣어볼 수 있다.
이때 사용하는 명령어가 `kafka-console-producer.sh`이다.

Apache Kafka 공식 Quickstart도 콘솔 Producer 클라이언트를 실행해 Topic에 이벤트를 쓰는 예시를 제공한다. [1]

이번 글에서는 아래 흐름을 실습한다.

```text
Topic 생성 -> 메시지 넣기 -> 메시지 조회하기
```

Kafka 서버는 `localhost:9092`에서 실행 중이라고 가정한다.

---

## 2. 토픽 생성하기

먼저 메시지를 넣을 Topic을 만든다.

이번 글에서는 `email.send`라는 Topic을 사용한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic email.send
```

이미 같은 이름의 Topic이 있다면 다시 만들 필요는 없다.
Topic이 있는지 확인하려면 아래 명령어를 사용한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --list
```

출력에 `email.send`가 보이면 Topic이 준비된 것이다.

---

## 3. 특정 토픽에 메시지 넣기

Kafka에 넣는 메시지는 Key-Value 형태로 넣을 수도 있고, Key 없이 Value만 넣을 수도 있다.

처음에는 Key를 생략하고 Value만 넣는 방식으로 실습한다.

`email.send` Topic에 메시지를 넣으려면 아래 명령어를 실행한다.

```bash
bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic email.send
```

명령어를 실행하면 터미널이 입력을 기다리는 상태가 된다.
이때 메시지를 입력하고 Enter를 누르면 한 줄이 하나의 메시지로 Kafka에 들어간다.

```text
hello1
hello2
hello3
```

Apache Kafka 공식 Quickstart는 콘솔 Producer에서 기본적으로 입력한 각 줄이 Topic에 쓰이는 별도 이벤트가 된다고 설명한다. [1]

메시지를 모두 입력했다면 `Ctrl + C`를 눌러 입력 상태를 종료한다.

아무런 에러가 뜨지 않았다면 메시지가 Topic에 들어간 것이다.

---

## 4. Kafka에서 메시지 조회하기

Kafka에서 메시지를 조회할 때는 `kafka-console-consumer.sh`를 사용한다.

Apache Kafka 공식 Quickstart도 콘솔 Consumer 클라이언트를 실행해 생성한 이벤트를 읽는 예시를 제공한다. [2]

`email.send` Topic에 저장된 메시지를 처음부터 조회하려면 아래 명령어를 실행한다.

```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic email.send \
  --from-beginning
```

여기서 `--from-beginning`은 Topic에 저장된 처음 메시지부터 읽겠다는 의미이다.

앞에서 `hello1`, `hello2`, `hello3`을 넣었다면 아래처럼 출력된다.

```text
hello1
hello2
hello3
```

---

## 5. Consumer는 실시간으로 새 메시지도 읽는다

위 Consumer 명령어를 실행하면 기존 메시지를 출력한 뒤에도 명령어가 바로 종료되지 않는다.
새 메시지가 들어오는지 계속 기다리는 상태가 된다.

이 상태를 확인하려면 터미널 창을 하나 더 열고 Producer를 다시 실행한다.

```bash
bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic email.send
```

그리고 새 메시지를 입력한다.

```text
hello4
```

그러면 `kafka-console-consumer.sh`를 실행해둔 터미널에 `hello4`가 바로 출력된다.

Apache Kafka 공식 Quickstart도 Producer 터미널에서 이벤트를 추가로 작성하면 Consumer 터미널에 즉시 표시되는 것을 확인할 수 있다고 설명한다. [2]

---

## 6. Kafka는 메시지를 다시 읽을 수 있다

Kafka는 메시지를 읽는 순간 바로 제거하는 방식으로 이해하면 안 된다.

Apache Kafka 공식 Quickstart는 Kafka에 이벤트가 durable하게 저장되기 때문에 원하는 만큼 여러 Consumer가 여러 번 읽을 수 있다고 설명한다. [2]

이 특징을 확인하려면 Consumer 명령어를 다시 실행해보면 된다.

```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic email.send \
  --from-beginning
```

앞에서 넣었던 메시지가 다시 출력된다.

```text
hello1
hello2
hello3
hello4
```

만약 Kafka가 메시지를 읽는 순간 삭제하는 방식이라면, 같은 메시지를 다시 읽을 수 없어야 한다.
하지만 Kafka는 Topic에 저장된 메시지를 읽을 수 있게 해주는 구조이기 때문에 `--from-beginning`으로 처음부터 다시 조회할 수 있다.

---

## 7. 이번 글에서 사용한 명령어 정리

Topic을 생성한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic email.send
```

Producer로 메시지를 넣는다.

```bash
bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic email.send
```

메시지를 입력한다.

```text
hello1
hello2
hello3
```

Consumer로 메시지를 처음부터 조회한다.

```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic email.send \
  --from-beginning
```

새 터미널에서 Producer를 다시 실행하고 메시지를 추가한다.

```bash
bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic email.send
```

```text
hello4
```

Consumer 명령어를 다시 실행해 메시지를 다시 읽을 수 있는지 확인한다.

```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic email.send \
  --from-beginning
```

---

## 정리

Kafka에 메시지를 넣을 때는 `kafka-console-producer.sh`를 사용할 수 있다.
Kafka에서 메시지를 조회할 때는 `kafka-console-consumer.sh`를 사용할 수 있다.

`--from-beginning` 옵션을 사용하면 Topic에 저장된 처음 메시지부터 읽을 수 있다.
Kafka에 저장된 메시지는 읽는 순간 바로 제거되는 방식이 아니므로 같은 메시지를 다시 읽는 것도 가능하다.

지금까지는 Kafka에 메시지를 넣고, Topic에 들어있는 메시지를 처음부터 끝까지 읽는 방법을 배웠다.
실제 서비스에서는 여기서 더 나아가 어디까지 읽었는지 기억하고 다음 메시지부터 이어서 처리하는 방식이 필요하다.

---

## 출처

1. Apache Kafka, "Quickstart - Step 4: Write some events into the topic", https://kafka.apache.org/quickstart/
2. Apache Kafka, "Quickstart - Step 5: Read the events", https://kafka.apache.org/quickstart/
