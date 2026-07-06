---
title: Monitoring Need And Tools
category: m
date: 2026-07-07 00:00:10 +0900
tags: [monitoring, actuator, prometheus, grafana, metrics, observability]
---

## 1. 모니터링이란 무엇일까?

모니터링은 서버와 애플리케이션의 상태를 지속적으로 관찰하는 것이다.

Spring Boot 공식 문서는 production 환경에서 애플리케이션을 monitor and manage 하기 위한 기능을 Actuator가 제공한다고 설명한다. [1]
Prometheus 공식 문서는 Prometheus를 systems monitoring and alerting toolkit이라고 설명한다. [2]

즉, 모니터링은 아래와 같은 것을 계속 추적하는 일이다.

1. 서버가 살아 있는지
2. CPU와 메모리가 얼마나 쓰이는지
3. 응답시간이 느려지고 있는지
4. 에러가 늘고 있는지
5. 서비스가 정상 동작 중인지

비유를 쓰면, 서버에 24시간 청진기를 대고 심장 박동처럼 metric을 듣는 것에 가깝다.

즉, 모니터링은 "문제가 터진 뒤 로그를 읽는 것"이 아니라, 문제가 생기기 전부터 상태를 계속 관찰하는 활동이다.

---

## 2. 왜 모니터링이 필요할까?

모니터링 없이 서버를 운영하는 것은, 지금 시스템이 어떤 상태인지 모르고 운영하는 것과 비슷하다.

예를 들어 아래 상황을 실시간으로 모른다면 위험하다.

1. CPU가 95%까지 올라간 상태
2. 메모리가 거의 다 찬 상태
3. 에러율이 갑자기 증가한 상태
4. DB 응답이 점점 느려지는 상태

즉, 겉으로는 애플리케이션이 아직 응답하고 있어도 내부에서는 이미 장애가 시작되고 있을 수 있다.

Prometheus 공식 문서도 모니터링 시스템이 단순 저장소가 아니라, 시간에 따른 변화를 관찰하고 문제를 찾는 데 쓰인다고 설명한다. [2][3]

---

## 3. 모니터링이 필수인 첫 번째 이유 - 사전 예방

모니터링이 있으면 문제가 실제 장애로 터지기 전에 조짐을 볼 수 있다.

예를 들어 아래처럼 해석할 수 있다.

1. 메모리 사용량이 평소보다 빠르게 증가한다.
2. 요청량이 특정 시간대마다 급증한다.
3. 특정 API 응답시간이 평소보다 길어진다.

이런 징후를 미리 보면

1. 서버를 미리 증설하거나
2. 캐시를 조정하거나
3. 비효율 쿼리를 고치거나
4. 배치 시간을 조정하는

대응이 가능하다.

즉, 모니터링은 장애가 난 뒤 대응하는 도구이기도 하지만, 더 중요한 역할은 장애가 나기 전에 징후를 감지하는 것이다.

---

## 4. 두 번째 이유 - 빠른 원인 파악

서비스가 느려졌다고 해서 항상 코드가 문제인 것은 아니다.

예를 들어 웨이팅 등록이 갑자기 느려졌다면 원인은 여러 가지일 수 있다.

1. 애플리케이션 CPU 과부하
2. GC 증가
3. DB 응답 지연
4. 외부 API 호출 지연
5. 요청량 급증

이때 모니터링 대시보드가 있으면 "무슨 계층이 먼저 이상해졌는지"를 빠르게 좁혀갈 수 있다.

예를 들어

1. 애플리케이션 CPU는 정상
2. DB 대기시간은 급증
3. 에러율은 DB timeout 위주

라면, 코드 전체보다 DB 병목을 우선 의심할 수 있다.

즉, 모니터링은 장애 원인을 빠르게 분리해내는 데 매우 중요하다.

---

## 5. 세 번째 이유 - 용량 계획

모니터링은 지금 상태만 보는 용도에 그치지 않는다.
앞으로 얼마나 자원이 더 필요할지 예측하는 데도 중요하다.

예를 들어 크리스마스이브, 유명 맛집 이벤트, 티켓 오픈 같은 날에는 트래픽이 평소보다 훨씬 커질 수 있다.

그럴 때 아래 데이터를 참고할 수 있다.

1. 평소 CPU 사용량
2. 피크 시간 요청량
3. 메모리 증가 속도
4. 에러율 변화
5. 응답시간 변화

즉, 모니터링은 단순한 현재 상태 확인을 넘어 capacity planning의 기초 자료가 된다.

---

## 6. Spring Boot Actuator는 무슨 역할을 할까?

Spring Boot Actuator는 운영 환경에서 애플리케이션을 모니터링하고 관리할 수 있는 endpoint를 제공한다.

Spring Boot 공식 문서는 Actuator endpoint를 통해 HTTP나 JMX로 애플리케이션을 monitor and interact 할 수 있다고 설명한다. [1][4]

예를 들어 아래 endpoint가 대표적이다.

1. `/actuator/health`
2. `/actuator/metrics`
3. `/actuator/prometheus`

여기서 중요한 점은 아래와 같다.

```text
Actuator는 메트릭 그 자체를 장기 저장하는 도구가 아니라
애플리케이션 상태와 메트릭을 노출하는 쪽에 가깝다.
```

