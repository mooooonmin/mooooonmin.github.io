source 'https://rubygems.org'

# GitHub Pages 공식 빌드 환경과 같은 의존성 묶음을 사용한다.
# actions/jekyll-build-pages@v1.0.13은 github-pages 232와 Jekyll 3.10.0 조합으로 빌드한다.
gem 'github-pages', '~> 232', group: :jekyll_plugins

# Windows에는 IANA zoneinfo 디렉터리가 기본 제공되지 않으므로 TZInfo 데이터 gem을 사용한다.
gem 'tzinfo-data', '~> 1.2026', platforms: [:mingw, :mswin, :x64_mingw]

# Ruby 3.4의 Windows 레지스트리 로더와 GitHub Metadata의 Faraday 안내를 명시적으로 충족한다.
gem 'fiddle', '1.1.6', platforms: [:mingw, :mswin, :x64_mingw]
gem 'faraday-retry', '~> 2.4'
