---
title: Logstash Core Features
category: l
date: 2026-07-01 00:00:10 +0900
tags: [logstash, input, filter, output, elasticsearch, logging]
---

## 1. Logstash는 무슨 일을 할까?

Logstash는 데이터를 받아서, 필요한 형태로 가공한 뒤, 다른 시스템으로 보내는 파이프라인 도구다.

Elastic 공식 문서는 Logstash를 server-side data processing pipeline이라고 설명한다. [1][2]

로그 관점에서 보면 아래 역할로 이해하면 된다.

```text
각 서버에서 로그를 받는다
-> 필요한 필드를 가공한다
-> Elasticsearch 같은 목적지로 보낸다
```

즉, 입문 단계에서는 `수집 -> 변환 -> 전달` 도구라고 이해하면 된다.

---

## 2. Logstash는 어떤 구조로 움직일까?

Logstash의 핵심 구조는 3단계다.

1. Input
2. Filter
3. Output

Elastic 공식 문서는 Logstash event processing pipeline이 `inputs -> filters -> outputs` 세 단계로 동작한다고 설명한다. inputs는 event를 만들고, filters는 event를 수정하며, outputs는 event를 다른 곳으로 보낸다. [3]

즉, 기본 흐름은 아래와 같다.

```text
Input -> Filter -> Output
```

이 3단계 구조만 이해해도 Logstash의 핵심은 거의 잡힌다.

---

## 3. Input(입력)

Input은 Logstash가 데이터를 어디서 받아올지 정하는 단계다.

Elastic 공식 문서는 input plugin이 특정 source에서 event를 읽어들이는 역할을 한다고 설명한다. [4]

예를 들어 아래 같은 입력원이 가능하다.

1. 로그 파일
2. Beats/Filebeat
3. Kafka
4. TCP/UDP
5. JDBC

초안처럼 `waiting-api-log.log` 파일을 읽는 예시도 가능하다.

예를 들어 file input plugin은 로그 파일을 감시하면서 새 줄이 추가될 때 이를 읽을 수 있다. [5]

즉, Input 단계는 아래 질문에 답하는 부분이다.

```text
Logstash가 어디서 로그를 가져올 것인가?
```

---

## 4. 파일을 한 줄씩 읽는다는 것은 무슨 뜻일까?

로그 파일 입력 예시를 떠올려보자.

```text
waiting-api-log.log
```

Logstash의 file input plugin은 파일의 현재 읽은 위치를 추적하면서, 새 로그 라인이 추가되면 event로 읽어들일 수 있다. Elastic 공식 문서는 이를 위해 `sincedb`라는 위치 추적 파일을 사용한다고 설명한다. [5]

즉, 입문 관점에서는 아래처럼 이해하면 된다.

1. 로그 파일을 계속 감시한다.
2. 새 줄이 생기면 읽는다.
3. 읽은 위치를 기억해둔다.

이 덕분에 Logstash를 재시작해도 어디까지 읽었는지 이어서 처리할 수 있다.

다만 운영 환경 전체에서 파일 수집을 Logstash로 직접만 하는 것이 항상 최선은 아니다.
Elastic 측도 파일 수집/전송에는 Filebeat가 더 가볍고 적합한 선택일 수 있다고 설명한다. [6]

즉, 입문 실습에서는 file input이 이해하기 쉽고, 운영 환경에서는 Filebeat/Elastic Agent와 함께 쓰는 경우도 많다.

---

## 5. Filter(필터)

Filter는 입력으로 들어온 로그를 가공하는 단계다.

Elastic 공식 문서는 filter plugin이 intermediary processing을 수행한다고 설명한다. 즉, event를 parsing하고 transforming하는 역할이다. [7][8]

이 단계가 중요한 이유는 로그를 그냥 긴 문자열 통째로 저장하는 것보다, 의미 있는 필드로 쪼개두는 편이 검색과 분석에 훨씬 유리하기 때문이다.

예를 들어 아래처럼 가공할 수 있다.

1. 시간(timestamp) 추출
2. 로그 레벨 추출
3. trace id 추출
4. 서비스 이름 분리
5. 민감정보 제거

즉, Filter 단계는 아래 질문에 답한다.

```text
이 로그를 어떻게 검색하기 좋은 구조로 바꿀 것인가?
```

---

## 6. 라벨링해서 구분한다는 것은 무슨 뜻일까?

원본 로그가 아래처럼 한 줄 문자열이라고 해보자.

```text
2026-07-01T10:00:00.000+09:00 INFO [waiting-api] [trace-123] Payment created
```

이 상태로는 그냥 텍스트 한 줄이다.

그런데 Filter를 거치면 아래처럼 필드를 나눠 저장할 수 있다.

