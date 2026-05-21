---
title: Docker 종료된 컨테이너 디버깅
category: docker-kubernetes
date: 2026-05-11 00:00:00 +0900
tags: [docker, container, debug, exec, entrypoint]
---

## 1. 컨테이너 내부 확인이 필요한 이유

프로그래밍을 할 때는 중간중간 명령어가 잘 실행됐는지 확인하는 습관이 중요하다.

어떤 명령어를 입력한 뒤에 그 명령어가 정상적으로 수행됐는지 확인하는 방법을 함께 알아두면, 문제가 생겼을 때 원인을 훨씬 빠르게 찾을 수 있다.

Docker를 사용하면 대부분의 코드가 컨테이너 내부에서 실행된다.
그래서 파일이 제대로 복사됐는지, 명령어가 어떤 경로에서 실행됐는지, 실행 환경이 어떻게 구성됐는지를 직접 눈으로 확인하기 어려울 때가 있다.

이때 보통 다음 두 가지 방법을 사용한다.

- `docker logs`로 컨테이너 로그 확인하기
- `docker exec -it`로 실행 중인 컨테이너 내부에 들어가기

Docker 공식 문서에 따르면 `docker logs`는 컨테이너 로그를 가져오는 명령이고, `docker exec`는 실행 중인 컨테이너 안에서 새 명령을 실행하는 명령이다. [1][2]

---

## 2. docker exec는 실행 중인 컨테이너에만 사용할 수 있다

`docker exec -it`는 컨테이너 내부에 들어가서 직접 명령어를 실행할 수 있기 때문에 디버깅할 때 자주 사용한다.

예를 들어 실행 중인 컨테이너에 `bash`로 들어가려면 다음처럼 입력한다.

```bash
docker exec -it 컨테이너명 bash
```

또는 `bash`가 없는 이미지라면 `sh`를 사용할 수 있다.

```bash
docker exec -it 컨테이너명 sh
```

하지만 이 명령은 **실행 중인 컨테이너**에만 사용할 수 있다.

Docker 공식 문서에 따르면 `docker exec`로 지정한 명령은 컨테이너의 기본 프로세스, 즉 PID 1이 실행 중일 때만 실행된다. [2]

따라서 컨테이너가 이미 종료된 상태라면 `docker exec -it`로 내부에 들어갈 수 없다.

---

## 3. 왜 컨테이너가 바로 종료될까?

컨테이너는 내부의 메인 프로세스를 기준으로 실행된다.

Docker 공식 문서에 따르면 detached mode로 실행한 컨테이너도 컨테이너를 실행하는 루트 프로세스가 종료되면 종료된다. [3]

즉, 컨테이너 안에서 실행할 명령이 모두 끝나면 컨테이너도 종료될 수 있다.

예를 들어 어떤 이미지를 만들고 컨테이너를 실행했는데, 실행할 작업이 금방 끝나는 구조라면 컨테이너가 바로 종료된다.

이 경우에는 컨테이너 내부가 어떻게 만들어졌는지 확인하려고 해도, 이미 컨테이너가 종료되어 `docker exec -it`를 사용할 수 없다.

---

## 4. 해결 방법: 컨테이너를 잠시 종료되지 않게 만들기

학습이나 디버깅 목적이라면 컨테이너가 바로 종료되지 않도록 임시 명령을 넣을 수 있다.

예를 들어 Dockerfile에 다음처럼 `ENTRYPOINT`를 추가한다.

```dockerfile
FROM openjdk:17-jdk

# 필요한 설정들
# ...

ENTRYPOINT ["/bin/bash", "-c", "sleep 500"]
```

`ENTRYPOINT`는 컨테이너가 시작될 때 실행할 기본 실행 파일을 지정하는 Dockerfile 명령이다. Docker 공식 문서에 따르면 `ENTRYPOINT`는 컨테이너가 실행 파일처럼 동작하도록 설정할 때 사용한다. [4]

위 예시에서는 컨테이너가 시작될 때 `/bin/bash -c "sleep 500"`을 실행한다.

즉, 컨테이너가 500초 동안 종료되지 않고 대기한다.
그 사이에 `docker exec -it`로 컨테이너 내부에 들어가서 디버깅할 수 있다.

---

## 5. 디버깅 흐름

Dockerfile을 수정했다면 이미지를 다시 빌드한다.

```bash
docker build -t debug-test .
```

그 다음 컨테이너를 실행한다.

```bash
docker run -d --name debug-container debug-test
```

컨테이너가 실행 중인지 확인한다.

```bash
docker ps
```

실행 중이라면 `docker exec -it`로 컨테이너 내부에 들어간다.

```bash
docker exec -it debug-container bash
```

컨테이너 내부에서는 필요한 명령어를 직접 실행하면서 확인할 수 있다.

```bash
pwd
ls
java -version
```

확인이 끝났다면 컨테이너 내부에서 나온다.

```bash
exit
```

그리고 디버깅용 컨테이너를 정리한다.

```bash
docker stop debug-container
docker rm debug-container
```

---

## 6. 주의할 점

`ENTRYPOINT ["/bin/bash", "-c", "sleep 500"]`은 디버깅을 위한 임시 설정으로 사용하는 것이 좋다.

이 설정을 그대로 두면 원래 애플리케이션 실행 명령이 아니라 `sleep 500`이 컨테이너의 기본 실행 명령이 된다.

따라서 디버깅이 끝난 뒤에는 실제 애플리케이션을 실행하는 `ENTRYPOINT` 또는 `CMD`로 다시 바꿔야 한다.

예를 들어 Spring Boot 애플리케이션이라면 최종 Dockerfile은 다음처럼 애플리케이션 실행 명령을 사용해야 한다.

```dockerfile
ENTRYPOINT ["java", "-jar", "app.jar"]
```

---

## 핵심 정리

`docker exec -it`는 실행 중인 컨테이너 내부에 들어갈 때 사용하는 명령이다. [2]

하지만 컨테이너가 이미 종료된 상태라면 사용할 수 없다.

이럴 때는 디버깅 목적으로 컨테이너가 바로 종료되지 않도록 `sleep` 명령을 `ENTRYPOINT`에 임시로 넣을 수 있다.

```dockerfile
ENTRYPOINT ["/bin/bash", "-c", "sleep 500"]
```

정리하면 흐름은 다음과 같다.

```text
Dockerfile에 sleep 명령 임시 추가
        ↓
이미지 다시 빌드
        ↓
컨테이너 실행
        ↓
docker exec -it로 내부 접속
        ↓
파일, 경로, 실행 환경 확인
```

즉, **종료가 너무 빨라서 확인할 수 없는 컨테이너는 잠시 살아 있게 만든 뒤 내부에 들어가서 디버깅하면 된다.**

---

## 출처

[1] Docker Docs, `docker container logs`, https://docs.docker.com/reference/cli/docker/container/logs/
[2] Docker Docs, `docker container exec`, https://docs.docker.com/engine/reference/commandline/exec/
[3] Docker Docs, `docker container run`, https://docs.docker.com/reference/cli/docker/container/run/
[4] Docker Docs, "Dockerfile reference - ENTRYPOINT", https://docs.docker.com/reference/dockerfile/#entrypoint
