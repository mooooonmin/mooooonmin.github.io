---
title: Kubernetes Pod
category: docker-kubernetes
date: 2026-05-19 00:00:00 +0900
tags: [kubernetes, k8s, pod, container, docker]
---

## 1. 파드(Pod)란?

파드(Pod)는 **쿠버네티스에서 만들고 관리할 수 있는 가장 작은 배포 단위**이다. Kubernetes 공식 문서는 Pod를 Kubernetes에서 만들고 관리할 수 있는 가장 작은 배포 가능한 컴퓨팅 단위라고 설명한다. [1]

또한 Pod는 **하나 이상의 컨테이너 그룹**이다. 이 컨테이너들은 스토리지와 네트워크 리소스를 공유하고, 컨테이너를 어떻게 실행할지에 대한 명세를 함께 가진다. [1]

쉽게 말하면, Docker를 배울 때는 보통 하나의 프로그램을 실행시키는 단위를 컨테이너라고 생각했다면, Kubernetes에서는 보통 하나의 프로그램을 실행시키는 단위를 Pod라고 생각하면 이해하기 쉽다.

다만 정확히 말하면 Pod와 컨테이너는 같은 개념이 아니다.

- 컨테이너: 실제 애플리케이션 프로세스가 실행되는 단위
- Pod: Kubernetes가 관리하는 최소 배포 단위이며, 하나 이상의 컨테이너를 감싸는 단위 [1]

Kubernetes 공식 문서도 일반적인 사용 방식에서는 하나의 Pod에 하나의 컨테이너를 두는 모델이 가장 흔하며, 이 경우 Pod를 하나의 컨테이너를 감싸는 wrapper처럼 생각할 수 있다고 설명한다. [1]

---

## 2. Pod는 쿠버네티스의 가장 작은 단위

Kubernetes에서 애플리케이션을 실행할 때 직접 컨테이너 하나만 던져서 실행한다고 보기보다는, Pod라는 단위로 실행한다고 이해하면 된다.

일반적으로는 다음과 같은 구조가 가장 흔하다. [1]

```text
Pod
└── Container
    └── Application
```

예를 들어 결제 서버 애플리케이션을 Kubernetes에서 실행한다면 보통 다음처럼 생각할 수 있다.

```text
payment-pod
└── payment-container
    └── payment application
```

따라서 실무에서 다음과 같은 표현을 자주 사용한다.

- 결제 서버 Pod 2개가 떠 있다.
- 결제 서버 Pod 1개가 죽었다.
- 업로드 서버를 Pod로 하나 띄우자.

즉, Kubernetes에서는 "서버 하나를 띄운다"는 말을 "Pod 하나를 띄운다"는 식으로 표현하는 경우가 많다.

---

## 3. 하나의 Pod에 여러 컨테이너가 들어갈 수도 있다

일반적으로는 하나의 Pod가 하나의 컨테이너를 가진다. 하지만 Pod는 반드시 컨테이너 하나만 가져야 하는 것은 아니다.

Kubernetes 공식 문서는 Pod가 함께 동작해야 하는 여러 컨테이너를 포함할 수 있다고 설명한다. 이런 컨테이너들은 같은 물리 또는 가상 머신에 함께 배치되고 함께 스케줄링되며, 리소스와 의존성을 공유할 수 있다. [1]

예를 들면 다음과 같은 구조가 가능하다.

```text
Pod
├── main-container
│   └── main application
└── sidecar-container
    └── helper process
```

이런 구조는 메인 애플리케이션 컨테이너 옆에 보조 역할을 하는 컨테이너가 붙는 형태다. Kubernetes 공식 문서는 한 컨테이너가 공유 볼륨의 데이터를 외부에 제공하고, 다른 컨테이너가 그 파일을 갱신하는 예를 설명한다. [1]

따라서 처음에는 다음처럼 기억하면 된다.

> 대부분은 1 Pod = 1 Container로 사용하지만, 필요하면 1 Pod 안에 여러 Container를 함께 둘 수 있다. [1]

---

## 4. Pod도 이미지를 기반으로 실행된다

Kubernetes에서 Pod 안의 컨테이너를 실행하려면 컨테이너 이미지가 필요하다.

예를 들어 아래 YAML은 `nginx:1.14.2` 이미지를 사용하는 Pod 예시다. Kubernetes 공식 문서의 Pod 예제도 `spec.containers[].image`에 컨테이너 이미지를 지정한다. [2]

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
    - name: nginx
      image: nginx:1.14.2
      ports:
        - containerPort: 80
```

즉, Docker에서 이미지를 기반으로 컨테이너를 실행하듯이, Kubernetes도 Pod 명세 안에 컨테이너 이미지를 적고 그 이미지를 기반으로 컨테이너를 실행한다.

---

## 5. 예시로 이해하기

### 결제 서버 Pod 2개가 떠 있다

```text
payment-pod-1
└── payment-container

payment-pod-2
└── payment-container
```

이 상황은 결제 서버 애플리케이션이 Pod 2개로 실행 중이라는 뜻이다.

---

### 결제 서버 Pod 1개가 죽었다

```text
payment-pod-1  Running
payment-pod-2  Failed
```

이 상황은 결제 서버 역할을 하던 Pod 중 하나가 실패했다는 뜻이다.

Kubernetes 공식 문서에 따르면 Pod는 일시적인 존재로 취급된다. Pod는 생성되고, 고유 ID를 받고, 노드에 스케줄링되어 실행되다가 종료되거나 삭제될 수 있다. [3]

---

### 업로드 서버를 하나 띄우자

```text
upload-pod
└── upload-container
    └── upload application
```

이 말은 업로드 서버 애플리케이션을 담은 컨테이너를 Pod 단위로 실행하자는 뜻으로 이해할 수 있다.

---

## 핵심 정리

Pod의 핵심은 다음과 같다.

- Pod는 Kubernetes에서 만들고 관리할 수 있는 가장 작은 배포 단위이다. [1]
- Pod는 하나 이상의 컨테이너를 담는 그룹이다. [1]
- 일반적으로는 하나의 Pod에 하나의 컨테이너를 두는 방식이 가장 흔하다. [1]
- 예외적으로 하나의 Pod 안에 여러 컨테이너를 둘 수 있다. [1]
- Pod 안의 컨테이너는 이미지를 기반으로 실행된다. [2]
- Kubernetes에서는 컨테이너를 직접 관리한다고 보기보다 Pod 단위로 애플리케이션을 실행하고 관리한다고 이해하면 된다. [1]

---

## 출처

확인일: 2026-05-18

[1] Kubernetes Documentation, Pods: <https://kubernetes.io/docs/concepts/workloads/pods/>
[2] Kubernetes Documentation, Pods - Using Pods: <https://kubernetes.io/docs/concepts/workloads/pods/#using-pods>
[3] Kubernetes Documentation, Pod Lifecycle: <https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/>
