"""
Módulo de Estimación Técnica y Análisis de Esfuerzo de I+D/IA.
Desglosa las horas de trabajo por cada uno de los 14 bloques solicitados en el documento de requisitos,
identifica dependencias críticas, riesgos técnicos y define los hitos de entrega para Huella Forense.
"""

from __future__ import annotations
from typing import List, Dict
from pydantic import BaseModel

class WorkPackage(BaseModel):
    id: int
    name: str
    hours_min: int
    hours_max: int
    deliverables: str
    dependencies: List[str]
    risks: str

class ProjectEstimationReport(BaseModel):
    project_name: str
    total_hours_min: int
    total_hours_max: int
    work_packages: List[WorkPackage]
    critical_dependencies: List[str]
    technical_risks: List[str]
    mvp_timeline_weeks: int

def generate_full_estimation() -> ProjectEstimationReport:
    packages = [
        WorkPackage(
            id=1,
            name="Análisis funcional y técnico de los requisitos",
            hours_min=20,
            hours_max=30,
            deliverables="Documento de especificación formal de casos de uso y diagramas de estados conversacionales.",
            dependencies=["Recepción de requisitos iniciales de Huella Forense"],
            risks="Ambigüedad en los criterios de éxito pedagógico."
        ),
        WorkPackage(
            id=2,
            name="Diseño de la arquitectura necesaria para los escenarios virtuales",
            hours_min=30,
            hours_max=45,
            deliverables="Arquitectura desacoplada (Backend FastAPI + RAG SQLite WAL + Web/WebSocket/REST + Evaluador).",
            dependencies=["Especificación funcional"],
            risks="Sobrecarga de latencia en la generación conversacional."
        ),
        WorkPackage(
            id=3,
            name="Desarrollo/configuración de los escenarios (Audiencia y Reunión)",
            hours_min=40,
            hours_max=60,
            deliverables="Motores de estado para el Escenario 1 (Audiencia judicial) y Escenario 2 (Reunión con cliente).",
            dependencies=["Diseño de arquitectura"],
            risks="Flujos conversacionales poco naturales o bloqueos en la moderación del tribunal."
        ),
        WorkPackage(
            id=4,
            name="Implementación de los personajes y sus respectivos roles",
            hours_min=35,
            hours_max=50,
            deliverables="Agentes del Juez, Fiscal, Abogados y Cliente con prompts de rol y avatar pasivo (monigote gris).",
            dependencies=["Guiones de personajes de Huella Forense"],
            risks="Alucinaciones del modelo que desvíen la personalidad procesal."
        ),
        WorkPackage(
            id=5,
            name="Definición e implementación de la lógica de interacción",
            hours_min=30,
            hours_max=45,
            deliverables="Orquestador de turnos de réplica, objeciones judiciales y límite temporal de intervención.",
            dependencies=["Configuración de escenarios"],
            risks="Monopolio de intervenciones de un solo personaje."
        ),
        WorkPackage(
            id=6,
            name="Integración y configuración de la IA (Modelos LLM & Prompts)",
            hours_min=45,
            hours_max=70,
            deliverables="Conectores LLM con fallback determinista, control de temperatura y streaming de tokens.",
            dependencies=["Claves API / Modelos acordados"],
            risks="Costes imprevistos de API o latencia de inferencia."
        ),
        WorkPackage(
            id=7,
            name="Mecanismo para incorporar y gestionar el conocimiento forense",
            hours_min=35,
            hours_max=55,
            deliverables="Motor RAG híbrido (SQLite WAL + BM25/Vectorial) con segmentación por tags y confidencialidad.",
            dependencies=["Casos y documentación pericial de Huella Forense"],
            risks="Recuperación de contexto irrelevante que confunda al personaje."
        ),
        WorkPackage(
            id=8,
            name="Diseño de la estructura para crear y gestionar diferentes casos",
            hours_min=25,
            hours_max=40,
            deliverables="CaseManager modular basado en JSON/YAML con validación estricta Pydantic y carga en caliente.",
            dependencies=["Definición de modelos de datos"],
            risks="Dificultad de los formadores para crear casos sin asistencia técnica."
        ),
        WorkPackage(
            id=9,
            name="Implementación del sistema de valoración y feedback",
            hours_min=40,
            hours_max=60,
            deliverables="Motor de rúbricas analíticas, cálculo de métricas ponderadas y reporte cuantitativo/cualitativo.",
            dependencies=["Criterios e indicadores oficiales de Huella Forense"],
            risks="Subjetividad en la corrección automática del lenguaje natural."
        ),
        WorkPackage(
            id=10,
            name="Gestión y almacenamiento de contenidos y recursos",
            hours_min=20,
            hours_max=35,
            deliverables="Base de datos persistente para evidencias, actas de custodia, peritajes y audios.",
            dependencies=["Estructura de casos"],
            risks="Pérdida de integridad en archivos adjuntos de gran tamaño."
        ),
        WorkPackage(
            id=11,
            name="Pruebas funcionales y validación de las interacciones",
            hours_min=30,
            hours_max=45,
            deliverables="Suite automatizada de tests unitarios y de integración (pytest) + sesiones de simulación completas.",
            dependencies=["Implementación del MVP"],
            risks="Detección tardía de inconsistencias jurídicas."
        ),
        WorkPackage(
            id=12,
            name="Revisión y ajustes tras las pruebas con Huella Forense",
            hours_min=25,
            hours_max=40,
            deliverables="Refactorización y ajuste fino de prompts y rúbricas tras sesiones de feedback con expertos.",
            dependencies=["Pruebas conjuntas con Huella Forense"],
            risks="Desviaciones sustanciales respecto a la expectativa inicial del cliente."
        ),
        WorkPackage(
            id=13,
            name="Documentación técnica y funcional",
            hours_min=20,
            hours_max=30,
            deliverables="Manual de arquitectura, guía de creación de casos para docentes, manual de usuario y OpenAPI.",
            dependencies=["Estabilización del código"],
            risks="Desactualización de manuales por cambios rápidos."
        ),
        WorkPackage(
            id=14,
            name="Puesta en producción de la primera versión (MVP)",
            hours_min=25,
            hours_max=40,
            deliverables="Despliegue containerizado (Docker), configuración de variables de entorno y monitorización básica.",
            dependencies=["Aprobación de la versión candidata"],
            risks="Problemas de infraestructura de alojamiento o cuotas de red."
        )
    ]

    total_min = sum(p.hours_min for p in packages)
    total_max = sum(p.hours_max for p in packages)

    dependencies = [
        "1. Entrega formal por parte de Huella Forense de los guiones piloto de audiencia y reunión.",
        "2. Definición exacta de los baremos e indicadores de evaluación (qué penaliza y qué suma nota).",
        "3. Decisión sobre el proveedor de infraestructura de IA (OpenAI, Anthropic o servidor local on-premise con vLLM).",
        "4. Confirmación del formato de entrega del feedback (PDF descargable, pantalla web interactiva, o ambos)."
    ]

    risks = [
        "Riesgo 1 (Alucinación Jurídica/Forense): Que la IA admita como válidas prácticas periciales erróneas. Mitigación: Grounding estricto vía RAG sobre normas UNE/ISO.",
        "Riesgo 2 (Latencia de Interacción): Delays superiores a 3 segundos en la respuesta del tribunal. Mitigación: Streaming SSE y modelos de inferencia rápida.",
        "Riesgo 3 (Escalabilidad de Creación de Casos): Dependencia del equipo de desarrollo para cada caso nuevo. Mitigación: CaseManager desacoplado con esquemas JSON/Pydantic listos para un panel de administración."
    ]

    return ProjectEstimationReport(
        project_name="Plataforma de Simulación Virtual Huella Forense",
        total_hours_min=total_min,
        total_hours_max=total_max,
        work_packages=packages,
        critical_dependencies=dependencies,
        technical_risks=risks,
        mvp_timeline_weeks=10
    )
