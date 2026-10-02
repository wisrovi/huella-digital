"""
Motor de Valoración del Estudiante y Generación de Feedback Multidimensional.
Analiza la interacción, aplica indicadores definidos por Huella Forense
y genera un reporte de evaluación cuantitativo y cualitativo detallado.
"""

from __future__ import annotations
from typing import List, Dict, Any
import re
from huella_forense.models.schemas import (
    CaseDefinition, Message, EvaluationReport, TurnFeedback, CharacterRole
)

class EvaluationEngine:
    def __init__(self, case: CaseDefinition):
        self.case = case

    def evaluate_session(self, session_id: str, student_id: str, history: List[Message]) -> EvaluationReport:
        # Extraer únicamente los turnos del estudiante
        student_messages = [m for m in history if m.speaker_role == CharacterRole.PERITO_ESTUDIANTE.value]

        if not student_messages:
            return EvaluationReport(
                session_id=session_id,
                case_id=self.case.case_id,
                student_id=student_id,
                global_score=0.0,
                category_scores={},
                indicator_scores={},
                qualitative_feedback="No se registraron intervenciones por parte del estudiante.",
                identified_strengths=[],
                actionable_recommendations=["Debe participar activamente en la simulación respondiendo a las preguntas."]
            )

        indicator_scores: Dict[str, float] = {}
        category_scores_acc: Dict[str, List[float]] = {}
        all_student_text = " ".join([m.content.lower() for m in student_messages])

        # 1. Evaluar cada indicador del caso
        for ind in self.case.evaluation_criteria:
            score = 70.0  # Base estándar
            
            # Puntuación por presencia de conceptos técnicos / palabras clave requeridas
            if ind.expected_keywords:
                matched = sum(1 for kw in ind.expected_keywords if kw.lower() in all_student_text)
                ratio = matched / len(ind.expected_keywords)
                # Escalar de 50 a 100 en función de aciertos
                score = 50.0 + (ratio * 50.0)

            # Penalización por términos de riesgo o falta de rigor
            if ind.penalized_keywords:
                penalized_hits = sum(1 for kw in ind.penalized_keywords if kw.lower() in all_student_text)
                score = max(20.0, score - (penalized_hits * 15.0))

            indicator_scores[ind.name] = round(score, 1)

            if ind.category not in category_scores_acc:
                category_scores_acc[ind.category] = []
            category_scores_acc[ind.category].append(score)

        # 2. Promedios por categoría
        category_scores: Dict[str, float] = {}
        for cat, scs in category_scores_acc.items():
            category_scores[cat] = round(sum(scs) / len(scs), 1)

        # 3. Nota global ponderada
        if indicator_scores:
            global_score = round(sum(indicator_scores.values()) / len(indicator_scores), 1)
        else:
            global_score = 75.0

        # 4. Análisis turno por turno
        turn_analysis: List[TurnFeedback] = []
        strengths = []
        improvements = []

        for idx, s_msg in enumerate(student_messages, 1):
            text = s_msg.content.lower()
            words_count = len(text.split())
            turn_score = 70.0
            turn_strengths = []
            turn_needs = []

            if words_count > 30:
                turn_score += 15.0
                turn_strengths.append("Argumentación detallada y formal")
            elif words_count < 10:
                turn_score -= 20.0
                turn_needs.append("Respuesta demasiado breve; falta fundamentación técnica")

            if any(term in text for term in ["hash", "sha-256", "sha256", "md5", "bloqueador"]):
                turn_score += 15.0
                turn_strengths.append("Garantía explícita de integridad criptográfica")
            else:
                turn_needs.append("No menciona explícitamente el cotejo de hashes ni herramientas forenses")

            if "creo que" in text or "tal vez" in text or "no estoy seguro" in text:
                turn_score -= 15.0
                turn_needs.append("Inseguridad en el testimonio pericial; usar afirmaciones basadas en hechos contrastables")

            turn_score = max(10.0, min(100.0, turn_score))
            turn_analysis.append(
                TurnFeedback(
                    turn_index=idx,
                    score=round(turn_score, 1),
                    strengths=turn_strengths,
                    areas_to_improve=turn_needs,
                    comments=f"Turno #{idx}: evaluación de claridad probatoria y solidez forense."
                )
            )

        # Consolidar fortalezas y áreas de mejora
        if global_score >= 80.0:
            strengths.append("Excelente dominio terminológico y solvencia procesal ante objeciones.")
            strengths.append("Preservación impecable de la cadena de custodia y principios de la evidencia digital.")
        elif global_score >= 60.0:
            strengths.append("Conocimiento básico del procedimiento forense adecuado.")
            improvements.append("Reforzar la precisión al justificar la metodología de clonación bit a bit.")
        else:
            improvements.append("Se detectan dudas metodológicas graves sobre la inviolabilidad de la evidencia.")
            improvements.append("Es necesario estudiar la norma UNE 71506 / ISO/IEC 27037 antes de acudir a sede judicial.")

        recommendations = [
            "Practicar la exposición oral sin titubeos, refiriéndose siempre a los folios y anexos del informe pericial.",
            "Recordar que el perito es un auxiliar técnico imparcial del tribunal, no un defensor ni un acusador.",
            "Detallar siempre la marca, modelo y número de serie del bloqueador de escritura y medios de almacenamiento empleados."
        ]

        qualitative = (
            f"El estudiante completó la simulación con un desempeño general calificado en {global_score}/100. "
            f"Demostró {'un sólido' if global_score >= 75 else 'un aceptable'} control del marco forense. "
            "Se valoró especialmente el manejo del vocabulario probatorio y la respuesta a los cuestionamientos de la contraparte."
        )

        return EvaluationReport(
            session_id=session_id,
            case_id=self.case.case_id,
            student_id=student_id,
            global_score=global_score,
            category_scores=category_scores,
            indicator_scores=indicator_scores,
            qualitative_feedback=qualitative,
            identified_strengths=strengths,
            actionable_recommendations=recommendations,
            turn_by_turn_analysis=turn_analysis
        )
