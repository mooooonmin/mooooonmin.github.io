---
title: Multi Process vs Multi Thread
category: 1
date: 2026-03-23 00:00:00 +0900
---

## 1. Multi Process vs Multi Thread 개념

Multi Process와 Multi Thread는 **여러 작업을 동시에 수행하는 실행 구조** 의미.

두 방식 모두 동시성 기반 처리 구조이지만  
**자원 관리 방식과 실행 구조에서 차이 존재**.

---

## 2. Multi Process 특징

Multi Process는 **여러 개의 Process가 독립적으로 실행되는 구조** 의미.

각 Process는

- 독립적인 Memory 공간 사용
- 독립적인 실행 환경 유지

특징

- 높은 안정성
- Process 간 영향 최소화
- 자원 사용량 증가

---

## 3. Multi Thread 특징

Multi Thread는 **하나의 Process 내부에서 여러 Thread가 실행되는 구조** 의미.

각 Thread는

- Stack 영역 독립 사용
- Code / Data / Heap 영역 공유

특징

- 메모리 사용량 감소
- Context Switching 비용 감소
- 자원 공유 구조

---

## 4. Multi Process vs Multi Thread 비교

| 구분 | Multi Process | Multi Thread |
|---|---|---|
| 메모리 사용 | 많은 메모리 공간 사용 | 적은 메모리 공간 사용 |
| CPU 사용 | 높은 CPU 사용 | 상대적으로 효율적 |
| Context Switching | 느림 | 빠름 |
| 안정성 | 높음 (Process 간 독립) | 낮음 (Thread 간 영향 존재) |
| 자원 공유 | 어려움 (IPC 필요) | 쉬움 (Memory 공유) |

---

## 5. 성능 및 구조 차이

Multi Thread는 Multi Process 대비

- 메모리 공간 절약 구조
- 시스템 자원 효율적 사용 구조
- Context Switching 시 오버헤드 감소

또한

- Process 생성 시 발생하는 System Call 비용 감소
- Thread 간 통신 비용 감소

---

## 6. Multi Thread의 장점

- 메모리 사용량 감소
- 자원 공유를 통한 효율적인 실행 구조
- Context Switching 속도 빠름
- IPC 대비 통신 오버헤드 감소

---

## 7. Multi Thread의 단점

- Thread 간 자원 공유로 인한 동기화 문제 발생 가능
- Race Condition 발생 가능성
- 하나의 Thread 장애 시 전체 Process 영향 가능

---

## 8. Multi Process의 장점

- Process 간 독립성 보장
- 하나의 Process 장애가 다른 Process에 영향 없음
- 높은 안정성 구조

---

## 9. Multi Process의 단점

- Memory 사용량 증가
- Context Switching 비용 증가
- Process 간 통신 비용(IPC) 발생

---

## 핵심 정리

> **Multi Process**
>
> - 독립적인 Process 기반 실행 구조  
> - 높은 안정성  
> - 높은 자원 사용 비용
>
> **Multi Thread**
>
> - 하나의 Process 내에서 실행되는 Thread 기반 구조  
> - 메모리 및 자원 효율성 높음  
> - 동기화 문제 및 안정성 이슈 존재