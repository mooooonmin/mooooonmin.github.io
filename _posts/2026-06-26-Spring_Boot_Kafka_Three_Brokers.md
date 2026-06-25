---
title: Spring Boot Kafka Three Brokers
category: s
date: 2026-06-26 00:00:10 +0900
tags: [spring-boot, kafka, broker, bootstrap-servers, producer, consumer]
---

## 1. Spring Boot에서 Kafka 서버 3대를 어떻게 연결할까?

Spring Boot에서 Kafka를 사용할 때 핵심은 Kafka broker 주소를 하나만 넣지 않고 여러 개 넣는 것이다.

Spring Boot 공식 문서는 Kafka 설정이 `spring.kafka.*` 속성으로 제어되며, `spring.kafka.bootstrap-servers`를 통해 Kafka 서버 주소를 지정한다고 설명한다. [1]

Apache Kafka 공식 문서는 `bootstrap.servers`를 초기 연결을 맺고 cluster 전체 broker를 발견하기 위한 주소 목록이라고 설명한다. 또한 resilience를 위해 하나보다 많은 server를 넣는 것을 권장한다고 설명한다. [2][3]

즉, Spring Boot에서 Kafka 서버 3대를 연결할 때 핵심은 아래 한 줄이다.

```yaml
spring:
  kafka:
    bootstrap-servers:
      - {Kafka 서버 IP 주소}:9092
      - {Kafka 서버 IP 주소}:19092
      - {Kafka 서버 IP 주소}:29092
```

이렇게 해두면 일부 broker가 내려가더라도 클라이언트가 남아 있는 broker에 붙어 cluster metadata를 다시 확인할 수 있다.

---

## 2. Producer와 Consumer에 공통으로 필요한 설정

Spring Boot에서는 보통 producer와 consumer가 같은 `spring.kafka.bootstrap-servers` 설정을 공통으로 사용한다.

즉, "Producer용 bootstrap-servers"와 "Consumer용 bootstrap-servers"를 따로 적는 것이 아니라, 아래처럼 공통 설정으로 두는 것이 기본이다.

```yaml
server:
  port: 0

spring:
  kafka:
    bootstrap-servers:
      - {Kafka 서버 IP 주소}:9092
      - {Kafka 서버 IP 주소}:19092
      - {Kafka 서버 IP 주소}:29092
```

여기서 `server.port: 0`은 Spring Boot 서버 포트를 랜덤으로 띄우겠다는 뜻이다.
Kafka와 직접 관련된 설정은 아니지만, producer 서버와 consumer 서버를 여러 개 동시에 띄우는 실습에서는 자주 사용한다.

---

## 3. Producer 서버 설정 예시

Producer 서버는 최소한 아래처럼 설정할 수 있다.

```yaml
server:
  port: 0

spring:
  kafka:
    bootstrap-servers:
      - {Kafka 서버 IP 주소}:9092
      - {Kafka 서버 IP 주소}:19092
      - {Kafka 서버 IP 주소}:29092
```

실무에서는 여기에 필요에 따라 아래 설정이 추가될 수 있다.

1. `acks`
2. `retries`
3. `delivery-timeout-ms`
4. `request-timeout-ms`
5. serializer 설정

하지만 입문 단계에서는 broker 주소 여러 개를 넣는 것이 가장 중요하다.

Apache Kafka 공식 producer 문서는 `bootstrap.servers`가 초기 접속점일 뿐이며, 클라이언트는 이후 cluster 전체 broker 정보를 자동으로 관리한다고 설명한다. [2]

즉, producer는 3개 주소 중 하나에 먼저 붙고, 그 뒤 실제 leader broker 정보를 알아내서 메시지를 전송한다.

---

## 4. Consumer 서버 설정 예시

Consumer 서버는 보통 broker 주소와 함께 consumer 관련 설정을 추가한다.

```yaml
server:
  port: 0

spring:
  kafka:
    bootstrap-servers:
      - {Kafka 서버 IP 주소}:9092
      - {Kafka 서버 IP 주소}:19092
      - {Kafka 서버 IP 주소}:29092
    consumer:
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      auto-offset-reset: earliest
```

이 설정의 의미는 아래와 같다.

| 설정 | 의미 |
|---|---|
| `bootstrap-servers` | Kafka cluster에 처음 접속하기 위한 broker 주소 목록 |
| `key-deserializer` | key를 문자열로 역직렬화 |
| `value-deserializer` | value를 문자열로 역직렬화 |
| `auto-offset-reset: earliest` | 저장된 offset이 없을 때 가장 앞 메시지부터 읽기 |

Apache Kafka 공식 consumer 문서도 `bootstrap.servers`를 cluster 초기 접속용 broker 목록이라고 설명하며, resilience를 위해 여러 broker를 넣는 것을 권장한다. [3]

---

## 5. 왜 broker 주소를 3개 다 넣는 것이 좋을까?

예를 들어 아래처럼 1개만 넣었다고 해보자.

