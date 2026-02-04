# 구조

```
├── 📁 _layouts          # 레이아웃 템플릿 (모든 페이지 공통 틀)
│   └── 🌐 default.html  # 기본 레이아웃: 헤더(로고, 검색창, 전체 탭), 본문 영역
├── 📁 _plugins          # Jekyll 플러그인 (커스텀 Liquid 필터 등)
│   └── 💎 replace-regex.rb  # replace_regex 필터: 검색 데이터 생성 시 공백 치환에 사용
├── 📁 _posts            # 블로그 글 (파일명: YYYY-MM-DD-제목.md)
│   └── 📝 *.md          # 각 포스트 마크다운 파일
├── 📁 _sass             # SCSS 소스 (스타일 변수, 레이아웃, 코드/표 스타일 등)
│   ├── 🎨 _code.scss    # 코드 블록 스타일
│   ├── 🎨 _layout.scss  # 헤더, 네비, 본문 레이아웃
│   ├── 🎨 _mixins.scss  # SCSS 믹스인
│   ├── 🎨 _normalize.scss  # CSS 리셋/정규화
│   ├── 🎨 _pygments.scss   # 문법 강조(코드) 스타일
│   ├── 🎨 _tables.scss  # 테이블 스타일
│   └── 🎨 _typography.scss # 글자/타이포 스타일
├── 📁 css
│   └── 🎨 main.scss     # 메인 스타일 진입점 (_sass import 후 빌드 시 main.css 생성)
├── 📁 images            # 이미지/아이콘 (사이트에서 참조)
│   ├── 🖼️ emblem.svg    # 헤더 로고
│   ├── 🖼️ favicon.png   # 브라우저 탭 아이콘
│   └── 🖼️ menu.svg      # 네비 열기(햄버거) 아이콘
├── 📁 scripts           # 클라이언트 스크립트
│   └── 📄 search.js     # (참고: 현재 검색 로직은 search.html 인라인으로 사용 중)
├── ⚙️ .gitignore        # Git 제외 목록 (_site, .sass-cache 등)
├── 🌐 404.html          # 404 에러 페이지
├── 📄 Gemfile           # Ruby/Jekyll 의존성 정의
├── 📄 Gemfile.lock      # 의존성 버전 고정 (bundle install 결과)
├── 📝 README.md         # 이 파일. 프로젝트 설명·구조
├── ⚙️ _config.yml       # Jekyll 설정 (사이트 제목, URL, 플러그인, permalink 등)
├── 🖼️ apple-touch-icon.png  # iOS 등 홈화면 추가 시 아이콘
├── 📝 index.md          # 루트(/) 페이지 = 전체 글 목록
├── 📄 robots.txt        # 검색엔진 크롤링 안내
├── 🌐 search.html       # 검색 결과 페이지 (/search/?q=검색어)
├── 📄 serve.sh          # 로컬 서버 실행 스크립트 (UTF-8 로케일 + jekyll serve)
├── 🖼️ siteicon.png      # SEO·소셜 미리보기용 로고 (_config.yml logo)
└── 🖼️ touch-icon.png    # 터치 기기용 아이콘 (192x192)
```
---
| 구분 | 역할 |
|------|------|
| **전체** | `index.md` → `/` 에서 전체 글 목록 표시 |
| **찾기** | 헤더 검색창에 입력 후 Enter → `search.html` 에서 결과만 표시 (별도 탭 없음) |
| **글 작성** | `_posts/` 에 `YYYY-MM-DD-제목.md` 형식으로 추가 |
