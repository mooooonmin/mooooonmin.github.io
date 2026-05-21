---
title: Docker Container Create And Start 1
category: docker-kubernetes
date: 2026-04-16 00:00:00 +0900
tags: [docker, container, create, start]
---

## 1. 컨테이너 생성

이미지를 바탕으로 컨테이너를 **생성만** 하려면 `docker create` 명령을 사용한다. [1]

```bash
docker create nginx
```

`docker create` 는 컨테이너를 만들지만, **시작(start)하지는 않는다.** [1]

즉:

- 이미지로부터 컨테이너를 생성하고 [1]
- 컨테이너 상태는 `created` 로 남아 있으며 [1]
- 이후 `docker start` 로 직접 실행할 수 있다. [1][2]

공식 문서 기준으로 `docker create` 는  
컨테이너 설정을 미리 준비해두고 나중에 시작하고 싶을 때 사용할 수 있다. [1]

따라서 초안의 "잘 사용하지 않는다"는 표현은 절대적인 사실로 보기는 어렵고,  
보통은 `docker run` 이 더 자주 쓰이지만, `create` 자체도 분명한 용도가 있다. [1][3]

---

## 2. 이미지가 로컬에 없을 때

컨테이너를 만들 때 로컬에 해당 이미지가 없으면,  
Docker는 기본적으로 이미지를 먼저 가져오려고 시도한다. [1]

공식 문서에서 `docker create` 의 `--pull` 기본값은 `missing` 으로 설명된다. [1]

즉, 이미지가 없으면 레지스트리에서 pull 한 뒤 컨테이너를 생성할 수 있다. [1]

---

## 3. 생성된 컨테이너 조회

생성된 컨테이너를 확인할 때는 `docker ps -a` 또는 `docker ps --all` 을 사용한다. [4]

```bash
docker ps -a
```

기본 `docker ps` 는 **실행 중인 컨테이너만** 보여주고, [4]  
`-a` 옵션을 주면 **중지된 컨테이너와 created 상태 컨테이너까지 포함**해서 보여준다. [4]

---

## 4. 컨테이너 실행

정지되어 있거나 created 상태인 컨테이너를 실행할 때는 `docker start` 명령을 사용한다. [2]

```bash
docker start 컨테이너명
```

또는:

```bash
docker start 컨테이너ID
```

`docker start` 는 **이미 존재하는 컨테이너를 시작**하는 명령이다. [2][3]

즉:

- `docker create` 는 생성만 수행하고 [1]
- `docker start` 는 이미 만들어진 컨테이너를 시작한다. [2]

---

## 5. 실행 중인 컨테이너 조회

실행 중인 컨테이너만 확인할 때는 `docker ps` 를 사용한다. [4]

```bash
docker ps
```

이 명령은 현재 실행 중인 컨테이너만 출력한다. [4]

---

## 6. 컨테이너 중지와 삭제

실행 중인 컨테이너를 중지하려면 `docker stop` 을 사용하고,  
삭제하려면 `docker rm` 을 사용한다. [5][6]

예:

```bash
docker ps
docker stop <container_id>
docker rm <container_id>
docker image rm nginx
```

흐름은 다음과 같이 이해하면 된다.

1. `docker ps` 로 실행 중인 컨테이너 확인 [4]
2. `docker stop` 으로 컨테이너 중지 [5]
3. `docker rm` 으로 컨테이너 삭제 [6]
4. 더 이상 필요 없으면 `docker image rm` 으로 이미지 삭제 [7]

다만 이미지 삭제는 해당 이미지를 사용하는 컨테이너가 남아 있는지에 따라 실패할 수 있다. [7]

---

## 7. create, start, run의 관계

처음 배울 때 가장 헷갈리는 부분은 `create`, `start`, `run` 의 차이다.

정리하면:

- `docker create` : 컨테이너만 생성 [1]
- `docker start` : 생성된 컨테이너 시작 [2]
- `docker run` : **create + start** 를 한 번에 수행 [3]

Docker 공식 문서도 `docker run` 이 필요 시 이미지를 pull 하고,  
새 컨테이너를 만든 뒤 시작한다고 설명한다. [3]

즉, 실무에서는 보통 `docker run` 을 더 자주 보게 되지만,  
개념을 정확히 이해하려면 `create` 와 `start` 를 나눠서 보는 것이 도움이 된다.

---

## 8. 핵심 정리

> **docker create**
>
> - 이미지를 바탕으로 컨테이너를 생성만 함 [1]
> - 자동으로 실행하지 않음 [1]
>
> **docker start**
>
> - 기존 컨테이너를 시작하는 명령 [2]
>
> **docker ps**
>
> - 실행 중인 컨테이너 조회 [4]
>
> **docker ps -a**
>
> - 모든 컨테이너 조회 [4]
>
> **docker run**
>
> - create 와 start 를 한 번에 수행 [3]

---

## 참고 자료

1. Docker Docs, `docker container create`  
   https://docs.docker.com/reference/cli/docker/container/create/
2. Docker Docs, `docker container start`  
   https://docs.docker.com/reference/cli/docker/container/start/
3. Docker Docs, `docker container run`  
   https://docs.docker.com/reference/cli/docker/container/run/
4. Docker Docs, Run containers  
   https://docs.docker.com/guides/golang/run-containers/
5. Docker Docs, `docker container stop`  
   https://docs.docker.com/reference/cli/docker/container/stop/
6. Docker Docs, `docker container rm`  
   https://docs.docker.com/reference/cli/docker/container/rm/
7. Docker Docs, `docker image rm`  
   https://docs.docker.com/reference/cli/docker/image/rm/
