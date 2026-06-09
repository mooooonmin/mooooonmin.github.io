---
title: Segmentation
category: s
date: 2026-04-03 00:00:00 +0900
tags: [os, memory, segmentation]
---

## 1. Segmentation 개념

**Segmentation**은 프로세스의 논리 주소 공간을 **의미 단위의 가변 크기 영역(segment)**으로 나누어 관리하는 메모리 관리 방식 의미. [1][2][3]

운영체제는 프로그램을 하나의 단순한 연속 배열로 보기보다,
**Code, Data, Heap, Stack**처럼 서로 다른 역할을 가진 영역의 집합으로 볼 수 있음.
Segmentation은 이런 관점을 그대로 주소 공간 관리에 반영한 방식. [1][2]

중요한 점은 **프로세스 전체가 하나의 연속된 물리 메모리 공간에 놓일 필요는 없지만**,
**각 segment 자체는 일반적으로 연속된 물리 메모리 공간**에 배치된다는 점. [1][3]

---

## 2. 논리 주소와 세그먼트 테이블

Segmentation에서 논리 주소는 보통 다음 두 부분으로 표현.

- **세그먼트 번호(Segment Number)**
- **오프셋(Offset)**

세그먼트 번호는 **세그먼트 테이블(Segment Table)**의 인덱스로 사용됨. [1][2][3]

일반적으로 세그먼트 테이블의 각 항목은 다음 정보를 가짐.

- **Base**: 해당 segment가 시작하는 물리 주소
- **Limit / Length**: 해당 segment의 길이
- **Protection 정보**: 읽기 / 쓰기 / 실행 권한 등 [2][3]

주소 변환 과정은 다음과 같음.

1. CPU가 논리 주소 생성
2. 논리 주소를 **세그먼트 번호 + 오프셋**으로 분리
3. 세그먼트 번호로 세그먼트 테이블 조회
4. 오프셋이 해당 segment의 길이(limit) 안에 있는지 검사
5. 유효하면 **Base + Offset**으로 물리 주소 생성

---

## 3. Segmentation Fault와 보호

Segmentation에서는 세그먼트별 길이가 서로 다르므로,
하드웨어는 **오프셋이 해당 segment 범위를 넘는지 검사**해야 함. [1][3]

오프셋이 segment의 limit 이상이면 **잘못된 주소 접근**으로 판단되어 예외가 발생함.
운영체제 문맥에서는 이를 **segmentation violation** 또는 **segmentation fault**로 설명하는 경우가 많음. [3]

또한 segment마다 보호 비트를 둘 수 있으므로,
예를 들어 코드 영역에는 쓰기를 금지하는 식의 **접근 권한 제어**를 적용할 수 있음. [2]

---

## 4. Segmentation과 메모리 단편화

Segmentation은 segment 크기만큼 가변적으로 메모리를 할당하므로
**paging처럼 고정 크기 블록 단위 때문에 생기는 내부 단편화는 거의 없거나 매우 작음**. [4]

반면, 크기가 서로 다른 segment들이 적재되고 해제되는 과정이 반복되면
빈 공간이 잘게 나뉘어 **외부 단편화(External Fragmentation)**가 발생할 수 있음. [1][2][4]

즉,

- **내부 단편화**: 거의 없거나 매우 작음 [4]
- **외부 단편화**: 발생 가능 [1][2][4]

---

## 5. Paging과 차이

Segmentation과 Paging의 핵심 차이는 **나누는 기준**에 있음.

- **Paging**: 같은 크기의 page 단위로 나눔 [1]
- **Segmentation**: 의미 단위의 가변 크기 segment로 나눔 [1][2]

또한 단편화 측면에서도 차이가 있음.

- **Paging**: 외부 단편화는 없거나 매우 크게 완화되지만 내부 단편화가 발생 가능 [1]
- **Segmentation**: 내부 단편화는 거의 없지만 외부 단편화가 발생 가능 [1][4]

---

## 6. Paged Segmentation

**Paged Segmentation**은 segmentation을 기본으로 하되,
각 segment를 다시 page 단위로 나누어 관리하는 방식 의미. [5][6]

이 경우 논리 주소는 개념적으로 다음처럼 해석 가능.

- **세그먼트 번호**
- **세그먼트 내부의 페이지 번호**
- **페이지 내부 오프셋** [5][6]

이 방식은 segmentation의 **논리적 보호와 공유 장점**을 유지하면서,
segment를 다시 paging하므로 **외부 단편화 문제를 줄이거나 피하는 데 도움**을 줌. [2][5][6]

다만 주소 변환 구조가 더 복잡해지고,
segment table과 page table을 함께 사용해야 한다는 비용이 생김. [5][6]

---

## 정리

> **Segmentation**
>
> - 프로세스 주소 공간을 의미 단위의 가변 크기 segment로 나누는 방식
> - 프로세스 전체는 비연속적으로 배치될 수 있지만, 각 segment 자체는 연속적으로 적재되는 것이 일반적
>
> **주소 변환**
>
> - 논리 주소는 세그먼트 번호와 오프셋으로 구성
> - 세그먼트 테이블의 base와 limit를 이용해 물리 주소를 계산
>
> **단편화**
>
> - 내부 단편화는 거의 없거나 매우 작음
> - 외부 단편화는 발생 가능

---

## 출처

1. KOCW, 운영체제 강의자료
   https://contents.kocw.or.kr/KOCW/document/2015/cup/weonsunghyun/7.pdf
2. University of Illinois Chicago, Operating Systems Notes, "Segmentation" / "Paging"
   https://www.cs.uic.edu/~jbell/CourseNotes/OperatingSystems/8_MainMemory.html
3. University of Maryland, Computer Architecture Notes, "Virtual Memory II"
   https://www.cs.umd.edu/users/meesh/411/CA-online/chapter/289/index.html
4. University of Wisconsin-Madison, CS 537 Notes, "Segmentation"
   https://pages.cs.wisc.edu/~solomon/cs537-old/s07/segmentation.html
5. Gordon College, CS322 Memory Management, "Paged and Segmented Memory Organizations"
   https://www.cs.gordon.edu/courses/cs322/lectures/memory.html
6. University of California, Davis, "Segmentation and Paging Combined"
   https://nob.cs.ucdavis.edu/classes/ecs150-2008-02/handouts/memory/mm-segpag.html
7. UC Davis ECS 150 Memory Management Notes, "Paged Segmentation"
   https://nob.cs.ucdavis.edu/classes/ecs150-2008-02/notes/memory.pdf
