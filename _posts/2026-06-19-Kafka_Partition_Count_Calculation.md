---
title: Kafka Partition Count Calculation
category: k
date: 2026-06-19 00:00:20 +0900
tags: [kafka, partition, throughput, load-test, consumer]
---

## 1. 적정 Partition 수를 계산하는 기준

Kafka Topic의 Partition 수를 정할 때 핵심은 아래와 같다.

```text
처리가 지연되는 메시지가 생기지 않는 선에서 Partition 수를 최소로 설정한다.
```

Partition이 너무 적으면 Consumer가 메시지를 처리하는 속도보다 Producer가 메시지를 넣는 속도가 더 빨라질 수 있다.
그러면 처리되지 못한 메시지가 계속 쌓인다.

반대로 Partition을 무작정 많이 만들면 관리해야 할 Partition이 많아진다.
Partition이 많아지면 브로커, Consumer Group rebalancing, 운영 관리 측면에서 부담이 커질 수 있다. [1]

그래서 적정 Partition 수를 정할 때는 처리량을 기준으로 계산해야 한다.

입문 단계에서는 아래 공식으로 생각하면 된다.

```text
Producer가 보내는 메시지량 <= 하나의 처리 단위가 처리하는 메시지량 x 병렬 처리 단위 수
```

Kafka에서 병렬 처리 단위 수를 늘릴 때 Partition 수가 중요한 기준이 된다.
다만 Partition 수만 늘린다고 처리량이 자동으로 늘어나는 것은 아니다.
Consumer 인스턴스 수, Consumer concurrency, 서버 자원도 함께 맞아야 한다.

---

## 2. 마트 계산대 비유

대형 마트에서 계산대를 몇 개 열지 결정한다고 생각해보자.

계산대를 너무 적게 열면 손님 줄이 길어진다.
손님이 계산까지 오래 기다리면 불만이 생긴다.

하지만 계산대를 무작정 많이 열 수도 없다.
계산대를 많이 열려면 직원을 더 많이 배치해야 하고, 마트 입장에서는 비용이 늘어난다.

그래서 마트는 아래 기준으로 계산대 수를 정해야 한다.

```text
손님 줄이 길어지지 않는 선에서 계산대 수를 최소로 유지한다.
```

Kafka Partition도 비슷하다.

```text
메시지가 밀리지 않는 선에서 Partition 수를 최소로 유지한다.
```

---

## 3. 1단계: 적절한 처리 스레드 수 측정하기

먼저 Consumer 서버가 몇 개의 처리 스레드를 사용할 때 가장 효율적인지 측정해야 한다.

이 값은 추측으로 정하면 안 된다.
실제 서버 환경에서 부하 테스트를 통해 확인해야 한다.

예를 들어 Consumer 서버가 아래 조건에서 가장 효율적이었다고 가정해보자.

```text
Consumer 서버 1대
처리 스레드 100개
```

이 값은 예시이다.
실제 서비스에서는 CPU, Memory, 네트워크, 외부 API 응답 시간, DB 성능에 따라 달라진다.

---

## 4. 2단계: Consumer 서버의 최대 처리량 측정하기

다음으로 Consumer 서버 1대가 최대 몇 개의 메시지를 처리할 수 있는지 측정한다.

예를 들어 부하 테스트 결과가 아래와 같다고 가정하자.

```text
Consumer 서버 1대
처리 스레드 100개
최대 처리량: 30 messages/sec
```

이 말은 Consumer 서버 1대가 1초에 메시지 30개를 처리할 수 있다는 뜻이다.

스레드 100개로 초당 30개를 처리했다면, 단순 평균으로 스레드 1개당 처리량은 아래처럼 계산할 수 있다.

```text
스레드 1개당 처리량 = 30 / 100
                  = 0.3 messages/sec
```

즉, 이 예시에서는 처리 단위 1개가 1초에 0.3개의 메시지를 처리한다고 볼 수 있다.

---

## 5. 3단계: Producer가 보내는 메시지량 측정하기

다음으로 Producer가 Kafka에 1초당 얼마나 많은 메시지를 보내는지 측정하거나 예상해야 한다.

예를 들어 사용자가 이메일 발송 API를 호출하고, API 서버가 `email.send` Topic에 메시지를 넣는다고 해보자.

운영 지표를 확인했더니 평균적으로 아래 정도의 메시지가 들어온다고 가정한다.

```text
평균 메시지량: 100 messages/sec
```

하지만 평균값만 보고 계산하면 위험하다.
트래픽은 순간적으로 평균보다 높아질 수 있다.

그래서 여유를 두고 아래 정도까지 처리할 수 있게 잡는다고 가정하자.

```text
목표 처리량: 120 messages/sec
```

여기서 120은 평균 100보다 20% 여유를 둔 예시이다.

```text
100 x 1.2 = 120
```

---

## 6. 4단계: 필요한 병렬 처리 단위 계산하기

이제 필요한 병렬 처리 단위 수를 계산한다.

앞에서 계산한 값은 아래와 같다.

```text
목표 처리량 = 120 messages/sec
처리 단위 1개당 처리량 = 0.3 messages/sec
```

필요한 병렬 처리 단위 수는 아래처럼 계산한다.

```text
필요한 병렬 처리 단위 수 = 목표 처리량 / 처리 단위 1개당 처리량
                       = 120 / 0.3
                       = 400
```

따라서 이 단순 계산에서는 400개의 병렬 처리 단위가 필요하다.

입문용 공식으로 쓰면 아래와 같다.

