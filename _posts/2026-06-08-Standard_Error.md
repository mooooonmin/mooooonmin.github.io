---
title: Standard Error
category: s
date: 2026-06-08 00:00:10 +0900
tags: [linux, stderr, standard-error, stdout, redirection, file-descriptor]
---

## 1. 표준 에러 출력이란?

표준 에러 출력(stderr)은 명령어 실행 중 발생한 에러 메시지를 출력할 곳으로 보내는 통로다.

예를 들어 존재하지 않는 파일이나 디렉터리를 `ls`로 조회해보자.

```bash
ls abc
```

`abc`라는 파일이나 디렉터리가 없다면 아래와 비슷한 에러 메시지가 터미널 화면에 출력된다.

```text
ls: cannot access 'abc': No such file or directory
```

이 메시지는 명령어의 정상 실행 결과가 아니라 에러 메시지다.
따라서 표준 출력(stdout)이 아니라 표준 에러 출력(stderr)을 통해 전달된다.

Ubuntu manpage는 표준 입력, 표준 출력, 표준 에러를 표준 I/O 스트림으로 설명하고, 표준 에러는 error stream이라고 설명한다. [1]

---

## 2. `>`만 쓰면 에러 메시지가 파일에 저장되지 않는다

먼저 `>`를 사용해 `ls abc`의 결과를 파일에 저장해보자.

```bash
ls abc > list2.txt
```

그 다음 파일이 생성되었는지 확인한다.

```bash
ls
cat list2.txt
```

하지만 에러 메시지는 여전히 터미널 화면에 출력되고, `list2.txt`에는 저장되지 않는다.
이유는 `>`가 기본적으로 표준 출력(stdout)만 리다이렉션하기 때문이다.

`ls abc`에서 발생한 메시지는 정상 결과가 아니라 에러 메시지다.
그래서 표준 출력이 아니라 표준 에러 출력으로 전달된다.

즉, 아래 명령어는 표준 출력만 파일로 보낸다.

```bash
ls abc > list2.txt
```

표준 에러 출력은 그대로 터미널 화면에 연결되어 있으므로 에러 메시지가 화면에 보인다.

GNU Bash 매뉴얼은 리다이렉션에서 파일 디스크립터 번호를 지정하지 않으면 `>`가 표준 출력인 파일 디스크립터 `1`을 사용한다고 설명한다. [2]

---

## 3. 에러 메시지는 표준 에러 출력으로 전달된다

C 언어에서는 에러 메시지를 출력할 때 `perror()` 같은 함수를 사용할 수 있다.
Java에서는 `System.err.println()`, JavaScript에서는 `console.error()`와 비슷하게 생각할 수 있다.

```c
perror("error");
```

이런 에러 출력 함수는 정상 결과를 표준 출력으로 보내는 것이 아니라, 에러 메시지를 표준 에러 출력으로 보낸다.

표준 출력과 표준 에러 출력은 서로 다른 통로다.
기본 목적지는 둘 다 터미널 화면이기 때문에 평소에는 같은 화면에 출력되는 것처럼 보인다.
하지만 리다이렉션을 하면 차이가 드러난다.

| 통로 | 약어 | 파일 디스크립터 | 주로 전달하는 내용 |
|---|---|---|---|
| 표준 출력 | stdout | `1` | 정상 실행 결과 |
| 표준 에러 출력 | stderr | `2` | 에러 메시지 |

Ubuntu manpage는 프로그램 시작 시 `stdin`, `stdout`, `stderr`와 연결된 정수 파일 디스크립터가 각각 `0`, `1`, `2`라고 설명한다. [1]

---

## 4. 에러 메시지를 파일로 저장하기

표준 에러 출력을 파일로 보내려면 `2>`를 사용한다.

```bash
ls abc 2> list3.txt
```

이 명령어를 실행하면 에러 메시지가 터미널 화면에 출력되지 않고 `list3.txt` 파일에 저장된다.

파일 내용을 확인해보자.

```bash
cat list3.txt
```

그러면 아래와 비슷한 에러 메시지가 파일 안에 저장되어 있는 것을 확인할 수 있다.

```text
ls: cannot access 'abc': No such file or directory
```

