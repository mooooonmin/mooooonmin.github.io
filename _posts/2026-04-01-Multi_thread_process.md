---
title: Synchronization
category: cs
date: 2026-04-01 00:00:00 +0900
tags: [os, thread, synchronization, mutex, semaphore]
---

## 1. 동기화 문제 개념

동기화 문제란 여러 프로세스 또는 Thread가 공유 자원에 동시에 접근하여 잘못된 결과가 발생하는 문제 의미.

발생 원인

- 메모리 공유 구조
- 동시 접근 발생
- 실행 순서 비결정성

---

## 2. Race Condition

Race Condition이란 여러 Thread가 동일한 자원에 접근할 때 실행 순서에 따라 결과가 달라지는 현상 의미.

예시: count++

동작 과정

- 변수 값 읽기
- 값 증가
- 결과 저장

해당 과정이 원자적이지 않은 구조이기 때문에 값 손실 발생 가능.

---

## 3. 임계영역 (Critical Section)

임계영역이란 공유 자원에 접근하는 코드 영역 의미.

조건

- 동시에 하나의 Thread만 접근 가능한 구조
- 원자적 실행 보장 필요

구성

- Entry Section : 진입 요청
- Critical Section : 실제 작업
- Exit Section : 자원 반환

---

## 4. 동기화 해결 방법

대표적인 동기화 방법

- Mutex
- Semaphore

---

## 5. Mutex

Mutex는 Mutual Exclusion 의미.

특징

- 하나의 Thread만 접근 가능한 구조
- Lock 기반 제어 방식
- 경쟁 상태(Race Condition) 방지 목적

동작 흐름

- Lock 획득
- 임계영역 실행
- Lock 반환

예시 구조

- acquire()
- critical section
- release()

단점

- 구현 방식에 따라 대기 중인 스레드를 block시키지 않으면 Busy Waiting 발생 가능
- 잠금 경쟁이 심하면 성능 저하 가능

---

## 6. Semaphore

Semaphore는 공유 자원 접근 개수를 제어하는 동기화 기법 의미.

특징

- 여러 스레드 접근 가능 구조
- 자원 개수 기반 제어 방식

동작 원리

- S 값 : 사용 가능한 자원 개수
- S > 0 → 접근 가능
- S == 0 → 대기 상태

연산

- wait(S) → S 감소
- signal(S) → S 증가

예시 구조

- wait(S)
- critical section
- signal(S)

---

## 7. Binary Semaphore

Semaphore 값이 0 또는 1만 가지는 경우 의미.

- 상호 배제 용도로 사용할 수 있음
- 다만 일반적으로 **소유권 개념이 있는 Mutex와는 동일 개념으로 보지 않음**

---

## 8. Mutex vs Semaphore 비교

| 구분 | Mutex | Semaphore |
|---|---|---|
| 접근 가능 수 | 1개 | N개 |
| 목적 | 상호 배제 | 자원 개수 제어 |
| 구조 | Lock 기반 | 카운터 기반 |
| 관계 | Binary Semaphore와 유사 | 일반화된 동기화 기법 |

---

## 핵심 정리

> 동기화 문제
> 공유 자원 동시 접근으로 인한 오류 발생 구조
>
> Race Condition
> 실행 순서에 따라 결과가 달라지는 문제
>
> Mutex
> 하나의 Thread만 접근 가능한 Lock 기반 제어
>
> Semaphore
> 여러 스레드 접근 가능, 자원 개수 기반 제어

---

## 출처

1. KOCW, 운영체제 강의자료
   https://contents.kocw.or.kr/KOCW/document/2015/cup/weonsunghyun/5.pdf
2. University of Illinois Chicago, Operating Systems Notes, "Process Synchronization"
   https://www.cs.uic.edu/~jbell/CourseNotes/OperatingSystems/5_Synchronization.html
