---
title: ImagePullBackOff
category: i
date: 2026-05-19 00:00:20 +0900
tags: [kubernetes, k8s, pod, image, image-pull-policy, imagepullbackoff]
---

## 1. 이미지가 없다고 에러가 뜨는 이유

이전에 Spring Boot 프로젝트를 이미지로 빌드해서 Pod로 띄웠는데 `ImagePullBackOff` 에러가 발생했다.

이 문제는 보통 Kubernetes가 이미지를 가져오는 방식과 관련이 있다. Kubernetes에서는 컨테이너를 실행하기 전에 `image`에 적힌 이미지를 사용할 수 있어야 한다.

그런데 이미지가 로컬에는 있고 원격 레지스트리에는 없는 상태에서 Kubernetes가 원격 레지스트리에서 이미지를 가져오려고 하면 실패할 수 있다.

이때 중요한 설정이 **이미지 풀 정책(Image Pull Policy)** 이다.

---

## 2. 이미지 풀 정책(Image Pull Policy)이란?

이미지 풀 정책(Image Pull Policy)은 Kubernetes가 Pod를 생성할 때 컨테이너 이미지를 어떻게 가져올지 결정하는 설정이다.

Kubernetes 공식 문서에 따르면 컨테이너의 `imagePullPolicy`와 이미지 태그는 kubelet이 해당 이미지를 언제 pull할지에 영향을 준다. [1]

`imagePullPolicy`에는 다음 값을 설정할 수 있다. [1]

### 2.1. Always

```yaml
imagePullPolicy: Always
```

`Always`는 컨테이너를 시작할 때마다 kubelet이 컨테이너 이미지 레지스트리에 이미지 이름을 질의한다. 같은 digest의 이미지가 로컬에 캐시되어 있으면 캐시된 이미지를 사용하고, 그렇지 않으면 이미지를 pull한다. [1]

처음 이해할 때는 다음처럼 생각하면 된다.

> 컨테이너를 실행할 때마다 레지스트리를 확인한다.

여기서 레지스트리는 Docker Hub, Amazon ECR, Google Artifact Registry 같은 원격 이미지 저장소를 의미한다.

---

### 2.2. IfNotPresent

```yaml
imagePullPolicy: IfNotPresent
```

`IfNotPresent`는 이미지가 로컬에 없는 경우에만 이미지를 pull한다. [1]

즉, 로컬에 이미지가 있으면 그 이미지를 사용하고, 로컬에 이미지가 없을 때만 레지스트리에서 가져오려고 한다.

---

### 2.3. Never

```yaml
imagePullPolicy: Never
```

`Never`는 kubelet이 이미지를 pull하지 않는 설정이다. 이미지가 로컬에 있으면 그 이미지를 사용하고, 로컬에도 이미지가 없으면 컨테이너 시작에 실패한다. [1]

즉, 원격 레지스트리에서 이미지를 가져오지 않고 로컬 이미지만 사용한다.

---

## 3. 매니페스트 파일에 이미지 풀 정책 설정하기

Pod 매니페스트에서는 컨테이너 설정 아래에 `imagePullPolicy`를 적으면 된다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: spring-pod
spec:
  containers:
    - name: spring-container
      image: spring-server
      ports:
        - containerPort: 8080
      imagePullPolicy: IfNotPresent
```

위 설정은 `spring-server` 이미지가 로컬에 있으면 로컬 이미지를 사용하고, 로컬에 없을 때만 레지스트리에서 pull하도록 한다. [1]

---

## 4. 기존 매니페스트 파일 다시 살펴보기

처음 작성한 `spring-pod.yaml`이 다음과 같았다고 하자.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: spring-pod
spec:
  containers:
    - name: spring-container
      image: spring-server
      ports:
        - containerPort: 8080
```

여기서는 `imagePullPolicy`를 따로 설정하지 않았다.

이럴 때 Kubernetes는 이미지 태그에 따라 기본 이미지 풀 정책을 자동으로 설정한다. Kubernetes 공식 문서의 기본 규칙은 다음과 같다. [1]

- 이미지 태그가 `:latest`인 경우: `imagePullPolicy`는 `Always`
- 이미지 태그를 명시하지 않은 경우: `imagePullPolicy`는 `Always`
- 이미지 태그가 `:latest`가 아닌 경우: `imagePullPolicy`는 `IfNotPresent`
- 이미지 digest를 명시한 경우: `imagePullPolicy`는 `IfNotPresent`

기존 매니페스트의 이미지는 다음과 같다.

```yaml
image: spring-server
```

이미지 태그를 명시하지 않았으므로 Kubernetes는 기본적으로 `latest` 태그를 사용하는 것으로 본다. Kubernetes 공식 문서에 따르면 이미지 태그를 생략하면 `latest`를 사용한 것처럼 동작한다. [1]

따라서 위 설정은 사실상 다음과 비슷하게 이해할 수 있다.

```yaml
image: spring-server:latest
imagePullPolicy: Always
```

결과적으로 Kubernetes는 로컬 이미지만 바로 쓰는 것이 아니라 레지스트리를 확인하려고 한다.

