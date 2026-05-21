---
title: Dockerfile COPY
category: docker-kubernetes
date: 2026-05-12 00:00:00 +0900
tags: [docker, dockerfile, copy, dockerignore, build-context]
---

## 1. COPY란?

`COPY`는 Dockerfile에서 **빌드 컨텍스트에 있는 파일이나 디렉터리를 이미지 파일 시스템으로 복사하는 명령**이다. Docker 공식 Dockerfile reference에 따르면 `COPY`는 `<src>`의 새 파일 또는 디렉터리를 이미지의 `<dest>` 경로에 추가한다. [1]

여기서 중요한 점은 `COPY`가 파일을 **이동**하는 명령이 아니라는 것이다.

호스트 컴퓨터의 원본 파일은 그대로 남아 있고, Docker 이미지를 만들 때 그 파일이 이미지 안으로 복사된다.

---

## 2. 사용법

`COPY`의 기본 문법은 다음과 같다. [1]

```dockerfile
COPY [호스트 컴퓨터에 있는 복사할 파일의 경로] [컨테이너에서 파일이 위치할 경로]
```

예를 들어 현재 디렉터리에 있는 `app.txt`를 이미지 안의 `/app.txt`로 복사하려면 다음처럼 작성한다.

```dockerfile
COPY app.txt /app.txt
```

`docker build -t my-server .`에서 마지막의 `.`은 현재 디렉터리를 빌드 컨텍스트로 사용한다는 의미이다. Docker 공식 문서에 따르면 빌드 컨텍스트는 빌드가 접근할 수 있는 파일들의 집합이고, `COPY` 같은 Dockerfile 명령은 이 컨텍스트 안의 파일을 참조할 수 있다. [2]

따라서 위 예시에서 `app.txt`는 `docker build`를 실행하는 현재 디렉터리 안에 있어야 한다.

---

## 3. 파일 하나 복사해보기

먼저 작업 디렉터리에 `app.txt` 파일을 만든다.

```bash
echo "hello docker" > app.txt
```

그 다음 같은 위치에 `Dockerfile`을 만든다.

```dockerfile
FROM ubuntu

COPY app.txt /app.txt

ENTRYPOINT ["/bin/bash", "-c", "sleep 500"]
```

이미지를 빌드하고 컨테이너를 실행한다.

```bash
docker build -t my-server .
docker run -d my-server
docker ps
```

실행 중인 컨테이너에 들어가서 파일을 확인한다.

```bash
docker exec -it [Container ID] bash
ls /
cat /app.txt
```

`/app.txt`가 보이면 `COPY app.txt /app.txt`가 정상적으로 동작한 것이다.

---

## 4. 폴더 안에 있는 파일들 복사하기

이번에는 `my-app` 디렉터리를 만들고, 그 안에 파일을 넣는다.

```bash
mkdir my-app
echo "hello app" > my-app/app.txt
echo "hello readme" > my-app/readme.txt
```

`Dockerfile`은 다음처럼 작성한다.

```dockerfile
FROM ubuntu

COPY my-app /my-app/

ENTRYPOINT ["/bin/bash", "-c", "sleep 500"]
```

이미지를 빌드하고 컨테이너를 실행한다.

```bash
docker build -t my-server .
docker run -d my-server
docker ps
docker exec -it [Container ID] bash
```

컨테이너 안에서 `/my-app` 디렉터리를 확인한다.

```bash
ls /my-app
cat /my-app/app.txt
cat /my-app/readme.txt
```

Docker 공식 문서에 따르면 `COPY`의 소스가 디렉터리인 경우, 해당 디렉터리의 내용이 대상 경로로 복사된다. 하위 디렉터리가 있으면 하위 디렉터리도 함께 복사된다. [1]

---

## 5. 와일드카드 사용해보기

`COPY`의 소스 경로에는 와일드카드를 사용할 수 있다. Docker 공식 문서에 따르면 로컬 파일을 복사할 때 `<src>`는 Go의 `filepath.Match` 규칙에 따라 와일드카드 매칭을 지원한다. [1]

