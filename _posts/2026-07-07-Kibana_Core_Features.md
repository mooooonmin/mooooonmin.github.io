---
title: Kibana Core Features
category: k
date: 2026-07-07 00:00:00 +0900
tags: [kibana, elasticsearch, dashboard, visualization, query, logs]
---

## 1. Kibana는 무슨 일을 할까?

Kibana는 Elasticsearch에 저장된 데이터를 사람이 화면에서 검색하고, 분석하고, 시각화할 수 있게 해주는 도구다.

Elastic 공식 사이트는 Kibana를 Elasticsearch에 저장된 데이터를 query, analyze, visualize, and manage 하기 위한 오픈소스 인터페이스라고 설명한다. [1]

즉, 입문 단계에서는 아래처럼 이해하면 된다.

```text
Elasticsearch가 데이터를 저장한다
Kibana가 그 데이터를 사람이 보기 쉽게 보여준다
```

그래서 Kibana는 단순히 그래프만 그려주는 도구가 아니라, 검색 화면이기도 하고, 분석 화면이기도 하고, 대시보드 화면이기도 하다.

---

## 2. Kibana의 가장 큰 역할

Kibana의 핵심 역할을 아주 짧게 정리하면 아래 두 가지다.

1. Elasticsearch에 쿼리를 실행한다.
2. 그 결과를 다양한 형태로 보여준다.

Elastic 공식 문서도 Kibana가 데이터를 search, interact with, explore, analyze 하는 도구 모음을 제공한다고 설명한다. [2]

즉, 아래 흐름으로 이해하면 된다.

```text
Elasticsearch에 쿼리
-> 결과 조회
-> 필터링
-> 시각화
-> 대시보드 구성
```

---

## 3. 검색과 조회 기능

Kibana를 처음 쓸 때 가장 많이 들어가는 화면 중 하나가 `Discover`다.

Elastic 공식 문서는 Discover를 Kibana에서 Elasticsearch 데이터를 탐색하는 primary tool이라고 설명한다. [3]

Discover에서는 아래 같은 작업을 할 수 있다.

1. 특정 단어 검색
2. 시간 범위 필터링
3. 필드별 값 확인
4. 원본 document 조회

예를 들어 로그를 보고 싶다면 아래처럼 찾을 수 있다.

1. `level: ERROR`
2. `trace_id: abc123`
3. 특정 시간대의 waiting-api 로그

즉, Kibana는 단순 대시보드가 아니라 "Elasticsearch 데이터를 직접 탐색하는 조회 도구"이기도 하다.

---

## 4. 시각화 기능

Kibana의 대표적인 기능 중 하나가 시각화다.

Elastic 공식 문서는 Kibana에서 visualization을 만들고, Lens를 통해 charts, tables, maps, metrics 등을 구성할 수 있다고 설명한다. [4]

즉, Kibana는 저장된 데이터를 아래처럼 보여줄 수 있다.

1. 막대 그래프
2. 꺾은선 그래프
3. 파이 차트
4. 표(table)
5. 메트릭 카드
6. 지도(map)

예를 들어 로그 데이터라면 아래 같은 시각화가 가능하다.

1. 시간대별 에러 건수
2. API별 요청 수
3. 로그 레벨 분포
4. 응답 지연 상위 엔드포인트

즉, Kibana는 단순히 "로그 문장"을 읽는 수준을 넘어, 패턴과 추세를 눈으로 볼 수 있게 해준다.

---

## 5. 대시보드 기능

Kibana에서 가장 실무적으로 많이 보는 화면은 대시보드인 경우가 많다.

Elastic 공식 문서는 대시보드를 여러 visualizations와 searches를 모아 보여주는 화면이라고 설명한다. [5]

즉, 대시보드는 아래처럼 이해하면 된다.

```text
여러 개의 그래프와 조회 화면을
한 페이지에 모아둔 관제판
```

예를 들어 운영 대시보드는 아래 패널들을 한 번에 보여줄 수 있다.

