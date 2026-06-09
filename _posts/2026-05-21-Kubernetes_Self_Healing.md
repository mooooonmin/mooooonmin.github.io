---
title: 서버가 죽었을 때 자동으로 복구하는 기능
category: k
date: 2026-05-21 00:00:10 +0900
tags: [kubernetes, k8s, pod, deployment, self-healing, restart-policy]
---

## 1. Self-Healing이란?

Self-Healing은 문제가 생긴 컨테이너나 Pod를 Kubernetes가 원하는 상태에 맞게 다시 복구하는 동작을 의미한다.

Kubernetes에는 Self-Healing 기능이 있다. Kubernetes 공식 문서는 Self-Healing을 실패한 컨테이너를 자동으로 교체하고, 노드를 사용할 수 없을 때 워크로드를 다시 스케줄링하며, 시스템의 원하는 상태를 유지하는 기능으로 설명한다. [1]

쉽게 말하면 다음과 같다.

```text
서버 비정상 종료
-> Kubernetes가 이상 상태 감지
-> 컨테이너 재시작 또는 Pod 교체
-> 원하는 개수와 상태를 다시 맞춤
```

다만 모든 상황에서 같은 방식으로 복구되는 것은 아니다.

- Pod 안의 컨테이너가 종료되면 kubelet이 Pod의 `restartPolicy`에 따라 컨테이너를 재시작할 수 있다. [2]
- Deployment가 관리하는 Pod 자체가 실패하면 Kubernetes는 지정된 replica 수를 유지하기 위해 대체 Pod를 만들 수 있다. [1]

---

## 2. 실행 중인 컨테이너를 종료해보기

실행 중인 컨테이너를 조회한다.

```bash
docker ps
```

특정 컨테이너를 종료한다.

```bash
docker kill 8c085c887430
```

위 명령어에서 `8c085c887430`은 예시 컨테이너 ID다. 실제 실습에서는 `docker ps`로 확인한 컨테이너 ID를 사용해야 한다.

여기서 주의할 점은 Kubernetes 클러스터 환경에 따라 컨테이너 런타임이 Docker가 아닐 수 있다는 점이다. 이 글의 예시는 Docker Desktop 또는 Docker 기반 실습 환경에서 컨테이너를 강제로 종료하는 상황을 가정한다.

---

## 3. Pod 상태 확인하기

컨테이너를 종료한 뒤 Pod 목록을 확인한다.

```bash
kubectl get pods
```

예시는 다음과 비슷하게 보일 수 있다.

```text
NAME                                  READY   STATUS    RESTARTS   AGE
spring-deployment-xxxxxxxxxx-aaaaa    1/1     Running   1          10m
spring-deployment-xxxxxxxxxx-bbbbb    1/1     Running   0          10m
spring-deployment-xxxxxxxxxx-ccccc    1/1     Running   0          10m
spring-deployment-xxxxxxxxxx-ddddd    1/1     Running   0          10m
spring-deployment-xxxxxxxxxx-eeeee    1/1     Running   0          10m
```

여전히 5개의 Pod가 실행 중이고, 첫 번째 Pod의 `RESTARTS` 값이 `1`로 증가한 것을 볼 수 있다.

`RESTARTS` 값이 증가했다는 것은 해당 Pod 안의 컨테이너가 한 번 재시작됐다는 뜻으로 이해할 수 있다. Kubernetes 공식 문서에 따르면 Pod의 `spec`에는 `restartPolicy` 필드가 있고, 값은 `Always`, `OnFailure`, `Never` 중 하나다. 기본값은 `Always`다. [2]

Deployment로 만든 일반적인 애플리케이션 Pod는 보통 컨테이너가 종료되면 같은 Pod 안에서 컨테이너가 다시 시작된다. 그래서 Pod 개수는 그대로 5개로 보이지만, 종료됐던 컨테이너가 재시작되면서 `RESTARTS` 값이 증가한다.

---

## 4. Deployment가 Pod 개수를 유지하는 방식

앞의 예시는 컨테이너가 종료되고 같은 Pod 안에서 컨테이너가 다시 시작된 상황이다.

반대로 Pod 자체가 삭제되거나 실패해서 사라지는 상황도 있다. Deployment가 `replicas: 5`로 설정되어 있다면 Kubernetes는 실제 Pod 수가 5개가 되도록 다시 맞추려고 한다.

Kubernetes 공식 문서는 Deployment나 StatefulSet 안의 Pod가 실패하면 Kubernetes가 지정된 replica 수를 유지하기 위해 대체 Pod를 만든다고 설명한다. [1]

즉, Deployment의 관점에서는 다음 상태를 계속 유지하려고 한다.

```text
원하는 상태: Pod 5개
실제 상태: Pod 4개
-> Kubernetes가 Pod 1개를 새로 생성
-> 실제 상태: Pod 5개
```

---

## 5. Self-Healing 동작 흐름

Kubernetes의 Self-Healing은 크게 두 가지 흐름으로 이해하면 된다.

```text
1. 컨테이너가 종료됨
   -> restartPolicy에 따라 컨테이너 재시작

2. Deployment가 관리하는 Pod가 실패하거나 사라짐
   -> replica 수를 맞추기 위해 대체 Pod 생성
```

따라서 "서버가 죽었는데 다시 살아났다"는 현상은 상황에 따라 다음 중 하나일 수 있다.

- 같은 Pod 안의 컨테이너가 재시작된 경우
- Deployment가 새 Pod를 만들어 replica 수를 다시 맞춘 경우

---

## 정리

Kubernetes는 Pod 안의 컨테이너가 종료되면 `restartPolicy`에 따라 컨테이너를 자동으로 재시작할 수 있다. [2]

또한 Deployment가 관리하는 Pod가 실패하면 Kubernetes는 지정된 replica 수를 유지하기 위해 대체 Pod를 만들 수 있다. [1]

이처럼 장애가 발생했을 때 Kubernetes가 원하는 상태를 다시 맞추려고 동작하는 기능을 Self-Healing이라고 한다. [1]

---

## 출처

[1] Kubernetes Docs, "Kubernetes Self-Healing", 확인일: 2026-05-20, <https://kubernetes.io/docs/concepts/architecture/self-healing/>

[2] Kubernetes Docs, "Pod Lifecycle", 확인일: 2026-05-20, <https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/>
