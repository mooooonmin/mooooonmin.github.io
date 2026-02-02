#!/bin/bash
# Windows/Git Bash에서 Jekyll 서버 실행 시 UTF-8 로케일 필요
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
bundle exec jekyll serve "$@"
