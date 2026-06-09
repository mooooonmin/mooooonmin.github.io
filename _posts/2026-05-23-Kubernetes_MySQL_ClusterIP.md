---
title: Kubernetes에서 외부 MySQL 접근 막기
category: k
date: 2026-05-23 00:00:10 +0900
tags: [kubernetes, k8s, mysql, service, clusterip, nodeport, port-forward, security]
---

## 1. 기존 구성의 보안 문제

기존 MySQL Service가 `NodePort` 타입으로 만들어져 있으면 외부에서 `<NodeIP>:<NodePort>` 형태로 Service에 접근할 수 있다.

예를 들어 MySQL Service가 다음처럼 설정되어 있다고 가정한다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql-service
spec:
  type: NodePort
  selector:
    app: mysql-db
  ports:
    - protocol: TCP
      port: 3306
      targetPort: 3306
      nodePort: 30002
```

이 설정에서는 MySQL이 `30002`번 NodePort를 통해 외부에 노출된다.

Kubernetes 공식 문서에 따르면 `NodePort` Service는 각 Node의 IP에서 정적 포트로 Service를 노출하고, 클러스터 외부에서 적절한 프로토콜과 포트로 Node에 연결해 접근할 수 있다. [1]

```text
외부 사용자
  |
  v
NodeIP:30002
  |
  v
mysql-service
  |
  v
MySQL Pod:3306
```

MySQL은 일반 사용자가 직접 접근해야 하는 서비스가 아니다. 이 구조에서는 애플리케이션 서버를 거치지 않고 DB 포트로 직접 접근할 수 있는 경로가 생긴다.

따라서 외부에서 직접 접근할 필요가 없는 DB Service는 `NodePort`가 아니라 `ClusterIP`로 두는 편이 적절하다.

---

## 2. Service 타입 복습

Kubernetes Service 타입은 Service를 어떤 범위로 노출할지 결정한다.

| 타입 | 동작 |
|---|---|
| `ClusterIP` | Service를 클러스터 내부 IP로 노출한다. Service 타입을 명시하지 않으면 기본값으로 사용된다. [1] |
| `NodePort` | 각 Node의 IP와 정적 포트를 통해 Service를 노출한다. 외부에서 `<NodeIP>:<NodePort>`로 접근할 수 있다. [1] |
| `LoadBalancer` | 외부 로드밸런서를 사용해 Service를 외부에 노출한다. Kubernetes는 로드밸런서 컴포넌트를 직접 제공하지 않고, 클라우드 제공자 등과 통합해 사용한다. [1] |

이번 목표는 MySQL을 외부에 직접 노출하지 않는 것이다. 그러므로 MySQL Service 타입은 `ClusterIP`가 맞다.

`ClusterIP`는 Service를 클러스터 내부 IP로 노출하며, 공식 문서에서는 이 타입의 Service가 클러스터 내부에서만 도달 가능하다고 설명한다. [1]

---

## 3. MySQL Service를 ClusterIP로 수정하기

기존 `mysql-service.yaml`에서 `type`을 `ClusterIP`로 바꾸고 `nodePort`를 제거한다.

`mysql-service.yaml`

```yaml
apiVersion: v1
kind: Service

# Service 기본 정보
metadata:
  name: mysql-service

# Service 세부 정보
spec:
  type: ClusterIP
  selector:
    app: mysql-db
  ports:
    - protocol: TCP
      port: 3306
      targetPort: 3306
```

변경 전후의 핵심 차이는 다음과 같다.

```diff
 spec:
-  type: NodePort
+  type: ClusterIP
   selector:
     app: mysql-db
   ports:
     - protocol: TCP
       port: 3306
       targetPort: 3306
