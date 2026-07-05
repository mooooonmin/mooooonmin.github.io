---
title: Logging Architecture With Elasticsearch
category: l
date: 2026-07-06 00:00:10 +0900
tags: [logback, logstash, elasticsearch, document, index, architecture]
---

## 1. Logback, Logstash, Elasticsearch를 함께 쓰면 어떤 구조가 될까?

입문 수준에서 가장 단순한 로그 수집 아키텍처는 아래 흐름으로 이해할 수 있다.

```text
User 요청
-> Spring Boot 애플리케이션
-> Logback이 로그 파일에 기록
-> Logstash가 파일을 읽음
-> Elasticsearch로 JSON 형태 이벤트 전송
```

즉, 각 구성의 역할은 아래처럼 나뉜다.

1. Logback
   - 애플리케이션 로그를 파일로 기록
2. Logstash
   - 파일 로그를 읽고 필요한 형태로 가공
3. Elasticsearch
   - 가공된 로그를 저장하고 검색

이 구조의 핵심은 "애플리케이션이 찍은 로그 한 줄"이 그대로 끝나는 것이 아니라, 중간에 가공을 거쳐 검색 가능한 데이터로 저장된다는 점이다.

---

## 2. Spring Boot와 Logback은 무엇을 할까?

Spring Boot 애플리케이션에서 로그가 발생하면, Logback이 그 로그를 파일에 기록할 수 있다.

예를 들어 아래 같은 파일이 생길 수 있다.

```text
waiting-api-log.log
```

앞선 글에서 정리했듯이, Logback은 로그를 어디로 보낼지 Appender로 제어하고, 파일 출력이 필요하면 `FileAppender` 또는 `RollingFileAppender`를 사용할 수 있다.

즉, 이 단계에서는 아래 역할만 맡는다.

```text
애플리케이션 내부에서 발생한 로그를 로그 파일로 남긴다
```

---

## 3. Logstash는 이 로그 파일을 어떻게 처리할까?

Logstash는 file input으로 로그 파일을 읽고, filter로 필요한 필드를 가공한 뒤, output으로 Elasticsearch에 전송할 수 있다.

Elastic 공식 문서는 Logstash가 `input -> filter -> output` 파이프라인 구조로 동작한다고 설명한다. [1]

즉, 이 단계는 아래처럼 이해하면 된다.

```text
로그 파일 읽기
-> 로그 한 줄 파싱
-> JSON 형태 이벤트 만들기
-> Elasticsearch로 전송
```

이 때문에 터미널에서 보던 한 줄 텍스트 로그가, Elasticsearch에 들어갈 때는 구조화된 데이터 한 건으로 바뀐다.

---

## 4. Elasticsearch에서 말하는 Document란 무엇일까?

Elasticsearch에서 가장 먼저 알아야 할 용어가 `document`다.

Elastic 공식 API 문서는 Elasticsearch에 JSON document를 index에 넣는다고 설명한다. [2][3]

즉, Elasticsearch에서 document는 아래처럼 이해하면 된다.

```text
JSON 형태로 저장되는 데이터 한 건
```

예를 들어 Spring Boot 로그 한 줄이 Logstash를 거친 뒤 아래처럼 바뀔 수 있다.

```json
{
  "@timestamp": "2026-07-06T10:00:00.123+09:00",
  "level": "INFO",
  "service": "waiting-api",
  "thread": "nio-8080-exec-4",
  "logger": "com.example.waiting.WaitingService",
  "message": "waiting created"
}
```

이 JSON 덩어리 하나가 Elasticsearch에서는 document다.

즉, 사용자가 터미널에서 보는 로그 한 줄이 Logstash를 거치면 "검색 가능한 JSON 한 건"으로 변환된다고 보면 된다.

---

## 5. 로그 한 줄이 왜 JSON document로 바뀌어야 할까?

그냥 문자열 한 줄로만 저장하면 검색과 분석이 어렵다.

예를 들어 아래처럼 구조화돼 있지 않으면

```text
2026-07-06 10:00:00 INFO waiting-api waiting created
```

다음 같은 조건 검색이 불편해진다.

1. `level = ERROR`만 찾기
2. 특정 thread만 찾기
3. 특정 logger만 집계하기
4. 시간대별 로그 수 계산하기

반면 JSON document로 분리해 두면

1. `level`
2. `service`
3. `thread`
4. `logger`
5. `message`
6. `@timestamp`

같은 필드 단위로 검색하고 집계할 수 있다.

즉, Logstash가 로그를 JSON document로 바꾸는 이유는 Elasticsearch가 잘 검색하고 잘 분석하게 만들기 위해서다.

---

## 6. Elasticsearch에서 말하는 Index란 무엇일까?

두 번째 핵심 용어는 `index`다.

Elastic 공식 문서는 index를 Elasticsearch의 fundamental unit of storage라고 설명한다. 또한 하나의 index는 document들의 모음이라고 설명한다. [4]