또한 Spring Boot 공식 문서는 Actuator가 Micrometer와 연동되어 여러 모니터링 시스템으로 metric을 내보낼 수 있다고 설명한다. [5]

즉, Actuator는 "우리 애플리케이션의 건강 상태를 밖에서 읽을 수 있게 열어주는 창구"라고 보면 된다.

---

## 7. Prometheus는 무슨 역할을 할까?

Prometheus는 노출된 metric을 주기적으로 수집하고 저장하는 모니터링 시스템이다.

Prometheus 공식 문서는 monitored target의 metrics HTTP endpoint를 scraping 해서 데이터를 수집한다고 설명한다. [6]

즉, 흐름은 보통 아래와 같다.

```text
Spring Boot Actuator가 메트릭 노출
-> Prometheus가 주기적으로 읽음(scrape)
-> 시계열 데이터로 저장
```

Prometheus 공식 문서는 모든 데이터를 time series로 저장한다고 설명한다. [7]

즉, Prometheus는 아래 역할을 맡는다.

1. metric 수집
2. 시계열 저장
3. 쿼리
4. 알림 규칙 기반 경고

그래서 Prometheus는 단순 수집기가 아니라 metrics monitoring 시스템 자체라고 보는 편이 정확하다.

---

## 8. Grafana는 무슨 역할을 할까?

Grafana는 수집된 데이터를 사람이 보기 쉬운 그래프와 대시보드로 보여주는 도구다.

Grafana 공식 문서는 Grafana가 metrics, logs, traces를 query, visualize, alert on, and explore 할 수 있게 해준다고 설명한다. [8][9]

또한 Grafana 공식 문서는 data source를 연결해 데이터를 질의하고, dashboards로 시각화한다고 설명한다. [10][11]

즉, Prometheus와 연결하면 아래 같은 화면을 만들 수 있다.

1. CPU 사용률 그래프
2. 메모리 사용량 그래프
3. 초당 요청 수
4. 에러율
5. 응답시간 패널

즉, Grafana는 "수집된 수치를 사람이 빠르게 읽고 판단하게 해주는 화면" 역할을 한다.

---

## 9. 세 도구를 한 번에 보면

이 세 가지를 같이 놓고 보면 역할 분리가 선명하다.

| 도구 | 역할 |
|---|---|
| Spring Boot Actuator | 애플리케이션 상태와 메트릭 노출 |
| Prometheus | 메트릭 수집, 저장, 조회, 알림 |
| Grafana | 그래프와 대시보드로 시각화 |

즉, 아주 단순하게는 아래처럼 이해하면 된다.

```text
Actuator = 우리 서버가 상태를 내보냄
Prometheus = 그 상태를 긁어와 모음
Grafana = 모아둔 수치를 보기 좋게 그림
```

---

## 10. 전체 흐름은 어떻게 될까?

입문 기준 전체 흐름은 보통 아래와 같다.

```text
Spring Boot 애플리케이션
-> Actuator가 health/metrics 노출
-> Prometheus가 주기적으로 scrape
-> Grafana가 Prometheus를 데이터 소스로 조회
-> 대시보드에서 시각화
```

즉, 이 구조가 있으면 운영자는 콘솔에 붙어 있지 않아도 서비스 상태를 계속 볼 수 있다.

---

## 정리

모니터링은 서버와 애플리케이션의 상태를 지속적으로 추적해서 장애를 예방하고, 원인을 빠르게 찾고, 용량 계획을 세우기 위한 활동이다.

핵심만 정리하면 아래와 같다.

1. Actuator는 애플리케이션의 health와 metrics를 노출한다.
2. Prometheus는 그 메트릭을 주기적으로 수집해 시계열 데이터로 저장한다.
3. Grafana는 수집된 데이터를 그래프와 대시보드로 시각화한다.
4. 모니터링은 장애 대응뿐 아니라 사전 예방과 capacity planning에도 중요하다.

즉, `Actuator -> Prometheus -> Grafana` 흐름을 이해하면 애플리케이션 모니터링의 큰 그림을 잡을 수 있다.

---

## 출처

1. Spring Boot Reference, "Production-ready Features", https://docs.spring.io/spring-boot/reference/actuator/index.html
2. Prometheus Docs, "Overview", https://prometheus.io/docs/introduction/overview/
3. Prometheus Homepage, https://prometheus.io/
4. Spring Boot Reference, "Monitoring and Management Over HTTP", https://docs.spring.io/spring-boot/reference/actuator/monitoring.html
5. Spring Boot Reference, "Metrics", https://docs.spring.io/spring-boot/reference/actuator/metrics.html
6. Prometheus Docs, "First steps with Prometheus", https://prometheus.io/docs/introduction/first_steps/
7. Prometheus Docs, "Data model", https://prometheus.io/docs/concepts/data_model/
8. Grafana Docs, "Introduction", https://grafana.com/docs/grafana/latest/introduction/
9. Grafana Docs, "About Grafana", https://grafana.com/docs/grafana/latest/introduction/
10. Grafana Docs, "Data sources", https://grafana.com/docs/grafana/latest/datasources/
11. Grafana Docs, "Dashboards", https://grafana.com/docs/grafana/latest/visualizations/dashboards/
