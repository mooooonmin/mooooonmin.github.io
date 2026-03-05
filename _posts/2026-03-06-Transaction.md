---
title: Transaction
date: 2026-03-06 00:00:00 +0900
---

## Transaction 개념

Transaction은 여러 데이터 변경 작업을 **하나의 묶음 단위로 처리하는 방식**.

예시 상황.  
A 계좌에서 B 계좌로 돈을 송금하는 경우.

- A 계좌에서 금액 차감
- B 계좌에 금액 증가

이 두 작업은 반드시 **함께 성공하거나 함께 실패해야 하는 구조**.

만약 A 계좌에서는 출금이 되었지만 B 계좌에 입금이 되지 않는 경우 **데이터 불일치 발생**.

이러한 문제를 방지하기 위한 처리 단위가 **Transaction**.

---

## Transaction 동작 흐름

1. Transaction 시작
2. 여러 SQL 작업 수행
3. 작업 성공 시 **COMMIT**
4. 오류 발생 시 **ROLLBACK**

---

## ACID 원칙

Transaction은 데이터 무결성을 보장하기 위해 **ACID 특성**을 만족해야 하는 구조.

| 특성 | 설명 |
|---|---|
| **Atomicity (원자성)** | Transaction에 포함된 작업은 **모두 실행되거나 모두 실행되지 않는 구조** |
| **Consistency (일관성)** | Transaction 실행 전후 데이터베이스 상태가 **일관된 규칙을 유지하는 상태** |
| **Isolation (고립성)** | 동시에 실행되는 Transaction 간 **서로의 작업에 간섭하지 않는 구조** |
| **Durability (지속성)** | 성공적으로 완료된 Transaction 결과는 **시스템 장애가 발생해도 유지되는 특성** |

---

## 동시성 제어 (Concurrency Control)

여러 Transaction이 **동시에 동일한 데이터를 수정하는 상황 발생 가능**.

이때 적절한 제어가 이루어지지 않으면 **갱신 손실(Lost Update)** 문제 발생 가능.

이를 방지하기 위한 DBMS 기능이 **동시성 제어**.

대표적인 방법.

- Lock 기반 제어
- Timestamp 기반 제어
- MVCC (Multi Version Concurrency Control)

Lock 방식의 경우

- 데이터를 수정하는 Transaction이 해당 데이터를 **잠금(Lock)** 상태로 변경
- 다른 Transaction의 접근 제한
- 작업 완료 후 **Unlock**

---

## COMMIT vs ROLLBACK

| 명령어 | 설명 |
|---|---|
| **COMMIT** | Transaction 작업을 정상 완료하고 변경 내용을 데이터베이스에 반영 |
| **ROLLBACK** | Transaction 수행 중 오류 발생 시 이전 상태로 되돌리는 작업 |

---

## 핵심 정리

> **Transaction**
> 
> - 데이터베이스 작업의 최소 처리 단위
> - 여러 SQL 작업을 하나의 논리적 작업으로 묶는 구조
>
> **ACID**
>
> - Atomicity : 전부 실행 또는 전부 실패
> - Consistency : 데이터 무결성 유지
> - Isolation : Transaction 간 독립성
> - Durability : 완료된 작업 영구 저장