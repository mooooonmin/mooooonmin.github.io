---
title: Docker Container List Stop And Remove
category: docker-kubernetes
date: 2026-04-30 00:00:00 +0900
tags: [docker, container, ps, stop, kill, rm]
---

## 1. 실행 중인 컨테이너 조회

현재 실행 중인 컨테이너만 확인하려면 `docker ps` 명령을 사용한다. [1]

```bash
docker ps
```

`docker ps` 는 `docker container ls` 의 별칭(alias)이다. [1]

공식 문서 기준으로 기본 `docker ps` 는 **실행 중인 컨테이너만** 보여준다. [1]

---

## 2. 모든 컨테이너 조회

실행 중인 컨테이너뿐 아니라 중지된 컨테이너까지 함께 보려면 `-a` 또는 `--all` 옵션을 사용한다. [1]

```bash
docker ps -a
```

또는:

```bash
docker ps --all
```

`-a, --all` 옵션은 모든 컨테이너를 보여주며, 기본값은 실행 중인 컨테이너만 보여주는 방식이다. [1]

컨테이너 ID만 출력하고 싶다면 `-q` 또는 `--quiet` 옵션을 사용할 수 있다. [1]

```bash
docker ps -q
docker ps -aq
```

여기서 `docker ps -aq` 는 **모든 컨테이너의 ID만 출력**한다. [1]

---

## 3. 컨테이너 중지

실행 중인 컨테이너를 정상적으로 중지하려면 `docker stop` 명령을 사용한다. [2]

```bash
docker stop 컨테이너명
docker stop 컨테이너ID
```

`docker stop` 은 `docker container stop` 의 별칭(alias)이다. [2]

공식 문서 기준으로 `docker stop` 은 컨테이너 안의 메인 프로세스에 먼저 `SIGTERM` 을 보내고,
일정 시간 안에 종료되지 않으면 `SIGKILL` 을 보낸다. [2]

즉, 일반적인 종료 흐름은 다음과 같다.

1. 먼저 정상 종료 요청을 보냄 [2]
2. 정해진 대기 시간 동안 기다림 [2]
3. 그래도 종료되지 않으면 강제 종료 신호를 보냄 [2]

---

## 4. 컨테이너 강제 종료

컨테이너를 즉시 강제 종료하려면 `docker kill` 명령을 사용한다. [3]

```bash
docker kill 컨테이너명
docker kill 컨테이너ID
```

`docker kill` 은 `docker container kill` 의 별칭(alias)이다. [3]

공식 문서 기준으로 `docker kill` 은 기본적으로 컨테이너의 메인 프로세스에 `SIGKILL` 신호를 보낸다. [3]

따라서 개념적으로는 다음처럼 구분할 수 있다.

- `docker stop` : 먼저 정상 종료를 시도한 뒤, 필요하면 강제 종료 [2]
- `docker kill` : 기본적으로 강제 종료 신호를 보냄 [3]

실무에서는 특별한 이유가 없다면 먼저 `docker stop` 을 사용하고,
정상적으로 종료되지 않을 때 `docker kill` 을 고려하는 편이 안전하다.

---

## 5. 중지된 특정 컨테이너 삭제

컨테이너를 삭제하려면 `docker rm` 명령을 사용한다. [4]

```bash
docker rm 컨테이너명
docker rm 컨테이너ID
```

`docker rm` 은 `docker container rm` 의 별칭(alias)이다. [4]

일반적인 흐름은 다음과 같다.

```bash
docker stop 컨테이너명
docker rm 컨테이너명
```

공식 문서에서 `docker container rm` 은 하나 이상의 컨테이너를 제거하는 명령으로 설명된다. [4]

---

## 6. 실행 중인 특정 컨테이너 삭제

실행 중인 컨테이너를 삭제하려면 `-f` 또는 `--force` 옵션을 사용할 수 있다. [4]

```bash
docker rm -f 컨테이너명
docker rm -f 컨테이너ID
```

공식 문서 기준으로 `-f, --force` 옵션은 실행 중인 컨테이너를 강제로 제거하며, 이때 `SIGKILL` 을 사용한다. [4]

다만 강제 삭제는 컨테이너 안에서 처리 중이던 작업을 정상적으로 마무리할 기회를 줄이지 않을 수 있다.
따라서 보통은 먼저 `docker stop` 으로 중지한 뒤 `docker rm` 으로 삭제하는 흐름이 더 안전하다. [2][4]

---

## 7. 중지된 모든 컨테이너 삭제

중지된 컨테이너를 한 번에 정리할 때는 공식 문서에서 `docker container prune` 을 사용할 수 있다고 안내한다. [4]

```bash
docker container prune
```

또는 셸 명령 조합을 사용해 중지된 컨테이너 ID만 골라 삭제할 수도 있다. [4]

```bash
docker rm $(docker ps --filter status=exited -q)
```

여기서 주의할 점은 다음 명령이다.

```bash
docker rm $(docker ps -qa)
```

`docker ps -qa` 는 **중지된 컨테이너만** 조회하는 명령이 아니라,
`-a` 로 모든 컨테이너를 조회하고 `-q` 로 ID만 출력하는 명령이다. [1]

따라서 위 조합은 모든 컨테이너 ID를 `docker rm` 에 넘긴다.
다만 `-f` 옵션이 없으면 실행 중인 컨테이너 삭제는 실패할 수 있다. [4]

또한 `$(...)` 문법은 Docker 명령 자체가 아니라 셸 기능이다.
공식 문서도 이런 조합 방식은 셸에 의존하므로 환경에 따라 문법이 달라질 수 있다고 설명한다. [4]

---

## 8. 모든 컨테이너 강제 삭제

모든 컨테이너 ID를 조회한 뒤 강제로 삭제하려면 다음처럼 실행할 수 있다.

```bash
docker rm -f $(docker ps -qa)
```

이 명령은 다음 두 동작을 조합한 것이다.

1. `docker ps -qa` 로 모든 컨테이너 ID 출력 [1]
2. `docker rm -f` 로 해당 컨테이너들을 강제 삭제 [4]

강제 삭제에는 `SIGKILL` 이 사용될 수 있으므로,
필요한 컨테이너가 포함되어 있지 않은지 먼저 `docker ps -a` 로 확인하는 것이 안전하다. [1][4]

---

## 핵심 정리

> **조회**
>
> - `docker ps` : 실행 중인 컨테이너 조회 [1]
> - `docker ps -a` : 모든 컨테이너 조회 [1]
> - `docker ps -q` : 컨테이너 ID만 조회 [1]
>
> **중지**
>
> - `docker stop 컨테이너명` : 정상 종료 시도 후 필요 시 강제 종료 [2]
> - `docker kill 컨테이너명` : 기본적으로 `SIGKILL` 전송 [3]
>
> **삭제**
>
> - `docker rm 컨테이너명` : 컨테이너 삭제 [4]
> - `docker rm -f 컨테이너명` : 실행 중인 컨테이너 강제 삭제 [4]
> - `docker container prune` : 중지된 컨테이너 정리 [4]

---

## 출처

1. Docker Docs, `docker container ls`
   https://docs.docker.com/reference/cli/docker/container/ls/
2. Docker Docs, `docker container stop`
   https://docs.docker.com/reference/cli/docker/container/stop/
3. Docker Docs, `docker container kill`
   https://docs.docker.com/reference/cli/docker/container/kill/
4. Docker Docs, `docker container rm`
   https://docs.docker.com/reference/cli/docker/container/rm/
