---
title: TCP 3-way handshake
date: 2026-02-12 11:50:00 +0900
---

## 1. 3-way Handshake: 연결 수립 (Connection Setup)
TCP/IP 프로토콜을 통한 통신 전, 데이터의 정확한 전송을 위해 상대방 컴퓨터와 세션을 수립하는 절차.

* **정의**: TCP 연결을 초기화하여 양방향 통신 준비를 완료하는 과정.
* **목적**: 전송 계층 사이의 논리적 연결 설립 및 상호 확인.
* **특징**: HTTP 1.1 및 2.0 버전 통신의 기초 단계로 활용.



---

## 2. 3-way Handshake 상세 단계

<img src="/images/2026-02-12-TCP_3-way-handshake/3way handshake.001.jpeg" alt="3way" style="max-width:100%;"  />
클라이언트와 서버 간의 3단계 패킷 교환 절차.

1. **Step 1 (SYN)**: 클라이언트가 서버에 접속 요청을 의미하는 **SYN(Synchronize)** 패킷 전송.
2. **Step 2 (SYN+ACK)**: 서버가 요청을 수락하는 **ACK(Acknowledgment)**와 본인의 접속 요청인 **SYN** 패킷을 병합하여 발송.
3. **Step 3 (ACK)**: 클라이언트가 서버의 응답을 확인한 후 다시 **ACK** 패킷을 발송하여 최종 연결 완료.

---

## 3. TCP 통신의 전체 라이프사이클
연결 수립부터 종료까지의 3단계 흐름.

* **연결 수립 (Connection Setup)**: 3-way handshake를 통한 세션 생성.
* **데이터 전송 (Data Transfer)**: 수립된 세션을 통해 실제 데이터를 주고받는 단계.
* **연결 종료 (Connection Termination)**: 4-way handshake를 통한 세션 해제.

---

## 4. 4-way Handshake: 연결 종료 (Connection Termination)
<img src="/images/2026-02-12-TCP_3-way-handshake/3way handshake.002.jpeg" alt="4way" style="max-width:100%;"  />
수립된 TCP 연결을 양방향에서 독립적으로 안전하게 닫기 위한 절차.

* **특징**: 양방향 연결이 각각 개별적으로 닫히므로 4단계의 과정이 필수적.
* **상세 절차**:
    1. **Active Close**: 클라이언트가 종료 요청인 **FIN** 세그먼트 전송.
    2. **Passive Close (Response)**: 서버가 요청 확인 응답인 **ACK**를 보내고 프로세스에 종료 신호(EOF) 전달.
    3. **Passive Close (Finish)**: 서버 프로세스가 종료 준비를 마치면 서버 측에서 **FIN** 세그먼트를 클라이언트로 전송.
    4. **Termination**: 클라이언트가 서버의 FIN에 대한 **ACK**를 보내면 최종적으로 연결 종료.



---

## 💡 핵심요약

**Q. 3-way handshake의 존재 이유는?**
* ✅ TCP 통신의 핵심인 신뢰성을 보장하기 위해 사전에 양측의 통신 가능 상태를 확인하는 필수 과정.
* ✅ 주소창에 URL을 입력할 때마다 브라우저와 서버 사이에서 발생하는 가장 기초적인 네트워크 지식.

**Q. 4-way handshake가 필요한 이유는?**
* ✅ 클라이언트가 데이터를 다 보냈더라도 서버는 아직 보낼 데이터가 남아있을 수 있기 때문에, 양측의 동의하에 독립적으로 연결을 끊어야 하기 때문.
* ✅ 데이터 유실 없는 안전한 연결 해제를 보장하기 위한 메커니즘.