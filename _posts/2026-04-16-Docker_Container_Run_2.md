---
title: Docker Container Run 2
category: docker-kubernetes
date: 2026-04-16 00:00:00 +0900
tags: [docker, container, run, port]
---

## 1. 컨테이너 생성과 실행을 한 번에

이미지를 바탕으로 **새 컨테이너를 만들고 바로 실행**하려면 `docker run` 명령을 사용한다. [1]

```bash
# docker run 이미지명[:태그명]
docker run nginx
```

`docker run` 은 내부적으로 **컨테이너 생성(create) 후 시작(start)** 까지 수행한다. [1][6][7]

즉:

- `docker create` 는 생성만 하고 [6]
- `docker start` 는 기존 컨테이너를 시작하며 [7]
- `docker run` 은 새 컨테이너를 만들어 바로 실행한다. [1]

---

## 2. 로컬에 이미지가 없을 때

`docker run` 의 기본 pull 정책은 `missing` 이다. [1]

따라서 로컬에 해당 이미지가 없으면, Docker는 이미지를 먼저 pull 한 뒤 컨테이너를 실행할 수 있다. [1]

반대로 로컬에 이미지가 이미 있으면 그 캐시된 이미지를 사용할 수 있다. [1]

즉, **항상 최신 이미지를 새로 받고 싶다면** 다음 중 하나를 사용하면 된다.

- `docker pull nginx` [5]
- `docker run --pull always nginx` [1]

초안의 "새롭게 갱신된 이미지를 받고 싶다면 `docker pull` 을 사용한다"는 설명은 대체로 맞지만,
공식 문서 기준으로는 `docker run --pull always` 도 가능한 방법이다. [1]

---

## 3. 백그라운드에서 실행

컨테이너를 **백그라운드 프로세스**로 실행하려면 `-d` 또는 `--detach` 옵션을 사용한다. [1]

```bash
docker run -d nginx
```

공식 문서는 `-d` 가 **터미널 창을 점유하지 않는(background) 방식**으로 컨테이너를 시작한다고 설명한다. [1]

다만 detached 모드에서도 **컨테이너의 루트 프로세스가 종료되면 컨테이너도 종료**된다. [1]

---

## 4. 컨테이너에 이름 붙이기

컨테이너 이름을 직접 지정하려면 `--name` 옵션을 사용한다. [1]

```bash
docker run -d --name my-web-server nginx
```

`--name` 은 컨테이너에 **사용자가 기억하기 쉬운 식별자**를 부여하는 옵션이다. [1]

이후에는 컨테이너 ID 대신 이름으로도 제어할 수 있다. [1]

예:

```bash
docker stop my-web-server
docker rm my-web-server
```

---

## 5. 호스트 포트와 컨테이너 포트 연결

호스트 포트를 컨테이너 포트에 연결하려면 `-p` 또는 `--publish` 옵션을 사용한다. [1]

```bash
docker run -d -p 4000:80 nginx
```

위 명령은 **호스트의 4000번 포트**를 **컨테이너의 80번 포트**에 바인딩한다. [1]

즉, 호스트 측 4000번 포트로 들어온 요청을 컨테이너의 80번 포트로 전달하도록 설정하는 것이다. [1]

공식 문서 기준으로 IP 주소를 따로 지정하지 않으면, Docker는 포트를 기본적으로 **모든 인터페이스(`0.0.0.0`)** 에 공개한다. [1]

---

## 6. 실행 중인 컨테이너 확인

실행 중인 컨테이너만 보려면 `docker ps` 를 사용한다. [2]

```bash
docker ps
```

모든 컨테이너를 보려면 `docker ps -a` 를 사용한다. [2]

```bash
docker ps -a
```

공식 문서 기준으로 기본 `docker ps` 는 **실행 중인 컨테이너만** 표시하고,
`-a` 를 사용하면 **중지된 컨테이너까지 포함**해서 확인할 수 있다. [2]

---

## 7. 컨테이너 중지와 삭제

실행 중인 컨테이너를 중지할 때는 `docker stop` 을 사용하고,
컨테이너를 삭제할 때는 `docker rm` 을 사용한다. [3][4]

예:

```bash
docker ps
docker stop my-web-server
docker rm my-web-server
docker image rm nginx
```

흐름을 정리하면 다음과 같다.

1. `docker ps` 로 실행 중인 컨테이너 확인 [2]
2. `docker stop` 으로 컨테이너 중지 [3]
3. `docker rm` 으로 컨테이너 삭제 [4]
4. 필요 없으면 `docker image rm` 으로 이미지 삭제 [5]

다만 이미지를 삭제할 때는 해당 이미지를 사용하는 컨테이너가 남아 있으면 실패할 수 있다. [5]

---

## 8. 한 번에 조합해서 실행하기

실무에서는 옵션을 함께 조합해서 쓰는 경우가 많다.

```bash
docker run -d --name my-web-server -p 4000:80 nginx
```

이 명령은 한 번에 다음을 수행한다.

- 새 컨테이너 생성 및 실행 [1]
- 백그라운드 실행 [1]
- 컨테이너 이름 지정 [1]
- 호스트 포트와 컨테이너 포트 연결 [1]

---

## 핵심 정리

> **docker run**
>
> - 새 컨테이너를 생성하고 바로 실행 [1]
>
> **-d**
>
> - 컨테이너를 백그라운드에서 실행 [1]
>
> **--name**
>
> - 컨테이너 이름 지정 [1]
>
> **-p**
>
> - 호스트 포트와 컨테이너 포트 연결 [1]
>
> **조회**
>
> - `docker ps` : 실행 중인 컨테이너 조회 [2]
> - `docker ps -a` : 전체 컨테이너 조회 [2]

---

## 출처

1. Docker Docs, `docker container run`
   https://docs.docker.com/reference/cli/docker/container/run/
2. Docker Docs, `docker container ls`
   https://docs.docker.com/reference/cli/docker/container/ls/
3. Docker Docs, `docker container stop`
   https://docs.docker.com/reference/cli/docker/container/stop/
4. Docker Docs, `docker container rm`
   https://docs.docker.com/reference/cli/docker/container/rm/
5. Docker Docs, `docker image rm`
   https://docs.docker.com/reference/cli/docker/image/rm/
6. Docker Docs, `docker container create`
   https://docs.docker.com/reference/cli/docker/container/create/
7. Docker Docs, `docker container start`
   https://docs.docker.com/reference/cli/docker/container/start/
