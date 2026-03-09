"""
Human-in-the-Loop - Ejemplos ejecutables
==========================================
Prerequisitos:
    pip install langgraph python-dotenv

Nota: Estos ejemplos simulan la interacción humana programáticamente.
      En producción, la pausa permitiría intervención real del usuario
      (vía UI, API, terminal, etc.).
"""

from typing import Annotated, TypedDict
from operator import add
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# ============================================================
# 1. interrupt_before básico
# ============================================================
print("=" * 60)
print("1. INTERRUPT_BEFORE BÁSICO")
print("=" * 60)


class ApprovalState(TypedDict):
    tarea: str
    aprobado: bool
    resultado: str
    log: Annotated[list[str], add]


def preparar_tarea(state: ApprovalState) -> dict:
    return {
        "log": [f"📋 Tarea preparada: '{state['tarea']}'"],
        "resultado": f"Listo para ejecutar: {state['tarea']}"
    }


def ejecutar_tarea(state: ApprovalState) -> dict:
    if state["aprobado"]:
        return {
            "log": ["✅ Tarea ejecutada (aprobada por humano)"],
            "resultado": f"Completado: {state['tarea']}"
        }
    return {
        "log": ["❌ Tarea cancelada (no aprobada)"],
        "resultado": "Cancelado"
    }


memory1 = MemorySaver()

graph1 = StateGraph(ApprovalState)
graph1.add_node("preparar", preparar_tarea)
graph1.add_node("ejecutar", ejecutar_tarea)

graph1.add_edge(START, "preparar")
graph1.add_edge("preparar", "ejecutar")
graph1.add_edge("ejecutar", END)

# Compilar con interrupción ANTES de "ejecutar"
app1 = graph1.compile(
    checkpointer=memory1,
    interrupt_before=["ejecutar"]
)

config1 = {"configurable": {"thread_id": "tarea-001"}}

# Paso 1: Ejecutar hasta la interrupción
print("--- Paso 1: Ejecutar hasta la pausa ---")
result1 = app1.invoke(
    {"tarea": "Enviar newsletter a 1000 usuarios", "aprobado": False, "resultado": "", "log": []},
    config1
)
print(f"  Estado actual: {result1}")
# Ejemplo salida →   Estado actual: {'tarea': 'Enviar newsletter a 1000 usuarios', 'aprobado': False, 'resultado': 'Listo para ejecutar: Enviar newsletter a 1000 usuarios', 'log': ["📋 Tarea preparada: 'Enviar newsletter a 1000 usuarios'"]}

# Paso 2: Revisar el estado
print("\n--- Paso 2: Revisar estado pausado ---")
state_snapshot = app1.get_state(config1)
print(f"  Siguiente nodo: {state_snapshot.next}")
# Ejemplo salida →   Siguiente nodo: ('ejecutar',)
print(f"  Tarea: {state_snapshot.values['tarea']}")
# Ejemplo salida →   Tarea: Enviar newsletter a 1000 usuarios

# Paso 3: Aprobar y continuar
print("\n--- Paso 3: Aprobar y continuar ---")
app1.update_state(config1, {"aprobado": True})
result1_final = app1.invoke(None, config1)

print(f"  Resultado: {result1_final['resultado']}")
# Ejemplo salida →   Resultado: Completado: Enviar newsletter a 1000 usuarios
print(f"  Log completo:")
for entry in result1_final["log"]:
    print(f"    {entry}")
# Ejemplo salida →     📋 Tarea preparada: 'Enviar newsletter a 1000 usuarios'
# Ejemplo salida →     ✅ Tarea ejecutada (aprobada por humano)
print()


# ============================================================
# 2. interrupt_before con rechazo
# ============================================================
print("=" * 60)
print("2. INTERRUPT_BEFORE CON RECHAZO")
print("=" * 60)

memory2 = MemorySaver()
app2 = graph1.compile(
    checkpointer=memory2,
    interrupt_before=["ejecutar"]
)

config2 = {"configurable": {"thread_id": "tarea-002"}}

# Ejecutar hasta la pausa
app2.invoke(
    {"tarea": "Borrar base de datos de producción", "aprobado": False, "resultado": "", "log": []},
    config2
)

# Revisar
state2 = app2.get_state(config2)
print(f"  Tarea pendiente: {state2.values['tarea']}")
# Ejemplo salida →   Tarea pendiente: Borrar base de datos de producción

