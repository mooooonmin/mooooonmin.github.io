---
title: 쿠키(Cookie)와 세션(Session)의 차이점
category: c
date: 2026-02-10 00:00:10 +0900
tags: [network, http, cookie, session]
---

## 1. 쿠키와 세션을 사용하는 이유

- HTTP는 비연결성(Connectionless)과 비상태성(Stateless)이라는 특징을 가진다.
- 서버는 클라이언트의 상태를 유지하지 않기 때문에 누가 요청을 보냈는지 기억하지 못한다.
- 쿠키나 세션이 없다면 페이지를 이동할 때마다 다시 로그인해야 하는 불편함이 생긴다.

---

## 2. 쿠키 (Cookie)

<img src="/images/2026-02-10-Cookie_Session/쿠키.jpeg" alt="쿠키" width="1920" height="1080" loading="lazy" decoding="async" />

- **정의:** 클라이언트(브라우저) 로컬에 key-value 쌍 형태로 저장되는 작은 데이터 파일이다.
- **동작 방식:**
    - 서버가 응답 헤더에 `Set-Cookie` 속성을 담아 보내면 브라우저가 이를 저장함.
    - 이후 브라우저는 매 요청마다 헤더에 쿠키를 자동으로 담아서 서버에 전송함.
- **특징:**
    - 유효시간이 있다면 브라우저를 꺼도 로컬에 남아있음.
    - 서버 자원을 쓰지 않아 속도가 빠르지만, 클라이언트에 저장되므로 보안에 취약함.

---

## 3. 세션 (Session)

<img src="/images/2026-02-10-Cookie_Session/세션.jpeg" alt="세션" width="1920" height="1080" loading="lazy" decoding="async" />

- **정의:** 사용자 정보를 브라우저가 아닌 서버 측에서 관리하는 방식이다.
- **동작 방식:**
    - 서버는 클라이언트마다 고유한 `Session ID`를 부여하고, 이를 쿠키에 담아 클라이언트에 보냄.
    - 클라이언트는 쿠키에 이 ID만 들고 있다가 요청 시 서버에 보여줌.
- **특징:**
    - 실제 정보는 서버에 있으므로 쿠키보다 보안이 좋음.
    - 서버 자원(메모리 등)을 사용하기 때문에 사용자가 많아지면 서버 부하가 커질 수 있음.

---

## 4. 쿠키 vs 세션 비교

| 구분 | 쿠키 (Cookie) | 세션 (Session) |
|---|---|---|
| **저장 위치** | 클라이언트 (브라우저 로컬) | 서버 (Server) |
| **보안성** | 낮음 (데이터가 로컬에 노출됨) | 높음 (서버에서 관리함) |
| **속도** | 빠름 (서버 조회 과정 없음) | 상대적으로 느림 (서버 처리 필요) |
| **유효 기간** | 설정에 따라 브라우저 종료 후에도 유지 가능 | 브라우저 종료 시 삭제됨 (기본값) |

---

## 정리

**"세션이 보안도 좋은데 쿠키를 왜 씀?"**
- 세션은 서버 자원을 사용하므로 모든 정보를 세션으로 처리하면 서버 부하가 커질 수 있다.
- 보안 민감도가 낮은 장바구니 정보나 팝업 상태 정보는 쿠키로 처리하여 서버 자원을 절약할 수 있다.

**"쿠키의 실제 사용 예시는?"**
- 쇼핑몰 장바구니 기능
- 로그인 시 "아이디 저장" 또는 자동 로그인
- 팝업창의 "오늘 더 이상 이 창을 보지 않음" 설정

---

## 출처

1. MDN Web Docs, Using HTTP cookies
   https://developer.mozilla.org/docs/Web/HTTP/Guides/Cookies
2. RFC 6265, HTTP State Management Mechanism
   https://www.rfc-editor.org/rfc/rfc6265
3. OWASP Cheat Sheet Series, Session Management
   https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
