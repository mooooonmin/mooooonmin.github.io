---
title: Secret 활용해 민감한 값을 환경 변수로 분리하기
category: s
date: 2026-05-21 00:00:40 +0900
tags: [kubernetes, k8s, secret, configmap, deployment, environment-variable, kubectl]
---

## 1. Secret이란?

ConfigMap은 애플리케이션 설정값을 Deployment와 분리해서 관리할 때 사용할 수 있다. 하지만 비밀번호, 토큰, 인증키처럼 보안적으로 중요한 값은 ConfigMap에 넣는 것이 적절하지 않다.

Kubernetes 공식 문서에 따르면 Secret은 비밀번호, 토큰, 키 같은 작은 양의 민감한 데이터를 담는 오브젝트다. Secret을 사용하면 이런 기밀 데이터를 애플리케이션 코드에 포함하지 않아도 된다. 또한 Secret은 ConfigMap과 비슷하지만, 기밀 데이터를 담기 위한 용도로 만들어졌다고 설명한다. [1]

쉽게 말하면 다음과 같다.

```text
ConfigMap = 일반 설정값 관리
Secret = 비밀번호, 토큰, 인증키 같은 민감한 값 관리
```

---

## 2. 기존 ConfigMap 살펴보기

환경 변수를 ConfigMap으로 분리해두었다고 가정하자.

`spring-config.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: spring-config
data:
  my-account: USER1
  my-password: password123
```

여기서 `my-account`는 일반 설정값이라고 볼 수 있다. 하지만 `my-password`가 실제 비밀번호라면 ConfigMap에 두면 안 된다.

Kubernetes 공식 문서는 ConfigMap이 secrecy 또는 encryption을 제공하지 않으며, 저장하려는 데이터가 기밀이라면 ConfigMap 대신 Secret을 사용하라고 설명한다. [2]

따라서 역할을 다음처럼 나누는 것이 좋다.

```text
my-account -> ConfigMap
my-password -> Secret
```

---

## 3. ConfigMap에서 민감한 값 제거하기

먼저 `spring-config.yaml`에서는 민감한 값인 `my-password`를 제거한다.

수정 후 `spring-config.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: spring-config
data:
  my-account: USER1
```

이제 ConfigMap에는 공개되어도 큰 문제가 없는 일반 설정값만 남는다.

---

## 4. Secret 매니페스트 만들기

비밀번호는 새 Secret 매니페스트로 분리한다.

`spring-secret.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: spring-secret
stringData:
  my-password: my-secret-password
```

핵심은 `stringData` 필드다.

```yaml
stringData:
  my-password: my-secret-password
```

Kubernetes Secret에는 `data`와 `stringData` 필드를 사용할 수 있다. 공식 문서에 따르면 `data` 필드의 값은 base64로 인코딩된 문자열이어야 하며, base64 변환을 직접 하고 싶지 않다면 임의의 문자열을 값으로 받는 `stringData` 필드를 사용할 수 있다. `stringData`의 값은 내부적으로 `data` 필드에 병합된다. [1]

다만 공식 문서는 `stringData` 필드가 server-side apply와 잘 맞지 않는다고 주의한다. [1] 이 글의 예시는 로컬 실습에서 이해를 쉽게 하기 위해 `stringData`를 사용한다.

---

## 5. Deployment에서 ConfigMap과 Secret 함께 사용하기

이제 Deployment에서 일반 설정값은 ConfigMap에서 가져오고, 민감한 값은 Secret에서 가져오도록 수정한다.

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
                secretKeyRef:
                  name: spring-secret
                  key: my-password
```

`MY_ACCOUNT`는 ConfigMap에서 가져온다.

```yaml
valueFrom:
  configMapKeyRef:
    name: spring-config
    key: my-account
```

`MY_PASSWORD`는 Secret에서 가져온다.

```yaml
valueFrom:
  secretKeyRef:
    name: spring-secret
    key: my-password
