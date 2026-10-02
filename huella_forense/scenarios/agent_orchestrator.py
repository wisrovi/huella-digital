"""
Orquestador de Personajes e Inferencia IA.
Soporta agentes autónomos basados en LLM (vía OpenAI/Anthropic/Local LLM o modo determinista simulado).
Asegura que cada personaje actúe estrictamente dentro de su rol, objetivos y acceso a información.
"""

from __future__ import annotations
from typing import List, Dict, Optional, Any
from huella_forense.models.schemas import CharacterConfig, CharacterRole, Message, CaseDefinition
from huella_forense.knowledge.repository import KnowledgeRepository

class CharacterAgent:
    """
    Representa un personaje activo en la simulación (Juez, Fiscal, Abogado, etc.).
    """
    def __init__(self, config: CharacterConfig, knowledge_repo: KnowledgeRepository, case_id: str):
        self.config = config
        self.knowledge_repo = knowledge_repo
        self.case_id = case_id

    def build_system_prompt(self, context_summary: str) -> str:
        prompt = (
            f"Eres {self.config.name}, desempeñando el rol de '{self.config.role.value}' en una simulación forense judicial/profesional.\n"
            f"Personalidad y Tono: {self.config.personality}\n"
            f"Tus Objetivos en este caso:\n" + "\n".join([f"- {obj}" for obj in self.config.objectives]) + "\n"
            f"Contexto general del caso:\n{context_summary}\n"
            "INSTRUCCIONES CLAVE:\n"
            "1. Mantén estrictamente tu personaje y autoridad procesal.\n"
            "2. Evalúa las declaraciones del perito forense (el estudiante). Exige rigor técnico, cadenas de custodia, hashes, metodologías forenses (ISO/IEC 27037).\n"
            "3. Si eres Juez: modera la sala, haz cumplir el orden procesal y formula preguntas de aclaración.\n"
            "4. Si eres Fiscal o Abogado Acusador: formula preguntas incisivas, busca contradicciones o fallos en el informe pericial.\n"
            "5. Si eres Abogado Defensor: apoya las tesis favorables a tu cliente o cuestiona la validez de las pruebas de cargo.\n"
            "6. Sé conciso y directo en tus turnos (máximo 2 o 3 párrafos).\n"
        )
        return prompt

    def generate_response(self, conversation_history: List[Message], student_last_input: str) -> str:
        """
        Genera la réplica o pregunta del personaje.
        Combina RAG (documentos relevantes) + lógica contextual del rol.
        """
        if not self.config.is_active_speaker:
            return f"[{self.config.name} ({self.config.role.value}) permanece en silencio y atento a la audiencia]."

        # Búsqueda de conocimiento relevante para el turno
        relevant_docs = self.knowledge_repo.search_relevant_context(
            case_id=self.case_id,
            query=student_last_input,
            allowed_tags=self.config.knowledge_access,
            top_k=2
        )
        context_snippets = [f"[{d.title}]: {d.content[:300]}..." for d in relevant_docs]
        context_str = "\n".join(context_snippets) if context_snippets else "Sin evidencia específica adicional."

        # Motor de respuesta heurística / LLM fallback
        return self._heuristic_or_llm_response(student_last_input, context_str, conversation_history)

    def _heuristic_or_llm_response(self, student_input: str, context: str, history: List[Message]) -> str:
        """
        Generador robusto para pruebas y ejecución determinista / extensible a LLMs remotos.
        """
        text_lower = student_input.lower()
        role = self.config.role

        if role == CharacterRole.JUEZ:
            if "objeción" in text_lower or "protesto" in text_lower:
                return f"{self.config.name}: 'Concedida. Señor perito, limítese a contestar sobre los hechos técnicos verificados en su informe pericial.'"
            elif len(student_input.strip()) < 15:
                return f"{self.config.name}: 'Señor perito, su respuesta ha sido excesivamente escueta. La sala requiere precisión técnica. ¿Podría detallar el procedimiento seguido?'"
            elif "hash" in text_lower or "cadena de custodia" in text_lower or "sha256" in text_lower:
                return f"{self.config.name}: 'Tomo nota de la verificación de integridad criptográfica. Señor fiscal, puede continuar con su interrogatorio.'"
            else:
                return f"{self.config.name}: 'Entendido su punto, perito. No obstante, le recuerdo que debe ceñirse a las evidencias analizadas. Abogado, tiene la palabra.'"

        elif role in [CharacterRole.FISCAL, CharacterRole.ABOGADO_ACUSACION]:
            if "hash" not in text_lower and "integridad" not in text_lower and len(history) <= 3:
                return f"{self.config.name}: 'Con la venia de Su Señoría. Perito, ¿puede usted acreditar documentalmente si se calculó el valor hash SHA-256 en el momento exacto del volcado de la memoria RAM o del disco?'"
            elif "volcado" in text_lower or "adquisición" in text_lower:
                return f"{self.config.name}: 'Afirma usted que realizó la adquisición... ¿Utilizó un bloqueador de escritura por hardware o software? ¿Cómo nos asegura que la evidencia no fue alterada durante el proceso?'"
            else:
                return f"{self.config.name}: 'Señor perito, consta en autos cierta discrepancia horaria en los logs de acceso. ¿Se realizó la debida normalización con respecto a la zona horaria UTC del servidor implicado?'"

        elif role == CharacterRole.ABOGADO_DEFENSA:
            if "duda" in text_lower or "posible" in text_lower or "hipótesis" in text_lower:
                return f"{self.config.name}: 'Efectivamente, perito. Como usted acaba de admitir, existe un margen de incertidumbre. ¿No es factible que una infección por malware previo causara esos registros anómalos?'"
            else:
                return f"{self.config.name}: 'Agradezco su aclaración. Queda acreditado entonces que no existen indicios concluyentes de manipulación directa imputable a mi defendido.'"

        elif role in [CharacterRole.CLIENTE_DIRECTOR, CharacterRole.CLIENTE_TECNICO]:
            if "coste" in text_lower or "impacto" in text_lower or "exfiltración" in text_lower:
                return f"{self.config.name}: 'Comprendo la gravedad técnica del incidente. En términos de negocio, ¿qué volumen exacto de datos de clientes pudo verse comprometido y cuál es la recomendación urgente para la AEPD?'"
            else:
                return f"{self.config.name}: 'Gracias por el informe forense preliminar. ¿Cuáles son los siguientes pasos de remediación para que nuestros servidores de producción sean seguros?'"

        return f"{self.config.name}: 'He escuchado con atención su exposición. Prosigamos con el análisis de los puntos clave del informe pericial.'"
