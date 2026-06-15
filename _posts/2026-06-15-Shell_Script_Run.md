---
title: Shell Script Run
category: s
date: 2026-06-15 00:00:00 +0900
tags: [linux, shell-script, bash, chmod, execute, permission]
---

## 1. 쉘 스크립트를 사용하는 이유

쉘 스크립트(shell script)는 여러 Linux 명령어를 파일에 순서대로 작성해두고 한 번에 실행하기 위한 파일이다.

예를 들어 아래 명령어를 매번 직접 입력해야 한다고 해보자.

```bash
echo 1
echo 2
echo 3
```

명령어가 몇 개 없을 때는 직접 입력해도 괜찮다.
하지만 명령어가 많아지거나 같은 작업을 반복해야 한다면 파일로 만들어두는 편이 편하다.

Bash 매뉴얼은 Bash가 표준 입력, 문자열, 파일에서 읽은 명령어를 실행하는 command language interpreter라고 설명한다. [1]
즉 Bash는 파일에 작성된 명령어도 읽어서 실행할 수 있다.

---

## 2. 파일명을 .sh로 끝나게 작성하기

먼저 쉘 스크립트 파일을 만든다.

```bash
vi first.sh
```

파일명은 반드시 `.sh`로 끝나야만 실행되는 것은 아니다.
하지만 파일명만 보고 쉘 스크립트 파일인지 알아보기 쉽게 `.sh` 확장자를 붙이는 것이 좋다.

예를 들어 아래 파일명은 쉘 스크립트 파일이라는 의도를 바로 알 수 있다.

```text
first.sh
deploy.sh
start-server.sh
```

---

## 3. 첫 줄에 #!/bin/bash 작성하기

`first.sh` 파일 첫 줄에 아래 내용을 작성한다.

```bash
#!/bin/bash
```

이 줄은 이 스크립트를 어떤 interpreter로 실행할지 알려주는 역할을 한다.

Bash 매뉴얼은 스크립트 첫 줄이 `#!`로 시작하면 나머지 줄이 프로그램의 interpreter를 지정한다고 설명한다. [2]
또한 Bash 스크립트는 Bash가 `/bin`에 설치되어 있다는 가정 아래 `#! /bin/bash`로 시작하는 경우가 많다고 설명한다. [2]

Linux man-pages의 `execve(2)`도 interpreter script가 execute 권한을 가진 텍스트 파일이며, 첫 줄이 아래 형태라고 설명한다. [3]

```text
#!interpreter [optional-arg]
```

입문 단계에서는 먼저 아래처럼 기억하면 된다.

```bash
#!/bin/bash
```

쉘 스크립트 파일 첫 줄에는 위 코드를 작성해 Bash로 실행되게 한다.

---

## 4. 실행하고 싶은 명령어 작성하기

이제 자동으로 실행시키고 싶은 명령어를 순서대로 작성한다.

```bash
#!/bin/bash

echo 1
echo 2
echo 3
```

파일을 저장하고 나온다.

`echo`는 문자열을 표준 출력으로 보내는 명령어이다.
따라서 위 스크립트를 실행하면 `1`, `2`, `3`이 순서대로 터미널 화면에 출력된다.

---

## 5. 쉘 스크립트 파일 실행하기

현재 디렉터리에 있는 `first.sh` 파일을 실행하려면 아래처럼 입력한다.

```bash
./first.sh
```

여기서 `./`는 현재 디렉터리에 있는 파일을 실행하겠다는 의미로 볼 수 있다.

하지만 처음 실행하면 아래와 같은 에러가 날 수 있다.

```text
Permission denied
```

이 에러가 발생하는 이유를 권한 관점에서 확인해보자.

---

## 6. Permission denied 원인 확인하기

파일 권한은 `ls -l`로 확인할 수 있다.

```bash
ls -l
ls -l first.sh
```

예를 들어 아래와 같은 결과가 나왔다고 해보자.

```text
-rw-rw-r-- 1 ubuntu ubuntu 32 Jun 15 10:00 first.sh
```

권한 부분은 아래 값이다.

```text
-rw-rw-r--
```

이 권한을 나누어 보면 아래와 같다.

| 대상 | 권한 | 의미 |
|---|---|---|
| 소유자 | `rw-` | 읽기, 쓰기 가능, 실행 불가 |
| 그룹 | `rw-` | 읽기, 쓰기 가능, 실행 불가 |
| 그 외 사용자 | `r--` | 읽기 가능, 실행 불가 |

일반 파일에서 `x` 권한은 파일을 실행할 수 있는 권한이다.
`first.sh`를 `./first.sh` 형태로 실행하려면 실행 권한이 필요하다.

위 예시에서는 소유자인 `ubuntu` 사용자에게도 `x` 권한이 없다.
그래서 `Permission denied`가 발생할 수 있다.

---

## 7. 실행 권한 복습하기

일반 파일에서 `r`, `w`, `x` 권한은 아래처럼 이해하면 된다.

