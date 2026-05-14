---
title: Docker Image Pull
category: 3
date: 2026-04-15 00:00:00 +0900
tags: [docker, image, dockerhub, registry]
---

## 1. 이미지 다운로드

Docker에서 이미지를 로컬로 내려받을 때는 `docker pull` 명령을 사용한다. [1]

```bash
# docker pull 이미지명[:태그명]
docker pull nginx
```

위 명령은 `nginx` 이미지를 내려받는다.  
공식 문서 기준으로 태그를 생략하면 Docker는 기본적으로 `latest` 태그를 사용한다. [1][2][3]

즉,

```bash
docker pull nginx
```

는 다음과 같은 의미로 동작한다. [1][2]

```bash
docker pull nginx:latest
```

---

## 2. 레지스트리를 생략하면 Docker Hub를 사용

이미지를 받을 때 별도의 레지스트리 주소를 적지 않으면,  
Docker는 기본적으로 `docker.io`를 사용한다. [2]

예를 들어 `nginx` 는 문서상 다음과 같이 해석된다. [2][3]

```text
docker.io/library/nginx:latest
```

여기서:

- `docker.io` 는 기본 레지스트리
- `library` 는 기본 네임스페이스
- `nginx` 는 저장소 이름
- `latest` 는 기본 태그

즉, 초안에서 말한 것처럼 **Docker Hub는 이미지를 저장하고 내려받는 레지스트리 역할**을 한다고 이해하면 된다. [2][4]

---

## 3. 특정 버전 이미지 다운로드

특정 버전이나 변형을 받고 싶다면 `이미지명:태그명` 형식으로 지정하면 된다. [1][4]

```bash
docker pull nginx:stable-perl
```

여기서 `stable-perl` 같은 값이 **태그(tag)** 다. [4]

태그는 하나의 이미지 저장소 안에서 서로 다른 버전, 변형, 배포 단위를 구분하는 이름이다. [4]

---

## 4. latest 태그를 볼 때 주의할 점

`latest` 는 **태그를 생략했을 때 기본으로 사용되는 태그 이름**이지,  
항상 "가장 최신 버전"을 뜻한다고 단정하면 안 된다. [1][4]

공식 문서는 태그 미지정 시 `latest` 가 기본값이라고 설명하지만,  
어떤 태그를 어떤 이미지에 붙일지는 이미지 제공자가 관리한다. [1][4]

따라서 실무에서는 재현성을 위해:

- `latest` 대신
- `nginx:1.27`
- `python:3.12.8`

처럼 **명시적인 태그를 사용하는 경우가 많다.**

---

## 5. 정리

> **docker pull**
>
> - 이미지를 레지스트리에서 로컬로 내려받는 명령 [1]
>
> **태그 생략**
>
> - 기본적으로 `latest` 태그를 사용 [1][2][3]
>
> **레지스트리 생략**
>
> - 기본적으로 `docker.io`(Docker Hub)를 사용 [2][3]
>
> **태그**
>
> - 이미지의 버전이나 변형을 구분하는 이름 [4]

---

## 참고 자료

1. Docker Docs, `docker image pull`  
   https://docs.docker.com/reference/cli/docker/image/pull/
2. Docker Docs, `docker image tag`  
   https://docs.docker.com/engine/reference/commandline/tag/
3. Docker Docs, Build, tag, and publish an image  
   https://docs.docker.com/get-started/docker-concepts/building-images/build-tag-and-publish-an-image/
4. Docker Docs, Tags on Docker Hub  
   https://docs.docker.com/docker-hub/repos/manage/hub-images/tags/
