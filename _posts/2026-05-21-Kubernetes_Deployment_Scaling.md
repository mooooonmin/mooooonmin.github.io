---
title: 디플로이먼트를 활용한 서버 개수 조절 방법
category: k
date: 2026-05-21 00:00:00 +0900
tags: [kubernetes, k8s, deployment, scaling, replicas, kubectl]
---

## 1. 서버 개수를 늘리고 싶다면?

트래픽이 늘어나서 서버를 5개로 늘리고 싶다면 Deployment의 `replicas` 값을 수정하면 된다.

Kubernetes에서 Deployment는 Pod 집합을 관리하는 리소스다. Kubernetes 공식 문서는 Deployment가 Pod와 ReplicaSet에 대한 선언적 업데이트를 제공한다고 설명한다. [1]

여기서 `replicas`는 유지하고 싶은 Pod 복제본 수를 의미한다. 예를 들어 `replicas: 5`로 설정하면 Kubernetes는 같은 템플릿으로 만들어진 Pod가 5개가 되도록 조정한다. Kubernetes 공식 문서의 Deployment 예시에서도 `.spec.replicas` 필드가 복제 Pod의 수를 지정한다고 설명한다. [1]

쉽게 말하면 다음과 같다.

```text
replicas: 5
= 같은 서버 역할을 하는 Pod 5개를 유지해줘
```

---

## 2. 매니페스트 파일 수정하기

`spring-deployment.yaml` 파일의 `spec.replicas` 값을 `5`로 수정한다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spring-deployment
spec:
  replicas: 5
  selector:
    matchLabels:
      app: backend-app
  template:
    metadata:
      labels:
        app: backend-app
    spec:
      containers:
        - name: spring-container
          image: spring-server
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8080
```

핵심은 이 부분이다.

```yaml
replicas: 5
```

이 값은 Deployment가 유지하려는 Pod 개수다. Kubernetes 공식 문서에 따르면 Deployment는 ReplicaSet을 만들고, ReplicaSet은 지정된 수의 동일한 Pod가 사용 가능하도록 보장하는 데 사용된다. [1][2]

---

## 3. 변경사항 적용하기

매니페스트 파일을 수정한 뒤 다음 명령어로 적용한다.

```bash
kubectl apply -f spring-deployment.yaml
```

`kubectl apply`는 파일 또는 표준 입력으로 전달한 설정을 리소스에 적용하는 명령어다. Kubernetes 공식 `kubectl` 참고 문서도 `apply`를 파일명, 디렉터리, URL로 리소스 설정을 적용하는 명령어로 설명한다. [3]

따라서 처음 Deployment를 만들 때도 사용할 수 있고, 이미 만들어진 Deployment의 변경사항을 반영할 때도 사용할 수 있다.

---

## 4. 잘 적용됐는지 확인하기

Pod 목록을 확인한다.

```bash
kubectl get pods
```

Deployment 상태도 함께 확인하면 더 명확하다.

```bash
kubectl get deployment spring-deployment
```

예상되는 방향은 `spring-deployment`가 관리하는 Pod가 5개로 늘어나는 것이다.

```text
NAME                                  READY   STATUS    RESTARTS   AGE
spring-deployment-xxxxxxxxxx-aaaaa    1/1     Running   0          1m
spring-deployment-xxxxxxxxxx-bbbbb    1/1     Running   0          1m
spring-deployment-xxxxxxxxxx-ccccc    1/1     Running   0          1m
spring-deployment-xxxxxxxxxx-ddddd    1/1     Running   0          1m
spring-deployment-xxxxxxxxxx-eeeee    1/1     Running   0          1m
```

다만 실제 Pod 이름, `AGE`, `STATUS` 값은 클러스터 상태와 이미지 Pull 성공 여부에 따라 달라질 수 있다.

---

## 5. 명령어로 바로 늘리는 방법

매니페스트 파일을 수정하지 않고 명령어로도 Deployment를 스케일링할 수 있다.

```bash
kubectl scale deployment spring-deployment --replicas=5
```

Kubernetes 공식 문서는 Deployment를 수동으로 스케일링할 때 `kubectl scale deployment ... --replicas=숫자` 형식을 사용할 수 있다고 설명한다. [4]

하지만 운영 설정을 매니페스트 파일로 관리하고 있다면 `spring-deployment.yaml`의 `replicas` 값도 같이 맞춰두는 것이 좋다. Kubernetes 공식 문서는 Deployment를 수동으로 스케일링한 뒤 매니페스트 기반으로 다시 `kubectl apply`를 실행하면, 매니페스트에 적힌 값이 수동 스케일링 값을 덮어쓴다고 설명한다. [1]

---

## 핵심 정리

Deployment로 서버 개수를 늘리는 흐름은 다음과 같다.

```text
1. spring-deployment.yaml에서 replicas 값을 5로 수정
2. kubectl apply -f spring-deployment.yaml 실행
3. kubectl get pods 또는 kubectl get deployment로 확인
```

즉, 서버 역할을 하는 Pod를 5개로 늘리고 싶다면 Deployment의 `replicas` 값을 `5`로 설정하면 된다.

---

## 출처

[1] Kubernetes Docs, "Deployments", 확인일: 2026-05-20, <https://kubernetes.io/docs/concepts/workloads/controllers/deployment/>

[2] Kubernetes Docs, "ReplicaSet", 확인일: 2026-05-20, <https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/>

[3] Kubernetes Docs, "kubectl apply", 확인일: 2026-05-20, <https://kubernetes.io/docs/reference/kubectl/generated/kubectl_apply/>

[4] Kubernetes Docs, "Horizontal Manual Scaling for a Deployment", 확인일: 2026-05-20, <https://kubernetes.io/docs/tasks/run-application/scale-deployment/>