| 권한 | 이름 | 일반 파일에서 의미 |
|---|---|---|
| `r` | read | 파일 내용을 읽을 수 있음 |
| `w` | write | 파일 내용을 수정할 수 있음 |
| `x` | execute | 파일을 실행할 수 있음 |

권한은 보통 `r`, `w`, `x` 순서로 표시한다.
권한이 없으면 `-`로 표시한다.

예를 들어 `rw-`는 읽기와 쓰기는 가능하지만 실행은 불가능하다는 뜻이다.

```text
rw-
```

---

## 8. chmod로 실행 권한 부여하기

실행 권한을 부여하려면 `chmod`를 사용한다.

숫자 방식으로는 아래처럼 설정할 수 있다.

```bash
chmod 775 first.sh
```

`775`는 아래와 같은 권한을 의미한다.

| 대상 | 숫자 | 권한 |
|---|---|---|
| 소유자 | `7` | `rwx` |
| 그룹 | `7` | `rwx` |
| 그 외 사용자 | `5` | `r-x` |

하지만 실행 권한만 추가하고 싶을 때는 더 간단하게 쓸 수 있다.

```bash
chmod +x first.sh
```

GNU Coreutils 문서는 `chmod`가 지정한 파일의 접근 권한을 변경한다고 설명한다. [4]
또한 symbolic mode 형식에서 권한 변경 연산자로 `+`를 사용할 수 있고, 권한 문자로 `r`, `w`, `x` 등을 사용할 수 있다고 설명한다. [5]

따라서 `chmod +x first.sh`는 `first.sh`에 실행 권한을 추가하는 명령어로 이해하면 된다.

권한이 잘 적용됐는지 확인한다.

```bash
ls -l first.sh
```

예상 결과는 아래와 비슷하다.

```text
-rwxrwxr-x 1 ubuntu ubuntu 32 Jun 15 10:00 first.sh
```

이제 소유자, 그룹, 그 외 사용자 권한에 `x`가 포함되어 있다.

---

## 9. 다시 쉘 스크립트 실행하기

실행 권한을 부여한 뒤 다시 실행한다.

```bash
./first.sh
```

출력은 아래와 비슷하다.

```text
1
2
3
```

스크립트 파일 안에 작성한 명령어가 위에서 아래로 순서대로 실행된 것이다.

즉 쉘 스크립트는 여러 Linux 명령어를 파일 하나에 작성해두고, 그 파일을 실행해서 명령어들을 순서대로 처리하게 만드는 방법이다.

---

## 10. 쉘 스크립트의 역할

쉘 스크립트는 반복 작업을 자동화할 때 많이 사용한다.

예를 들어 아래 작업을 매번 직접 입력해야 한다고 해보자.

```bash
cd ~/linux-springboot/build/libs
nohup java -jar linux-springboot-0.0.1-SNAPSHOT.jar >> result.log 2>&1 &
tail -f result.log
```

이런 명령어들을 스크립트 파일에 작성해두면, 파일 하나를 실행하는 것만으로 여러 명령어를 순서대로 실행할 수 있다.

입문 단계에서는 아래 흐름을 먼저 기억하면 된다.

1. `.sh` 파일을 만든다.
2. 첫 줄에 `#!/bin/bash`를 작성한다.
3. 실행할 명령어를 순서대로 작성한다.
4. `chmod +x 파일명`으로 실행 권한을 부여한다.
5. `./파일명`으로 실행한다.

---

## 정리

쉘 스크립트는 여러 Linux 명령어를 파일에 작성해두고 순서대로 실행하기 위한 파일이다.

```bash
vi first.sh
```

파일 내용은 아래처럼 작성한다.

```bash
#!/bin/bash

echo 1
echo 2
echo 3
```

실행 권한을 부여한다.

```bash
chmod +x first.sh
```

스크립트를 실행한다.

```bash
./first.sh
```

`Permission denied`가 발생하면 `ls -l first.sh`로 권한을 확인하고, 실행 권한 `x`가 있는지 확인해야 한다.

---

## 출처

[1] Linux man-pages, "bash(1) - Linux manual page", 확인일: 2026-06-15, <https://man7.org/linux/man-pages/man1/bash.1.html>

[2] GNU Bash Manual, "Shell Scripts", 확인일: 2026-06-15, <https://www.gnu.org/software/bash/manual/html_node/Shell-Scripts.html>

[3] Linux man-pages, "execve(2) - Linux manual page", 확인일: 2026-06-15, <https://man7.org/linux/man-pages/man2/execve.2.html>

[4] GNU Coreutils Manual, "chmod invocation", 확인일: 2026-06-15, <https://www.gnu.org/software/coreutils/manual/html_node/chmod-invocation.html>

[5] GNU Coreutils Manual, "Setting Permissions", 확인일: 2026-06-15, <https://www.gnu.org/software/coreutils/manual/html_node/Setting-Permissions.html>
