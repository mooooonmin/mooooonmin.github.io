---
title: IP Address
category: i
date: 2026-06-11 00:00:20 +0900
tags: [linux, ip, public-ip, private-ip, curl, network]
---

## 1. IP 주소를 확인해야 하는 이유

IP 주소는 네트워크에서 특정 컴퓨터나 네트워크 인터페이스를 식별할 때 사용하는 주소이다.

예를 들어 아래와 같은 값은 IPv4 주소 형태이다.

```text
13.250.15.132
```

백엔드 서버와 통신하려면 서버가 실행 중인 컴퓨터의 주소를 알아야 한다.
브라우저나 `curl`로 서버에 요청을 보낼 때도 결국 서버 주소와 포트 번호를 함께 사용한다.

```bash
curl 13.250.15.132:8080
```

AWS 콘솔이나 AWS에서 제공하는 터미널 화면에서는 Public IP와 Private IP를 함께 보여주는 경우가 있다.
하지만 일반적인 Linux 터미널에서는 항상 IP 주소가 화면에 표시되는 것은 아니므로, 명령어로 확인하는 방법을 알아두는 것이 좋다.

---

## 2. Public IP와 Private IP

입문 단계에서는 Public IP와 Private IP를 아래처럼 구분하면 된다.

| 구분 | 의미 |
|---|---|
| Public IP | 외부 인터넷에서 접근할 때 사용하는 IP 주소 |
| Private IP | 같은 사설 네트워크 안에서 통신할 때 사용하는 IP 주소 |

AWS EC2 문서는 인스턴스가 시작될 때 서브넷의 IPv4 CIDR 범위에서 private IPv4 주소를 받는다고 설명한다. [1]
또한 public IPv4 주소는 Amazon의 public IPv4 주소 풀에서 인스턴스에 할당된다고 설명한다. [1]

즉 AWS EC2 기준으로 보면 Private IP는 VPC 내부 네트워크에서 사용하는 주소이고, Public IP는 외부 인터넷에서 접근할 때 사용하는 주소라고 이해할 수 있다.

이 개념이 처음에는 바로 와닿지 않아도 괜찮다.
서버 배포와 AWS 네트워크를 다루다 보면 Public IP와 Private IP의 차이를 더 구체적으로 이해하게 된다.

---

## 3. Public IP 주소 확인하기

현재 터미널에서 외부 인터넷으로 접속할 때 보이는 Public IP를 확인하려면 `curl`로 외부 서비스에 요청을 보낼 수 있다.

```bash
curl ifconfig.me
```

이 명령어는 `ifconfig.me` 주소로 GET 요청을 보내고, 응답으로 IP 주소를 출력한다.

ifconfig.me는 페이지 예시에서 `curl ifconfig.me` 또는 `curl ifconfig.me/ip` 요청이 IP 주소를 반환하는 형태를 보여준다. [2]

조금 더 명시적으로 IP 주소만 받고 싶다면 아래처럼 요청할 수도 있다.

```bash
curl ifconfig.me/ip
```

브라우저에서 아래 주소로 접속해도 Public IP 정보를 확인할 수 있다.

```text
https://ifconfig.me
```

다만 이 방법은 외부 서비스에 요청을 보내는 방식이다.
따라서 인터넷 연결이 되지 않거나, 해당 서비스에 접근할 수 없는 환경에서는 사용할 수 없다.

---

## 4. Private IP 주소 확인하기

Linux 서버 안에서 네트워크 인터페이스에 설정된 IP 주소를 확인할 때는 `ip` 명령어를 사용할 수 있다.

```bash
ip a
```

`ip a`는 보통 `ip address`를 줄여 쓰는 형태로 사용한다.
Linux man-pages의 `ip(8)` 문서는 `ip addr` 예시가 모든 네트워크 인터페이스에 할당된 주소를 보여준다고 설명한다. [3]
또한 `ip-address(8)` 문서는 `ip address` 명령이 주소와 그 속성을 표시한다고 설명한다. [4]

출력 예시는 아래와 비슷하다.

