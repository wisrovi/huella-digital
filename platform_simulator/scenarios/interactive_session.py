"""
Motor de Escenarios Interactivos y Adaptativos para LEX VIRTUALIS™ / Huella Forense RPG.
Permite que el usuario seleccione cualquier personaje a encarnar (Perito, Abogado, Fiscal, etc.)
y orquesta la simulación judicial o corporativa en tiempo real.
Calcula adicionalmente para CADA mensaje los emoticonos / estados de reacción de TODOS los personajes
en escena (si están de acuerdo, en desacuerdo, enojados, escépticos, etc.), permitiendo que en el entorno
virtual 3D aparezcan sobre la cabeza de cada personaje sus respectivas reacciones.
"""

from __future__ import annotations
import uuid
from typing import List, Dict, Tuple, Optional
from platform_simulator.agents.langchain_runner import (
    ScenarioCase, Character, AvatarVisual, InteractionMessage, LangChainAgentRunner
)
from platform_simulator.rag.chroma_engine import ChromaRAGEngine, RAGDocument

class InteractiveScenarioSession:
    def __init__(self, session_id: str, case: ScenarioCase, user_role: str, user_name: str, rag_engine: ChromaRAGEngine):
        self.session_id = session_id
        self.case = case
        self.user_role = user_role
        self.user_name = user_name
        self.rag_engine = rag_engine
        self.history: List[InteractionMessage] = []
        self.current_turn = 0
        self.is_completed = False
        
        # Configurar personajes marcando al controlado por el usuario
        self.agents: Dict[str, LangChainAgentRunner] = {}
        for char in self.case.characters:
            char_copy = char.model_copy()
            if char_copy.role == self.user_role:
                char_copy.is_user_controlled = True
                char_copy.name = f"{self.user_name} (Tú)"
            else:
                char_copy.is_user_controlled = False
            self.agents[char_copy.id] = LangChainAgentRunner(char_copy, self.rag_engine, self.case.case_id)

    def _compute_court_reactions(self, speaker_role: str, text: str) -> Dict[str, Dict[str, str]]:
        """
        Calcula cómo reacciona CADA personaje en la sala ante lo que dice el orador.
        Retorna: { role: { 'emoji': '😠', 'status': 'En desacuerdo / Enojado', 'state': 'disagree' } }
        """
        reactions = {}
        text_lower = text.lower()
        has_hash = any(t in text_lower for t in ["hash", "sha-256", "sha256", "duplicadora", "tableau"])
        has_protesta = any(t in text_lower for t in ["protesto", "objeción", "impugno", "inadmisible"])
        has_duda = any(t in text_lower for t in ["creo", "tal vez", "quizas", "no sé", "duda"])

        for char in self.case.characters:
            r = char.role
            if r == speaker_role:
                reactions[r] = {"emoji": "🗣️", "status": "Interviniendo en sala", "state": "speaking"}
                continue

            if r == "juez":
                if has_protesta:
                    reactions[r] = {"emoji": "⚖️", "status": "Atendiendo protesta formal", "state": "strict"}
                elif has_duda:
                    reactions[r] = {"emoji": "🤨", "status": "Escéptico ante la vacilación", "state": "skeptical"}
                elif has_hash:
                    reactions[r] = {"emoji": "🧐", "status": "Examinando rigor probatorio", "state": "evaluating"}
                else:
                    reactions[r] = {"emoji": "👨‍⚖️", "status": "Atento y neutral", "state": "neutral"}

            elif r in ["fiscal", "abogado_acusacion"]:
                if speaker_role in ["abogado_defensa", "persona_juzgada"]:
                    reactions[r] = {"emoji": "😠", "status": "En desacuerdo / Beligerante", "state": "angry"}
                elif speaker_role == "estudiante_perito":
                    reactions[r] = {"emoji": "🤔" if not has_hash else "😏", "status": "Fiscalizando minuciosamente", "state": "questioning"}
                else:
                    reactions[r] = {"emoji": "👂", "status": "Escuchando al tribunal", "state": "listening"}

            elif r == "abogado_defensa":
                if speaker_role in ["fiscal", "abogado_acusacion"]:
                    reactions[r] = {"emoji": "😡", "status": "Disconforme / A la defensiva", "state": "opposed"}
                elif speaker_role == "estudiante_perito":
                    reactions[r] = {"emoji": "😌" if has_hash else "😰", "status": "Buscando beneficio para el reo", "state": "analyzing"}
                else:
                    reactions[r] = {"emoji": "🧐", "status": "Pendiente de la resolución judicial", "state": "attentive"}

            elif r == "persona_juzgada":
                if speaker_role in ["fiscal", "abogado_acusacion"]:
                    reactions[r] = {"emoji": "😨", "status": "Preocupado en el banquillo", "state": "fearful"}
                elif speaker_role == "abogado_defensa":
                    reactions[r] = {"emoji": "🙏", "status": "Esperanzado", "state": "hopeful"}
                else:
                    reactions[r] = {"emoji": "😐", "status": "Silencioso", "state": "passive"}

            elif r in ["cliente_director", "cliente_tecnico"]:
                if has_hash or "contención" in text_lower:
                    reactions[r] = {"emoji": "😊", "status": "Aliviado", "state": "pleased"}
                else:
                    reactions[r] = {"emoji": "😰", "status": "Alerta / Preocupado por impacto", "state": "alarmed"}

            else:
                reactions[r] = {"emoji": "👀", "status": "Observando el debate", "state": "neutral"}

        return reactions

    def start_session(self) -> List[InteractionMessage]:
        opening_msgs = []
        if self.case.scenario_type.value == "audiencia":
            judge_agent = next((a for a in self.agents.values() if a.character.role == "juez"), None)
            fiscal_agent = next((a for a in self.agents.values() if a.character.role == "fiscal"), None)
            defense_agent = next((a for a in self.agents.values() if a.character.role == "abogado_defensa"), None)

            # 1. Apertura solemne del Juez
            if judge_agent:
                judge_opening = InteractionMessage(
                    speaker_id=judge_agent.character.id,
                    speaker_name=judge_agent.character.name,
                    speaker_role="juez",
                    content=(
                        f"Se abre la sesión en la causa de autos sobre '{self.case.title}'. "
                        f"Este tribunal exige estricto rigor probatorio a las partes. Comparece {self.user_name} asumiendo el rol de '{self.user_role}'. "
                        f"Tiene la palabra el Ministerio Fiscal para formular su posición inicial, y seguidamente la Defensa técnica."
                    ),
                    animation="speaking",
                    emotion_tag="[Solemne & Ecuánime]",
                    emotion_intensity=0.85,
                    facial_expression="serious",
                    internal_thought="La sala debe determinar si la cadena de custodia y el clonado digital cumplen la legalidad o adolecen de nulidad.",
                    court_reactions=self._compute_court_reactions("juez", "Apertura solemne de sala")
                )
                self.history.append(judge_opening)
                opening_msgs.append(judge_opening)

            # 2. El Ministerio Fiscal expone y cede la palabra (si no es el usuario)
            if fiscal_agent and not fiscal_agent.character.is_user_controlled:
                f_reply, f_emotion = fiscal_agent.llm_provider.generate_dialogue_with_emotion(
                    character_name=fiscal_agent.character.name,
                    character_role=fiscal_agent.character.role,
                    personality=fiscal_agent.character.personality,
                    objectives=fiscal_agent.character.objectives,
                    system_prompt=fiscal_agent.character.system_prompt,
                    rag_context=["[Acta Notarial SSD]: Clonado bit a bit realizado con duplicadora certificada."],
                    history_dialogues=[{"speaker": judge_opening.speaker_name, "role": "juez", "text": judge_opening.content}],
                    user_input="Apertura del juicio oral y presentación de pruebas de cargo",
                    user_role=self.user_role,
                    turn_number=1,
                    is_closing=False
                )
                fiscal_msg = InteractionMessage(
                    speaker_id=fiscal_agent.character.id,
                    speaker_name=fiscal_agent.character.name,
                    speaker_role="fiscal",
                    content=f"{f_reply} Doy la palabra a la defensa para que formule sus cuestiones previas.",
                    animation="speaking",
                    emotion_tag=f_emotion.sentiment_tag,
                    emotion_intensity=f_emotion.intensity,
                    facial_expression=f_emotion.facial_expression,
                    internal_thought=f_emotion.internal_thought,
                    court_reactions=self._compute_court_reactions("fiscal", f_reply)
                )
                self.history.append(fiscal_msg)
                opening_msgs.append(fiscal_msg)

            # 3. La Defensa interviene de forma concisa si no es el usuario
            if defense_agent and not defense_agent.character.is_user_controlled and self.user_role != "abogado_defensa":
                d_reply, d_emotion = defense_agent.llm_provider.generate_dialogue_with_emotion(
                    character_name=defense_agent.character.name,
                    character_role=defense_agent.character.role,
                    personality=defense_agent.character.personality,
                    objectives=defense_agent.character.objectives,
                    system_prompt=defense_agent.character.system_prompt,
                    rag_context=["[UNE 71506]: Requiere verificación estricta de bloqueadores y sellado de tiempo."],
                    history_dialogues=[{"speaker": m.speaker_name, "role": m.speaker_role, "text": m.content} for m in self.history],
                    user_input="Cuestiones previas de la defensa sobre posible alteración del soporte",
                    user_role=self.user_role,
                    turn_number=1,
                    is_closing=False
                )
                def_msg = InteractionMessage(
                    speaker_id=defense_agent.character.id,
                    speaker_name=defense_agent.character.name,
                    speaker_role="abogado_defensa",
                    content=d_reply,
                    animation="speaking",
                    emotion_tag=d_emotion.sentiment_tag,
                    emotion_intensity=d_emotion.intensity,
                    facial_expression=d_emotion.facial_expression,
                    internal_thought=d_emotion.internal_thought,
                    court_reactions=self._compute_court_reactions("abogado_defensa", d_reply)
                )
                self.history.append(def_msg)
                opening_msgs.append(def_msg)

        else:
            director_agent = next((a for a in self.agents.values() if "cliente" in a.character.role), None)
            if director_agent:
                msg = InteractionMessage(
                    speaker_id=director_agent.character.id,
                    speaker_name=director_agent.character.name,
                    speaker_role=director_agent.character.role,
                    content=f"Buenos días a todos. Damos inicio a este comité de crisis urgente sobre el incidente reportado.",
                    animation="speaking",
                    emotion_tag="[Preocupado]",
                    emotion_intensity=0.85,
                    facial_expression="worried",
                    internal_thought="La continuidad de la compañía y el riesgo de sanción RGPD dependen de esta reunión.",
                    court_reactions=self._compute_court_reactions(director_agent.character.role, "Apertura de comité")
                )
                self.history.append(msg)
                opening_msgs.append(msg)

        return opening_msgs

    def submit_user_action(self, user_text: str) -> Tuple[InteractionMessage, List[InteractionMessage]]:
        if self.is_completed:
            raise ValueError("La sesión interactiva ya ha concluido.")

        self.current_turn += 1
        is_final_turn = (self.current_turn >= self.case.max_turns)

        # 1. Mensaje del usuario con las reacciones que provocó en el resto de la sala
        user_reactions = self._compute_court_reactions(self.user_role, user_text)
        user_msg = InteractionMessage(
            speaker_id="user_player",
            speaker_name=f"{self.user_name} ({self.user_role.upper()})",
            speaker_role=self.user_role,
            content=user_text,
            animation="speaking",
            emotion_tag="[Intervención Activa]",
            emotion_intensity=0.8,
            facial_expression="confident",
            court_reactions=user_reactions
        )
        self.history.append(user_msg)

        # 2. Análisis por los demás personajes en escena y réplicas en concordancia
        responses: List[InteractionMessage] = []
        active_ai_agents = [
            a for a in self.agents.values()
            if not a.character.is_user_controlled and a.character.is_active_speaker and a.character.role != "persona_juzgada"
        ]

        # Si la pregunta es abierta o sobre acusación/culpabilidad/pruebas, tanto la fiscalía como la defensa replican
        user_lower = user_text.lower()
        is_broad_inquiry = any(k in user_lower for k in ["por qué", "porque", "acus", "culpab", "delito", "hecho", "prueba", "evidencia", "rat", "hash", "cadena"])
        
        agents_to_speak = []
        if is_broad_inquiry and len(active_ai_agents) > 1:
            # Hablan los agentes activos en orden de confrontación
            agents_to_speak = active_ai_agents
        elif active_ai_agents:
            chosen_agent = active_ai_agents[(self.current_turn - 1) % len(active_ai_agents)]
            agents_to_speak = [chosen_agent]

        for ag in agents_to_speak:
            ai_msg = ag.generate_turn_response(
                self.history, user_text, self.user_role,
                turn_number=self.current_turn,
                is_closing=is_final_turn
            )
            ai_msg.court_reactions = self._compute_court_reactions(ai_msg.speaker_role, ai_msg.content)
            self.history.append(ai_msg)
            responses.append(ai_msg)


        # 3. Intervención aclaratoria del Magistrado Juez o Veredicto Final
        judge_agent = next((a for a in self.agents.values() if a.character.role == "juez"), None)
        first_speaker_role = agents_to_speak[0].character.role if agents_to_speak else ""
        if judge_agent and not judge_agent.character.is_user_controlled and first_speaker_role != "juez":
            if is_final_turn:
                self.is_completed = True
                verdict_msg = judge_agent.generate_turn_response(
                    self.history, user_text, self.user_role,
                    turn_number=self.current_turn,
                    is_closing=True
                )
                verdict_msg.speaker_name = f"{judge_agent.character.name} (VEREDICTO FINAL)"
                verdict_msg.court_reactions = self._compute_court_reactions("juez", verdict_msg.content)
                self.history.append(verdict_msg)
                responses.append(verdict_msg)
            elif self.current_turn % 2 == 0:
                judge_moderation = judge_agent.generate_turn_response(
                    self.history, user_text, self.user_role,
                    turn_number=self.current_turn,
                    is_closing=False
                )
                judge_moderation.court_reactions = self._compute_court_reactions("juez", judge_moderation.content)
                self.history.append(judge_moderation)
                responses.append(judge_moderation)

        return user_msg, responses
