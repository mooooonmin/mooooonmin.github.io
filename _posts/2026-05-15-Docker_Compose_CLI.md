---
title: 자주 사용하는 Docker Compose CLI 명령어
category: docker-kubernetes
date: 2026-05-15 00:00:00 +0900
tags: [docker, docker-compose, compose, cli, container]
---

## 1. Docker Compose CLI 문법

Docker Compose v1은 `docker-compose` 명령으로 실행되었고, Compose v2는 `docker compose` 명령으로 실행된다. Docker 공식 문서 기준으로, 확인일인 2026-05-14 현재 지원되는 Docker Compose CLI 버전은 Compose v2와 Compose v5이다. [1]

또한 Docker 공식 문서는 standalone legacy Compose 설치 방식을 권장하지 않으며, 호환성 목적일 때만 사용하라고 설명한다. 이 legacy 방식은 현재 표준 문법인 `docker compose` 대신 `docker-compose` 문법을 사용한다. [2]

그래서 새로 Docker Compose 명령어를 작성할 때는 `docker-compose`보다 `docker compose` 형식으로 작성하는 것이 좋다. [1][2]

> 아래 명령어들은 Compose 파일이 있는 디렉터리에서 실행한다. Docker 공식 문서 기준 기본 Compose 파일 경로는 작업 디렉터리의 `compose.yaml` 또는 `compose.yml`이며, `compose.yaml`이 선호되는 이름이다. [3]

## 2. compose.yml 작성

Compose 파일은 애플리케이션의 서비스를 YAML로 정의하는 파일이다. Docker 공식 문서에 따르면 Compose 파일에는 `services` 최상위 요소를 선언하고, 그 아래에 서비스 이름과 서비스별 설정을 작성한다. [4]

**compose.yml**

```yaml
services:
  webserver:
    container_name: webserver
    image: nginx
    ports:
      - "80:80"
```

위 예시는 `webserver` 서비스를 정의하고, `nginx` 이미지를 사용하며, 호스트의 80번 포트와 컨테이너의 80번 포트를 연결한다. Compose의 `image` 속성은 컨테이너를 시작할 이미지를 지정하고, `ports` 속성은 호스트와 컨테이너 사이의 포트 매핑을 정의한다. [4]

## 3. compose.yml에 정의한 컨테이너 실행

`docker compose up`은 Compose 파일에 정의된 서비스의 컨테이너를 생성하고 시작하는 명령이다. Docker 공식 문서는 이 명령이 서비스 컨테이너를 build, recreate, start, attach한다고 설명한다. [5]

```bash
docker compose up
docker compose up -d
```

- `docker compose up`: 포그라운드에서 실행한다. 명령이 실행되는 동안 각 컨테이너의 출력이 현재 터미널에 모여서 출력된다. [5]
- `docker compose up -d`: detached mode로 실행한다. Docker 공식 문서에 따르면 `--detach` 또는 `-d` 옵션은 컨테이너를 백그라운드에서 실행하고 계속 실행 상태로 둔다. [5]

## 4. Docker Compose로 실행한 컨테이너 확인

`docker compose ps`는 Compose 프로젝트의 컨테이너 목록을 보여주는 명령이다. Docker 공식 문서 기준 기본 출력은 실행 중인 컨테이너만 보여주고, `--all` 또는 `-a` 옵션을 사용하면 중지된 컨테이너도 포함한다. [6]

```bash
docker compose ps
docker compose ps -a
```

- `docker compose ps`: Compose 프로젝트에서 실행 중인 컨테이너를 확인한다. [6]
- `docker compose ps -a`: Compose 프로젝트의 중지된 컨테이너까지 포함해서 확인한다. [6]

## 5. Docker Compose 로그 확인

`docker compose logs`는 Compose 서비스의 로그 출력을 확인하는 명령이다. Docker 공식 문서는 이 명령을 서비스의 로그 출력을 표시하는 명령으로 설명한다. [7]

```bash
docker compose logs
```

실시간으로 로그를 계속 보고 싶다면 `-f` 또는 `--follow` 옵션을 사용할 수 있다. [7]

```bash
docker compose logs -f
```

## 6. 컨테이너 실행 전에 이미지 재빌드

`docker compose up --build`는 컨테이너를 시작하기 전에 이미지를 빌드하는 옵션이다. Docker 공식 CLI 문서에서 `docker compose up`의 `--build` 옵션은 컨테이너 시작 전에 이미지를 빌드한다고 설명된다. [5]

```bash
docker compose up --build
docker compose up --build -d
```

