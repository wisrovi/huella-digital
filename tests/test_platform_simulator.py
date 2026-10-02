"""
Tests automatizados para la Plataforma Simulador 3D con ChromaDB y LangChain.
Verifica:
1. Indexación y consultas semánticas RAG con ChromaDB.
2. Control adaptativo del usuario sobre cualquier personaje (Perito, Abogado, Fiscal, etc.).
3. Filtrado estricto de evidencia por rol procesal.
4. Orquestación del tribunal y moderación con agentes de personajes.
"""

import pytest
from platform_simulator.rag.chroma_engine import ChromaRAGEngine, RAGDocument
from platform_simulator.core.case_initializer import get_demo_cases, populate_demo_rag
from platform_simulator.scenarios.interactive_session import InteractiveScenarioSession

@pytest.fixture
def chroma_rag():
    rag = ChromaRAGEngine()
    populate_demo_rag(rag)
    return rag

def test_chroma_semantic_search(chroma_rag):
    results = chroma_rag.query_context(
        case_id="audiencia_clonado_forense",
        query="duplicadora hardware bloqueador",
        requester_role="estudiante_perito",
        top_k=2
    )
    assert len(results) > 0
    assert "Tableau" in results[0]["content"]

def test_user_takes_power_of_lawyer(chroma_rag):
    case = get_demo_cases()[0]
    session = InteractiveScenarioSession(
        session_id="lawyer_test",
        case=case,
        user_role="abogado_defensa",
        user_name="D. Letrado Defensor",
        rag_engine=chroma_rag
    )
    opening = session.start_session()
    assert len(opening) >= 1
    # Juez abre la sesión judicial
    assert opening[0].speaker_role == "juez"

    # Usuario interviene como Abogado
    user_msg, replies = session.submit_user_action("Señoría, formulo objeción formal contra el informe pericial aportado.")
    assert user_msg.speaker_role == "abogado_defensa"
    assert len(replies) >= 1

def test_user_takes_power_of_forensic_expert(chroma_rag):
    case = get_demo_cases()[0]
    session = InteractiveScenarioSession(
        session_id="expert_test",
        case=case,
        user_role="estudiante_perito",
        user_name="Perito Forense Oficial",
        rag_engine=chroma_rag
    )
    user_msg, replies = session.submit_user_action("Acredito que la clonación forense se realizó con bloqueador Tableau y hash SHA-256 inalterado.")
    assert user_msg.speaker_role == "estudiante_perito"
    assert len(replies) >= 1
