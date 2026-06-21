---
title: Kafka Consumer Lag
category: k
date: 2026-06-22 00:00:00 +0900
tags: [kafka, consumer-lag, consumer-group, monitoring, offset]
---

## 1. Lag이란?

일상에서 컴퓨터가 느려지거나 버벅거리면 "렉 걸린다"라고 말한다.
이때 렉은 영어 `lag`를 그대로 읽은 표현이다.

Kafka에서 말하는 Consumer Lag은 Consumer Group이 아직 따라잡지 못한 메시지의 지연 정도를 의미한다.
입문 단계에서는 아래처럼 이해하면 된다.

```text
Consumer Lag = 컨슈머가 아직 처리하지 못한 메시지 수를 offset 차이로 본 값
```

Confluent 문서는 Consumer offset을 Consumer Group의 진행 상태를 추적하기 위한 값으로 설명한다. [1]
Confluent Cloud 문서는 Consumer Lag 모니터링을 Consumer Group이 얼마나 뒤처져 있는지 확인하는 방법으로 설명한다. [2]

실무에서는 보통 아래처럼 이해한다.

```text
Lag = LOG-END-OFFSET - CURRENT-OFFSET
```

즉, 가장 최신 메시지 위치와 Consumer Group이 현재 따라간 위치의 차이이다.

---

## 2. Consumer Lag은 언제 발생할까?

Consumer Lag은 Producer가 메시지를 넣는 속도보다 Consumer가 메시지를 처리하는 속도가 느릴 때 발생한다.

예를 들어 아래 상황을 가정해보자.

```text
Producer: 1초에 메시지 3개 생산
Consumer: 1초에 메시지 1개 처리
```

그러면 1초마다 메시지 2개씩 밀린다.

```text
1초 뒤: 2개 밀림
2초 뒤: 4개 밀림
3초 뒤: 6개 밀림
```

이런 상황이 계속되면 Consumer Lag이 점점 커진다.

실제 서비스에서는 아래 같은 상황에서 Lag이 자주 생긴다.

| 상황 | 설명 |
|---|---|
| 트래픽 급증 | Producer가 평소보다 많은 메시지를 보낼 때 |
| Consumer 장애 | Consumer가 죽거나 멈췄을 때 |
| 처리 로직 지연 | DB, 외부 API, 파일 처리 등으로 Consumer가 느려질 때 |
| Partition 불균형 | 특정 Partition만 유독 밀릴 때 |

AWS MSK 문서도 Consumer Lag 모니터링을 통해 최신 데이터 속도를 따라가지 못하는 느리거나 멈춘 Consumer를 식별할 수 있다고 설명한다. [3]

---

## 3. Consumer Lag이 왜 중요할까?

Consumer Lag이 커진다는 것은 메시지 처리가 늦어지고 있다는 뜻이다.

예를 들어 이메일 발송 시스템을 생각해보자.

```text
사용자 -> 이메일 발송 요청
Producer -> Kafka에 메시지 저장
Consumer -> 실제 이메일 발송 처리
```

이때 Consumer Lag이 계속 커지면, 사용자가 버튼을 눌렀어도 실제 이메일 발송은 한참 뒤에 일어날 수 있다.

즉, 사용자 입장에서는 아래처럼 느낄 수 있다.

```text
요청은 보냈는데 처리가 안 된다
서비스가 느리다
서비스에 문제가 생긴 것 같다
```

따라서 Consumer Lag이 계속 증가하고 있다면 빨리 원인을 찾고 조치해야 한다.

---

## 4. CLI로 Consumer Lag 확인하기

Kafka CLI에서는 Consumer Group 세부 정보를 조회하는 명령어로 Lag을 확인할 수 있다.

```bash
bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group email-send-group \
  --describe
```

이 명령어를 실행하면 보통 아래와 비슷한 항목이 보인다.

```text
GROUP             TOPIC       PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
email-send-group  email.send  0          10              12              2
email-send-group  email.send  1          20              21              1
email-send-group  email.send  2          30              31              1
```

각 항목의 의미는 아래와 같다.

| 항목 | 의미 |
|---|---|
| `CURRENT-OFFSET` | Consumer Group이 현재 기록해둔 offset 위치 |
| `LOG-END-OFFSET` | 해당 Partition에 저장된 가장 최신 위치 |
| `LAG` | 아직 따라잡지 못한 offset 차이 |

위 예시라면 Partition별 Lag은 아래와 같다.

```text
Partition 0: 12 - 10 = 2
Partition 1: 21 - 20 = 1
Partition 2: 31 - 30 = 1
```

총 Lag은 아래처럼 볼 수 있다.

```text
2 + 1 + 1 = 4
```

즉, 이 Consumer Group이 아직 처리하지 못한 메시지가 총 4개 정도 밀려 있다고 해석할 수 있다.

---

## 5. Lag을 의도적으로 만들어 확인하기

Consumer Lag을 직접 보고 싶다면 Consumer를 멈춘 뒤 Producer만 메시지를 쌓이게 만들면 된다.

실습 순서는 아래와 같다.

1. Consumer 서버를 종료한다.
2. Producer 서버는 켜둔다.
3. API 요청을 여러 번 보내 Topic에 메시지가 쌓이게 만든다.
4. `kafka-consumer-groups.sh --describe`로 Lag을 확인한다.

예를 들어 API 요청을 4번 보내면 Partition별로 메시지가 나누어 저장될 수 있다.
그 상태에서 Consumer가 멈춰 있으면 `CURRENT-OFFSET`은 그대로인데 `LOG-END-OFFSET`만 증가하므로 `LAG` 값이 커진다.

입문 단계에서는 아래만 기억하면 된다.

