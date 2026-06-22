---
title: Kafka Three Node Setup
category: k
date: 2026-06-23 00:00:00 +0900
tags: [kafka, kraft, cluster, controller, broker, replication]
---

## 1. 왜 Kafka 서버를 3대로 구성할까?

이전 글에서 Kafka Node 1대만 운영하면 그 Node에 장애가 나는 순간 서비스 전체에 영향을 줄 수 있다고 설명했다.

Kafka KRaft 문서는 Controller quorum을 보통 3대 또는 5대로 두며, 3대일 때는 1대 장애를 견딜 수 있다고 설명한다. [1]

즉, 입문 단계에서는 아래처럼 이해하면 된다.

```text
Kafka 서버 1대 = 단일 장애 지점이 되기 쉽다
Kafka 서버 3대 = 일부 장애가 나도 계속 동작할 여지가 커진다
```

실무에서는 보통 Kafka Node를 각각 다른 서버에 따로 배치한다.
하지만 실습에서는 비용과 편의를 위해 하나의 EC2 인스턴스 안에서 Kafka 프로세스 3개를 띄워 3개 Node처럼 구성할 수 있다.

이 방식은 실습용이다.
Kafka 공식 문서는 `broker,controller`를 한 프로세스에 함께 두는 combined mode가 개발 환경에는 단순하지만, 중요 운영 환경에는 권장되지 않는다고 설명한다. [1]

---

## 2. 이번 실습의 구조

이번 글에서는 하나의 EC2 인스턴스 안에서 Kafka Node 3개를 띄운다.

구조는 아래와 같다.

```text
Node 1 -> Broker 9092 / Controller 9093
Node 2 -> Broker 19092 / Controller 19093
Node 3 -> Broker 29092 / Controller 29093
```

각 Node는 아래 항목이 달라야 한다.

| 항목 | Node마다 달라야 하는 이유 |
|---|---|
| `node.id` | Kafka Node를 구분하기 위해 필요 |
| `listeners` 포트 | 같은 서버에서 동시에 띄우므로 포트 충돌 방지 |
| `log.dirs` | 각 Node의 데이터 저장 경로를 분리해야 함 |
| 설정 파일명 | Node별 설정을 따로 관리해야 함 |

이번 실습은 Kafka 4.x KRaft 기준으로 작성한다.

---

## 3. KRaft 기준으로 주의할 점

Kafka KRaft에서는 Kafka 서버가 `broker`, `controller`, `broker,controller` 역할 중 하나를 가질 수 있다. [1]

이번 글은 실습 단순화를 위해 각 Node를 combined mode로 구성한다.

즉, 각 설정 파일에 아래 값이 들어간다고 가정한다.

```text
process.roles=broker,controller
```

또한 Kafka 최신 문서는 dynamic quorum을 사용할 때 `controller.quorum.voters` 대신 `controller.quorum.bootstrap.servers`를 사용하고, Node를 추가할 때는 `kafka-storage.sh format --no-initial-controllers`와 `kafka-metadata-quorum.sh add-controller`를 사용한다고 설명한다. [2]

---

## 4. 첫 번째 설정 파일 수정하기

먼저 Kafka 설정 디렉터리로 이동한다.

```bash
cd kafka_2.13-4.0.0/config
```

그리고 `server.properties`를 수정한다.

핵심 항목은 아래와 같다.

```properties
process.roles=broker,controller
node.id=1
controller.listener.names=CONTROLLER
listener.security.protocol.map=PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT
controller.quorum.bootstrap.servers={EC2 Public IP}:9093,{EC2 Public IP}:19093,{EC2 Public IP}:29093
listeners=PLAINTEXT://:9092,CONTROLLER://:9093
advertised.listeners=PLAINTEXT://{EC2 Public IP}:9092
log.dirs=/tmp/kafka-logs-1
```

여기서 중요한 점은 아래이다.

1. `node.id=1`
2. `listeners`는 실제 바인딩할 포트
3. `advertised.listeners`는 외부 클라이언트가 접속할 Broker 주소
4. `log.dirs`는 Node 1 전용 경로

Kafka 공식 Listener 문서는 KRaft combined mode에서 `listeners`에 broker와 controller listener를 둘 다 포함해야 한다고 설명한다. [3]
반면 클라이언트는 broker listener로 접속해야 하므로, 실습에서는 `advertised.listeners`에 broker listener만 두는 편이 안전하다. [3][4]

