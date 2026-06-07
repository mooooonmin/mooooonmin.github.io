---
title: Redirection Append
category: r
date: 2026-06-08 00:00:20 +0900
tags: [linux, stdout, stderr, redirection, append, file-descriptor]
---

## 1. 덮어쓰기와 이어쓰기

표준 출력(stdout)과 표준 에러 출력(stderr)은 파일로 리다이렉션할 수 있다.
이때 파일에 저장하는 방식은 크게 두 가지다.

| 방식 | 의미 |
|---|---|
| 덮어쓰기 | 기존 파일 내용을 지우고 새 출력값을 저장한다. |
| 이어쓰기 | 기존 파일 내용을 유지하고 파일 끝에 새 출력값을 추가한다. |

명령어 출력을 파일에 저장할 때는 이 차이를 반드시 알아야 한다.
특히 로그처럼 기존 내용이 사라지면 안 되는 파일은 덮어쓰기가 아니라 이어쓰기를 사용해야 한다.

GNU Bash 매뉴얼은 `>` 리다이렉션이 파일을 쓰기 용도로 열고, 파일이 이미 있으면 0 크기로 자른다고 설명한다. 즉, 기존 내용이 삭제된다. [1]
반대로 `>>` 리다이렉션은 파일을 append 모드로 열고, 파일이 없으면 새로 만든다고 설명한다. [2]

---

## 2. 표준 출력 덮어쓰기

표준 출력을 파일에 저장할 때는 `>`를 사용한다.

```bash
pwd > result.txt
```

이 명령어는 `pwd`의 출력 결과를 `result.txt` 파일에 저장한다.
파일에 출력값이 잘 저장되었는지 확인해보자.

```bash
ls
cat result.txt
```

그런데 같은 명령어를 한 번 더 실행하면 기존 파일 내용이 유지되지 않는다.

```bash
pwd > result.txt
```

`>`는 기존 파일을 덮어쓴다.
따라서 `result.txt` 안에 있던 이전 내용은 사라지고, 새 출력값만 남는다.

---

## 3. 표준 출력 이어쓰기

기존 파일 내용을 유지하면서 표준 출력을 파일 끝에 추가하려면 `>>`를 사용한다.

먼저 기존 파일 내용을 확인한다.

```bash
cat result.txt
```

그 다음 `pwd` 결과를 기존 파일에 이어서 저장한다.

```bash
pwd >> result.txt
```

파일 내용을 다시 확인한다.

```bash
cat result.txt
```

이번에는 기존 내용이 사라지지 않고, 파일 끝에 새 출력값이 추가된다.

로그를 남길 때는 이런 방식이 중요하다.
서버를 운영하다 보면 이전 로그를 계속 보존하면서 새로운 로그를 아래쪽에 쌓아야 하는 경우가 많다.
이때 `>`를 사용하면 기존 로그가 사라질 수 있으므로, 이어쓰기가 필요하면 `>>`를 사용해야 한다.

---

## 4. 표준 에러 출력 덮어쓰기

표준 에러 출력(stderr)을 파일에 저장할 때는 `2>`를 사용한다.

```bash
ls abc 2> error.txt
```

`abc`라는 파일이나 디렉터리가 없다면 에러 메시지가 발생한다.
이 에러 메시지는 터미널 화면에 출력되지 않고 `error.txt` 파일에 저장된다.

파일 내용을 확인한다.

```bash
ls
cat error.txt
```

같은 명령어를 한 번 더 실행하면 기존 `error.txt` 내용은 덮어써진다.

```bash
ls abc 2> error.txt
```

`2>`도 `>`와 마찬가지로 파일을 덮어쓰는 방식이다.
차이는 리다이렉션 대상이 표준 출력이 아니라 표준 에러 출력이라는 점이다.

---

## 5. 표준 에러 출력 이어쓰기

표준 에러 출력을 기존 파일에 이어서 저장하려면 `2>>`를 사용한다.

먼저 기존 에러 로그 파일 내용을 확인한다.

```bash
cat error.txt
```

그 다음 에러 메시지를 기존 파일 끝에 추가한다.

```bash
ls abc 2>> error.txt
```

파일 내용을 다시 확인한다.

```bash
cat error.txt
```

한 번 더 다른 에러를 발생시켜보자.

```bash
ls xxxx 2>> error.txt
cat error.txt
```

`2>>`를 사용하면 기존 `error.txt` 내용은 사라지지 않고, 새 에러 메시지가 파일 끝에 추가된다.

---

## 6. 표준 출력과 표준 에러 출력 정리

표준 출력과 표준 에러 출력은 서로 다른 통로다.
따라서 덮어쓰기와 이어쓰기 기호도 각각 구분해서 사용한다.

| 대상 | 덮어쓰기 | 이어쓰기 |
|---|---|---|
| 표준 출력(stdout) | `>` | `>>` |
| 표준 에러 출력(stderr) | `2>` | `2>>` |

예를 들어 정상 결과를 계속 파일 끝에 쌓으려면 아래처럼 작성한다.

```bash
pwd >> result.txt
```

에러 메시지를 계속 파일 끝에 쌓으려면 아래처럼 작성한다.

```bash
ls abc 2>> error.txt
```

GNU Bash 매뉴얼은 파일 디스크립터 번호를 생략하고 `>` 계열 리다이렉션을 사용하면 표준 출력인 파일 디스크립터 `1`이 대상이 된다고 설명한다. [3]
따라서 `>> result.txt`는 `1>> result.txt`와 같은 의미로 이해할 수 있다.

---

## 핵심 정리

`>`는 기존 파일 내용을 덮어쓴다.
기존 파일 내용이 사라져도 괜찮을 때 사용한다.

```bash
pwd > result.txt
```

`>>`는 기존 파일 내용 뒤에 이어서 쓴다.
기존 출력값이나 로그가 사라지면 안 되는 경우 사용한다.

```bash
pwd >> result.txt
```

표준 에러 출력도 같은 방식으로 생각하면 된다.

```bash
ls abc 2> error.txt
ls abc 2>> error.txt
```

기존 파일의 내용이 사라지면 안 되는 경우에는 반드시 `>>` 또는 `2>>`를 사용해야 한다.

---

## 출처

[1] GNU Bash Manual, "Redirecting Output", <https://www.gnu.org/software/bash/manual/html_node/Redirections.html>

[2] GNU Bash Manual, "Appending Redirected Output", <https://www.gnu.org/software/bash/manual/html_node/Redirections.html>

[3] GNU Bash Manual, "Redirections", <https://www.gnu.org/software/bash/manual/html_node/Redirections.html>