즉, 아래처럼 이해하면 된다.

```text
Document = JSON 데이터 한 건
Index = 그런 document들을 묶어 보관하는 논리적 저장 공간
```

관계형 DB에 익숙한 사람이라면 아주 대략적으로 아래처럼 비유할 수 있다.

```text
RDB의 행(row) 비슷한 개념 -> document
RDB의 테이블과 비슷하게 데이터를 모아두는 공간 -> index
```

물론 완전히 같은 개념은 아니지만, 입문 단계에서는 이렇게 이해해도 무방하다.

---

## 7. 날짜별 인덱스로 묶는다는 것은 무슨 뜻일까?

사용자가 준 Logstash 설정 예시는 아래와 같다.

```ruby
index => "waiting-api-logs-%{+YYYY.MM.dd}"
```

Logstash Elasticsearch output plugin 공식 문서는 `index` 옵션으로 target index 이름을 지정할 수 있다고 설명한다. [5]

이 설정은 날짜 형식이 들어간 index 이름을 만들겠다는 뜻이다.

예를 들어 2026년 7월 6일 로그라면 아래처럼 저장될 수 있다.

```text
waiting-api-logs-2026.07.06
```

다음 날이면

```text
waiting-api-logs-2026.07.07
```

처럼 다른 index가 만들어질 수 있다.

즉, "도큐먼트를 모아서 날짜별 인덱스에 묶는다"는 말은 아래와 같다.

1. 로그 한 줄 -> document 한 건
2. 같은 날짜 로그 document들 -> 같은 날짜 index에 저장

---

## 8. 왜 날짜별 index가 유용할까?

로그는 시간 기반 데이터이기 때문에 날짜별로 나누어 저장하는 것이 관리에 유리한 경우가 많다.

예를 들어 아래 장점이 있다.

1. 특정 날짜 로그만 조회하기 쉽다.
2. 오래된 로그를 삭제하거나 보관 정책 적용하기 쉽다.
3. 운영 중 index 단위 관리가 편하다.

즉, 아래처럼 생각하면 된다.

```text
로그는 시간이 핵심 정보이므로
시간 기준으로 index를 나누는 것이 자연스럽다.
```

다만 최신 Elastic 환경에서는 전통적인 일자별 index 대신 data stream을 더 권장하는 경우도 많다. [5]
그래도 입문 실습에서 `index => "waiting-api-logs-%{+YYYY.MM.dd}"` 패턴은 날짜별 index 개념을 이해하기에 충분히 좋은 예시다.

---

## 9. 전체 흐름을 한 번에 보면

이 구조를 처음부터 끝까지 다시 써보면 아래와 같다.

```text
1. 사용자가 API 요청을 보낸다
2. Spring Boot 애플리케이션에서 로그가 발생한다
3. Logback이 로그를 파일에 쓴다
4. Logstash가 파일을 tail/read 한다
5. Logstash가 로그 한 줄을 JSON event로 변환한다
6. Elasticsearch에 HTTP로 전송한다
7. Elasticsearch는 그 JSON을 document로 저장한다
8. document들은 날짜별 index에 모인다
```

즉, 이 아키텍처의 본질은 아래 한 줄로 요약할 수 있다.

```text
텍스트 로그를 검색 가능한 document와 index 구조로 바꾸는 흐름
```

---

## 정리

Logback, Logstash, Elasticsearch를 함께 사용하면 애플리케이션 로그를 파일에 기록하고, 이를 구조화된 JSON document로 변환해 Elasticsearch index에 저장하는 아키텍처를 만들 수 있다.

핵심만 정리하면 아래와 같다.

1. Logback은 애플리케이션 로그를 파일에 기록한다.
2. Logstash는 로그 파일을 읽어 JSON event로 변환한다.
3. Elasticsearch는 그 JSON 한 건을 document로 저장한다.
4. 여러 document는 index라는 논리적 저장 공간에 묶인다.
5. `index => "waiting-api-logs-%{+YYYY.MM.dd}"` 설정을 사용하면 날짜별 index로 저장할 수 있다.

즉, 이 구조를 이해하면 "로그 한 줄이 Elasticsearch에서 어떻게 저장되고 관리되는지"를 전체 흐름으로 볼 수 있게 된다.

---

## 출처

1. Elastic Docs, "How Logstash Works", https://www.elastic.co/docs/reference/logstash/how-logstash-works
2. Elasticsearch API, "Create a new document in the index", https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-create
3. Elasticsearch API, "Create or update a document in an index", https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-index
4. Elastic Docs, "Index fundamentals", https://www.elastic.co/docs/manage-data/data-store/index-basics
5. Elastic Docs, "Elasticsearch output plugin", https://www.elastic.co/docs/reference/logstash/plugins/plugins-outputs-elasticsearch
