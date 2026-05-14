---
title: Docker Image List And Remove
category: 3
date: 2026-04-16 00:00:00 +0900
tags: [docker, image, cli, cleanup]
---

## 1. 이미지 조회

로컬에 내려받은 이미지를 확인할 때는 `docker image ls` 명령을 사용한다. [1]

```bash
docker image ls
```

`docker images` 는 `docker image ls` 의 별칭(alias)이다. [1]

기본 출력에서 자주 보는 항목은 다음과 같다. [1]

| 항목 | 의미 |
|---|---|
| `REPOSITORY` | 이미지 저장소 이름 |
| `TAG` | 이미지 태그 |
| `IMAGE ID` | 이미지 식별자 |
| `CREATED` | 이미지가 생성된 시점 |
| `SIZE` | 이미지 크기 |

여기서 `CREATED` 는 **내가 다운로드한 시각이 아니라 이미지가 만들어진 시점**을 의미한다. [1]

또한 `SIZE` 는 해당 이미지와 부모 이미지까지 포함한 누적 크기로 표시된다. [1]

---

## 2. 이미지 ID만 조회

이미지 ID만 간단히 보고 싶다면 `-q` 옵션을 사용할 수 있다. [1]

```bash
docker image ls -q
```

여기서 `-q` 는 `quiet` 의 약자이며,  
상세 정보 대신 이미지 ID만 출력한다. [1]

---

## 3. 특정 이미지 삭제

특정 이미지를 삭제할 때는 `docker image rm` 명령을 사용한다. [2]

```bash
docker image rm [이미지 ID 또는 이미지명:태그]
```

예:

```bash
docker image rm nginx:latest
docker image rm 605c77e624dd
```

Docker 공식 문서 기준으로 이미지는 **짧은 ID(short ID)** 로도 삭제할 수 있다.  
단, 입력한 ID가 하나의 이미지에만 고유하게 매칭되어야 한다. [2]

또한 `docker image rm` 은 단순히 "파일처럼 바로 삭제"되는 개념만은 아니고,  
태그가 여러 개 달린 이미지에서는 먼저 **untag** 가 일어날 수 있다. [2]

즉:

- 하나의 이미지에 여러 태그가 붙어 있으면 태그만 제거될 수 있고 [2]
- 마지막 태그까지 제거될 때 실제 이미지가 삭제된다. [2]

---

## 4. 강제 삭제

강제로 삭제할 때는 `-f` 옵션을 사용한다. [2]

```bash
docker image rm -f [이미지 ID 또는 이미지명]
```

공식 문서 기준으로 **실행 중인 컨테이너가 사용하는 이미지도 `-f` 옵션으로 삭제할 수 있다**고 설명한다. [2]

다만 실무에서는:

- 실행 중 컨테이너가 있으면 먼저 컨테이너 상태를 확인하고
- 정말 필요한 경우에만 강제 삭제하는 편이 안전하다.

---

## 5. 여러 이미지 한 번에 삭제

여러 이미지를 한 번에 삭제하려면 여러 인자를 함께 넘길 수 있다. [2]

```bash
docker image rm image1 image2 image3
```

이미지 ID 목록만 뽑아서 한꺼번에 삭제하는 방식도 자주 사용한다.

예를 들어 셸 기능을 이용하면 다음과 같이 실행할 수 있다.

```bash
docker image rm $(docker image ls -q)
```

강제로 삭제하려면:

```bash
docker image rm -f $(docker image ls -q)
```

다만 이 방식은 **셸 문법에 의존**하므로,  
Bash, Zsh, PowerShell 등 환경에 따라 동작 형태가 달라질 수 있다.

---

## 6. 전체 정리와 주의점

이미지 정리 시 기억할 포인트는 다음과 같다.

- `docker image ls` 는 로컬 이미지를 조회하는 명령이다. [1]
- `docker image ls -q` 는 이미지 ID만 출력한다. [1]
- `docker image rm` 은 이미지 또는 태그를 제거하는 명령이다. [2]
- `-f` 는 강제 삭제 옵션이다. [2]

또한 문서상 이미지 삭제는 로컬 호스트에서만 일어나며,  
레지스트리(Docker Hub 등)의 이미지를 지우는 것은 아니다. [2]

---

## 7. 핵심 정리

> **조회**
>
> - `docker image ls`
> - `docker image ls -q`
>
> **삭제**
>
> - `docker image rm [이미지 ID 또는 이미지명:태그]`
> - `docker image rm -f [이미지 ID 또는 이미지명:태그]`
>
> **주의**
>
> - `CREATED` 는 다운로드 시점이 아니라 이미지 생성 시점 [1]
> - `-q` 는 `quiet` 옵션 [1]
> - `rm` 은 태그 제거와 실제 이미지 삭제를 모두 포함하는 개념 [2]

---

## 참고 자료

1. Docker Docs, `docker image ls`  
   https://docs.docker.com/reference/cli/docker/image/ls/
2. Docker Docs, `docker image rm`  
   https://docs.docker.com/reference/cli/docker/image/rm/
