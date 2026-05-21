---
title: 파드(Pod)로 띄운 프로그램에 접속이 안 되는 이유
category: docker-kubernetes
date: 2026-05-19 00:00:10 +0900
tags: [kubernetes, k8s, pod, network, port-forward, nginx]
---

## 1. 파드(Pod)로 띄운 프로그램에 접속이 안 되는 이유

Docker를 공부할 때는 컨테이너 내부 네트워크와 컨테이너 외부 네트워크가 분리되어 있다는 점을 배웠다.

Kubernetes에서도 비슷하게, Pod 안에서 실행되는 애플리케이션은 내 로컬 컴퓨터의 네트워크와 그대로 연결되어 있는 것이 아니다.

Kubernetes 공식 문서에 따르면 각 Pod는 고유한 IP 주소를 할당받고, Pod 안의 모든 컨테이너는 네트워크 namespace를 공유한다. 즉, Pod 안의 컨테이너들은 같은 IP 주소와 포트 공간을 공유한다. [1]

그래서 Pod 안에서는 다음처럼 접근할 수 있다.

```bash
curl localhost:80
```

하지만 로컬 컴퓨터에서 바로 다음처럼 요청한다고 해서 항상 Pod 안의 Nginx에 접근할 수 있는 것은 아니다.

```bash
curl localhost:80
```

이때의 `localhost`는 Pod 내부가 아니라 **내 로컬 컴퓨터 자신**을 의미하기 때문이다.

즉, Pod 안의 `localhost:80`과 로컬 컴퓨터의 `localhost:80`은 같은 위치가 아니다.

```text
Local Computer
└── localhost:80

Kubernetes Pod
└── localhost:80
    └── nginx
```

정리하면, Pod로 Nginx를 띄웠는데 로컬 컴퓨터에서 바로 접속이 안 되는 이유는 **Pod의 네트워크와 로컬 컴퓨터의 네트워크가 분리되어 있기 때문**이다.

---

## 2. Pod 내부 네트워크는 컨테이너들이 공유한다

Pod 안에 컨테이너가 하나만 있다면 다음처럼 생각할 수 있다.

```text
Pod
└── nginx-container
    └── nginx:80
```

이 경우 Pod 내부에서 `localhost:80`으로 요청하면 Nginx에 접근할 수 있다.

Pod 안에 컨테이너가 여러 개 있어도 네트워크 관점에서는 같은 Pod 안의 컨테이너들이 IP 주소와 포트 공간을 공유한다. Kubernetes 공식 문서는 같은 Pod 안의 컨테이너들이 `localhost`를 사용해 서로를 찾을 수 있다고 설명한다. [1]

예를 들어 다음과 같은 구조가 가능하다.

```text
Pod
├── app-container
│   └── app
└── nginx-container
    └── nginx:80
```

이때 같은 Pod 안의 다른 컨테이너에서 `localhost:80`으로 요청하면 `nginx-container`의 Nginx에 접근할 수 있다.

단, 이 말은 **Pod 내부에서만** 해당한다. 로컬 컴퓨터에서의 `localhost`는 Pod 내부의 `localhost`가 아니다.

---

## 3. Nginx에 접근하는 방법

Pod로 띄운 Nginx에 접근하려면 대표적으로 다음 두 가지 방법을 사용할 수 있다.

1. Pod 내부로 들어가서 접근하기
2. `kubectl port-forward`로 로컬 포트와 Pod 포트를 연결하기

하나씩 확인해보자.

---

## 4. Pod 내부로 들어가서 Nginx로 요청 보내기

먼저 Pod 내부로 접속한 뒤 Nginx에 요청을 보내는 방법이다.

```bash
kubectl exec -it nginx-pod -- bash
```

`kubectl exec`는 실행 중인 컨테이너 안에서 명령을 실행할 때 사용한다. Docker의 `docker exec -it [컨테이너 ID] bash`와 비슷하게 이해하면 된다.

Pod 내부로 들어간 뒤 다음 명령어를 실행한다.

```bash
curl localhost:80
```

예상되는 흐름은 다음과 같다.

```text
Local Computer
└── kubectl exec
    └── Pod 내부 shell
        └── curl localhost:80
            └── nginx 응답
```

이 방식으로 접근하면 `localhost:80`은 로컬 컴퓨터가 아니라 Pod 내부의 네트워크를 기준으로 해석된다.

