"""
Gestor de Casos de Entrenamiento (Case Manager).
Permite crear, guardar, cargar y listar casos modulares en formato JSON/YAML sin tocar el código fuente,
cumpliendo el requerimiento de incorporación progresiva y evolución continua de Huella Forense.
"""

from __future__ import annotations
import os
import json
from typing import List, Optional
from huella_forense.models.schemas import (
    CaseDefinition, ScenarioType, CharacterConfig, CharacterRole,
    KnowledgeDocument, EvaluationIndicator
)

class CaseManager:
    def __init__(self, cases_dir: str):
        self.cases_dir = cases_dir
        os.makedirs(self.cases_dir, exist_ok=True)
        self._ensure_sample_cases()

    def save_case(self, case: CaseDefinition):
        file_path = os.path.join(self.cases_dir, f"{case.case_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(case.model_dump_json(indent=2))

    def load_case(self, case_id: str) -> Optional[CaseDefinition]:
        file_path = os.path.join(self.cases_dir, f"{case_id}.json")
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return CaseDefinition.model_validate(data)

    def list_cases(self) -> List[dict]:
        cases = []
        for fname in os.listdir(self.cases_dir):
            if fname.endswith(".json"):
                cid = fname[:-5]
                c = self.load_case(cid)
                if c:
                    cases.append({
                        "case_id": c.case_id,
                        "title": c.title,
                        "scenario_type": c.scenario_type.value,
                        "difficulty": c.difficulty,
                        "characters_count": len(c.characters),
                        "docs_count": len(c.knowledge_base)
                    })
        return cases

    def _ensure_sample_cases(self):
        """Inicializa los dos casos canónicos exigidos por el documento de requisitos: Audiencia y Reunión con Cliente."""
        # 1. Caso Audiencia Judicial (Escenario 1)
        audiencia_id = "caso_01_audiencia_clonado_evidencia"
        if not os.path.exists(os.path.join(self.cases_dir, f"{audiencia_id}.json")):
            case_audiencia = CaseDefinition(
                case_id=audiencia_id,
                title="Audiencia Previa: Manipulación de Evidencia Digital en Fraude Financiero",
                description="Vista oral donde el estudiante actúa como perito forense defendiendo la autenticidad del volcado forense y la cadena de custodia de un disco SSD incautado.",
                scenario_type=ScenarioType.AUDIENCIA,
                difficulty="intermedio",
                max_turns=6,
                characters=[
                    CharacterConfig(
                        name="Magistrado D. Antonio Morales",
                        role=CharacterRole.JUEZ,
                        personality="Institucional, riguroso con el procedimiento judicial, exige orden y respuestas inequívocas.",
                        objectives=["Garantizar la pulcritud procesal", "Aclarar si la prueba digital puede admitirse sin vulnerar derechos fundamentales"],
                        knowledge_access=["general", "judicial", "ley"],
                        is_active_speaker=True
                    ),
                    CharacterConfig(
                        name="Fiscal Dña. Carmen Serrano",
                        role=CharacterRole.FISCAL,
                        personality="Incisiva, metódica, busca afianzar la acusación a través del rigor del informe pericial.",
                        objectives=["Demostrar que el acusado alteró las transferencias bancarias", "Comprobar que el hash SHA-256 no varió"],
                        knowledge_access=["general", "informe_pericial", "evidencia_forense"],
                        is_active_speaker=True
                    ),
                    CharacterConfig(
                        name="Letrado D. Jorge Valenzuela",
                        role=CharacterRole.ABOGADO_DEFENSA,
                        personality="Escéptico, agresivo en la repregunta, busca cualquier fallo en la cadena de custodia para anular la prueba.",
                        objectives=["Sembrar duda sobre la custodia del disco", "Alegar posible contaminación por software espía"],
                        knowledge_access=["general", "informe_pericial"],
                        is_active_speaker=True
                    ),
                    CharacterConfig(
                        name="Acusado D. Roberto Medina",
                        role=CharacterRole.PERSONA_JUZGADA,
                        personality="Silencioso, cabizbajo.",
                        objectives=["Permanecer a la espera de la resolución judicial"],
                        is_active_speaker=False,
                        avatar_type="monigote_gris"
                    )
                ],
                knowledge_base=[
                    KnowledgeDocument(
                        title="Acta Notarial de Cadena de Custodia SSD-981",
                        category="cadena_custodia",
                        content="El disco SSD Samsung EVO 1TB fue clonado bit a bit el día 12/03 con duplicadora Tableau Forensic TD2u. Hash SHA-256 origen: a7f8c9b2... Hash imagen E01: a7f8c9b2... Coincidencia 100%.",
                        tags=["general", "evidencia_forense", "informe_pericial"]
                    ),
                    KnowledgeDocument(
                        title="Normativa UNE 71506:2013 Metodologías de Análisis Forense",
                        category="ley_procesal",
                        content="Establece los requisitos para la adquisición, preservación y documentación de evidencias electrónicas garantizando la no alterabilidad.",
                        tags=["general", "ley", "judicial"]
                    )
                ],
                evaluation_criteria=[
                    EvaluationIndicator(
                        id="ind_01",
                        name="Garantía de Cadena de Custodia y Hashes",
                        category="rigor_tecnico",
                        description="Menciona y justifica el cotejo de hashes criptográficos (SHA-256/MD5) y uso de bloqueadores de escritura.",
                        expected_keywords=["hash", "sha-256", "bloqueador", "integridad", "clonación"],
                        penalized_keywords=["no sé", "no comprobé", "se me olvidó"]
                    ),
                    EvaluationIndicator(
                        id="ind_02",
                        name="Solvencia y Compostura Judicial",
                        category="comunicacion_judicial",
                        description="Tratamiento formal a Su Señoría y respuestas firmes sin caer en especulaciones no demostradas.",
                        expected_keywords=["señoría", "informe", "evidencia", "análisis", "metodología"],
                        penalized_keywords=["creo que", "supongo", "tal vez"]
                    )
                ]
            )
            self.save_case(case_audiencia)

        # 2. Caso Reunión con Cliente (Escenario 2)
        reunion_id = "caso_02_reunion_cliente_ransomware"
        if not os.path.exists(os.path.join(self.cases_dir, f"{reunion_id}.json")):
            case_reunion = CaseDefinition(
                case_id=reunion_id,
                title="Comité de Crisis: Presentación de Conclusiones de Incidente Ransomware",
                description="Reunión técnica y ejecutiva donde el perito debe explicar al Director General y al CISO cómo se produjo la intrusión y si hubo fuga de datos personales (RGPD).",
                scenario_type=ScenarioType.REUNION_CLIENTE,
                difficulty="avanzado",
                max_turns=5,
                characters=[
                    CharacterConfig(
                        name="D. Fernando Ortiz (CEO)",
                        role=CharacterRole.CLIENTE_DIRECTOR,
                        personality="Pragmático, preocupado por la continuidad de negocio, impacto económico y sanciones legales.",
                        objectives=["Conocer el impacto de la brecha", "Decidir si notificar a la Agencia de Protección de Datos"],
                        knowledge_access=["general", "ejecutivo"],
                        is_active_speaker=True
                    ),
                    CharacterConfig(
                        name="Dña. Elena Ramos (CISO)",
                        role=CharacterRole.CLIENTE_TECNICO,
                        personality="Técnica, detallista, busca conocer el vector inicial de ataque (PoC) y medidas de contención.",
                        objectives=["Entender el vector de entrada (phishing/RDP)", "Validar el aislamiento de la DMZ"],
                        knowledge_access=["general", "tecnico", "logs"],
                        is_active_speaker=True
                    )
                ],
                knowledge_base=[
                    KnowledgeDocument(
                        title="Informe de Triaje de Logs de Active Directory y Firewall",
                        category="informe_pericial",
                        content="Se detectó tráfico anómalo vía puerto 3389 (RDP) desde una IP de Tor hacia el servidor de ficheros principal a las 02:14 AM. No hubo exfiltración masiva demostrable gracias al bloqueo perimetral a las 03:00 AM.",
                        tags=["general", "tecnico", "logs"]
                    )
                ],
                evaluation_criteria=[
                    EvaluationIndicator(
                        id="ind_reunion_01",
                        name="Claridad Ejecutiva y Comunicación No Técnica",
                        category="comunicacion_ejecutiva",
                        description="Capacidad para traducir hallazgos técnicos complejos a impacto de negocio para la dirección.",
                        expected_keywords=["impacto", "notificación", "riesgo", "contención", "aepd"],
                        penalized_keywords=["no entiendo", "imposible saber"]
                    )
                ]
            )
            self.save_case(case_reunion)
