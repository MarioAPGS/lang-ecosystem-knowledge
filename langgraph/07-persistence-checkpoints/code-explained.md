# Persistence y Checkpoints - Explicación Detallada

## ¿Qué es la persistencia en LangGraph?

La **persistencia** permite que un grafo **guarde su estado** y pueda retomarse más tarde. Esto habilita:

- **Conversaciones con memoria**: El chatbot recuerda lo anterior
- **Threads múltiples**: Cada usuario/sesión tiene su propio historial
- **Recuperación**: Si algo falla, puedes retomar desde el último checkpoint
- **Time travel**: Navegar por estados anteriores del grafo

---

## MemorySaver: checkpointer en memoria

El checkpointer más simple. Guarda los estados **en memoria** (se pierde al cerrar la aplicación):

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = graph.compile(checkpointer=memory)
```

> **Para producción** existen checkpointers persistentes como `SqliteSaver`, `PostgresSaver`, etc.

---

## thread_id: identificador de sesión

Cada ejecución se identifica por un `thread_id` en la configuración:

```python
config = {"configurable": {"thread_id": "sesion-abc-123"}}
result = app.invoke(input, config)
```

- Mismo `thread_id` → **continúa** la conversación/estado anterior
- Nuevo `thread_id` → **empieza de cero**

---

## Flujo con persistencia

```
Thread "usuario-1":
  invoke #1 → Estado A → checkpoint guardado
  invoke #2 → Estado A → Estado B → checkpoint guardado
  invoke #3 → Estado B → Estado C → checkpoint guardado

Thread "usuario-2":
  invoke #1 → Estado X → checkpoint guardado
  invoke #2 → Estado X → Estado Y → checkpoint guardado
```

Cada thread tiene su **propia línea temporal** de estados.

---

## get_state: consultar el estado actual

```python
state = app.get_state(config)
print(state.values)       # Estado actual
print(state.next)         # Siguiente nodo (si hay interrupción)
print(state.config)       # Configuración del checkpoint
```

---

## get_state_history: historial de estados

Permite navegar por **todos los checkpoints** de un thread:

```python
for state in app.get_state_history(config):
    print(f"Checkpoint: {state.config}")
    print(f"  Valores: {state.values}")
    print(f"  Siguiente: {state.next}")
```

---

## Time Travel: volver a un estado anterior

Puedes **retomar la ejecución desde cualquier checkpoint anterior**:

```python
# Obtener el historial
historia = list(app.get_state_history(config))

# Elegir un checkpoint anterior
checkpoint_anterior = historia[2]  # 3er estado desde el más reciente

# Ejecutar desde ese checkpoint
result = app.invoke(None, checkpoint_anterior.config)
```

---

## Chatbot con persistencia

El caso de uso más común: un chatbot que recuerda conversaciones:

```python
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

def chatbot(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"])]}

graph = StateGraph(MessagesState)
graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# Turno 1
config = {"configurable": {"thread_id": "chat-lucia"}}
app.invoke({"messages": [("human", "Me llamo Lucía")]}, config)

# Turno 2 — recuerda el turno anterior
app.invoke({"messages": [("human", "¿Cómo me llamo?")]}, config)
# → "Te llamas Lucía"
```

---

## Múltiples threads simultáneos

```python
# Cada usuario tiene su propio thread
config_lucia = {"configurable": {"thread_id": "lucia-session"}}
config_carlos = {"configurable": {"thread_id": "carlos-session"}}

# Las conversaciones son completamente independientes
app.invoke({"messages": [("human", "Soy Lucía")]}, config_lucia)
app.invoke({"messages": [("human", "Soy Carlos")]}, config_carlos)
```

---

## Checkpointers para producción

| Checkpointer | Tipo | Paquete |
|---|---|---|
| `MemorySaver` | En memoria (dev) | `langgraph` |
| `SqliteSaver` | SQLite (local) | `langgraph-checkpoint-sqlite` |
| `PostgresSaver` | PostgreSQL (producción) | `langgraph-checkpoint-postgres` |

```bash
pip install langgraph-checkpoint-sqlite
```

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Persistencia en archivo local
with SqliteSaver.from_conn_string("checkpoints.db") as memory:
    app = graph.compile(checkpointer=memory)
```

---

## Resumen

| Concepto | API | Uso |
|---|---|---|
| MemorySaver | `MemorySaver()` | Checkpointer en memoria (dev) |
| thread_id | `{"configurable": {"thread_id": "..."}}` | Identificar sesión |
| get_state | `app.get_state(config)` | Ver estado actual |
| get_state_history | `app.get_state_history(config)` | Ver historial de checkpoints |
| Time travel | `app.invoke(None, old_config)` | Retomar desde checkpoint anterior |
| Continuar | `app.invoke({"messages": [nuevo_msg]}, config)` | Añadir al historial existente |
