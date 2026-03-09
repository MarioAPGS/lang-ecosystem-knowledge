# StateGraph y Estado - Explicación Detallada

## El Estado: corazón de LangGraph

En LangGraph, el **estado** es la estructura central que fluye por todo el grafo. Es un diccionario tipado (`TypedDict`) que:

- Se pasa a cada nodo como argumento
- Cada nodo puede leer y modificar campos
- Los cambios se propagan al siguiente nodo

```python
from typing import TypedDict

class State(TypedDict):
    query: str
    resultado: str
    intentos: int
```

---

## TypedDict vs Annotated

### TypedDict simple (sobreescritura)

Por defecto, cuando un nodo retorna un campo, **sobreescribe** el valor anterior:

```python
class State(TypedDict):
    valor: str  # Cada nodo que retorne "valor" sobreescribe el anterior

# Nodo A retorna {"valor": "A"} → estado = {"valor": "A"}
# Nodo B retorna {"valor": "B"} → estado = {"valor": "B"}  ← sobreescrito
```

### Annotated con Reducers (acumulación)

Usando `Annotated`, puedes definir **cómo se combinan** los valores con un **reducer**:

```python
from typing import Annotated, TypedDict
from operator import add

class State(TypedDict):
    messages: Annotated[list[str], add]  # Cada retorno se ACUMULA con +
    counter: int                          # Este se sobreescribe normalmente
```

Con el reducer `add`:
```
# Nodo A retorna {"messages": ["Hola"]} → estado.messages = ["Hola"]
# Nodo B retorna {"messages": ["Mundo"]} → estado.messages = ["Hola", "Mundo"]  ← acumulado
```

---

## Reducers comunes

| Reducer | Import | Comportamiento |
|---|---|---|
| `add` | `from operator import add` | Concatena listas: `[a] + [b]` |
| `add_messages` | `from langgraph.graph import MessagesState` | Agrega mensajes; si comparten `id`, actualiza en vez de duplicar |
| Función custom | — | Cualquier lógica personalizada |

### Ejemplo: reducer personalizado

```python
def ultimo_no_vacio(existente: str, nuevo: str) -> str:
    """Solo actualiza si el nuevo valor no está vacío."""
    return nuevo if nuevo else existente

class State(TypedDict):
    respuesta: Annotated[str, ultimo_no_vacio]
```

---

## MessagesState: estado prebuilt para chatbots

LangGraph provee un estado especializado para aplicaciones de chat que usa el tipo `Messages` del ecosistema LangChain:

```python
from langgraph.graph import MessagesState

# Equivalente a:
# class State(TypedDict):
#     messages: Annotated[list[BaseMessage], add_messages]
```

`add_messages` es un reducer especial que:
- Agrega mensajes nuevos a la lista
- Si un mensaje tiene el mismo `id`, lo **actualiza** en lugar de duplicar

---

## Ejemplo 1: Estado con sobreescritura

```python
class State(TypedDict):
    texto: str
    paso_actual: str

def paso_a(state):
    return {"texto": state["texto"] + " → A", "paso_actual": "A"}

def paso_b(state):
    return {"texto": state["texto"] + " → B", "paso_actual": "B"}

# Después de paso_a: {"texto": "inicio → A", "paso_actual": "A"}
# Después de paso_b: {"texto": "inicio → A → B", "paso_actual": "B"}
```

> **Nota:** Aquí `texto` sigue usando sobreescritura (no hay reducer). La concatenación ocurre porque el nodo **lee manualmente** el valor previo con `state["texto"] + ...` y retorna el string completo. No es acumulación automática — el valor retornado reemplaza al anterior.

---

## Ejemplo 2: Estado con reducer (acumulación)

```python
from typing import Annotated, TypedDict
from operator import add

class State(TypedDict):
    log: Annotated[list[str], add]  # Se acumula
    resultado: str                   # Se sobreescribe

def paso_a(state):
    return {"log": ["Ejecutado paso A"], "resultado": "parcial"}

def paso_b(state):
    return {"log": ["Ejecutado paso B"], "resultado": "final"}

# Después de paso_a: log=["Ejecutado paso A"], resultado="parcial"
# Después de paso_b: log=["Ejecutado paso A", "Ejecutado paso B"], resultado="final"
```

---

## Ejemplo 3: MessagesState para chatbots

```python
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

def chatbot(state: MessagesState) -> dict:
    last_msg = state["messages"][-1]
    return {"messages": [AIMessage(content=f"Recibí: {last_msg.content}")]}

graph = StateGraph(MessagesState)
graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

app = graph.compile()
result = app.invoke({"messages": [HumanMessage(content="Hola")]})
```

---

## Estado inicial vs retorno parcial

Al invocar un grafo, provees el **estado inicial completo**:

```python
result = app.invoke({
    "query": "¿Qué es LangGraph?",
    "resultado": "",
    "intentos": 0
})
```

Los nodos retornan **diccionarios parciales** — solo los campos que quieren modificar:

```python
def mi_nodo(state):
    # Solo modifica "resultado", deja "query" e "intentos" sin tocar
    return {"resultado": "LangGraph es un framework de grafos"}
```

---

## Resumen

| Concepto | Qué hace | Cuándo usar |
|---|---|---|
| TypedDict simple | Sobreescribe valores | Campos que se reemplazan (contadores, flags) |
| Annotated + add | Acumula listas | Logs, historial de mensajes |
| Reducer custom | Lógica personalizada | Validaciones, merge condicional |
| MessagesState | Estado prebuilt para chat | Chatbots con historial de mensajes |
| Retorno parcial | Actualiza solo algunos campos | Siempre (es la norma en LangGraph) |