-      nodePort: 30002
```

`ClusterIP` Service에서는 `nodePort`를 지정하지 않는다. `nodePort`는 `NodePort` 타입에서 외부 접근 포트를 지정하는 필드이기 때문이다. [1]

---

## 4. Service를 지웠을 때 장애가 나는지 확인하기

먼저 기존 MySQL Service를 삭제해 본다.

```bash
kubectl delete service mysql-service
```

그 다음 Spring Boot Deployment를 재시작한다.

```bash
kubectl rollout restart deployment spring-deployment
```

Spring Boot 서버가 DB에 연결할 때 `mysql-service`라는 Service 이름을 사용하고 있다면, Service 삭제 후에는 정상적으로 DB에 연결할 수 없다.

이 단계는 "Spring Boot 서버가 MySQL Pod IP에 직접 붙는 것이 아니라 Service 이름을 통해 DB에 접근하고 있는지" 확인하는 과정이다.

다만 실제 실패 메시지는 애플리케이션 설정, JDBC 드라이버, 로그 레벨에 따라 달라질 수 있다. 그러므로 정확한 로그 문구는 이 글만으로 확인할 수 없다.

상태를 확인할 때는 다음 명령어를 사용할 수 있다.

```bash
kubectl get pods
kubectl logs deployment/spring-deployment
```

---

## 5. 수정한 Service 적용하기

수정한 `mysql-service.yaml`을 다시 적용한다.

```bash
kubectl apply -f mysql-service.yaml
```

그리고 Spring Boot Deployment를 다시 재시작한다.

```bash
kubectl rollout restart deployment spring-deployment
```

재시작 상태는 다음 명령어로 확인한다.

```bash
kubectl rollout status deployment/spring-deployment
```

Kubernetes 공식 문서의 `kubectl rollout` 예시에서도 Deployment 재시작 명령으로 `kubectl rollout restart deployment/abc` 형식을 사용한다. [2]

Service 타입이 바뀌었는지는 다음 명령어로 확인한다.

```bash
kubectl get service mysql-service
```

정상적으로 `ClusterIP`로 바뀌었다면 `TYPE`이 `ClusterIP`로 표시되고, `PORT(S)`에는 `3306/TCP`처럼 NodePort 없이 표시된다.

예상 형태는 다음과 같다.

```text
NAME            TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
mysql-service   ClusterIP   10.x.x.x        <none>        3306/TCP   10s
```

---

## 6. Spring Boot 서버와 연결 확인하기

Spring Boot 서버가 정상적으로 MySQL에 연결되는지 확인한다.

확인 방법은 프로젝트 구조에 따라 달라질 수 있지만, 일반적으로 다음 중 하나로 확인할 수 있다.

```bash
kubectl logs deployment/spring-deployment
```

또는 외부에 노출된 Spring Boot API가 있다면 해당 API를 호출해 DB 조회, 저장 기능이 정상 동작하는지 확인한다.

```bash
curl http://<Spring Boot 서버 주소>/<확인할 API 경로>
```

이 글만으로는 사용 중인 API 경로와 응답 형식을 확인할 수 없다. 따라서 위 명령어의 `<확인할 API 경로>`는 실제 프로젝트에서 DB를 사용하는 API 경로로 바꿔야 한다.

---

## 7. 외부에서 MySQL 접속이 막혔는지 확인하기

기존에 외부에서 MySQL에 접속하던 방식이 다음과 같았다고 가정한다.

```text
host: <NodeIP>
port: 30002
```

Service를 `ClusterIP`로 바꾼 뒤에는 이 경로로 접속할 수 없어야 한다.

```bash
mysql -h <NodeIP> -P 30002 -u root -p
```

접속이 실패해야 정상이다.

단, 실패 메시지는 운영체제, MySQL 클라이언트, 네트워크 상태에 따라 달라질 수 있다. 예를 들어 연결 시간 초과, 연결 거부, 라우팅 실패처럼 환경별로 다른 메시지가 나올 수 있다. 이 글만으로 특정 에러 문구까지 단정할 수는 없다.

구조를 그림으로 정리하면 다음과 같다.

```text
변경 전: NodePort

외부 사용자
  |
  v
NodeIP:30002
  |
  v
mysql-service
  |
  v
MySQL Pod
```

```text
변경 후: ClusterIP

외부 사용자
  |
  x
mysql-service

Spring Boot Pod
  |
  v
mysql-service:3306
  |
  v
