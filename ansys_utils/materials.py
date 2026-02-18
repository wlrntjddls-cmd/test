"""재료 속성 데이터베이스 모듈."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Material:
    """재료 속성 데이터 클래스."""

    name: str
    youngs_modulus: float  # GPa
    poissons_ratio: float
    density: float  # kg/m³
    yield_strength: float  # MPa
    ultimate_strength: float  # MPa
    thermal_conductivity: Optional[float] = None  # W/(m·K)
    specific_heat: Optional[float] = None  # J/(kg·K)

    def safety_factor(self, applied_stress: float) -> float:
        """
        안전 계수를 계산합니다.

        Args:
            applied_stress: 적용 응력 (MPa)

        Returns:
            안전 계수
        """
        if applied_stress <= 0:
            raise ValueError("적용 응력은 양수여야 합니다.")
        return self.yield_strength / applied_stress


class MaterialDatabase:
    """재료 속성 데이터베이스 클래스."""

    _DEFAULT_MATERIALS: Dict[str, Dict] = {
        "steel_A36": {
            "name": "Steel A36",
            "youngs_modulus": 200.0,
            "poissons_ratio": 0.26,
            "density": 7850.0,
            "yield_strength": 250.0,
            "ultimate_strength": 400.0,
            "thermal_conductivity": 50.0,
            "specific_heat": 490.0,
        },
        "aluminum_6061": {
            "name": "Aluminum 6061-T6",
            "youngs_modulus": 68.9,
            "poissons_ratio": 0.33,
            "density": 2700.0,
            "yield_strength": 276.0,
            "ultimate_strength": 310.0,
            "thermal_conductivity": 167.0,
            "specific_heat": 896.0,
        },
        "titanium_Ti6Al4V": {
            "name": "Titanium Ti-6Al-4V",
            "youngs_modulus": 114.0,
            "poissons_ratio": 0.34,
            "density": 4430.0,
            "yield_strength": 880.0,
            "ultimate_strength": 950.0,
            "thermal_conductivity": 7.2,
            "specific_heat": 526.0,
        },
        "stainless_steel_304": {
            "name": "Stainless Steel 304",
            "youngs_modulus": 193.0,
            "poissons_ratio": 0.29,
            "density": 8000.0,
            "yield_strength": 215.0,
            "ultimate_strength": 505.0,
            "thermal_conductivity": 16.2,
            "specific_heat": 500.0,
        },
    }

    def __init__(self):
        """데이터베이스를 초기화합니다."""
        self._materials: Dict[str, Material] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        """기본 재료를 로드합니다."""
        for key, props in self._DEFAULT_MATERIALS.items():
            self._materials[key] = Material(**props)

    def get(self, material_id: str) -> Material:
        """
        재료 속성을 가져옵니다.

        Args:
            material_id: 재료 ID

        Returns:
            Material 객체

        Raises:
            KeyError: 재료를 찾을 수 없을 때
        """
        if material_id not in self._materials:
            available = ", ".join(self._materials.keys())
            raise KeyError(
                f"재료 '{material_id}'를 찾을 수 없습니다. "
                f"사용 가능한 재료: {available}"
            )
        return self._materials[material_id]

    def add(self, material_id: str, material: Material) -> None:
        """
        새 재료를 추가합니다.

        Args:
            material_id: 재료 ID
            material: Material 객체
        """
        self._materials[material_id] = material

    def list_materials(self) -> list:
        """사용 가능한 재료 목록을 반환합니다."""
        return list(self._materials.keys())
