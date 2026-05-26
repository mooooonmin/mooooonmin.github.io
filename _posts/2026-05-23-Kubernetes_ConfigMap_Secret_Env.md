---
title: ConfigMap, Secret 활용해 환경변수 분리하기
category: c
date: 2026-05-23 00:00:00 +0900
tags: [kubernetes, k8s, configmap, secret, deployment, environment-variable, kubectl]
---

## 1. 환경 변수를 분리하는 이유

애플리케이션을 Kubernetes에 배포할 때 DB 접속 정보 같은 값은 컨테이너 이미지나 Deployment 매니페스트 안에 직접 고정하지 않는 것이 좋다.

예를 들어 Spring 애플리케이션에서 다음 값들이 필요하다고 가정한다.

```text
DB_HOST=mysql-service
DB_PORT=3306
DB_NAME=kub-practice
DB_USERNAME=root
DB_PASSWORD=password123
```

이 값들을 모두 Deployment에 직접 적으면 설정값과 배포 정의가 한 파일에 섞인다.

Kubernetes에서는 일반 설정값은 **ConfigMap**, 민감한 값은 **Secret**으로 분리할 수 있다.

Kubernetes 공식 문서에 따르면 ConfigMap은 기밀이 아닌 데이터를 key-value 쌍으로 저장하는 API 오브젝트이며, Pod는 ConfigMap을 환경 변수, command-line argument, 또는 volume 안의 설정 파일로 사용할 수 있다. [1]

Secret은 비밀번호, 토큰, 키 같은 작은 양의 민감한 데이터를 저장하기 위한 오브젝트다. [2]

```text
ConfigMap: DB host, port, database name 같은 일반 설정값
Secret: DB username, password 같은 민감한 값
```

---

## 2. ConfigMap 매니페스트 파일 생성하기

먼저 민감하지 않은 DB 설정값을 ConfigMap으로 분리한다.

`spring-config.yaml`

```yaml
apiVersion: v1
kind: ConfigMap

# ConfigMap 기본 정보
metadata:
  name: spring-config # ConfigMap 이름

# Key, Value 형식으로 설정값 저장
data:
  db-host: mysql-service
  db-port: "3306"
  db-name: kub-practice
```

여기서 `data` 아래에 작성한 key는 Deployment에서 `configMapKeyRef`로 참조할 수 있다.

Kubernetes 공식 문서에 따르면 ConfigMap은 대부분의 Kubernetes 오브젝트와 달리 `spec` 대신 `data`와 `binaryData` 필드를 가지며, 이 필드는 key-value 쌍을 값으로 받는다. [1]

---

## 3. ConfigMap을 Deployment 환경 변수로 사용하기

다음은 ConfigMap에서 DB 접속 설정을 가져오고, 사용자명과 비밀번호는 아직 Deployment에 직접 적은 상태다.

`spring-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment

# Deployment 기본 정보
metadata:
  name: spring-deployment # Deployment 이름

# Deployment 세부 정보
spec:
  replicas: 3 # 생성할 파드의 복제본 개수
  selector:
    matchLabels:
      app: backend-app # 아래에서 정의한 Pod 중 'app: backend-app'이라는 값을 가진 파드를 선택

  # 배포할 Pod 정의
  template:
    metadata:
      labels: # 레이블 (= 카테고리)
        app: backend-app
    spec:
      containers:
        - name: spring-container # 컨테이너 이름
          image: spring-server # 컨테이너를 생성할 때 사용할 이미지
          imagePullPolicy: IfNotPresent # 로컬에서 이미지를 먼저 가져온다. 없으면 레지스트리에서 가져온다.
          ports:
            - containerPort: 8080 # 컨테이너에서 사용하는 포트를 명시적으로 표현
          env:
            - name: DB_HOST
              valueFrom:
                configMapKeyRef:
                  name: spring-config
                  key: db-host
            - name: DB_PORT
              valueFrom:
                configMapKeyRef:
                  name: spring-config
                  key: db-port
            - name: DB_NAME
              valueFrom:
                configMapKeyRef:
                  name: spring-config
                  key: db-name
            - name: DB_USERNAME
              value: root
            - name: DB_PASSWORD
              value: password123
```

핵심은 다음 부분이다.

```yaml
valueFrom:
  configMapKeyRef:
    name: spring-config
    key: db-host
```

이 설정은 `spring-config` ConfigMap의 `db-host` 값을 `DB_HOST` 환경 변수로 주입한다.

