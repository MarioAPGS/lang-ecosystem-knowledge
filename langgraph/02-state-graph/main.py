"""
StateGraph y Estado - Ejemplos ejecutables
============================================
Prerequisitos:
    pip install langgraph langchain-openai python-dotenv

Configuración:
    Crea un archivo .env en la raíz del proyecto con:
    OPENAI_API_KEY=sk-...
"""

from typing import Annotated, TypedDict
from operator import add
from langgraph.graph import StateGraph, MessagesState, START, END

# ============================================================
# 1. Estado simple con sobreescritura
# ============================================================
print("=" * 60)
print("1. ESTADO SIMPLE CON SOBREESCRITURA")
print("=" * 60)


class SimpleState(TypedDict):
    texto: str
    paso_actual: str


def paso_a(state: SimpleState) -> dict:
    return {"texto": state["texto"] + " → A", "paso_actual": "A"}


def paso_b(state: SimpleState) -> dict:
    return {"texto": state["texto"] + " → B", "paso_actual": "B"}


graph1 = StateGraph(SimpleState)
graph1.add_node("paso_a", paso_a)
graph1.add_node("paso_b", paso_b)
graph1.add_edge(START, "paso_a")
graph1.add_edge("paso_a", "paso_b")
graph1.add_edge("paso_b", END)

app1 = graph1.compile()
result1 = app1.invoke({"texto": "inicio", "paso_actual": ""})
print(f"Texto: {result1['texto']}")
# Ejemplo salida → Texto: inicio → A → B
print(f"Paso actual: {result1['paso_actual']}")
# Ejemplo salida → Paso actual: B
print()


# ============================================================
# 2. Estado con Annotated + reducer (acumulación)
# ============================================================
print("=" * 60)
print("2. ESTADO CON REDUCER (ACUMULACIÓN)")
print("=" * 60)


class LogState(TypedDict):
    log: Annotated[list[str], add]  # Se acumula con +
    resultado: str                   # Se sobreescribe


def proceso_1(state: LogState) -> dict:
    return {
        "log": ["✅ Proceso 1 ejecutado"],
        "resultado": "parcial"
    }


def proceso_2(state: LogState) -> dict:
    return {
        "log": ["✅ Proceso 2 ejecutado"],
        "resultado": "completo"
    }


def proceso_3(state: LogState) -> dict:
    return {
        "log": [f"✅ Proceso 3 ejecutado (resultado previo: {state['resultado']})"],
        "resultado": "final"
    }


graph2 = StateGraph(LogState)
graph2.add_node("proceso_1", proceso_1)
graph2.add_node("proceso_2", proceso_2)
graph2.add_node("proceso_3", proceso_3)

graph2.add_edge(START, "proceso_1")
graph2.add_edge("proceso_1", "proceso_2")
graph2.add_edge("proceso_2", "proceso_3")
graph2.add_edge("proceso_3", END)

app2 = graph2.compile()
result2 = app2.invoke({"log": [], "resultado": ""})

print("Log acumulado:")
for entry in result2["log"]:
    print(f"  {entry}")
# Ejemplo salida →   ✅ Proceso 1 ejecutado
# Ejemplo salida →   ✅ Proceso 2 ejecutado
# Ejemplo salida →   ✅ Proceso 3 ejecutado (resultado previo: completo)
print(f"Resultado final: {result2['resultado']}")
# Ejemplo salida → Resultado final: final
print()


# ============================================================
# 3. Reducer personalizado
# ============================================================
print("=" * 60)
print("3. REDUCER PERSONALIZADO")
print("=" * 60)


def max_valor(existente: int, nuevo: int) -> int:
    """Solo actualiza si el nuevo valor es mayor."""
    return max(existente, nuevo)


def concat_con_separador(existente: str, nuevo: str) -> str:
    """Concatena con ' | ' como separador."""
    if not existente:
        return nuevo
    return f"{existente} | {nuevo}"


class CustomReducerState(TypedDict):
    max_score: Annotated[int, max_valor]
    historial: Annotated[str, concat_con_separador]


def evaluacion_1(state: CustomReducerState) -> dict:
    return {"max_score": 75, "historial": "eval_1"}


def evaluacion_2(state: CustomReducerState) -> dict:
    return {"max_score": 92, "historial": "eval_2"}


def evaluacion_3(state: CustomReducerState) -> dict:
    return {"max_score": 61, "historial": "eval_3"}


graph3 = StateGraph(CustomReducerState)
graph3.add_node("eval_1", evaluacion_1)
graph3.add_node("eval_2", evaluacion_2)
graph3.add_node("eval_3", evaluacion_3)

graph3.add_edge(START, "eval_1")
graph3.add_edge("eval_1", "eval_2")
graph3.add_edge("eval_2", "eval_3")
graph3.add_edge("eval_3", END)

