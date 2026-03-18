---
title: Multi Thread
category: 1
date: 2026-03-19 00:00:00 +0900
---

## 1. Thread 개념

**Thread**란 하나의 Process 내부에서 실행되는 **동작의 단위** 의미.

Thread는 Process 내부에서 **독립적인 기능을 수행하는 실행 흐름** 의미.

여기서 독립적인 기능 수행이란 **독립적으로 함수를 호출하고 실행하는 구조** 의미.

---

## 2. Multi Thread 개념

**Multi Thread**란 하나의 Process가 동시에 여러 작업을 수행할 수 있도록 하는 구조 의미.

즉, 하나의 Process 내부에 **여러 개의 Thread가 존재하는 구조** 의미.

이를 통해 하나의 프로그램이 여러 작업을 **동시에 처리하는 방식** 구현 가능.

---

## 3. Thread와 Memory 구조

Multi Thread 환경에서 각 Thread는 **Stack 영역을 제외한 나머지 Memory 영역을 공유하는 구조**.

공유되는 영역은 다음과 같음.

- Code 영역
- Data 영역
- Heap 영역

반면 **Stack 영역은 각 Thread가 독립적으로 할당받는 구조**.

즉 Thread의 Memory 구조는 다음과 같은 형태.


| 구분    | 공유 여부 |
| ----- | ----- |
| Code  | 공유    |
| Data  | 공유    |
| Heap  | 공유    |
| Stack | 독립    |


---

## 4. 독립적인 Stack Memory가 필요한 이유

Thread는 Process 내부에서 **독립적으로 함수를 호출하는 실행 단위** 의미.

함수 호출 과정에서는 다음 정보 저장 필요.

- 함수 인자(Parameter)
- Return Address
- 지역 변수(Local Variable)

이 정보들은 **Stack Memory 영역에 저장되는 구조**.

따라서 각 Thread가 서로 독립적으로 실행되기 위해서는  
각 Thread마다 **독립적인 Stack Memory 영역 필요**.

---

## 5. PC Register와 Thread

Multi Thread 환경에서는 **각 Thread마다 독립적인 PC(Program Counter) Register 필요**.

그 이유는 Thread 간에도 **Context Switch 발생**하기 때문.

PC Register에는 다음 정보 저장.

- 다음에 실행할 명령어 주소

Thread 실행이 중단되었다가 다시 이어서 실행되기 위해서는  
각 Thread가 **자신의 다음 실행 위치 정보 유지 필요**.

따라서 각 Thread마다 **독립적인 PC Register 필요 구조**.

---

## 6. Multi Thread 동작 구조

하나의 Process 내부에 여러 Thread가 존재하는 구조.

이때 각 Thread는

- Stack 영역 독립 사용
- Code / Data / Heap 영역 공유
- 독립적인 실행 흐름 유지

즉 하나의 Process 내부에서 여러 기능을 동시에 수행하는 실행 모델 의미.

---

## 7. Process와 Thread 비교


| 구분     | Process                       | Thread                  |
| ------ | ----------------------------- | ----------------------- |
| 개념     | 운영체제로부터 자원을 할당받는 작업 단위        | Process 내부에서 실행되는 동작 단위 |
| Memory | Code, Data, Heap, Stack 모두 독립 | Stack 제외 나머지 영역 공유      |
| 자원 할당  | 운영체제가 직접 자원 할당                | Process가 할당받은 자원 활용     |
| 실행 단위  | 프로그램 실행 단위                    | 함수 실행 흐름 단위             |


---

## 핵심 정리

> **Thread**
>
> - 하나의 Process 내부에서 실행되는 동작 단위
> - 독립적인 기능 수행 구조
>
> **Multi Thread**
>
> - 하나의 Process 내부에서 여러 Thread가 동시에 실행되는 구조
>
> **Memory 구조**
>
> - Code / Data / Heap 영역 공유
> - Stack 영역 독립 할당
>
> **독립 Stack 필요 이유**
>
> - 함수 인자, Return Address, 지역 변수 저장 필요
>
> **PC Register**
>
> - 각 Thread마다 독립적으로 필요한 구조
> - Thread 간 Context Switch 이후 실행 위치 복구 목적

