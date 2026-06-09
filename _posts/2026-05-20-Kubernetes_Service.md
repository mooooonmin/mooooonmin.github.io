---
title: Kubernetes Service
category: k
date: 2026-05-20 00:00:20 +0900
tags: [kubernetes, k8s, service, networking, load-balancing]
---

## 1. 서비스(Service)란?

서비스(Service)는 클러스터 안팎의 요청을 Pod로 안정적으로 전달하기 위한 Kubernetes 리소스다.

서비스(Service)는 Kubernetes 클러스터 안에서 실행 중인 하나 이상의 Pod로 네트워크 애플리케이션을 노출하는 방법이다. Kubernetes 공식 문서는 Service를 클러스터 안에서 하나 이상의 Pod로 실행되는 네트워크 애플리케이션을 노출하는 방법이라고 설명한다. [1]

쉽게 말하면 Service는 요청을 받는 고정된 입구 역할을 한다.

```text
Client -> Service -> Pod
```

실제 서비스에서 Pod에 요청을 보낼 때 매번 `kubectl port-forward`를 사용하거나, `kubectl exec`로 Pod 내부에 직접 들어가서 요청을 보내지는 않는다. 일반적으로는 Service를 통해 Pod에 접근한다.

그 이유는 Pod가 계속 같은 상태로 존재한다고 보장할 수 없기 때문이다. Kubernetes 공식 문서에 따르면 Deployment가 Pod를 동적으로 생성하고 삭제할 수 있으며, Pod는 클러스터의 원하는 상태에 맞춰 생성되고 삭제되는 일시적인 리소스다. [1]

즉, Pod IP는 바뀔 수 있다.

```text
기존 Pod 삭제 -> 새 Pod 생성 -> 새 Pod IP 할당
```

따라서 클라이언트가 Pod IP를 직접 기억하고 접근하면 문제가 생길 수 있다. Service는 이런 문제를 해결하기 위해 안정적인 접근 지점을 제공한다. Kubernetes 공식 문서는 Service API가 시간이 지나면서 개별 Pod가 바뀔 수 있는 상황에서도 하나 이상의 backend Pod로 구현된 서비스에 안정적인 IP 주소 또는 hostname을 제공한다고 설명한다. [2]

---

## 2. 서비스(Service)의 역할

### 2.1. 안정적인 접근 지점을 제공한다

Pod는 생성되고 삭제될 수 있지만, Service는 Service가 살아 있는 동안 고유한 IP 주소를 가진다. Kubernetes 공식 튜토리얼은 Service가 생성될 때 고유한 IP 주소인 `clusterIP`를 할당받고, 이 주소는 Service의 생명주기에 묶여 있으며 Service가 살아 있는 동안 바뀌지 않는다고 설명한다. [3]

즉, 클라이언트는 매번 Pod IP를 직접 찾을 필요 없이 Service 주소로 요청하면 된다.

```text
Client -> Service IP -> 현재 살아 있는 Pod들
```

---

### 2.2. Pod로 트래픽을 전달한다

Service는 selector를 사용해 어떤 Pod로 트래픽을 보낼지 결정한다. Kubernetes 공식 문서는 Service가 보통 사용자가 정의한 selector를 통해 대상 Pod 집합을 결정한다고 설명한다. [1]

예를 들어 Service에 다음 selector가 있다면,

```yaml
selector:
  app: nginx
```

`app: nginx` 라벨이 붙은 Pod들이 Service의 대상이 된다.

```text
Service selector: app=nginx

Pod A labels: app=nginx -> 대상
Pod B labels: app=nginx -> 대상
Pod C labels: app=api   -> 대상 아님
```

---

### 2.3. 로드밸런서처럼 동작한다

Service는 들어온 요청을 Service에 연결된 Pod 중 하나로 전달한다. Kubernetes 공식 튜토리얼은 Pod가 Service와 통신하도록 설정될 수 있고, Service로 향한 통신은 Service의 멤버인 어떤 Pod로 자동 load-balanced 된다고 설명한다. [3]

다만 여기서 "균등하게 분배한다"는 표현은 주의해야 한다. Service는 로드밸런싱 역할을 하지만, 모든 환경에서 요청 수가 정확히 같은 비율로 나뉜다고 단정할 수는 없다. Kubernetes 공식 문서도 `type: LoadBalancer` Service의 경우 외부 로드밸런서에서 들어온 트래픽이 backend Pod로 전달되며, 클라우드 제공자가 로드밸런싱 방식을 결정한다고 설명한다. [1]

따라서 처음 이해할 때는 다음처럼 정리하면 된다.

```text
Service는 요청을 받아 여러 Pod 중 하나로 분산 전달한다.
정확한 분배 방식은 Service 타입, kube-proxy, 클라우드 로드밸런서 구현에 따라 달라질 수 있다. [1][2][3]
```

---

## 3. 서비스(Service)의 구조

Service의 기본 구조는 다음과 같다.

```text
Client
  |
  v
Service
  |
  v
EndpointSlice
  |
  v
Pod A / Pod B / Pod C
```

각 요소의 역할은 다음과 같다.

- `Client`: Service로 요청을 보내는 주체다.
- `Service`: 고정된 접근 지점 역할을 한다. [1][2]
- `selector`: Service가 어떤 Pod를 대상으로 삼을지 결정한다. [1]
- `EndpointSlice`: Service 뒤에 있는 실제 네트워크 endpoint 정보를 담는다. Kubernetes 공식 문서는 EndpointSlice가 Service의 backend network endpoint 일부를 나타내는 객체라고 설명한다. [1]
- `Pod`: 실제 애플리케이션 컨테이너가 실행되는 단위다.

