"""ANSYS 결과 후처리 모듈."""

from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from ansys.mapdl.reader import read_binary


class ResultsPlotter:
    """ANSYS 결과 시각화 클래스.

    ansys-mapdl-reader를 사용하여 .rst/.rfl/.res 결과 파일을
    읽고 pyvista 기반으로 시각화합니다. lazy loading 패턴을 사용하여
    첫 플롯 호출 시 자동으로 파일을 로드합니다.
    """

    SUPPORTED_FORMATS = {".rst", ".rfl", ".res"}

    def __init__(self, results_file: str):
        """
        결과 플로터를 초기화합니다.

        Args:
            results_file: ANSYS 결과 파일 경로
        """
        self.results_path = Path(results_file)
        self._validate_file()
        self._data_loaded = False
        self._result = None

    def _validate_file(self) -> None:
        """결과 파일의 유효성을 검사합니다."""
        if not self.results_path.exists():
            raise FileNotFoundError(
                f"결과 파일을 찾을 수 없습니다: {self.results_path}"
            )
        if self.results_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"지원하지 않는 파일 형식: {self.results_path.suffix}. "
                f"지원 형식: {self.SUPPORTED_FORMATS}"
            )

    def load(self) -> None:
        """결과 파일을 로드합니다."""
        self._result = read_binary(str(self.results_path))
        self._data_loaded = True

    def plot_von_mises_stress(
        self,
        output: Optional[str] = None,
        colormap: str = "jet",
        show_edges: bool = True,
    ) -> None:
        """
        Von Mises 응력 분포를 시각화합니다.

        Args:
            output: 출력 파일 경로 (None이면 화면에 표시)
            colormap: 컬러맵 이름
            show_edges: 메쉬 엣지 표시 여부
        """
        if not self._data_loaded:
            self.load()

        plot_kwargs = {
            "comp": "SEQV",
            "cmap": colormap,
            "show_edges": show_edges,
        }
        if output:
            plot_kwargs["screenshot"] = output

        self._result.plot_nodal_stress(0, **plot_kwargs)

        if output and self.results_path:
            print(f"파일로 저장: {output}")

    def plot_deformation(
        self,
        scale_factor: float = 1.0,
        output: Optional[str] = None,
    ) -> None:
        """
        변형 결과를 시각화합니다.

        Args:
            scale_factor: 변형 배율
            output: 출력 파일 경로
        """
        if not self._data_loaded:
            self.load()

        plot_kwargs = {}
        if output:
            plot_kwargs["screenshot"] = output

        self._result.plot_nodal_solution(0, **plot_kwargs)

        if output:
            print(f"파일로 저장: {output}")

    def get_min_max(self, result_type: str) -> Tuple[float, float]:
        """
        결과의 최소/최대값을 반환합니다.

        Args:
            result_type: 결과 유형 ('stress', 'deformation', 'strain')

        Returns:
            (최솟값, 최댓값) 튜플
        """
        valid_types = {"stress", "deformation", "strain"}
        if result_type not in valid_types:
            raise ValueError(
                f"지원하지 않는 결과 유형: {result_type}. 지원 유형: {valid_types}"
            )

        if not self._data_loaded:
            self.load()

        if result_type == "stress":
            nnum, stress = self._result.principal_nodal_stress(0)
            von_mises = stress[:, -1]
            return (float(np.min(von_mises)), float(np.max(von_mises)))
        elif result_type == "deformation":
            nnum, disp = self._result.nodal_displacement(0)
            total = np.linalg.norm(disp[:, :3], axis=1)
            return (float(np.min(total)), float(np.max(total)))
        else:  # strain
            nnum, strain = self._result.nodal_elastic_strain(0)
            eqv = strain[:, -1]
            return (float(np.min(eqv)), float(np.max(eqv)))
