---
title: Dockerfile RUN
category: docker-kubernetes
date: 2026-05-13 00:00:00 +0900
tags: [docker, dockerfile, run, image, build]
---

## 1. RUN이란?

`RUN`은 Dockerfile에서 **이미지를 빌드하는 과정 중에 명령어를 실행하는 명령**이다.

Docker 공식 Dockerfile reference에 따르면 `RUN` 명령은 현재 이미지 위에서 명령어를 실행하고, 그 결과로 새 레이어를 만든다. 이렇게 만들어진 레이어는 Dockerfile의 다음 단계에서 사용된다. [1]

즉, `RUN`은 컨테이너가 시작된 뒤에 실행되는 명령이 아니라, **이미지가 만들어지는 동안 실행되는 명령**이다.

예를 들어 Ubuntu 이미지에 `git`을 설치한 이미지를 만들고 싶다면 다음처럼 작성할 수 있다.

```dockerfile
FROM ubuntu

RUN apt update && apt install -y git
```

위 Dockerfile을 빌드하면 `git`이 설치된 새 이미지가 만들어진다.

---

## 2. 사용법

`RUN`의 기본 문법은 다음과 같다.

```dockerfile
RUN [명령문]
```

예를 들어 Node.js 프로젝트에서 의존성을 설치하려면 다음처럼 작성할 수 있다.

```dockerfile
RUN npm install
```

Docker 공식 문서에 따르면 `RUN`에는 shell form과 exec form 두 가지 형식이 있다. [1]

가장 흔히 사용하는 형식은 shell form이다.

```dockerfile
RUN apt update && apt install -y git
```

exec form은 JSON 배열 형태로 작성한다.

```dockerfile
RUN ["echo", "hello"]
```

Docker 공식 문서에 따르면 shell form은 자동으로 명령 셸을 사용하고, exec form은 자동으로 셸을 호출하지 않는다. [2]

따라서 `$HOME` 같은 셸 변수 치환이나 `&&` 같은 셸 기능이 필요하다면 shell form을 쓰거나, exec form에서 직접 셸을 실행해야 한다. [2]

```dockerfile
RUN ["sh", "-c", "echo $HOME"]
```

---

## 3. RUN vs ENTRYPOINT

`RUN`과 `ENTRYPOINT`는 둘 다 명령어를 적는 Dockerfile 명령이기 때문에 헷갈릴 수 있다.

하지만 두 명령의 실행 시점은 다르다.

`RUN`은 **이미지 빌드 중** 실행된다.

```dockerfile
RUN apt update && apt install -y git
```

위 명령은 이미지를 만들 때 실행된다. 그래서 빌드가 끝난 이미지에는 `git`이 설치된 상태가 된다.

`ENTRYPOINT`는 **컨테이너가 시작될 때** 실행할 기본 명령을 지정한다. Docker 공식 문서에서도 `ENTRYPOINT`는 컨테이너가 실행 파일처럼 동작하도록 설정할 때 사용한다고 설명한다. [3]

```dockerfile
ENTRYPOINT ["/bin/bash", "-c", "sleep 500"]
```

위 명령은 이미지를 빌드할 때 실행되는 것이 아니라, 그 이미지로 컨테이너를 시작할 때 실행된다.

정리하면 다음과 같다.

| 명령 | 실행 시점 | 주된 용도 |
| --- | --- | --- |
| `RUN` | 이미지 빌드 중 | 패키지 설치, 파일 생성, 빌드 작업 |
| `ENTRYPOINT` | 컨테이너 시작 시 | 컨테이너의 기본 실행 명령 지정 |

---

## 4. 예제: git이 설치된 Ubuntu 이미지 만들기

Ubuntu 환경에 `git`이 설치되어 있는 이미지를 만들어보자.

먼저 `Dockerfile`을 작성한다.

**Dockerfile**

```dockerfile
FROM ubuntu

RUN apt update && apt install -y git

ENTRYPOINT ["/bin/bash", "-c", "sleep 500"]
```

여기서 `RUN apt update && apt install -y git`은 이미지를 빌드하는 동안 실행된다.

그리고 `ENTRYPOINT ["/bin/bash", "-c", "sleep 500"]`은 컨테이너가 시작될 때 실행된다.

---

## 5. 이미지 빌드 및 컨테이너 실행

이미지를 빌드한다.

```bash
docker build -t my-server .
```

Docker 공식 CLI 문서에 따르면 `docker build`에서 마지막 위치 인자는 빌드 컨텍스트를 의미한다. 아래 예시의 `.`은 현재 작업 디렉터리를 빌드 컨텍스트로 사용한다는 뜻이다. [4]

컨테이너를 백그라운드에서 실행한다.

```bash
docker run -d my-server
```

실행 중인 컨테이너 목록을 확인한다.

```bash
docker ps
```

컨테이너 안으로 들어간다.

```bash
docker exec -it [Container ID] bash
```

Docker 공식 문서에 따르면 `docker exec`는 실행 중인 컨테이너에서 새 명령을 실행한다. 또한 `docker exec`로 지정한 명령은 컨테이너의 기본 프로세스가 실행 중일 때만 동작한다. [5]

컨테이너 안에서 `git`이 설치되었는지 확인한다.

```bash
git -v
```

`git version ...` 형태의 결과가 나오면 `RUN` 명령으로 이미지 빌드 중 `git`이 설치된 것이다.

---

## 6. 정리

`RUN`은 Dockerfile에서 이미지를 만드는 동안 필요한 명령어를 실행할 때 사용한다.

핵심은 다음과 같다.

- `RUN`은 이미지 빌드 중 명령어를 실행하고, 그 결과를 새 이미지 레이어로 만든다. [1]
- `RUN npm install`은 이미지를 만들 때 Node.js 의존성을 설치한다.
- `RUN apt update && apt install -y git`은 이미지를 만들 때 Ubuntu 이미지 안에 `git`을 설치한다.
- `RUN`은 이미지 빌드 시점에 실행되고, `ENTRYPOINT`는 컨테이너 시작 시점에 실행된다.
- 실행 중인 컨테이너에서 명령을 실행하려면 `docker exec`를 사용할 수 있다. [5]

---

## 참고자료

[1] Docker Docs, Dockerfile reference - RUN: <https://docs.docker.com/reference/dockerfile/#run>  
[2] Docker Docs, Dockerfile reference - Shell and exec form: <https://docs.docker.com/reference/dockerfile/#shell-and-exec-form>  
[3] Docker Docs, Dockerfile reference - ENTRYPOINT: <https://docs.docker.com/reference/dockerfile/#entrypoint>  
[4] Docker Docs, docker image build: <https://docs.docker.com/reference/cli/docker/image/build/>  
[5] Docker Docs, docker container exec: <https://docs.docker.com/reference/cli/docker/container/exec/>
