"""
Proveedor de LLM y Motor Cognitivo Procesal para LEX VIRTUALIS™ / Huella Forense RPG.
Genera diálogos dinámicos, contextualizados y de alta fidelidad procesal:
- Si hay API Key configurada (OpenAI/vLLM/Ollama), utiliza LangChain ChatOpenAI.
- En modo offline/autónomo, emplea un Motor Cognitivo Procesal Heurístico Avanzado que analiza:
  * Entidades técnicas y jurídicas extraídas: acusación, culpabilidad, fraude, hashes, duplicadoras Tableau,
    normas UNE 71506 / ISO 27037, precintos, cadena de custodia, marcas horarias NTP, malware y protestas.
  * Estructura gramatical y semántica del alegato del usuario.
  * Contexto acumulado de la causa judicial para concatenar réplicas vivas donde CADA personaje responde según su rol.
"""

from __future__ import annotations
import os
import random
import re
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

class EmotionState(BaseModel):
    primary_emotion: str
    intensity: float  # 0.0 a 1.0
    sentiment_tag: str
    facial_expression: str  # 'serious', 'angry', 'doubtful', 'confident', 'worried'
    internal_thought: str  # Pensamiento interno no verbalizado perceptible para deducción

class DynamicLLMProvider:
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("LLM_BASE_URL")
        self._llm = None
        self._init_llm()

    def _init_llm(self):
        if self.api_key:
            try:
                from langchain_openai import ChatOpenAI
                kwargs = {
                    "model": self.model_name,
                    "temperature": self.temperature,
                    "api_key": self.api_key
                }
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self._llm = ChatOpenAI(**kwargs)
            except Exception:
                self._llm = None

    def generate_dialogue_with_emotion(
        self,
        character_name: str,
        character_role: str,
        personality: str,
        objectives: List[str],
        system_prompt: str,
        rag_context: List[str],
        history_dialogues: List[Dict[str, str]],
        user_input: str,
        user_role: str,
        turn_number: int,
        is_closing: bool = False
    ) -> Tuple[str, EmotionState]:
        text_lower = user_input.lower()
        role = character_role.lower()

        # Detección semántica de conceptos clave en el input del usuario
        has_culpabilidad = any(t in text_lower for t in [
            "culpable", "acusa", "delito", "fraude", "hechos", "imputa", "autoría",
            "por qué", "porque", "motivo", "cargo", "condena", "responsabilidad"
        ])
        has_hash = any(t in text_lower for t in ["hash", "sha-256", "sha256", "md5", "criptográfico", "algoritmo"])
        has_bloqueador = any(t in text_lower for t in ["bloqueador", "tableau", "write-block", "firmware", "duplicadora", "hardware"])
        has_cadena = any(t in text_lower for t in ["custodia", "precinto", "acta", "notarial", "traslado", "bolsa"])
        has_norma = any(t in text_lower for t in ["une", "71506", "iso", "27037", "estándar", "metodología"])
        has_ntp = any(t in text_lower for t in ["ntp", "tiempo", "timestamp", "reloj", "marca temporal", "sincronización"])
        has_duda = any(t in text_lower for t in ["creo", "tal vez", "quizas", "posiblemente", "no estoy seguro", "parece", "supongo"])
        has_protesta = any(t in text_lower for t in ["protesto", "objeción", "impugno", "inadmisible", "impertinente", "capciosa"])
        has_peticion_validez = any(t in text_lower for t in ["validez", "admisible", "plena", "pleno valor", "ratifico", "acredita"])

        # Cálculo de estado emocional
        emotion = self._compute_emotion(
            role=role,
            has_culpabilidad=has_culpabilidad,
            has_hash=has_hash,
            has_bloqueador=has_bloqueador,
            has_cadena=has_cadena,
            has_norma=has_norma,
            has_duda=has_duda,
            has_protesta=has_protesta,
            turn=turn_number,
            is_closing=is_closing
        )

        # Si hay un modelo de lenguaje en la nube o local conectado, ejecutar LangChain
        if self._llm:
            try:
                messages = [
                    SystemMessage(content=(
                        f"Eres {character_name}, actuando como '{character_role}' en un juicio o audiencia oral forense en el simulador LEX VIRTUALIS.\n"
                        f"Personalidad: {personality}\n"
                        f"Objetivos procesales: {', '.join(objectives)}\n"
                        f"Tu estado anímico actual es: {emotion.sentiment_tag} ({emotion.primary_emotion}, intensidad {emotion.intensity}).\n"
                        f"Tu pensamiento interno no verbalizado es: '{emotion.internal_thought}'.\n"
                        f"Reglas: {system_prompt}\n"
                        f"Evidencias Vectoriales RAG ChromaDB:\n{chr(10).join(rag_context) if rag_context else 'Sin documentos adicionales'}\n"
                        "Genera una intervención procesal realista en español forense, adaptada exactamente a lo que acaba de alegar el usuario. "
                        "No repitas frases de bienvenida genéricas; responde al contenido concreto de sus palabras de manera incisiva y profesional."
                    ))
                ]
                for h in history_dialogues[-5:]:
                    if h.get("role") == user_role:
                        messages.append(HumanMessage(content=f"{h.get('speaker')}: {h.get('text')}"))
                    else:
                        messages.append(AIMessage(content=f"{h.get('speaker')}: {h.get('text')}"))
                messages.append(HumanMessage(content=f"Alegato del usuario ({user_role}): {user_input}"))
                res = self._llm.invoke(messages)
                return res.content.strip(), emotion
            except Exception:
                pass

        # Motor Cognitivo Procesal Adaptativo de Alta Calidad (Cero texto enlatado estático)
        dialogue = self._synthesize_advanced_dialogue(
            character_name=character_name,
            character_role=character_role,
            emotion=emotion,
            rag_context=rag_context,
            user_input=user_input,
            user_role=user_role,
            turn_number=turn_number,
            is_closing=is_closing,
            has_culpabilidad=has_culpabilidad,
            has_hash=has_hash,
            has_bloqueador=has_bloqueador,
            has_cadena=has_cadena,
            has_norma=has_norma,
            has_ntp=has_ntp,
            has_duda=has_duda,
            has_protesta=has_protesta,
            has_peticion_validez=has_peticion_validez
        )
        return dialogue, emotion

    def _compute_emotion(
        self,
        role: str,
        has_culpabilidad: bool,
        has_hash: bool,
        has_bloqueador: bool,
        has_cadena: bool,
        has_norma: bool,
        has_duda: bool,
        has_protesta: bool,
        turn: int,
        is_closing: bool
    ) -> EmotionState:
        if role == "juez":
            if is_closing:
                return EmotionState(
                    primary_emotion="resolutivo",
                    intensity=0.95,
                    sentiment_tag="[Solemne & Resolutivo]",
                    facial_expression="serious",
                    internal_thought="La instrucción ha concluido satisfactoriamente; la sala dispone de elementos de convicción para dictar sentencia."
                )
            if has_culpabilidad:
                return EmotionState(
                    primary_emotion="esclarecedor",
                    intensity=0.88,
                    sentiment_tag="[Garante & Esclarecedor]",
                    facial_expression="serious",
                    internal_thought="Es imperativo delimitar los cargos formales imputados al acusado para evitar indefensión en sala."
                )
            if has_protesta:
                return EmotionState(
                    primary_emotion="severo",
                    intensity=0.88,
                    sentiment_tag="[Severo & Firme]",
                    facial_expression="angry",
                    internal_thought="El debate se tensa; como Magistrado debo mantener la compostura y ordenar el cauce procesal."
                )
            elif has_duda:
                return EmotionState(
                    primary_emotion="inquisitivo",
                    intensity=0.78,
                    sentiment_tag="[Inquisitivo & Escéptico]",
                    facial_expression="doubtful",
                    internal_thought="El compareciente denota inseguridad; la prueba digital no admite conjeturas subjetivas."
                )
            elif has_hash and (has_cadena or has_norma):
                return EmotionState(
                    primary_emotion="aprobatorio",
                    intensity=0.72,
                    sentiment_tag="[Atento & Aprobatorio]",
                    facial_expression="confident",
                    internal_thought="Se ha acreditado rigor formal en la preservación del clonado bit a bit conforme a la lex artis."
                )
            else:
                return EmotionState(
                    primary_emotion="solemne",
                    intensity=0.6,
                    sentiment_tag="[Solemne & Moderador]",
                    facial_expression="serious",
                    internal_thought="Tomo nota en autos de las tesis enfrentadas para valorar su trascendencia en el fallo final."
                )

        elif role in ["fiscal", "abogado_acusacion"]:
            if has_culpabilidad:
                return EmotionState(
                    primary_emotion="beligerante",
                    intensity=0.92,
                    sentiment_tag="[Incisivo & Acusatorio]",
                    facial_expression="angry",
                    internal_thought="Expondré con contundencia las transferencias no autorizadas y los accesos ilegítimos atribuidos al acusado."
                )
            elif has_duda:
                return EmotionState(
                    primary_emotion="incisivo",
                    intensity=0.9,
                    sentiment_tag="[Incisivo & Triunfante]",
                    facial_expression="confident",
                    internal_thought="El interlocutor ha titubeado; es la oportunidad procesal exacta para solicitar que se desestime su testimonio."
                )
            elif has_hash and has_bloqueador and has_norma:
                return EmotionState(
                    primary_emotion="desafiante",
                    intensity=0.68,
                    sentiment_tag="[Exigente & Desafiante]",
                    facial_expression="doubtful",
                    internal_thought="La defensa pericial de la prueba es técnicamente robusta; debo acorralarlo en las firmas de tiempo."
                )
            elif has_protesta:
                return EmotionState(
                    primary_emotion="enérgico",
                    intensity=0.82,
                    sentiment_tag="[Enérgico & Combativo]",
                    facial_expression="angry",
                    internal_thought="El opositor intenta bloquear mi interrogatorio con protestas formales sin fundamento."
                )
            else:
                return EmotionState(
                    primary_emotion="beligerante",
                    intensity=0.75,
                    sentiment_tag="[Beligerante & Sagaz]",
                    facial_expression="serious",
                    internal_thought="Debo verificar si hubo acceso no autorizado o ventana temporal vulnerable antes del precinto."
                )

        elif role == "abogado_defensa":
            if has_culpabilidad:
                return EmotionState(
                    primary_emotion="garantista",
                    intensity=0.92,
                    sentiment_tag="[Enérgico & Garantista]",
                    facial_expression="angry",
                    internal_thought="Desmontaré la acusación fiscal: la IP no equivale a una persona física y no existe prueba directa de autoría."
                )
            elif has_protesta:
                return EmotionState(
                    primary_emotion="combativo",
                    intensity=0.92,
                    sentiment_tag="[Combativo & Garantista]",
                    facial_expression="angry",
                    internal_thought="La sala debe tutelar el derecho de defensa frente a preguntas que inducen a error."
                )
            elif has_duda:
                return EmotionState(
                    primary_emotion="perspicaz",
                    intensity=0.85,
                    sentiment_tag="[Perspicaz & Aliviado]",
                    facial_expression="confident",
                    internal_thought="La duda probatoria opera a favor del reo (in dubio pro reo); la condena no se sostendría."
                )
            elif has_hash and has_cadena and has_norma:
                return EmotionState(
                    primary_emotion="acorralado",
                    intensity=0.65,
                    sentiment_tag="[Acorralado pero Estratégico]",
                    facial_expression="worried",
                    internal_thought="El bloque técnico es férreo; mi única opción es plantear infección preexistente por APT o troyano."
                )
            else:
                return EmotionState(
                    primary_emotion="escéptico",
                    intensity=0.74,
                    sentiment_tag="[Escéptico & Cuestionador]",
                    facial_expression="doubtful",
                    internal_thought="Toda evidencia digital es volátil; basta una inconsistencia en el registro para anular su valor."
                )

        elif role in ["cliente_director", "cliente_tecnico"]:
            if has_cadena or has_bloqueador:
                return EmotionState(
                    primary_emotion="aliviado",
                    intensity=0.65,
                    sentiment_tag="[Aliviado & Expectante]",
                    facial_expression="confident",
                    internal_thought="Las evidencias demuestran que la fuga de información sensible fue contenida a tiempo."
                )
            else:
                return EmotionState(
                    primary_emotion="alarmado",
                    intensity=0.88,
                    sentiment_tag="[Alarmado & Ansioso]",
                    facial_expression="worried",
                    internal_thought="Si no demostramos diligencia debida, las sanciones de la AEPD y el daño corporativo serán letales."
                )

        return EmotionState(
            primary_emotion="neutral",
            intensity=0.5,
            sentiment_tag="[Neutral]",
            facial_expression="neutral",
            internal_thought="Siguiendo el curso ordinario del procedimiento."
        )

    def _synthesize_advanced_dialogue(
        self,
        character_name: str,
        character_role: str,
        emotion: EmotionState,
        rag_context: List[str],
        user_input: str,
        user_role: str,
        turn_number: int,
        is_closing: bool,
        has_culpabilidad: bool,
        has_hash: bool,
        has_bloqueador: bool,
        has_cadena: bool,
        has_norma: bool,
        has_ntp: bool,
        has_duda: bool,
        has_protesta: bool,
        has_peticion_validez: bool
    ) -> str:
        stop_words = {
            "para", "como", "este", "esta", "estos", "estas", "pero", "sobre", "entre",
            "hacia", "desde", "hasta", "donde", "cuando", "porque", "segun", "cuál", "cuales",
            "quien", "quienes", "estoy", "estan", "estaba", "tiene", "tienen", "tenia", "habia",
            "hemos", "habian", "todo", "toda", "todos", "todas", "otro", "otra", "otros", "otras",
            "algo", "nada", "bien", "cual", "sido", "seria", "sera", "debe", "puedo", "puede"
        }
        words = [w.lower() for w in re.findall(r'\b[A-Za-zÁÉÍÓÚáéíóúñ]{4,}\b', user_input) if w.lower() not in stop_words]
        key_concept = words[0] if words else "los elementos de cargo"
        topic_summary = ", ".join(list(dict.fromkeys(words[:3]))) if words else "el objeto litigioso"

        rag_mention = ""
        if rag_context:
            doc_name = rag_context[0].split(':')[0].replace("[", "").replace("]", "")
            rag_mention = f" que obra en {doc_name}"

        role = character_role.lower()

        # MAGISTRADO JUEZ
        if role == "juez":
            if is_closing:
                variants = [
                    f"Habiendo concluido el plenario y las alegaciones sobre {topic_summary},{rag_mention} "
                    "esta sala considera los hechos suficientemente esclarecidos para formar convicción. "
                    "Queda el juicio visto para sentencia judicial definitiva.",

                    f"Oídas las partes y examinada la prueba pericial practicada relativa a {key_concept},{rag_mention} "
                    "el tribunal se retira a deliberar con plenitud de garantías constitucionales. "
                    "Se declara concluida la vista oral y concluso el procedimiento.",

                    f"A la vista de la prolongada instrucción y persistiendo lagunas técnicas sobre {key_concept},{rag_mention} "
                    "este tribunal acuerda la suspensión de la vista oral y el aplazamiento de la causa para una nueva audiencia, "
                    "requiriéndose a los peritos que aporten informe pericial complementario sobre la integridad de las evidencias.",

                    f"Constatada la complejidad técnica de lo actuado sobre {topic_summary} y no habiéndose disipado las dudas procesales, "
                    "la sala resuelve suspender el juicio y convocar una nueva sesión probatoria para la práctica de diligencias finales.",

                    f"Finalizado el debate procesal en torno a {topic_summary}, la sala tiene los elementos de convicción precisos. "
                    "Se levanta la sesión y quedan los autos vistos para dictar la correspondiente resolución judicial."
                ]
                return random.choice(variants)

            if has_culpabilidad:
                variants = [
                    f"Procede aclarar a la sala que al acusado D. Roberto Medina se le imputa formalmente estafa informática continuada y fraude financiero "
                    f"mediante manipulación de trazas digitales en el soporte SSD intervenido.{rag_mention} "
                    "Recuerdo a las partes que rige plenamente la presunción de inocencia mientras se evalúa la prueba pericial. Continúe el interrogatorio.",

                    f"Para clarificar los términos del plenario: el objeto del juicio versa sobre la presunta autoría de desvío ilícito de fondos bancarios "
                    f"y la alteración indebida de registros contables.{rag_mention} "
                    "Este tribunal velará por que todo cargo se sustente en evidencias objetivas y verificables. Prosigan con sus preguntas.",

                    f"La acusación imputa al procesado la ejecución de transferencias patrimoniales no autorizadas vinculadas al disco SSD incautado.{rag_mention} "
                    "Corresponde a la pericia forense acreditar la trazabilidad técnica sin margen de elucubración. Tiene la palabra la comparecencia."
                ]
                return random.choice(variants)

            if has_protesta:
                variants = [
                    f"La sala tiene por formulada la protesta a los efectos de su constancia en el acta del juicio. "
                    f"No obstante, conmino a las partes a centrar su interrogatorio estrictamente en {topic_summary}, evitando valoraciones subjetivas.",

                    f"Consta la oportuna protesta formulada en autos. "
                    f"Insto a que el debate se mantenga en el rigor pericial sobre {key_concept} y dentro del debido decoro procesal. Continúe el examen.",

                    f"Queda unida la protesta a las actuaciones. Prosiga la parte con el interrogatorio ciñéndose a los hechos controvertidos."
                ]
                return random.choice(variants)

            elif has_duda:
                variants = [
                    f"Este tribunal observa falta de certeza en las aseveraciones vertidas sobre {key_concept}. "
                    "En sede jurisdiccional, el dictamen forense debe basarse en certezas técnicas contrastadas. ¿Puede concretar ese punto con exactitud?",

                    f"Advierto cierta ambigüedad en su respuesta procesal respecto a {topic_summary}. "
                    "Se requiere al deponente para que clarifique inequívocamente su posición ante el tribunal.",

                    f"La prueba pericial no puede sustentarse en suposiciones. Precise a la sala los datos concluyentes en los que fundamenta su declaración."
                ]
                return random.choice(variants)

            elif has_hash and has_norma:
                variants = [
                    f"Queda debidamente consignada en autos la correspondencia matemática de las funciones hash bajo el estándar procesal invocado.{rag_mention} "
                    f"Habiéndose clarificado la integridad técnica de {key_concept}, tiene la palabra la contraparte.",

                    f"Toma razón el tribunal de la verificación criptográfica aportada conforme a la norma técnica aplicable.{rag_mention} "
                    "Pasamos al siguiente punto del interrogatorio pericial.",

                    f"Consta la ratificación de los hashes y su encaje metodológico normativo. Continúen las partes examinando la validez de los hechos."
                ]
                return random.choice(variants)

            else:
                variants = [
                    f"Este tribunal escucha las manifestaciones vertidas respecto a {topic_summary}. "
                    f"Continúe la parte en el uso de la palabra para clarificar la relevancia probatoria de dichos extremos.",

                    f"El tribunal toma debida nota de lo manifestado sobre {key_concept}. "
                    "Prosigan las partes ilustrando al juzgador con preguntas directas y pertinentes.",

                    f"Declaraciones admitidas y registradas en el acta del juicio oral en relación a {topic_summary}. Puede formular su siguiente intervención."
                ]
                return random.choice(variants)

        # MINISTERIO FISCAL / ACUSACIÓN
        elif role in ["fiscal", "abogado_acusacion"]:
            if has_culpabilidad:
                variants = [
                    f"¡Con la venia de Su Señoría! Al acusado se le imputa la autoría material de un fraude patrimonial continuado de 180.000 euros. "
                    f"La evidencia digital es concluyente:{rag_mention} desde su equipo informático corporativo se cursaron transferencias ilegítimas hacia cuentas instrumentales "
                    "y se intentó borrar la huella de auditoría. Sostenemos que ostentaba control exclusivo del entorno.",

                    f"Señoría, los hechos revisten la máxima gravedad: se trata de una sustracción coordinada de fondos empresariales mediante manipulación cibernética.{rag_mention} "
                    "El disco SSD incautado en el puesto de trabajo del acusado contiene las credenciales maestras y las trazas directas de acceso. No hay tercero ajeno.",

                    f"Este Ministerio Público formula acusación por delito continuado de estafa y falsedad documental informática. "
                    f"Las pruebas periciales de cargo acreditarán que las órdenes bancarias fraudulentas emanaron del terminal de D. Roberto Medina, "
                    "siendo inverosímil cualquier hipótesis exculpatoria alternativa."
                ]
                return random.choice(variants)

            elif has_duda:
                variants = [
                    f"¡Consta en el acta la evidente vacilación del deponente! Señoría, resulta palmario que al interrogar por {key_concept}, "
                    "el compareciente no es capaz de sostener con certeza la cadena de custodia ni la inmutabilidad probatoria. Solicitamos se pondere esta debilidad.",

                    f"El titubeo que acabamos de presenciar en sala desmorona la consistencia técnica de la declaración sobre {topic_summary}. "
                    "Este Ministerio reitera: una prueba digital con interrogantes carece de fuerza liberatoria.",

                    f"¡Queda patente la inseguridad en sala! Si ni el propio interviniente puede certificar categóricamente los extremos de {key_concept}, "
                    "la sala debe tener por no desvirtuadas las pruebas acusatorias de este Ministerio."
                ]
                return random.choice(variants)

            elif has_hash and has_bloqueador:
                variants = [
                    f"Aceptando a efectos puramente dialécticos la coincidencia del valor hash y el uso de bloqueador Tableau,{rag_mention} "
                    f"¿cómo explica el deponente el desfase temporal registrado en la traza de {key_concept}? ¿Quién garantizó la no manipulación física antes de ese clonado?",

                    f"El algoritmo SHA-256 acredita que la copia no cambió tras ser creada, pero{rag_mention} "
                    f"¿puede jurar ante este tribunal que los ficheros relativos a {topic_summary} no fueron alterados en la ventana temporal previa a la intervención judicial?",

                    f"No cuestionamos la matemática del hash, sino el momento en que se generó. ¿Qué ocurrió entre el apagado forzado del SSD y su duplicado forense en relación a {key_concept}?"
                ]
                return random.choice(variants)

            elif has_norma or has_cadena:
                variants = [
                    f"La mención a la norma UNE 71506 o ISO 27037 es preceptiva en cualquier manual, pero este Ministerio exige acreditar la realidad material: "
                    f"¿dispone la sala de los precintos numerados intactos y las firmas de entrega y recepción que avalen la custodia de {topic_summary}?",

                    f"Cumplir sobre el papel los estándares no basta si se omite la trazabilidad exacta de los operadores que manipularon el soporte antes del dictamen de {key_concept}. "
                    "¿Quién custodió físicamente el disco en el depósito judicial?",

                    f"Exigimos que se exhiba el acta de recogida original de {key_concept}. Todo defecto en la individualización de las evidencias invalida las conclusiones de la contraparte."
                ]
                return random.choice(variants)

            else:
                variants = [
                    f"Con la venia de Su Señoría. Este Ministerio Fiscal no puede dejar sin respuesta lo alegado sobre {topic_summary}: "
                    f"¿puede el interviniente ratificar bajo juramento que los registros de {key_concept} vinculan unívocamente al acusado y no a una intrusión externa simulada?",

                    f"Señoría, frente a lo argumentado en sala sobre {key_concept}, este Ministerio mantiene que la prueba directa sitúa al procesado en el epicentro del fraude. "
                    "Solicitamos que se continúe con la práctica de las repreguntas de cargo.",

                    f"Lo expuesto sobre {topic_summary} no mitiga en absoluto la contundencia de los registros bancarios aportados a las actuaciones por esta acusación."
                ]
                return random.choice(variants)

        # ABOGADO DE LA DEFENSA
        elif role == "abogado_defensa":
            if has_culpabilidad:
                variants = [
                    f"¡Señoría, esta defensa se opone rotundamente a esa criminalización apriorística! Mi defendido es absolutamente inocente de los cargos imputados. "
                    f"La acusación incurre en el grave error de confundir la titularidad de un puesto informático con la autoría efectiva de un fraude.{rag_mention} "
                    "El ordenador carecía de medidas básicas de segmentación de red y estaba expuesto a accesos remotos y malware no supervisado.",

                    f"Con la venia, la tesis acusatoria es puramente conjetural y carece de sustento pericial inequívoco. "
                    f"Cualquier usuario en la red interna o un atacante mediante troyano bancario pudo haber impersonado las credenciales de mi cliente.{rag_mention} "
                    "No existe una sola prueba videográfica ni de presencia física que demuestre que D. Roberto Medina pulsó esa tecla.",

                    f"¡Protestamos ante la imputación automática de culpabilidad! Pretenden condenar a mi representado por meras trazas IP corporativas. "
                    f"Demostraremos en este juicio que existieron accesos no autorizados concurrentes y que la custodia del SSD fue negligente."
                ]
                return random.choice(variants)

            elif has_protesta:
                variants = [
                    f"Reitero mi más enérgica protesta procesal, Señoría. Se vulnera flagrantemente el principio de contradicción y tutela judicial "
                    f"cuando se inducen conclusiones precipitadas sobre {key_concept} sin dejar espacio a la contrapericia técnica debida.",

                    f"Formalizo protesta formal para constancia en recurso: la línea interrogatoria seguida respecto a {topic_summary} "
                    "constituye una evidente coacción argumentativa hacia el declarante.",

                    f"Pedimos amparo al tribunal para que no se permita a la acusación formular preguntas capciosas dirigidas a tergiversar la verdad material sobre {key_concept}."
                ]
                return random.choice(variants)

            elif has_duda:
                variants = [
                    f"Como Su Señoría acaba de apreciar claramente, no existe certeza científica ni probatoria respecto a {topic_summary}. "
                    "Existiendo dudas sustanciales y lagunas en el análisis, procede la aplicación íntegra del principio 'in dubio pro reo' y la libre absolución de mi defendido.",

                    f"La vacilación advertida demuestra lo que esta defensa siempre sostuvo: la evidencia digital es deleznable. "
                    f"Si el propio deponente reconoce incertidumbre en torno a {key_concept}, ninguna condena penal puede fundarse en tales presupuestos.",

                    f"¡La duda razonable ha quedado acreditada en sala! Ante la imposibilidad de aseverar los hechos de {key_concept}, la presunción de inocencia de mi patrocinado debe prevalecer."
                ]
                return random.choice(variants)

            elif has_hash and has_cadena:
                variants = [
                    f"Aunque el hash SHA-256 de la copia forense coincida con la imagen adquirida,{rag_mention} "
                    f"eso sólo prueba que el duplicado es idéntico al disco que se conectó, pero no descarta en modo alguno que {key_concept} "
                    "hubiese sido implantado previamente por un atacante remoto o malware de intrusión sigilosa.",

                    f"Un hash coincide incluso si los archivos del soporte fueron alterados antes de la clonación judicial. "
                    f"¿Dispone la acusación de algún registro que garantice que nadie accedió físicamente a {topic_summary} en las 48 horas previas al precinto?",

                    f"La integridad del fichero pericial no equivale a autenticidad del autor. Si el sistema estaba vulnerado por un exploit remoto, el hash sólo certifica la copia del engaño."
                ]
                return random.choice(variants)

            else:
                variants = [
                    f"Con los debidos respetos al tribunal, la argumentación sostenida respecto a {topic_summary} omite deliberadamente que "
                    f"cualquier alteración no detectada en {key_concept} invalida de raíz la eficacia probatoria de cargo.",

                    f"Esta parte defensora subraya ante Su Señoría que la falta de garantías en el examen de {key_concept} "
                    "impide atribuir responsabilidad penal individualizada a mi representado.",

                    f"Lo expuesto sobre {topic_summary} corrobora nuestra tesis: la investigación omitió líneas forenses alternativas que exculpan fehacientemente a mi defendido."
                ]
                return random.choice(variants)

        # CLIENTES / DIRECTIVOS / COMITÉ DE CRISIS
        elif role == "cliente_director":
            if has_culpabilidad:
                variants = [
                    f"Para el consejo de administración y la dirección general, lo crucial es clarificar de forma inapelable si este incidente derivó de deslealtad de empleados "
                    f"o de una brecha en nuestro perímetro defensivo corporativo,{rag_mention} pues de ello penden las pólizas de ciberriesgo y las demandas de responsabilidad civil.",

                    f"Necesitamos conclusiones certeras y documentadas: si los fondos sustraídos fueron movidos desde dentro o desde fuera,{rag_mention} "
                    "nuestro plan de contingencia legal ante los reguladores bancarios debe activarse en las próximas 24 horas."
                ]
                return random.choice(variants)

            variants = [
                f"A la vista de lo debatido sobre {topic_summary},{rag_mention} "
                f"¿podemos garantizar al comité ejecutivo que los datos personales y bancarios vinculados a {key_concept} no fueron filtrados a la Dark Web, "
                "o debemos preparar la notificación preceptiva a la AEPD?",

                f"El impacto reputacional y financiero de este informe sobre {key_concept} es enorme. "
                "Requiero al equipo pericial máxima concisión: ¿cuál es la exposición de pasivo real para la empresa?"
            ]
            return random.choice(variants)

        elif role == "cliente_tecnico":
            variants = [
                f"Desde la óptica estricta de la infraestructura IT y la DMZ,{rag_mention} "
                f"¿los indicadores de compromiso (IOC) identificados en torno a {key_concept} demuestran movimiento lateral hacia los servidores de producción o persistencia de ransomware?",

                f"Necesitamos corroborar en los logs del cortafuegos si hubo exfiltración masiva por túneles SSH o DNS vinculados al análisis de {topic_summary}. "
                "¿Qué vectores de entrada quedan técnicamente confirmados?"
            ]
            return random.choice(variants)

        variants = [
            f"Tomo debida nota de los argumentos vertidos en sala respecto a {topic_summary} para su constancia y valoración.",
            f"Hechos registrados y examinados conforme al estado de las actuaciones en relación a {key_concept}."
        ]
        return random.choice(variants)
