---
title: Kubernetes
category: k
date: 2026-05-18 00:00:10 +0900
tags: [kubernetes, k8s, container, docker, orchestration]
---

## 1. 쿠버네티스(Kubernetes)란?

쿠버네티스(Kubernetes)는 **컨테이너화된 워크로드와 서비스를 관리하기 위한 오픈 소스 플랫폼**이다. Kubernetes 공식 문서는 Kubernetes를 컨테이너화된 워크로드와 서비스를 관리하고, 선언적 설정과 자동화를 쉽게 해주는 이식 가능하고 확장 가능한 오픈 소스 플랫폼으로 설명한다. [1]

쉽게 말하면, 애플리케이션을 컨테이너로 실행할 때 여러 컨테이너를 어떻게 배포하고, 늘리고, 줄이고, 장애가 났을 때 복구할지 관리해주는 시스템이다.

Docker Compose와 비슷하게 느껴질 수 있다. Docker Compose도 여러 컨테이너로 구성된 애플리케이션을 정의하고 실행하는 도구이기 때문이다. Docker 공식 문서는 Compose를 멀티 컨테이너 애플리케이션을 정의하고 실행하는 도구라고 설명한다. [2]

다만 Kubernetes를 정확히 말하면 Docker Compose의 단순한 확장판은 아니다. Compose는 보통 하나의 YAML 파일로 서비스, 네트워크, 볼륨을 정의하고 한 명령으로 실행하는 도구에 가깝다. [2] 반면 Kubernetes는 클러스터 안에서 사용자가 선언한 원하는 상태와 실제 상태가 맞아지도록 여러 control process가 계속 동작하는 플랫폼이다. Kubernetes 공식 문서도 Kubernetes가 단순한 orchestration system이 아니라, 현재 상태를 원하는 상태로 계속 맞추는 독립적인 control process들의 집합이라고 설명한다. [3]

그래서 처음 이미지를 잡을 때는 다음처럼 이해하면 된다.

> Docker Compose가 로컬 또는 작은 규모의 멀티 컨테이너 실행을 쉽게 해주는 도구라면, Kubernetes는 여러 서버로 구성된 클러스터에서 컨테이너 기반 애플리케이션을 배포, 확장, 복구, 관리하는 플랫폼이다. [1][2][3]

---

## 2. 쿠버네티스의 장점

### 2.1. 컨테이너 관리 자동화

Kubernetes는 선언적 설정과 자동화를 지원한다. [1]

예를 들어 사용자가 "이 애플리케이션을 몇 개 실행하고 싶다"는 상태를 정의하면, Kubernetes는 실제 상태가 그 선언에 맞도록 동작한다. Kubernetes 공식 문서는 Kubernetes가 현재 상태를 사용자가 제공한 원하는 상태로 계속 맞추는 control process들로 구성된다고 설명한다. [3]

또한 Deployment를 사용하면 애플리케이션 업데이트와 롤백을 관리할 수 있다. Kubernetes 공식 문서에 따르면 Deployment의 rollout 이력은 기본적으로 보관되며, 필요할 때 rollback할 수 있다. [4]

---

### 2.2. 부하 분산

Kubernetes에서는 Service를 사용해 여러 Pod에 접근하는 안정적인 진입점을 만들 수 있다. Kubernetes 공식 문서는 Service가 selector와 일치하는 Pod들을 계속 스캔하고, Service의 EndpointSlice 집합을 필요한 상태로 갱신한다고 설명한다. [5]

외부에서 접근해야 하는 서비스라면 `LoadBalancer` 타입을 사용할 수 있다. Kubernetes 공식 문서는 `LoadBalancer` 타입 Service가 외부 로드 밸런서를 사용해 Service를 외부로 노출한다고 설명한다. 다만 Kubernetes 자체가 직접 로드 밸런싱 컴포넌트를 제공하는 것은 아니며, 별도의 로드 밸런서를 제공하거나 클라우드 제공자와 통합해야 한다. [6]

---

### 2.3. 쉬운 스케일링

Kubernetes는 애플리케이션을 수동 또는 자동으로 확장할 수 있다.

Kubernetes 공식 문서는 애플리케이션을 명령어, UI 또는 CPU 사용량에 따라 자동으로 scale up/down 할 수 있다고 설명한다. [7]

자동 확장은 HorizontalPodAutoscaler를 통해 할 수 있다. Kubernetes 공식 문서에 따르면 HorizontalPodAutoscaler는 Deployment나 StatefulSet 같은 workload resource의 용량을 수요에 맞게 자동으로 조정한다. [8]

---

### 2.4. 셀프 힐링

Kubernetes의 중요한 장점 중 하나는 self-healing이다.

Kubernetes 공식 문서는 Kubernetes가 실패한 컨테이너를 재시작하고, 컨테이너를 교체하며, 사용자가 정의한 health check에 응답하지 않는 컨테이너를 종료하고, 준비되지 않은 컨테이너를 클라이언트에 노출하지 않는다고 설명한다. [7]

즉, 컨테이너나 애플리케이션 일부에 문제가 생겼을 때 사람이 매번 직접 재시작하지 않아도 Kubernetes가 정해진 규칙에 따라 복구를 시도할 수 있다.

---

## 정리

쿠버네티스는 여러 컨테이너를 실행하는 것에서 끝나지 않고, 컨테이너 기반 애플리케이션을 안정적으로 운영하기 위한 플랫폼이다.

핵심은 다음과 같다.

- Kubernetes는 컨테이너화된 워크로드와 서비스를 관리하는 오픈 소스 플랫폼이다. [1]
- Docker Compose와 비슷하게 여러 컨테이너를 다룰 수 있지만, Kubernetes는 클러스터에서 원하는 상태를 계속 유지하는 플랫폼이라는 점이 다르다. [2][3]
- 배포, 확장, 업데이트, 롤백 같은 운영 작업을 자동화하는 데 도움을 준다. [1][4]
- Service와 LoadBalancer 타입을 통해 서비스 접근과 부하 분산 구성을 지원한다. [5][6]
- HorizontalPodAutoscaler를 통해 수요에 맞춘 자동 확장이 가능하다. [8]
- 실패한 컨테이너 재시작, 교체, health check 기반 제외 같은 self-healing 기능을 제공한다. [7]

---

## 출처

확인일: 2026-05-14

[1] Kubernetes Documentation, Overview: <https://kubernetes.io/docs/concepts/overview/>
[2] Docker Docs, Docker Compose: <https://docs.docker.com/compose/>
[3] Kubernetes Documentation, What Kubernetes is not: <https://kubernetes.io/docs/concepts/overview/#what-kubernetes-is-not>
[4] Kubernetes Documentation, Deployments - Rolling Back a Deployment: <https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#rolling-back-a-deployment>
[5] Kubernetes Documentation, Service - Defining a Service: <https://kubernetes.io/docs/concepts/services-networking/service/#defining-a-service>
[6] Kubernetes Documentation, Service type - LoadBalancer: <https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer>
[7] Kubernetes Documentation, Why you need Kubernetes and what it can do: <https://kubernetes.io/docs/concepts/overview/#why-you-need-kubernetes-and-what-it-can-do>
[8] Kubernetes Documentation, Horizontal Pod Autoscaling: <https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/>
