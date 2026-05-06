---
title: Docker Volume
category: 1
date: 2026-05-07 00:00:00 +0900
tags: [docker, container, volume, bind-mount, storage]
---

## 1. 컨테이너가 가진 데이터 저장 문제

Docker를 사용하면 특정 프로그램을 컨테이너로 실행할 수 있다.
컨테이너는 이미지에서 만들어진 실행 환경이며, 컨테이너 안에서는 파일을 만들고 수정하고 삭제할 수 있다. [1]

하지만 컨테이너 내부의 변경 내용은 기본적으로 해당 컨테이너의 생명주기에 묶인다.
Docker 공식 문서에 따르면 컨테이너가 삭제되면 컨테이너 안에서 변경된 파일도 함께 삭제된다. [1]

예를 들어 MySQL이나 PostgreSQL 같은 데이터베이스를 컨테이너로 실행했다고 가정해보자.
데이터베이스 파일을 컨테이너 내부에만 저장하면, 컨테이너를 삭제하고 새 컨테이너로 교체할 때 데이터도 사라질 수 있다. [1]

따라서 컨테이너를 교체하더라도 유지되어야 하는 데이터가 있다면,
컨테이너 내부 저장 공간이 아니라 컨테이너 밖의 저장 공간을 사용해야 한다.
이때 사용하는 대표적인 방법이 **Docker Volume**이다. [1][2]

---

## 2. Docker Volume이란?

Docker Volume은 컨테이너에서 생성하고 사용하는 데이터를 영속적으로 저장하기 위한 Docker의 저장소 방식이다. [2]

Docker 공식 문서에서는 볼륨을 컨테이너가 생성하고 사용하는 데이터를 유지하기 위한 선호 방식이라고 설명한다. [2]
볼륨은 Docker가 관리하며, 호스트의 Docker 저장소 영역 안에 만들어진다. [2]

컨테이너에 볼륨을 연결하면 컨테이너는 해당 경로를 일반 디렉터리처럼 사용할 수 있다.
그러나 실제 데이터는 컨테이너의 쓰기 가능한 레이어가 아니라 볼륨에 저장된다. [2]

즉, 컨테이너를 삭제해도 볼륨 자체는 자동으로 삭제되지 않는다.
Docker 공식 문서에 따르면 볼륨의 내용은 특정 컨테이너의 생명주기 밖에 존재하며,
컨테이너가 삭제되어도 볼륨의 데이터는 유지된다. [2]

---

## 3. Volume을 사용하는 기본 명령어

Docker Volume을 사용하는 기본 형식은 다음과 같다.

```bash
docker run -v [볼륨명]:[컨테이너의 디렉터리 절대경로] [이미지명]:[태그명]
```

예를 들어 `mysql-data`라는 볼륨을 MySQL 컨테이너의 데이터 저장 경로에 연결하려면 다음과 같이 실행할 수 있다.

```bash
docker run -d \
  --name mysql-volume-test \
  -e MYSQL_ROOT_PASSWORD=1234 \
  -v mysql-data:/var/lib/mysql \
  mysql:latest
```

위 명령에서 `mysql-data`는 Docker Volume의 이름이고,
`/var/lib/mysql`은 컨테이너 내부에서 MySQL 데이터가 저장되는 경로이다.

만약 `mysql-data`라는 볼륨이 아직 없다면 Docker가 자동으로 생성한다. [2]
이후 컨테이너를 삭제하고 새 컨테이너를 만들더라도 같은 볼륨을 다시 연결하면 기존 데이터를 계속 사용할 수 있다. [1][2]

---

## 4. Volume 관리 명령어

볼륨은 컨테이너와 별도로 관리할 수 있다. [2]

볼륨 생성:

```bash
docker volume create my-volume
```

볼륨 목록 확인:

```bash
docker volume ls
```

볼륨 상세 정보 확인:

```bash
docker volume inspect my-volume
```

볼륨 삭제:

```bash
docker volume rm my-volume
```

사용하지 않는 볼륨 전체 삭제:

```bash
docker volume prune
```

Docker 공식 문서에 따르면 `docker volume rm`은 컨테이너에 연결되어 있지 않은 볼륨을 삭제할 때 사용하고,
`docker volume prune`은 사용하지 않는 볼륨을 삭제할 때 사용한다. [1]

---

## 5. 호스트 디렉터리를 직접 연결하는 방식

다음과 같은 명령어도 자주 사용된다.

```bash
docker run -v [호스트의 디렉터리 절대경로]:[컨테이너의 디렉터리 절대경로] [이미지명]:[태그명]
```

예시는 다음과 같다.

```bash
docker run -d \
  --name nginx-bind-test \
  -v C:\docker-html:/usr/share/nginx/html \
  nginx:latest
```

이 방식은 Docker가 관리하는 named volume이 아니라,
호스트의 특정 파일 또는 디렉터리를 컨테이너 안으로 연결하는 **bind mount** 방식이다. [3]

