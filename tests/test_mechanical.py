"""ANSYS Mechanical 인터페이스 테스트."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from ansys_utils.mechanical import (
    DeformationResult,
    MechanicalSession,
    StressResult,
)


class TestDeformationResult:
    """DeformationResult 클래스 테스트."""

    def test_range_calculation(self):
        """변형 범위 계산을 테스트합니다."""
        result = DeformationResult(max_deformation=5.0, min_deformation=1.0)
        assert result.range == pytest.approx(4.0)

    def test_range_zero(self):
        """변형 범위가 0인 경우를 테스트합니다."""
        result = DeformationResult(max_deformation=0.0, min_deformation=0.0)
        assert result.range == pytest.approx(0.0)


class TestStressResult:
    """StressResult 클래스 테스트."""

    def test_is_safe_below_yield(self):
        """항복 응력 이하에서 안전 판정을 테스트합니다."""
        result = StressResult(max_von_mises=200.0, min_von_mises=0.0)
        assert result.is_safe(yield_strength=250.0) is True

    def test_is_not_safe_above_yield(self):
        """항복 응력 초과에서 불안전 판정을 테스트합니다."""
        result = StressResult(max_von_mises=300.0, min_von_mises=0.0)
        assert result.is_safe(yield_strength=250.0) is False

    def test_is_not_safe_at_yield(self):
        """항복 응력과 동일한 경우 불안전 판정을 테스트합니다."""
        result = StressResult(max_von_mises=250.0, min_von_mises=0.0)
        assert result.is_safe(yield_strength=250.0) is False


class TestMechanicalSession:
    """MechanicalSession 클래스 테스트."""

    def test_init_default_path(self):
        """기본 경로로 초기화를 테스트합니다."""
        session = MechanicalSession()
        assert session.verbose is False
        assert session._is_connected is False

    def test_init_custom_path(self):
        """사용자 경로로 초기화를 테스트합니다."""
        session = MechanicalSession(ansys_path="/custom/path")
        assert session.ansys_path == "/custom/path"

    def test_open_nonexistent_database(self):
        """존재하지 않는 데이터베이스 열기를 테스트합니다."""
        session = MechanicalSession()
        with pytest.raises(FileNotFoundError):
            session.open_database("nonexistent.db")

    @patch("ansys_utils.mechanical.launch_mapdl")
    def test_open_database_success(self, mock_launch, tmp_path):
        """데이터베이스 열기 성공을 테스트합니다."""
        mock_mapdl = MagicMock()
        mock_launch.return_value = mock_mapdl

        db_file = tmp_path / "test.db"
        db_file.write_text("mock db content")

        session = MechanicalSession()
        session.open_database(str(db_file))
        assert session._is_connected is True
        mock_mapdl.resume.assert_called_once_with(str(db_file))

    def test_solve_without_database(self):
        """데이터베이스 없이 해석 실행을 테스트합니다."""
        session = MechanicalSession()
        with pytest.raises(RuntimeError, match="데이터베이스가 열려 있지 않습니다"):
            session.solve()

    @patch("ansys_utils.mechanical.launch_mapdl")
    def test_solve_invalid_type(self, mock_launch, tmp_path):
        """잘못된 해석 유형으로 해석 실행을 테스트합니다."""
        mock_mapdl = MagicMock()
        mock_launch.return_value = mock_mapdl

        db_file = tmp_path / "test.db"
        db_file.write_text("mock db content")

        session = MechanicalSession()
        session.open_database(str(db_file))

        with pytest.raises(ValueError, match="지원하지 않는 해석 유형"):
            session.solve(solver_type="INVALID")

    @patch("ansys_utils.mechanical.launch_mapdl")
    def test_solve_valid_types(self, mock_launch, tmp_path):
        """지원 해석 유형으로 해석 실행을 테스트합니다."""
        mock_mapdl = MagicMock()
        mock_launch.return_value = mock_mapdl

        db_file = tmp_path / "test.db"
        db_file.write_text("mock db content")

        session = MechanicalSession()
        session.open_database(str(db_file))

        for solver_type in ["STATIC", "MODAL", "TRANSIENT", "HARMONIC"]:
            assert session.solve(solver_type=solver_type) is True

    def test_get_deformation_without_database(self):
        """데이터베이스 없이 변형 결과 조회를 테스트합니다."""
        session = MechanicalSession()
        with pytest.raises(RuntimeError):
            session.get_deformation()

    @patch("ansys_utils.mechanical.launch_mapdl")
    def test_get_deformation_returns_result(self, mock_launch, tmp_path):
        """변형 결과 반환을 테스트합니다."""
        mock_mapdl = MagicMock()
        mock_launch.return_value = mock_mapdl
        mock_mapdl.post_processing.nodal_displacement.return_value = (
            np.array([0.0, 1.5, 3.0, 0.5])
        )

        db_file = tmp_path / "test.db"
        db_file.write_text("mock db content")

        session = MechanicalSession()
        session.open_database(str(db_file))
        result = session.get_deformation()

        assert isinstance(result, DeformationResult)
        assert result.max_deformation == pytest.approx(3.0)
        assert result.min_deformation == pytest.approx(0.0)
        assert len(result.node_deformations) == 4

    @patch("ansys_utils.mechanical.launch_mapdl")
    def test_get_stress_returns_result(self, mock_launch, tmp_path):
        """응력 결과 반환을 테스트합니다."""
        mock_mapdl = MagicMock()
        mock_launch.return_value = mock_mapdl
        mock_mapdl.post_processing.nodal_eqv_stress.return_value = (
            np.array([10.0, 50.0, 200.0, 150.0])
        )

        db_file = tmp_path / "test.db"
        db_file.write_text("mock db content")

        session = MechanicalSession()
        session.open_database(str(db_file))
        result = session.get_stress()

        assert isinstance(result, StressResult)
        assert result.max_von_mises == pytest.approx(200.0)
        assert result.min_von_mises == pytest.approx(10.0)
        assert len(result.node_stresses) == 4

    @patch("ansys_utils.mechanical.launch_mapdl")
    def test_context_manager(self, mock_launch, tmp_path):
        """컨텍스트 매니저 사용을 테스트합니다."""
        mock_mapdl = MagicMock()
        mock_launch.return_value = mock_mapdl

        db_file = tmp_path / "test.db"
        db_file.write_text("mock db content")

        with MechanicalSession() as session:
            session.open_database(str(db_file))
            assert session._is_connected is True

        assert session._is_connected is False
        mock_mapdl.exit.assert_called_once()

    @patch("ansys_utils.mechanical.launch_mapdl")
    def test_close_cleans_up(self, mock_launch):
        """close()가 리소스를 정리하는지 테스트합니다."""
        mock_mapdl = MagicMock()
        mock_launch.return_value = mock_mapdl

        session = MechanicalSession()
        session.launch()
        assert session._is_connected is True
        assert session._mapdl is not None

        session.close()
        assert session._is_connected is False
        assert session._mapdl is None
        mock_mapdl.exit.assert_called_once()

    @patch("ansys_utils.mechanical.launch_mapdl")
    def test_connect_to_server(self, mock_launch):
        """기존 MAPDL 서버 연결을 테스트합니다."""
        mock_mapdl = MagicMock()
        mock_launch.return_value = mock_mapdl

        session = MechanicalSession()
        session.connect(ip="192.168.1.100", port=50053)

        assert session._is_connected is True
        mock_launch.assert_called_once_with(
            start_instance=False,
            ip="192.168.1.100",
            port=50053,
        )
