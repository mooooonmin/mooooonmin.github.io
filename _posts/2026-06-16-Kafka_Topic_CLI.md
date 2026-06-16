---
title: Kafka Topic CLI
category: k
date: 2026-06-16 00:00:00 +0900
tags: [kafka, topic, cli, kafka-topics, backend]
---

## 1. CLI를 활용한 Kafka 조작

이전 글에서는 백엔드 서버가 Kafka에 메시지를 넣고 읽는 흐름을 중심으로 설명했다.
그래서 Kafka는 Spring Boot 같은 백엔드 서버 코드로만 조작하는 것처럼 느껴질 수 있다.

하지만 Kafka는 CLI로도 조작할 수 있다.

Kafka를 설치하면 `bin` 디렉터리 안에 여러 명령어 도구가 들어있다.
Apache Kafka 공식 Operations 문서도 Kafka 배포판의 `bin/` 디렉터리 아래에 여러 도구가 있고, 인자 없이 실행하면 가능한 옵션 정보를 출력한다고 설명한다. [1]

이번 글에서는 그중 Topic을 만들고, 조회하고, 삭제할 때 사용하는 `kafka-topics.sh`를 다룬다.

```text
bin/kafka-topics.sh
```

이 글의 명령어는 Kafka 서버가 `localhost:9092`에서 실행 중이라고 가정한다.

---

## 2. Kafka 디렉터리로 이동하기

먼저 Kafka를 압축 해제한 디렉터리로 이동한다.

강의 환경에서 Kafka 디렉터리명이 `kafka_2.13-4.0.0`이라면 아래처럼 이동하면 된다.

```bash
cd kafka_2.13-4.0.0
```

Apache Kafka 공식 Quickstart는 최신 릴리스 예시로 `kafka_2.13-4.3.0` 디렉터리를 사용한다. [2]
따라서 실제로는 본인이 다운로드한 Kafka 버전에 맞는 디렉터리명으로 이동하면 된다.

예를 들어 설치한 버전이 다르면 아래처럼 디렉터리명이 달라질 수 있다.

```bash
cd kafka_2.13-4.3.0
```

중요한 점은 `bin/kafka-topics.sh` 파일이 있는 Kafka 설치 디렉터리 안에서 명령어를 실행한다는 것이다.

---

## 3. 토픽 생성하기

토픽을 생성할 때는 `--create` 옵션을 사용한다.

기본 형식은 아래와 같다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server <Kafka 주소> \
  --create \
  --topic <토픽명>
```

여기서 각 옵션의 의미는 아래와 같다.

| 옵션 | 의미 |
|---|---|
| `--bootstrap-server` | 접속할 Kafka 서버 주소 |
| `--create` | 토픽을 생성하겠다는 의미 |
| `--topic` | 생성할 토픽 이름 |

예를 들어 `email.send`라는 토픽을 만들고 싶다면 아래처럼 입력한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic email.send
```

Apache Kafka 공식 Quickstart도 토픽을 생성할 때 `bin/kafka-topics.sh --create --topic ... --bootstrap-server localhost:9092` 형식의 명령어를 사용한다. [2]

정상적으로 생성되면 Kafka 안에 `email.send`라는 토픽이 만들어진다.

---

## 4. 토픽 전체 조회하기

Kafka에 어떤 토픽이 있는지 확인하려면 `--list` 옵션을 사용한다.

기본 형식은 아래와 같다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server <Kafka 주소> \
  --list
```

로컬 Kafka 서버에서 전체 토픽 목록을 조회하려면 아래처럼 입력한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --list
```

방금 `email.send` 토픽을 만들었다면 출력에 아래 값이 포함된다.

```text
email.send
```

Apache Kafka 공식 Quickstart도 토픽 목록을 확인할 때 `bin/kafka-topics.sh --list --bootstrap-server localhost:9092` 명령어를 사용한다. [3]

---

## 5. 특정 토픽 세부 정보 조회하기

특정 토픽의 세부 정보를 확인하려면 `--describe` 옵션을 사용한다.

기본 형식은 아래와 같다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server <Kafka 주소> \
  --describe \
  --topic <토픽명>
```

`email.send` 토픽의 세부 정보를 조회하려면 아래처럼 입력한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic email.send
```

출력에는 파티션 수, 복제 계수, 리더, 복제본 같은 정보가 포함될 수 있다.
Apache Kafka 공식 Quickstart도 `--describe` 명령어로 Topic의 partition count 같은 세부 정보를 확인할 수 있다고 설명한다. [2]

아직 입문 단계에서는 세부 정보가 정확히 무엇을 의미하는지 전부 외울 필요는 없다.
지금은 아래 정도만 기억하면 된다.

```text
--describe는 특정 토픽의 상세 정보를 조회하는 옵션이다.
```

---

## 6. 토픽 삭제하기

토픽을 삭제할 때는 `--delete` 옵션을 사용한다.

기본 형식은 아래와 같다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server <Kafka 주소> \
  --delete \
  --topic <토픽명>
```

`email.send` 토픽을 삭제하려면 아래처럼 입력한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic email.send
```

Apache Kafka 공식 Operations 문서도 토픽 삭제 예시로 `bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic ...` 형식을 보여준다. [1]

삭제가 잘 되었는지 확인하려면 다시 전체 토픽 목록을 조회한다.

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --list
```

목록에 `email.send`가 보이지 않으면 삭제된 것이다.

---

## 7. 명령어 흐름 정리

이번 글에서 사용한 명령어를 순서대로 정리하면 아래와 같다.

```bash
cd kafka_2.13-4.0.0
```

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic email.send
```

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --list
```

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic email.send
```

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic email.send
```

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --list
```

---

## 정리

Kafka Topic은 CLI로도 생성, 조회, 삭제할 수 있다.

Topic을 다룰 때 사용하는 명령어는 `bin/kafka-topics.sh`이다.
토픽 생성은 `--create`, 전체 조회는 `--list`, 세부 정보 조회는 `--describe`, 삭제는 `--delete` 옵션을 사용한다.

이번 글에서는 Kafka 서버가 `localhost:9092`에서 실행 중이라는 전제로 실습했다.

---

## 출처

1. Apache Kafka, "Basic Kafka Operations", https://kafka.apache.org/43/operations/basic-kafka-operations/
2. Apache Kafka, "Quickstart - Step 3: Create a topic to store your events", https://kafka.apache.org/quickstart/
3. Apache Kafka, "Quick Start - Step 3: Create a topic", https://kafka.apache.org/26/getting-started/quickstart/