# Rechazar (no aprobamos, continuamos con aprobado=False)
print("  ⚠️ Rechazando tarea peligrosa...")
result2 = app2.invoke(None, config2)  # Continúa sin aprobar
print(f"  Resultado: {result2['resultado']}")
# Ejemplo salida →   Resultado: Cancelado
print()


# ============================================================
# 3. interrupt_after (revisar resultado generado)
# ============================================================
print("=" * 60)
print("3. INTERRUPT_AFTER (REVISAR DRAFT)")
print("=" * 60)


class DraftState(TypedDict):
    tema: str
    draft: str
    version_final: str
    log: Annotated[list[str], add]


def generar_draft(state: DraftState) -> dict:
    # Simula generación de LLM
    draft = f"[DRAFT] Artículo sobre '{state['tema']}': Este es un borrador automático sobre el tema solicitado."
    return {"draft": draft, "log": ["📝 Draft generado automáticamente"]}


def publicar(state: DraftState) -> dict:
    return {
        "version_final": state["draft"],
        "log": ["🚀 Publicado"]
    }


memory3 = MemorySaver()

graph3 = StateGraph(DraftState)
graph3.add_node("generar", generar_draft)
graph3.add_node("publicar", publicar)

graph3.add_edge(START, "generar")
graph3.add_edge("generar", "publicar")
graph3.add_edge("publicar", END)

# Pausa DESPUÉS de generar (para revisar el draft)
app3 = graph3.compile(
    checkpointer=memory3,
    interrupt_after=["generar"]
)

config3 = {"configurable": {"thread_id": "articulo-001"}}

# Paso 1: Generar draft
print("--- Paso 1: Generar draft ---")
result3 = app3.invoke(
    {"tema": "Inteligencia Artificial", "draft": "", "version_final": "", "log": []},
    config3
)
print(f"  Draft generado: {result3['draft']}")
# Ejemplo salida →   Draft generado: [DRAFT] Artículo sobre 'Inteligencia Artificial': Este es un borrador automático sobre el tema solicitado.

# Paso 2: Humano revisa y corrige el draft
print("\n--- Paso 2: Humano corrige el draft ---")
app3.update_state(config3, {
    "draft": "La Inteligencia Artificial está transformando el mundo. Este artículo explora sus aplicaciones más impactantes.",
    "log": ["✏️ Draft corregido por humano"]
})

# Paso 3: Continuar (publicar con el draft corregido)
print("--- Paso 3: Publicar versión corregida ---")
result3_final = app3.invoke(None, config3)
print(f"  Versión final: {result3_final['version_final']}")
# Ejemplo salida →   Versión final: La Inteligencia Artificial está transformando el mundo. Este artículo explora sus aplicaciones más impactantes.
print(f"  Log:")
for entry in result3_final["log"]:
    print(f"    {entry}")
# Ejemplo salida →     📝 Draft generado automáticamente
# Ejemplo salida →     ✏️ Draft corregido por humano
# Ejemplo salida →     🚀 Publicado
print()


# ============================================================
# 4. Múltiples puntos de interrupción
# ============================================================
print("=" * 60)
print("4. MÚLTIPLES PUNTOS DE INTERRUPCIÓN")
print("=" * 60)


class PipelineState(TypedDict):
    datos: str
    validado: bool
    transformado: bool
    resultado: str
    log: Annotated[list[str], add]


def cargar_datos(state: PipelineState) -> dict:
    return {"datos": state["datos"].strip(), "log": ["1️⃣ Datos cargados"]}


def validar_datos(state: PipelineState) -> dict:
    es_valido = len(state["datos"]) > 5
    return {"validado": es_valido, "log": [f"2️⃣ Validación: {'OK' if es_valido else 'FAIL'}"]}


def transformar_datos(state: PipelineState) -> dict:
    return {
        "datos": state["datos"].upper(),
        "transformado": True,
        "log": ["3️⃣ Datos transformados"]
    }


def guardar_datos(state: PipelineState) -> dict:
    return {
        "resultado": f"Guardado: {state['datos']}",
        "log": ["4️⃣ Datos guardados"]
    }


memory4 = MemorySaver()

graph4 = StateGraph(PipelineState)
graph4.add_node("cargar", cargar_datos)
graph4.add_node("validar", validar_datos)
graph4.add_node("transformar", transformar_datos)
graph4.add_node("guardar", guardar_datos)

