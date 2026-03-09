"""
Persistence y Checkpoints - Ejemplos ejecutables
===================================================
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

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage

# ============================================================
# 1. Persistencia básica con MemorySaver
# ============================================================
print("=" * 60)
print("1. PERSISTENCIA BÁSICA CON MEMORYSAVER")
print("=" * 60)


class CounterState(TypedDict):
    valor: int
    historial: Annotated[list[str], add]


def incrementar(state: CounterState) -> dict:
    nuevo = state["valor"] + 1
    return {"valor": nuevo, "historial": [f"Incrementado a {nuevo}"]}


memory1 = MemorySaver()

graph1 = StateGraph(CounterState)
graph1.add_node("incrementar", incrementar)
graph1.add_edge(START, "incrementar")
graph1.add_edge("incrementar", END)

app1 = graph1.compile(checkpointer=memory1)

config = {"configurable": {"thread_id": "counter-001"}}

# Primera invocación
r1 = app1.invoke({"valor": 0, "historial": []}, config)
print(f"Invocación 1: valor = {r1['valor']}")
# Ejemplo salida → Invocación 1: valor = 1

# Segunda invocación: continúa desde el estado guardado
r2 = app1.invoke({"valor": r1["valor"], "historial": []}, config)
print(f"Invocación 2: valor = {r2['valor']}")
# Ejemplo salida → Invocación 2: valor = 2

# Tercera invocación
r3 = app1.invoke({"valor": r2["valor"], "historial": []}, config)
print(f"Invocación 3: valor = {r3['valor']}")
# Ejemplo salida → Invocación 3: valor = 3

# Ver historial acumulado
state = app1.get_state(config)
print(f"Historial: {state.values['historial']}")
# Ejemplo salida → Historial: ['Incrementado a 3']
print()


# ============================================================
# 2. Múltiples threads independientes
# ============================================================
print("=" * 60)
print("2. MÚLTIPLES THREADS INDEPENDIENTES")
print("=" * 60)


class SessionState(TypedDict):
    nombre: str
    mensajes: Annotated[list[str], add]


def saludar(state: SessionState) -> dict:
    return {"mensajes": [f"¡Hola {state['nombre']}! Bienvenido/a."]}


def despedir(state: SessionState) -> dict:
    return {"mensajes": [f"Hasta luego, {state['nombre']}. ¡Vuelve pronto!"]}


memory2 = MemorySaver()

graph2 = StateGraph(SessionState)
graph2.add_node("saludar", saludar)
graph2.add_node("despedir", despedir)
graph2.add_edge(START, "saludar")
graph2.add_edge("saludar", "despedir")
graph2.add_edge("despedir", END)

app2 = graph2.compile(checkpointer=memory2)

# Thread de Lucía
config_lucia = {"configurable": {"thread_id": "session-lucia"}}
r_lucia = app2.invoke({"nombre": "Lucía", "mensajes": []}, config_lucia)

# Thread de Carlos
config_carlos = {"configurable": {"thread_id": "session-carlos"}}
r_carlos = app2.invoke({"nombre": "Carlos", "mensajes": []}, config_carlos)

print("Sesión de Lucía:")
for msg in r_lucia["mensajes"]:
    print(f"  {msg}")
# Ejemplo salida →   ¡Hola Lucía! Bienvenido/a.
# Ejemplo salida →   Hasta luego, Lucía. ¡Vuelve pronto!

print("\nSesión de Carlos:")
for msg in r_carlos["mensajes"]:
    print(f"  {msg}")
# Ejemplo salida →   ¡Hola Carlos! Bienvenido/a.
# Ejemplo salida →   Hasta luego, Carlos. ¡Vuelve pronto!

# Verificar que son independientes
state_lucia = app2.get_state(config_lucia)
state_carlos = app2.get_state(config_carlos)
print(f"\nThread Lucía - nombre: {state_lucia.values['nombre']}")
# Ejemplo salida → Thread Lucía - nombre: Lucía
print(f"Thread Carlos - nombre: {state_carlos.values['nombre']}")
# Ejemplo salida → Thread Carlos - nombre: Carlos
print()


# ============================================================
# 3. Chatbot con memoria persistente
# ============================================================
print("=" * 60)
print("3. CHATBOT CON MEMORIA PERSISTENTE")
print("=" * 60)


def chatbot_echo(state: MessagesState) -> dict:
    """Chatbot simple que responde basándose en el historial."""
    messages = state["messages"]
    last = messages[-1]
    num_msgs = len(messages)

    # Simular respuestas contextuales
    if num_msgs == 1:
        respuesta = f"¡Hola! Encantado de conocerte. Dijiste: '{last.content}'"
    elif num_msgs <= 4:
        respuesta = f"Interesante. Llevamos {num_msgs} mensajes en esta conversación. Tu último mensaje: '{last.content}'"
    else:
        respuesta = f"Ya llevamos {num_msgs} mensajes. ¡Qué buena charla! Respondiendo a: '{last.content}'"

    return {"messages": [AIMessage(content=respuesta)]}


memory3 = MemorySaver()

graph3 = StateGraph(MessagesState)
graph3.add_node("chatbot", chatbot_echo)
graph3.add_edge(START, "chatbot")
graph3.add_edge("chatbot", END)

app3 = graph3.compile(checkpointer=memory3)

config_chat = {"configurable": {"thread_id": "chat-001"}}

# Turno 1
print("--- Turno 1 ---")
r_t1 = app3.invoke({"messages": [HumanMessage(content="Hola, soy Lucía")]}, config_chat)
print(f"  🤖 {r_t1['messages'][-1].content}")
# Ejemplo salida →   🤖 ¡Hola! Encantado de conocerte. Dijiste: 'Hola, soy Lucía'

# Turno 2
print("--- Turno 2 ---")
r_t2 = app3.invoke({"messages": [HumanMessage(content="Estoy aprendiendo LangGraph")]}, config_chat)
print(f"  🤖 {r_t2['messages'][-1].content}")
# Ejemplo salida →   🤖 Interesante. Llevamos 3 mensajes en esta conversación. Tu último mensaje: 'Estoy aprendiendo LangGraph'

# Turno 3
print("--- Turno 3 ---")
r_t3 = app3.invoke({"messages": [HumanMessage(content="¿Cuántos mensajes llevamos?")]}, config_chat)
print(f"  🤖 {r_t3['messages'][-1].content}")
# Ejemplo salida →   🤖 Ya llevamos 5 mensajes. ¡Qué buena charla! Respondiendo a: '¿Cuántos mensajes llevamos?'

# Ver todo el historial
print("\n--- Historial completo ---")
state_chat = app3.get_state(config_chat)
for msg in state_chat.values["messages"]:
    role = "🧑" if isinstance(msg, HumanMessage) else "🤖"
    print(f"  {role} {msg.content}")
print()


# ============================================================
# 4. get_state_history: navegar checkpoints
# ============================================================
print("=" * 60)
print("4. GET_STATE_HISTORY - NAVEGAR CHECKPOINTS")
print("=" * 60)

print("Historial de checkpoints del chat:")
for i, state in enumerate(app3.get_state_history(config_chat)):
    num_msgs = len(state.values.get("messages", []))
    next_node = state.next
    print(f"  Checkpoint {i}: {num_msgs} mensajes, next={next_node}")
# Ejemplo salida →   Checkpoint 0: 6 mensajes, next=()
# Ejemplo salida →   Checkpoint 1: 5 mensajes, next=('chatbot',)
# Ejemplo salida →   Checkpoint 2: 4 mensajes, next=()
# Ejemplo salida →   Checkpoint 3: 3 mensajes, next=('chatbot',)
# Ejemplo salida →   Checkpoint 4: 2 mensajes, next=()
# Ejemplo salida →   Checkpoint 5: 1 mensajes, next=('chatbot',)
# Ejemplo salida →   Checkpoint 6: 0 mensajes, next=('__start__',)
print()


# ============================================================
# 5. Time Travel: bifurcar desde un checkpoint anterior
# ============================================================
print("=" * 60)
print("5. TIME TRAVEL - BIFURCAR DESDE CHECKPOINT ANTERIOR")
print("=" * 60)


class JuegoState(TypedDict):
    posicion: str
    movimientos: Annotated[list[str], add]
    puntos: int


def mover(state: JuegoState) -> dict:
    nueva_pos = f"pos_{state['puntos'] + 1}"
    return {
        "posicion": nueva_pos,
        "movimientos": [f"Move a {nueva_pos}"],
        "puntos": state["puntos"] + 10
    }


memory5 = MemorySaver()

graph5 = StateGraph(JuegoState)
graph5.add_node("mover", mover)
graph5.add_edge(START, "mover")
graph5.add_edge("mover", END)

app5 = graph5.compile(checkpointer=memory5)

config_juego = {"configurable": {"thread_id": "juego-001"}}

# Hacer 3 movimientos
print("--- Realizando 3 movimientos ---")
for i in range(3):
    state_actual = app5.get_state(config_juego)
    valor_actual = state_actual.values.get("puntos", 0) if state_actual.values else 0
    pos_actual = state_actual.values.get("posicion", "inicio") if state_actual.values else "inicio"
    movs_actual = state_actual.values.get("movimientos", []) if state_actual.values else []

    result = app5.invoke(
        {"posicion": pos_actual, "movimientos": movs_actual, "puntos": valor_actual},
        config_juego
    )
    print(f"  Movimiento {i+1}: posición={result['posicion']}, puntos={result['puntos']}")
# Ejemplo salida →   Movimiento 1: posición=pos_1, puntos=10
# Ejemplo salida →   Movimiento 2: posición=pos_2, puntos=20
# Ejemplo salida →   Movimiento 3: posición=pos_3, puntos=30

# Obtener historial de checkpoints
historial = list(app5.get_state_history(config_juego))
print(f"\nTotal checkpoints: {len(historial)}")
# Ejemplo salida → Total checkpoints: 6

# Time travel: volver al estado con 10 puntos (checkpoint más antiguo con puntos)
print("\n--- Time Travel: volviendo al primer movimiento ---")
for h in historial:
    if h.values.get("puntos") == 10:
        print(f"  Restaurando checkpoint con puntos={h.values['puntos']}")
        # Ejemplo salida →   Restaurando checkpoint con puntos=10

        # Hacer un movimiento diferente desde ese punto
        new_result = app5.invoke(
            {"posicion": h.values["posicion"], "movimientos": h.values["movimientos"], "puntos": h.values["puntos"]},
            h.config  # Usa la config del checkpoint anterior
        )
        print(f"  Nuevo camino: posición={new_result['posicion']}, puntos={new_result['puntos']}")
        # Ejemplo salida →   Nuevo camino: posición=pos_2, puntos=20
        break
print()

print("=" * 60)
print("✅ Todos los ejemplos de Persistence y Checkpoints ejecutados")
print("=" * 60)
