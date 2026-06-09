---
title: Kubernetes Volume
category: k
date: 2026-05-22 00:00:00 +0900
tags: [kubernetes, volume, pv, pvc, storage]
---

## 1. 파드가 가진 저장 공간 문제

Kubernetes에서 애플리케이션은 보통 Pod 단위로 실행된다.

Pod 안에서 실행되는 컨테이너가 파일을 만들 수는 있지만, 그 파일을 항상 안전하게 오래 보관할 수 있는 것은 아니다.
Pod가 새로 만들어지거나 기존 Pod가 사라지는 상황에서는 Pod 내부에만 있던 데이터도 함께 사라질 수 있다.

예를 들어 MySQL을 Pod로 실행하고, MySQL 데이터가 컨테이너 내부 파일시스템에만 저장되어 있다면 문제가 생길 수 있다.
Pod가 교체되거나 삭제될 때 데이터까지 같이 사라질 수 있기 때문이다.

이런 문제를 해결하기 위해 Kubernetes에서는 **Volume**을 사용한다. [1]

---

## 2. Volume이란?

Volume은 Pod 안의 컨테이너가 사용할 수 있는 디렉터리 형태의 저장 공간이다.

Kubernetes 공식 문서에 따르면 Volume은 Pod 안의 컨테이너가 접근할 수 있는 디렉터리이며, 실제 저장 방식은 어떤 Volume 타입을 사용하느냐에 따라 달라진다. [1]

Pod에서 Volume을 사용하려면 두 가지 설정이 필요하다. [1]

- `.spec.volumes`: Pod에 제공할 Volume을 정의한다.
- `.spec.containers[*].volumeMounts`: 컨테이너 안의 어느 경로에 Volume을 연결할지 정의한다.

즉, Volume은 단순히 저장소를 만드는 개념이 아니라, **Pod와 컨테이너가 특정 저장 공간을 어떤 경로로 사용할지 연결하는 방법**이다.

---

## 3. 일시적 Volume과 Persistent Volume

Kubernetes Volume은 생명주기 기준으로 크게 일시적 Volume과 Persistent Volume으로 나누어 이해할 수 있다.

### 일시적 Volume

일시적 Volume은 특정 Pod의 생명주기에 묶이는 Volume이다.

Kubernetes 공식 문서에 따르면 ephemeral volume 타입은 특정 Pod의 생명주기와 연결되어 있고, Pod가 사라지면 Kubernetes가 ephemeral volume도 삭제한다. [1]

따라서 임시 파일, 캐시, Pod 안의 컨테이너 간 파일 공유처럼 Pod가 사라질 때 같이 없어져도 되는 데이터에 적합하다.

주의할 점은, 이 글에서 말하는 일시적 Volume은 사용자가 흔히 말하는 “파드 내부 저장 공간”에 가까운 개념이다.
Kubernetes에는 `local`이라는 PersistentVolume 타입도 있으므로, 운영 문서에서는 “로컬 볼륨”이라는 표현만으로 설명하면 혼동될 수 있다.

### Persistent Volume

Persistent Volume은 개별 Pod보다 오래 살아남을 수 있는 저장 공간이다.

Kubernetes 공식 문서에 따르면 Persistent Volume은 관리자가 미리 만들거나 StorageClass를 통해 동적으로 만들어지는 클러스터의 저장 리소스이며, 특정 Pod와 독립적인 생명주기를 가진다. [2]

따라서 MySQL, PostgreSQL, 파일 업로드 저장소처럼 Pod가 삭제되거나 새로 만들어져도 데이터가 유지되어야 하는 경우에는 Persistent Volume을 사용해야 한다.

---

## 4. PV와 PVC 관계

Persistent Volume을 이해하려면 PV와 PVC를 구분해야 한다.

| 구분 | 의미 |
|---|---|
| PV | 클러스터에 준비된 실제 저장 공간 |
| PVC | 사용자가 요청하는 저장 공간 요청서 |

Kubernetes 공식 문서에 따르면 PVC는 사용자가 저장 공간을 요청하는 리소스이며, CPU나 메모리를 Pod가 요청하는 것처럼 PVC는 PV 리소스를 요청한다. [2]

Pod는 PV에 직접 연결되는 것이 아니라 PVC를 Volume처럼 사용한다.
Kubernetes는 PVC가 어떤 PV와 연결되어 있는지 확인한 뒤, 해당 Volume을 Pod에 마운트한다. [2]

구조를 단순화하면 다음과 같다.

```text
Pod
  -> PVC
      -> PV
          -> 실제 저장소
```

여기서 실제 저장소는 클러스터 내부에 준비된 저장 장치일 수도 있고, NFS나 클라우드 제공자의 디스크 같은 외부 저장소일 수도 있다. [2]

---

## 5. PVC가 필요한 이유

PVC는 Pod와 실제 저장소 사이의 중개자 역할을 한다.

Pod가 “어떤 물리 저장소를 직접 쓸지”까지 알 필요가 없게 만들고, 필요한 저장 용량과 접근 방식만 요청할 수 있게 해준다.

이 구조의 장점은 다음과 같다.

- Pod는 PVC만 참조하면 된다.
- 실제 저장소 구현 방식은 PV와 StorageClass 쪽에서 관리할 수 있다.
- 저장소가 NFS인지, 클라우드 디스크인지, 다른 스토리지 시스템인지를 애플리케이션 설정에서 분리할 수 있다.

즉, PVC는 애플리케이션 입장에서 저장소 사용 방식을 단순하게 만들어주는 추상화 계층이다.

---

## 정리

> Pod 내부에만 저장된 데이터는 Pod 교체나 삭제 상황에서 유지되지 않을 수 있다.
>
> Volume은 Pod 안의 컨테이너가 특정 저장 공간을 사용할 수 있게 연결하는 방법이다.
>
> 오래 유지되어야 하는 데이터는 Pod 생명주기와 분리된 Persistent Volume을 사용해야 한다.
>
> Pod는 PV를 직접 사용하는 것이 아니라 PVC를 통해 PV를 사용한다.

---

## 출처

1. Kubernetes Docs, "Volumes"
   https://kubernetes.io/docs/concepts/storage/volumes/

2. Kubernetes Docs, "Persistent Volumes"
   https://kubernetes.io/docs/concepts/storage/persistent-volumes/
