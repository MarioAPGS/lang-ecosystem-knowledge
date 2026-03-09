"""
Conceptos Fundamentales de LangGraph - Ejemplos ejecutables
============================================================
Prerequisitos:
    pip install langgraph langchain-openai python-dotenv

Configuración:
    Crea un archivo .env en la raíz del proyecto con:
    OPENAI_API_KEY=sk-...
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# ============================================================
# 1. Grafo mínimo - Un solo nodo
# ============================================================
print("=" * 60)
print("1. GRAFO MÍNIMO - UN SOLO NODO")
print("=" * 60)


class SimpleState(TypedDict):
    mensaje: str


def procesar(state: SimpleState) -> dict:
    return {"mensaje": f"Procesado: {state['mensaje']}"}


graph = StateGraph(SimpleState)
graph.add_node("procesar", procesar)
graph.add_edge(START, "procesar")
graph.add_edge("procesar", END)

app = graph.compile()
result = app.invoke({"mensaje": "Hola LangGraph"})
print(f"Resultado: {result}")
# Ejemplo salida → Resultado: {'mensaje': 'Procesado: Hola LangGraph'}
print()


# ============================================================
# 2. Grafo lineal - Dos nodos secuenciales
# ============================================================
print("=" * 60)
print("2. GRAFO LINEAL - DOS NODOS SECUENCIALES")
print("=" * 60)


def mayusculas(state: SimpleState) -> dict:
    return {"mensaje": state["mensaje"].upper()}


def decorar(state: SimpleState) -> dict:
    return {"mensaje": f"✅ {state['mensaje']}"}


graph2 = StateGraph(SimpleState)
graph2.add_node("mayusculas", mayusculas)
graph2.add_node("decorar", decorar)

graph2.add_edge(START, "mayusculas")
graph2.add_edge("mayusculas", "decorar")
graph2.add_edge("decorar", END)

app2 = graph2.compile()
result2 = app2.invoke({"mensaje": "hola mundo"})
print(f"Resultado: {result2}")
# Ejemplo salida → Resultado: {'mensaje': '✅ HOLA MUNDO'}
print()


# ============================================================
# 3. Estado con múltiples campos
# ============================================================
print("=" * 60)
print("3. ESTADO CON MÚLTIPLES CAMPOS")
print("=" * 60)


class MultiState(TypedDict):
    texto: str
    longitud: int
    procesado: bool


def analizar_texto(state: MultiState) -> dict:
    return {
        "longitud": len(state["texto"]),
        "procesado": True
    }


def reportar(state: MultiState) -> dict:
    print(f"  Texto: '{state['texto']}'")
    # Ejemplo salida →   Texto: 'LangGraph es genial'
    print(f"  Longitud: {state['longitud']} caracteres")
    # Ejemplo salida →   Longitud: 19 caracteres
    print(f"  Procesado: {state['procesado']}")
    # Ejemplo salida →   Procesado: True
    return state


graph3 = StateGraph(MultiState)
graph3.add_node("analizar", analizar_texto)
graph3.add_node("reportar", reportar)

graph3.add_edge(START, "analizar")
graph3.add_edge("analizar", "reportar")
graph3.add_edge("reportar", END)

app3 = graph3.compile()
result3 = app3.invoke({"texto": "LangGraph es genial", "longitud": 0, "procesado": False})
print()


# ============================================================
# 4. Grafo de tres nodos - Pipeline de texto
# ============================================================
print("=" * 60)
print("4. PIPELINE DE TEXTO - TRES NODOS")
print("=" * 60)


class TextPipeline(TypedDict):
    texto: str
    pasos: int


def limpiar(state: TextPipeline) -> dict:
    texto_limpio = state["texto"].strip().lower()
    return {"texto": texto_limpio, "pasos": state["pasos"] + 1}


def capitalizar(state: TextPipeline) -> dict:
    texto_cap = state["texto"].title()
    return {"texto": texto_cap, "pasos": state["pasos"] + 1}


def finalizar(state: TextPipeline) -> dict:
    texto_final = f"[Resultado] {state['texto']}"
    return {"texto": texto_final, "pasos": state["pasos"] + 1}


graph4 = StateGraph(TextPipeline)
graph4.add_node("limpiar", limpiar)
graph4.add_node("capitalizar", capitalizar)
graph4.add_node("finalizar", finalizar)

graph4.add_edge(START, "limpiar")
graph4.add_edge("limpiar", "capitalizar")
graph4.add_edge("capitalizar", "finalizar")
graph4.add_edge("finalizar", END)

app4 = graph4.compile()
result4 = app4.invoke({"texto": "  HOLA MUNDO LANGGRAPH  ", "pasos": 0})
print(f"Texto final: {result4['texto']}")
# Ejemplo salida → Texto final: [Resultado] Hola Mundo Langgraph
print(f"Pasos ejecutados: {result4['pasos']}")
# Ejemplo salida → Pasos ejecutados: 3
print()


# ============================================================
# 5. Visualización del grafo
# ============================================================
print("=" * 60)
print("5. VISUALIZACIÓN DEL GRAFO")
print("=" * 60)

print("\n--- Representación ASCII ---")
print(app4.get_graph().draw_ascii())
# Ejemplo salida →
# +-----------+
# | __start__ |
# +-----------+
#       *
#       *
#       *
#   +----------+
#   | limpiar  |
#   +----------+
#       *
#       *
#       *
# +-------------+
# | capitalizar |
# +-------------+
#       *
#       *
#       *
# +-----------+
# | finalizar |
# +-----------+
#       *
#       *
#       *
#  +---------+
#  | __end__ |
#  +---------+

print("\n--- Representación Mermaid ---")
print(app4.get_graph().draw_mermaid())
# Ejemplo salida →
# graph TD;
#   __start__ --> limpiar;
#   limpiar --> capitalizar;
#   capitalizar --> finalizar;
#   finalizar --> __end__;
print()


# ============================================================
# 6. Invoke vs Stream
# ============================================================
print("=" * 60)
print("6. INVOKE VS STREAM")
print("=" * 60)

# invoke() devuelve el estado final
print("--- invoke() ---")
final = app4.invoke({"texto": "  streaming test  ", "pasos": 0})
print(f"Estado final: {final}")
# Ejemplo salida → Estado final: {'texto': '[Resultado] Streaming Test', 'pasos': 3}

# stream() devuelve cada paso intermedio
print("\n--- stream() ---")
for step in app4.stream({"texto": "  streaming test  ", "pasos": 0}):
    print(f"Paso: {step}")
# Ejemplo salida → Paso: {'limpiar': {'texto': 'streaming test', 'pasos': 1}}
# Ejemplo salida → Paso: {'capitalizar': {'texto': 'Streaming Test', 'pasos': 2}}
# Ejemplo salida → Paso: {'finalizar': {'texto': '[Resultado] Streaming Test', 'pasos': 3}}
print()

print("=" * 60)
print("✅ Todos los ejemplos de conceptos fundamentales ejecutados")
print("=" * 60)
