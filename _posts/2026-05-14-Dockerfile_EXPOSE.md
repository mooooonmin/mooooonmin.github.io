---
title: Dockerfile EXPOSE
category: docker-kubernetes
date: 2026-05-14 00:00:00 +0900
tags: [docker, dockerfile, expose, port, container]
---

## 1. EXPOSE란?

`EXPOSE`는 Dockerfile에서 **컨테이너가 실행될 때 어떤 네트워크 포트를 사용할 예정인지 표시하는 명령**이다.

Docker 공식 Dockerfile reference에 따르면 `EXPOSE`는 컨테이너가 런타임에 지정된 네트워크 포트에서 listen한다는 정보를 Docker에 알려준다. [1]

하지만 `EXPOSE`는 포트를 실제로 외부에 공개하지 않는다. Docker 공식 문서에서도 `EXPOSE`는 이미지를 만든 사람과 컨테이너를 실행하는 사람 사이에서 어떤 포트를 publish할 의도인지 알려주는 문서화 역할을 한다고 설명한다. [1]

쉽게 말하면 `EXPOSE`는 다음과 같은 의미에 가깝다.

> 이 컨테이너 안의 프로그램은 보통 이 포트를 사용합니다.

예를 들어 Node.js 서버가 컨테이너 내부에서 3000번 포트로 실행된다면 다음처럼 적을 수 있다.

```dockerfile
EXPOSE 3000
```

---

## 2. 사용법

`EXPOSE`의 기본 문법은 다음과 같다.

```dockerfile
EXPOSE [포트 번호]
```

예시는 다음과 같다.

```dockerfile
EXPOSE 3000
```

Docker 공식 문서에 따르면 프로토콜을 따로 적지 않으면 기본값은 TCP이다. [1]

즉, 다음 두 명령은 같은 의미로 볼 수 있다.

```dockerfile
EXPOSE 3000
EXPOSE 3000/tcp
```

UDP 포트를 표시하려면 다음처럼 작성한다.

```dockerfile
EXPOSE 3000/udp
```

TCP와 UDP를 모두 표시하려면 두 줄을 모두 적는다. [1]

```dockerfile
EXPOSE 3000/tcp
EXPOSE 3000/udp
```

---

## 3. EXPOSE는 포트를 열어주지 않는다

`EXPOSE 3000`을 Dockerfile에 적었다고 해서 내 컴퓨터의 3000번 포트로 바로 접속할 수 있는 것은 아니다.

Docker 공식 문서에 따르면 컨테이너 포트를 호스트 포트로 publish하려면 `docker run`에서 `-p` 또는 `--publish` 옵션을 사용해야 한다. [1][2]

예를 들어 컨테이너 내부의 3000번 포트를 호스트의 8080번 포트로 연결하려면 다음처럼 실행한다.

```bash
docker run -p 8080:3000 my-server
```

Docker 공식 문서의 port publishing 설명에 따르면 `-p HOST_PORT:CONTAINER_PORT` 형식에서 앞의 값은 호스트 포트이고, 뒤의 값은 컨테이너 내부 포트이다. [2]

따라서 위 명령은 다음 의미이다.

- 호스트 포트: `8080`
- 컨테이너 포트: `3000`
- 결과: 호스트의 `8080`으로 들어온 요청을 컨테이너 내부의 `3000`으로 전달한다. [2]

즉, `EXPOSE`와 `-p`는 역할이 다르다.

```dockerfile
EXPOSE 3000
```

위 명령은 "이 이미지의 컨테이너는 3000번 포트를 사용할 예정"이라고 기록하는 것이다.

```bash
docker run -p 8080:3000 my-server
```

위 명령은 실제로 호스트 포트와 컨테이너 포트를 연결하는 것이다.

---

## 4. EXPOSE가 없어도 -p는 동작한다

`EXPOSE`가 없어도 `docker run -p`로 포트를 publish할 수 있다.

Docker 공식 Dockerfile reference는 `EXPOSE` 설정과 관계없이 런타임에 `-p` 옵션으로 포트 설정을 override할 수 있다고 설명한다. [1]

예를 들어 Dockerfile에 `EXPOSE 3000`이 없어도, 컨테이너 안의 프로그램이 실제로 3000번 포트에서 listen하고 있다면 다음 명령으로 호스트 포트와 연결할 수 있다.

```bash
docker run -p 8080:3000 my-server
```

다만 `EXPOSE`를 적어두면 이 이미지를 사용하는 사람이 "이 컨테이너는 내부적으로 3000번 포트를 쓰는구나"라고 빠르게 파악할 수 있다.

---

## 5. 예외: -P 옵션

일반적인 `-p` 사용에서는 `EXPOSE`가 없어도 포트를 직접 지정해서 publish할 수 있다.

하지만 `docker run -P` 또는 `docker run --publish-all`을 사용할 때는 `EXPOSE`가 의미를 가진다.

Docker 공식 문서에 따르면 `-P` 또는 `--publish-all` 옵션은 이미지에 설정된 exposed port 전체를 임시 호스트 포트에 자동 publish한다. [1][2]

예를 들어 Dockerfile에 다음처럼 적혀 있다고 하자.

```dockerfile
EXPOSE 3000
```

이 이미지를 다음처럼 실행하면 Docker가 호스트의 임시 포트를 하나 골라 컨테이너 내부 3000번 포트에 연결한다.

```bash
docker run -P my-server
```

따라서 정확히 정리하면 다음과 같다.

- `EXPOSE`는 그 자체로 포트를 외부에 공개하지 않는다. [1]
- 직접 포트를 연결하려면 `docker run -p HOST_PORT:CONTAINER_PORT`를 사용한다. [1][2]
- `docker run -P`를 사용할 때는 `EXPOSE`에 적힌 포트가 자동 publish 대상이 된다. [1][2]

---

## 핵심 정리

`EXPOSE`는 Dockerfile에서 컨테이너 내부 애플리케이션이 사용할 포트를 문서화하는 명령이다.

핵심은 다음과 같다.

- `EXPOSE 3000`은 컨테이너가 런타임에 3000번 포트를 사용할 예정임을 표시한다. [1]
- `EXPOSE`는 포트를 실제로 publish하지 않는다. [1]
- 실제 포트 연결은 `docker run -p HOST_PORT:CONTAINER_PORT`로 한다. [1][2]
- 프로토콜을 생략하면 기본값은 TCP이다. [1]
- `docker run -P`를 사용하면 `EXPOSE`에 적힌 포트들이 임시 호스트 포트로 자동 publish된다. [1][2]

---

## 출처

[1] Docker Docs, Dockerfile reference - EXPOSE: <https://docs.docker.com/reference/dockerfile/#expose>
[2] Docker Docs, Publishing and exposing ports: <https://docs.docker.com/get-started/docker-concepts/running-containers/publishing-ports/>
