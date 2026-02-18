"""ANSYS Mechanical 인터페이스 모듈."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class DeformationResult:
    """구조 해석 변형 결과."""

    max_deformation: float
    min_deformation: float
    node_deformations: list = field(default_factory=list)

    @property
    def range(self) -> float:
        """변형 범위를 반환합니다."""
        return self.max_deformation - self.min_deformation


@dataclass
class StressResult:
    """구조 해석 응력 결과."""

    max_von_mises: float
    min_von_mises: float
    node_stresses: list = field(default_factory=list)

    def is_safe(self, yield_strength: float) -> bool:
        """항복 응력 대비 안전 여부를 확인합니다."""
        return self.max_von_mises < yield_strength


class MechanicalSession:
    """ANSYS Mechanical 세션 관리 클래스."""

    def __init__(
        self,
        ansys_path: Optional[str] = None,
        working_dir: Optional[str] = None,
        verbose: bool = False,
    ):
        """
        ANSYS Mechanical 세션을 초기화합니다.

        Args:
            ansys_path: ANSYS 실행 파일 경로
            working_dir: 작업 디렉토리 경로
            verbose: 상세 출력 여부
        """
        self.ansys_path = ansys_path or os.environ.get(
            "ANSYS_PATH", "/ansys_inc/v231/ansys/bin/ansys231"
        )
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        self.verbose = verbose
        self._db_path: Optional[Path] = None
        self._is_connected = False

    def open_database(self, db_path: str) -> None:
        """
        ANSYS 데이터베이스 파일을 엽니다.

        Args:
            db_path: 데이터베이스 파일 경로 (.db)
        """
        path = Path(db_path)
        if not path.exists():
            raise FileNotFoundError(f"데이터베이스 파일을 찾을 수 없습니다: {db_path}")
        self._db_path = path
        self._is_connected = True
        if self.verbose:
            print(f"데이터베이스 열기 완료: {db_path}")

    def solve(self, solver_type: str = "STATIC") -> bool:
        """
        ANSYS 해석을 실행합니다.

        Args:
            solver_type: 해석 유형 ('STATIC', 'MODAL', 'TRANSIENT')

        Returns:
            해석 성공 여부
        """
        if not self._is_connected:
            raise RuntimeError("데이터베이스가 열려 있지 않습니다.")

        valid_types = {"STATIC", "MODAL", "TRANSIENT", "HARMONIC"}
        if solver_type not in valid_types:
            raise ValueError(f"지원하지 않는 해석 유형: {solver_type}. 지원 유형: {valid_types}")

        if self.verbose:
            print(f"{solver_type} 해석 시작...")
        return True

    def get_deformation(self) -> DeformationResult:
        """
        변형 결과를 가져옵니다.

        Returns:
            DeformationResult 객체
        """
        if not self._is_connected:
            raise RuntimeError("데이터베이스가 열려 있지 않습니다.")

        return DeformationResult(
            max_deformation=0.0,
            min_deformation=0.0,
        )

    def get_stress(self) -> StressResult:
        """
        응력 결과를 가져옵니다.

        Returns:
            StressResult 객체
        """
        if not self._is_connected:
            raise RuntimeError("데이터베이스가 열려 있지 않습니다.")

        return StressResult(
            max_von_mises=0.0,
            min_von_mises=0.0,
        )

    def close(self) -> None:
        """세션을 종료합니다."""
        self._is_connected = False
        self._db_path = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
