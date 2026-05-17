---
title: Ubuntu에서 Docker, Docker Compose 설치하기
category: 3
date: 2026-05-18 00:00:00 +0900
tags: [docker, ubuntu, docker-compose, compose, install]
---

## 1. 설치 방식

Docker 공식 문서는 Ubuntu에서 Docker Engine을 설치할 때 Docker의 `apt` 저장소를 설정한 뒤 `docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-buildx-plugin`, `docker-compose-plugin` 패키지를 설치하는 방법을 안내한다. [1]

Docker Compose는 Linux에서 Docker Compose plugin 방식으로 설치할 수 있다. Docker 공식 문서 기준 Ubuntu와 Debian에서는 `docker-compose-plugin` 패키지를 설치한다. [2]

따라서 새로 설치할 때는 `docker-compose` 명령보다 `docker compose` 명령을 사용하는 plugin 방식을 기준으로 잡는 것이 좋다. Docker 공식 문서는 standalone Compose 설치 방식을 권장하지 않고, 하위 호환성 목적일 때만 사용하라고 설명한다. [3]

> 아래 명령어는 2026-05-14에 확인한 Docker 공식 문서를 기준으로 정리했다.

---

## 2. Docker와 Docker Compose 설치하기

먼저 Docker의 공식 GPG key와 `apt` 저장소를 등록한다. [1]

```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
```

그 다음 Docker Engine, Docker CLI, containerd, Buildx plugin, Compose plugin을 설치한다. [1]

```bash
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

위 명령에서 `docker-compose-plugin`을 함께 설치했기 때문에 Docker Compose는 다음처럼 `docker compose` 형식으로 실행한다. [2]

```bash
docker compose version
```

---

## 3. sudo 없이 docker 명령어 사용하기

Docker 공식 문서에 따르면 기본적으로 Docker daemon은 `root` 사용자로 실행되고, Docker socket도 `root`가 소유한다. 그래서 일반 사용자가 `sudo` 없이 `docker` 명령어를 사용하려면 사용자를 `docker` 그룹에 추가해야 한다. [4]

```bash
sudo usermod -aG docker $USER
newgrp docker
```

만약 `docker` 그룹이 없다는 오류가 나오면 그룹을 먼저 만든 뒤 다시 사용자를 추가한다. Docker 공식 문서는 `docker` 그룹을 만들고 사용자를 추가하는 절차를 안내한다. [4]

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

다만 Docker 공식 문서는 `docker` 그룹이 사용자에게 root 수준의 권한을 부여한다고 경고한다. 운영 환경에서는 이 보안 영향을 고려해야 한다. [4]

---

## 4. 잘 설치됐는지 확인하기

Docker CLI 버전은 다음 명령어로 확인할 수 있다.

```bash
docker -v
```

Docker Compose plugin 버전은 다음 명령어로 확인할 수 있다. Docker 공식 문서도 Compose plugin 설치 확인 명령으로 `docker compose version`을 제시한다. [2]

```bash
docker compose version
```

Docker Engine이 실제로 동작하는지 확인하려면 `hello-world` 이미지를 실행한다. Docker 공식 문서는 Ubuntu 설치 확인 단계에서 `sudo docker run hello-world`를 실행하라고 안내한다. [1]

```bash
docker run hello-world
```

권한 설정을 아직 하지 않았다면 다음처럼 `sudo`를 붙여 실행한다. [1][4]

```bash
sudo docker run hello-world
```

---

## 5. 참고: docker-compose 명령이 꼭 필요한 경우

예전 자료에서는 `/usr/local/bin/docker-compose`에 standalone binary를 내려받아 `docker-compose` 명령을 사용하는 방식이 자주 보인다.

하지만 Docker 공식 문서 기준 standalone Compose 설치 방식은 권장되지 않고, 하위 호환성을 위해서만 지원된다. 또한 standalone Compose는 현재 표준 문법인 `docker compose`가 아니라 `docker-compose` 문법을 사용한다. [3]

따라서 특별히 기존 스크립트가 `docker-compose` 명령에 의존하는 상황이 아니라면 `docker-compose-plugin`을 설치하고 `docker compose` 명령을 사용하는 편이 낫다. [2][3]

---

## 6. 정리

Ubuntu에서 Docker와 Docker Compose를 새로 설치할 때 핵심은 다음과 같다.

- Docker 공식 `apt` 저장소를 등록한다. [1]
- `docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-buildx-plugin`, `docker-compose-plugin`을 설치한다. [1]
- Docker Compose는 `docker compose` 명령으로 확인하고 실행한다. [2]
- `sudo` 없이 Docker를 쓰려면 사용자를 `docker` 그룹에 추가할 수 있지만, 이 그룹은 root 수준 권한을 부여한다. [4]
- standalone `docker-compose` 방식은 권장 설치 방식이 아니라 하위 호환성용 방식이다. [3]

---

## 참고 자료

확인일: 2026-05-14

[1] Docker Docs, Install Docker Engine on Ubuntu: <https://docs.docker.com/engine/install/ubuntu/>  
[2] Docker Docs, Install the Docker Compose plugin: <https://docs.docker.com/compose/install/linux/>  
[3] Docker Docs, Install the Docker Compose standalone (Legacy): <https://docs.docker.com/compose/install/standalone/>  
[4] Docker Docs, Linux post-installation steps for Docker Engine: <https://docs.docker.com/engine/install/linux-postinstall/>
