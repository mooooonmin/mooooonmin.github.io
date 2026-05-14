---
title: Dockerfile
category: 3
date: 2026-05-08 00:00:00 +0900
tags: [docker, dockerfile, image, build]
---

## 1. Docker 이미지는 어디에서 오는가?

Docker 이미지는 Docker Hub 같은 컨테이너 레지스트리에서 내려받아 사용할 수 있다.
Docker 공식 문서에 따르면 Docker Hub는 Docker 이미지를 저장하고, 관리하고, 공유하기 위한 컨테이너 레지스트리이며, 미리 만들어진 이미지와 자산을 제공한다. [4]

예를 들어 `nginx`, `mysql`, `redis` 같은 이미지는 Docker Hub에서 내려받아 바로 컨테이너로 실행할 수 있다.

```bash
docker pull nginx
docker run nginx
```

그렇다면 이런 Docker 이미지는 어떻게 만들어지는 걸까?

Docker 이미지는 보통 **Dockerfile**을 기반으로 만든다. Docker 공식 문서에서도 이미지를 만들 때 가장 흔히 사용하는 방식은 Dockerfile을 사용하는 것이라고 설명한다. [3]

---

## 2. Dockerfile이란?

**Dockerfile**은 Docker 이미지를 만들기 위한 명령들이 들어 있는 텍스트 파일이다.

Docker 공식 문서에 따르면 Dockerfile은 컨테이너 이미지를 만들기 위해 사용하는 텍스트 기반 문서이며, 이미지 빌더에게 실행할 명령, 복사할 파일, 시작 명령 등을 알려준다. [1]

즉, Dockerfile은 다음과 같은 내용을 적어두는 파일이다.

- 어떤 이미지를 기반으로 시작할 것인지
- 어떤 파일을 이미지 안으로 복사할 것인지
- 어떤 명령어를 실행해서 프로그램을 설치하거나 설정할 것인지
- 컨테이너가 시작될 때 어떤 명령을 실행할 것인지

정리하면, **Dockerfile은 Docker 이미지를 만들게 해주는 설계도 같은 파일**이다.

---

## 3. 왜 Dockerfile이 필요한가?

Docker Hub에 이미 올라와 있는 이미지만 사용할 수도 있다.
하지만 항상 남이 만든 이미지만 사용하는 것은 아니다.

예를 들어 내가 만든 Spring Boot 프로젝트가 있다고 해보자.
이 프로젝트를 다른 컴퓨터나 서버에서도 같은 방식으로 실행하고 싶다면, 애플리케이션 코드와 실행 환경을 하나의 Docker 이미지로 만들 수 있다.

이때 Dockerfile을 작성하면 다음과 같은 흐름으로 나만의 이미지를 만들 수 있다.

1. Dockerfile에 이미지 생성 과정을 작성한다.
2. `docker build` 명령으로 Docker 이미지를 만든다.
3. 만들어진 이미지를 `docker run` 명령으로 컨테이너로 실행한다.
4. 필요하다면 이미지를 Docker Hub 같은 레지스트리에 올려 다른 곳에서도 사용할 수 있게 한다.

Docker 공식 문서도 이미지를 빌드하고, 태그를 붙이고, 레지스트리에 게시하는 과정을 설명하면서 Dockerfile을 기반으로 이미지를 만든다고 설명한다. [3]

---

## 4. Dockerfile의 기본 예시

아주 단순한 Dockerfile은 다음처럼 작성할 수 있다.

```dockerfile
FROM nginx
COPY index.html /usr/share/nginx/html/index.html
```

위 Dockerfile은 다음 의미를 가진다.

- `FROM nginx`: `nginx` 이미지를 기반 이미지로 사용한다.
- `COPY index.html /usr/share/nginx/html/index.html`: 현재 디렉터리의 `index.html` 파일을 이미지 안의 Nginx 기본 웹 페이지 경로로 복사한다.

Docker 공식 Dockerfile reference에 따르면 `FROM`은 새 빌드 단계를 만들고 기반 이미지를 지정하는 명령이며, `COPY`는 파일과 디렉터리를 복사하는 명령이다. [2]

---

## 5. Dockerfile로 이미지 만들기

Dockerfile이 있는 디렉터리에서 다음 명령을 실행하면 이미지를 만들 수 있다.

```bash
docker build -t my-nginx:latest .
```

여기서 각 부분의 의미는 다음과 같다.

- `docker build`: Docker 이미지를 빌드하는 명령
- `-t my-nginx:latest`: 이미지 이름과 태그 지정
- `.`: 현재 디렉터리를 빌드 컨텍스트로 사용

Docker 공식 문서에 따르면 `docker build -t test:latest .` 형식에서 `-t` 옵션은 이미지 이름과 태그를 지정하고, 마지막의 점(`.`)은 현재 디렉터리를 빌드 컨텍스트로 설정한다. [1]

이미지가 만들어졌는지 확인하려면 다음 명령을 사용한다.

```bash
docker images
```

만든 이미지를 컨테이너로 실행하려면 다음처럼 실행할 수 있다.

```bash
docker run -d -p 8080:80 --name my-nginx-container my-nginx:latest
```

---

## 6. 자주 사용하는 Dockerfile 명령

Dockerfile에는 여러 명령을 사용할 수 있다.
Docker 공식 reference에서 설명하는 대표적인 명령은 다음과 같다. [2]

| 명령 | 의미 |
| --- | --- |
| `FROM` | 기반 이미지를 지정한다. |
| `WORKDIR` | 작업 디렉터리를 변경한다. |
| `COPY` | 파일이나 디렉터리를 이미지 안으로 복사한다. |
| `RUN` | 이미지 빌드 중 명령을 실행한다. |
| `ENV` | 환경 변수를 설정한다. |
| `EXPOSE` | 컨테이너가 수신하는 포트를 설명한다. |
| `CMD` | 컨테이너가 시작될 때 실행할 기본 명령을 지정한다. |
| `ENTRYPOINT` | 컨테이너가 시작될 때 실행할 기본 실행 파일을 지정한다. |

처음에는 모든 명령을 외우려고 하기보다, `FROM`, `COPY`, `RUN`, `CMD` 정도부터 이해하면 된다.

---

## 7. 정리

Dockerfile은 Docker 이미지를 만들기 위한 텍스트 파일이다.

Docker Hub에서 이미 만들어진 이미지를 내려받아 사용할 수도 있지만, 내가 만든 애플리케이션을 이미지로 만들고 싶을 때는 Dockerfile을 작성하면 된다.

전체 흐름은 다음과 같다.

```text
Dockerfile 작성
        ↓
docker build 실행
        ↓
Docker 이미지 생성
        ↓
docker run으로 컨테이너 실행
```

즉, **Dockerfile은 나만의 Docker 이미지를 만들기 위한 출발점**이라고 정리할 수 있다.

---

## 참고 자료

[1] Docker Docs, "Dockerfile overview", https://docs.docker.com/build/concepts/dockerfile/  
[2] Docker Docs, "Dockerfile reference", https://docs.docker.com/reference/builder  
[3] Docker Docs, "Build, tag, and publish an image", https://docs.docker.com/get-started/docker-concepts/building-images/build-tag-and-publish-an-image/  
[4] Docker Docs, "Docker Hub", https://docs.docker.com/docker-hub/
