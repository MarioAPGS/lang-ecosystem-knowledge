"""
Nodos y Edges - Ejemplos ejecutables
======================================
Prerequisitos:
    pip install langgraph langchain-openai python-dotenv

Configuración:
    Crea un archivo .env en la raíz del proyecto con:
    OPENAI_API_KEY=sk-...
"""

import os
from typing import Annotated, TypedDict
from operator import add
from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END

# ============================================================
# 1. Grafo lineal básico: A → B → C
# ============================================================
print("=" * 60)
print("1. GRAFO LINEAL: A → B → C")
print("=" * 60)


class PipelineState(TypedDict):
    texto: str
    log: Annotated[list[str], add]


def nodo_a(state: PipelineState) -> dict:
    return {
        "texto": state["texto"].strip(),
        "log": ["A: texto limpiado"]
    }


def nodo_b(state: PipelineState) -> dict:
    return {
        "texto": state["texto"].upper(),
        "log": ["B: texto en mayúsculas"]
    }


def nodo_c(state: PipelineState) -> dict:
    return {
        "texto": f"[{state['texto']}]",
        "log": ["C: texto envuelto en brackets"]
    }


graph1 = StateGraph(PipelineState)
graph1.add_node("A", nodo_a)
graph1.add_node("B", nodo_b)
graph1.add_node("C", nodo_c)

graph1.add_edge(START, "A")
graph1.add_edge("A", "B")
graph1.add_edge("B", "C")
graph1.add_edge("C", END)

app1 = graph1.compile()
result1 = app1.invoke({"texto": "  hola langgraph  ", "log": []})

print(f"Texto final: {result1['texto']}")
# Ejemplo salida → Texto final: [HOLA LANGGRAPH]
print(f"Log de ejecución:")
for entry in result1["log"]:
    print(f"  → {entry}")
# Ejemplo salida →   → A: texto limpiado
# Ejemplo salida →   → B: texto en mayúsculas
# Ejemplo salida →   → C: texto envuelto en brackets
print()


# ============================================================
# 2. Fan-out: ejecución paralela
# ============================================================
print("=" * 60)
print("2. FAN-OUT: EJECUCIÓN PARALELA")
print("=" * 60)


class FanoutState(TypedDict):
    texto: str
    resultados: Annotated[list[str], add]


def analyser_longitud(state: FanoutState) -> dict:
    longitud = len(state["texto"])
    return {"resultados": [f"📏 Longitud: {longitud} caracteres"]}


def analyser_palabras(state: FanoutState) -> dict:
    palabras = len(state["texto"].split())
    return {"resultados": [f"📝 Palabras: {palabras}"]}


def analyser_mayusculas(state: FanoutState) -> dict:
    mayusculas = sum(1 for c in state["texto"] if c.isupper())
    return {"resultados": [f"🔠 Mayúsculas: {mayusculas}"]}


def reporte_final(state: FanoutState) -> dict:
    print("  Análisis completado:")
    for r in state["resultados"]:
        print(f"    {r}")
    return {}


graph2 = StateGraph(FanoutState)
graph2.add_node("longitud", analyser_longitud)
graph2.add_node("palabras", analyser_palabras)
graph2.add_node("mayusculas", analyser_mayusculas)
graph2.add_node("reporte", reporte_final)

# Fan-out desde START a tres nodos en paralelo
graph2.add_edge(START, "longitud")
graph2.add_edge(START, "palabras")
graph2.add_edge(START, "mayusculas")

# Todos convergen en reporte
graph2.add_edge("longitud", "reporte")
graph2.add_edge("palabras", "reporte")
graph2.add_edge("mayusculas", "reporte")

graph2.add_edge("reporte", END)

app2 = graph2.compile()
result2 = app2.invoke({"texto": "LangGraph Es Un Framework Genial", "resultados": []})
# Ejemplo salida →   Análisis completado:
# Ejemplo salida →     📏 Longitud: 32 caracteres
# Ejemplo salida →     📝 Palabras: 6
# Ejemplo salida →     🔠 Mayúsculas: 5
print()


# ============================================================
# 3. Nodo con side effects (logging)
# ============================================================
print("=" * 60)
print("3. NODO CON SIDE EFFECTS")
print("=" * 60)


class TaskState(TypedDict):
    tarea: str
    completada: bool


def validar_tarea(state: TaskState) -> dict:
    print(f"  📋 Validando tarea: '{state['tarea']}'")
    # Ejemplo salida →   📋 Validando tarea: 'Aprender LangGraph'
    es_valida = len(state["tarea"]) > 0
    print(f"  ✅ Tarea válida: {es_valida}")
    # Ejemplo salida →   ✅ Tarea válida: True
    return {}