Kubernetes는 Service 뒤에 있는 Pod 집합이 바뀌면 EndpointSlice 정보를 갱신한다. Kubernetes 공식 문서는 Service의 Pod 집합이 바뀔 때마다 Kubernetes가 해당 Service의 EndpointSlice를 업데이트한다고 설명한다. [1]

예를 들어 `app: nginx` 라벨이 붙은 Pod가 3개 있다면 구조는 다음처럼 볼 수 있다.

```text
Service: nginx-service
selector: app=nginx

EndpointSlice
├── nginx-pod-1
├── nginx-pod-2
└── nginx-pod-3
```

---

## 4. Service 매니페스트 예시

아래 예시는 `app: nginx` 라벨이 붙은 Pod의 80번 포트로 요청을 전달하는 Service다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

각 항목의 의미는 다음과 같다.

- `apiVersion: v1`: Service는 core API group의 `v1` 버전을 사용한다.
- `kind: Service`: 생성할 리소스 종류가 Service임을 의미한다.
- `metadata.name`: Service의 이름이다.
- `spec.selector`: Service가 연결할 Pod를 찾는 기준이다. [1]
- `spec.ports.port`: Service가 노출하는 포트다. [1]
- `spec.ports.targetPort`: 실제 Pod 컨테이너가 요청을 받는 포트다. [1]

Kubernetes 공식 문서도 Service가 들어오는 `port`를 `targetPort`로 매핑할 수 있으며, 기본적으로 `targetPort`는 `port`와 같은 값으로 설정된다고 설명한다. [1]

---

## 5. Deployment와 Service 연결 예시

먼저 `app: nginx` 라벨을 가진 Pod를 만드는 Deployment가 있다고 하자.

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

그리고 Service를 다음처럼 만든다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

이때 연결 기준은 라벨이다.

```text
Service selector: app=nginx
Pod label:        app=nginx
```

즉, Service는 `app: nginx` 라벨이 붙은 Pod들을 찾아 요청을 전달한다.

---

## 6. Service 타입

Service에는 여러 타입이 있다. Kubernetes 공식 문서는 Service 타입으로 `ClusterIP`, `NodePort`, `LoadBalancer`, `ExternalName`을 설명한다. [1]

### 6.1. ClusterIP

`ClusterIP`는 클러스터 내부 IP로 Service를 노출한다. 이 타입을 선택하면 Service는 클러스터 내부에서만 접근할 수 있다. Service 타입을 명시하지 않으면 기본값은 `ClusterIP`다. [1]

```yaml
spec:
  type: ClusterIP
```

처음 Service를 공부할 때는 내부 통신용 Service라고 이해하면 쉽다.

---

### 6.2. NodePort

`NodePort`는 각 Node의 IP와 정적 포트를 통해 Service를 노출한다. Kubernetes 공식 문서는 NodePort Service에서 클러스터의 모든 Node가 할당된 포트를 listen하고, 해당 Service와 연결된 ready endpoint 중 하나로 트래픽을 전달한다고 설명한다. [1]

```yaml
spec:
  type: NodePort
```

처음 공부할 때는 외부에서 `<NodeIP>:<NodePort>` 형태로 접근할 수 있게 만드는 방식이라고 이해하면 된다.

---

### 6.3. LoadBalancer

`LoadBalancer`는 외부 로드밸런서를 사용해 Service를 외부로 노출한다. Kubernetes 공식 문서는 `LoadBalancer` 타입이 외부 로드밸런서를 사용해 Service를 외부로 노출하며, Kubernetes가 직접 로드밸런싱 컴포넌트를 제공하는 것은 아니므로 별도로 제공하거나 클라우드 제공자와 통합해야 한다고 설명한다. [1]

```yaml
spec:
  type: LoadBalancer
```

클라우드 환경에서 외부 사용자가 접근해야 하는 서비스에 자주 사용된다.

---

## 7. Service 생성과 확인

Service 매니페스트를 적용한다.

```bash
kubectl apply -f nginx-service.yaml
```

Service 목록을 확인한다.

```bash
kubectl get svc
```

Service 상세 정보를 확인한다.

```bash
kubectl describe svc nginx-service
```

EndpointSlice를 확인한다.

```bash
kubectl get endpointslices
```

Kubernetes 공식 튜토리얼도 Service를 확인할 때 `kubectl get svc`, `kubectl describe svc`, `kubectl get endpointslices`를 사용해 Service와 연결된 endpoint 정보를 확인한다. [3]

---

## 정리

Service는 Pod 앞에 서 있는 안정적인 네트워크 입구다.

```text
Client -> Service -> Pod
```

Service를 사용하는 이유는 다음과 같다.

- Pod IP가 바뀌어도 안정적인 접근 지점을 제공한다. [1][2][3]
- selector로 대상 Pod를 찾는다. [1]
- 요청을 연결된 Pod 중 하나로 분산 전달한다. [3]
- EndpointSlice를 통해 Service 뒤의 실제 endpoint 정보를 관리한다. [1][2]
- `ClusterIP`, `NodePort`, `LoadBalancer` 같은 타입으로 접근 범위를 정할 수 있다. [1]

따라서 실제 운영 환경에서는 Pod에 직접 접근하기보다는 Service를 통해 접근하는 방식이 일반적이다.

---

## 출처

[1] Kubernetes Docs, "Service", 확인일: 2026-05-19, <https://kubernetes.io/docs/concepts/services-networking/service/>

[2] Kubernetes Docs, "Services, Load Balancing, and Networking", 확인일: 2026-05-19, <https://kubernetes.io/docs/concepts/services-networking/>

[3] Kubernetes Docs, "Connecting Applications with Services", 확인일: 2026-05-19, <https://kubernetes.io/docs/tutorials/services/connect-applications-service/>
