---
title: Volume 활용해 MySQL 실행시키기
category: v
date: 2026-05-22 00:00:10 +0900
tags: [kubernetes, mysql, volume, pv, pvc, persistent-volume]
---

## 1. 실습 목표

이전 실습에서 MySQL Pod를 다시 만들거나 Deployment를 재시작했을 때, 기존에 만들었던 `new-db` 데이터베이스가 사라지는 상황을 확인했다.

실제 데이터베이스에서는 Pod가 교체되더라도 데이터가 함께 사라지면 안 된다.
따라서 MySQL 데이터 디렉터리인 `/var/lib/mysql`을 Kubernetes Volume에 연결해 데이터가 유지되도록 설정한다.

이번 실습에서는 PersistentVolume(PV), PersistentVolumeClaim(PVC), Deployment를 함께 사용한다.

```text
MySQL 컨테이너
  -> /var/lib/mysql
      -> PVC
          -> PV
              -> Node의 /mnt/data
```

Kubernetes 공식 문서에 따르면 PersistentVolume은 클러스터의 저장 리소스이고, PersistentVolumeClaim은 사용자가 저장소를 요청하는 리소스이다. [1]

---

## 2. PV와 PVC 매니페스트 작성

먼저 MySQL이 사용할 실제 저장 공간인 PV와, Pod가 참조할 PVC를 작성한다.

### PV 작성

`mysql-pv.yaml`

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mysql-pv
spec:
  storageClassName: my-storage
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/mnt/data"
```

주요 설정은 다음과 같다.

| 설정 | 의미 |
|---|---|
| `storageClassName` | PVC와 매칭할 때 사용할 스토리지 클래스 이름 |
| `capacity.storage` | PV가 제공하는 저장 용량 |
| `accessModes` | 볼륨 접근 방식 |
| `hostPath.path` | Node 파일시스템에서 사용할 경로 |

`hostPath`는 Node의 파일이나 디렉터리를 Pod에 마운트하는 Volume 타입이다. Kubernetes 공식 문서는 `hostPath`가 대부분의 Pod에 필요한 방식은 아니며, 보안 위험이 있으므로 가능하면 피하라고 설명한다. [2]

따라서 이 설정은 학습용 또는 로컬 실습용 예시로 이해하는 것이 좋다.

### PVC 작성

`mysql-pvc.yaml`

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  storageClassName: my-storage
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

PVC는 Pod가 직접 PV를 찾지 않게 해주는 요청서 역할을 한다.

이 예시에서는 PV와 PVC의 `storageClassName`, `accessModes`, 요청 용량 조건이 맞기 때문에 PVC가 PV에 바인딩될 수 있다. Kubernetes 공식 문서도 control plane이 클러스터 안의 적절한 PV와 PVC를 바인딩한다고 설명한다. [1]

---

## 3. Deployment에 PVC 연결하기

이제 MySQL Deployment에서 PVC를 Volume으로 사용하도록 수정한다.

`mysql-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql-db
  template:
    metadata:
      labels:
        app: mysql-db
    spec:
      containers:
        - name: mysql-container
          image: mysql
          ports:
            - containerPort: 3306
          env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-secret
                  key: mysql-root-password
            - name: MYSQL_DATABASE
              valueFrom:
                configMapKeyRef:
                  name: mysql-config
                  key: mysql-database
          volumeMounts:
            - name: mysql-persistent-storage
              mountPath: /var/lib/mysql
      volumes:
        - name: mysql-persistent-storage
          persistentVolumeClaim:
            claimName: mysql-pvc
