# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

ANSYS Mechanical/Fluent 시뮬레이션을 Python으로 자동화하는 유틸리티 패키지. Python 3.9 이상 필요.

## 명령어

```bash
# 테스트
PYTHONPATH=. pytest tests/ -v           # 전체 테스트
PYTHONPATH=. pytest tests/test_mechanical.py -v  # 단일 파일
PYTHONPATH=. pytest tests/test_mechanical.py::TestStressResult::test_is_safe_below_yield -v  # 단일 테스트

# 린터
flake8 ansys_utils/ tests/

# 의존성 설치
pip install -r requirements.txt         # 프로덕션
pip install -r requirements-dev.txt     # 개발 (pytest, flake8, black)
```

## 아키텍처

`ansys_utils/` 패키지는 3개의 핵심 모듈로 구성:

- **mechanical.py**: `MechanicalSession`이 ANSYS 실행을 관리 (context manager 지원). `DeformationResult`/`StressResult` dataclass로 결과 반환. 세션은 `open_database()` → `solve()` → `get_deformation()`/`get_stress()` 순서로 사용하며, 연결 없이 결과 조회 시 `RuntimeError` 발생.
- **materials.py**: `MaterialDatabase`가 내장 재료(Steel A36, Al 6061, Ti-6Al-4V, SS304)를 제공. `Material` dataclass에 기계적/열적 속성 포함. `safety_factor()` 메서드로 안전 계수 계산.
- **postprocess.py**: `ResultsPlotter`가 `.rst`/`.rfl`/`.res` 결과 파일을 시각화. lazy loading 패턴 사용 (`load()`는 첫 플롯 호출 시 자동 실행).

## 코드 스타일

- flake8 max-line-length: 88 (black 호환)
- `E203`, `W503` 무시 (`.flake8` 설정)
- 한국어 docstring 및 에러 메시지
- 타입 힌트 사용
