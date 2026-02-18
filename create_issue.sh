#!/bin/bash
gh issue create \
  --repo wlrntjddls-cmd/test \
  --title "Claude Code 여러 인스턴스 동시 실행 방법 정리" \
  --body "## 개요

Claude Code를 여러 개 동시에 실행하는 다양한 방법 정리.

---

## 방법별 요약

| 방법 | 난이도 | 추천 상황 |
|------|--------|----------|
| 여러 터미널 | 쉬움 | 일반 병렬 작업 |
| Git Worktree | 중간 | 같은 레포 다중 브랜치 |
| \`-p\` 헤드리스 | 쉬움 | 자동화/스크립트 |
| Tmux | 중간 | 장시간 세션 관리 |
| Python SDK | 높음 | CI/CD, 복잡한 워크플로우 |

---

## 1. 여러 터미널 (가장 간단)

\`\`\`bash
cd /project-a && claude  # 터미널 1
cd /project-b && claude  # 터미널 2
\`\`\`

---

## 2. Git Worktree (같은 레포 병렬 작업 시 권장)

\`\`\`bash
git worktree add ../project-feature-a -b feature-a
git worktree add ../project-bugfix -b bugfix-123

cd ../project-feature-a && claude   # 터미널 1
cd ../project-bugfix && claude      # 터미널 2

git worktree remove ../project-feature-a  # 정리
\`\`\`

---

## 3. Headless 모드 (\`-p\` 플래그)

\`\`\`bash
# 백그라운드 병렬 실행
claude -p \"버그 분석\" --output-format json > result1.json &
claude -p \"성능 검사\" --output-format json > result2.json &
claude -p \"보안 검토\" --output-format json > result3.json &
wait

# 예산/턴 제한
claude -p \"복잡한 작업\" --max-turns 5 --max-budget-usd 3.00
\`\`\`

---

## 4. Tmux 세션 관리

\`\`\`bash
tmux new-session -d -s work1 \"cd /project-a && claude\"
tmux new-session -d -s work2 \"cd /project-b && claude\"

tmux attach -t work1  # 전환 (Ctrl+B, D로 빠져나옴)
tmux list-sessions
\`\`\`

---

## 5. GNU parallel 활용

\`\`\`bash
echo -e \"버그 분석\n성능 검사\n보안 검토\" | \
  parallel -j 3 'claude -p \"{}\" --output-format json > result_{#}.json'
\`\`\`

---

## 6. Python SDK 병렬 실행

\`\`\`python
import asyncio
from claude_code_sdk import query, ClaudeCodeOptions

async def run_agent(prompt, cwd):
    async for msg in query(prompt=prompt, options=ClaudeCodeOptions(cwd=cwd)):
        if hasattr(msg, 'result'):
            return msg.result

async def main():
    results = await asyncio.gather(
        run_agent(\"버그 분석\", \"/project/auth\"),
        run_agent(\"성능 검사\", \"/project/db\"),
        run_agent(\"문서 생성\", \"/project/api\"),
    )
    for r in results:
        print(r)

asyncio.run(main())
\`\`\`

---

## 빠른 시작 추천

- **바로 시작**: 터미널 여러 개 + \`-p\` 플래그
- **같은 레포 병렬 작업**: Git Worktree
- **자동화/CI**: Headless 모드 또는 Python SDK"
