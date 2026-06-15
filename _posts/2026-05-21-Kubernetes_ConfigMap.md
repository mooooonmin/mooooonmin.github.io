---
title: ConfigMap 활용해 환경변수 분리하기
category: c
date: 2026-05-21 00:00:30 +0900
tags: [kubernetes, k8s, configmap, deployment, environment-variable, kubectl]
---

## 1. ConfigMap이란?

Spring Boot에서는 설정값을 `application.yml` 또는 `application.properties` 같은 외부 설정으로 분리해서 관리할 수 있다. Spring Boot 공식 문서도 같은 애플리케이션 코드를 여러 환경에서 사용할 수 있도록 설정을 외부화할 수 있으며, YAML 파일, 환경 변수, command-line argument 같은 여러 설정 소스를 사용할 수 있다고 설명한다. [1]

NestJS에서도 설정값을 환경 변수로 분리해서 다룰 수 있다. NestJS 공식 문서는 `@nestjs/config` 패키지가 내부적으로 `dotenv`를 사용하며, 기본 위치의 `.env` 파일에서 환경 변수를 불러올 수 있다고 설명한다. [2]

Kubernetes에서도 비슷하게 애플리케이션 설정값을 컨테이너 이미지나 Deployment 매니페스트에서 분리할 수 있다. 이때 사용하는 Kubernetes 오브젝트가 **ConfigMap**이다.

Kubernetes 공식 문서에 따르면 ConfigMap은 기밀이 아닌 데이터를 key-value 쌍으로 저장하는 API 오브젝트다. Pod는 ConfigMap을 환경 변수, command-line argument, 또는 volume 안의 설정 파일로 사용할 수 있다. [3]

쉽게 말하면 다음과 같다.

```text
ConfigMap = Kubernetes에서 설정값을 따로 저장하는 오브젝트
```

---

## 2. Deployment에 환경 변수를 직접 쓰는 방식

먼저 환경 변수를 Deployment 안에 직접 작성하는 예시를 보자.

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
            - name: MY_ACCOUNT
              value: USER1
            - name: MY_PASSWORD
              value: pwd1234
```

이 방식은 동작은 한다. Kubernetes Pod 명세에서 `env` 필드는 컨테이너에 환경 변수를 설정하는 데 사용된다. ConfigMap을 쓰지 않고 `value`에 값을 직접 적으면 해당 값이 컨테이너 환경 변수로 들어간다.

하지만 환경 변수를 Deployment 내부에 직접 작성하면 설정값과 배포 정의가 한 파일에 섞인다.

```text
Deployment 역할: 어떤 Pod를 몇 개 띄울지 정의
환경 변수 역할: 애플리케이션 실행 설정값 제공
```

개발, 테스트, 프로덕션 환경마다 값이 달라져야 한다면 Deployment YAML을 계속 수정해야 한다. 설정값만 바꾸고 싶은 상황에서도 Deployment 매니페스트 전체를 건드리게 되므로 관리가 불편해질 수 있다.

---

## 3. ConfigMap 매니페스트 만들기

환경 변수로 사용할 값을 ConfigMap으로 분리한다.

`spring-config.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: spring-config
data:
  my-account: USER2
  my-password: password123
```

핵심은 `data` 필드다.

```yaml
data:
  my-account: USER2
  my-password: password123
```

Kubernetes 공식 문서에 따르면 ConfigMap은 대부분의 Kubernetes 오브젝트와 다르게 `spec`이 아니라 `data`와 `binaryData` 필드를 가지며, 이 필드들은 key-value 쌍을 값으로 받는다. `data` 필드는 UTF-8 문자열을 담기 위한 필드다. [3]

위 예시에서는 확인을 쉽게 하기 위해 기존 Deployment에 직접 적었던 값과 다르게 설정했다.

```text
기존 값: USER1 / pwd1234
ConfigMap 값: USER2 / password123
```

---

## 4. Deployment에서 ConfigMap 값 사용하기

이제 Deployment의 환경 변수 값을 ConfigMap에서 가져오도록 수정한다.

`spring-deployment.yaml`

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
          env:
            - name: MY_ACCOUNT
              valueFrom:
                configMapKeyRef:
                  name: spring-config
                  key: my-account
            - name: MY_PASSWORD
              valueFrom:
                configMapKeyRef:
                  name: spring-config
                  key: my-password
```

핵심은 `valueFrom.configMapKeyRef`다.

```yaml
valueFrom:
  configMapKeyRef:
    name: spring-config
    key: my-account
```

이 설정은 다음 뜻이다.

```text
MY_ACCOUNT 환경 변수의 값은
spring-config ConfigMap의
my-account key에서 가져와라
```

Kubernetes 공식 문서는 ConfigMap key 값을 컨테이너 환경 변수로 사용하려면 각 컨테이너의 `env[].valueFrom.configMapKeyRef` 필드에 환경 변수와 ConfigMap key를 지정한다고 설명한다. [4]

---

## 5. 매니페스트 파일 반영하기

