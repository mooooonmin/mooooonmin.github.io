---
title: 파드(Pod) 디버깅 하는 방법
category: p
date: 2026-05-20 00:00:00 +0900
tags: [kubernetes, k8s, pod, debugging, kubectl, logs]
---

## 1. Pod가 정상적으로 실행되지 않았을 때

Pod를 생성하다 보면 `Running` 상태가 아니라 `ErrImagePull`, `ImagePullBackOff`, `CrashLoopBackOff` 같은 상태가 나타날 수 있다.

이때 `kubectl get pods`만 보면 대략적인 상태는 알 수 있지만, 구체적인 원인을 바로 알기 어려울 때가 많다.

Pod 디버깅에서는 보통 다음 순서로 확인한다.

1. `kubectl get pods`로 상태 확인
2. `kubectl describe pod [파드명]`으로 상세 정보와 Events 확인
3. `kubectl logs [파드명]`으로 애플리케이션 로그 확인
4. `kubectl exec -it [파드명] -- sh` 또는 `bash`로 Pod 내부 접속

Kubernetes 공식 문서에 따르면 `kubectl describe`는 선택한 리소스의 상세 설명과 관련 리소스, events를 출력한다. [1]

---

## 2. 매니페스트 파일 생성하기

예시로 Nginx Pod를 생성해보자.

`nginx-pod.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
    - name: nginx-container
      image: nginx:1.26.4
      ports:
        - containerPort: 80
```

각 항목의 의미는 다음과 같다.

- `apiVersion: v1`: Pod 리소스는 core API group의 `v1` 버전을 사용한다.
- `kind: Pod`: 생성할 리소스 종류가 Pod임을 의미한다.
- `metadata.name`: Pod의 이름이다.
- `spec.containers`: Pod 안에서 실행할 컨테이너 목록이다.
- `image`: 컨테이너를 생성할 때 사용할 이미지다.
- `containerPort`: 컨테이너가 사용하는 포트를 명시적으로 표현한다.

---

## 3. Pod 생성하고 상태 확인하기

매니페스트 파일을 적용한다.

```bash
kubectl apply -f nginx-pod.yaml
```

Pod가 생성됐는지 확인한다.

```bash
kubectl get pods
```

정상이라면 다음처럼 `Running` 상태가 된다.

```text
NAME        READY   STATUS    RESTARTS   AGE
nginx-pod   1/1     Running   0          10s
```

하지만 이미지 pull에 실패하면 다음처럼 `ErrImagePull` 또는 `ImagePullBackOff` 상태가 나타날 수 있다.

```text
NAME        READY   STATUS         RESTARTS   AGE
nginx-pod   0/1     ErrImagePull   0          10s
```

`STATUS`만 보면 이미지 관련 문제라는 정도는 알 수 있다. 하지만 정확히 어떤 이미지 이름이나 태그에서 문제가 났는지, 인증 문제인지, 네트워크 문제인지까지는 부족하다.

이럴 때 `describe`를 사용한다.

---

## 4. 에러 메시지 자세히 확인하기

Pod의 세부 정보를 확인한다.

```bash
kubectl describe pod nginx-pod
```

또는 다음처럼 복수형을 써도 된다.

```bash
kubectl describe pods nginx-pod
```

`kubectl describe`는 리소스의 상세 정보와 관련 Events를 보여준다. [1]

출력의 아래쪽에 있는 `Events` 영역을 확인하면 이미지 pull 실패 원인을 더 자세히 볼 수 있다.

예시는 다음과 같다.

```text
Events:
  Type     Reason     Message
  ----     ------     -------
  Normal   Pulling    Pulling image "nginx:1.26.4"
  Warning  Failed     Failed to pull image "nginx:1.26.4"
  Warning  Failed     Error: ErrImagePull
```

이 영역에서 확인할 수 있는 내용은 보통 다음과 같다.

- 어떤 이미지를 pull하려고 했는지
- 이미지 pull이 실패했는지
- 이미지 태그가 없는지
- 레지스트리 인증이 실패했는지
- 네트워크 또는 DNS 문제가 있는지

따라서 Pod가 생성되지 않거나 `Running` 상태가 되지 않으면 먼저 `describe`의 Events를 확인하는 것이 좋다.

---

## 5. Pod 로그를 확인하고 싶을 때

이미지 문제를 해결한 뒤, 실행 중인 애플리케이션의 로그를 보고 싶을 때는 `kubectl logs`를 사용한다.

예를 들어 이미지 태그를 정상적인 값으로 수정한다.

