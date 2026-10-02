"""
API REST y Servidor Web FastAPI para la Plataforma de Simulación Virtual Huella Forense.
Expone endpoints para listar casos, iniciar sesiones de audiencia/reunión, interactuar en turnos,
obtener la evaluación final y consultar la estimación técnica de I+D/IA.
"""

from __future__ import annotations
import os
import uuid
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from huella_forense.core.case_manager import CaseManager
from huella_forense.models.schemas import CaseDefinition, Message, EvaluationReport
from huella_forense.scenarios.session_runner import SimulationSession
from huella_forense.evaluation.engine import EvaluationEngine
from huella_forense.estimation.effort_estimator import generate_full_estimation, ProjectEstimationReport

app = FastAPI(
    title="Huella Forense - Plataforma de Entrenamiento y Simulación Virtual",
    description="API para la gestión y ejecución de audiencias judiciales y reuniones periciales interactivas impulsadas por IA.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar gestores
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cases")
case_manager = CaseManager(cases_dir=DATA_DIR)
active_sessions: Dict[str, SimulationSession] = {}

class StartSessionRequest(BaseModel):
    case_id: str
    student_id: str
    student_name: str = "Perito Forense"

from fastapi.responses import FileResponse

class SubmitTurnRequest(BaseModel):
    student_input: str

@app.get("/", tags=["General"])
def root():
    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "platform": "Huella Forense - Virtual Training Arena",
        "status": "operational",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/cases", tags=["Casos de Simulación"])
def get_cases():
    """Lista todos los casos disponibles para entrenamiento."""
    return case_manager.list_cases()

@app.get("/cases/{case_id}", tags=["Casos de Simulación"])
def get_case_details(case_id: str):
    """Devuelve los detalles completos de un caso concreto."""
    case = case_manager.load_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return case

@app.post("/cases", tags=["Casos de Simulación"])
def create_or_update_case(case: CaseDefinition):
    """Permite a Huella Forense incorporar nuevos casos sin tocar código."""
    case_manager.save_case(case)
    return {"message": "Caso guardado exitosamente", "case_id": case.case_id}

@app.post("/sessions/start", tags=["Simulación Interactiva"])
def start_session(req: StartSessionRequest):
    """Inicia una nueva sesión de simulación con un estudiante."""
    case = case_manager.load_case(req.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="El caso especificado no existe")

    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    session = SimulationSession(
        session_id=session_id,
        case=case,
        student_id=req.student_id,
        student_name=req.student_name
    )
    active_sessions[session_id] = session
    opening_messages = session.start_session()

    return {
        "session_id": session_id,
        "case_id": req.case_id,
        "case_title": case.title,
        "scenario_type": case.scenario_type.value,
        "opening_messages": opening_messages
    }

@app.post("/sessions/{session_id}/turn", tags=["Simulación Interactiva"])
def submit_turn(session_id: str, req: SubmitTurnRequest):
    """Envía la intervención del estudiante y recibe la respuesta del tribunal/interlocutor."""
    session = active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión activa no encontrada")

    if session.is_completed:
        raise HTTPException(status_code=400, detail="La sesión ya ha finalizado. Solicite la evaluación.")

    student_msg, bot_responses = session.submit_student_turn(req.student_input)
    return {
        "session_id": session_id,
        "current_turn": session.current_turn,
        "max_turns": session.case.max_turns,
        "is_completed": session.is_completed,
        "student_message": student_msg,
        "character_responses": bot_responses
    }

@app.get("/sessions/{session_id}/evaluate", tags=["Sistema de Valoración"])
def evaluate_session(session_id: str) -> EvaluationReport:
    """Calcula y devuelve la valoración detallada del desempeño del estudiante con feedback multidimensional."""
    session = active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión activa no encontrada")

    evaluator = EvaluationEngine(session.case)
    report = evaluator.evaluate_session(
        session_id=session.session_id,
        student_id=session.student_id,
        history=session.history
    )
    return report

@app.get("/estimation", tags=["Estimación de I+D/IA"])
def get_technical_estimation() -> ProjectEstimationReport:
    """Devuelve el desglose detallado de horas de I+D/IA solicitadas para el proyecto Huella Forense."""
    return generate_full_estimation()
