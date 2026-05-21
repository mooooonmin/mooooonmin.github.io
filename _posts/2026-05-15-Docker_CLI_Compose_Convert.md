---
title: Docker CLI와 Docker Compose 쉽게 변환하기
category: docker-kubernetes
date: 2026-05-15 00:00:10 +0900
tags: [docker, docker-compose, compose, cli, converter]
---

## 1. Docker CLI와 Docker Compose의 관계

Docker Compose는 Compose 파일이라는 YAML 설정 파일로 애플리케이션의 서비스를 구성하고, Compose CLI로 그 설정에 정의된 서비스를 생성하고 시작하는 방식으로 동작한다. Docker 공식 문서는 Compose 파일을 애플리케이션 서비스를 설정하는 YAML 파일로 설명한다. [1]

Compose 파일의 핵심은 `services`이다. Docker 공식 Compose file reference에 따르면 Compose 파일은 `services` 최상위 요소를 선언해야 하고, 각 서비스 정의에는 해당 서비스 컨테이너에 적용되는 설정이 들어간다. [2]

즉, `docker run` 명령어에 직접 적던 옵션들을 Compose 파일의 서비스 설정으로 옮겨 적을 수 있다.

예를 들어 다음 Docker CLI 명령어가 있다고 하자.

```bash
docker run -d --name webserver -p 80:80 nginx
```

이 명령은 다음과 같은 Compose 파일로 표현할 수 있다.

```yaml
services:
  webserver:
    container_name: webserver
    image: nginx
    ports:
      - "80:80"
```

위 예시에서 Docker CLI 옵션과 Compose 파일의 대응 관계는 다음과 같다.

| Docker CLI | compose.yml |
|---|---|
| `--name webserver` | `container_name: webserver` |
| `nginx` | `image: nginx` |
| `-p 80:80` | `ports: ["80:80"]` |
| `-d` | `docker compose up -d` 실행 옵션 |

---

## 2. Docker CLI에서 compose.yml로 변환

Docker CLI 명령어를 Compose 파일로 바꾸고 싶다면 Composerize를 사용할 수 있다.

Composerize의 npm 패키지 설명은 Composerize가 `docker run` 명령을 `compose.yaml` 파일로 변환한다고 설명한다. [3] Composerize GitHub 저장소의 README도 같은 기능을 설명하며, 기존 `compose.yaml`과 병합하는 기능도 언급한다. [4]

웹에서 바로 사용하려면 다음 사이트를 열면 된다.

```text
https://www.composerize.com/
```

예를 들어 아래 명령어를 Composerize에 넣으면 Compose 형식의 YAML을 얻을 수 있다.

```bash
docker run -d --name webserver -p 80:80 nginx
```

결과는 도구 버전과 설정에 따라 조금 달라질 수 있지만, 핵심적으로는 `image`, `container_name`, `ports` 같은 Compose 서비스 설정으로 변환된다. [3][4]

---

## 3. compose.yml에서 Docker CLI로 변환

반대로 Compose 파일을 Docker CLI 명령어로 바꾸고 싶다면 Decomposerize를 사용할 수 있다.

Decomposerize 사이트는 Docker Compose 파일을 `docker run` 명령으로 변환한다고 설명한다. 또한 입력 칸에 Docker Compose 파일 내용을 붙여넣고, 출력으로 실행 가능한 `docker run` 명령을 복사할 수 있다고 안내한다. [5]

웹에서 바로 사용하려면 다음 사이트를 열면 된다.

```text
https://www.decomposerize.com/
```

예를 들어 다음 Compose 파일을 Decomposerize에 넣는다고 하자.

```yaml
services:
  webserver:
    container_name: webserver
    image: nginx
    ports:
      - "80:80"
```

이 설정은 대략 다음 Docker CLI 명령어로 표현할 수 있다.

```bash
docker run --name webserver -p 80:80 nginx
```

다만 Compose와 Docker CLI는 실행 방식이 완전히 같지는 않다. Docker 공식 문서에 따르면 Compose는 `compose.yaml` 파일에 정의된 멀티 컨테이너 애플리케이션의 생명주기를 `docker compose` 명령과 하위 명령으로 관리한다. [1]

그래서 Decomposerize로 변환한 명령어는 학습용 또는 초안 작성용으로 사용하고, 실제 실행 전에는 빠진 옵션이 없는지 직접 확인하는 것이 좋다.

---

## 4. 변환 도구를 사용할 때 주의할 점

자동 변환 도구는 편리하지만, 결과가 항상 프로젝트 의도와 완전히 일치한다고 단정할 수는 없다.

특히 다음 항목은 변환 후 직접 확인하는 것이 좋다.

- 포트 매핑: `-p 80:80`이 Compose의 `ports`에 올바르게 들어갔는지 확인한다.
- 볼륨 마운트: `-v` 또는 `--volume` 값이 호스트 경로와 컨테이너 경로로 정확히 나뉘었는지 확인한다.
- 환경 변수: `-e` 또는 `--env` 값이 Compose의 `environment`에 맞게 들어갔는지 확인한다.
- 컨테이너 이름: `--name` 값이 `container_name` 또는 서비스 이름으로 의도대로 반영됐는지 확인한다.
- 백그라운드 실행: `-d`는 Compose 파일 안의 서비스 속성이 아니라 실행할 때 사용하는 `docker compose up -d` 옵션으로 이해한다.

---

## 핵심 정리

Docker CLI와 Docker Compose는 서로 다른 문법을 사용하지만, 컨테이너 실행에 필요한 이미지, 포트, 볼륨, 환경 변수 같은 설정은 서로 대응시켜 이해할 수 있다. [1][2]

- Docker CLI에서 Compose 파일로 바꿀 때는 Composerize를 사용할 수 있다. [3][4]
- Compose 파일에서 Docker CLI 명령어로 바꿀 때는 Decomposerize를 사용할 수 있다. [5]
- 자동 변환 결과는 그대로 실행하기 전에 직접 검토해야 한다.

---

## 출처

확인일: 2026-05-14

[1] Docker Docs, How Compose works: <https://docs.docker.com/compose/intro/compose-application-model/>
[2] Docker Docs, Define services in Docker Compose: <https://docs.docker.com/reference/compose-file/services/>
[3] npm, composerize package: <https://www.npmjs.com/package/composerize>
[4] GitHub, composerize/composerize: <https://github.com/composerize/composerize>
[5] Decomposerize: <https://www.decomposerize.com/>
