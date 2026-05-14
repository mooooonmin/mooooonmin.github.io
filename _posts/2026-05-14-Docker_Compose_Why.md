---
title: Docker Compose를 사용하는 이유
category: 1
date: 2026-05-14 00:00:10 +0900
tags: [docker, docker-compose, compose, container, yaml]
---

## 1. Docker Compose란?

Docker Compose는 **여러 개의 Docker 컨테이너로 구성된 애플리케이션을 정의하고 실행하는 도구**이다.

Docker 공식 문서에 따르면 Docker Compose는 멀티 컨테이너 애플리케이션을 정의하고 실행하기 위한 도구이다. 또한 애플리케이션 전체 스택의 서비스, 네트워크, 볼륨을 하나의 YAML 설정 파일에서 관리할 수 있게 해준다. [1]

쉽게 말하면, 여러 컨테이너를 하나씩 `docker run`으로 실행하는 대신 `compose.yaml` 파일에 필요한 설정을 적어두고 한 번에 실행할 수 있게 해주는 도구이다.

예를 들어 애플리케이션이 다음처럼 여러 컨테이너로 이루어져 있다고 하자.

- 웹 서버 컨테이너
- 백엔드 서버 컨테이너
- MySQL 컨테이너
- Redis 컨테이너

이런 컨테이너들을 각각 따로 실행하고 연결하려면 명령어가 길어지고 관리가 복잡해진다.

Docker Compose를 사용하면 이 컨테이너들을 하나의 `compose.yaml` 파일에 서비스 단위로 정의하고, 다음 명령어 하나로 실행할 수 있다.

```bash
docker compose up
```

Docker 공식 문서에 따르면 Compose에서는 YAML 설정 파일로 애플리케이션의 서비스를 구성하고, Compose CLI로 해당 설정의 모든 서비스를 생성하고 시작한다. [2]

---

## 2. Docker Compose를 사용하는 이유

Docker Compose를 사용하는 가장 큰 이유는 **여러 컨테이너를 하나의 애플리케이션처럼 관리할 수 있기 때문**이다.

컨테이너가 하나뿐이라면 `docker run`만으로도 충분할 수 있다.

하지만 실제 애플리케이션은 보통 하나의 컨테이너만으로 끝나지 않는다.

예를 들어 백엔드 서버와 MySQL을 함께 실행해야 한다면 최소 2개의 컨테이너가 필요하다.

- 백엔드 서버 컨테이너
- MySQL 컨테이너

여기에 Redis, Nginx, 메시지 큐 같은 도구가 추가되면 실행해야 할 컨테이너가 더 늘어난다.

Docker Compose는 이런 여러 컨테이너의 실행 설정을 한 파일에 모아두고, 한 번에 실행하고 중지할 수 있게 해준다.

---

## 3. 긴 docker run 명령어를 줄일 수 있다

Docker Compose를 쓰지 않으면 컨테이너를 실행할 때마다 긴 `docker run` 명령어를 직접 입력해야 할 수 있다.

예를 들어 MySQL 컨테이너를 실행한다고 해보자.

```bash
docker run -e MYSQL_ROOT_PASSWORD=password123 -p 3306:3306 -v /Users/jaeseong/Documents/Develop/docker-mysql/mysql_data:/var/lib/mysql -d mysql
```

위 명령어에는 여러 설정이 들어 있다.

- `-e MYSQL_ROOT_PASSWORD=password123`: MySQL root 비밀번호를 환경 변수로 설정한다.
- `-p 3306:3306`: 호스트의 3306번 포트와 컨테이너의 3306번 포트를 연결한다.
- `-v /Users/jaeseong/Documents/Develop/docker-mysql/mysql_data:/var/lib/mysql`: 호스트 디렉터리를 컨테이너의 MySQL 데이터 디렉터리에 마운트한다.
- `-d`: 컨테이너를 백그라운드에서 실행한다.
- `mysql`: 사용할 이미지 이름이다.

이 명령어는 한 번만 보면 이해할 수 있지만, 매번 직접 입력하기에는 길고 실수하기 쉽다.

Docker Compose를 사용하면 이 설정을 `compose.yaml` 파일에 적어둘 수 있다.

```yaml
services:
  db:
    image: mysql
    environment:
      MYSQL_ROOT_PASSWORD: password123
    ports:
      - "3306:3306"
    volumes:
      - /Users/jaeseong/Documents/Develop/docker-mysql/mysql_data:/var/lib/mysql
```

이제 MySQL 컨테이너를 실행할 때는 다음 명령어만 사용하면 된다.

```bash
docker compose up -d
```

Docker 공식 CLI 문서에 따르면 `docker compose up`은 컨테이너를 생성하고 시작하는 명령이다. [3]

즉, Docker Compose를 사용하면 길고 복잡한 실행 옵션을 매번 직접 입력하지 않고, 설정 파일에 저장해두고 재사용할 수 있다.

---

## 4. 실행 환경을 파일로 공유할 수 있다

Docker Compose의 또 다른 장점은 실행 환경을 파일로 공유할 수 있다는 점이다.

Docker 공식 문서에 따르면 Docker Compose를 사용하면 모든 컨테이너와 설정을 하나의 YAML 파일에 정의할 수 있고, 이 파일을 코드 저장소에 포함하면 다른 사람이 저장소를 clone한 뒤 단일 명령어로 실행 환경을 시작할 수 있다. [4]

예를 들어 프로젝트에 `compose.yaml` 파일이 포함되어 있다면, 다른 개발자는 복잡한 실행 옵션을 직접 외울 필요가 없다.

프로젝트를 받은 뒤 다음 명령어를 실행하면 된다.

```bash
docker compose up
```

이렇게 하면 개발 환경을 맞추는 과정에서 생기는 차이를 줄일 수 있다.

---

## 5. 정리

Docker Compose는 여러 컨테이너를 하나의 애플리케이션 단위로 정의하고 실행하기 위한 도구이다.

핵심은 다음과 같다.

- Docker Compose는 멀티 컨테이너 애플리케이션을 정의하고 실행하는 도구이다. [1]
- `compose.yaml` 파일에 서비스, 네트워크, 볼륨 같은 설정을 작성할 수 있다. [1][2]
- 긴 `docker run` 명령어를 매번 입력하지 않고 `docker compose up`으로 실행할 수 있다. [3]
- 여러 컨테이너로 구성된 애플리케이션을 한 번에 관리하기 쉽다.
- `compose.yaml` 파일을 공유하면 다른 개발자도 같은 실행 환경을 쉽게 사용할 수 있다. [4]

---

## 참고자료

[1] Docker Docs, Docker Compose: <https://docs.docker.com/compose/>  
[2] Docker Docs, How Compose works: <https://docs.docker.com/compose/intro/compose-application-model/>  
[3] Docker Docs, docker compose up: <https://docs.docker.com/reference/cli/docker/compose/up/>  
[4] Docker Docs, What is Docker Compose?: <https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-docker-compose/>
