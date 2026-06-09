---
title: Create/Delete
category: c
date: 2026-06-01 00:00:00 +0900
tags: [linux, touch, mkdir, rm, file, directory, command]
---

## 1. 일반 파일 생성하기

Linux에서 빈 파일을 만들 때는 `touch` 명령어를 사용할 수 있다.

```bash
touch file-name
```

예를 들어 홈 디렉터리로 이동한 뒤 `jscode-file`이라는 빈 파일을 만들려면 아래처럼 입력한다.

```bash
cd ~
pwd
touch jscode-file
ls
```

GNU Coreutils 문서는 `touch`를 파일의 timestamp를 바꾸는 명령어로 설명한다.
또한 파일이 존재하지 않으면 빈 파일을 만든다고 설명한다. [1]

---

## 2. 디렉터리 생성하기

디렉터리를 만들 때는 `mkdir` 명령어를 사용한다.

```bash
mkdir directory-name
```

예를 들어 `apps`라는 디렉터리를 만들려면 아래처럼 입력한다.

```bash
mkdir apps
ls
ls -l
```

`mkdir`은 `make directory`의 줄임말로 이해하면 된다.
GNU Coreutils 문서도 `mkdir`을 디렉터리를 만드는 명령어로 설명한다. [2]

---

## 3. 파일 삭제하기

파일을 삭제할 때는 `rm` 명령어를 사용한다.

```bash
rm file-name
```

예를 들어 현재 디렉터리에 있는 `jscode-file`을 삭제하려면 아래처럼 입력한다.

```bash
ls
rm jscode-file
ls
```

`rm`은 `remove`의 줄임말로 이해하면 된다.
GNU Coreutils 문서는 `rm`을 파일이나 디렉터리를 제거하는 명령어로 설명한다. [3]

단, 일반적인 `rm` 명령어만으로는 디렉터리를 삭제할 수 없다.

```bash
ls
rm apps
```

디렉터리에 대해 위 명령어를 실행하면 오류가 발생할 수 있다.
디렉터리를 삭제하려면 recursive 옵션을 사용해야 한다.

---

## 4. 디렉터리 삭제하기

디렉터리를 삭제할 때는 `rm -r`을 사용할 수 있다.

```bash
rm -r directory-name
```

예를 들어 `apps` 디렉터리를 삭제하려면 아래처럼 입력한다.

```bash
rm -r apps
ls
```

`-r`은 `--recursive`와 같은 의미다.
GNU Coreutils 문서는 `-r`, `-R`, `--recursive` 옵션을 디렉터리와 그 안의 내용을 재귀적으로 삭제하는 옵션으로 설명한다. [3]

| 옵션 | 의미 |
|---|---|
| `-r` | 디렉터리 내부 항목까지 재귀적으로 삭제 |
| `--recursive` | `-r`과 같은 의미 |

---

## 5. 파일과 디렉터리를 같은 방식으로 삭제하기

실무에서는 일반 파일과 디렉터리를 구분하지 않고 삭제하기 위해 `rm -rf`를 사용하는 경우가 있다.

```bash
rm -rf target-name
```

예를 들어 테스트용 파일과 디렉터리를 만든 뒤 삭제해보면 아래와 같다.

```bash
touch testfile
mkdir testdir
ls

rm -rf testfile
ls

rm -rf testdir
ls
```

`rm -rf`는 `-r`과 `-f`를 함께 사용한 명령어다.

| 옵션 | 의미 |
|---|---|
| `-r` | 디렉터리 내부까지 재귀적으로 삭제 |
| `-f` | 존재하지 않는 파일을 무시하고, 확인 질문을 줄이는 force 옵션 |

GNU Coreutils 문서는 `-f`, `--force` 옵션을 존재하지 않는 파일을 무시하고 대부분의 확인 질문을 하지 않는 옵션으로 설명한다. [3]

---

## 6. `rm -rf`를 사용할 때 주의할 점

`rm -rf`는 편리하지만 위험한 명령어다.
삭제 대상 경로를 잘못 입력하면 의도하지 않은 파일이나 디렉터리까지 한꺼번에 삭제할 수 있다.

특히 아래처럼 변수가 비어 있거나 경로를 잘못 작성한 경우 큰 문제가 될 수 있다.

```bash
rm -rf $TARGET_DIR/*
```

따라서 `rm -rf`를 사용할 때는 먼저 `ls`로 삭제 대상을 확인하는 습관이 필요하다.

```bash
ls target-name
rm -rf target-name
```

입문 단계에서는 `rm -rf`를 외우는 것보다, `rm`이 삭제 명령이고 `-r`이 디렉터리 내부까지 삭제한다는 점을 먼저 정확히 이해하는 것이 중요하다.

---

## 정리

- `touch file-name`은 빈 파일을 만들 때 사용할 수 있다.
- `mkdir directory-name`은 디렉터리를 만들 때 사용한다.
- `rm file-name`은 일반 파일을 삭제할 때 사용한다.
- `rm -r directory-name`은 디렉터리와 내부 항목을 삭제할 때 사용한다.
- `rm -rf target-name`은 파일과 디렉터리를 구분하지 않고 삭제할 때 자주 사용되지만, 삭제 대상 확인이 필요하다.
- `rm` 계열 명령어는 삭제 결과를 쉽게 되돌릴 수 없으므로 실행 전에 경로를 반드시 확인해야 한다.

---

## 출처

- [1] GNU Coreutils Manual, `touch` invocation - <https://www.gnu.org/s/coreutils/manual/html_node/touch-invocation.html>
- [2] GNU Coreutils Manual, `mkdir` invocation - <https://www.gnu.org/s/coreutils/manual/html_node/mkdir-invocation.html>
- [3] GNU Coreutils Manual, `rm` invocation - <https://www.gnu.org/software/coreutils/rm>
