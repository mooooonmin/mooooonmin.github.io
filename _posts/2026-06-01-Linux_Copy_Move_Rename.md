---
title: Copy/Move
category: c
date: 2026-06-01 00:00:10 +0900
tags: [linux, cp, mv, copy, move, rename, file, directory]
---

## 1. 파일 복사하기

파일을 복사할 때는 `cp` 명령어를 사용한다.

```bash
cp source target
```

GNU Coreutils 문서는 `cp`를 파일을 복사하는 명령어로 설명한다. [1]
복사 대상이 디렉터리라면 원본 파일 이름을 유지한 채 그 디렉터리 안으로 복사된다. [1]

먼저 실습에 사용할 파일과 디렉터리를 만든다.

```bash
cd ~
touch a.txt
mkdir box
ls
```

---

## 2. 파일을 디렉터리로 복사하기

현재 디렉터리에 있는 `a.txt`를 `box` 디렉터리 안으로 복사하려면 아래처럼 입력한다.

```bash
cp a.txt ./box
cd box
ls
```

복사된 파일을 지우려면 아래처럼 입력한다.

```bash
rm -rf a.txt
ls
```

상대 경로 대신 절대 경로를 사용해도 된다.

```bash
cd ..
cp a.txt /home/ubuntu/box
cd box
ls
rm -rf a.txt
ls
```

현재 사용자의 홈 디렉터리가 `/home/ubuntu`라면 위 명령어는 `a.txt`를 `/home/ubuntu/box` 안으로 복사한다.

---

## 3. 파일 이름을 바꿔 복사하기

`cp`의 두 번째 인자에 새 파일명을 적으면, 원본 파일을 새 이름으로 복사할 수 있다.

```bash
cd ..
cp a.txt b.txt
ls
rm -rf b.txt
```

`b.txt`와 `./b.txt`는 현재 디렉터리 기준으로 같은 경로다.

```bash
cp a.txt ./b.txt
ls
rm -rf b.txt
```

다른 디렉터리 안에 새 이름으로 복사할 수도 있다.

```bash
cp a.txt ./box/b.txt
cd box
ls
rm -rf b.txt
```

정리하면 파일 복사는 아래처럼 이해하면 된다.

| 명령어 | 의미 |
|---|---|
| `cp a.txt ./box` | `a.txt`를 `box` 디렉터리 안으로 복사 |
| `cp a.txt b.txt` | `a.txt`를 현재 디렉터리에 `b.txt`라는 이름으로 복사 |
| `cp a.txt ./box/b.txt` | `a.txt`를 `box` 디렉터리 안에 `b.txt`라는 이름으로 복사 |

---

## 4. 디렉터리 복사하기

디렉터리를 복사할 때는 `cp -r`을 사용한다.

```bash
cp -r source-directory target-directory
```

`-r`은 `--recursive`와 같은 의미다.
GNU Coreutils 문서는 `--recursive` 옵션을 디렉터리를 재귀적으로 복사하는 옵션으로 설명한다. [2]

`-r` 옵션 없이 디렉터리를 복사하려고 하면 오류가 발생할 수 있다.

```bash
cd ~
cp box box2
```

디렉터리를 복사하려면 아래처럼 입력한다.

```bash
cp -r box box2
ls
```

위 명령어는 `box` 디렉터리를 현재 경로에 `box2`라는 이름으로 복사한다.

---

## 5. 파일과 디렉터리 이동하기

파일이나 디렉터리를 이동할 때는 `mv` 명령어를 사용한다.

```bash
mv source target
```

GNU Coreutils 문서는 `mv`를 파일을 이동하거나 이름을 변경하는 명령어로 설명한다. [3]
마지막 인자가 디렉터리라면 원본 파일이나 디렉터리가 그 디렉터리 안으로 이동한다. [3]

예를 들어 `a.txt`를 `box` 디렉터리 안으로 이동하려면 아래처럼 입력한다.

```bash
cd ~
mv a.txt ./box
```

디렉터리도 같은 방식으로 이동할 수 있다.

```bash
mv box2 ./box
```

이동 결과는 `box` 디렉터리 안에서 확인할 수 있다.

```bash
cd box
ls
```

---

## 6. 파일과 디렉터리 이름 변경하기

`mv`는 이동뿐 아니라 이름 변경에도 사용한다.
같은 디렉터리 안에서 `mv 기존이름 새이름` 형태로 입력하면 이름이 바뀐다.

```bash
cd ~
mv box new-box
ls
```

위 명령어는 `box`라는 디렉터리 이름을 `new-box`로 변경한다.

`mv`는 대상 위치에 따라 이동과 이름 변경처럼 보일 수 있다.
핵심은 원본 경로를 대상 경로로 옮긴다는 점이다.

| 명령어 | 의미 |
|---|---|
| `mv a.txt ./box` | `a.txt`를 `box` 디렉터리 안으로 이동 |
| `mv box2 ./box` | `box2` 디렉터리를 `box` 디렉터리 안으로 이동 |
| `mv box new-box` | `box` 이름을 `new-box`로 변경 |

---

## 핵심 정리

- `cp source target`은 파일을 복사할 때 사용한다.
- `cp a.txt b.txt`는 `a.txt`를 `b.txt`라는 이름으로 복사한다.
- `cp -r source-directory target-directory`는 디렉터리를 복사할 때 사용한다.
- `mv source target`은 파일이나 디렉터리를 이동할 때 사용한다.
- `mv old-name new-name`은 파일이나 디렉터리 이름을 변경할 때 사용한다.
- `cp`는 원본을 남기고 복사본을 만들지만, `mv`는 원본 위치를 옮기거나 이름을 바꾼다.

---

## 출처

- [1] GNU Coreutils Manual, `cp` invocation - <https://www.gnu.org/software/coreutils/cp>
- [2] GNU Coreutils Manual, `cp --recursive` option - <https://www.gnu.org/s/coreutils/manual/html_node/cp-invocation.html>
- [3] GNU Coreutils Manual, `mv` invocation - <https://www.gnu.org/software/coreutils/mv>