```

여기서 중요한 부분은 `volumeMounts`와 `volumes`이다.

| 설정 | 의미 |
|---|---|
| `volumeMounts[*].name` | 컨테이너에 연결할 Volume 이름 |
| `volumeMounts[*].mountPath` | 컨테이너 내부에서 Volume을 사용할 경로 |
| `volumes[*].name` | Pod가 사용할 Volume 이름 |
| `persistentVolumeClaim.claimName` | 연결할 PVC 이름 |

`volumeMounts[*].name`과 `volumes[*].name`은 같은 값이어야 한다.
이 값이 같아야 Pod 안에서 정의한 Volume을 컨테이너의 특정 경로에 마운트할 수 있다.

MySQL 공식 이미지 문서에 따르면 `MYSQL_DATABASE`는 컨테이너가 처음 시작될 때 지정한 이름의 데이터베이스를 만들 때 사용된다. [3]
이미 초기화된 데이터 디렉터리를 다시 사용하는 경우에는 기존 데이터가 유지되므로, 같은 환경 변수를 다시 지정해도 기존 데이터가 매번 새로 만들어지는 방식으로 동작하지 않는다.

---

## 4. 매니페스트 적용하기

작성한 매니페스트를 다음 순서로 적용한다.

```bash
kubectl apply -f mysql-pv.yaml
kubectl apply -f mysql-pvc.yaml
kubectl apply -f mysql-deployment.yaml
```

적용 후에는 PVC가 정상적으로 바인딩되었는지 확인한다.

```bash
kubectl get pv
kubectl get pvc
```

PVC의 상태가 `Bound`라면 PVC가 PV와 연결된 것이다.

---

## 5. 데이터 유지 확인하기

먼저 MySQL에 접속해서 새 데이터베이스를 만든다.

```sql
CREATE DATABASE `new-db`;
SHOW DATABASES;
```

그다음 Deployment를 재시작한다.

```bash
kubectl rollout restart deployment mysql-deployment
```

재시작이 끝난 뒤 다시 MySQL에 접속해서 데이터베이스 목록을 확인한다.

```sql
SHOW DATABASES;
```

`new-db`가 그대로 남아 있다면 MySQL 데이터가 Pod 내부에만 저장된 것이 아니라, PVC를 통해 PV에 저장되고 있다는 뜻이다.

---

## 6. 실습 시 주의할 점

이 예시는 `hostPath`를 사용하기 때문에 로컬 Kubernetes 학습 환경에서는 이해하기 쉽다.
하지만 운영 환경에서 데이터베이스 저장소로 그대로 사용하기에는 적합하지 않을 수 있다.

주의할 점은 다음과 같다.

- `hostPath`는 특정 Node의 파일시스템 경로를 사용한다. [2]
- Pod가 다른 Node로 이동하면 같은 데이터가 보장되지 않을 수 있다. [2]
- Kubernetes 공식 문서는 `hostPath` 사용이 여러 보안 위험을 만든다고 경고한다. [2]
- 운영 환경에서는 보통 클라우드 디스크, NFS, CSI 드라이버, StorageClass 기반 동적 프로비저닝 같은 방식을 검토한다. [1]

따라서 이 글의 목적은 MySQL과 PV/PVC 연결 흐름을 이해하는 것이다.
운영 환경에서는 클러스터 구조와 스토리지 요구사항에 맞는 저장소 방식을 별도로 선택해야 한다.

---

## 핵심 정리

> MySQL 데이터는 컨테이너 내부에만 두면 Pod 교체나 삭제 시 사라질 수 있다.
>
> MySQL의 데이터 디렉터리인 `/var/lib/mysql`을 PVC에 연결하면 PV를 통해 데이터를 유지할 수 있다.
>
> Pod는 PV를 직접 참조하지 않고 PVC를 Volume으로 사용한다.
>
> `hostPath`는 학습용으로는 단순하지만, 운영 환경에서는 보안과 Node 종속성을 주의해야 한다.

---

## 출처

1. Kubernetes Docs, "Persistent Volumes"
   https://kubernetes.io/docs/concepts/storage/persistent-volumes/

2. Kubernetes Docs, "Volumes - hostPath"
   https://kubernetes.io/docs/concepts/storage/volumes/#hostpath

3. Docker Library Docs, "mysql"
   https://github.com/docker-library/docs/tree/master/mysql