Kubernetes 공식 문서에 따르면 ConfigMap key를 Pod 환경 변수로 사용하려면 컨테이너의 `env[].valueFrom.configMapKeyRef` 필드에 사용할 ConfigMap key를 지정한다. [1]

---

## 4. Secret 매니페스트 파일 만들기

`DB_USERNAME`, `DB_PASSWORD`는 인증 정보이므로 Secret으로 분리한다.

`spring-secret.yaml`

```yaml
apiVersion: v1
kind: Secret

# Secret 기본 정보
metadata:
  name: spring-secret # Secret 이름

# Key, Value 형식으로 값 저장
stringData:
  db-username: root
  db-password: password123
```

Secret에는 `data`와 `stringData`를 사용할 수 있다.

Kubernetes 공식 문서에 따르면 Secret을 매니페스트로 만들 때 `data` 또는 `stringData` 필드를 지정할 수 있다. `stringData`를 사용하면 사람이 읽을 수 있는 문자열을 그대로 작성할 수 있고, Kubernetes가 내부적으로 Secret data로 처리한다. [3]

다만 공식 문서는 `stringData`가 server-side apply와 잘 맞지 않는다고 주의한다. [3]

이 글에서는 실습에서 이해하기 쉽게 `stringData`를 사용한다.

---

## 5. Deployment에서 ConfigMap과 Secret 함께 사용하기

이제 Deployment에서 일반 설정값은 ConfigMap에서 가져오고, 민감한 값은 Secret에서 가져오도록 수정한다.

`spring-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment

# Deployment 기본 정보
metadata:
  name: spring-deployment # Deployment 이름

# Deployment 세부 정보
spec:
  replicas: 3 # 생성할 파드의 복제본 개수
  selector:
    matchLabels:
      app: backend-app # 아래에서 정의한 Pod 중 'app: backend-app'이라는 값을 가진 파드를 선택

  # 배포할 Pod 정의
  template:
    metadata:
      labels: # 레이블 (= 카테고리)
        app: backend-app
    spec:
      containers:
        - name: spring-container # 컨테이너 이름
          image: spring-server # 컨테이너를 생성할 때 사용할 이미지
          imagePullPolicy: IfNotPresent # 로컬에서 이미지를 먼저 가져온다. 없으면 레지스트리에서 가져온다.
          ports:
            - containerPort: 8080 # 컨테이너에서 사용하는 포트를 명시적으로 표현
          env:
            - name: DB_HOST
              valueFrom:
                configMapKeyRef:
                  name: spring-config
                  key: db-host
            - name: DB_PORT
              valueFrom:
                configMapKeyRef:
                  name: spring-config
                  key: db-port
            - name: DB_NAME
              valueFrom:
                configMapKeyRef:
                  name: spring-config
                  key: db-name
            - name: DB_USERNAME
              valueFrom:
                secretKeyRef:
                  name: spring-secret
                  key: db-username
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: spring-secret
                  key: db-password
```

`DB_USERNAME`과 `DB_PASSWORD`는 이제 Deployment에 값을 직접 쓰지 않는다.

```yaml
valueFrom:
  secretKeyRef:
    name: spring-secret
    key: db-password
```

위 설정은 `spring-secret` Secret의 `db-password` 값을 `DB_PASSWORD` 환경 변수로 주입한다.

Kubernetes 공식 문서에 따르면 Secret data를 컨테이너 환경 변수로 사용할 수 있고, Pod 명세에서 `env[].valueFrom.secretKeyRef`로 Secret의 이름과 key를 지정한다. [4]

---

## 6. 매니페스트 파일 반영하기

먼저 Secret을 적용한다.

```bash
kubectl apply -f spring-secret.yaml
```

ConfigMap을 적용한다.

```bash
kubectl apply -f spring-config.yaml
```

Deployment를 적용한다.

```bash
kubectl apply -f spring-deployment.yaml
```

`kubectl apply`는 파일 또는 표준 입력으로 전달한 리소스 설정을 클러스터에 적용하는 명령이다. [5]

이미 실행 중인 Deployment에 변경된 환경 변수를 반영하려면 Deployment를 재시작한다.

```bash
kubectl rollout restart deployment spring-deployment
```

Kubernetes 공식 `kubectl rollout` 문서는 Deployment를 재시작하는 예시로 `kubectl rollout restart deployment/abc` 형식을 제공한다. [6]