```

Kubernetes 공식 문서에 따르면 Secret의 데이터를 컨테이너 환경 변수로 사용할 수 있으며, Pod 명세에서 `valueFrom.secretKeyRef`를 사용해 Secret의 특정 key 값을 환경 변수에 할당할 수 있다. [3]

---

## 6. 매니페스트 파일 반영하기

먼저 Secret을 적용한다.

```bash
kubectl apply -f spring-secret.yaml
```

ConfigMap도 적용한다.

```bash
kubectl apply -f spring-config.yaml
```

Deployment도 적용한다.

```bash
kubectl apply -f spring-deployment.yaml
```

`kubectl apply`는 파일 또는 표준 입력으로 전달한 리소스 설정을 적용하는 명령어다. Kubernetes 공식 문서는 `kubectl apply`가 설정 파일을 적용하고, 리소스가 없으면 생성한다고 설명한다. [4]

---

## 7. Deployment 재시작하기

이미 실행 중인 Pod가 Secret 값을 환경 변수로 사용하고 있다면 Secret 변경사항이 자동으로 환경 변수에 반영되지 않는다.

Kubernetes 공식 문서에 따르면 컨테이너가 이미 Secret을 환경 변수로 소비하고 있다면, Secret 업데이트는 컨테이너가 재시작되기 전까지 보이지 않는다. [3]

따라서 Deployment를 재시작한다.

```bash
kubectl rollout restart deployment spring-deployment
```

Kubernetes 공식 `kubectl rollout` 문서는 Deployment를 재시작하는 예시로 `kubectl rollout restart deployment/abc` 형식을 제공한다. [5]

상태를 확인한다.

```bash
kubectl rollout status deployment/spring-deployment
```

---

## 8. 잘 반영됐는지 확인하기

Pod 목록을 확인한다.

```bash
kubectl get pods
```

새로 생성된 Pod 이름을 확인한 뒤 환경 변수를 확인한다.

```bash
kubectl exec -it spring-deployment-xxxxxxxxxx-aaaaa -- printenv MY_ACCOUNT
```

예상 출력은 다음과 같다.

```text
USER1
```

Secret에서 가져온 값도 확인한다.

```bash
kubectl exec -it spring-deployment-xxxxxxxxxx-aaaaa -- printenv MY_PASSWORD
```

예상 출력은 다음과 같다.

```text
my-secret-password
```

여기서 `spring-deployment-xxxxxxxxxx-aaaaa`는 예시 Pod 이름이다. 실제 실습에서는 `kubectl get pods`로 확인한 Pod 이름을 사용해야 한다.

---

## 9. Secret을 쓰면 완전히 안전할까?

Secret은 ConfigMap보다 민감한 값을 관리하는 데 적합하지만, Secret을 쓴다고 해서 자동으로 모든 보안 문제가 해결되는 것은 아니다.

Kubernetes 공식 문서에 따르면 Secret은 기본적으로 API 서버의 기반 데이터 저장소인 etcd에 암호화되지 않은 상태로 저장된다. API 접근 권한이 있는 사람은 Secret을 조회하거나 수정할 수 있고, etcd 접근 권한이 있는 사람도 Secret에 접근할 수 있다. [1]

공식 문서는 Secret을 안전하게 사용하기 위해 최소한 다음 조치를 권장한다. [1]

```text
1. Secret에 대해 Encryption at Rest 활성화
2. RBAC을 최소 권한 원칙으로 설정
3. 특정 컨테이너로 Secret 접근 제한
4. 외부 Secret Store Provider 사용 검토
```

따라서 Secret은 "민감한 값을 ConfigMap이나 Deployment에 그대로 적는 것보다 나은 방식"이지, "아무 설정 없이 완벽하게 안전한 저장소"라고 이해하면 안 된다.

---

## 정리

Secret을 활용해 민감한 값을 환경 변수로 분리하는 흐름은 다음과 같다.

```text
1. ConfigMap에서 민감한 값 제거
2. spring-secret.yaml 생성
3. Secret의 stringData에 민감한 값 작성
4. Deployment에서 secretKeyRef로 Secret key 참조
5. kubectl apply -f spring-secret.yaml
6. kubectl apply -f spring-config.yaml
7. kubectl apply -f spring-deployment.yaml
8. kubectl rollout restart deployment spring-deployment
9. kubectl exec 또는 애플리케이션 응답으로 반영 확인
```

핵심은 일반 설정값은 ConfigMap에 두고, 비밀번호 같은 민감한 값은 Secret으로 분리한 뒤 Deployment에서 각각 참조하도록 만드는 것이다.

---

## 출처

[1] Kubernetes Docs, "Secrets", 확인일: 2026-05-21, <https://kubernetes.io/docs/concepts/configuration/secret/>

[2] Kubernetes Docs, "ConfigMaps", 확인일: 2026-05-21, <https://kubernetes.io/docs/concepts/configuration/configmap/>

[3] Kubernetes Docs, "Distribute Credentials Securely Using Secrets", 확인일: 2026-05-21, <https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/>

[4] Kubernetes Docs, "kubectl apply", 확인일: 2026-05-21, <https://kubernetes.io/docs/reference/kubectl/generated/kubectl_apply/>

[5] Kubernetes Docs, "kubectl rollout", 확인일: 2026-05-21, <https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/>