먼저 ConfigMap을 생성하거나 갱신한다.

```bash
kubectl apply -f spring-config.yaml
```

그다음 Deployment를 적용한다.

```bash
kubectl apply -f spring-deployment.yaml
```

`kubectl apply`는 파일 또는 표준 입력으로 전달한 리소스 설정을 적용하는 명령어다. Kubernetes 공식 문서는 `kubectl apply`가 설정 파일을 적용하고, 리소스가 없으면 생성한다고 설명한다. [5]

---

## 6. Deployment 재시작하기

ConfigMap 값을 환경 변수로 주입받는 경우에는 Pod 재시작이 필요하다.

Kubernetes 공식 문서에 따르면 volume으로 사용 중인 ConfigMap은 업데이트가 Pod에 나중에 반영될 수 있지만, 환경 변수로 소비된 ConfigMap은 자동으로 업데이트되지 않으며 Pod 재시작이 필요하다. [3]

따라서 ConfigMap 값을 바꾼 뒤 이미 실행 중인 Deployment에 반영하려면 다음 명령어로 Deployment를 재시작한다.

```bash
kubectl rollout restart deployment spring-deployment
```

Kubernetes 공식 `kubectl rollout` 문서는 Deployment를 재시작하는 예시로 `kubectl rollout restart deployment/abc` 형식을 제공한다. [6]

재시작 상태는 다음 명령어로 확인할 수 있다.

```bash
kubectl rollout status deployment/spring-deployment
```

---

## 7. 잘 반영됐는지 확인하기

Pod 목록을 확인한다.

```bash
kubectl get pods
```

새로 뜬 Pod 중 하나의 이름을 확인한 뒤, 컨테이너 안에서 환경 변수를 확인한다.

```bash
kubectl exec -it spring-deployment-xxxxxxxxxx-aaaaa -- printenv MY_ACCOUNT
```

예상 출력은 다음과 같다.

```text
USER2
```

비밀번호 예시 값도 확인하려면 다음처럼 볼 수 있다.

```bash
kubectl exec -it spring-deployment-xxxxxxxxxx-aaaaa -- printenv MY_PASSWORD
```

예상 출력은 다음과 같다.

```text
password123
```

여기서 `spring-deployment-xxxxxxxxxx-aaaaa`는 예시 Pod 이름이다. 실제 실습에서는 `kubectl get pods`로 확인한 Pod 이름을 사용해야 한다.

---

## 8. 비밀번호는 ConfigMap에 넣어도 될까?

이 글에서는 환경 변수 분리 방법을 보여주기 위해 `MY_PASSWORD`를 ConfigMap에 넣었다. 하지만 실제 운영 환경의 비밀번호, 토큰, 인증키 같은 민감한 값은 ConfigMap에 저장하면 안 된다.

Kubernetes 공식 문서는 ConfigMap이 secrecy 또는 encryption을 제공하지 않으며, 저장하려는 데이터가 기밀이라면 ConfigMap 대신 Secret을 사용하라고 주의한다. [3]

따라서 역할을 나누면 다음과 같다.

```text
ConfigMap: 공개되어도 큰 문제가 없는 일반 설정값
Secret: 비밀번호, 토큰, 인증키 같은 민감한 값
```

이 글의 `MY_PASSWORD` 예시는 학습을 위한 값이며, 실제 운영 환경에서는 Secret을 사용하는 편이 맞다.

---

## 정리

ConfigMap을 사용해 환경 변수를 분리하는 흐름은 다음과 같다.

```text
1. spring-config.yaml 파일 생성
2. ConfigMap의 data에 설정값 작성
3. Deployment의 env.valueFrom.configMapKeyRef로 ConfigMap key 참조
4. kubectl apply -f spring-config.yaml
5. kubectl apply -f spring-deployment.yaml
6. kubectl rollout restart deployment spring-deployment
7. kubectl exec 또는 애플리케이션 응답으로 환경 변수 반영 확인
```

핵심은 Deployment 내부에 설정값을 직접 적는 대신 ConfigMap에 설정값을 분리하고, Deployment에서는 그 값을 참조하도록 만드는 것이다.

---

## 출처

[1] Spring Boot Docs, "Externalized Configuration", 확인일: 2026-05-21, <https://docs.spring.io/spring-boot/4.1/reference/features/external-config.html>

[2] NestJS Docs, "Configuration", 확인일: 2026-05-21, <https://docs.nestjs.com/techniques/configuration>

[3] Kubernetes Docs, "ConfigMaps", 확인일: 2026-05-21, <https://kubernetes.io/docs/concepts/configuration/configmap/>

[4] Kubernetes Docs, "Configure a Pod to Use a ConfigMap", 확인일: 2026-05-21, <https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/>

[5] Kubernetes Docs, "kubectl apply", 확인일: 2026-05-21, <https://kubernetes.io/docs/reference/kubectl/generated/kubectl_apply/>

[6] Kubernetes Docs, "kubectl rollout", 확인일: 2026-05-21, <https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/>
