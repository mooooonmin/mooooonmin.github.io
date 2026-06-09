---
title: Group
category: g
date: 2026-06-03 00:00:00 +0900
tags: [linux, group, user, groups, passwd]
---

## 1. 그룹이란?

Linux에서 그룹(group)은 사용자 계정을 묶어서 권한을 관리하기 위한 단위이다.
여러 사용자에게 공통된 권한을 한 번에 부여하고 관리할 때 사용한다.

예를 들어 어떤 파일이나 디렉터리를 특정 그룹만 읽거나 수정할 수 있게 만들 수 있다.
이때 사용자마다 권한을 따로 주는 대신, 사용자를 같은 그룹에 넣고 그룹 권한을 설정하면 관리하기 쉽다.

Linux man-pages의 `group(5)` 문서는 `/etc/group` 파일이 시스템의 그룹을 정의하는 텍스트 파일이라고 설명한다. [1]

---

## 2. 그룹의 특징

사용자는 기본 그룹(primary group)을 가진다.
Linux man-pages의 `passwd(5)` 문서는 `/etc/passwd` 파일의 `GID` 필드가 해당 사용자의 숫자 기본 그룹 ID라고 설명한다. [2]

또한 사용자는 기본 그룹 외에 추가 그룹에도 속할 수 있다.
`passwd(5)` 문서는 사용자의 추가 그룹이 시스템 그룹 파일에서 정의된다고 설명한다. [2]

정리하면 아래처럼 이해하면 된다.

| 구분 | 의미 |
|---|---|
| 기본 그룹 | 사용자 계정에 연결된 대표 그룹 |
| 추가 그룹 | 기본 그룹 외에 사용자가 함께 속할 수 있는 그룹 |

입문 단계에서는 아래 두 가지만 기억하면 충분하다.

- 한 사용자(user)는 기본 그룹(group)을 가진다.
- 한 사용자(user)는 여러 그룹(group)에 속할 수 있다.

---

## 3. 특정 계정이 속한 그룹 확인하기

특정 사용자가 어떤 그룹에 속해 있는지 확인하려면 `groups` 명령어를 사용한다.

```bash
groups 사용자명
```

GNU Coreutils의 `groups(1)` 문서는 `groups` 명령어가 지정한 사용자의 그룹 멤버십을 출력한다고 설명한다. [3]

예를 들어 `ubuntu` 사용자의 그룹을 확인하려면 아래처럼 입력한다.

```bash
groups ubuntu
```

출력 예시는 아래와 같다.

```text
ubuntu : ubuntu adm cdrom sudo dip lxd
```

이 출력은 `ubuntu` 사용자가 아래 그룹에 속해 있다는 뜻이다.

| 사용자 | 속한 그룹 |
|---|---|
| `ubuntu` | `ubuntu`, `adm`, `cdrom`, `sudo`, `dip`, `lxd` |

이번에는 `root` 사용자의 그룹을 확인해보자.

```bash
groups root
```

출력 예시는 아래와 같다.

```text
root : root
```

이 출력은 `root` 사용자가 `root` 그룹에 속해 있다는 뜻이다.

| 사용자 | 속한 그룹 |
|---|---|
| `root` | `root` |

다만 위 출력은 예시이다.
실제 결과는 Linux 배포판, 서버 설정, 사용자가 추가된 그룹에 따라 달라질 수 있다.

---

## 4. `ubuntu` 그룹과 `root` 그룹

Linux에서는 사용자 이름과 같은 이름의 그룹이 함께 보이는 경우가 많다.
예를 들어 아래 출력에서는 `ubuntu` 사용자가 `ubuntu` 그룹에 속해 있다.

```text
ubuntu : ubuntu adm cdrom sudo dip lxd
```

아래 출력에서는 `root` 사용자가 `root` 그룹에 속해 있다.

```text
root : root
```

입문 단계에서는 먼저 아래 정도만 기억해두면 된다.

| 사용자 | 우선 기억할 그룹 |
|---|---|
| `ubuntu` | `ubuntu` 그룹 |
| `root` | `root` 그룹 |

나중에 파일 권한을 배울 때 `사용자`, `그룹`, `기타 사용자`라는 기준이 나오는데, 이때 그룹 개념이 다시 사용된다.

---

## 정리

- 그룹(group)은 사용자 계정을 묶어서 권한을 관리하기 위한 단위이다.
- 사용자는 기본 그룹을 가진다.
- 사용자는 기본 그룹 외에 여러 추가 그룹에도 속할 수 있다.
- 특정 사용자가 속한 그룹은 `groups 사용자명`으로 확인한다.
- `groups ubuntu` 출력에서 `ubuntu : ubuntu adm cdrom sudo dip lxd`가 나오면 `ubuntu` 사용자가 해당 그룹들에 속해 있다는 뜻이다.
- `groups root` 출력에서 `root : root`가 나오면 `root` 사용자가 `root` 그룹에 속해 있다는 뜻이다.
- 실제 그룹 목록은 시스템 설정에 따라 달라질 수 있다.

---

## 출처

- [1] Linux man-pages, `group(5)` - <https://man7.org/linux/man-pages/man5/group.5.html>
- [2] Linux man-pages, `passwd(5)` - <https://man7.org/linux/man-pages/man5/passwd.5.html>
- [3] Linux man-pages, `groups(1)` - <https://man7.org/linux/man-pages/man1/groups.1.html>