- `docker compose up --build`: 이미지를 빌드한 뒤 포그라운드에서 컨테이너를 실행한다. [5]
- `docker compose up --build -d`: 이미지를 빌드한 뒤 백그라운드에서 컨테이너를 실행한다. [5]

Compose 서비스의 `Dockerfile` 또는 build context 안의 파일이 변경되었다면 이미지를 다시 빌드해야 변경 내용이 이미지에 반영된다. Docker 공식 문서도 서비스의 `Dockerfile`이나 build directory 내용이 바뀌면 `docker compose build`를 실행해 다시 빌드하라고 설명한다. [8]

> **참고: `docker compose up` vs `docker compose up --build`**
>
> - `docker compose up`: 서비스를 생성하고 시작한다. 기존 컨테이너가 있고 서비스 설정이나 이미지가 컨테이너 생성 이후 변경되었다면 Compose는 컨테이너를 중지하고 다시 생성해서 변경을 반영한다. [5]
> - `docker compose up --build`: 컨테이너 시작 전에 이미지를 빌드한다. [5]

## 7. 이미지 내려받기 또는 업데이트하기

`docker compose pull`은 Compose 파일에 정의된 서비스 이미지들을 내려받는 명령이다. Docker 공식 문서는 이 명령이 `compose.yaml` 파일에 정의된 서비스의 이미지를 pull하지만, 그 이미지로 컨테이너를 시작하지는 않는다고 설명한다. [9]

```bash
docker compose pull
```

`--policy` 옵션을 사용하면 pull 정책을 지정할 수 있다. Docker 공식 문서 기준 `docker compose pull`의 `--policy` 옵션 값은 `missing` 또는 `always`이다. [9]

```bash
docker compose pull --policy always
```

## 8. Docker Compose로 실행한 컨테이너 종료

`docker compose down`은 `docker compose up`으로 생성된 컨테이너를 중지하고, 컨테이너와 네트워크를 제거하는 명령이다. Docker 공식 문서는 이 명령이 `up`으로 생성한 컨테이너, 네트워크, 볼륨, 이미지를 중지하고 제거한다고 설명한다. 다만 기본적으로 제거되는 대상은 Compose 파일에 정의된 서비스 컨테이너, Compose 파일의 networks 섹션에 정의된 네트워크, 그리고 기본 네트워크이다. [10]

```bash
docker compose down
```

기본 `docker compose down`은 anonymous volume을 제거하지 않는다. 볼륨까지 제거하려면 `-v` 또는 `--volumes` 옵션을 사용한다. [10]

```bash
docker compose down -v
```

## 핵심 정리

자주 사용하는 Docker Compose CLI 명령어는 다음처럼 정리할 수 있다.

| 명령어 | 용도 |
| --- | --- |
| `docker compose up` | Compose 서비스 컨테이너를 생성하고 실행한다. [5] |
| `docker compose up -d` | 컨테이너를 백그라운드에서 실행한다. [5] |
| `docker compose ps` | 실행 중인 Compose 컨테이너를 확인한다. [6] |
| `docker compose ps -a` | 중지된 컨테이너까지 포함해서 확인한다. [6] |
| `docker compose logs` | Compose 서비스 로그를 확인한다. [7] |
| `docker compose up --build` | 컨테이너 시작 전에 이미지를 빌드한다. [5] |
| `docker compose pull` | Compose 서비스 이미지를 내려받는다. [9] |
| `docker compose down` | Compose 컨테이너와 네트워크를 중지하고 제거한다. [10] |

## 참고 자료

확인일: 2026-05-14

[1] Docker Docs, History and development of Docker Compose: <https://docs.docker.com/compose/intro/history/>  
[2] Docker Docs, Install the Docker Compose standalone (Legacy): <https://docs.docker.com/compose/install/standalone/>  
[3] Docker Docs, How Compose works - The Compose file: <https://docs.docker.com/compose/intro/compose-application-model/>  
[4] Docker Docs, Define services in Docker Compose: <https://docs.docker.com/reference/compose-file/services/>  
[5] Docker Docs, `docker compose up`: <https://docs.docker.com/reference/cli/docker/compose/up/>  
[6] Docker Docs, `docker compose ps`: <https://docs.docker.com/reference/cli/docker/compose/ps/>  
[7] Docker Docs, `docker compose logs`: <https://docs.docker.com/reference/cli/docker/compose/logs/>  
[8] Docker Docs, `docker compose build`: <https://docs.docker.com/reference/cli/docker/compose/build/>  
[9] Docker Docs, `docker compose pull`: <https://docs.docker.com/reference/cli/docker/compose/pull/>  
[10] Docker Docs, `docker compose down`: <https://docs.docker.com/reference/cli/docker/compose/down/>
