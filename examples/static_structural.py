"""정적 구조 해석 예제."""

from ansys_utils.mechanical import MechanicalSession
from ansys_utils.materials import MaterialDatabase
from ansys_utils.postprocess import ResultsPlotter


def run_static_analysis(db_path: str, results_path: str) -> None:
    """
    정적 구조 해석을 실행하고 결과를 시각화합니다.

    Args:
        db_path: ANSYS 데이터베이스 파일 경로
        results_path: 결과 파일 경로
    """
    # 재료 정보 로드
    mat_db = MaterialDatabase()
    steel = mat_db.get("steel_A36")
    print(f"재료: {steel.name}")
    print(f"  영율: {steel.youngs_modulus} GPa")
    print(f"  항복 강도: {steel.yield_strength} MPa")

    # 해석 실행
    with MechanicalSession(verbose=True) as session:
        session.open_database(db_path)
        session.solve(solver_type="STATIC")

        deformation = session.get_deformation()
        stress = session.get_stress()

        print(f"\n해석 결과:")
        print(f"  최대 변형량: {deformation.max_deformation:.4f} mm")
        print(f"  최대 Von Mises 응력: {stress.max_von_mises:.2f} MPa")

        safety_factor = steel.safety_factor(max(stress.max_von_mises, 0.001))
        print(f"  안전 계수: {safety_factor:.2f}")

        if stress.is_safe(steel.yield_strength):
            print("  상태: 안전 ✓")
        else:
            print("  상태: 경고 - 항복 응력 초과!")

    # 결과 시각화
    plotter = ResultsPlotter(results_path)
    plotter.plot_von_mises_stress(
        output="stress_distribution.png",
        colormap="jet",
    )
    plotter.plot_deformation(
        scale_factor=10.0,
        output="deformation.png",
    )
    print("\n결과 이미지가 저장되었습니다.")


if __name__ == "__main__":
    run_static_analysis(
        db_path="model.db",
        results_path="results.rst",
    )