```text
Consumer가 멈춰 있고 Producer만 계속 메시지를 넣으면 LAG가 증가한다.
```

---

## 6. CLI만으로는 충분하지 않은 이유

CLI로 Consumer Lag을 확인하는 방법은 유용하다.
하지만 사람이 24시간 내내 터미널을 열어두고 확인할 수는 없다.

운영에서는 아래가 더 중요하다.

```text
LAG가 생겼는가?
LAG가 줄어드는가?
LAG가 계속 커지는가?
특정 Consumer Group만 문제인가?
특정 Partition만 문제인가?
```

이런 변화는 계속 모니터링해야 한다.

Confluent Cloud 문서도 Consumer Lag은 시간에 따라 어떻게 변하는지 모니터링하는 것이 중요하다고 설명한다. [2]

---

## 7. 현업에서 Consumer Lag 체크하는 방법

현업에서는 보통 CLI 대신 모니터링 도구를 사용한다.

대표적인 방식은 두 가지이다.

### 7-1. 외부 모니터링 도구 사용

많이 사용하는 예시는 아래와 같다.

| 도구 | 성격 |
|---|---|
| Datadog | 상용 모니터링 서비스 |
| Burrow | Kafka Consumer Lag 전용 오픈소스 도구 |
| Prometheus | 오픈소스 모니터링/알림 수집 도구 |
| Grafana | 메트릭 시각화와 대시보드 도구 |

Datadog은 Amazon MSK 통합 문서를 제공하고, MSK 메트릭 수집 구성을 설명한다. [4]
Burrow는 LinkedIn이 공개한 오픈소스 프로젝트로, Kafka Consumer Lag checking을 서비스 형태로 제공한다고 설명한다. [5]
Prometheus는 공식 문서에서 오픈소스 모니터링 및 알림 툴킷이라고 설명한다. [6]
Grafana는 공식 문서에서 메트릭, 로그, 트레이스를 시각화하고 탐색할 수 있는 오픈소스 소프트웨어라고 설명한다. [7]

이런 도구를 사용하면 Lag을 대시보드로 보고, 임계값을 넘으면 알림을 보내게 만들 수 있다.

### 7-2. 매니지드 Kafka 서비스의 모니터링 기능 사용

현업에서는 Kafka를 직접 설치해 운영하지 않고 관리형 서비스를 쓰는 경우도 많다.

대표적인 예시는 아래와 같다.

| 서비스 | 설명 |
|---|---|
| AWS MSK | AWS의 관리형 Kafka 서비스 |
| Confluent Cloud | Confluent의 관리형 Kafka 서비스 |

AWS MSK 문서는 CloudWatch 또는 Prometheus 기반 open monitoring으로 Consumer Lag을 모니터링할 수 있다고 설명한다. [3]
Confluent Cloud 문서는 Cloud Console, Metrics API, Java client metrics 등으로 Consumer Lag을 모니터링하는 방법을 제공한다. [2]

즉, 관리형 서비스를 사용하면 Consumer Lag 모니터링 기능을 직접 구성하는 부담을 줄일 수 있다.

---

## 8. Consumer Lag을 볼 때 주의할 점

Lag이 0이 아니라고 해서 무조건 장애는 아니다.

예를 들어 아래 상황은 다르게 봐야 한다.

| 상태 | 해석 |
|---|---|
| Lag이 잠깐 생겼다가 빠르게 0으로 돌아감 | 일시적인 트래픽 증가일 수 있음 |
| Lag이 0보다 크지만 일정하게 유지됨 | 다소 밀리지만 현재 속도로 따라잡는 중일 수 있음 |
| Lag이 계속 증가함 | Consumer가 Producer 속도를 따라가지 못하는 상황 |

중요한 것은 특정 시점의 숫자 하나보다 시간에 따른 추세이다.

```text
Lag가 줄어드는가?
Lag가 유지되는가?
Lag가 계속 커지는가?
```

운영에서는 이 추세를 보고 알림 조건과 대응 기준을 정해야 한다.

---

## 정리

Consumer Lag은 Consumer Group이 아직 따라잡지 못한 메시지의 지연 정도를 offset 차이로 보는 지표이다.

입문적으로는 아래처럼 이해하면 된다.

```text
Lag = LOG-END-OFFSET - CURRENT-OFFSET
```

Producer가 메시지를 넣는 속도보다 Consumer가 처리하는 속도가 느리면 Lag이 커진다.
CLI에서는 `kafka-consumer-groups.sh --describe`로 확인할 수 있다.

실제 운영에서는 CLI를 계속 보는 대신 Datadog, Burrow, Prometheus, Grafana 같은 도구나 AWS MSK, Confluent Cloud 같은 관리형 서비스의 모니터링 기능으로 Consumer Lag을 지속적으로 추적하는 편이 일반적이다.

---

## 출처

1. Confluent Documentation, "Kafka Consumer Design: Consumers, Consumer Groups, and Offsets", https://docs.confluent.io/kafka/design/consumer-design.html
2. Confluent Cloud Documentation, "Monitor Kafka Consumer Lag in Confluent Cloud", https://docs.confluent.io/cloud/current/monitoring/monitor-lag.html
3. Amazon Web Services, "Monitor consumer lags", https://docs.aws.amazon.com/msk/latest/developerguide/consumer-lag.html
4. Datadog Docs, "Amazon MSK", https://docs.datadoghq.com/integrations/amazon-msk/
5. LinkedIn Burrow GitHub, "Burrow: Kafka Consumer Lag Checking", https://github.com/linkedin/burrow
6. Prometheus Documentation, "Overview", https://prometheus.io/docs/introduction/overview/
7. Grafana Documentation, "Introduction", https://grafana.com/docs/grafana/latest/fundamentals/