1. 최근 1시간 에러 건수
2. API별 요청량
3. 5xx 응답 비율
4. 최근 장애 로그 테이블
5. 특정 서비스 상태 요약

그래서 Kibana는 단순 조회 도구를 넘어 "운영 상황판" 역할도 한다.

---

## 6. 왜 Kibana가 로그 분석에 유용할까?

로그를 그냥 텍스트 파일로만 보면 아래 문제가 있다.

1. 원하는 조건으로 찾기 어렵다.
2. 여러 서버 로그를 한눈에 비교하기 어렵다.
3. 시간대별 변화 추세를 보기 어렵다.
4. 집계와 시각화가 번거롭다.

반면 Kibana를 사용하면 아래가 쉬워진다.

1. 필터로 빠르게 검색
2. 시간 범위로 조회
3. 그래프로 추세 파악
4. 대시보드로 공유

즉, Kibana는 "로그를 파일처럼 읽는 경험"을 "데이터를 탐색하는 경험"으로 바꿔준다.

---

## 7. Kibana는 Elasticsearch 없이 쓸 수 있을까?

일반적인 ELK/Elastic Stack 맥락에서는 Kibana는 Elasticsearch 데이터를 대상으로 동작한다.

Elastic 공식 문서도 Kibana를 Elasticsearch 데이터에 대한 인터페이스로 설명한다. [1][2]

즉, Kibana 자체가 로그를 직접 저장하는 도구는 아니다.

정리하면 아래와 같다.

1. Elasticsearch
   - 데이터를 저장하고 검색
2. Kibana
   - 그 데이터를 조회하고 시각화

즉, Kibana는 "저장소"가 아니라 "화면과 분석 도구"에 가깝다.

---

## 8. 실무에서는 어떻게 쓰일까?

실무에서는 보통 아래 흐름으로 많이 사용한다.

```text
애플리케이션 로그 수집
-> Elasticsearch 저장
-> Kibana Discover에서 검색
-> Kibana Visualization/Lens로 그래프 생성
-> Kibana Dashboard로 운영 화면 구성
```

예를 들어 장애가 났을 때는 아래 순서가 자연스럽다.

1. Discover에서 에러 로그 검색
2. 시간 범위 좁히기
3. 특정 trace id로 상세 흐름 확인
4. Dashboard에서 같은 시각의 에러량 추세 확인

즉, Kibana는 단순 시각화 툴이 아니라, 검색과 시각화와 공유를 한 곳에 모아둔 운영 분석 도구다.

---

## 정리

Kibana의 핵심 기능은 Elasticsearch에 쌓인 데이터를 조회하고, 분석하고, 시각화하고, 대시보드로 구성하는 것이다.

핵심만 정리하면 아래와 같다.

1. Kibana는 Elasticsearch 데이터에 쿼리를 실행할 수 있다.
2. Discover를 통해 데이터를 검색하고 필터링할 수 있다.
3. Lens와 시각화 기능으로 그래프, 표, 메트릭을 만들 수 있다.
4. Dashboard로 여러 시각화를 한 화면에 모아 운영 관제판처럼 쓸 수 있다.
5. 그래서 Kibana는 로그 분석에서 매우 중요한 UI 역할을 한다.

즉, Kibana는 "Elasticsearch 데이터를 사람이 이해할 수 있는 화면으로 바꿔주는 도구"라고 이해하면 된다.

---

## 출처

1. Elastic, "Kibana", https://www.elastic.co/kibana
2. Elastic Docs, "Explore and analyze data with Kibana", https://www.elastic.co/docs/explore-analyze
3. Elastic Docs, "Discover", https://www.elastic.co/docs/explore-analyze/discover
4. Elastic Docs, "Lens", https://www.elastic.co/docs/explore-analyze/visualize/lens
5. Elastic Docs, "Exploring dashboards", https://www.elastic.co/docs/explore-analyze/dashboards/using
