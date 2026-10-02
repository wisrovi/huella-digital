"""
Módulo de Inicialización de Casos y Base de Datos Vectorial ChromaDB.
"""

from __future__ import annotations
import os
from platform_simulator.agents.langchain_runner import ScenarioCase, ScenarioType, Character, AvatarVisual
from platform_simulator.rag.chroma_engine import ChromaRAGEngine, RAGDocument

def get_demo_cases() -> list[ScenarioCase]:
    cases = [
        ScenarioCase(
            case_id="audiencia_clonado_forense",
            title="Audiencia Previa: Manipulación de Evidencia Digital en Fraude Financiero",
            scenario_type=ScenarioType.AUDIENCIA,
            description="Juicio oral en el que las partes interrogan sobre la adquisición forense de un disco SSD y la integridad criptográfica de las trazas.",
            environment_3d="courtroom_classic",
            difficulty="intermedio",
            max_turns=50,
            characters=[
                Character(
                    id="char_juez",
                    name="Magistrado D. Antonio Morales",
                    role="juez",
                    personality="Riguroso, ecuánime, garante de las formas procesales.",
                    system_prompt="Eres el Magistrado Juez. Modera la sala y haz cumplir el orden procesal.",
                    objectives=["Dirigir el debate y requerir rigor"],
                    avatar=AvatarVisual(avatar_id="av_juez", model_3d_type="avatar_3d_judge", mesh_color="#0284c7")
                ),
                Character(
                    id="char_fiscal",
                    name="Fiscal Dña. Carmen Serrano",
                    role="fiscal",
                    personality="Incisiva, metódica, busca probar la autoría del delito.",
                    system_prompt="Eres la Fiscal. Interroga sobre hashes, bloqueadores y fechas de adquisición.",
                    objectives=["Comprobar no alteración de la prueba digital"],
                    avatar=AvatarVisual(avatar_id="av_fiscal", model_3d_type="avatar_3d_fiscal", mesh_color="#ea580c")
                ),
                Character(
                    id="char_abogado",
                    name="Letrado D. Jorge Valenzuela",
                    role="abogado_defensa",
                    personality="Escéptico, perspicaz, busca vacíos en la cadena de custodia.",
                    system_prompt="Eres el Abogado de la Defensa. Cuestiona la validez de los logs y la cadena de custodia.",
                    objectives=["Sembrar duda sobre contaminación previa por malware"],
                    avatar=AvatarVisual(avatar_id="av_abogado", model_3d_type="avatar_3d_lawyer", mesh_color="#9333ea")
                ),
                Character(
                    id="char_acusado",
                    name="Acusado D. Roberto Medina",
                    role="persona_juzgada",
                    personality="Silencioso y atento al desarrollo del juicio.",
                    system_prompt="Eres el acusado representado como figura neutral.",
                    objectives=["Permanecer en el banquillo"],
                    is_active_speaker=False,
                    avatar=AvatarVisual(avatar_id="av_monigote", model_3d_type="monigote_gris", mesh_color="#64748b")
                ),
                Character(
                    id="char_perito",
                    name="Perito Forense Colegiado",
                    role="estudiante_perito",
                    personality="Técnico, imparcial, basado en evidencias probadas.",
                    system_prompt="Eres el perito informático forense asignado por el juzgado.",
                    objectives=["Acreditar rigor técnico según norma UNE 71506"],
                    avatar=AvatarVisual(avatar_id="av_perito", model_3d_type="avatar_3d_expert", mesh_color="#10b981")
                )
            ]
        ),
        ScenarioCase(
            case_id="reunion_crisis_ransomware",
            title="Comité de Crisis: Presentación de Conclusiones de Incidente Ransomware",
            scenario_type=ScenarioType.REUNION_CLIENTE,
            description="Reunión técnica y directiva urgente para evaluar el alcance de una intrusión en servidores y el impacto regulatorio RGPD/AEPD.",
            environment_3d="boardroom_executive",
            difficulty="avanzado",
            max_turns=50,
            characters=[
                Character(
                    id="char_ceo",
                    name="D. Fernando Ortiz (CEO)",
                    role="cliente_director",
                    personality="Pragmático, orientado al impacto reputacional, financiero y legal.",
                    system_prompt="Eres el Director General. Evalúa si procede la notificación a la AEPD.",
                    objectives=["Conocer si hubo exfiltración masiva de datos"],
                    avatar=AvatarVisual(avatar_id="av_ceo", model_3d_type="avatar_3d_ceo", mesh_color="#0369a1")
                ),
                Character(
                    id="char_ciso",
                    name="Dña. Elena Ramos (CISO)",
                    role="cliente_tecnico",
                    personality="Analítica, enfocada en IOCs, aislamiento de la DMZ y persistencia.",
                    system_prompt="Eres la CISO. Pregunta por vectores de entrada y contención.",
                    objectives=["Confirmar si el malware se propagó lateralmente"],
                    avatar=AvatarVisual(avatar_id="av_ciso", model_3d_type="avatar_3d_ciso", mesh_color="#0f766e")
                ),
                Character(
                    id="char_consultor",
                    name="Auditor / Consultor Forense",
                    role="estudiante_perito",
                    personality="Claro, pedagógico y resolutivo.",
                    system_prompt="Eres el consultor forense externo contratado para la respuesta a incidentes.",
                    objectives=["Explicar el triaje y plan de remediación"],
                    avatar=AvatarVisual(avatar_id="av_consultor", model_3d_type="avatar_3d_expert", mesh_color="#10b981")
                )
            ]
        )
    ]
    return cases

def populate_demo_rag(rag_engine: ChromaRAGEngine):
    docs = [
        RAGDocument(
            id="doc_custodia_ssd",
            case_id="audiencia_clonado_forense",
            title="Acta Notarial de Cadena de Custodia SSD-981",
            category="cadena_custodia",
            content="El disco SSD Samsung EVO 1TB fue clonado bit a bit con duplicadora Tableau TD2u por hardware. Hash origen SHA-256: a7f8c9b2e1... Hash destino: a7f8c9b2e1... Coincidencia absoluta. No hubo alteración.",
            allowed_roles=["juez", "fiscal", "abogado_defensa", "estudiante_perito"]
        ),
        RAGDocument(
            id="doc_norma_une",
            case_id="audiencia_clonado_forense",
            title="Normativa UNE 71506 y Guía ISO/IEC 27037",
            category="ley_procesal",
            content="Dispone que todo volcado de evidencias electrónicas debe salvaguardar la integridad criptográfica y realizarse con bloqueadores físicos o lógicos de escritura certificados.",
            allowed_roles=["juez", "fiscal", "abogado_defensa", "estudiante_perito"]
        ),
        RAGDocument(
            id="doc_triaje_ransomware",
            case_id="reunion_crisis_ransomware",
            title="Informe de Triaje e Indicadores de Compromiso (IoC)",
            category="informe_pericial",
            content="Se identificó acceso RDP sin doble factor a las 02:14 UTC. Se ejecutó script PowerShell malicioso que cifró unidades locales, pero el cortafuegos bloqueó la conexión saliente a la IP de Tor, evitando la exfiltración masiva.",
            allowed_roles=["cliente_director", "cliente_tecnico", "estudiante_perito"]
        )
    ]
    rag_engine.index_batch(docs)
