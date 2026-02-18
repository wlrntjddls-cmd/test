"""재료 데이터베이스 테스트."""

import pytest

from ansys_utils.materials import Material, MaterialDatabase


class TestMaterial:
    """Material 클래스 테스트."""

    def test_safety_factor_calculation(self):
        """안전 계수 계산을 테스트합니다."""
        material = Material(
            name="Test Steel",
            youngs_modulus=200.0,
            poissons_ratio=0.26,
            density=7850.0,
            yield_strength=250.0,
            ultimate_strength=400.0,
        )
        assert material.safety_factor(125.0) == pytest.approx(2.0)

    def test_safety_factor_zero_stress(self):
        """적용 응력이 0인 경우 예외를 테스트합니다."""
        material = Material(
            name="Test Steel",
            youngs_modulus=200.0,
            poissons_ratio=0.26,
            density=7850.0,
            yield_strength=250.0,
            ultimate_strength=400.0,
        )
        with pytest.raises(ValueError, match="적용 응력은 양수여야 합니다"):
            material.safety_factor(0.0)

    def test_safety_factor_negative_stress(self):
        """적용 응력이 음수인 경우 예외를 테스트합니다."""
        material = Material(
            name="Test Steel",
            youngs_modulus=200.0,
            poissons_ratio=0.26,
            density=7850.0,
            yield_strength=250.0,
            ultimate_strength=400.0,
        )
        with pytest.raises(ValueError):
            material.safety_factor(-50.0)


class TestMaterialDatabase:
    """MaterialDatabase 클래스 테스트."""

    def test_init_loads_defaults(self):
        """초기화 시 기본 재료가 로드되는지 테스트합니다."""
        db = MaterialDatabase()
        materials = db.list_materials()
        assert len(materials) > 0
        assert "steel_A36" in materials
        assert "aluminum_6061" in materials

    def test_get_steel_A36(self):
        """Steel A36 재료 조회를 테스트합니다."""
        db = MaterialDatabase()
        steel = db.get("steel_A36")
        assert steel.name == "Steel A36"
        assert steel.youngs_modulus == pytest.approx(200.0)
        assert steel.yield_strength == pytest.approx(250.0)

    def test_get_aluminum_6061(self):
        """Aluminum 6061 재료 조회를 테스트합니다."""
        db = MaterialDatabase()
        aluminum = db.get("aluminum_6061")
        assert aluminum.name == "Aluminum 6061-T6"
        assert aluminum.density == pytest.approx(2700.0)

    def test_get_nonexistent_material(self):
        """존재하지 않는 재료 조회를 테스트합니다."""
        db = MaterialDatabase()
        with pytest.raises(KeyError, match="찾을 수 없습니다"):
            db.get("nonexistent_material")

    def test_add_custom_material(self):
        """사용자 정의 재료 추가를 테스트합니다."""
        db = MaterialDatabase()
        custom = Material(
            name="Custom Material",
            youngs_modulus=100.0,
            poissons_ratio=0.3,
            density=5000.0,
            yield_strength=300.0,
            ultimate_strength=450.0,
        )
        db.add("custom_mat", custom)
        retrieved = db.get("custom_mat")
        assert retrieved.name == "Custom Material"

    def test_list_materials_returns_all(self):
        """재료 목록 반환을 테스트합니다."""
        db = MaterialDatabase()
        materials = db.list_materials()
        assert "steel_A36" in materials
        assert "aluminum_6061" in materials
        assert "titanium_Ti6Al4V" in materials
        assert "stainless_steel_304" in materials

    def test_titanium_properties(self):
        """티타늄 재료 속성을 테스트합니다."""
        db = MaterialDatabase()
        titanium = db.get("titanium_Ti6Al4V")
        assert titanium.yield_strength == pytest.approx(880.0)
        assert titanium.density == pytest.approx(4430.0)
