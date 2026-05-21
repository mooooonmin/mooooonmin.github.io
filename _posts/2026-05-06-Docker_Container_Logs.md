---
title: Docker Container Logs
category: docker-kubernetes
date: 2026-05-06 00:00:00 +0900
tags: [docker, container, logs, tail, follow]
---

## 1. 컨테이너 로그를 확인해야 하는 이유

컨테이너를 실행한 뒤에는 애플리케이션이 정상적으로 동작하는지, 에러가 발생하지 않았는지 확인해야 한다.
이때 가장 먼저 확인하는 정보가 로그다.

Docker 공식 문서에 따르면 `docker logs` 명령은 컨테이너의 로그를 가져오는 명령이며, `docker container logs`의 별칭(alias)이다. [1]

```bash
docker logs 컨테이너명
docker logs 컨테이너ID
```

Docker의 컨테이너 로그는 기본적으로 컨테이너 안에서 실행 중인 프로세스가 `STDOUT`과 `STDERR`로 출력한 내용을 보여준다. [2]

---

## 2. 특정 컨테이너의 모든 로그 조회

특정 컨테이너의 로그를 확인하려면 `docker logs` 뒤에 컨테이너 ID 또는 컨테이너명을 입력한다. [1]

```bash
docker logs 컨테이너명
```

예를 들어 Nginx 컨테이너를 백그라운드로 실행하고 로그를 확인하려면 다음처럼 실행할 수 있다.

```bash
docker run -d --name nginx-logs-test nginx
docker logs nginx-logs-test
```

컨테이너명을 지정하지 않고 실행했다면 먼저 컨테이너 ID를 확인한 뒤 로그를 조회한다.

```bash
docker ps
docker logs 컨테이너ID
```

---

## 3. 최근 로그 10줄만 조회

로그가 너무 많을 때는 `--tail` 옵션을 사용해 마지막 부분의 일부 로그만 확인할 수 있다.
Docker 공식 문서에서 `--tail` 또는 `-n` 옵션은 로그의 끝에서부터 표시할 줄 수를 지정하는 옵션이다. [1]

```bash
docker logs --tail 10 컨테이너명
```

또는 짧은 옵션인 `-n`을 사용할 수 있다.

```bash
docker logs -n 10 컨테이너명
```

정리하면 다음과 같다.

- `--tail 10` : 로그 끝에서부터 10줄만 조회 [1]
- `-n 10` : `--tail 10`과 같은 의미 [1]

---

## 4. 기존 로그와 새 로그를 실시간으로 함께 조회

기존 로그를 먼저 출력한 뒤, 새로 생성되는 로그까지 계속 보고 싶다면 `-f` 또는 `--follow` 옵션을 사용한다.
Docker 공식 문서에 따르면 `docker logs --follow`는 컨테이너의 `STDOUT`과 `STDERR`에서 새로 출력되는 내용을 계속 스트리밍한다. [1]

```bash
docker logs -f 컨테이너명
```

예시는 다음과 같다.

```bash
docker run -d -p 80:80 --name nginx-logs-follow nginx
docker logs -f nginx-logs-follow
```

여기서 `-f`는 `--follow`의 짧은 옵션이다. [1]

실시간 로그 조회를 종료하려면 터미널에서 `Ctrl + C`를 입력한다.

---

## 5. 기존 로그는 보지 않고 새 로그만 실시간 조회

기존에 쌓인 로그는 보지 않고, 명령 실행 이후 새로 생성되는 로그만 보고 싶다면 `--tail 0`과 `-f`를 함께 사용한다.

```bash
docker logs --tail 0 -f 컨테이너명
```

이 명령은 다음 두 옵션을 조합한 것이다.

1. `--tail 0` : 로그 끝에서 0줄만 출력 [1]
2. `-f` : 이후 새로 생성되는 로그를 계속 출력 [1]

따라서 이미 쌓인 로그는 출력하지 않고, 명령 실행 후 발생하는 로그만 실시간으로 확인할 수 있다.

---

## 6. 시간 기준으로 로그 조회

특정 시점 이후의 로그만 보고 싶다면 `--since` 옵션을 사용할 수 있다.
Docker 공식 문서에 따르면 `--since`는 지정한 시간 이후에 생성된 로그만 보여준다. [1]

```bash
docker logs --since 10m 컨테이너명
```

위 명령은 최근 10분 동안 생성된 로그를 조회한다.

특정 시점 이전의 로그만 보고 싶다면 `--until` 옵션을 사용할 수 있다.
Docker 공식 문서에서 `--until`은 지정한 시간 이전의 로그를 보여주는 옵션이다. [1]

```bash
docker logs --until 10m 컨테이너명
```

위 명령은 현재 시점 기준으로 10분 전까지의 로그를 조회한다.

`--since`와 `--until`은 RFC 3339 형식의 날짜, Unix timestamp, Go duration 형식의 상대 시간 등을 사용할 수 있다. [1]

---

## 7. 로그에 타임스탬프 함께 출력

로그가 언제 발생했는지 함께 확인하고 싶다면 `-t` 또는 `--timestamps` 옵션을 사용한다.
Docker 공식 문서에 따르면 이 옵션은 각 로그 항목에 RFC3339Nano 형식의 타임스탬프를 추가한다. [1]

```bash
docker logs -t 컨테이너명
```

실시간 조회와 함께 사용할 수도 있다.

```bash
docker logs -t -f 컨테이너명
```

---

## 8. 핵심 정리

> **기본 조회**
>
> - `docker logs 컨테이너명` : 특정 컨테이너의 로그 조회 [1]
> - `docker logs 컨테이너ID` : 특정 컨테이너 ID의 로그 조회 [1]
>
> **일부 로그 조회**
>
> - `docker logs --tail 10 컨테이너명` : 최근 로그 10줄 조회 [1]
> - `docker logs -n 10 컨테이너명` : 최근 로그 10줄 조회 [1]
>
> **실시간 조회**
>
> - `docker logs -f 컨테이너명` : 기존 로그를 출력한 뒤 새 로그를 계속 조회 [1]
> - `docker logs --tail 0 -f 컨테이너명` : 기존 로그 없이 새 로그만 실시간 조회 [1]
>
> **시간과 형식**
>
> - `docker logs --since 10m 컨테이너명` : 최근 10분 로그 조회 [1]
> - `docker logs --until 10m 컨테이너명` : 현재 기준 10분 전까지의 로그 조회 [1]
> - `docker logs -t 컨테이너명` : 로그에 타임스탬프 추가 [1]

---

## 참고 자료

1. Docker Docs, `docker container logs`  
   https://docs.docker.com/reference/cli/docker/container/logs/
2. Docker Docs, Logs and metrics  
   https://docs.docker.com/engine/logging/
