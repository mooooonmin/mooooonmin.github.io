---
title: MySQL과 연결이 제대로 되지 않았다면 어떻게 될까?
category: docker-kubernetes
date: 2026-05-22 00:00:20 +0900
tags: [kubernetes, mysql, spring, deployment, troubleshooting, logs]
---

## 1. 실습 목표

Spring 애플리케이션이 MySQL에 연결하도록 설정되어 있을 때, DB 접속 정보가 잘못되면 어떤 일이 발생하는지 확인한다.

이번 실습에서는 `DB_PASSWORD` 값을 일부러 틀리게 설정한다.
그다음 Deployment를 다시 적용하고, Pod 상태와 로그를 확인한다.

다만 DB 연결 실패가 항상 같은 Pod 상태로 나타나는 것은 아니다.
애플리케이션이 DB 연결 실패를 만나자마자 종료되면 Pod가 재시작을 반복할 수 있고, 애플리케이션이 종료되지 않도록 구현되어 있다면 Pod는 `Running` 상태를 유지하면서 로그에만 연결 오류가 남을 수 있다.

Kubernetes 공식 문서에 따르면 `CrashLoopBackOff`는 컨테이너가 제대로 시작하지 못하고 반복적으로 실패할 때 `kubectl` 출력에서 볼 수 있는 상태 또는 이벤트다. 원인에는 애플리케이션 오류, 잘못된 환경 변수, 누락된 설정 파일 등이 포함될 수 있다. [1]

---

## 2. DB 정보를 일부러 틀리게 수정하기

먼저 Spring Deployment의 DB 비밀번호를 잘못된 값으로 바꾼다.

`spring-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spring-deployment
spec:
  replicas: 3
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
          env:
            - name: DB_HOST
              value: mysql-service
            - name: DB_PORT
              value: "3306"
            - name: DB_NAME
              value: kub-practice
            - name: DB_USERNAME
              value: root
            - name: DB_PASSWORD
              value: wrong-password
```

여기서 `DB_PASSWORD` 값을 실제 MySQL root 비밀번호와 다르게 설정했다.

`DB_HOST`에는 `mysql-service`를 사용한다.
같은 Kubernetes 클러스터 안에서 MySQL Service가 `mysql-service`라는 이름으로 만들어져 있다면, 애플리케이션은 이 Service 이름으로 MySQL에 접근할 수 있다.

---

## 3. Deployment 적용 및 재시작

수정한 매니페스트를 적용한다.

```bash
kubectl apply -f spring-deployment.yaml
```

Kubernetes 공식 문서에 따르면 `kubectl apply`는 파일 또는 표준 입력으로 전달한 설정을 리소스에 적용한다. 리소스가 아직 없다면 생성한다. [3]

이미 실행 중인 Pod를 새 설정으로 다시 띄우고 싶다면 Deployment를 재시작한다.

```bash
kubectl rollout restart deployment spring-deployment
```

Kubernetes 공식 문서에 따르면 `kubectl rollout restart`는 리소스의 rollout을 재시작하는 명령이다. [4]

---

## 4. Pod 상태 확인하기

Deployment를 다시 적용한 뒤 Pod 상태를 확인한다.

```bash
kubectl get pods
```

DB 연결 실패가 발생했을 때 볼 수 있는 대표적인 상황은 다음과 같다.

| 상태 | 의미 |
|---|---|
| `CrashLoopBackOff` | 애플리케이션이 DB 연결 실패 때문에 종료되고, 컨테이너가 반복 재시작되는 경우 |
| `Running` | 애플리케이션 프로세스는 살아 있지만, 내부적으로 DB 연결 오류를 로그로 남기는 경우 |
| `Running`이지만 Ready 아님 | readiness probe가 있고 DB 연결 실패를 준비 실패로 판단하는 경우 |

Kubernetes 공식 문서에 따르면 readiness probe가 실패하면 해당 Pod의 IP는 Service가 사용하는 EndpointSlice에서 제거된다. 또한 liveness probe가 실패하면 kubelet이 컨테이너를 종료하고 restart policy에 따라 다시 시작한다. [2]

