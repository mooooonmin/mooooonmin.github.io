---
title: Curl API Request
category: c
date: 2026-06-11 00:00:10 +0900
tags: [linux, curl, api, http, get, post, put, spring-boot]
---

## 1. 서버 응답 확인이 필요한 이유

백엔드 서버를 실행한 뒤에는 서버가 실제로 요청에 응답하는지 확인해야 한다.

브라우저로 접속해서 확인할 수도 있고, API 테스트 도구를 사용할 수도 있다.
하지만 Linux 터미널에서는 `curl` 명령어만으로도 간단한 HTTP 요청을 바로 보낼 수 있다.

curl 공식 문서는 `curl`을 URL 문법을 사용해서 서버로 데이터를 전송하거나 서버에서 데이터를 받아오는 도구로 설명한다. [1]
또한 curl의 HTTP scripting 문서는 curl을 HTTP 요청에 사용할 수 있는 명령줄 도구로 설명한다. [2]

이번 글에서는 Spring Boot 서버가 잘 실행되고 있는지 빠르게 확인하는 용도로 `curl`을 사용하는 방법을 정리한다.

---

## 2. curl 기본 사용법

가장 기본적인 형태는 아래와 같다.

```bash
curl [요청할 URL]
```

예를 들어 아래 명령어는 `http://example.com/api/data` 주소로 요청을 보낸다.

```bash
curl http://example.com/api/data
```

Everything curl 문서는 단순히 URL만 지정해서 실행하면 HTTP 요청의 method가 `GET`이 된다고 설명한다. [3]
따라서 아래 명령어는 GET 요청을 보내는 명령어로 이해하면 된다.

```bash
curl http://example.com/api/data
```

입문 단계에서 서버 응답만 빠르게 확인하고 싶다면 이 GET 요청 형태를 가장 자주 사용한다.

---

## 3. 여러 HTTP method로 요청 보내기

HTTP API는 GET 외에도 POST, PUT, DELETE 같은 method를 사용할 수 있다.

Everything curl 문서는 HTTP 요청에는 method가 있고, 자주 쓰이는 method로 `GET`, `POST`, `HEAD`, `PUT`을 언급한다. [3]
또한 `-X` 또는 `--request` 옵션으로 요청 method를 지정할 수 있다고 설명한다. [4]

예시는 아래와 같다.

```bash
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "홍길동", "email": "gildong@example.com"}'
```

```bash
curl -X PUT http://localhost:8080/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "홍길동", "email": "gildong@example.com"}'
```

curl man page는 `-H, --header` 옵션을 서버로 보낼 추가 header를 지정하는 옵션으로 설명한다. [5]
또한 `-d, --data` 옵션을 HTTP POST 요청에서 서버로 데이터를 보내는 옵션으로 설명한다. [5]

위 명령어는 아래처럼 나누어 볼 수 있다.

| 부분 | 의미 |
|---|---|
| `-X POST` | HTTP method를 POST로 지정 |
| `-X PUT` | HTTP method를 PUT으로 지정 |
| `-H "Content-Type: application/json"` | 요청 본문 형식이 JSON임을 header로 전달 |
| `-d '{...}'` | 요청 body에 JSON 데이터 전달 |

다만 처음 실습 단계에서는 POST나 PUT 요청보다 단순 GET 요청을 먼저 익히는 편이 좋다.
GET 요청은 URL만 있으면 바로 보낼 수 있어 서버가 살아 있는지 확인하기 쉽다.

---

## 4. Spring Boot 서버가 내부에서 응답하는지 확인하기

Spring Boot 서버를 8080번 포트에서 실행했다면 같은 Linux 서버 안에서 아래처럼 요청할 수 있다.

```bash
curl localhost:8080
```

이 명령어는 현재 Linux 서버 자기 자신을 기준으로 8080번 포트에 요청을 보낸다.

예를 들어 이전 글에서 Spring Boot 서버를 아래처럼 실행했다고 해보자.

```bash
nohup java -jar linux-springboot-0.0.1-SNAPSHOT.jar &
```

그 다음 같은 서버에서 아래 명령어를 실행한다.

```bash
curl localhost:8080
```

