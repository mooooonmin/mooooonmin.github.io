---
title: Echo Print Text
category: e
date: 2026-06-12 00:00:20 +0900
tags: [linux, echo, stdout, terminal, shell-script]
---

## 1. echo 명령어를 배우는 이유

`echo`는 문자열을 터미널 화면에 출력할 때 사용하는 명령어이다.

처음에는 Java의 `System.out.println()`, JavaScript의 `console.log()`처럼 값을 화면에 찍어보는 명령어라고 이해하면 쉽다.
다만 Linux 관점에서 더 정확히 말하면, `echo`는 문자열을 표준 출력(stdout)으로 보내는 명령어이다.

표준 출력의 기본 목적지가 터미널 화면이기 때문에, 사용자는 `echo`가 터미널 화면에 문자열을 출력하는 것처럼 보게 된다.

GNU Coreutils 문서는 `echo`가 각 문자열을 표준 출력으로 쓰고, 문자열 사이에는 공백을 넣으며, 마지막 문자열 뒤에는 줄바꿈을 출력한다고 설명한다. [1]

---

## 2. echo 기본 사용법

기본 형태는 아래와 같다.

```bash
echo [출력할 문자열]
```

예를 들어 숫자를 출력해보자.

```bash
echo 1234
```

출력은 아래와 같다.

```text
1234
```

문자도 출력할 수 있다.

```bash
echo abcd
```

출력은 아래와 같다.

```text
abcd
```

`echo` 입장에서는 숫자처럼 보이는 값도 문자열처럼 출력한다.
즉 숫자와 문자를 구분해서 계산하는 명령어가 아니라, 전달받은 값을 표준 출력으로 보내는 명령어라고 이해하면 된다.

---

## 3. 띄어쓰기가 있는 문자열 출력하기

띄어쓰기가 있는 문자열도 출력할 수 있다.

```bash
echo USER1 USER2
```

출력은 아래와 같다.

```text
USER1 USER2
```

GNU Coreutils 문서는 `echo`가 전달받은 각 문자열 사이에 공백을 넣어 출력한다고 설명한다. [1]
따라서 여러 단어를 나누어 입력해도 화면에는 공백으로 구분되어 출력된다.

쌍따옴표로 묶어서 출력할 수도 있다.

```bash
echo "USER1 USER2"
```

출력은 아래와 같다.

```text
USER1 USER2
```

입문 단계에서는 띄어쓰기가 포함된 문장을 하나의 덩어리로 다루고 싶을 때 따옴표로 묶는다고 이해하면 된다.

---

## 4. echo와 표준 출력

`echo`는 화면에 글자를 직접 새기는 명령어라기보다, 문자열을 표준 출력으로 보내는 명령어이다.

아래 명령어를 실행하면 문자열이 터미널 화면에 보인다.

```bash
echo hello
```

출력은 아래와 같다.

```text
hello
```

이는 표준 출력의 기본 목적지가 터미널 화면이기 때문이다.

표준 출력은 파일로도 보낼 수 있다.

```bash
echo hello > result.txt
```

이 명령어는 `hello`를 터미널 화면에 출력하지 않고 `result.txt` 파일에 저장한다.

파일 내용을 확인한다.

```bash
cat result.txt
```

출력은 아래와 같다.

```text
hello
```

이 예시는 `echo`의 출력이 표준 출력으로 전달되고, 리다이렉션을 사용하면 그 목적지를 파일로 바꿀 수 있다는 점을 보여준다.

---

## 5. shell script에서 echo를 사용하는 이유

`echo`는 shell script를 작성할 때 자주 사용한다.

예를 들어 스크립트 실행 중 현재 어떤 단계까지 진행됐는지 화면에 보여주고 싶을 때 사용할 수 있다.

```bash
echo "서버 실행을 시작합니다."
echo "설정 파일을 확인합니다."
echo "서버 실행이 끝났습니다."
```

출력 예시는 아래와 같다.

```text
서버 실행을 시작합니다.
설정 파일을 확인합니다.
서버 실행이 끝났습니다.
```

이렇게 `echo`를 사용하면 사용자가 스크립트 진행 상황을 쉽게 확인할 수 있다.
그래서 shell script를 배우기 전에 `echo` 기본 사용법을 먼저 익혀두면 좋다.

---

## 6. 주의할 점

GNU Coreutils 문서는 shell alias나 shell built-in `echo` 때문에, 단순히 `echo`를 실행하면 문서에서 설명하는 GNU `echo`와 다른 기능이 실행될 수 있다고 설명한다. [1]

즉 실제 환경에서는 Bash 같은 shell이 제공하는 내장 `echo`가 실행될 수 있다.
입문 단계의 기본 출력 예시는 대부분 동일하게 동작하지만, 옵션이나 특수 문자 처리까지 깊게 들어가면 환경에 따라 차이가 날 수 있다.

이번 글에서는 가장 기본적인 사용법만 기억하면 된다.

```bash
echo 1234
echo abcd
echo "USER1 USER2"
```

---

## 정리

`echo`는 문자열을 표준 출력으로 보내는 명령어이다.
표준 출력의 기본 목적지가 터미널 화면이므로, 결과가 화면에 보인다.

```bash
echo 1234
echo abcd
echo "USER1 USER2"
```

띄어쓰기가 있는 문자열도 출력할 수 있고, 따옴표로 묶어 출력할 수도 있다.

```bash
echo "hello linux"
```

나중에 shell script를 작성할 때 진행 상황이나 메시지를 출력하는 용도로 자주 사용한다.

---

## 출처

[1] GNU Coreutils Manual, "echo invocation", 확인일: 2026-06-12, <https://www.gnu.org/software/coreutils/manual/html_node/echo-invocation.html>
