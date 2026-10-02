"""
Modelos de Dominio y LangChain Chains para los Agentes Autónomos.
Permite que el usuario adopte cualquier rol (Perito, Abogado, Juez, Fiscal, Cliente)
mientras la IA orquesta autónomamente a los personajes restantes con RAG vectorial en ChromaDB.
"""

from __future__ import annotations
import uuid
import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from platform_simulator.rag.chroma_engine import ChromaRAGEngine

class ScenarioType(str, Enum):
    AUDIENCIA = "audiencia"
    REUNION_CLIENTE = "reunion_cliente"
    INSPECCION_OCULAR = "inspeccion_ocular"

class AvatarVisual(BaseModel):
    avatar_id: str
    model_3d_type: str = "avatar_3d"  # 'avatar_3d_judge', 'avatar_3d_lawyer', 'avatar_3d_fiscal', 'monigote_gris'
    mesh_color: str = "#38bdf8"
    animation_state: str = "idle"  # 'idle', 'speaking', 'objecting', 'listening', 'thinking'
    expression: str = "neutral"  # 'neutral', 'serious', 'skeptical', 'approving'

class Character(BaseModel):
    id: str
    name: str
    role: str  # 'juez', 'fiscal', 'abogado_defensa', 'abogado_acusacion', 'persona_juzgada', 'cliente_director', 'cliente_tecnico', 'estudiante_perito'
    personality: str
    system_prompt: str
    objectives: List[str] = Field(default_factory=list)
    is_active_speaker: bool = True
    is_user_controlled: bool = False  # Si el usuario toma el control de este personaje
    avatar: AvatarVisual

class ScenarioCase(BaseModel):
    case_id: str
    title: str
    scenario_type: ScenarioType
    description: str
    environment_3d: str = "courtroom_classic"  # 'courtroom_classic', 'boardroom_executive', 'forensic_lab'
    difficulty: str = "intermedio"
    characters: List[Character]
    max_turns: int = 10
    eval_indicators: List[Dict[str, Any]] = Field(default_factory=list)

class InteractionMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    speaker_id: str
    speaker_name: str
    speaker_role: str
    content: str
    animation: str = "speaking"
    emotion_tag: str = "[Neutral]"
    emotion_intensity: float = 0.5
    facial_expression: str = "neutral"
    internal_thought: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    retrieved_context: List[str] = Field(default_factory=list)
    court_reactions: Dict[str, Dict[str, str]] = Field(default_factory=dict)

from platform_simulator.agents.dynamic_llm import DynamicLLMProvider, EmotionState

class LangChainAgentRunner:
    """
    Agente que encapsula la lógica conversacional guiada por RAG con ChromaDB y LLM dinámico con emociones.
    """
    def __init__(self, character: Character, rag_engine: ChromaRAGEngine, case_id: str, llm_provider: Optional[DynamicLLMProvider] = None):
        self.character = character
        self.rag_engine = rag_engine
        self.case_id = case_id
        self.llm_provider = llm_provider or DynamicLLMProvider()

    def generate_turn_response(self, history: List[InteractionMessage], user_input: str, user_role: str, turn_number: int = 1, is_closing: bool = False) -> InteractionMessage:
        if not self.character.is_active_speaker or self.character.is_user_controlled:
            return InteractionMessage(
                speaker_id=self.character.id,
                speaker_name=self.character.name,
                speaker_role=self.character.role,
                content=f"[{self.character.name} permanece en silencio procesal].",
                animation="idle",
                emotion_tag="[Silencio]",
                internal_thought="Observo en silencio."
            )

        # 1. Recuperar contexto vectorial semántico mediante ChromaDB
        relevant_docs = self.rag_engine.query_context(
            case_id=self.case_id,
            query=user_input,
            requester_role=self.character.role,
            top_k=2
        )
        context_snippets = [f"[{d['title']}]: {d['content'][:250]}..." for d in relevant_docs]

        # 2. Formatear historial conversacional para el LLM
        history_dicts = [
            {"speaker": m.speaker_name, "role": m.speaker_role, "text": m.content}
            for m in history
        ]

        # 3. Generar diálogo dinámicamente con inferencia de emoción
        reply_content, emotion = self.llm_provider.generate_dialogue_with_emotion(
            character_name=self.character.name,
            character_role=self.character.role,
            personality=self.character.personality,
            objectives=self.character.objectives,
            system_prompt=self.character.system_prompt,
            rag_context=context_snippets,
            history_dialogues=history_dicts,
            user_input=user_input,
            user_role=user_role,
            turn_number=turn_number,
            is_closing=is_closing
        )

        # Determinar animación
        animation = "speaking"
        if emotion.facial_expression in ["angry", "doubtful"] or "protesto" in reply_content.lower():
            animation = "objecting"
        elif emotion.facial_expression == "worried":
            animation = "thinking"

        return InteractionMessage(
            speaker_id=self.character.id,
            speaker_name=self.character.name,
            speaker_role=self.character.role,
            content=reply_content,
            animation=animation,
            emotion_tag=emotion.sentiment_tag,
            emotion_intensity=emotion.intensity,
            facial_expression=emotion.facial_expression,
            internal_thought=emotion.internal_thought,
            retrieved_context=context_snippets
        )