그런데 `spring-server` 이미지를 Docker Hub 같은 레지스트리에 올린 적이 없다면 Kubernetes는 이미지를 가져오지 못한다. 이때 `ImagePullBackOff` 같은 상태가 나타날 수 있다.

---

## 5. 로컬 이미지 사용하도록 수정하기

로컬에 빌드해둔 `spring-server` 이미지를 사용하려면 `imagePullPolicy`를 명시적으로 설정한다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: spring-pod
spec:
  containers:
    - name: spring-container
      image: spring-server
      ports:
        - containerPort: 8080
      imagePullPolicy: IfNotPresent
```

이렇게 하면 로컬에 이미지가 있는 경우 그 이미지를 사용한다. [1]

다만 중요한 점이 있다. Kubernetes에서 말하는 "로컬 이미지"는 보통 **Pod가 실제로 실행되는 노드의 컨테이너 런타임에 존재하는 이미지**를 의미한다. 내 PC에서 Docker로 이미지를 빌드했더라도, 클러스터 노드가 다른 환경이면 그 노드에는 이미지가 없을 수 있다.

예를 들어 Docker Desktop Kubernetes나 minikube처럼 로컬 개발 환경을 쓰는 경우에는 설정에 따라 로컬 이미지를 사용할 수 있다. 하지만 원격 Kubernetes 클러스터에서는 이미지를 레지스트리에 push하거나, 해당 노드에 이미지를 미리 올려두어야 한다.

---

## 6. 기존 Pod 삭제 후 다시 생성하기

매니페스트를 수정했다면 기존 Pod를 삭제하고 다시 생성한다.

```bash
kubectl delete pod spring-pod
kubectl apply -f spring-pod.yaml
kubectl get pods
```

`spring-pod`의 상태가 `Running`으로 바뀌면 이미지 문제는 해결된 것이다.

상태를 더 자세히 보고 싶다면 다음 명령어를 사용할 수 있다.

```bash
kubectl describe pod spring-pod
```

`describe` 결과의 Events 영역에서 이미지 pull 시도, 실패 원인, 컨테이너 시작 여부 등을 확인할 수 있다.

---

## 7. Spring Boot 서버 응답 확인하기

Pod가 정상적으로 실행되면 Spring Boot 서버가 응답하는지 확인한다.

### 7.1. Pod 내부로 들어가서 요청 보내기

```bash
kubectl exec -it spring-pod -- bash
curl localhost:8080
```

만약 이미지에 `bash`가 없다면 `sh`를 사용한다.

```bash
kubectl exec -it spring-pod -- sh
curl localhost:8080
```

Pod 내부에서 `localhost:8080`으로 요청하면 Pod 내부 네트워크 기준으로 Spring Boot 서버에 접근한다.

---

### 7.2. 포트 포워딩으로 요청 보내기

로컬 컴퓨터에서 접속하려면 `kubectl port-forward`를 사용할 수 있다.

```bash
kubectl port-forward pod/spring-pod 12345:8080
```

이 명령어는 로컬 컴퓨터의 `12345`번 포트를 Pod의 `8080`번 포트로 연결한다.

다른 터미널에서 다음처럼 요청한다.

```bash
curl localhost:12345
```

브라우저에서는 다음 주소로 접속할 수 있다.

```text
http://localhost:12345
```

Kubernetes 공식 문서에 따르면 `kubectl port-forward`는 로컬 포트를 Pod의 포트로 전달하는 기능을 제공한다. [2]

---

## 8. Pod 삭제하기

테스트가 끝났다면 Pod를 삭제한다.

```bash
kubectl delete pod spring-pod
```

삭제 여부는 다음 명령어로 확인할 수 있다.

```bash
kubectl get pods
```

---

## 핵심 정리

핵심은 다음과 같다.

- `imagePullPolicy`는 kubelet이 컨테이너 이미지를 언제 pull할지 결정하는 설정이다. [1]
- `Always`는 컨테이너 시작 시 레지스트리를 확인한다. [1]
- `IfNotPresent`는 로컬에 이미지가 없을 때만 pull한다. [1]
- `Never`는 이미지를 pull하지 않고 로컬 이미지만 사용한다. [1]
- 이미지 태그를 생략하면 `latest`로 취급되고, `imagePullPolicy`는 기본적으로 `Always`가 된다. [1]
- `image: spring-server`처럼 태그 없이 적으면 로컬 이미지가 있어도 레지스트리를 확인하려고 하면서 `ImagePullBackOff`가 발생할 수 있다.
- 로컬 이미지를 사용하려면 `imagePullPolicy: IfNotPresent`를 명시한다.
- 단, 로컬 이미지는 Pod가 실행되는 노드에 존재해야 한다.

---

## 출처

확인일: 2026-05-18

[1] Kubernetes Documentation, 이미지 - 이미지 풀 정책: <https://kubernetes.io/ko/docs/concepts/containers/images/#image-pull-policy>
[2] Kubernetes Documentation, Use Port Forwarding to Access Applications in a Cluster: <https://kubernetes.io/docs/tasks/access-application-cluster/port-forward-access-application-cluster/>
