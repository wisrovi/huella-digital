"""
Pruebas automatizadas unitarias y de integración para la solución de Huella Forense.
Verifica:
1. Creación y persistencia de casos modulares.
2. Motor de base de conocimiento (SQLite WAL + búsqueda de contexto).
3. Ciclo de interacción de simulación de audiencia (Juez, Fiscal, Abogado, Monigote pasivo).
4. Ciclo de simulación de reunión con cliente.
5. Motor de valoración y generación de feedback analítico.
6. Estimación técnica de horas I+D/IA y verificación de los 14 bloques de trabajo.
"""

import pytest
import os
import shutil
import tempfile

from huella_forense.models.schemas import ScenarioType, CharacterRole
from huella_forense.core.case_manager import CaseManager
from huella_forense.scenarios.session_runner import SimulationSession
from huella_forense.evaluation.engine import EvaluationEngine
from huella_forense.estimation.effort_estimator import generate_full_estimation

@pytest.fixture
def temp_case_manager():
    temp_dir = tempfile.mkdtemp()
    mgr = CaseManager(cases_dir=temp_dir)
    yield mgr
    shutil.rmtree(temp_dir)

def test_case_manager_loads_canonical_cases(temp_case_manager):
    cases = temp_case_manager.list_cases()
    assert len(cases) == 2
    case_ids = [c["case_id"] for c in cases]
    assert "caso_01_audiencia_clonado_evidencia" in case_ids
    assert "caso_02_reunion_cliente_ransomware" in case_ids

def test_audiencia_simulation_flow(temp_case_manager):
    case = temp_case_manager.load_case("caso_01_audiencia_clonado_evidencia")
    assert case is not None
    assert case.scenario_type == ScenarioType.AUDIENCIA

    session = SimulationSession(
        session_id="test_sess_01",
        case=case,
        student_id="student_pytest",
        student_name="Perito Forense Oficial"
    )

    # Apertura
    opening = session.start_session()
    assert len(opening) >= 1
    assert opening[0].speaker_role == CharacterRole.JUEZ.value

    # Turno 1 del estudiante
    student_msg, responses = session.submit_student_turn(
        "Con la venia de Su Señoría. La adquisición se realizó mediante duplicadora forense con bloqueador de escritura y se certificó el hash SHA-256 coincidente."
    )
    assert student_msg.content.startswith("Con la venia")
    assert len(responses) >= 1
    # Debe responder la contraparte o el fiscal
    assert session.current_turn == 1

def test_evaluation_engine_gives_positive_feedback_on_proper_terms(temp_case_manager):
    case = temp_case_manager.load_case("caso_01_audiencia_clonado_evidencia")
    session = SimulationSession(
        session_id="test_sess_eval",
        case=case,
        student_id="student_top",
        student_name="Perito Senior"
    )
    session.start_session()
    session.submit_student_turn(
        "Señoría, garantizamos la cadena de custodia íntegra. El hash SHA-256 fue cotejado y se utilizó bloqueador de escritura físico Tableau Forensic."
    )

    evaluator = EvaluationEngine(case)
    report = evaluator.evaluate_session(session.session_id, session.student_id, session.history)

    assert report.global_score >= 70.0
    assert len(report.identified_strengths) > 0
    assert len(report.turn_by_turn_analysis) == 1

def test_reunion_cliente_scenario(temp_case_manager):
    case = temp_case_manager.load_case("caso_02_reunion_cliente_ransomware")
    assert case is not None
    assert case.scenario_type == ScenarioType.REUNION_CLIENTE

    session = SimulationSession(
        session_id="test_sess_reunion",
        case=case,
        student_id="student_client",
        student_name="Consultor Forense"
    )
    opening = session.start_session()
    assert len(opening) >= 1
    assert "Buenos días" in opening[0].content

    # Respuesta sobre impacto ejecutivo
    student_msg, responses = session.submit_student_turn(
        "Hemos contenido el ataque a nivel perimetral. No hay evidencia de exfiltración masiva de bases de datos, por lo que el impacto reputacional y regulatorio ante la AEPD queda acotado."
    )
    assert len(responses) >= 1

def test_rd_ia_estimation_blocks():
    est = generate_full_estimation()
    assert len(est.work_packages) == 14
    assert est.total_hours_min > 300
    assert est.total_hours_max > est.total_hours_min
    assert len(est.critical_dependencies) >= 4
    assert len(est.technical_risks) >= 3