graph4.add_edge(START, "cargar")
graph4.add_edge("cargar", "validar")
graph4.add_edge("validar", "transformar")
graph4.add_edge("transformar", "guardar")
graph4.add_edge("guardar", END)

# Dos puntos de interrupción
app4 = graph4.compile(
    checkpointer=memory4,
    interrupt_before=["transformar", "guardar"]
)

config4 = {"configurable": {"thread_id": "pipeline-001"}}

# Fase 1: Cargar y validar
print("--- Fase 1: Cargar y validar ---")
r4 = app4.invoke(
    {"datos": "  datos de ejemplo  ", "validado": False, "transformado": False, "resultado": "", "log": []},
    config4
)
state4 = app4.get_state(config4)
print(f"  Parado antes de: {state4.next}")
# Ejemplo salida →   Parado antes de: ('transformar',)
print(f"  Validado: {state4.values['validado']}")
# Ejemplo salida →   Validado: True

# Fase 2: Aprobar transformación
print("\n--- Fase 2: Aprobar transformación ---")
r4 = app4.invoke(None, config4)
state4 = app4.get_state(config4)
print(f"  Parado antes de: {state4.next}")
# Ejemplo salida →   Parado antes de: ('guardar',)
print(f"  Datos transformados: {state4.values['datos']}")
# Ejemplo salida →   Datos transformados: DATOS DE EJEMPLO

# Fase 3: Aprobar guardado
print("\n--- Fase 3: Aprobar guardado ---")
r4_final = app4.invoke(None, config4)
print(f"  Resultado: {r4_final['resultado']}")
# Ejemplo salida →   Resultado: Guardado: DATOS DE EJEMPLO
print(f"  Log completo:")
for entry in r4_final["log"]:
    print(f"    {entry}")
# Ejemplo salida →     1️⃣ Datos cargados
# Ejemplo salida →     2️⃣ Validación: OK
# Ejemplo salida →     3️⃣ Datos transformados
# Ejemplo salida →     4️⃣ Datos guardados
print()


# ============================================================
# 5. update_state con as_node
# ============================================================
print("=" * 60)
print("5. UPDATE_STATE CON AS_NODE")
print("=" * 60)


class ReviewState(TypedDict):
    propuesta: str
    revision: str
    aprobado: bool


def crear_propuesta(state: ReviewState) -> dict:
    return {"propuesta": f"Propuesta automática: Implementar feature X"}


def revisar(state: ReviewState) -> dict:
    return {"revision": f"Revisión de: {state['propuesta']}"}


def aprobar(state: ReviewState) -> dict:
    return {"aprobado": True}


memory5 = MemorySaver()

graph5 = StateGraph(ReviewState)
graph5.add_node("crear", crear_propuesta)
graph5.add_node("revisar", revisar)
graph5.add_node("aprobar", aprobar)

graph5.add_edge(START, "crear")
graph5.add_edge("crear", "revisar")
graph5.add_edge("revisar", "aprobar")
graph5.add_edge("aprobar", END)

app5 = graph5.compile(
    checkpointer=memory5,
    interrupt_before=["revisar"]
)

config5 = {"configurable": {"thread_id": "review-001"}}

# Ejecutar hasta la pausa
app5.invoke({"propuesta": "", "revision": "", "aprobado": False}, config5)

# Inyectar una propuesta manual como si viniera del nodo "crear"
print("--- Inyectando propuesta manual (as_node='crear') ---")
app5.update_state(
    config5,
    {"propuesta": "Propuesta MANUAL: Rediseñar la arquitectura del sistema"},
    as_node="crear"
)

# Continuar
result5 = app5.invoke(None, config5)
print(f"  Propuesta: {result5['propuesta']}")
# Ejemplo salida →   Propuesta: Propuesta MANUAL: Rediseñar la arquitectura del sistema
print(f"  Revisión: {result5['revision']}")
# Ejemplo salida →   Revisión: Revisión de: Propuesta MANUAL: Rediseñar la arquitectura del sistema
print(f"  Aprobado: {result5['aprobado']}")
# Ejemplo salida →   Aprobado: True
print()

print("=" * 60)
print("✅ Todos los ejemplos de Human-in-the-Loop ejecutados")
print("=" * 60)