def ejecutar_tarea(state: TaskState) -> dict:
    print(f"  🔄 Ejecutando tarea: '{state['tarea']}'")
    # Ejemplo salida →   🔄 Ejecutando tarea: 'Aprender LangGraph'
    return {"completada": True}


def confirmar(state: TaskState) -> dict:
    print(f"  🎉 Tarea completada: {state['completada']}")
    # Ejemplo salida →   🎉 Tarea completada: True
    return {}


graph3 = StateGraph(TaskState)
graph3.add_node("validar", validar_tarea)
graph3.add_node("ejecutar", ejecutar_tarea)
graph3.add_node("confirmar", confirmar)

graph3.add_edge(START, "validar")
graph3.add_edge("validar", "ejecutar")
graph3.add_edge("ejecutar", "confirmar")
graph3.add_edge("confirmar", END)

app3 = graph3.compile()
result3 = app3.invoke({"tarea": "Aprender LangGraph", "completada": False})
print()


# ============================================================
# 4. Stream para ver ejecución paso a paso
# ============================================================
print("=" * 60)
print("4. STREAM - EJECUCIÓN PASO A PASO")
print("=" * 60)


class CounterState(TypedDict):
    valor: int
    historial: Annotated[list[str], add]


def incrementar(state: CounterState) -> dict:
    nuevo = state["valor"] + 1
    return {"valor": nuevo, "historial": [f"incrementar → {nuevo}"]}


def duplicar(state: CounterState) -> dict:
    nuevo = state["valor"] * 2
    return {"valor": nuevo, "historial": [f"duplicar → {nuevo}"]}


def restar_uno(state: CounterState) -> dict:
    nuevo = state["valor"] - 1
    return {"valor": nuevo, "historial": [f"restar_uno → {nuevo}"]}


graph4 = StateGraph(CounterState)
graph4.add_node("incrementar", incrementar)
graph4.add_node("duplicar", duplicar)
graph4.add_node("restar_uno", restar_uno)

graph4.add_edge(START, "incrementar")
graph4.add_edge("incrementar", "duplicar")
graph4.add_edge("duplicar", "restar_uno")
graph4.add_edge("restar_uno", END)

app4 = graph4.compile()

print("Ejecutando con stream (valor inicial: 5):")
for step in app4.stream({"valor": 5, "historial": []}):
    nodo_name = list(step.keys())[0]
    nodo_data = step[nodo_name]
    print(f"  Nodo '{nodo_name}': valor = {nodo_data.get('valor', '?')}")
# Ejemplo salida →   Nodo 'incrementar': valor = 6
# Ejemplo salida →   Nodo 'duplicar': valor = 12
# Ejemplo salida →   Nodo 'restar_uno': valor = 11

final = app4.invoke({"valor": 5, "historial": []})
print(f"\nHistorial completo: {final['historial']}")
# Ejemplo salida → Historial completo: ['incrementar → 6', 'duplicar → 12', 'restar_uno → 11']
print()


# ============================================================
# 5. Nodo con LLM
# ============================================================
print("=" * 60)
print("5. NODO CON LLM")
print("=" * 60)

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


class LLMState(TypedDict):
    pregunta: str
    respuesta: str


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def generar_respuesta(state: LLMState) -> dict:
    messages = [
        SystemMessage(content="Responde en máximo una frase."),
        HumanMessage(content=state["pregunta"])
    ]
    response = llm.invoke(messages)
    return {"respuesta": response.content}


def formatear_respuesta(state: LLMState) -> dict:
    return {"respuesta": f"📝 {state['respuesta']}"}


graph5 = StateGraph(LLMState)
graph5.add_node("generar", generar_respuesta)
graph5.add_node("formatear", formatear_respuesta)

graph5.add_edge(START, "generar")
graph5.add_edge("generar", "formatear")
graph5.add_edge("formatear", END)

app5 = graph5.compile()
result5 = app5.invoke({"pregunta": "¿Qué es LangGraph?", "respuesta": ""})
print(f"Respuesta: {result5['respuesta']}")
# Ejemplo salida → Respuesta: 📝 LangGraph es un framework para construir aplicaciones con flujos de trabajo basados en grafos dirigidos.
print()


# ============================================================
# 6. Visualización del grafo fan-out
# ============================================================
print("=" * 60)
print("6. VISUALIZACIÓN DEL GRAFO FAN-OUT")
print("=" * 60)

print("\n--- Estructura del grafo paralelo ---")
print(app2.get_graph().draw_ascii())
print()

print("=" * 60)
print("✅ Todos los ejemplos de Nodos y Edges ejecutados")
print("=" * 60)