`nginx-pod.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
    - name: nginx-container
      image: nginx:1.26.2
      ports:
        - containerPort: 80
```

변경사항을 적용한다.

```bash
kubectl apply -f nginx-pod.yaml
```

Pod 로그를 확인한다.

```bash
kubectl logs nginx-pod
```

Kubernetes 공식 문서에 따르면 `kubectl logs`는 Pod 안의 컨테이너 로그를 출력한다. Pod에 컨테이너가 하나만 있으면 컨테이너 이름은 생략할 수 있다. [2]

만약 Pod 안에 컨테이너가 여러 개 있다면 `-c` 옵션으로 컨테이너 이름을 지정한다.

```bash
kubectl logs nginx-pod -c nginx-container
```

실시간으로 로그를 보고 싶다면 `-f` 옵션을 사용한다.

```bash
kubectl logs -f nginx-pod
```

이전 컨테이너 인스턴스의 로그를 보고 싶을 때는 `--previous` 또는 `-p` 옵션을 사용할 수 있다. Kubernetes 공식 문서도 이전에 종료된 컨테이너 로그를 확인하는 예시를 제공한다. [2]

```bash
kubectl logs nginx-pod --previous
```

---

## 6. Pod에 접속하고 싶을 때

실행 중인 Pod 내부에 들어가서 직접 명령어를 실행하고 싶을 때는 `kubectl exec`를 사용한다.

Kubernetes 공식 문서에 따르면 `kubectl exec`는 컨테이너 안에서 명령을 실행한다. [3]

```bash
kubectl exec -it nginx-pod -- bash
```

Docker의 다음 명령어와 비슷하게 이해하면 된다.

```bash
docker exec -it [컨테이너 ID] bash
```

다만 컨테이너 이미지에 따라 `bash`가 설치되어 있지 않을 수 있다.

`bash`로 접속이 안 되면 `sh`를 사용한다.

```bash
kubectl exec -it nginx-pod -- sh
```

Kubernetes 공식 quick reference도 실행 중인 Pod에 interactive shell로 접근하는 예시로 다음 형식을 안내한다. [4]

```bash
kubectl exec --stdin --tty my-pod -- /bin/sh
```

Nginx Pod 안에 들어간 뒤에는 다음처럼 내부에서 요청을 보내볼 수 있다.

```bash
curl localhost:80
```

---

## 7. 자주 쓰는 디버깅 명령어 정리

Pod 목록 확인:

```bash
kubectl get pods
```

Pod 상세 정보와 Events 확인:

```bash
kubectl describe pod nginx-pod
```

Pod 로그 확인:

```bash
kubectl logs nginx-pod
```

Pod 로그 실시간 확인:

```bash
kubectl logs -f nginx-pod
```

여러 컨테이너 중 특정 컨테이너 로그 확인:

```bash
kubectl logs nginx-pod -c nginx-container
```

Pod 내부 접속:

```bash
kubectl exec -it nginx-pod -- sh
```

Pod 삭제:

```bash
kubectl delete pod nginx-pod
```

---

## 핵심 정리

Pod 디버깅의 핵심은 다음과 같다.

- `kubectl get pods`로 현재 상태를 먼저 확인한다.
- `ErrImagePull`, `ImagePullBackOff`처럼 상태만으로 원인이 부족할 때는 `kubectl describe pod [파드명]`으로 Events를 확인한다. [1]
- 애플리케이션 로그는 `kubectl logs [파드명]`으로 확인한다. [2]
- Pod 안에 컨테이너가 여러 개 있으면 `kubectl logs [파드명] -c [컨테이너명]`처럼 컨테이너를 지정한다. [2]
- 실행 중인 Pod 내부에서 명령어를 실행하려면 `kubectl exec -it [파드명] -- sh` 또는 `bash`를 사용한다. [3][4]
- `bash`가 없으면 `sh`로 접속을 시도한다.

---

## 출처

확인일: 2026-05-18

[1] Kubernetes Documentation, kubectl describe: <https://kubernetes.io/docs/reference/kubectl/kubectl-cmds/#describe>
[2] Kubernetes Documentation, kubectl logs: <https://kubernetes.io/docs/reference/kubectl/generated/kubectl_logs/>
[3] Kubernetes Documentation, kubectl exec: <https://kubernetes.io/docs/reference/kubectl/kubectl-cmds/#exec>
[4] Kubernetes Documentation, kubectl Quick Reference - Interacting with running Pods: <https://kubernetes.io/docs/reference/kubectl/quick-reference/#interacting-with-running-pods>
