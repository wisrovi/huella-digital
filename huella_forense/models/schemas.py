"""
Modelos de dominio central para la plataforma de simulación Huella Forense.
Diseñados con Pydantic v2 para tipado estricto, serialización y validación.
"""

from __future__ import annotations
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import uuid
import datetime

class ScenarioType(str, Enum):
    AUDIENCIA = "audiencia"
    REUNION_CLIENTE = "reunion_cliente"

class CharacterRole(str, Enum):
    # Escenario Audiencia
    JUEZ = "juez"
    FISCAL = "fiscal"
    ABOGADO_DEFENSA = "abogado_defensa"
    ABOGADO_ACUSACION = "abogado_acusacion"
    PERSONA_JUZGADA = "persona_juzgada"  # Rol pasivo / dummy
    # Escenario Reunión Cliente
    CLIENTE_DIRECTOR = "cliente_director"
    CLIENTE_TECNICO = "cliente_tecnico"
    # General
    PERITO_ESTUDIANTE = "estudiante"

class CharacterConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: CharacterRole
    personality: str = Field(..., description="Tono y estilo de comportamiento del personaje")
    objectives: List[str] = Field(default_factory=list, description="Objetivos específicos del rol en este caso")
    knowledge_access: List[str] = Field(default_factory=list, description="IDs o etiquetas de conocimiento que este personaje conoce")
    is_active_speaker: bool = Field(True, description="Si interviene activamente o es pasivo (ej. monigote gris)")
    system_prompt: Optional[str] = None
    avatar_type: str = "standard"  # 'monigote_gris' para acusado, 'avatar_3d', etc.

class KnowledgeDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    category: str  # 'evidencia_forense', 'ley_procesal', 'informe_pericial', 'cadena_custodia'
    content: str
    tags: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())

class EvaluationIndicator(BaseModel):
    id: str
    name: str
    category: str  # 'rigor_tecnico', 'claridad_comunicativa', 'resiliencia_objeciones', 'cadena_custodia'
    description: str
    weight: float = 1.0  # Ponderación en el cálculo final
    expected_keywords: List[str] = Field(default_factory=list)
    penalized_keywords: List[str] = Field(default_factory=list)

class CaseDefinition(BaseModel):
    case_id: str
    title: str
    description: str
    scenario_type: ScenarioType
    difficulty: str = "intermedio"  # basico, intermedio, avanzado
    characters: List[CharacterConfig]
    knowledge_base: List[KnowledgeDocument] = Field(default_factory=list)
    evaluation_criteria: List[EvaluationIndicator] = Field(default_factory=list)
    max_turns: int = 15
    case_context: Dict[str, Any] = Field(default_factory=dict)

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    speaker_id: str
    speaker_name: str
    speaker_role: str
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    target_character: Optional[str] = None

class TurnFeedback(BaseModel):
    turn_index: int
    score: float
    strengths: List[str]
    areas_to_improve: List[str]
    comments: str

class EvaluationReport(BaseModel):
    session_id: str
    case_id: str
    student_id: str
    created_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    global_score: float  # 0 a 100
    category_scores: Dict[str, float]
    indicator_scores: Dict[str, float]
    qualitative_feedback: str
    identified_strengths: List[str]
    actionable_recommendations: List[str]
    turn_by_turn_analysis: List[TurnFeedback] = Field(default_factory=list)