```text
Producer가 보내는 메시지량 <= 하나의 처리 단위가 처리하는 메시지량 x 병렬 처리 단위 수
120 <= 0.3 x 400
120 <= 120
```

이 조건을 만족하므로 목표 처리량 120 messages/sec를 처리할 수 있다고 계산할 수 있다.

---

## 7. Partition 수와 Consumer 자원은 같이 맞아야 한다

여기서 주의할 점이 있다.

필요한 병렬 처리 단위가 400개라고 해서 Partition만 400개로 만들면 끝나는 것은 아니다.

Kafka에서 같은 Consumer Group 안에서는 하나의 Partition이 한 시점에 하나의 Consumer에게 할당된다. [2]
따라서 병렬 처리를 충분히 하려면 Partition 수뿐만 아니라 Consumer 인스턴스 수나 Consumer concurrency도 함께 준비되어야 한다.

예를 들어 앞에서 Consumer 서버 1대가 스레드 100개로 30 messages/sec를 처리한다고 했다.

목표 처리량이 120 messages/sec라면 Consumer 서버도 아래 정도가 필요할 수 있다.

```text
필요한 Consumer 서버 수 = 목표 처리량 / Consumer 서버 1대 처리량
                     = 120 / 30
                     = 4
```

즉, 이 예시에서는 아래 조건이 함께 필요할 수 있다.

```text
Partition 수: 최소 400개 수준
Consumer 서버: 4대 수준
총 처리 스레드: 400개 수준
```

정확한 값은 실제 부하 테스트 결과로 판단해야 한다.

---

## 8. 왜 최소로 설정해야 할까?

Partition은 많을수록 무조건 좋은 것이 아니다.

Partition이 많으면 병렬 처리 가능성은 커질 수 있다.
하지만 관리 비용도 함께 늘어난다.

예를 들어 아래 문제가 생길 수 있다.

```text
Partition metadata 증가
Consumer Group rebalancing 부담 증가
브로커 리소스 사용량 증가
운영 복잡도 증가
```

Confluent 문서는 Partition 수를 정할 때 처리량뿐 아니라 consumer rebalancing, producer latency, broker resource 같은 요소를 함께 고려해야 한다고 설명한다. [1]

그래서 적정 Partition 수는 아래처럼 정해야 한다.

```text
목표 처리량을 만족하는 최소 Partition 수
```

---

## 9. 계산 과정 정리

이번 예시의 계산 과정을 다시 정리하면 아래와 같다.

먼저 부하 테스트로 Consumer 서버 성능을 측정한다.

```text
Consumer 서버 1대
처리 스레드 100개
최대 처리량 30 messages/sec
```

스레드 1개당 처리량을 계산한다.

```text
30 / 100 = 0.3 messages/sec
```

Producer가 보내는 평균 메시지량을 확인한다.

```text
평균 100 messages/sec
```

트래픽 증가 여유를 반영해 목표 처리량을 정한다.

```text
100 x 1.2 = 120 messages/sec
```

필요한 병렬 처리 단위 수를 계산한다.

```text
120 / 0.3 = 400
```

따라서 이 예시에서는 400개 수준의 병렬 처리 단위가 필요하다고 볼 수 있다.
Kafka에서는 이를 감당할 수 있는 Partition 수와 Consumer 처리 자원을 함께 준비해야 한다.

---

## 10. 실제 운영에서는 무엇을 더 봐야 할까?

실제 운영에서는 단순 계산만으로 끝내면 안 된다.

아래 요소도 함께 확인해야 한다.

| 확인할 항목 | 이유 |
|---|---|
| Consumer 처리 시간 | 메시지 하나를 처리하는 데 걸리는 시간이 처리량에 직접 영향을 준다 |
| 외부 API 응답 시간 | 이메일 발송 같은 외부 시스템이 병목이 될 수 있다 |
| DB 성능 | Consumer가 DB를 사용한다면 DB가 병목이 될 수 있다 |
| Consumer lag | 메시지가 밀리는지 확인할 수 있는 핵심 지표이다 |
| Partition 수 증가 가능성 | Partition 수는 늘릴 수 있지만 줄일 수 없으므로 처음 설정이 중요하다 |
| Consumer Group rebalancing | Consumer 추가/제거 시 처리 지연이 생길 수 있다 |

결론적으로 Partition 수는 계산으로 초안을 잡고, 부하 테스트와 운영 지표로 조정해야 한다.

---

## 정리

적정 Partition 수를 정할 때 핵심은 메시지가 밀리지 않는 선에서 Partition 수를 최소로 설정하는 것이다.

입문용 공식은 아래와 같다.

```text
Producer가 보내는 메시지량 <= 하나의 처리 단위가 처리하는 메시지량 x 병렬 처리 단위 수
```

예시에서는 목표 처리량 120 messages/sec, 처리 단위 1개당 처리량 0.3 messages/sec이므로 필요한 병렬 처리 단위는 400개이다.

```text
120 / 0.3 = 400
```

다만 Partition 수만 늘리면 끝나는 것이 아니다.
Consumer 서버 수, Consumer concurrency, 실제 처리량, Consumer lag까지 함께 확인해야 한다.

---

## 출처

1. Confluent Documentation, "Choose and Change the Partition Count in Kafka", https://docs.confluent.io/kafka/operations-tools/partition-determination.html
2. Confluent Documentation, "Kafka Consumer Design: Consumers, Consumer Groups, and Offsets", https://docs.confluent.io/kafka/design/consumer-design.html
3. Apache Kafka, "Introduction - Main Concepts and Terminology", https://kafka.apache.org/intro/