응답 내용이 출력되면 Spring Boot 서버가 내부에서 요청을 받고 응답하고 있다고 볼 수 있다.
반대로 연결 실패 메시지가 나오면 서버가 실행 중인지, 포트가 맞는지, 애플리케이션 로그에 에러가 없는지 다시 확인해야 한다.

---

## 5. 외부 IP로 서버 응답 확인하기

EC2 같은 원격 서버에서 Spring Boot 서버를 실행했다면 외부에서 접속되는지도 확인해야 한다.

예를 들어 EC2 퍼블릭 IP가 `203.0.113.10`이고 Spring Boot 서버가 8080번 포트에서 실행 중이라면 아래처럼 요청할 수 있다.

```bash
curl 203.0.113.10:8080
```

위 IP 주소는 문서 예시용 주소이다.
실제 실습에서는 본인의 EC2 퍼블릭 IP 또는 서버 주소를 사용해야 한다.

내부 요청과 외부 요청은 확인하는 범위가 다르다.

| 명령어 | 확인하는 내용 |
|---|---|
| `curl localhost:8080` | 같은 서버 안에서 Spring Boot가 응답하는지 확인 |
| `curl [EC2 퍼블릭 IP]:8080` | 외부에서 서버로 접근할 수 있는지 확인 |

`localhost:8080`은 성공하는데 외부 IP 요청이 실패한다면, 서버 프로세스 자체보다 보안 그룹, 방화벽, 네트워크 설정을 확인해야 할 수 있다.

---

## 6. 잘못된 주소로 요청 보내보기

테스트할 때는 일부러 잘못된 포트로 요청해볼 수도 있다.

```bash
curl localhost:9999
```

9999번 포트에서 아무 서버도 실행 중이지 않다면 연결 실패 메시지가 출력될 수 있다.
이런 실패 결과를 한 번 확인해두면, 정상 응답과 실패 응답을 구분하는 데 도움이 된다.

예를 들어 아래 두 명령어를 비교해볼 수 있다.

```bash
curl localhost:8080
curl localhost:9999
```

첫 번째 명령어는 Spring Boot 서버가 실행 중인 포트로 요청을 보내는 예시이다.
두 번째 명령어는 서버가 실행되지 않은 포트로 요청을 보내는 예시이다.

---

## 7. 외부 API 서버 확인하기

`curl`은 내가 실행한 서버뿐 아니라 외부 API 서버를 확인할 때도 사용할 수 있다.

예를 들어 아래처럼 공개 샘플 API에 요청을 보낼 수 있다.

```bash
curl https://jsonplaceholder.typicode.com/posts
```

이 명령어는 해당 URL로 GET 요청을 보내고, 서버가 반환한 응답을 터미널에 출력한다.

외부 API를 테스트할 때도 처음에는 단순 GET 요청부터 확인하는 것이 좋다.
요청 body나 header가 필요한 API는 명령어가 길어질 수 있기 때문이다.

---

## 정리

`curl`은 터미널에서 URL로 요청을 보내고 응답을 확인할 수 있는 명령어이다.

서버가 내부에서 응답하는지 확인할 때는 아래처럼 요청한다.

```bash
curl localhost:8080
```

외부 IP로 접근되는지 확인할 때는 아래처럼 요청한다.

```bash
curl [EC2 퍼블릭 IP]:8080
```

외부 API 서버가 응답하는지 확인할 때는 아래처럼 요청할 수 있다.

```bash
curl https://jsonplaceholder.typicode.com/posts
```

처음에는 복잡한 POST, PUT 요청보다 단순 GET 요청으로 서버가 살아 있는지 빠르게 확인하는 용도로 사용하는 것이 좋다.

---

## 출처

[1] curl man page, "curl(1)", 확인일: 2026-06-11, <https://curl.se/docs/manpage.html>

[2] curl Documentation, "The Art Of Scripting HTTP Requests Using curl", 확인일: 2026-06-11, <https://curl.se/docs/httpscripting.html>

[3] Everything curl, "Method", 확인일: 2026-06-11, <https://everything.curl.dev/http/method.html>

[4] Everything curl, "Request method", 확인일: 2026-06-11, <https://everything.curl.dev/http/modify/method.html>

[5] curl man page, "Options", 확인일: 2026-06-11, <https://curl.se/docs/manpage.html>