예를 들어 `app.txt`, `readme.txt` 파일을 만든다.

```bash
echo "app" > app.txt
echo "readme" > readme.txt
```

`Dockerfile`은 다음처럼 작성한다.

```dockerfile
FROM ubuntu

COPY *.txt /text-files/

ENTRYPOINT ["/bin/bash", "-c", "sleep 500"]
```

이미지를 빌드하고 컨테이너를 실행한다.

```bash
docker build -t my-server .
docker run -d my-server
docker ps
docker exec -it [Container ID] bash
```

컨테이너 안에서 `/text-files` 디렉터리를 확인한다.

```bash
ls /text-files
```

`app.txt`와 `readme.txt`가 보이면 `COPY *.txt /text-files/`가 정상적으로 동작한 것이다.

주의할 점은 `COPY *.txt /text-files/`처럼 대상 경로 끝에 `/`를 붙이는 것이다.

Docker 공식 문서에 따르면 여러 소스 파일을 지정하거나 와일드카드를 사용해 여러 파일이 매칭되는 경우, 대상 경로는 디렉터리여야 하며 `/`로 끝나야 한다. [1]

또한 대상 경로의 마지막 `/`는 의미가 있다. 예를 들어 `COPY test.txt /abs`는 `/abs`라는 파일을 만들고, `COPY test.txt /abs/`는 `/abs/test.txt`를 만든다. [1]

---

## 6. .dockerignore 사용해보기

특정 파일이나 폴더를 이미지에 복사하고 싶지 않을 때는 `.dockerignore`를 사용할 수 있다.

Docker 공식 문서에 따르면 `.dockerignore` 파일은 빌드 컨텍스트에서 제외할 파일이나 디렉터리를 지정할 때 사용한다. 빌드 클라이언트는 컨텍스트의 루트 디렉터리에서 `.dockerignore` 파일을 찾고, 패턴과 일치하는 파일을 빌더로 보내기 전에 컨텍스트에서 제거한다. [2]

예를 들어 다음 파일들을 준비한다.

```bash
echo "app" > app.txt
echo "readme" > readme.txt
```

`.dockerignore` 파일을 만든다.

```bash
readme.txt
```

`Dockerfile`은 다음처럼 작성한다.

```dockerfile
FROM ubuntu

COPY ./ /

ENTRYPOINT ["/bin/bash", "-c", "sleep 500"]
```

이미지를 빌드하고 컨테이너를 실행한다.

```bash
docker build -t my-server .
docker run -d my-server
docker ps
docker exec -it [Container ID] bash
```

컨테이너 안에서 파일을 확인한다.

```bash
ls /
```

`.dockerignore`에 `readme.txt`를 적었기 때문에 `COPY ./ /`를 사용해도 `readme.txt`는 빌드 컨텍스트에서 제외된다. 따라서 이미지 안으로 복사되지 않는다. [2]

---

## 핵심 정리

`COPY`는 호스트 컴퓨터의 파일을 직접 실행 중인 컨테이너에 보내는 명령이 아니라, Docker 이미지를 빌드하는 과정에서 빌드 컨텍스트의 파일을 이미지 안으로 복사하는 Dockerfile 명령이다. [1][2]

자주 기억해야 할 내용은 다음과 같다.

- `COPY app.txt /app.txt`는 `app.txt`를 이미지 안의 `/app.txt`로 복사한다.
- `COPY my-app /my-app/`는 `my-app` 디렉터리의 내용을 이미지 안의 `/my-app/` 경로에 복사한다.
- `COPY *.txt /text-files/`처럼 와일드카드를 사용할 수 있다.
- 여러 파일이 복사될 수 있는 경우 대상 경로는 `/`로 끝나는 디렉터리여야 한다.
- `.dockerignore`를 사용하면 빌드 컨텍스트에서 특정 파일이나 폴더를 제외할 수 있다.

---

## 참고자료

[1] Docker Docs, Dockerfile reference - COPY: <https://docs.docker.com/reference/builder/#copy>  
[2] Docker Docs, Build context - .dockerignore files: <https://docs.docker.com/build/building/context/#dockerignore-files>
