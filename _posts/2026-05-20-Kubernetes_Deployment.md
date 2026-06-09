---
title: Kubernetes Deployment
category: k
date: 2026-05-20 00:00:10 +0900
tags: [kubernetes, k8s, deployment, replicaset, pod]
---

## 1. 디플로이먼트(Deployment)란?

디플로이먼트(Deployment)는 여러 Pod를 원하는 상태로 유지하고, 업데이트와 롤백을 쉽게 관리하기 위한 Kubernetes 리소스다.

디플로이먼트(Deployment)는 애플리케이션 워크로드를 실행하기 위한 파드(Pod) 집합을 관리하는 Kubernetes 리소스다. Kubernetes 공식 문서는 Deployment가 보통 상태를 유지하지 않는 애플리케이션 워크로드를 실행하기 위해 Pod 집합을 관리한다고 설명한다. [1]

또한 Deployment는 Pod와 ReplicaSet에 대한 선언적 업데이트를 제공한다. 즉, 사용자가 Deployment에 원하는 상태를 적어두면 Deployment 컨트롤러가 실제 상태를 원하는 상태로 바꾸는 방식으로 동작한다. [1]

현업에서는 일반적으로 서버를 작동시킬 때 Pod를 직접 하나씩 수동으로 배포하기보다는 Deployment를 사용해 Pod를 생성하고 관리하는 경우가 많다. Kubernetes 공식 문서도 보통 Pod를 직접 만들 필요가 없으며, Deployment나 Job 같은 워크로드 리소스를 사용해 Pod를 만들라고 설명한다. [2]

쉽게 말하면 다음과 같다.

```text
Deployment = 같은 역할을 하는 Pod 여러 개를 자동으로 만들고 관리하는 단위
```

---

## 2. 디플로이먼트(Deployment)의 장점

### 2.1. 원하는 개수만큼 Pod를 쉽게 생성할 수 있다

Deployment에는 `replicas` 값을 지정할 수 있다.

예를 들어 `replicas: 3`이라고 설정하면 Deployment가 ReplicaSet을 만들고, 그 ReplicaSet이 3개의 복제된 Pod를 생성한다. Kubernetes 공식 문서의 Deployment 예시에서도 `.spec.replicas` 필드가 3개의 복제 Pod를 만들도록 지정한다고 설명한다. [1]

```yaml
spec:
  replicas: 3
```

즉, 사용자가 직접 Pod 3개를 하나씩 작성하는 것이 아니라 "이 구성의 Pod를 3개 유지해줘"라고 선언하는 방식이다.

---

### 2.2. Pod 수를 유지한다

Deployment가 직접 Pod를 하나하나 관리한다기보다는, Deployment가 ReplicaSet을 만들고 ReplicaSet이 Pod 수를 맞추는 구조로 이해하면 된다. [1][3]

ReplicaSet의 목적은 특정 시점에 안정적인 복제 Pod 집합을 유지하는 것이다. Kubernetes 공식 문서는 ReplicaSet이 지정된 수의 동일한 Pod가 사용 가능하도록 보장하는 데 사용된다고 설명한다. [3]

예를 들어 `replicas: 3`으로 설정했는데 Pod 1개가 사라지면, ReplicaSet은 다시 Pod를 만들어 원하는 개수에 맞추려고 한다. Kubernetes 공식 문서에 따르면 ReplicaSet은 필요한 경우 Pod를 생성하거나 삭제해서 원하는 복제본 수에 도달한다. [3]

---

### 2.3. 여러 Pod를 한 번에 업데이트할 수 있다

Deployment는 Pod 템플릿을 변경하면 새로운 ReplicaSet을 만들고, 새 ReplicaSet을 점진적으로 늘리면서 기존 ReplicaSet을 줄이는 방식으로 Pod를 교체한다. Kubernetes 공식 문서는 Deployment의 PodTemplateSpec을 업데이트하면 새 ReplicaSet이 생성되고, Deployment가 새 ReplicaSet을 늘리는 동시에 기존 ReplicaSet을 줄인다고 설명한다. [1]

예를 들어 Nginx 이미지를 `nginx:1.14.2`에서 `nginx:1.16.1`로 바꾸면 Deployment rollout이 진행된다. Kubernetes 공식 문서에 따르면 Deployment의 rollout은 `.spec.template`이 변경될 때 발생한다. [1]

즉, "100개의 Pod로 떠 있는 결제 서버"가 있다면 각 Pod를 하나씩 수정하는 것이 아니라 Deployment의 Pod 템플릿을 수정해 일괄 업데이트할 수 있다.

---

### 2.4. 롤백할 수 있다

