"""
Script de Demostración Completa Automatizada de la Plataforma Huella Forense.
Ejecuta de extremo a extremo:
1. Simulación de una Audiencia Judicial completa con interacción pericial.
2. Simulación de una Reunión con Cliente.
3. Evaluación multidimensional y rúbrica pedagógica.
4. Generación y renderizado de la estimación de 14 bloques para I+D/IA.
"""

import sys
import os

# Asegurar path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from huella_forense.core.case_manager import CaseManager
from huella_forense.scenarios.session_runner import SimulationSession
from huella_forense.evaluation.engine import EvaluationEngine
from huella_forense.estimation.effort_estimator import generate_full_estimation
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def run_demo():
    console.print(Panel.fit(
        "[bold cyan]🔍 DEMOSTRACIÓN END-TO-END - HUELLA FORENSE[/bold cyan]\n"
        "[dim]Simulación de Escenarios Virtuales con IA y Sistema de Valoración[/dim]",
        border_style="cyan"
    ))

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "huella_forense", "data", "cases")
    mgr = CaseManager(cases_dir=data_dir)

    # 1. Simulación de Audiencia Judicial
    console.print("\n[bold green]═══ 1. SIMULACIÓN: ESCENARIO 1 (AUDIENCIA JUDICIAL) ═══[/bold green]")
    case_aud = mgr.load_case("caso_01_audiencia_clonado_evidencia")
    session_aud = SimulationSession(
        session_id="demo_audiencia_01",
        case=case_aud,
        student_id="estudiante_forense_01",
        student_name="Dña. Laura Gómez (Perito Forense Colegiada)"
    )

    opening = session_aud.start_session()
    for m in opening:
        console.print(f"[bold magenta]{m.speaker_name} ({m.speaker_role.upper()}):[/bold magenta] {m.content}")

    # Intervención 1 del estudiante
    turn1_text = (
        "Con la venia de Su Señoría. Como perito informático forense asignado, certifico que la adquisición del "
        "disco SSD incautado se efectuó mediante duplicadora Tableau Forensic con bloqueador de escritura por hardware. "
        "Se calculó inmediatamente el hash SHA-256 en origen y destino, coincidiendo bit a bit según consta en el acta notarial."
    )
    console.print(f"\n[bold green]👤 ESTUDIANTE (Perito):[/bold green] {turn1_text}")
    _, resp1 = session_aud.submit_student_turn(turn1_text)
    for r in resp1:
        console.print(f"[bold yellow]{r.speaker_name} ({r.speaker_role.upper()}):[/bold yellow] {r.content}")

    # Intervención 2 del estudiante
    turn2_text = (
        "Señoría y señor letrado: las marcas de tiempo fueron correlacionadas mediante la escala UTC estándar. "
        "Descartamos contaminación por malware gracias a la verificación de firmas digitales y la cadena de custodia ininterrumpida."
    )
    console.print(f"\n[bold green]👤 ESTUDIANTE (Perito):[/bold green] {turn2_text}")
    _, resp2 = session_aud.submit_student_turn(turn2_text)
    for r in resp2:
        console.print(f"[bold cyan]{r.speaker_name} ({r.speaker_role.upper()}):[/bold cyan] {r.content}")

    # Evaluación de la sesión
    console.print("\n[bold yellow]═══ 2. EVALUACIÓN Y FEEDBACK AUTOMATIZADO DEL ESTUDIANTE ═══[/bold yellow]")
    evaluator = EvaluationEngine(case_aud)
    report = evaluator.evaluate_session(session_aud.session_id, session_aud.student_id, session_aud.history)

    console.print(f"🎯 [bold]Puntuación Global:[/bold] [bold green]{report.global_score}/100[/bold green]")
    console.print(f"📋 [bold]Feedback Cualitativo:[/bold] {report.qualitative_feedback}")
    console.print("[bold]Fortalezas destacadas:[/bold]")
    for st in report.identified_strengths:
        console.print(f"  • {st}")
    console.print("[bold]Recomendaciones docentes:[/bold]")
    for rec in report.actionable_recommendations:
        console.print(f"  • {rec}")

    # 3. Estimación técnica
    console.print("\n[bold blue]═══ 3. ESTIMACIÓN DE ESFUERZO TÉCNICO I+D/IA (14 BLOQUES) ═══[/bold blue]")
    est = generate_full_estimation()
    table = Table(title="Desglose de Horas por Tarea Solicitada")
    table.add_column("Bloque", style="cyan", justify="center")
    table.add_column("Nombre de la Tarea", style="white")
    table.add_column("Rango Horas", style="green", justify="right")
    table.add_column("Dependencias", style="dim")

    for p in est.work_packages:
        table.add_row(f"B{p.id}", p.name, f"{p.hours_min} - {p.hours_max}h", p.dependencies[0][:40])

    table.add_row("[bold]TOTAL[/bold]", "[bold]Esfuerzo Completo I+D/IA[/bold]", f"[bold]{est.total_hours_min} - {est.total_hours_max}h[/bold]", f"[bold]{est.mvp_timeline_weeks} semanas MVP[/bold]")
    console.print(table)

if __name__ == "__main__":
    run_demo()
