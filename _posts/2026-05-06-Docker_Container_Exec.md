---
title: Docker Container Exec
category: d
date: 2026-05-06 00:00:00 +0900
tags: [docker, container, exec, bash, shell]
---

## 1. 컨테이너 개념 다시 짚어보기

컨테이너는 호스트 컴퓨터 위에서 격리되어 실행되는 프로세스다.
Docker 공식 문서에 따르면 컨테이너에서 실행되는 프로세스는 자체 파일 시스템, 자체 네트워크, 호스트와 분리된 프로세스 트리를 가진다. [2]

따라서 학습 관점에서는 컨테이너를 **호스트 컴퓨터 안에 따로 마련된 실행 공간**으로 이해할 수 있다.
컨테이너마다 파일 시스템, 설치된 프로그램, 실행 중인 프로세스가 분리되어 있기 때문이다. [2]

---

## 2. 실행 중인 컨테이너 내부에 접속하기

실행 중인 컨테이너 안에서 명령어를 실행하려면 `docker exec` 명령을 사용한다.
Docker 공식 문서에 따르면 `docker exec`는 실행 중인 컨테이너 안에서 새 명령을 실행하는 명령이며, `docker container exec`의 별칭(alias)이다. [1]

```bash
docker exec [옵션] 컨테이너명 명령어
docker exec [옵션] 컨테이너ID 명령어
```

컨테이너 내부에 쉘로 접속하려면 보통 다음처럼 `-it` 옵션과 `bash`를 함께 사용한다.

```bash
docker exec -it 컨테이너명 bash
```

또는 컨테이너 ID를 사용할 수 있다.

```bash
docker exec -it 컨테이너ID bash
```

---

## 3. Nginx 컨테이너 내부 접속 예시

먼저 Nginx 컨테이너를 백그라운드에서 실행한다.

```bash
docker run -d --name nginx-exec-test nginx
```

컨테이너가 실행 중인지 확인한다.

```bash
docker ps
```

그 다음 `docker exec -it` 명령으로 컨테이너 내부에 접속한다.

```bash
docker exec -it nginx-exec-test bash
```

접속 후에는 컨테이너 내부에서 명령어를 실행할 수 있다.

```bash
ls
cd /etc/nginx
cat nginx.conf
```

컨테이너 내부에서 나오려면 다음 중 하나를 사용한다.

```bash
exit
```

또는 터미널에서 `Ctrl + D`를 입력한다.

---

## 4. `bash`의 의미

`bash`는 쉘(Shell)의 한 종류다.
쉘은 사용자가 입력한 명령어를 운영체제에 전달하고, 실행 결과를 다시 보여주는 프로그램이다.

```bash
docker exec -it nginx-exec-test bash
```

위 명령은 `nginx-exec-test` 컨테이너 안에서 `bash` 명령을 실행한다는 뜻이다.

단, 모든 컨테이너 이미지에 `bash`가 설치되어 있는 것은 아니다.
예를 들어 가벼운 이미지에는 `bash`가 없고 `sh`만 있는 경우가 있다.
이 경우에는 다음처럼 `sh`로 접속할 수 있다.

```bash
docker exec -it 컨테이너명 sh
```

Docker 공식 문서의 예시에서도 실행 중인 컨테이너 안에 대화형 `sh` 쉘을 실행할 때 `docker exec -it mycontainer sh`를 사용한다. [1]

---

## 5. `-it` 옵션의 의미

`-it`는 실제로 두 옵션을 붙여 쓴 것이다.

- `-i`, `--interactive` : 표준 입력(STDIN)을 열린 상태로 유지한다. [1]
- `-t`, `--tty` : 가상 터미널(pseudo-TTY)을 할당한다. [1]

즉, `-it`는 컨테이너 안에서 명령어를 직접 입력하고 결과를 확인할 수 있도록 만드는 조합이다.

```bash
docker exec -it 컨테이너명 bash
```

`-it` 없이 단일 명령만 실행할 수도 있다.

```bash
docker exec nginx-exec-test ls /etc/nginx
```

위 명령은 컨테이너 내부의 `/etc/nginx` 목록을 한 번 출력하고 종료한다.
반면 `docker exec -it nginx-exec-test bash`는 쉘 세션을 열기 때문에, 사용자가 `exit` 또는 `Ctrl + D`로 나가기 전까지 계속 명령어를 입력할 수 있다.

---

## 6. `docker exec` 사용 시 주의할 점

`docker exec`는 **실행 중인 컨테이너**를 대상으로 한다.
Docker 공식 문서에 따르면 `docker exec`로 지정한 명령은 컨테이너의 기본 프로세스, 즉 PID 1이 실행 중일 때만 실행된다. [1]

따라서 컨테이너가 종료된 상태라면 먼저 컨테이너를 시작해야 한다.

```bash
docker start 컨테이너명
docker exec -it 컨테이너명 bash
```

또한 `docker exec`로 실행한 명령은 컨테이너가 재시작될 때 자동으로 다시 실행되지 않는다. [1]

---

## 핵심 정리

> **컨테이너 내부 접속**
>
> - `docker exec -it 컨테이너명 bash` : 실행 중인 컨테이너 안에서 `bash` 실행 [1]
> - `docker exec -it 컨테이너ID bash` : 컨테이너 ID를 사용해 `bash` 실행 [1]
> - `docker exec -it 컨테이너명 sh` : `bash`가 없을 때 `sh` 실행 [1]
>
> **옵션**
>
> - `-i`, `--interactive` : 표준 입력을 열린 상태로 유지 [1]
> - `-t`, `--tty` : 가상 터미널 할당 [1]
> - `-it` : 컨테이너 내부에서 계속 명령어를 입력하기 위한 일반적인 조합 [1]
>
> **종료**
>
> - `exit` : 컨테이너 내부 쉘에서 나가기
> - `Ctrl + D` : 현재 쉘 입력 종료

---

## 출처

1. Docker Docs, `docker container exec`
   https://docs.docker.com/engine/reference/commandline/exec
2. Docker Docs, Running containers
   https://docs.docker.com/engine/containers/run/
