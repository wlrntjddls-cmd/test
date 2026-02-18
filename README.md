# ANSYS 시뮬레이션 자동화 도구

ANSYS 시뮬레이션을 Python으로 자동화하기 위한 유틸리티 모음입니다.

## 개요

이 프로젝트는 ANSYS Mechanical 및 ANSYS Fluent 시뮬레이션을 자동화하고, 결과를 후처리하는 Python 도구를 제공합니다.

## 주요 기능

- ANSYS Mechanical 스크립트 자동화
- ANSYS Fluent 배치 실행 지원
- 시뮬레이션 결과 파싱 및 시각화
- 재료 속성 데이터베이스
- 메쉬 품질 검사 유틸리티

## 설치

### 사전 요구 사항

- Python 3.9 이상
- ANSYS 2023 R1 이상 (라이선스 필요)

### 의존성 설치

```bash
pip install -r requirements.txt
```

## 프로젝트 구조

```
ansys-automation/
├── ansys_utils/           # 메인 패키지
│   ├── __init__.py
│   ├── mechanical.py      # ANSYS Mechanical 인터페이스
│   ├── fluent.py          # ANSYS Fluent 인터페이스
│   ├── postprocess.py     # 결과 후처리
│   └── materials.py       # 재료 속성 데이터베이스
├── tests/                 # 테스트 모음
│   ├── __init__.py
│   ├── test_mechanical.py
│   ├── test_fluent.py
│   └── test_postprocess.py
├── examples/              # 사용 예제
│   ├── static_structural.py
│   └── cfd_basic.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 사용 예제

### ANSYS Mechanical 정적 구조 해석

```python
from ansys_utils.mechanical import MechanicalSession

session = MechanicalSession(ansys_path="/ansys_inc/v231/ansys/bin/ansys231")
session.open_database("model.db")
session.solve()
results = session.get_deformation()
print(f"최대 변형량: {results.max_deformation:.4f} mm")
```

### 결과 시각화

```python
from ansys_utils.postprocess import ResultsPlotter

plotter = ResultsPlotter("results.rst")
plotter.plot_von_mises_stress(output="stress_plot.png")
```

## 테스트 실행

```bash
pytest tests/ -v
```

## 린터 실행

```bash
flake8 ansys_utils/ tests/
```

## 기여 방법

1. 이 레포지토리를 Fork합니다.
2. 기능 브랜치를 생성합니다: `git checkout -b feature/새기능`
3. 변경사항을 커밋합니다: `git commit -m 'Add: 새 기능 추가'`
4. 브랜치에 Push합니다: `git push origin feature/새기능`
5. Pull Request를 생성합니다.

## 라이선스

MIT License

## 문의

문의 사항은 Issues를 통해 제출해주세요.
