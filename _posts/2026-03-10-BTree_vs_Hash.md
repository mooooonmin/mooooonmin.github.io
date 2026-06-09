---
title: B+Tree Index vs Hash Index
category: b
date: 2026-03-10 08:00:00 +0900
tags: [database, index, btree, hash]
---

## 1. Index 자료구조 선택 문제

자료구조 관점에서 보면

- **Hash Table** 평균 시간 복잡도 : `O(1)`
- **B+Tree** 시간 복잡도 : `O(logN)`

이론적으로 Hash가 더 빠른 구조처럼 보이지만
대부분의 데이터베이스에서는 **Index 구조로 B+Tree를 사용**.

그 이유는 **데이터베이스의 실제 검색 패턴** 때문.

---

## 2. Hash Index 특징

Hash Index는 **특정 값 검색(Equal Search)**에 매우 빠른 구조.

### 특징

- 평균 검색 시간 `O(1)`
- 특정 값 조회에 매우 효율적
- 해시 함수 기반 데이터 접근

하지만 다음과 같은 제약 존재.

| 제한 사항 | 설명 |
|---|---|
| 범위 검색 불가능 | `<`, `>`, `BETWEEN` 같은 조건 비효율 |
| 정렬 불가능 | `ORDER BY` 처리 불리 |
| Range Scan 불가능 | 연속 데이터 탐색 어려움 |

예시

```sql
WHERE id = 10
```

→ 효율적

```sql
WHERE id > 10
```

→ 비효율적

이러한 이유로 **DB 검색 패턴과 맞지 않는 경우가 많음**.

---

## 3. B+Tree Index 특징

대부분의 RDBMS에서 사용하는 **기본 인덱스 구조**.

### 특징

- 항상 **정렬된 구조 유지**
- 검색 / 삽입 / 삭제 시간 복잡도 `O(logN)`
- **Range Query 처리에 매우 유리**

특히 다음 연산에서 강점 존재.

| 연산 | 설명 |
|---|---|
| 범위 검색 | `<`, `>`, `BETWEEN` |
| 정렬 | `ORDER BY` |
| 범위 탐색 | Range Scan |
| JOIN | 인덱스 기반 JOIN 가능 |

B+Tree는 **리프 노드가 연결된 구조**이기 때문에
범위 데이터 조회 시 **Sequential Access 가능**.

---

## 4. DB Index에서 B+Tree가 사용되는 이유

데이터베이스 검색은 단순한 **단일 값 조회보다 범위 검색이 훨씬 많음**.

대표적인 SQL 패턴

```sql
WHERE id = 10
WHERE id > 10
WHERE id BETWEEN 10 AND 20
ORDER BY id
```

이러한 조건을 효율적으로 처리하기 위해
**정렬 기반 구조인 B+Tree가 더 적합**.

---

## 5. B+Tree vs Hash Index 비교

| 구분 | B+Tree | Hash |
|---|---|---|
| 시간 복잡도 | `O(logN)` | `O(1)` (평균) |
| 정렬 | 가능 | 불가능 |
| 범위 검색 | 가능 | 비효율 |
| Range Scan | 가능 | 불가능 |
| DB Index 사용 | 매우 일반적 | 제한적 |

---

## 정리

> **Hash Index**
>
> - 단일 값 검색에 매우 빠른 구조
> - 평균 시간 복잡도 `O(1)`
> - 범위 검색에 부적합
>
> **B+Tree Index**
>
> - 정렬된 데이터 구조
> - Range Query 처리 가능
> - 대부분의 RDBMS에서 기본 인덱스 구조로 사용