bind mount를 사용하면 호스트의 디렉터리가 컨테이너의 지정한 경로에 마운트된다. [3]
따라서 컨테이너에서 해당 경로에 파일을 쓰면 호스트 디렉터리에도 반영될 수 있다.

---

## 6. 기존 파일이 있는 경로에 마운트하면 어떻게 될까?

볼륨이나 bind mount를 컨테이너 내부의 비어 있지 않은 디렉터리에 연결하면 주의해야 한다.

Docker 공식 문서에 따르면 bind mount를 컨테이너의 기존 파일이 있는 디렉터리에 마운트하면,
컨테이너에 원래 있던 파일은 삭제되는 것이 아니라 마운트된 디렉터리 뒤에 가려진다. [3]

예를 들어 Nginx 컨테이너의 `/usr/share/nginx/html` 경로에는 기본 HTML 파일이 들어 있다.
그런데 호스트의 `C:\docker-html` 디렉터리를 이 경로에 bind mount하면,
컨테이너의 기본 HTML 파일 대신 호스트의 `C:\docker-html` 내용이 보이게 된다. [3]

이때 컨테이너 안의 기존 파일이 실제로 삭제된 것은 아니다.
다만 마운트 때문에 접근할 수 없게 보이는 상태이다. [3]

---

## 7. 빈 Volume을 연결하면 파일이 복사될 수 있다

named volume에서는 다른 동작도 있다.

Docker 공식 문서에 따르면 비어 있는 볼륨을 컨테이너 내부의 파일이 이미 있는 디렉터리에 마운트하면,
기본적으로 컨테이너의 기존 파일이나 디렉터리가 볼륨으로 복사된다. [2]

즉, 아래 명령처럼 Docker가 관리하는 볼륨을 사용하는 경우에는
컨테이너의 기존 파일이 빈 볼륨 안으로 복사될 수 있다. [2]

```bash
docker run -v my-volume:/app nginx:latest
```

반대로 호스트 절대경로를 사용하는 bind mount에서는 이 설명을 그대로 적용하면 안 된다.
Docker 공식 문서에 따르면 `-v`로 bind mount를 사용할 때 호스트 경로가 없으면 Docker가 해당 경로를 디렉터리로 생성하지만,
컨테이너 파일을 호스트로 복사한다는 설명은 bind mount가 아니라 빈 volume의 동작에 해당한다. [2][3]

---

## 8. Volume과 Bind Mount 차이

| 구분 | Volume | Bind Mount |
| --- | --- | --- |
| 저장 위치 | Docker가 관리하는 호스트 저장소 | 사용자가 지정한 호스트 경로 |
| 생성 방식 | `docker volume create` 또는 컨테이너 실행 시 자동 생성 | 호스트 파일 또는 디렉터리 경로를 직접 지정 |
| Docker 권장 용도 | 컨테이너 데이터 영속 저장 | 개발 중 소스 코드 공유, 설정 파일 연결 |
| 호스트 경로 의존성 | 낮음 | 높음 |
| 예시 | `-v mysql-data:/var/lib/mysql` | `-v C:\data:/var/lib/mysql` |

Docker 공식 문서에 따르면 컨테이너가 생성하고 사용하는 데이터를 영속적으로 저장할 때는 Volume이 선호되는 방식이다. [2]
반면 bind mount는 호스트의 디렉터리 구조와 운영체제에 의존한다. [2][3]

---

## 핵심 정리

> **컨테이너의 기본 저장 공간**
>
> - 컨테이너가 삭제되면 컨테이너 내부의 파일 변경 내용도 삭제된다. [1]
>
> **Docker Volume**
>
> - 컨테이너 데이터 영속 저장을 위한 Docker 관리 저장소이다. [2]
> - 컨테이너를 삭제해도 볼륨 데이터는 유지된다. [2]
> - 데이터베이스처럼 유지되어야 하는 데이터에 적합하다. [1][2]
>
> **Bind Mount**
>
> - 호스트의 특정 경로를 컨테이너에 직접 연결하는 방식이다. [3]
> - `-v [호스트 절대경로]:[컨테이너 절대경로]` 형식은 bind mount에 해당한다. [3]
> - 컨테이너의 기존 파일이 있는 경로에 연결하면 기존 파일은 삭제되지 않고 마운트에 의해 가려진다. [3]
>
> **주의할 점**
>
> - 빈 named volume을 컨테이너의 기존 파일이 있는 경로에 연결하면 파일이 볼륨으로 복사될 수 있다. [2]
> - 호스트 절대경로를 사용하는 bind mount와 Docker가 관리하는 volume의 동작을 구분해야 한다. [2][3]

---

## 참고 자료

1. Docker Docs, "Persisting container data"  
   https://docs.docker.com/get-started/docker-concepts/running-containers/persisting-container-data/
2. Docker Docs, "Volumes"  
   https://docs.docker.com/engine/storage/volumes/
3. Docker Docs, "Bind mounts"  
   https://docs.docker.com/engine/storage/bind-mounts/
