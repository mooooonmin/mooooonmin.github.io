---
title: 새로운 버전의 서버로 업데이트 시키기
category: docker-kubernetes
date: 2026-05-21 00:00:20 +0900
tags: [kubernetes, k8s, deployment, rollout, update, spring-boot, docker]
---

## 1. 서버 버전을 업데이트한다는 것

실제 서버를 운영하다 보면 기능을 수정하거나 버그를 고친 뒤, 새로운 버전의 서버로 교체해야 하는 일이 생긴다.

Kubernetes에서 Deployment를 사용하고 있다면 보통 Pod를 하나씩 직접 지우고 다시 만드는 방식으로 업데이트하지 않는다. Deployment의 Pod 템플릿, 예를 들어 컨테이너 이미지 값을 바꾸면 Kubernetes가 새로운 ReplicaSet을 만들고, 새 ReplicaSet을 점진적으로 늘리면서 기존 ReplicaSet을 줄이는 방식으로 Pod를 교체한다. Kubernetes 공식 문서는 Deployment의 Pod 템플릿인 `.spec.template`이 변경될 때 rollout이 트리거된다고 설명한다. [1]

쉽게 말하면 다음과 같다.

```text
새 서버 코드 작성
-> 새 Docker 이미지 빌드
-> Deployment의 image 값 변경
-> kubectl apply
-> Kubernetes가 Pod를 새 버전으로 교체
```

---

## 2. 코드 수정하기

먼저 Spring Boot 서버의 응답 값을 새 버전으로 바꾼다.

`AppController.java`

```java
package com.example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AppController {
  @GetMapping("/")
  public String home() {
    return "Version 1.0";
  }
}
```

여기서는 루트 경로(`/`)로 요청했을 때 `"Version 1.0"`을 반환하도록 수정했다.

---

## 3. Spring Boot 프로젝트 다시 빌드하기

코드를 수정했다면 Spring Boot 프로젝트를 다시 빌드한다.

```bash
./gradlew clean build
```

Windows PowerShell에서 실행한다면 프로젝트 설정에 따라 다음처럼 실행할 수도 있다.

```powershell
.\gradlew clean build
```

빌드가 성공하면 일반적으로 `build/libs` 아래에 jar 파일이 생성된다. 정확한 jar 파일 이름은 프로젝트의 Gradle 설정에 따라 달라질 수 있다.

---

## 4. 새 Docker 이미지 빌드하기

빌드된 jar 파일을 기반으로 새 이미지를 만든다.

```bash
docker build -t spring-server:1.0 .
```

여기서 `spring-server:1.0`은 이미지 이름과 태그다.

```text
spring-server = 이미지 이름
1.0 = 이미지 태그
```

이미지가 생성됐는지 확인한다.

```bash
docker image ls
```

목록에 `spring-server` 이미지와 `1.0` 태그가 보이면 이미지가 생성된 것이다.

---

## 5. Deployment 매니페스트 수정하기

