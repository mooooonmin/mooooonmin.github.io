---
title: Dockerfile ENTRYPOINT
category: docker-kubernetes
date: 2026-05-12 00:00:00 +0900
tags: [docker, dockerfile, entrypoint, container]
---

## 1. ENTRYPOINT란?

`ENTRYPOINT`는 Dockerfile에서 **컨테이너가 시작될 때 실행할 기본 실행 파일을 지정하는 명령**이다.

Docker 공식 Dockerfile reference에 따르면 `ENTRYPOINT`는 컨테이너가 실행 파일처럼 동작하도록 설정할 때 사용한다. [1]

쉽게 말하면 컨테이너라는 작은 컴퓨터를 켰을 때, 가장 먼저 실행할 명령을 적는 곳이라고 이해하면 된다.

예를 들어 Node.js 서버를 실행하는 이미지라면 다음처럼 작성할 수 있다.

```dockerfile
ENTRYPOINT ["node", "dist/main.js"]
```

이 이미지를 컨테이너로 실행하면 `node dist/main.js`가 컨테이너의 기본 실행 명령이 된다.

---

## 2. 사용법

`ENTRYPOINT`는 크게 두 가지 형식으로 작성할 수 있다. Docker 공식 문서에서는 exec form을 선호되는 형식이라고 설명한다. [1]

```dockerfile
ENTRYPOINT ["실행파일", "인자1", "인자2"]
```

예시는 다음과 같다.

```dockerfile
ENTRYPOINT ["node", "dist/main.js"]
```

또는 shell form으로도 작성할 수 있다.

```dockerfile
ENTRYPOINT 명령어 인자1 인자2
```

예시는 다음과 같다.

```dockerfile
ENTRYPOINT echo hello
```

다만 이 글에서는 Docker 공식 문서에서 선호하는 exec form을 기준으로 설명한다. [1]

---

## 3. 예제

아래 Dockerfile을 만든다.

```dockerfile
FROM ubuntu

ENTRYPOINT ["/bin/bash", "-c", "echo hello"]
```

이미지를 빌드한다.

```bash
docker build -t my-server .
```

컨테이너를 백그라운드에서 실행한다.

```bash
docker run -d my-server
```

컨테이너 목록을 확인한다.

```bash
docker ps -a
```

로그를 확인한다.

```bash
docker logs [Container ID]
```

로그에 다음처럼 출력되면 `ENTRYPOINT`가 실행된 것이다.

```bash
hello
```

---

## 4. 왜 docker ps가 아니라 docker ps -a로 확인할까?

위 예제의 `ENTRYPOINT`는 다음 명령을 실행한다.

```bash
/bin/bash -c "echo hello"
```

`echo hello`는 `hello`를 출력한 뒤 바로 종료된다.

Docker 공식 `docker container run` 문서에 따르면 detached mode로 시작한 컨테이너는 컨테이너를 실행하는 root process가 종료되면 함께 종료된다. [2]

따라서 이 예제의 컨테이너는 실행되자마자 `hello`를 출력하고 종료된다.

그래서 실행 중인 컨테이너만 보여주는 `docker ps`에는 보이지 않을 수 있다.

종료된 컨테이너까지 확인하려면 다음처럼 `-a` 옵션을 사용한다.

```bash
docker ps -a
```

그리고 종료된 컨테이너가 출력했던 내용은 다음 명령으로 확인할 수 있다.

```bash
docker logs [Container ID]
```

---

## 5. 컨테이너를 잠시 유지하고 싶다면

ENTRYPOINT 실행 결과를 확인하기 전에 컨테이너가 바로 종료되는 것이 불편하다면, 디버깅용으로 `sleep`을 사용할 수 있다.

```dockerfile
FROM ubuntu

ENTRYPOINT ["/bin/bash", "-c", "echo hello && sleep 500"]
```

이렇게 하면 컨테이너가 시작될 때 `hello`를 출력한 뒤 500초 동안 종료되지 않는다.

```bash
docker build -t my-server .
docker run -d my-server
docker ps
docker logs [Container ID]
docker exec -it [Container ID] bash
```

다만 `sleep 500`은 학습이나 디버깅을 위한 임시 방법이다.

실제 애플리케이션 이미지에서는 컨테이너가 계속 실행해야 하는 메인 프로세스를 `ENTRYPOINT`에 지정하는 것이 일반적이다.

---

## 6. 정리

`ENTRYPOINT`는 컨테이너가 시작될 때 실행할 기본 명령을 지정한다.

핵심은 다음과 같다.

- `ENTRYPOINT ["node", "dist/main.js"]`처럼 컨테이너 시작 시 실행할 명령을 적는다.
- Docker 공식 문서는 `ENTRYPOINT ["실행파일", "인자"]` 형태의 exec form을 선호되는 형식으로 설명한다. [1]
- `ENTRYPOINT ["/bin/bash", "-c", "echo hello"]`는 컨테이너 시작 시 `hello`를 출력한다.
- `echo hello`처럼 금방 끝나는 명령을 실행하면 컨테이너도 바로 종료될 수 있다. [2]
- 종료된 컨테이너는 `docker ps -a`로 확인하고, 출력 결과는 `docker logs [Container ID]`로 확인한다.

---

## 참고자료

[1] Docker Docs, Dockerfile reference - ENTRYPOINT: <https://docs.docker.com/reference/builder/#entrypoint>  
[2] Docker Docs, docker container run - Detached mode: <https://docs.docker.com/reference/cli/docker/container/run/#detached-mode--d---detach>
