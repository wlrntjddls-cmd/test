"""ANSYS Mechanical 인터페이스 모듈."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
from ansys.mapdl.core import launch_mapdl


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
    """ANSYS Mechanical 세션 관리 클래스.

    PyMAPDL을 사용하여 ANSYS MAPDL 인스턴스와 통신합니다.
    launch() 또는 connect()로 MAPDL에 연결한 후,
    open_database() → solve() → get_deformation()/get_stress() 순서로
    사용합니다.
    """

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
        self._mapdl = None

    def launch(self, **kwargs) -> None:
        """
        새 MAPDL 인스턴스를 실행합니다.

        Args:
            **kwargs: launch_mapdl()에 전달할 추가 인자
        """
        launch_kwargs = {
            "run_location": str(self.working_dir),
            "verbose_mapdl": self.verbose,
        }
        if os.path.exists(self.ansys_path):
            launch_kwargs["exec_file"] = self.ansys_path
        launch_kwargs.update(kwargs)

        self._mapdl = launch_mapdl(**launch_kwargs)
        self._is_connected = True
        if self.verbose:
            print("MAPDL 인스턴스 실행 완료")

    def connect(self, ip: str = "127.0.0.1", port: int = 50052) -> None:
        """
        기존 MAPDL 서버에 연결합니다.

        Args:
            ip: MAPDL 서버 IP 주소
            port: MAPDL 서버 포트
        """
        self._mapdl = launch_mapdl(
            start_instance=False,
            ip=ip,
            port=port,
        )
        self._is_connected = True
        if self.verbose:
            print(f"MAPDL 서버에 연결됨: {ip}:{port}")

    def open_database(self, db_path: str) -> None:
        """
        ANSYS 데이터베이스 파일을 엽니다.

        MAPDL이 아직 실행되지 않았으면 자동으로 launch()를 호출합니다.

        Args:
            db_path: 데이터베이스 파일 경로 (.db)
        """
        path = Path(db_path)
        if not path.exists():
            raise FileNotFoundError(
                f"데이터베이스 파일을 찾을 수 없습니다: {db_path}"
            )
        self._db_path = path

        if self._mapdl is None:
            self.launch()

        self._mapdl.resume(str(path))
        self._is_connected = True
        if self.verbose:
            print(f"데이터베이스 열기 완료: {db_path}")

    def solve(self, solver_type: str = "STATIC") -> bool:
        """
        ANSYS 해석을 실행합니다.

        Args:
            solver_type: 해석 유형 ('STATIC', 'MODAL', 'TRANSIENT', 'HARMONIC')

        Returns:
            해석 성공 여부
        """
        if not self._is_connected:
            raise RuntimeError("데이터베이스가 열려 있지 않습니다.")

        valid_types = {"STATIC", "MODAL", "TRANSIENT", "HARMONIC"}
        if solver_type not in valid_types:
            raise ValueError(
                f"지원하지 않는 해석 유형: {solver_type}. "
                f"지원 유형: {valid_types}"
            )

        if self.verbose:
            print(f"{solver_type} 해석 시작...")

        antype_map = {
            "STATIC": "STATIC",
            "MODAL": "MODAL",
            "TRANSIENT": "TRANS",
            "HARMONIC": "HARMIC",
        }

        self._mapdl.slashsolu()
        self._mapdl.antype(antype_map[solver_type])
        self._mapdl.solve()
        self._mapdl.finish()

        if self.verbose:
            print(f"{solver_type} 해석 완료")

        return True

    def get_deformation(self) -> DeformationResult:
        """
        변형 결과를 가져옵니다.

        Returns:
            DeformationResult 객체
        """
        if not self._is_connected:
            raise RuntimeError("데이터베이스가 열려 있지 않습니다.")

        self._mapdl.post1()
        self._mapdl.set(1, 1)

        nodal_disp = self._mapdl.post_processing.nodal_displacement("NORM")

        return DeformationResult(
            max_deformation=float(np.max(nodal_disp)),
            min_deformation=float(np.min(nodal_disp)),
            node_deformations=nodal_disp.tolist(),
        )

    def get_stress(self) -> StressResult:
        """
        응력 결과를 가져옵니다.

        Returns:
            StressResult 객체
        """
        if not self._is_connected:
            raise RuntimeError("데이터베이스가 열려 있지 않습니다.")

        self._mapdl.post1()
        self._mapdl.set(1, 1)

        nodal_stress = self._mapdl.post_processing.nodal_eqv_stress()

        return StressResult(
            max_von_mises=float(np.max(nodal_stress)),
            min_von_mises=float(np.min(nodal_stress)),
            node_stresses=nodal_stress.tolist(),
        )

    def close(self) -> None:
        """세션을 종료합니다."""
        if self._mapdl is not None:
            try:
                self._mapdl.exit()
            except Exception:
                pass
            self._mapdl = None
        self._is_connected = False
        self._db_path = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
