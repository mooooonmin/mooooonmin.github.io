---
title: Chmod
category: c
date: 2026-06-04 00:00:00 +0900
tags: [linux, chmod, permission, file, directory, rwx]
---

## 1. `chmod`란?

`chmod`는 파일이나 디렉터리의 권한을 변경할 때 사용하는 명령어다.

```bash
chmod 777 script.sh
chmod 644 file.txt
chmod 755 secret.txt
```

GNU Coreutils 문서는 `chmod`를 파일의 접근 권한을 변경하는 명령어로 설명한다. [1]
권한은 문자 방식으로도 바꿀 수 있지만, 입문 단계에서는 숫자 세 자리 방식부터 익히면 이해하기 쉽다.

기본 형태는 아래와 같다.

```bash
chmod [숫자 세 자리] [권한 변경할 파일명]
```

---

## 2. 권한 숫자 이해하기

Linux 권한은 읽기, 쓰기, 실행 권한으로 나뉜다.
숫자 권한에서는 각 권한에 아래 숫자가 대응된다.

| 권한 | 의미 | 숫자 |
|---|---|---|
| `r` | 읽기(read) | `4` |
| `w` | 쓰기(write) | `2` |
| `x` | 실행(execute) | `1` |

GNU Coreutils 문서는 numeric mode에서 읽기, 쓰기, 실행 권한을 각각 `4`, `2`, `1` 값으로 더해 표현한다고 설명한다. [2]

예를 들어 `rwx` 권한은 아래처럼 계산한다.

```text
rwx = 4 + 2 + 1 = 7
```

`rw-` 권한은 실행 권한이 없으므로 아래처럼 계산한다.

```text
rw- = 4 + 2 + 0 = 6
```

`r--` 권한은 읽기 권한만 있으므로 아래처럼 계산한다.

```text
r-- = 4 + 0 + 0 = 4
```

---

## 3. 숫자 세 자리의 의미

`chmod`에서 사용하는 숫자 세 자리는 각각 다른 대상을 의미한다.

```text
chmod 755 file-name
      |||
      ||└─ 그 외 사용자(others)
      |└── 그룹(group)
      └─── 소유자(user)
```

| 자리 | 대상 |
|---|---|
| 첫 번째 숫자 | 소유자(user) |
| 두 번째 숫자 | 소유 그룹(group) |
| 세 번째 숫자 | 그 외 사용자(others) |

예를 들어 `755`는 아래 의미다.

| 대상 | 숫자 | 권한 |
|---|---|---|
| 소유자 | `7` | `rwx` |
| 그룹 | `5` | `r-x` |
| 그 외 사용자 | `5` | `r-x` |

따라서 `755`는 전체 권한으로 보면 `rwxr-xr-x`가 된다.

---

## 4. 예시 1: `chmod 777`

파일에 소유자, 그룹, 그 외 사용자 모두에게 모든 권한을 부여하고 싶다면 `777`을 사용한다.

```bash
chmod 777 file-name
```

`777`은 아래처럼 계산된다.

| 대상 | 계산 | 권한 |
|---|---|---|
| 소유자 | `4 + 2 + 1 = 7` | `rwx` |
| 그룹 | `4 + 2 + 1 = 7` | `rwx` |
| 그 외 사용자 | `4 + 2 + 1 = 7` | `rwx` |

결과 권한은 아래와 같다.

```text
rwxrwxrwx
```

`777`은 모든 사용자에게 읽기, 쓰기, 실행 권한을 주는 설정이다.
편하지만 위험할 수 있으므로 실제 운영 환경에서는 신중하게 사용해야 한다.

---

## 5. 예시 2: `chmod 644`

파일에 `rw-r--r--` 권한을 부여하고 싶다면 `644`를 사용한다.

```bash
chmod 644 file-name
```

`644`는 아래처럼 계산된다.

| 대상 | 계산 | 권한 |
|---|---|---|
| 소유자 | `4 + 2 + 0 = 6` | `rw-` |
| 그룹 | `4 + 0 + 0 = 4` | `r--` |
| 그 외 사용자 | `4 + 0 + 0 = 4` | `r--` |

결과 권한은 아래와 같다.

```text
rw-r--r--
```

일반 텍스트 파일이나 설정 파일에서 자주 볼 수 있는 권한 형태다.

---

## 6. 예시 3: `chmod 755`

파일이나 디렉터리에 `rwxr-xr-x` 권한을 부여하고 싶다면 `755`를 사용한다.

```bash
chmod 755 file-name
```

`755`는 아래처럼 계산된다.

| 대상 | 계산 | 권한 |
|---|---|---|
| 소유자 | `4 + 2 + 1 = 7` | `rwx` |
| 그룹 | `4 + 0 + 1 = 5` | `r-x` |
| 그 외 사용자 | `4 + 0 + 1 = 5` | `r-x` |

결과 권한은 아래와 같다.

```text
rwxr-xr-x
```

실행 파일이나 접근 가능한 디렉터리에서 자주 볼 수 있는 권한 형태다.

---

## 7. 권한 변경 확인하기

권한을 바꾼 뒤에는 `ls -l`로 결과를 확인한다.

```bash
chmod 644 file.txt
ls -l file.txt
```

예상 결과는 아래와 비슷하다.

```text
-rw-r--r-- 1 ubuntu ubuntu 0 Jun  4 09:00 file.txt
```

맨 앞의 `-`는 일반 파일을 의미하고, 그 뒤 `rw-r--r--`가 권한을 의미한다.

---

## 핵심 정리

- `chmod`는 파일이나 디렉터리 권한을 변경하는 명령어다.
- 숫자 권한에서 `r`은 `4`, `w`는 `2`, `x`는 `1`이다.
- 숫자 세 자리는 소유자, 그룹, 그 외 사용자 권한을 순서대로 의미한다.
- `chmod 777 file`은 `rwxrwxrwx` 권한을 부여한다.
- `chmod 644 file`은 `rw-r--r--` 권한을 부여한다.
- `chmod 755 file`은 `rwxr-xr-x` 권한을 부여한다.
- 권한 변경 후에는 `ls -l`로 결과를 확인하는 습관이 필요하다.

---

## 출처

- [1] GNU Coreutils Manual, `chmod` invocation - <https://www.gnu.org/software/coreutils/manual/html_node/chmod-invocation.html>
- [2] GNU Coreutils Manual, numeric modes - <https://www.gnu.org/s/coreutils/manual/html_node/Numeric-Modes.html>
- [3] GNU Coreutils Manual, file permissions - <https://www.gnu.org/software/coreutils/manual/html_node/File-permissions.html>
