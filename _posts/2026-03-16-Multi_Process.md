---
title: Multi process
category: 1
date: 2026-03-16 00:00:00 +0900
tags: [os, process, concurrency, multiprocessing]
---

## 1. Multi process 개념

**Multi process**란 **2개 이상의 Process가 동시에 실행되는 구조** 의미.

여기서 동시에 실행된다는 의미는 다음 두 가지 개념 포함.

- **동시성(Concurrency)**
- **병렬성(Parallelism)**

---

## 2. 동시성(Concurrency) vs 병렬성(Parallelism)

| 동시성 | 병렬성 |
|---|---|
| Single Core 환경 | Multi Core 환경 |
| 동시에 실행되는 것처럼 보이는 구조 | 실제로 동시에 실행되는 구조 |

**동시성**은 CPU Core가 하나일 때 여러 Process가 **짧은 시간 단위로 번갈아 실행되는 방식** 의미.

이를 **시분할 시스템(Time Sharing System)**이라고 함.

**병렬성**은 CPU Core가 여러 개 존재할 때 각각의 Core가 서로 다른 Process를 동시에 실행하는 구조 의미.

---

## 3. Multi process 구조

Multi process 환경에서는 여러 Process가 동시에 Memory에 적재되는 구조.

각 Process는 **자신만의 메모리 영역을 독립적으로 할당받는 구조**.

**하나의 CPU Core는 한 순간에 하나의 Process 또는 Thread만 실행 가능**.

하지만 CPU 처리 속도가 매우 빠르기 때문에 **수 ms 단위로 Process가 교체 실행되는 구조**.

이로 인해 사용자 입장에서는 **여러 프로그램이 동시에 실행되는 것처럼 보이는 현상 발생**.

이러한 방식이 **시분할 시스템(Time Sharing System)** 구조 의미.

---

## 4. 메모리 관리

여러 Process가 동시에 Memory에 적재되는 상황 발생.

이때 서로 다른 Process의 메모리 영역 침범 방지 필요.

이를 위해 운영체제가 다음 기능 수행.

- 각 Process의 메모리 영역 분리 관리
- Process가 자신의 메모리 영역에만 접근하도록 제어

즉 **프로세스 간 메모리 보호 구조 존재**.

---

## 5. CPU 연산과 Program Counter Register

CPU는 **PC(Program Counter) Register가 가리키는 명령어를 실행하는 구조**.

PC Register 역할

- 다음에 실행할 명령어 주소 저장
- CPU 실행 흐름 제어

Multi 프로세스 환경에서 동작 구조

1. Process1 실행 시 PC Register가 Process1 Code 영역 명령어 가리키는 상태
2. Process2 실행 시 PC Register가 Process2 Code 영역 명령어 가리키는 상태
3. CPU는 PC Register가 가리키는 명령어를 읽어 연산 수행

즉 **PC Register에 따라 실행 프로세스 변경 구조**.

---

## 6. Context

시분할 시스템에서는 Process가 CPU를 **아주 짧은 시간 동안 점유하는 구조**.

Process가 CPU를 다시 사용할 때 이전 실행 상태 정보 필요.

이러한 정보를 **Context**라고 함.

**Context 의미**

- 프로세스 실행 상태 전체 정보
- CPU Register 상태
- Program Counter
- 메모리 정보

Context 정보는 **PCB(프로세스 Control Block)**에 저장되는 구조.

---

## 7. PCB (프로세스 Control Block)

PCB는 **운영체제가 Process를 관리하기 위해 사용하는 자료구조** 의미.

PCB는 일반 사용자가 접근할 수 없는 **보호된 메모리 영역**에 저장되는 구조.

일부 운영체제에서는 **커널 Stack 영역에 위치**.

PCB에 포함되는 정보

| PCB 정보 | 설명 |
|---|---|
| 프로세스 State | new, running, waiting, halted 상태 정보 |
| 프로세스 Number | 프로세스 식별 번호 |
| Program Counter | 다음 실행 명령어 주소 |
| Registers | CPU Register 값 |
| 메모리 Limits | base register, limit register, page table 등 |
| 기타 정보 | CPU Scheduling 정보 등 |

---

## 8. Context Switch

**Context Switch**란 **한 Process에서 다른 Process로 CPU 제어권을 넘기는 과정** 의미.

Context Switch 수행 과정

1. 현재 실행 프로세스 상태를 **PCB에 저장**
2. 다음 실행 Process의 **PCB 정보 로드**
3. 저장된 Context 복구
4. CPU 실행 프로세스 변경

즉 **CPU가 실행하는 Process가 변경되는 과정** 의미.

---

## 핵심 정리

> **Multi 프로세스**
>
> - 여러 Process가 동시에 실행되는 구조
>
> **동시성**
>
> - Single Core 환경에서 시분할 방식 실행
>
> **병렬성**
>
> - Multi Core 환경에서 실제 동시 실행
>
> **Context**
>
> - 프로세스 실행 상태 정보
>
> **PCB**
>
> - 프로세스 관리 자료구조
>
> **Context Switch**
>
> - CPU 실행 프로세스 변경 과정

---

## 참고 자료

1. KOCW, 운영체제 강의자료  
   https://contents.kocw.or.kr/KOCW/document/2015/cup/weonsunghyun/3.pdf
2. University of Illinois Chicago, Operating Systems Notes, "Processes"  
   https://www.cs.uic.edu/~jbell/CourseNotes/OperatingSystems/3_Processes.html
3. University of Illinois Chicago, Operating Systems Notes, "CPU Scheduling"  
   https://www.cs.uic.edu/~jbell/CourseNotes/OperatingSystems/6_CPU_Scheduling.html
