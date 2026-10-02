"""
Lógica del Escenario Virtual y Máquina de Estados de la Audiencia / Reunión.
Gestiona el turno de palabra, intervenciones, orden judicial y registro de la interacción.
"""

from __future__ import annotations
from typing import List, Dict, Optional, Tuple
import datetime
from huella_forense.models.schemas import (
    CaseDefinition, Message, CharacterRole, CharacterConfig, ScenarioType
)
from huella_forense.knowledge.repository import KnowledgeRepository
from huella_forense.scenarios.agent_orchestrator import CharacterAgent

class SimulationSession:
    """
    Sesión activa de simulación con un estudiante.
    Maneja el flujo de la vista/audiencia o reunión con el cliente.
    """
    def __init__(self, session_id: str, case: CaseDefinition, student_id: str, student_name: str = "Perito Forense"):
        self.session_id = session_id
        self.case = case
        self.student_id = student_id
        self.student_name = student_name
        self.history: List[Message] = []
        self.current_turn = 0
        self.is_completed = False
        
        # Repositorio de conocimiento
        self.knowledge_repo = KnowledgeRepository()
        for doc in case.knowledge_base:
            self.knowledge_repo.add_document(case.case_id, doc)
            
        # Agentes
        self.agents: Dict[str, CharacterAgent] = {}
        for char in case.characters:
            self.agents[char.id] = CharacterAgent(char, self.knowledge_repo, case.case_id)

    def start_session(self) -> List[Message]:
        """
        Apertura de la sesión según el escenario (ej. el Juez abre la sesión o el Cliente da la bienvenida).
        """
        opening_messages = []
        if self.case.scenario_type == ScenarioType.AUDIENCIA:
            juez_config = next((c for c in self.case.characters if c.role == CharacterRole.JUEZ), None)
            if juez_config:
                msg = Message(
                    speaker_id=juez_config.id,
                    speaker_name=juez_config.name,
                    speaker_role=juez_config.role.value,
                    content=(
                        f"Se abre la sesión en el procedimiento de referencia judicial sobre '{self.case.title}'. "
                        f"Comparece ante este tribunal D./Dña. {self.student_name} en calidad de perito informático forense. "
                        "Tiene la palabra el Ministerio Fiscal para iniciar el interrogatorio pericial."
                    )
                )
                self.history.append(msg)
                opening_messages.append(msg)
        elif self.case.scenario_type == ScenarioType.REUNION_CLIENTE:
            client_config = next((c for c in self.case.characters if c.role == CharacterRole.CLIENTE_DIRECTOR), self.case.characters[0])
            msg = Message(
                speaker_id=client_config.id,
                speaker_name=client_config.name,
                speaker_role=client_config.role.value,
                content=(
                    f"Buenos días. Gracias por acudir a esta reunión de emergencia tras el incidente. "
                    f"Necesitamos que nos exponga las conclusiones principales de la auditoría e intrusión detectada."
                )
            )
            self.history.append(msg)
            opening_messages.append(msg)

        return opening_messages

    def submit_student_turn(self, student_input: str) -> Tuple[Message, List[Message]]:
        """
        Procesa la respuesta del estudiante y genera las réplicas del tribunal/cliente.
        """
        if self.is_completed:
            raise ValueError("La sesión de simulación ya ha concluido.")

        self.current_turn += 1

        # 1. Registrar mensaje del estudiante
        student_msg = Message(
            speaker_id=self.student_id,
            speaker_name=self.student_name,
            speaker_role=CharacterRole.PERITO_ESTUDIANTE.value,
            content=student_input
        )
        self.history.append(student_msg)

        # 2. Determinar quién interviene según la ronda y el escenario
        active_responses: List[Message] = []
        
        # En Audiencia: alternancia entre Fiscal, Abogado Defensa y moderación del Juez
        if self.case.scenario_type == ScenarioType.AUDIENCIA:
            # Seleccionar interlocutor activo
            active_chars = [c for c in self.case.characters if c.is_active_speaker and c.role != CharacterRole.PERSONA_JUZGADA]
            
            # Rotación orgánica: Fiscal -> Abogado -> Juez
            if self.current_turn % 3 == 1:
                target_role = CharacterRole.FISCAL
            elif self.current_turn % 3 == 2:
                target_role = CharacterRole.ABOGADO_DEFENSA
            else:
                target_role = CharacterRole.JUEZ

            chosen_char = next((c for c in active_chars if c.role == target_role), active_chars[0])
            agent = self.agents[chosen_char.id]
            resp_text = agent.generate_response(self.history, student_input)
            
            bot_msg = Message(
                speaker_id=chosen_char.id,
                speaker_name=chosen_char.name,
                speaker_role=chosen_char.role.value,
                content=resp_text
            )
            self.history.append(bot_msg)
            active_responses.append(bot_msg)

        elif self.case.scenario_type == ScenarioType.REUNION_CLIENTE:
            # Alternar entre directivo y perfil técnico del cliente
            active_chars = [c for c in self.case.characters if c.is_active_speaker]
            chosen_char = active_chars[(self.current_turn - 1) % len(active_chars)]
            agent = self.agents[chosen_char.id]
            resp_text = agent.generate_response(self.history, student_input)
            
            bot_msg = Message(
                speaker_id=chosen_char.id,
                speaker_name=chosen_char.name,
                speaker_role=chosen_char.role.value,
                content=resp_text
            )
            self.history.append(bot_msg)
            active_responses.append(bot_msg)

        # Comprobar si se ha llegado al límite de turnos del caso
        if self.current_turn >= self.case.max_turns:
            self.is_completed = True
            closing_msg = Message(
                speaker_id="system",
                speaker_name="Tribunal / Presidencia",
                speaker_role="moderador",
                content="Habiéndose cumplido el objeto de la comparecencia, se da por finalizada la sesión pericial. Queda vista para resolución y evaluación."
            )
            self.history.append(closing_msg)
            active_responses.append(closing_msg)

        return student_msg, active_responses

    def finish_session(self):
        self.is_completed = True