또한 EC2 Public IP가 바뀌었다면 `{EC2 Public IP}` 부분도 새 IP로 전부 바꿔야 한다.
예를 들어 기존 값이 `192.168.219.163`이었는데 현재 `192.168.219.78`이라면 새 IP로 맞춰야 한다.

---

## 5. 설정 파일 복사하기

이제 첫 번째 설정 파일을 복사해 Node 2, Node 3용 설정 파일을 만든다.

```bash
cp server.properties server2.properties
cp server.properties server3.properties
```

---

## 6. 두 번째, 세 번째 설정 파일 수정하기

`server2.properties`는 아래처럼 바꾼다.

```properties
process.roles=broker,controller
node.id=2
controller.listener.names=CONTROLLER
listener.security.protocol.map=PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT
controller.quorum.bootstrap.servers={EC2 Public IP}:9093,{EC2 Public IP}:19093,{EC2 Public IP}:29093
listeners=PLAINTEXT://:19092,CONTROLLER://:19093
advertised.listeners=PLAINTEXT://{EC2 Public IP}:19092
log.dirs=/tmp/kafka-logs-2
```

`server3.properties`는 아래처럼 바꾼다.

```properties
process.roles=broker,controller
node.id=3
controller.listener.names=CONTROLLER
listener.security.protocol.map=PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT
controller.quorum.bootstrap.servers={EC2 Public IP}:9093,{EC2 Public IP}:19093,{EC2 Public IP}:29093
listeners=PLAINTEXT://:29092,CONTROLLER://:29093
advertised.listeners=PLAINTEXT://{EC2 Public IP}:29092
log.dirs=/tmp/kafka-logs-3
```

Node마다 반드시 달라야 하는 값은 아래이다.

```text
node.id
listeners 포트
advertised.listeners 포트
log.dirs
```

---

## 7. 첫 Node는 클러스터를 초기화하고, 나머지는 기존 클러스터에 붙이기

Kafka 디렉터리로 돌아간다.

```bash
cd ..
```

기존 Kafka가 떠 있다면 종료한다.

```bash
bin/kafka-server-stop.sh
```

먼저 Cluster ID를 만든다.

```bash
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
```

그리고 첫 번째 Node를 클러스터의 초기 controller로 format한다.

```bash
KAFKA_CONTROLLER_ID="$(bin/kafka-storage.sh random-uuid)"

bin/kafka-storage.sh format \
  -t $KAFKA_CLUSTER_ID \
  -c config/server.properties \
  --initial-controllers "1@localhost:9093:$KAFKA_CONTROLLER_ID"
```

Kafka와 Confluent 문서는 dynamic quorum에서 적어도 한 controller는 `--initial-controllers` 또는 `--standalone`으로 format해야 한다고 설명한다. [2][5]

그 다음 Node 2, Node 3은 기존 클러스터에 붙는 방식으로 format한다.

```bash
bin/kafka-storage.sh format \
  -t $KAFKA_CLUSTER_ID \
  -c config/server2.properties \
  --no-initial-controllers
```

```bash
bin/kafka-storage.sh format \
  -t $KAFKA_CLUSTER_ID \
  -c config/server3.properties \
  --no-initial-controllers
```

Kafka 공식 KRaft 문서는 기존 클러스터에 추가할 broker나 controller는 `--no-initial-controllers`로 format하라고 설명한다. [2]

---

## 8. Kafka Node 3대 실행하기

로그를 보기 쉽게 터미널 창을 3개 열고 각 Node를 포그라운드로 실행한다.

```bash
bin/kafka-server-start.sh config/server.properties
```

```bash
bin/kafka-server-start.sh config/server2.properties
```

```bash
bin/kafka-server-start.sh config/server3.properties
```

이렇게 하면 하나의 EC2 안에 Kafka Node 3개가 동시에 뜬다.

---

## 9. 포트가 잘 열렸는지 확인하기

새 터미널을 열고 Broker와 Controller 포트를 확인한다.

Broker 포트:

```bash
lsof -i:9092
lsof -i:19092
lsof -i:29092
```

Controller 포트:

```bash
lsof -i:9093
lsof -i:19093
lsof -i:29093
```

세 Node가 모두 잘 떠 있으면 각 포트에서 Kafka Java 프로세스를 확인할 수 있다.

---

## 10. 클러스터에 Controller 등록하기

Node 2와 Node 3은 format만 했다고 바로 quorum voter가 되지 않는다.
dynamic quorum에서는 따라잡기(catch-up)를 확인한 뒤 `add-controller`를 수행해야 한다. [5]

먼저 Node 2, Node 3을 시작한 뒤 replication 상태를 확인한다.

```bash
bin/kafka-metadata-quorum.sh \
  --bootstrap-server localhost:9092 \
  describe \
  --replication
```

Kafka/Confluent 문서는 새 controller가 active controller를 따라잡았는지 `describe --replication`으로 확인한 뒤 `add-controller`를 실행하라고 설명한다. [2][5]

그 다음 Node 2를 controller quorum에 추가한다.

```bash
bin/kafka-metadata-quorum.sh \
  --command-config config/server2.properties \
  --bootstrap-server localhost:9092 \
  add-controller
```

Node 3도 같은 방식으로 추가한다.

```bash
bin/kafka-metadata-quorum.sh \
  --command-config config/server3.properties \
  --bootstrap-server localhost:9092 \
  add-controller
```

---

## 11. Controller가 잘 등록됐는지 확인하기

아래 명령어로 quorum 상태를 확인한다.

```bash
bin/kafka-metadata-quorum.sh \
  --bootstrap-server localhost:9092 \
  describe \
  --status
```

출력에서 `CurrentVoters`를 확인한다.

```text
CurrentVoters: [ ... 3개 controller 정보 ... ]
```

`CurrentVoters`에 3개 Node 정보가 보이면 controller quorum이 3대로 구성된 것이다.

---

## 12. 실습에서 특히 조심할 점

이번 실습은 하나의 EC2 인스턴스에 Kafka Node 3개를 띄우는 구조라서 운영 환경과는 다르다.

주의할 점은 아래와 같다.

| 항목 | 이유 |
|---|---|
| 같은 서버 장애 | EC2 1대가 죽으면 Node 3개가 같이 죽는다 |
| IP 변경 | EC2 Public IP가 바뀌면 `controller.quorum.bootstrap.servers`, `advertised.listeners`를 다시 맞춰야 한다 |
| 포트 충돌 | 각 Node의 broker/controller 포트가 모두 달라야 한다 |
| 데이터 경로 분리 | `log.dirs`를 Node마다 다르게 줘야 한다 |

즉, 이 구조는 Kafka 3대 운영 연습을 위한 실습 구조이지, 실제 고가용성 자체를 완전히 보장하는 운영 구조는 아니다.

---

## 정리

Kafka Node를 3대로 구성하면 controller quorum을 3대로 만들어 일부 장애를 견딜 수 있는 구조를 연습할 수 있다.

이번 실습에서는 하나의 EC2 안에서 Node 3개를 combined mode로 띄웠다.
핵심은 아래와 같다.

1. Node마다 `node.id`, 포트, `log.dirs`를 다르게 설정한다.
2. 첫 Node는 `--initial-controllers`로 format한다.
3. 나머지 Node는 `--no-initial-controllers`로 format한다.
4. Node 2, Node 3을 시작한 뒤 `add-controller`로 quorum에 추가한다.
5. `describe --status`에서 `CurrentVoters`가 3개인지 확인한다.

다음 글에서는 이렇게 만든 Kafka 서버 3대가 실제로 잘 연동되는지 확인하는 과정을 이어서 다룬다.

---

## 출처

1. Apache Kafka, "KRaft - Process Roles and Controllers", https://kafka.apache.org/39/operations/kraft/
2. Apache Kafka, "KRaft - Formatting Brokers and New Controllers", https://kafka.apache.org/41/operations/kraft/
3. Apache Kafka, "Listener Configuration", https://kafka.apache.org/42/security/listener-configuration/
4. Apache Kafka, "Broker Configs - advertised.listeners", https://kafka.apache.org/41/configuration/broker-configs/
5. Confluent Documentation, "Configure and Monitor KRaft", https://docs.confluent.io/platform/current/kafka-metadata/config-kraft.html