```text
timestamp = 2026-07-01T10:00:00.000+09:00
level = INFO
service = waiting-api
trace_id = trace-123
message = Payment created
```

이렇게 되면 나중에 Elasticsearch에서 아래처럼 검색하기 쉬워진다.

1. `level = ERROR`
2. `trace_id = trace-123`
3. `service = waiting-api`

즉, Filter는 단순 문자열을 "검색 가능한 구조화 데이터"로 바꾸는 핵심 단계다.

---

## 7. Output(출력)

Output은 가공된 데이터를 어디로 보낼지 정하는 마지막 단계다.

Elastic 공식 문서는 output plugin이 event data를 특정 destination으로 보내는 final stage라고 설명한다. [9]

예를 들어 목적지는 아래처럼 다양할 수 있다.

1. Elasticsearch
2. 파일
3. stdout
4. Kafka
5. 다른 파이프라인

초안처럼 가장 대표적인 목적지는 Elasticsearch다.

Elasticsearch output plugin 공식 문서는 이 plugin이 logs, events, metrics 같은 데이터를 Elasticsearch에 저장할 수 있다고 설명한다. [10]

즉, Output 단계는 아래 질문에 답한다.

```text
가공한 로그를 최종적으로 어디에 보낼 것인가?
```

---

## 8. 전체 흐름을 한 번에 보면

입문 예시를 아주 단순하게 정리하면 아래와 같다.

```text
waiting-api-log.log 파일
-> Input이 읽는다
-> Filter가 timestamp, level, trace id 등을 분리한다
-> Output이 Elasticsearch로 보낸다
-> Kibana에서 검색하고 시각화한다
```

즉, Logstash는 ELK 안에서 아래 역할을 맡는 셈이다.

```text
원본 로그를 Elasticsearch에 넣기 좋은 형태로 바꿔 전달하는 중간 처리기
```

---

## 9. 실무에서는 꼭 파일 입력만 쓸까?

그렇지는 않다.

입문에서는 file input이 이해하기 쉽지만, 실제 운영에서는 Filebeat나 Elastic Agent가 로그 수집을 담당하고, Logstash는 그 뒤에서 가공을 맡는 구조도 흔하다.

Elastic 블로그도 파일 수집과 전달 자체는 Filebeat가 더 가볍고 효율적이라고 설명한다. [6]

즉, 실무에서는 아래 같은 구성이 많다.

```text
애플리케이션 로그 파일
-> Filebeat
-> Logstash
-> Elasticsearch
-> Kibana
```

그래도 Logstash의 본질은 변하지 않는다.

1. 입력 받기
2. 필터링/변환하기
3. 출력하기

---

## 정리

Logstash의 핵심 기능은 로그나 이벤트 데이터를 받아서, 가공하고, 원하는 목적지로 보내는 것이다.

핵심만 정리하면 아래와 같다.

1. Input은 데이터를 어디서 읽어올지 정한다.
2. Filter는 데이터를 검색하기 좋은 구조로 가공한다.
3. Output은 가공된 데이터를 최종 목적지로 보낸다.
4. 파일 로그를 읽어 Elasticsearch로 보내는 구조는 Logstash 입문 예시로 이해하기 좋다.
5. 운영 환경에서는 Filebeat/Elastic Agent와 함께 쓰는 경우도 많다.

즉, Logstash는 ELK에서 "수집된 로그를 분석 가능한 데이터로 바꿔주는 중간 처리 파이프라인"이라고 이해하면 된다.

---

## 출처

1. Elastic, "Logstash", https://www.elastic.co/logstash
2. Elastic Docs, "Logstash", https://www.elastic.co/docs/reference/logstash
3. Elastic Docs, "How Logstash Works", https://www.elastic.co/docs/reference/logstash/how-logstash-works
4. Elastic Docs, "Input plugins", https://www.elastic.co/docs/reference/logstash/plugins/input-plugins
5. Elastic Docs, "File input plugin", https://www.elastic.co/docs/reference/logstash/plugins/plugins-inputs-file
6. Elastic Blog, "A Practical Introduction to Logstash", https://www.elastic.co/blog/a-practical-introduction-to-logstash
7. Elastic Docs, "Filter plugins", https://www.elastic.co/docs/reference/logstash/plugins/filter-plugins
8. Elastic, "Logstash: Collect, Parse, Transform Logs", https://www.elastic.co/logstash
9. Elastic Docs, "Output plugins", https://www.elastic.co/docs/reference/logstash/plugins/output-plugins
10. Elastic Docs, "Elasticsearch output plugin", https://www.elastic.co/docs/reference/logstash/plugins/plugins-outputs-elasticsearch
