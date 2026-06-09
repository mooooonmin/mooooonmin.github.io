---
title: Dockerfile WORKDIR
category: d
date: 2026-05-13 00:00:10 +0900
tags: [docker, dockerfile, workdir, directory, build]
---

## 1. WORKDIR이란?

`WORKDIR`은 Dockerfile에서 **작업 디렉터리를 지정하는 명령**이다.

Docker 공식 Dockerfile reference에 따르면 `WORKDIR`은 그 뒤에 등장하는 `RUN`, `CMD`, `ENTRYPOINT`, `COPY`, `ADD` 명령의 작업 디렉터리를 설정한다. 또한 지정한 `WORKDIR`이 존재하지 않으면, 이후 명령에서 사용하지 않더라도 자동으로 생성된다. [1]

쉽게 말하면 `WORKDIR`은 Dockerfile 안에서 `cd`를 해두는 것과 비슷하게 이해할 수 있다.

```dockerfile
WORKDIR /usr/src/app
```

위처럼 작성하면 이후 명령들은 `/usr/src/app` 디렉터리를 기준으로 실행된다.

---

## 2. WORKDIR을 사용하는 이유

컨테이너도 하나의 작은 컴퓨터 환경처럼 생각할 수 있다.

이미지 안에는 운영체제 기본 파일과 디렉터리가 이미 들어 있다. 여기에 애플리케이션 파일을 아무 위치에나 복사하면, 기존 파일들과 섞여서 관리하기 어려워질 수 있다.

그래서 보통 애플리케이션 파일은 `/app`, `/usr/src/app`, `/my-dir` 같은 특정 디렉터리에 모아둔다.

예를 들어 다음처럼 작업 디렉터리를 지정할 수 있다.

```dockerfile
WORKDIR /my-dir
```

이후 `COPY ./ ./`를 실행하면 파일들이 컨테이너의 루트 디렉터리 `/`가 아니라 `/my-dir` 아래에 복사된다. Docker 공식 문서에 따르면 `COPY`의 대상 경로가 `/`로 시작하지 않는 상대 경로라면, 빌드 컨테이너의 현재 작업 디렉터리를 기준으로 해석된다. [2]

---

## 3. 사용법

`WORKDIR`의 기본 문법은 다음과 같다.

```dockerfile
WORKDIR [작업 디렉터리로 사용할 경로]
```

예시는 다음과 같다.

```dockerfile
WORKDIR /usr/src/app
```

작업 디렉터리는 절대 경로로 지정하는 것이 이해하기 쉽다.

Docker 공식 문서에 따르면 `WORKDIR`은 여러 번 사용할 수도 있다. 상대 경로를 사용하면 이전 `WORKDIR`을 기준으로 이어진다. [1]

```dockerfile
WORKDIR /a
WORKDIR b
WORKDIR c
RUN pwd
```

위 예제에서 마지막 `pwd` 결과는 `/a/b/c`가 된다. [1]

따라서 처음 배우는 단계에서는 다음처럼 절대 경로를 사용하는 편이 실수를 줄이기 쉽다.

```dockerfile
WORKDIR /my-dir
```

---

## 4. 예제 준비

`WORKDIR`을 쓰지 않았을 때와 썼을 때 파일 위치가 어떻게 달라지는지 비교해보자.

먼저 작업 디렉터리에 예제 파일과 폴더를 만든다.

```bash
echo "hello" > app.txt
mkdir src
echo "{}" > config.json
```

현재 폴더에는 다음 파일과 디렉터리가 있다고 가정한다.

```bash
app.txt
config.json
src/
Dockerfile
```

---

## 5. WORKDIR을 쓰지 않은 경우

먼저 `WORKDIR`을 쓰지 않고 파일을 복사해보자.

**Dockerfile**

```dockerfile
FROM ubuntu

COPY ./ ./

ENTRYPOINT ["/bin/bash", "-c", "sleep 500"]
```

이미지를 빌드한다.

```bash
docker build -t my-server .
```

컨테이너를 백그라운드에서 실행한다.

```bash
docker run -d my-server
```

컨테이너 안으로 들어간다.

```bash
docker exec -it [Container ID] bash
```

파일 목록을 확인한다.

```bash
ls
```

이 경우 `COPY ./ ./`의 대상 경로 `./`는 현재 작업 디렉터리를 기준으로 한다.

`WORKDIR`을 따로 지정하지 않으면 Docker 공식 문서 기준 기본 작업 디렉터리는 `/`이다. 다만 `FROM scratch`가 아닌 베이스 이미지를 사용할 때는 베이스 이미지가 이미 `WORKDIR`을 설정했을 수 있다. 그래서 의도하지 않은 위치에서 명령이 실행되는 것을 피하려면 `WORKDIR`을 명시하는 것이 좋다고 Docker 공식 문서는 설명한다. [1]

이 예제의 `ubuntu` 이미지에서는 별도 `WORKDIR`을 지정하지 않았으므로 파일이 루트 디렉터리 기준으로 복사된 것처럼 보일 수 있다.

---

## 6. WORKDIR을 쓴 경우

이번에는 `WORKDIR`을 사용해 파일을 `/my-dir` 아래에 모아보자.

**Dockerfile**

```dockerfile
FROM ubuntu

WORKDIR /my-dir

COPY ./ ./

ENTRYPOINT ["/bin/bash", "-c", "sleep 500"]
```

이미지를 다시 빌드한다.

```bash
docker build -t my-server .
```

컨테이너를 실행한다.

```bash
docker run -d my-server
```

컨테이너 안으로 들어간다.

```bash
docker exec -it [Container ID] bash
```

현재 위치를 확인한다.

```bash
pwd
```

`/my-dir`이 출력된다.

파일 목록을 확인한다.

```bash
ls
```

`app.txt`, `config.json`, `src`가 `/my-dir` 안에 모여 있는 것을 확인할 수 있다.

이렇게 되는 이유는 `WORKDIR /my-dir` 이후에 등장한 `COPY ./ ./`의 대상 경로 `./`가 `/my-dir`을 기준으로 해석되기 때문이다. [1][2]

---

## 정리

`WORKDIR`은 Dockerfile에서 이후 명령들이 실행될 작업 디렉터리를 지정한다.

핵심은 다음과 같다.

- `WORKDIR /my-dir`은 작업 디렉터리를 `/my-dir`로 설정한다.
- 지정한 디렉터리가 없으면 Docker가 자동으로 생성한다. [1]
- `WORKDIR` 이후의 `RUN`, `CMD`, `ENTRYPOINT`, `COPY`, `ADD`는 해당 작업 디렉터리를 기준으로 동작한다. [1]
- `COPY ./ ./`처럼 상대 경로를 쓰면 현재 작업 디렉터리를 기준으로 파일이 복사된다. [2]
- 의도하지 않은 위치에서 명령이 실행되는 것을 피하려면 `WORKDIR`을 명시하는 것이 좋다. [1]

---

## 출처

[1] Docker Docs, Dockerfile reference - WORKDIR: <https://docs.docker.com/reference/dockerfile/#workdir>
[2] Docker Docs, Dockerfile reference - COPY destination: <https://docs.docker.com/reference/dockerfile/#destination>
