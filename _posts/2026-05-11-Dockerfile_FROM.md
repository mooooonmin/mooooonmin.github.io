---
title: Dockerfile FROM
category: docker-kubernetes
date: 2026-05-11 00:00:00 +0900
tags: [docker, dockerfile, from, image]
---

## 1. FROM이란?

`FROM`은 Dockerfile에서 **기반 이미지(base image)를 지정하는 명령**이다.

Docker 공식 Dockerfile reference에 따르면 `FROM` 명령은 새 빌드 단계를 만들고, 그 빌드 단계에서 사용할 기반 이미지를 지정한다. [1]

즉, Docker 이미지를 만들 때 아무것도 없는 상태에서 시작하는 것이 아니라, 특정 이미지를 출발점으로 삼고 그 위에 필요한 설정이나 파일을 추가할 수 있다.

여기서 출발점이 되는 이미지가 **베이스 이미지**이다.

---

## 2. 쉽게 이해하기

새 Windows 컴퓨터를 처음 켜면 인터넷 브라우저, 메모장, 그림판 같은 기본 프로그램이 이미 설치되어 있다.

Docker의 베이스 이미지도 이와 비슷하게 생각할 수 있다.

컨테이너로 작은 컴퓨터 환경을 만든다고 했을 때, 처음부터 어떤 프로그램과 실행 환경이 들어 있으면 좋을지 선택하는 것이다.

예를 들어 다음처럼 선택할 수 있다.

- Java 애플리케이션을 실행하고 싶다면 JDK가 포함된 이미지를 기반으로 사용할 수 있다.
- Node.js 애플리케이션을 실행하고 싶다면 Node.js가 포함된 이미지를 기반으로 사용할 수 있다.
- 웹 서버를 실행하고 싶다면 Nginx 이미지 같은 웹 서버 이미지를 기반으로 사용할 수 있다.

Docker 공식 문서에서도 Docker 이미지는 애플리케이션 실행에 필요한 파일, 바이너리, 라이브러리, 설정을 포함하는 패키지라고 설명한다. [2]

따라서 `FROM`은 **내 이미지가 어떤 실행 환경에서 출발할지 정하는 명령**이라고 이해하면 된다.

---

## 3. 사용법

`FROM`의 기본 문법은 다음과 같다.

```dockerfile
FROM 이미지명
FROM 이미지명:태그명
```

예를 들어 `nginx` 이미지를 기반으로 사용하려면 다음처럼 작성한다.

```dockerfile
FROM nginx
```

특정 버전을 지정하고 싶다면 태그를 함께 적는다.

```dockerfile
FROM nginx:1.27
```

Docker 공식 문서 기준으로 이미지 이름 뒤에 태그를 붙이지 않으면 기본적으로 `latest` 태그가 사용된다. [3]

즉, 아래 두 문장은 같은 의미로 볼 수 있다.

```dockerfile
FROM nginx
FROM nginx:latest
```

다만 `latest`는 항상 최신 버전을 고정해서 보장한다는 뜻이 아니라, 이미지 저장소에서 `latest`라는 태그가 붙은 이미지를 의미한다. Docker 공식 문서도 태그를 생략하면 Docker가 `latest` 태그를 사용한다고 설명한다. [3]

---

## 4. 예시

아래 Dockerfile은 Nginx 이미지를 기반으로 사용한다.

```dockerfile
FROM nginx

COPY index.html /usr/share/nginx/html/index.html
```

각 줄의 의미는 다음과 같다.

- `FROM nginx`: `nginx` 이미지를 기반 이미지로 사용한다.
- `COPY index.html /usr/share/nginx/html/index.html`: 현재 디렉터리의 `index.html` 파일을 이미지 안의 Nginx 기본 HTML 경로로 복사한다.

이 Dockerfile로 이미지를 빌드하면, 기본 Nginx 실행 환경 위에 내가 만든 `index.html` 파일이 추가된 새 이미지를 만들 수 있다.

---

## 5. FROM은 보통 Dockerfile의 첫 명령이다

Dockerfile에서 `FROM`은 보통 가장 먼저 작성한다.

그 이유는 이후에 실행되는 `COPY`, `RUN`, `CMD` 같은 명령들이 `FROM`으로 지정한 기반 이미지 위에서 동작하기 때문이다.

예를 들어 다음 Dockerfile에서는 `node:22` 이미지가 먼저 선택되고, 그 위에서 작업 디렉터리 설정과 파일 복사가 이어진다.

```dockerfile
FROM node:22

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
CMD ["npm", "start"]
```

이 경우 `node:22` 이미지에 포함된 Node.js 실행 환경을 기반으로 애플리케이션 이미지를 만드는 흐름이다.

---

## 핵심 정리

`FROM`은 Dockerfile에서 기반 이미지를 지정하는 명령이다.

정리하면 다음과 같다.

```text
FROM으로 기반 이미지 선택
        ↓
COPY, RUN 등으로 필요한 파일과 설정 추가
        ↓
새 Docker 이미지 생성
```

즉, **FROM은 Docker 이미지가 어떤 환경에서 시작할지 결정하는 출발점**이다.

---

## 참고 자료

[1] Docker Docs, "Dockerfile reference - FROM", https://docs.docker.com/reference/builder/#from  
[2] Docker Docs, "What is an image?", https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/  
[3] Docker Docs, "docker image tag", https://docs.docker.com/reference/cli/docker/image/tag/
