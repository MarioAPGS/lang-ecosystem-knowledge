# LangGraph - Guía de Iniciación

## ¿Qué es LangGraph?

LangGraph es un **framework para construir aplicaciones con estado usando grafos dirigidos**. Forma parte del ecosistema LangChain y está diseñado para crear workflows complejos donde los pasos se modelan como **nodos** y las transiciones como **aristas (edges)**.

> **En resumen:** LangGraph te permite construir flujos de trabajo (workflows) donde cada paso es un nodo, y el flujo entre ellos puede ser lineal, condicional o cíclico — ideal para agentes, chatbots y pipelines multi-paso.

---

## ¿Por qué LangGraph y no solo Chains?

| Chains (LCEL) | LangGraph |
|---|---|
| Flujo lineal: A → B → C | Flujo como grafo: puede tener ciclos, condicionales |
| Sin estado persistente | Estado compartido entre todos los nodos |
| Ideal para pipelines simples | Ideal para agentes, workflows complejos |
| No soporta "human-in-the-loop" | Soporta interrupciones y aprobación humana |
| Sin checkpointing | Persistence y checkpoints nativos |

---

## Arquitectura de un Grafo LangGraph

```
                    ┌──────────────┐
                    │   __start__  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │   Nodo A     │
                    │ (función)    │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐     ¿condición?
                    │  Router      │─── True ──► Nodo B
                    │ (condicional)│
                    └──────┬───────┘
                           │ False
                    ┌──────▼───────┐
                    │   Nodo C     │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │   __end__    │
                    └──────────────┘
```

### Conceptos clave:
- **State**: Un diccionario tipado compartido por todos los nodos
- **Nodo**: Una función que recibe el estado, lo modifica y lo devuelve
- **Edge**: Conexión entre nodos (puede ser fija o condicional)
- **StateGraph**: La clase principal para construir grafos
- **Compilación**: Un grafo se compila en un `CompiledGraph` ejecutable

---

## Instalación

```bash
# LangGraph
pip install langgraph

# LLM (para ejemplos con modelos)
pip install langchain-openai

# Utilidades
pip install python-dotenv
```

---

## Conceptos Clave - Lecciones

Cada concepto tiene su **carpeta dedicada** con explicación detallada (`code-explained.md`) y código ejecutable (`main.py`):

| # | Concepto | Carpeta | Descripción |
|---|---|---|---|
| 1 | [Conceptos Fundamentales](01-conceptos-fundamentales/) | `01-conceptos-fundamentales/` | Qué es un grafo, State, nodos y edges básicos |
| 2 | [StateGraph y Estado](02-state-graph/) | `02-state-graph/` | Definir estado tipado, Annotated, reducers |
| 3 | [Nodos y Edges](03-nodes-edges/) | `03-nodes-edges/` | Crear nodos, conectar edges, flujos lineales |
| 4 | [Conditional Edges](04-conditional-edges/) | `04-conditional-edges/` | Routing condicional, branching dinámico |
| 5 | [ReAct Agent](05-react-agent/) | `05-react-agent/` | Agente prebuilt con herramientas |
| 6 | [Human-in-the-Loop](06-human-in-the-loop/) | `06-human-in-the-loop/` | Interrupciones y aprobación humana |
| 7 | [Persistence y Checkpoints](07-persistence-checkpoints/) | `07-persistence-checkpoints/` | Estado persistente, threads, recuperación |

---

### 1. Conceptos Fundamentales

LangGraph modela todo como un **grafo dirigido** con estado:

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# 1. Definir el estado
class State(TypedDict):
    mensaje: str

# 2. Crear el grafo
graph = StateGraph(State)

# 3. Definir un nodo (función que modifica estado)
def saludar(state: State) -> dict:
    return {"mensaje": f"¡Hola! Recibí: {state['mensaje']}"}

# 4. Agregar nodo y edges
graph.add_node("saludar", saludar)
graph.add_edge(START, "saludar")
graph.add_edge("saludar", END)

# 5. Compilar y ejecutar
app = graph.compile()
result = app.invoke({"mensaje": "Mundo"})
print(result)  # {'mensaje': '¡Hola! Recibí: Mundo'}
```

### 2. StateGraph y Estado

El estado es un `TypedDict` que se comparte entre todos los nodos. Puedes usar `Annotated` con **reducers** para controlar cómo se acumulan los valores:

```python
from typing import Annotated, TypedDict
from operator import add

class State(TypedDict):
    messages: Annotated[list[str], add]  # Se acumulan con +
    counter: int                          # Se sobreescribe
```

### 3. Nodos y Edges

Los nodos son funciones puras. Los edges definen el flujo:

```python
graph.add_node("paso_1", funcion_paso_1)
graph.add_node("paso_2", funcion_paso_2)

graph.add_edge(START, "paso_1")
graph.add_edge("paso_1", "paso_2")
graph.add_edge("paso_2", END)
```

### 4. Conditional Edges

Permiten tomar caminos diferentes según el estado:

```python
def decidir_ruta(state: State) -> str:
    if state["score"] > 0.8:
        return "aprobar"
    return "revisar"

graph.add_conditional_edges("evaluar", decidir_ruta)
```

### 5. ReAct Agent

LangGraph provee un agente prebuilt que sigue el patrón **ReAct** (Reasoning + Acting):

```python
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(llm, tools=[mi_herramienta])
result = agent.invoke({"messages": [("human", "Haz algo")]})
```

### 6. Human-in-the-Loop

Puedes interrumpir la ejecución para pedir aprobación humana:

```python
app = graph.compile(
    checkpointer=memory,
    interrupt_before=["accion_critica"]
)
```

### 7. Persistence y Checkpoints

Con `MemorySaver`, el grafo guarda su estado y puede retomarse:

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# Cada thread_id tiene su propio historial
config = {"configurable": {"thread_id": "sesion-1"}}
```

---

## Flujo Típico de una Aplicación LangGraph

```
  1. Definir State (TypedDict)
  2. Crear StateGraph(State)
  3. Definir funciones (nodos)
  4. Agregar nodos al grafo
  5. Conectar edges (fijos o condicionales)
  6. Compilar con graph.compile()
  7. Ejecutar con app.invoke(estado_inicial)
```

---

## Próximos Pasos Sugeridos

1. **Ejecutar el primer grafo** con un nodo simple (Lección 1)
2. **Experimentar con estado** usando reducers y Annotated (Lección 2)
3. **Crear flujos multi-nodo** con edges lineales (Lección 3)
4. **Implementar branching** con conditional edges (Lección 4)
5. **Construir un agente ReAct** con herramientas (Lección 5)
6. **Agregar supervisión humana** con human-in-the-loop (Lección 6)
7. **Persistir conversaciones** con checkpoints y threads (Lección 7)

---

> **Tip:** LangGraph es más potente que las cadenas LCEL cuando necesitas ciclos, estado o aprobación humana. Para pipelines lineales simples, LCEL sigue siendo la opción más sencilla.