즉, DB 연결 실패가 어떤 상태로 보이는지는 Spring 애플리케이션의 시작 방식, 예외 처리 방식, probe 설정 여부에 따라 달라진다.

---

## 5. 로그로 에러 메시지 확인하기

DB 정보가 잘못되었는지는 Pod 로그에서 확인하는 것이 가장 직접적이다.

```bash
kubectl logs [파드명]
```

Pod 안에 컨테이너가 하나만 있다면 컨테이너 이름은 생략할 수 있다.
Kubernetes 공식 문서에 따르면 `kubectl logs`는 Pod 안의 컨테이너 로그를 출력한다. [5]

컨테이너가 재시작된 뒤 이전 컨테이너 인스턴스의 로그를 확인해야 한다면 `--previous` 옵션을 사용할 수 있다.

```bash
kubectl logs [파드명] --previous
```

여러 Pod가 만들어져 있다면 label selector로 로그를 볼 수도 있다.

```bash
kubectl logs -l app=backend-app --all-containers=true
```

DB 비밀번호가 잘못된 경우에는 애플리케이션 로그에서 인증 실패, 접속 실패, 커넥션 생성 실패와 관련된 메시지를 확인할 수 있다.
정확한 메시지는 사용하는 JDBC 드라이버, Spring 설정, 예외 처리 방식에 따라 달라진다.

---

## 6. DB 정보를 다시 올바르게 수정하기

이제 `DB_PASSWORD` 값을 올바른 값으로 되돌린다.

`spring-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spring-deployment
spec:
  replicas: 3
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
          env:
            - name: DB_HOST
              value: mysql-service
            - name: DB_PORT
              value: "3306"
            - name: DB_NAME
              value: kub-practice
            - name: DB_USERNAME
              value: root
            - name: DB_PASSWORD
              value: password123
```

수정한 설정을 다시 적용하고 Deployment를 재시작한다.

```bash
kubectl apply -f spring-deployment.yaml
kubectl rollout restart deployment spring-deployment
```

다시 Pod 상태를 확인한다.

```bash
kubectl get pods
```

Pod가 정상적으로 실행되고 애플리케이션 로그에 DB 연결 오류가 더 이상 없다면, MySQL 연결 정보가 올바르게 적용된 것이다.

---

## 7. 확인 순서 정리

DB 연결 문제를 확인할 때는 다음 순서로 보는 것이 좋다.

1. Pod 상태 확인

   ```bash
   kubectl get pods
   ```

2. Pod 상세 이벤트 확인

   ```bash
   kubectl describe pod [파드명]
   ```

3. 현재 컨테이너 로그 확인

   ```bash
   kubectl logs [파드명]
   ```

4. 재시작 이전 로그 확인

   ```bash
   kubectl logs [파드명] --previous
   ```

5. Deployment 설정 확인

   ```bash
   kubectl get deployment spring-deployment -o yaml
   ```

---

## 핵심 정리

> DB 비밀번호가 틀리면 Spring 애플리케이션은 MySQL 연결에 실패할 수 있다.
>
> 애플리케이션이 연결 실패 시 종료되면 Pod는 `CrashLoopBackOff`처럼 보일 수 있다.
>
> 애플리케이션이 종료되지 않으면 Pod는 `Running`이어도 로그에 DB 연결 오류가 남을 수 있다.
>
> 실제 원인은 `kubectl logs [파드명]`과 `kubectl describe pod [파드명]`으로 함께 확인하는 것이 좋다.

---

## 출처

1. Kubernetes Docs, "Pod Lifecycle - How Pods handle problems with containers"
   https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/

2. Kubernetes Docs, "Pod Lifecycle - Types of probe"
   https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/

3. Kubernetes Docs, "kubectl apply"
   https://kubernetes.io/docs/reference/kubectl/generated/kubectl_apply/

4. Kubernetes Docs, "kubectl rollout restart"
   https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/kubectl_rollout_restart/

5. Kubernetes Docs, "kubectl logs"
   https://kubernetes.io/docs/reference/kubectl/generated/kubectl_logs/
