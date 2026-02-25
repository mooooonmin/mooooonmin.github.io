---
title: Stack으로 Queue 구현
date: 2026-02-25 09:00:00 +0900
---

## 1. 구현 원리 및 로직
서로 반대되는 성격의 Stack(LIFO) 2개를 조합하여 Queue(FIFO)의 선입선출 구조를 재현하는 방식.

* **instack**: 데이터 삽입(Enqueue)을 전담하는 스택.
* **outstack**: 데이터 추출(Dequeue)을 전담하는 스택.
* **핵심**: `instack`의 데이터를 `outstack`으로 옮기면 순서가 뒤집히며, 이때 `outstack`의 상단(Top)에는 가장 먼저 들어온 데이터가 위치하게 됨.



---

## 2. 주요 연산 절차

### ① Enqueue (데이터 추가)
* `instack`에 `push()` 연산을 수행하여 데이터를 단순 저장.

### ② Dequeue (데이터 추출)
1.  **outstack 확인**: `outstack`이 비어 있는지 우선 확인.
2.  **데이터 이전**: `outstack`이 비어 있다면, `instack`의 모든 데이터를 하나씩 `pop()` 하여 `outstack`에 `push()` 함.
    * 이 과정을 통해 데이터의 순서가 반전되어 Queue의 선입선출(FIFO) 조건 충족.
3.  **최종 추출**: `outstack`에서 `pop()`을 수행하여 데이터를 반환.

---

## 3. Python 코드 예시

```python
class Queue(object):
    def __init__(self):
        # 두 개의 스택 초기화
        self.instack = []
        self.outstack = []

    def enqueue(self, element):
        # instack에 데이터 추가
        self.instack.append(element)

    def dequeue(self):
        # outstack이 비어 있다면 instack의 데이터를 모두 옮김
        if not self.outstack:
            while self.instack:
                self.outstack.append(self.instack.pop())
        
        # outstack에서 데이터 추출
        return self.outstack.pop()
```

---

## 4. 시간 복잡도 분석 (Time Complexity)
작업 빈도와 데이터 이동 과정을 고려한 성능 분석 결과.

| 연산 | 시간 복잡도 | 비고 |
| :--- | :--- | :--- |
| **Enqueue** | O(1) | instack.push() 1회 수행 절차. |
| **Dequeue (Best)** | O(1) | outstack에 데이터가 존재하는 경우 즉시 반환. |
| **Dequeue (Worst)** | O(n) | outstack이 비어 있어 instack의 모든 데이터를 이동시키는 경우. |
| **Dequeue (평균)** | **Amortized O(1)** | 전체 데이터 이동 횟수를 평균적으로 계산한 효율성. |

---

## 💡 핵심요약
* **구현 방식**: 삽입 전용 스택(instack)과 추출 전용 스택(outstack)을 분리하여 논리적으로 순서를 반전시키는 기법.
* **성능 특징**: 개별 Dequeue는 최악의 경우 O(n)이지만, 전체적인 관점에서의 평균 비용은 **Amortized O(1)**로 매우 효율적.
* **결론**: Queue의 선입선출(FIFO) 원칙 유지를 위해 outstack이 비어있을 때만 데이터를 이전하는 것이 핵임.

---

## 💡 추가내용
> **Q. 왜 outstack이 비었을 때만 데이터를 옮겨야 하는가?**
> * outstack에 데이터가 남아 있는데 instack에서 새 데이터를 부으면 선입선출 순서가 어긋나는 현상 발생 가능.
> * 반드시 outstack을 완전히 비운 뒤에만 새로운 묶음을 이전해야 데이터 무결성 유지가 가능.

> **Q. 면접에서 이 질문의 의도는?**
> * 기본적인 자료구조의 특성(LIFO vs FIFO)을 활용하여 새로운 기능을 설계하는 문제 해결 능력을 평가하기 위함.
> * 특히 O(n)의 연산이 가끔 발생하더라도 전체적인 효율성이 O(1)로 수렴하는 **Amortized O(1)** 개념을 정확히 설명할 수 있는지 확인하는 것이 주된 목적.