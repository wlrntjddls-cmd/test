"""ANSYS Mechanical 인터페이스 테스트."""

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

    def test_open_database_success(self, tmp_path):
        """데이터베이스 열기 성공을 테스트합니다."""
        db_file = tmp_path / "test.db"
        db_file.write_text("mock db content")

        session = MechanicalSession()
        session.open_database(str(db_file))
        assert session._is_connected is True

    def test_solve_without_database(self):
        """데이터베이스 없이 해석 실행을 테스트합니다."""
        session = MechanicalSession()
        with pytest.raises(RuntimeError, match="데이터베이스가 열려 있지 않습니다"):
            session.solve()

    def test_solve_invalid_type(self, tmp_path):
        """잘못된 해석 유형으로 해석 실행을 테스트합니다."""
        db_file = tmp_path / "test.db"
        db_file.write_text("mock db content")

        session = MechanicalSession()
        session.open_database(str(db_file))

        with pytest.raises(ValueError, match="지원하지 않는 해석 유형"):
            session.solve(solver_type="INVALID")

    def test_solve_valid_types(self, tmp_path):
        """지원 해석 유형으로 해석 실행을 테스트합니다."""
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

    def test_context_manager(self, tmp_path):
        """컨텍스트 매니저 사용을 테스트합니다."""
        db_file = tmp_path / "test.db"
        db_file.write_text("mock db content")

        with MechanicalSession() as session:
            session.open_database(str(db_file))
            assert session._is_connected is True

        assert session._is_connected is False
