# Informe Técnico de Estimación de Esfuerzo I+D/IA

**Proyecto:** Plataforma de Simulación Virtual de Audiencias y Reuniones con Clientes  
**Cliente:** Huella Forense  
**Elaborado por:** Departamento de I+D e Inteligencia Artificial  

---

## 1. Resumen Ejecutivo de la Estimación

- **Esfuerzo Total Estimado:** **420 – 645 horas de desarrollo especializado**.
- **Plazo de Entrega MVP Funcional:** **10 a 12 semanas** (con dedicación de un equipo core de 2 ingenieros).
- **Régimen de Entrega:** Metodología ágil iterativa en 3 fases (Fundación, Simulación & RAG, y Evaluación & Despliegue).

---

## 2. Desglose Detallado por Bloque de Trabajo (14 Bloques)

| Bloque | Tarea Solicitada en el Documento de Requisitos | Horas Min | Horas Max | Entregable Clave |
| :---: | :--- | :---: | :---: | :--- |
| **B1** | Análisis funcional y técnico de los requisitos | 20 h | 30 h | Especificación de casos de uso y diagramas de flujo interactivo |
| **B2** | Diseño de la arquitectura de escenarios virtuales | 30 h | 45 h | Documento de arquitectura modular, API REST y esquemas de datos |
| **B3** | Desarrollo y configuración de los escenarios (Audiencia y Reunión) | 40 h | 60 h | Máquina de estados para sala judicial y reunión de crisis |
| **B4** | Implementación de personajes y sus respectivos roles | 35 h | 50 h | Agentes del Juez, Fiscal, Abogados y avatar pasivo (monigote gris) |
| **B5** | Definición e implementación de la lógica de interacción | 30 h | 45 h | Orquestador de turnos, objeciones y moderación procesal |
| **B6** | Integración y configuración de la IA (Prompts y LLM) | 45 h | 70 h | Conectores LLM con RAG, control de temperatura y baja latencia |
| **B7** | Mecanismo de gestión del conocimiento forense | 35 h | 55 h | Repositorio híbrido (SQLite WAL + BM25/Vectorial) con control de acceso |
| **B8** | Estructura para crear y gestionar diferentes casos | 25 h | 40 h | `CaseManager` desacoplado en JSON/YAML con validación Pydantic |
| **B9** | Sistema de valoración y generación de feedback | 40 h | 60 h | Motor de rúbricas analíticas y generación de informes de desempeño |
| **B10**| Gestión y almacenamiento de contenidos y recursos | 20 h | 35 h | Persistencia de evidencias digitales, actas y documentación de casos |
| **B11**| Pruebas funcionales y validación de interacciones | 30 h | 45 h | Suite de tests automatizados (pytest) y pruebas de coherencia procesal |
| **B12**| Revisión y ajustes tras pruebas con Huella Forense | 25 h | 40 h | Calibración de personalidad de agentes y afinamiento de rúbricas |
| **B13**| Documentación técnica y funcional | 20 h | 30 h | Manuales de arquitectura, guía docente para crear casos y OpenAPI |
| **B14**| Puesta en producción de la primera versión (MVP) | 25 h | 40 h | Contenedores Docker, CI/CD y despliegue del entorno piloto |
| **TOTAL** | **Esfuerzo Completo I+D/IA** | **420 h** | **645 h** | **Plataforma Integral MVP en 10-12 Semanas** |

---

## 3. Dependencias Críticas Identificadas

Para cumplir con este cronograma sin bloqueos, se requiere que Huella Forense suministre:
1. **Guiones completos y diálogos tipo:** Casos de prueba reales para afinar las preguntas del Fiscal y Abogado Defensor.
2. **Perfiles y directrices de cada rol:** Límites de agresividad retórica del fiscal y tolerancia del juez.
3. **Indicadores y criterios de baremación:** Listado de conceptos obligatorios, errores eliminatorios y pesos relativos de cada competencia.
4. **Infraestructura de inferencia:** Definición sobre uso de APIs en la nube (OpenAI / Anthropic) o servidor local GPU con modelos Open Source.

---

## 4. Riesgos Técnicos y Plan de Mitigación

1. **Alucinaciones o respuestas jurídicamente incorrectas:**
   - *Mitigación:* Se implementa **RAG estricto con grounding forzado** sobre la documentación del caso y normas periciales (UNE 71506 / ISO 27037).
2. **Latencia conversacional perceptible:**
   - *Mitigación:* Generación con streaming de tokens (SSE) y segmentación de turnos para tiempos de respuesta inferiores a 1.5 segundos.
3. **Dependencia de programación para nuevos casos:**
   - *Mitigación:* Arquitectura basada en **ficheros declarativos JSON/YAML**. El personal docente podrá crear un caso nuevo en minutos sin escribir código.