이제 Kubernetes가 새 이미지를 사용하도록 Deployment 매니페스트를 수정한다.

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
          image: spring-server:1.0
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8080
```

핵심은 이 부분이다.

```yaml
image: spring-server:1.0
```

Deployment의 `.spec.template.spec.containers[].image` 값은 Pod 템플릿 안에 있다. Kubernetes 공식 문서에 따르면 Deployment의 rollout은 `.spec.template`이 변경될 때 발생하며, 컨테이너 이미지 변경이 그 예시에 포함된다. [1]

따라서 기존 이미지가 `spring-server` 또는 `spring-server:0.1`이었다면, 이것을 `spring-server:1.0`으로 바꾸는 순간 새 버전 Pod로 교체하는 rollout 대상이 된다.

---

## 6. 변경사항 적용하기

수정된 매니페스트 파일을 Kubernetes에 적용한다.

```bash
kubectl apply -f spring-deployment.yaml
```

`kubectl apply`는 파일 또는 표준 입력으로 전달한 리소스 설정을 적용하는 명령어다. Kubernetes 공식 `kubectl apply` 문서는 설정 파일을 적용하고, 리소스가 존재하지 않으면 생성한다고 설명한다. [2]

이미 `spring-deployment`가 존재하는 상태라면 위 명령은 Deployment 설정을 갱신한다.

---

## 7. 업데이트 상태 확인하기

rollout 진행 상태를 확인한다.

```bash
kubectl rollout status deployment/spring-deployment
```

Kubernetes 공식 문서에 따르면 `kubectl rollout status`는 rollout 상태를 보여주며, 기본적으로 최신 rollout이 끝날 때까지 상태를 watch한다. [3]

성공하면 다음과 비슷한 메시지를 볼 수 있다.

```text
deployment "spring-deployment" successfully rolled out
```

Pod 목록도 확인한다.

```bash
kubectl get pods
```

ReplicaSet 변화를 보고 싶다면 다음 명령어를 사용할 수 있다.

```bash
kubectl get rs
```

Deployment 업데이트 과정에서는 새 ReplicaSet이 만들어지고, 새 ReplicaSet의 Pod 수가 늘어나며, 기존 ReplicaSet의 Pod 수가 줄어든다. Kubernetes 공식 문서는 기본 RollingUpdate 전략에서 old ReplicaSet을 점진적으로 줄이고 new ReplicaSet을 점진적으로 늘리는 방식으로 Pod를 업데이트한다고 설명한다. [4]

---

## 8. 실제 응답 확인하기

Service 또는 port-forward를 통해 서버에 요청을 보내면 새 응답을 확인할 수 있다. Kubernetes 공식 `kubectl port-forward` 문서는 `deployment/mydeployment` 같은 `TYPE/NAME` 형식으로 Pod를 선택해 로컬 포트를 전달할 수 있다고 설명한다. [6]

예를 들어 port-forward를 사용하고 있다면 다음처럼 실행한다.

```bash
kubectl port-forward deployment/spring-deployment 8080:8080
```

다른 터미널에서 요청한다.

```bash
curl http://localhost:8080
```

예상 응답은 다음과 같다.

```text
Version 1.0
```

다만 실제 응답은 애플리케이션 코드, Service 설정, port-forward 대상, rollout 성공 여부에 따라 달라질 수 있다.

---

## 9. 주의할 점

로컬 실습 환경에서는 `imagePullPolicy: IfNotPresent`와 로컬 이미지를 함께 사용하는 경우가 많다. Kubernetes 공식 문서에 따르면 `imagePullPolicy`가 `IfNotPresent`이면 이미지가 로컬에 없을 때만 pull한다. [5]

하지만 여기서 말하는 로컬 이미지는 보통 **Pod가 실행되는 Kubernetes 노드의 컨테이너 런타임에 존재하는 이미지**다. 내 PC에서 `docker build`를 했더라도, Pod가 다른 노드에서 실행된다면 그 노드에는 이미지가 없을 수 있다.

따라서 원격 클러스터에서는 보통 다음 흐름이 필요하다.

```text
1. docker build로 이미지 생성
2. Docker Hub, ECR, GCR 같은 이미지 레지스트리에 push
3. Deployment의 image 값을 레지스트리 주소가 포함된 이미지로 변경
4. kubectl apply로 적용
```

예시는 다음과 같은 형태가 된다.

```yaml
image: my-registry.example.com/spring-server:1.0
```

이 글의 `spring-server:1.0` 예시는 로컬 Kubernetes 실습 환경에서 이미지를 직접 사용할 수 있다는 전제를 둔 예시다.

---

## 10. 정리

Kubernetes에서 새로운 버전의 서버로 업데이트하는 흐름은 다음과 같다.

```text
1. Spring Boot 코드 수정
2. ./gradlew clean build
3. docker build -t spring-server:1.0 .
4. spring-deployment.yaml의 image 값을 spring-server:1.0으로 수정
5. kubectl apply -f spring-deployment.yaml
6. kubectl rollout status deployment/spring-deployment로 확인
```

핵심은 Deployment의 Pod 템플릿 안에 있는 컨테이너 이미지 값을 바꾸는 것이다. 이 값이 바뀌면 Deployment rollout이 발생하고, Kubernetes는 새 버전 Pod를 만들면서 기존 Pod를 점진적으로 교체한다. [1][4]

---

## 출처

[1] Kubernetes Docs, "Deployments - Updating a Deployment", 확인일: 2026-05-21, <https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#updating-a-deployment>

[2] Kubernetes Docs, "kubectl apply", 확인일: 2026-05-21, <https://kubernetes.io/docs/reference/kubectl/generated/kubectl_apply/>

[3] Kubernetes Docs, "kubectl rollout status", 확인일: 2026-05-21, <https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/kubectl_rollout_status/>

[4] Kubernetes Docs, "Deployments - Rolling Update Deployment", 확인일: 2026-05-21, <https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#rolling-update-deployment>

[5] Kubernetes Docs, "Images - Image pull policy", 확인일: 2026-05-21, <https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy>

[6] Kubernetes Docs, "kubectl port-forward", 확인일: 2026-05-21, <https://kubernetes.io/docs/reference/kubectl/generated/kubectl_port-forward/>