app3 = graph3.compile()
result3 = app3.invoke({"max_score": 0, "historial": ""})
print(f"Max score: {result3['max_score']}")
# Ejemplo salida → Max score: 92
print(f"Historial: {result3['historial']}")
# Ejemplo salida → Historial: eval_1 | eval_2 | eval_3
print()


# ============================================================
# 4. MessagesState para chatbots
# ============================================================
print("=" * 60)
print("4. MESSAGESSTATE PARA CHATBOTS")
print("=" * 60)

from langchain_core.messages import HumanMessage, AIMessage


def chatbot_simple(state: MessagesState) -> dict:
    """Simula un chatbot que responde al último mensaje."""
    last_msg = state["messages"][-1]
    respuesta = AIMessage(content=f"Recibí tu mensaje: '{last_msg.content}'. ¡Soy un bot simple!")
    return {"messages": [respuesta]}


graph4 = StateGraph(MessagesState)
graph4.add_node("chatbot", chatbot_simple)
graph4.add_edge(START, "chatbot")
graph4.add_edge("chatbot", END)

app4 = graph4.compile()
result4 = app4.invoke({"messages": [HumanMessage(content="Hola, ¿qué tal?")]})

print("Conversación:")
for msg in result4["messages"]:
    role = "🧑" if isinstance(msg, HumanMessage) else "🤖"
    print(f"  {role} {msg.content}")
# Ejemplo salida →   🧑 Hola, ¿qué tal?
# Ejemplo salida →   🤖 Recibí tu mensaje: 'Hola, ¿qué tal?'. ¡Soy un bot simple!
print()


# ============================================================
# 5. MessagesState con múltiples turnos
# ============================================================
print("=" * 60)
print("5. MESSAGESSTATE CON MÚLTIPLES TURNOS")
print("=" * 60)


def responder(state: MessagesState) -> dict:
    """Responde según la cantidad de mensajes acumulados."""
    num_msgs = len(state["messages"])
    last = state["messages"][-1]
    respuesta = AIMessage(
        content=f"[Turno {num_msgs}] Respondiendo a: '{last.content}'"
    )
    return {"messages": [respuesta]}


graph5 = StateGraph(MessagesState)
graph5.add_node("responder", responder)
graph5.add_edge(START, "responder")
graph5.add_edge("responder", END)

app5 = graph5.compile()

# Simular varios turnos manualmente
conversacion = [HumanMessage(content="¿Qué es LangGraph?")]
result5 = app5.invoke({"messages": conversacion})
print(f"Turno 1: {result5['messages'][-1].content}")
# Ejemplo salida → Turno 1: [Turno 1] Respondiendo a: '¿Qué es LangGraph?'

# Segundo turno: pasamos todo el historial + nuevo mensaje
conversacion = result5["messages"] + [HumanMessage(content="¿Y para qué sirve?")]
result5 = app5.invoke({"messages": conversacion})
print(f"Turno 2: {result5['messages'][-1].content}")
# Ejemplo salida → Turno 2: [Turno 3] Respondiendo a: '¿Y para qué sirve?'

# Tercer turno
conversacion = result5["messages"] + [HumanMessage(content="Dame un ejemplo")]
result5 = app5.invoke({"messages": conversacion})
print(f"Turno 3: {result5['messages'][-1].content}")
# Ejemplo salida → Turno 3: [Turno 5] Respondiendo a: 'Dame un ejemplo'

print(f"\nTotal mensajes en historial: {len(result5['messages'])}")
# Ejemplo salida → Total mensajes en historial: 6
print()


# ============================================================
# 6. Retorno parcial vs completo
# ============================================================
print("=" * 60)
print("6. RETORNO PARCIAL VS COMPLETO")
print("=" * 60)


class FullState(TypedDict):
    nombre: str
    edad: int
    saludo: str
    procesado: bool


def generar_saludo(state: FullState) -> dict:
    # Solo retorna "saludo" y "procesado", deja "nombre" y "edad" intactos
    return {
        "saludo": f"¡Hola {state['nombre']}! Tienes {state['edad']} años.",
        "procesado": True
    }


graph6 = StateGraph(FullState)
graph6.add_node("saludar", generar_saludo)
graph6.add_edge(START, "saludar")
graph6.add_edge("saludar", END)

app6 = graph6.compile()
result6 = app6.invoke({
    "nombre": "Lucía",
    "edad": 28,
    "saludo": "",
    "procesado": False
})

print(f"Nombre (intacto): {result6['nombre']}")
# Ejemplo salida → Nombre (intacto): Lucía
print(f"Edad (intacta): {result6['edad']}")
# Ejemplo salida → Edad (intacta): 28
print(f"Saludo (generado): {result6['saludo']}")
# Ejemplo salida → Saludo (generado): ¡Hola Lucía! Tienes 28 años.
print(f"Procesado (actualizado): {result6['procesado']}")
# Ejemplo salida → Procesado (actualizado): True
print()

print("=" * 60)
print("✅ Todos los ejemplos de StateGraph y Estado ejecutados")
print("=" * 60)
