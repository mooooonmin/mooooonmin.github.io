---
title: Multi process vs Multi thread
category: cs
date: 2026-03-23 00:00:00 +0900
tags: [os, process, thread, comparison, concurrency]
---

## 1. Multi process vs Multi thread 개념

Multi Process와 Multi Thread는 **여러 작업을 동시에 수행하는 실행 구조** 의미.

두 방식 모두 동시성 기반 처리 구조이지만
**자원 관리 방식과 실행 구조에서 차이 존재**.

---

## 2. Multi 프로세스 특징

Multi Process는 **여러 개의 Process가 독립적으로 실행되는 구조** 의미.

각 Process는

- 독립적인 메모리 공간 사용
- 독립적인 실행 환경 유지

특징

- 높은 안정성
- 프로세스 간 영향 최소화
- 자원 사용량 증가

---

## 3. Multi 스레드 특징

Multi Thread는 **하나의 프로세스 내부에서 여러 Thread가 실행되는 구조** 의미.

각 Thread는

- Stack 영역 독립 사용
- Code / Data / Heap 영역 공유

특징

- 메모리 사용량 감소
- Context Switching 비용 감소
- 자원 공유 구조

---

## 4. Multi 프로세스 vs Multi 스레드 비교

| 구분 | Multi 프로세스 | Multi 스레드 |
|---|---|---|
| 메모리 사용 | 많은 메모리 공간 사용 | 적은 메모리 공간 사용 |
| 생성 / 전환 비용 | 상대적으로 큼 | 상대적으로 작음 |
| Context Switching | 느림 | 빠름 |
| 안정성 | 높음 (프로세스 간 독립) | 낮음 (스레드 간 영향 존재) |
| 자원 공유 | 어려움 (IPC 필요) | 쉬움 (메모리 공유) |

---

## 5. 성능 및 구조 차이

Multi Thread는 Multi 프로세스 대비

- 메모리 공간 절약 구조
- 시스템 자원 효율적 사용 구조
- Context Switching 시 오버헤드 감소

또한

- 프로세스 생성 시 발생하는 System Call 비용 감소
- 스레드 간 통신 비용 감소

---

## 6. Multi Thread의 장점

- 메모리 사용량 감소
- 자원 공유를 통한 효율적인 실행 구조
- Context Switching 속도 빠름
- IPC 대비 통신 오버헤드 감소

---

## 7. Multi Thread의 단점

- 스레드 간 자원 공유로 인한 동기화 문제 발생 가능
- Race Condition 발생 가능성
- 하나의 스레드 장애 시 전체 프로세스 영향 가능

---

## 8. Multi Process의 장점

- 프로세스 간 독립성 보장
- 하나의 프로세스 장애가 다른 Process에 영향 없음
- 높은 안정성 구조

---

## 9. Multi Process의 단점

- 메모리 사용량 증가
- Context Switching 비용 증가
- 프로세스 간 통신 비용(IPC) 발생

---

## 핵심 정리

> **Multi 프로세스**
>
> - 독립적인 프로세스 기반 실행 구조
> - 높은 안정성
> - 높은 자원 사용 비용
>
> **Multi 스레드**
>
> - 하나의 프로세스 내에서 실행되는 스레드 기반 구조
> - 메모리 및 자원 효율성 높음
> - 동기화 문제 및 안정성 이슈 존재

---

## 출처

1. KOCW, 운영체제 강의자료
   https://contents.kocw.or.kr/KOCW/document/2015/cup/weonsunghyun/3.pdf
2. University of Illinois Chicago, Operating Systems Notes, "Processes" / "Threads"
   https://www.cs.uic.edu/~jbell/CourseNotes/OperatingSystems/3_Processes.html
   https://www.cs.uic.edu/~jbell/CourseNotes/OperatingSystems/4_Threads.html
