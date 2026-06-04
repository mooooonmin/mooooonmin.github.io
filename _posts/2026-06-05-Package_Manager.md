---
title: Package Manager
category: p
date: 2026-06-05 00:00:20 +0900
tags: [linux, package-manager, apt, dnf, yum, npm, pip]
---

## 1. 패키지 매니저란?

패키지 매니저는 프로그램이나 라이브러리 같은 소프트웨어 패키지를 설치, 업데이트, 제거할 때 사용하는 도구다.

스마트폰에서 앱을 설치할 때 Android는 Play Store를 사용하고, iOS는 App Store를 사용한다.
개발 환경에서도 비슷하게 프로그램을 직접 찾아서 내려받기보다, 환경에 맞는 패키지 매니저를 사용해 설치하는 경우가 많다.

예를 들어 Ubuntu에서 새로운 프로그램을 설치하려면 보통 `apt`를 사용한다.

```bash
sudo apt install [패키지명]
```

Ubuntu 공식 문서는 APT 명령이 새 소프트웨어 패키지 설치, 기존 패키지 업그레이드, 패키지 목록 갱신 등에 사용된다고 설명한다. [1]

---

## 2. 환경마다 패키지 매니저가 다르다

패키지 매니저는 운영체제나 개발 환경에 따라 다르다.
그래서 어떤 환경에서 작업하는지에 따라 사용하는 도구도 달라진다.

| 환경 | 대표 패키지 매니저 |
|---|---|
| Node.js | `npm`, `yarn` |
| Python | `pip` |
| Ubuntu/Debian 계열 Linux | `apt` |
| Fedora 계열 Linux | `dnf` |
| CentOS/RHEL 계열 Linux | `yum`, `dnf` |

Node.js 공식 문서는 `npm`을 Node.js의 표준 패키지 매니저라고 설명한다. [2]
Python Packaging User Guide는 Python 패키지를 설치할 때 `pip`와 가상 환경을 사용하는 방법을 안내한다. [3]
Fedora 문서는 DNF를 패키지 조회, 저장소에서 패키지 가져오기, 설치, 제거, 시스템 업데이트에 사용할 수 있는 패키지 매니저로 설명한다. [4]

즉, 패키지 매니저는 하나만 있는 것이 아니라 환경마다 다르게 존재한다.

---

## 3. 패키지 매니저가 하는 일

패키지 매니저는 단순히 프로그램을 설치하는 도구만은 아니다.
보통 아래 작업을 함께 처리한다.

| 작업 | 의미 |
|---|---|
| 설치 | 필요한 프로그램이나 라이브러리를 설치한다. |
| 업데이트 | 설치된 패키지를 새 버전으로 갱신한다. |
| 제거 | 더 이상 필요 없는 패키지를 삭제한다. |
| 검색 | 설치 가능한 패키지를 찾는다. |
| 의존성 처리 | 필요한 추가 패키지를 함께 설치하거나 관리한다. |

예를 들어 어떤 프로그램이 다른 라이브러리를 필요로 한다면, 패키지 매니저는 그 라이브러리까지 함께 설치해야 하는지 확인한다.
이런 추가로 필요한 패키지를 의존성이라고 부른다.

---

## 4. Ubuntu에서 사용하는 `apt`

Ubuntu에서는 주로 `apt`를 사용한다.
패키지 목록을 갱신할 때는 아래 명령어를 사용한다.

```bash
sudo apt update
```

패키지를 설치할 때는 아래 명령어를 사용한다.

```bash
sudo apt install [패키지명]
```

패키지를 제거할 때는 아래 명령어를 사용할 수 있다.

```bash
sudo apt remove [패키지명]
```

여기서 `sudo`를 붙이는 이유는 패키지 설치나 제거가 시스템에 영향을 주는 작업이기 때문이다.
일반 사용자 권한으로는 시스템 전체에 프로그램을 설치하거나 제거할 수 없는 경우가 많다.

---

## 5. 개발 환경에서 사용하는 패키지 매니저

운영체제뿐 아니라 개발 언어나 프레임워크에도 패키지 매니저가 있다.

Node.js 환경에서는 `npm`을 사용해 JavaScript 패키지를 설치할 수 있다.

```bash
npm install [패키지명]
```

Python 환경에서는 `pip`를 사용해 Python 패키지를 설치할 수 있다.

```bash
python -m pip install [패키지명]
```

Spring 프로젝트에서는 패키지 매니저라는 표현보다 빌드 도구라는 표현을 더 자주 사용하지만, 외부 라이브러리 의존성을 관리한다는 점에서 Gradle이나 Maven을 함께 떠올릴 수 있다.

처음에는 아래처럼만 구분해도 충분하다.

| 상황 | 사용할 도구 |
|---|---|
| Ubuntu에서 프로그램 설치 | `apt` |
| Node.js 패키지 설치 | `npm` |
| Python 패키지 설치 | `pip` |
| Spring 프로젝트 의존성 관리 | `Gradle`, `Maven` |

---

## 6. 직접 설치와 패키지 매니저 설치의 차이

프로그램을 직접 내려받아 설치할 수도 있지만, 개발 환경에서는 패키지 매니저를 사용하는 편이 관리하기 쉽다.

패키지 매니저를 사용하면 아래 작업을 명령어로 처리할 수 있다.

- 어떤 패키지가 설치되어 있는지 확인
- 패키지를 새 버전으로 업데이트
- 필요 없는 패키지 제거
- 패키지 설치에 필요한 의존성 처리

직접 파일을 내려받아 설치하면 처음 설치는 가능할 수 있다.
하지만 나중에 업데이트하거나 제거할 때 어떤 파일이 어디에 설치되었는지 직접 추적해야 할 수 있다.

그래서 개발 환경에서는 가능하면 해당 환경에서 권장하는 패키지 매니저를 사용하는 것이 좋다.

---

## 핵심 정리

패키지 매니저는 프로그램이나 라이브러리 같은 소프트웨어 패키지를 설치, 업데이트, 제거할 때 사용하는 도구다.

운영체제나 개발 환경에 따라 사용하는 패키지 매니저는 다르다.
Ubuntu에서는 `apt`, Node.js에서는 `npm`, Python에서는 `pip`를 주로 사용한다.

패키지 매니저는 단순히 설치만 하는 도구가 아니다.
패키지 검색, 업데이트, 제거, 의존성 관리까지 함께 처리해 개발 환경을 더 쉽게 관리할 수 있게 도와준다.

---

## 출처

[1] Ubuntu Server Documentation, "Install and manage packages", <https://ubuntu.com/server/docs/package-management/>

[2] Node.js Learn, "An introduction to the npm package manager", <https://nodejs.org/en/learn/getting-started/an-introduction-to-the-npm-package-manager>

[3] Python Packaging User Guide, "Installing Packages", <https://packaging.python.org/installing/>

[4] Fedora Docs, "DNF", <https://docs.fedoraproject.org/ast/fedora/f31/system-administrators-guide/package-management/DNF/>