```text
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default
    inet 127.0.0.1/8 scope host lo

2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9001 qdisc mq state UP group default
    inet 172.31.10.25/20 brd 172.31.15.255 scope global dynamic eth0
```

여기서 `inet` 뒤에 있는 값이 IPv4 주소이다.

| 출력 부분 | 의미 |
|---|---|
| `lo` | 자기 자신을 가리키는 loopback 인터페이스 |
| `127.0.0.1/8` | loopback 주소 |
| `eth0` | 서버의 네트워크 인터페이스 예시 |
| `172.31.10.25/20` | 해당 인터페이스에 설정된 IPv4 주소와 prefix 길이 |

실습에서 주로 확인할 값은 `lo`가 아니라 `eth0` 같은 실제 네트워크 인터페이스의 `inet` 값이다.
AWS EC2라면 이 값이 Private IP로 보이는 경우가 많다.

---

## 5. ip a 출력에서 어떤 값을 봐야 할까?

`ip a` 출력에는 여러 줄이 나오기 때문에 처음에는 헷갈릴 수 있다.

입문 단계에서는 아래 순서로 확인하면 된다.

1. `lo` 인터페이스는 건너뛴다.
2. `eth0`, `ens5` 같은 실제 네트워크 인터페이스를 찾는다.
3. 해당 인터페이스 아래의 `inet` 값을 확인한다.

예를 들어 아래 출력이 있다고 해보자.

```text
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9001 qdisc mq state UP group default
    inet 172.31.10.25/20 brd 172.31.15.255 scope global dynamic eth0
```

여기서 Private IP 주소로 먼저 볼 값은 아래 부분이다.

```text
172.31.10.25
```

뒤의 `/20`은 네트워크 범위를 나타내는 prefix 길이이다.
지금 단계에서는 IP 주소 본문과 prefix 길이가 함께 표시될 수 있다는 정도만 알아두면 된다.

---

## 6. Public IP와 Private IP 확인 명령어 비교

두 명령어는 확인하는 대상이 다르다.

| 확인 대상 | 명령어 | 설명 |
|---|---|---|
| Public IP | `curl ifconfig.me` | 외부 서비스가 바라본 내 접속 IP 확인 |
| Private IP | `ip a` | Linux 서버의 네트워크 인터페이스 주소 확인 |

서버가 외부에서 접속되는지 확인할 때는 보통 Public IP를 사용한다.

```bash
curl [Public IP]:8080
```

같은 VPC나 같은 사설 네트워크 내부에서 통신할 때는 Private IP를 사용할 수 있다.

```bash
curl [Private IP]:8080
```

아직 서버 배포 경험이 많지 않다면 먼저 아래 명령어를 기억하면 된다.

```bash
curl ifconfig.me
```

이 명령어로 현재 터미널 환경에서 외부 인터넷에 보이는 Public IP를 빠르게 확인할 수 있다.

---

## 정리

IP 주소는 네트워크에서 컴퓨터나 네트워크 인터페이스를 식별하는 주소이다.

Public IP는 외부 인터넷에서 접근할 때 사용하는 주소이고, Private IP는 같은 사설 네트워크 안에서 통신할 때 사용하는 주소이다.

Public IP를 확인할 때는 아래 명령어를 사용할 수 있다.

```bash
curl ifconfig.me
```

Private IP를 확인할 때는 아래 명령어를 사용할 수 있다.

```bash
ip a
```

처음에는 Public IP 확인 방법을 먼저 익혀두면 서버 접속 테스트를 할 때 도움이 된다.

---

## 출처

[1] AWS Documentation, "Amazon EC2 instance IP addressing", 확인일: 2026-06-11, <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-instance-addressing.html>

[2] ifconfig.me, "What Is My IP Address?", 확인일: 2026-06-11, <https://ifconfig.me/>

[3] Linux man-pages, "ip(8) - Linux manual page", 확인일: 2026-06-11, <https://man7.org/linux/man-pages/man8/ip.8.html>

[4] Linux man-pages, "ip-address(8) - Linux manual page", 확인일: 2026-06-11, <https://man7.org/linux/man-pages/man8/ip-address.8.html>