```yaml
spring:
  kafka:
    bootstrap-servers:
      - {Kafka 서버 IP 주소}:9092
```

이 경우 9092 broker가 내려간 시점에, 애플리케이션이 처음 연결을 맺거나 재연결해야 하는 순간 실패할 가능성이 커진다.

반면 아래처럼 여러 개를 넣어두면

```yaml
spring:
  kafka:
    bootstrap-servers:
      - {Kafka 서버 IP 주소}:9092
      - {Kafka 서버 IP 주소}:19092
      - {Kafka 서버 IP 주소}:29092
```

클라이언트는 남아 있는 다른 broker로 bootstrap을 시도할 수 있다.

Apache Kafka 공식 producer/consumer 설정 문서는 공통적으로

1. 이 목록은 전체 broker를 다 넣을 필요는 없지만,
2. 하나보다 많은 server를 넣는 것을 권장하고,
3. order는 중요하지 않다고 설명한다. [2][3]

즉, 3개 broker를 운용하고 있다면 Spring Boot 설정에도 3개를 같이 넣는 편이 가장 자연스럽다.

---

## 6. 일부 Kafka 서버가 중단돼도 왜 동작할 수 있을까?

이유는 두 단계로 나눠서 이해하면 된다.

### 6-1. 초기 접속 단계

`bootstrap-servers`에 여러 주소가 있으므로, 특정 broker가 내려가도 다른 broker로 접속을 시도할 수 있다.

### 6-2. 실제 메시지 송수신 단계

producer와 consumer는 cluster metadata를 바탕으로 어느 broker가 leader인지 확인한 뒤 실제 read/write를 수행한다.

즉, 아래처럼 이해하면 된다.

```text
Spring Boot -> 여러 bootstrap broker 중 하나에 접속
Kafka client -> cluster metadata 조회
Kafka client -> 실제 leader broker와 통신
```

그래서 broker 1대가 중단돼도 cluster 전체가 살아 있고, ISR과 leader election이 정상적으로 동작하는 상황이라면 Spring Boot 애플리케이션도 계속 Kafka를 사용할 수 있다.

다만 이것은 cluster 자체가 정상적으로 고가용성 구성을 갖추고 있다는 전제가 필요하다.

예를 들어 아래 조건들이 중요하다.

1. replication factor
2. ISR 상태
3. leader election 가능 여부
4. 살아 있는 broker 수

즉, Spring Boot 설정만 여러 개 적는다고 자동으로 고가용성이 완성되는 것은 아니다.
Kafka cluster 자체가 제대로 구성되어 있어야 한다.

---

## 7. Producer와 Consumer 설정을 따로 나눠 적어야 할까?

입문 단계에서는 보통 공통 `spring.kafka.bootstrap-servers`를 두고, producer/consumer 전용 설정만 하위에 나누는 구조가 가장 깔끔하다.

예를 들어 아래처럼 쓰면 된다.

```yaml
server:
  port: 0

spring:
  kafka:
    bootstrap-servers:
      - {Kafka 서버 IP 주소}:9092
      - {Kafka 서버 IP 주소}:19092
      - {Kafka 서버 IP 주소}:29092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.apache.kafka.common.serialization.StringSerializer
    consumer:
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      auto-offset-reset: earliest
```

이 구조의 장점은 아래와 같다.

1. broker 주소를 한 군데에서 관리할 수 있다.
2. producer/consumer 공통 설정과 개별 설정이 분리된다.
3. 설정 파일이 덜 중복된다.

Spring Boot 공식 문서도 `spring.kafka.*` 하위 속성으로 Kafka 설정을 관리한다고 설명한다. [1]

---

## 정리

Spring Boot에서 Kafka 서버 3대를 연결할 때 가장 중요한 설정은 `spring.kafka.bootstrap-servers`에 broker 주소를 여러 개 넣는 것이다.

핵심만 다시 정리하면 아래와 같다.

1. `spring.kafka.bootstrap-servers`에 3개 broker 주소를 넣는다.
2. producer와 consumer는 이 주소 목록을 초기 접속점으로 사용한다.
3. 실제 송수신은 metadata를 바탕으로 leader broker와 이뤄진다.
4. 일부 broker가 내려가도 남은 broker로 bootstrap이 가능할 수 있다.
5. 다만 Kafka cluster 자체의 replication, ISR, leader election 구성이 정상이어야 한다.

즉, Spring Boot에서 Kafka 서버 3대를 연결하는 방법은 복잡하지 않다.
공통 bootstrap 서버 목록을 정확히 적고, producer/consumer 개별 설정만 필요한 만큼 추가하면 된다.

---

## 출처

1. Spring Boot Reference, "Apache Kafka Support", https://docs.spring.io/spring-boot/reference/messaging/kafka.html
2. Apache Kafka, "Producer Configs", https://kafka.apache.org/43/configuration/producer-configs/
3. Apache Kafka, "Consumer Configs", https://kafka.apache.org/41/configuration/consumer-configs/
