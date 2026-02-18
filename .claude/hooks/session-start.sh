#!/bin/bash
set -euo pipefail

# 웹 환경에서만 실행
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo "ANSYS 자동화 프로젝트 의존성 설치 중..."

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# dev 의존성 설치 (테스트 및 린터 포함)
pip install -r "${PROJECT_DIR}/requirements-dev.txt"

# 프로젝트 루트를 PYTHONPATH에 추가 (테스트에서 import 가능하게)
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export PYTHONPATH=\"${PROJECT_DIR}:\${PYTHONPATH:-}\"" >> "${CLAUDE_ENV_FILE}"
fi

echo "의존성 설치 완료."