여기서 `2`는 표준 에러 출력의 파일 디스크립터 번호다.
따라서 `2>`는 표준 에러 출력을 파일로 보내라는 의미다.

---

## 5. 정상 결과는 여전히 화면에 출력된다

이번에는 에러가 발생하지 않는 명령어에 `2>`를 붙여보자.

```bash
ls 2> list4.txt
```

`ls`의 정상 결과는 표준 출력(stdout)을 통해 전달된다.
그런데 위 명령어는 표준 에러 출력(stderr)만 `list4.txt`로 보낸다.

따라서 정상 결과는 파일에 저장되지 않고 터미널 화면에 그대로 출력된다.
`list4.txt`에는 에러 메시지가 없으므로 내용이 비어 있을 수 있다.

```bash
cat list4.txt
```

이 예시는 표준 출력과 표준 에러 출력이 독립적인 통로라는 점을 보여준다.

---

## 6. 표준 출력과 표준 에러를 서로 다른 파일로 보내기

표준 출력과 표준 에러 출력을 서로 다른 파일로 저장할 수도 있다.

정상 결과가 있는 경우는 아래처럼 실행한다.

```bash
ls > list.txt 2> error.txt
```

에러 메시지가 있는 경우는 아래처럼 실행한다.

```bash
ls xxx > list.txt 2> error.txt
```

이 명령어의 의미는 아래와 같다.

| 부분 | 의미 |
|---|---|
| `> list.txt` | 표준 출력을 `list.txt`로 보낸다. |
| `2> error.txt` | 표준 에러 출력을 `error.txt`로 보낸다. |

정상 결과와 에러 메시지를 분리해서 저장하고 싶을 때 이 방식을 사용할 수 있다.

---

## 7. 표준 출력과 표준 에러를 같은 파일로 보내기

표준 출력과 표준 에러 출력을 같은 파일로 저장하고 싶을 때가 있다.
이때 아래처럼 같은 파일을 각각 지정하는 방식은 피하는 것이 좋다.

```bash
ls > all.txt 2> all.txt
```

이 방식은 두 통로가 같은 파일을 따로 열어서 쓰기 때문에 출력이 섞이거나 덮어써지는 문제가 생길 수 있다.

대신 아래처럼 작성한다.

```bash
ls > all.txt 2>&1
```

이 명령어는 먼저 표준 출력을 `all.txt`로 보낸다.
그 다음 표준 에러 출력도 현재 표준 출력이 향하는 곳과 같은 곳으로 보낸다.

즉, 표준 출력과 표준 에러 출력이 모두 `all.txt`에 기록된다.

GNU Bash 매뉴얼은 `&>` 또는 `>&` 형식이 표준 출력과 표준 에러 출력을 함께 리다이렉션한다고 설명하고, `>word 2>&1` 방식과 의미가 같다고 설명한다. [3]

---

## 핵심 정리

표준 출력(stdout)은 명령어의 정상 실행 결과를 출력할 곳으로 보내는 통로다.
표준 출력은 기본적으로 파일 디스크립터 `1`을 사용한다.

표준 에러 출력(stderr)은 명령어 실행 중 발생한 에러 메시지를 출력할 곳으로 보내는 통로다.
표준 에러 출력은 파일 디스크립터 `2`를 사용한다.

표준 출력을 파일로 보내려면 `>`를 사용한다.

```bash
ls > list.txt
```

표준 에러 출력을 파일로 보내려면 `2>`를 사용한다.

```bash
ls abc 2> error.txt
```

표준 출력과 표준 에러 출력을 같은 파일로 보내려면 아래처럼 작성한다.

```bash
ls > all.txt 2>&1
```

---

## 출처

[1] Ubuntu Manpage, "stdin, stdout, stderr - standard I/O streams", <https://manpages.ubuntu.com/manpages/noble/man3/stdout.3.html>

[2] GNU Bash Manual, "Redirections", <https://www.gnu.org/software/bash/manual/html_node/Redirections.html>

[3] GNU Bash Manual, "Redirecting Standard Output and Standard Error", <https://www.gnu.org/software/bash/manual/html_node/Redirections.html>
