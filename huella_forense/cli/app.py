"""
Interfaz Interactiva de Consola (CLI) con estilo enriquecido (Rich).
Permite ejecutar simulaciones interactivas directamente desde la terminal,
probar audiencias judiciales, reuniones con clientes y ver la evaluación en tiempo real.
"""

from __future__ import annotations
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from huella_forense.core.case_manager import CaseManager
from huella_forense.scenarios.session_runner import SimulationSession
from huella_forense.evaluation.engine import EvaluationEngine
from huella_forense.estimation.effort_estimator import generate_full_estimation

console = Console()

def run_cli():
    console.print(Panel.fit(
        "[bold cyan]⚖️ PLATAFORMA DE ENTRENAMIENTO FORENSE - ESCENARIOS VIRTUALES[/bold cyan]\n"
        "[dim]Diseñado para Huella Forense | Simulación de Audiencia y Reuniones con Cliente[/dim]",
        border_style="cyan"
    ))

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cases")
    case_mgr = CaseManager(cases_dir=data_dir)

    while True:
        console.print("\n[bold yellow]Menú Principal:[/bold yellow]")
        console.print("1. Iniciar Simulación de Audiencia Judicial (Escenario 1)")
        console.print("2. Iniciar Simulación de Reunión con Cliente (Escenario 2)")
        console.print("3. Ver Estimación Técnica de Horas I+D/IA (14 bloques)")
        console.print("4. Listar Casos Disponibles en la Base de Conocimiento")
        console.print("5. Salir")

        opt = Prompt.ask("Seleccione una opción", choices=["1", "2", "3", "4", "5"], default="1")

        if opt == "1":
            start_simulation(case_mgr, "caso_01_audiencia_clonado_evidencia")
        elif opt == "2":
            start_simulation(case_mgr, "caso_02_reunion_cliente_ransomware")
        elif opt == "3":
            show_estimation_table()
        elif opt == "4":
            list_cases_table(case_mgr)
        elif opt == "5":
            console.print("[green]Sesión finalizada. ¡Hasta pronto![/green]")
            break

def start_simulation(case_mgr: CaseManager, case_id: str):
    case = case_mgr.load_case(case_id)
    if not case:
        console.print(f"[red]Error: No se encontró el caso {case_id}[/red]")
        return

    student_name = Prompt.ask("\nIntroduzca su nombre de Perito Forense", default="D. Juan Pérez (Perito)")
    session = SimulationSession(
        session_id="cli_session",
        case=case,
        student_id="student_01",
        student_name=student_name
    )

    console.print(Panel(
        f"[bold]Caso:[/bold] {case.title}\n"
        f"[bold]Tipo:[/bold] {case.scenario_type.value.upper()} | [bold]Dificultad:[/bold] {case.difficulty}\n"
        f"[bold]Sinopsis:[/bold] {case.description}\n"
        f"[bold]Personajes en sala:[/bold] {', '.join([c.name + ' (' + c.role.value + ')' for c in case.characters])}",
        title="[bold green]INICIANDO SESIÓN DE ENTRENAMIENTO[/bold green]",
        border_style="green"
    ))

    # Apertura
    opening = session.start_session()
    for m in opening:
        console.print(f"\n[bold magenta]{m.speaker_name} ({m.speaker_role.upper()}):[/bold magenta] {m.content}")

    # Bucle de interacción
    while not session.is_completed:
        console.print(f"\n[bold blue]--- Turno {session.current_turn + 1}/{case.max_turns} ---[/bold blue]")
        user_input = Prompt.ask("[bold green]Su declaración pericial (o 'salir' para evaluar ya)[/bold green]")
        
        if user_input.strip().lower() in ["salir", "exit", "quit", "terminar"]:
            session.finish_session()
            break

        if not user_input.strip():
            continue

        student_msg, bot_responses = session.submit_student_turn(user_input)
        for b in bot_responses:
            color = "cyan" if "juez" in b.speaker_role else "yellow" if "fiscal" in b.speaker_role else "magenta"
            console.print(f"\n[bold {color}]{b.speaker_name} ({b.speaker_role.upper()}):[/bold {color}] {b.content}")

    # Evaluación Final
    console.print("\n[bold yellow]Generando feedback y evaluación del estudiante...[/bold yellow]")
    evaluator = EvaluationEngine(case)
    report = evaluator.evaluate_session(session.session_id, session.student_id, session.history)

    # Mostrar informe
    score_color = "green" if report.global_score >= 75 else "yellow" if report.global_score >= 50 else "red"
    console.print(Panel(
        f"[bold]Calificación Global:[/bold] [{score_color}]{report.global_score} / 100[/{score_color}]\n\n"
        f"[bold]Feedback Cualitativo:[/bold]\n{report.qualitative_feedback}\n\n"
        f"[bold]Fortalezas Identificadas:[/bold]\n" + "\n".join([f"  ✅ {s}" for s in report.identified_strengths]) + "\n\n"
        f"[bold]Recomendaciones de Mejora:[/bold]\n" + "\n".join([f"  ⚠️ {r}" for r in report.actionable_recommendations]),
        title="[bold]REPORTE FINAL DE VALORACIÓN - HUELLA FORENSE[/bold]",
        border_style=score_color
    ))

def show_estimation_table():
    report = generate_full_estimation()
    table = Table(title="ESTIMACIÓN TÉCNICA DE HORAS I+D/IA (14 BLOQUES SOLICITADOS)")
    table.add_column("#", justify="center", style="cyan")
    table.add_column("Bloque de Trabajo", style="white")
    table.add_column("Horas Min", justify="right", style="green")
    table.add_column("Horas Max", justify="right", style="red")
    table.add_column("Entregable Clave", style="dim")

    for p in report.work_packages:
        table.add_row(str(p.id), p.name, str(p.hours_min), str(p.hours_max), p.deliverables[:50] + "...")

    table.add_row(
        "[bold]TOTAL[/bold]",
        "[bold]Horas Estimadas de Desarrollo I+D/IA[/bold]",
        f"[bold green]{report.total_hours_min}[/bold green]",
        f"[bold red]{report.total_hours_max}[/bold red]",
        f"[bold]Cronograma estimado: {report.mvp_timeline_weeks} semanas[/bold]"
    )
    console.print(table)

def list_cases_table(case_mgr: CaseManager):
    cases = case_mgr.list_cases()
    table = Table(title="CASOS DISPONIBLES EN LA PLATAFORMA")
    table.add_column("ID", style="cyan")
    table.add_column("Título", style="white")
    table.add_column("Escenario", style="yellow")
    table.add_column("Dificultad", style="magenta")
    table.add_column("Personajes", justify="center")
    table.add_column("Docs Base", justify="center")

    for c in cases:
        table.add_row(c["case_id"], c["title"], c["scenario_type"], c["difficulty"], str(c["characters_count"]), str(c["docs_count"]))
    console.print(table)

if __name__ == "__main__":
    run_cli()