MySQL Pod
```

---

## 8. DB 관리가 필요할 때는 port-forward 사용하기

MySQL을 외부에 항상 열어 두지 않아도, 관리가 필요할 때는 `kubectl port-forward`를 사용할 수 있다.

먼저 MySQL Pod 이름을 확인한다.

```bash
kubectl get pods
```

그 다음 로컬 `3306` 포트를 MySQL Pod의 `3306` 포트로 전달한다.

```bash
kubectl port-forward pod/<MySQL 파드명> 3306:3306
```

Kubernetes 공식 문서에 따르면 `kubectl port-forward`는 하나 이상의 로컬 포트를 Pod로 전달하는 명령이다. 기본 `--address` 값은 `localhost`이며, `localhost`가 지정되면 `kubectl`은 `127.0.0.1`과 `::1`에 바인딩을 시도한다. [3]

따라서 위 명령을 기본 옵션으로 실행하면 로컬 컴퓨터에서 다음 주소로 MySQL에 접속할 수 있다.

```text
host: 127.0.0.1
port: 3306
```

예시는 다음과 같다.

```bash
mysql -h 127.0.0.1 -P 3306 -u root -p
```

포트 포워딩은 명령어가 실행 중인 동안만 유지된다. 공식 문서에 따르면 선택된 Pod가 종료되면 포워딩 세션도 끝나며, 다시 사용하려면 명령을 다시 실행해야 한다. [3]

---

## 9. ClusterIP만으로 충분한가?

`ClusterIP`로 바꾸면 외부에서 NodePort로 MySQL에 직접 접근하는 경로는 제거된다. 하지만 이것이 "클러스터 내부의 모든 접근까지 차단한다"는 뜻은 아니다.

공식 문서 기준으로 `ClusterIP`는 Service를 클러스터 내부 IP로 노출하는 타입이다. [1] 즉, 같은 클러스터 내부의 Pod는 네트워크 정책이나 애플리케이션 설정에 따라 여전히 `mysql-service:3306`으로 접근할 수 있다.

클러스터 내부에서도 어떤 Pod가 MySQL에 접근할 수 있는지 제한하려면 `NetworkPolicy`를 검토해야 한다.

Kubernetes 공식 문서에 따르면 `NetworkPolicy`는 IP 주소 또는 포트 수준에서 트래픽 흐름을 제어할 때 사용하는 리소스이며, NetworkPolicy를 사용하려면 이를 지원하는 네트워크 플러그인이 필요하다. [4]

따라서 이번 변경의 범위는 다음처럼 정리할 수 있다.

```text
이번 글에서 해결한 것:
- 외부에서 NodePort 30002로 MySQL에 직접 접근하는 경로 제거

이번 글만으로 해결하지 않는 것:
- 클러스터 내부 Pod 사이의 세부 접근 제어
- MySQL 계정 권한 관리
- Secret 암호화 저장
- 운영 환경 방화벽, 보안 그룹, VPC 네트워크 정책
```

---

## 정리

MySQL처럼 외부 사용자가 직접 접근할 필요가 없는 DB는 `NodePort`로 노출하지 않는 것이 좋다.

이번 변경의 핵심은 다음과 같다.

```text
1. mysql-service.yaml에서 type을 NodePort에서 ClusterIP로 변경
2. nodePort: 30002 제거
3. kubectl delete service mysql-service로 기존 Service 삭제
4. kubectl apply -f mysql-service.yaml로 수정한 Service 적용
5. kubectl rollout restart deployment spring-deployment로 Spring Boot 재시작
6. kubectl get service mysql-service로 TYPE이 ClusterIP인지 확인
7. 외부에서 <NodeIP>:30002 접속이 실패하는지 확인
8. DB 관리가 필요할 때만 kubectl port-forward 사용
```

최종 구조는 다음과 같다.

```text
외부 사용자 -> Spring Boot Service -> Spring Boot Pod -> mysql-service -> MySQL Pod

외부 사용자 -> NodeIP:30002 -> MySQL Pod
위 경로는 제거한다.
```

---

## 출처

[1] Kubernetes Docs, "Service", 확인일 2026-05-23, <https://kubernetes.io/docs/concepts/services-networking/service/>

[2] Kubernetes Docs, "kubectl rollout", 확인일 2026-05-23, <https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/>

[3] Kubernetes Docs, "kubectl port-forward", 확인일 2026-05-23, <https://kubernetes.io/docs/reference/kubectl/generated/kubectl_port-forward/>

[4] Kubernetes Docs, "Network Policies", 확인일 2026-05-23, <https://kubernetes.io/docs/concepts/services-networking/network-policies/>