따라서 Nginx가 정상적으로 실행 중이고 80번 포트를 listen하고 있다면 응답을 받을 수 있다.

만약 `bash`가 없는 이미지라면 다음처럼 `sh`를 사용할 수 있다.

```bash
kubectl exec -it nginx-pod -- sh
```

---

## 5. 포트 포워딩으로 Nginx에 요청 보내기

두 번째 방법은 `kubectl port-forward`를 사용하는 것이다.

Kubernetes 공식 문서에 따르면 `kubectl port-forward`는 로컬 포트를 Pod의 포트로 전달할 수 있다. [2][3]

예를 들어 로컬 컴퓨터의 8080번 포트를 Pod의 80번 포트와 연결하려면 다음처럼 실행한다.

```bash
kubectl port-forward pod/nginx-pod 8080:80
```

그러면 요청 흐름은 다음과 같다.

```text
Local Computer
└── localhost:8080
    └── kubectl port-forward
        └── nginx-pod:80
            └── nginx
```

이제 다른 터미널에서 다음처럼 요청할 수 있다.

```bash
curl localhost:8080
```

브라우저에서도 다음 주소로 접속할 수 있다.

```text
http://localhost:8080
```

Kubernetes 공식 문서는 `kubectl port-forward` 명령이 종료되지 않고 계속 실행된다고 설명한다. 따라서 포트 포워딩을 유지한 상태에서 테스트하려면 새 터미널을 하나 더 열어 요청을 보내야 한다. [2]

---

## 6. 왜 80:80 대신 8080:80을 쓰는가?

예제에서 다음 명령어를 사용할 수도 있다.

```bash
kubectl port-forward pod/nginx-pod 80:80
```

형식은 다음과 같다.

```text
kubectl port-forward pod/[파드명] [로컬 포트]:[Pod 포트]
```

즉, `80:80`은 로컬 컴퓨터의 80번 포트를 Pod의 80번 포트로 연결한다는 뜻이다.

하지만 로컬의 80번 포트는 이미 다른 프로그램이 사용 중일 수 있고, 운영체제 설정에 따라 관리자 권한이 필요할 수 있다. 그래서 학습이나 테스트에서는 보통 로컬 포트를 8080처럼 잡는 것이 편하다.

```bash
kubectl port-forward pod/nginx-pod 8080:80
```

이 경우에는 로컬에서 `localhost:8080`으로 접속하면 Pod의 `80`번 포트로 연결된다.

---

## 7. Pod 삭제하기

테스트가 끝났다면 Pod를 삭제할 수 있다.

```bash
kubectl delete pod nginx-pod
```

삭제 여부는 다음 명령어로 확인한다.

```bash
kubectl get pods
```

`nginx-pod`가 목록에 보이지 않으면 삭제된 것이다.

---

## 8. 정리

핵심은 다음과 같다.

- Pod 안의 컨테이너들은 네트워크 namespace를 공유한다. [1]
- 같은 Pod 안의 컨테이너들은 같은 IP 주소와 포트 공간을 공유하고, `localhost`로 서로 접근할 수 있다. [1]
- 로컬 컴퓨터의 `localhost`와 Pod 내부의 `localhost`는 같은 위치가 아니다.
- Pod 내부에서 확인하려면 `kubectl exec -it nginx-pod -- bash` 또는 `sh`로 들어가서 `curl localhost:80`을 실행한다.
- 로컬 컴퓨터에서 접근하려면 `kubectl port-forward pod/nginx-pod 8080:80`처럼 로컬 포트와 Pod 포트를 연결한다. [2][3]
- `kubectl port-forward`는 실행 중인 동안 포트 전달을 유지하므로, 요청 테스트는 다른 터미널에서 진행한다. [2]

---

## 참고 자료

확인일: 2026-05-18

[1] Kubernetes Documentation, Pods - Pod networking: <https://kubernetes.io/docs/concepts/workloads/pods/#pod-networking>  
[2] Kubernetes Documentation, Use Port Forwarding to Access Applications in a Cluster: <https://kubernetes.io/docs/tasks/access-application-cluster/port-forward-access-application-cluster/>  
[3] Kubernetes Documentation, kubectl port-forward: <https://kubernetes.io/docs/reference/kubectl/generated/kubectl_port-forward>