Deployment는 rollout 이력을 이용해 이전 revision으로 되돌릴 수 있다. Kubernetes 공식 문서는 Deployment가 안정적이지 않은 상태, 예를 들어 crash looping 상태가 되었을 때 이전 Deployment revision으로 rollback할 수 있다고 설명한다. [1]

예를 들어 새 버전 배포 후 문제가 생기면 다음과 같은 명령으로 이전 상태로 되돌릴 수 있다.

```bash
kubectl rollout undo deployment/nginx-deployment
```

---

### 2.5. 일시 중지와 재개가 가능하다

Deployment rollout은 일시 중지했다가 다시 재개할 수 있다. Kubernetes 공식 문서는 PodTemplateSpec에 여러 수정 사항을 적용한 뒤 새 rollout을 시작하기 위해 Deployment rollout을 pause/resume할 수 있다고 설명한다. [1]

```bash
kubectl rollout pause deployment/nginx-deployment
kubectl rollout resume deployment/nginx-deployment
```

---

## 3. 디플로이먼트(Deployment)의 구조

Deployment는 다음 구조로 이해할 수 있다.

```text
Deployment
└── ReplicaSet
    ├── Pod
    ├── Pod
    └── Pod
```

핵심은 다음과 같다.

- Deployment는 ReplicaSet을 관리한다. [1][3]
- ReplicaSet은 Pod 복제본 수를 유지한다. [3]
- Pod는 Kubernetes에서 만들고 관리할 수 있는 가장 작은 배포 단위다. [2]

정리하면 다음과 같다.

```text
Deployment가 ReplicaSet을 관리하고,
ReplicaSet이 여러 Pod를 관리한다.
```

여기서 Replica는 복제본을 의미하고, ReplicaSet은 복제본 Pod들의 묶음을 의미한다고 이해하면 된다. Kubernetes 공식 문서도 ReplicaSet을 "replica Pods"의 안정적인 집합을 유지하는 리소스로 설명한다. [3]

---

## 4. Deployment 매니페스트 예시

아래 예시는 Nginx Pod 3개를 유지하는 Deployment다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.26.4
          ports:
            - containerPort: 80
```

각 항목의 의미는 다음과 같다.

- `apiVersion: apps/v1`: Deployment는 `apps/v1` API를 사용한다. Kubernetes 공식 예시도 Deployment에 `apps/v1`을 사용한다. [1]
- `kind: Deployment`: 생성할 리소스 종류가 Deployment임을 의미한다.
- `metadata.name`: Deployment의 이름이다.
- `spec.replicas`: 유지할 Pod 복제본 수다. [1]
- `spec.selector.matchLabels`: 이 Deployment가 관리할 Pod를 찾는 기준이다. [1]
- `spec.template`: 새 Pod를 만들 때 사용할 Pod 템플릿이다. [1]
- `spec.template.metadata.labels`: Pod에 붙일 라벨이다. Deployment의 selector와 맞아야 한다. Kubernetes 공식 문서는 Deployment에서 적절한 selector와 Pod template label을 지정해야 한다고 설명한다. [1]
- `spec.template.spec.containers`: Pod 안에서 실행할 컨테이너 목록이다.

---

## 5. Deployment 생성과 확인

매니페스트 파일을 적용한다.

```bash
kubectl apply -f nginx-deployment.yaml
```

Deployment 상태를 확인한다.

```bash
kubectl get deployments
```

ReplicaSet을 확인한다.

```bash
kubectl get rs
```

Pod를 확인한다.

```bash
kubectl get pods
```

Kubernetes 공식 문서의 Deployment 생성 예시에서도 Deployment를 만든 뒤 `kubectl get deployments`, `kubectl get rs`, `kubectl get pods --show-labels`로 Deployment, ReplicaSet, Pod를 확인한다. [1]

---

## 정리

Deployment는 Pod를 직접 하나씩 관리하지 않고, 원하는 상태를 선언해서 Pod 집합을 관리하는 Kubernetes 리소스다. [1]

구조는 다음과 같다.

```text
Deployment -> ReplicaSet -> Pod
```

따라서 Deployment를 사용하면 다음 작업을 쉽게 할 수 있다.

- 같은 구성의 Pod 여러 개 생성 [1]
- 지정한 Pod 개수 유지 [3]
- Pod 일괄 업데이트 [1]
- 이전 revision으로 롤백 [1]
- rollout 일시 중지와 재개 [1]

---

## 출처

[1] Kubernetes Docs, "Deployments", 확인일: 2026-05-19, <https://kubernetes.io/docs/concepts/workloads/controllers/deployment/>

[2] Kubernetes Docs, "Pods", 확인일: 2026-05-19, <https://kubernetes.io/docs/concepts/workloads/pods/>

[3] Kubernetes Docs, "ReplicaSet", 확인일: 2026-05-19, <https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/>