재시작 상태는 다음 명령으로 확인할 수 있다.

```bash
kubectl rollout status deployment/spring-deployment
```

---

## 7. 잘 반영됐는지 확인하기

Pod 목록을 확인한다.

```bash
kubectl get pods
```

새로 생성된 Pod 이름을 확인한 뒤, 환경 변수를 조회한다.

```bash
kubectl exec -it spring-deployment-xxxxxxxxxx-aaaaa -- printenv DB_HOST
kubectl exec -it spring-deployment-xxxxxxxxxx-aaaaa -- printenv DB_PORT
kubectl exec -it spring-deployment-xxxxxxxxxx-aaaaa -- printenv DB_NAME
kubectl exec -it spring-deployment-xxxxxxxxxx-aaaaa -- printenv DB_USERNAME
kubectl exec -it spring-deployment-xxxxxxxxxx-aaaaa -- printenv DB_PASSWORD
```

예상 출력은 다음과 같다.

```text
mysql-service
3306
kub-practice
root
password123
```

여기서 `spring-deployment-xxxxxxxxxx-aaaaa`는 예시 Pod 이름이다. 실제 실습에서는 `kubectl get pods`로 확인한 Pod 이름을 사용해야 한다.

민감한 값을 터미널에 직접 출력하는 방식은 실습 확인용으로만 사용한다. 실제 운영 환경에서는 Secret 값을 로그나 터미널에 불필요하게 노출하지 않는 것이 좋다.

---

## 8. Secret을 사용하면 완전히 안전할까?

Secret은 ConfigMap보다 민감한 값을 관리하는 데 적합하지만, Secret을 사용한다고 해서 자동으로 모든 보안 문제가 해결되는 것은 아니다.

Kubernetes 공식 문서에 따르면 Secret은 기본적으로 API 서버의 기반 데이터 저장소인 etcd에 암호화되지 않은 상태로 저장된다. 또한 API 접근 권한이 있는 사용자는 Secret을 조회하거나 수정할 수 있고, etcd 접근 권한이 있는 사용자도 Secret에 접근할 수 있다. [2]

따라서 Secret을 사용할 때도 다음 사항을 함께 고려해야 한다.

```text
1. Secret에 대한 Encryption at Rest 활성화
2. RBAC으로 Secret 조회 권한 최소화
3. 필요한 Pod 또는 컨테이너에서만 Secret 사용
4. 운영 환경에서는 외부 Secret Store Provider 사용 검토
```

Secret은 "Deployment에 민감한 값을 직접 적는 것보다 나은 방식"이지, "아무 설정 없이 완전히 안전한 저장소"는 아니다.

---

## 핵심 정리

ConfigMap과 Secret으로 환경 변수를 분리하는 흐름은 다음과 같다.

```text
1. spring-config.yaml 생성
2. 일반 설정값을 ConfigMap data에 작성
3. spring-secret.yaml 생성
4. 민감한 값을 Secret stringData에 작성
5. Deployment에서 configMapKeyRef로 ConfigMap key 참조
6. Deployment에서 secretKeyRef로 Secret key 참조
7. kubectl apply로 Secret, ConfigMap, Deployment 적용
8. kubectl rollout restart로 실행 중인 Deployment 재시작
9. kubectl exec 또는 애플리케이션 동작으로 환경 변수 반영 확인
```

핵심은 **일반 설정값은 ConfigMap**, **민감한 값은 Secret**으로 분리하고, Deployment에서는 직접 값을 적지 않고 각각의 key를 참조하도록 만드는 것이다.

---

## 출처

[1] Kubernetes Docs, "ConfigMaps", 확인일: 2026-05-23, <https://kubernetes.io/docs/concepts/configuration/configmap/>

[2] Kubernetes Docs, "Secrets", 확인일: 2026-05-23, <https://kubernetes.io/docs/concepts/configuration/secret/>

[3] Kubernetes Docs, "Managing Secrets using Configuration File", 확인일: 2026-05-23, <https://kubernetes.io/docs/tasks/configmap-secret/managing-secret-using-config-file/>

[4] Kubernetes Docs, "Distribute Credentials Securely Using Secrets", 확인일: 2026-05-23, <https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/>

[5] Kubernetes Docs, "kubectl apply", 확인일: 2026-05-23, <https://kubernetes.io/docs/reference/kubectl/generated/kubectl_apply/>

[6] Kubernetes Docs, "kubectl rollout", 확인일: 2026-05-23, <https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/>