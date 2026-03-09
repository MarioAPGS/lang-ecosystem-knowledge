# Conceptos Fundamentales de LangGraph - Explicación Detallada

## ¿Qué es un grafo?

Un **grafo dirigido** es una estructura compuesta por:
- **Nodos**: Puntos que ejecutan lógica (funciones)
- **Aristas (Edges)**: Conexiones que definen el flujo entre nodos
- **Dirección**: El flujo va en un sentido específico (de A a B, no viceversa automáticamente)

LangGraph usa grafos dirigidos para modelar workflows donde cada paso es un nodo y las transiciones entre pasos son edges.

---

## ¿Qué diferencia a LangGraph de LCEL?

| Característica | LCEL (Chains) | LangGraph |
|---|---|---|
| Estructura | Pipeline lineal | Grafo dirigido |
| Ciclos | No soportados | Soportados |
| Estado | Pasa de un paso al siguiente | Estado global compartido |
| Condicionales | Limitado (RunnableBranch) | Conditional edges nativos |
| Persistencia | No nativo | Checkpoints nativos |
| Interrupción | No | Human-in-the-loop |

---

## Los 5 pilares de LangGraph

### 1. State (Estado)

El estado es un **diccionario tipado** (`TypedDict`) que se comparte entre todos los nodos del grafo. Es la "memoria de trabajo" del workflow.

```python
from typing import TypedDict

class State(TypedDict):
    input: str
    resultado: str
    pasos: int
```

Cada nodo puede **leer y modificar** el estado. Los cambios se propagan al siguiente nodo.

### 2. StateGraph

Es la clase principal para construir grafos. Recibe el tipo de estado como parámetro:

```python
from langgraph.graph import StateGraph

graph = StateGraph(State)
```

### 3. Nodos (Nodes)

Un nodo es una **función** que:
- Recibe el estado actual como argumento
- Retorna un **diccionario parcial** con los campos a actualizar

```python
def mi_nodo(state: State) -> dict:
    return {"resultado": "procesado", "pasos": state["pasos"] + 1}
```

> **Importante**: No necesitas retornar TODO el estado, solo los campos que quieres cambiar.

### 4. Edges (Aristas)

Conectan nodos entre sí. Hay dos tipos principales:
- **Edge fijo**: Siempre va de A a B
- **Conditional edge**: Decide el destino según el estado

```python
graph.add_edge("nodo_a", "nodo_b")  # Fijo: A → B siempre
```

### 5. START y END

Constantes especiales que marcan el inicio y fin del grafo:

```python
from langgraph.graph import START, END

graph.add_edge(START, "primer_nodo")    # Punto de entrada
graph.add_edge("ultimo_nodo", END)      # Punto de salida
```

---

## Ciclo de vida de un grafo

```
 1. Definir State         →  TypedDict con los campos necesarios
 2. Crear StateGraph      →  StateGraph(State)
 3. Agregar nodos         →  graph.add_node("nombre", función)
 4. Conectar edges        →  graph.add_edge(origen, destino)
 5. Compilar              →  app = graph.compile()
 6. Ejecutar              →  result = app.invoke(estado_inicial)
```

---

## Ejemplo 1: Grafo mínimo (un solo nodo)

El grafo más simple posible: un nodo que modifica el estado.

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    mensaje: str

def procesar(state: State) -> dict:
    return {"mensaje": f"Procesado: {state['mensaje']}"}

graph = StateGraph(State)
graph.add_node("procesar", procesar)
graph.add_edge(START, "procesar")
graph.add_edge("procesar", END)

app = graph.compile()
result = app.invoke({"mensaje": "Hola LangGraph"})
# result = {'mensaje': 'Procesado: Hola LangGraph'}
```

---

## Ejemplo 2: Grafo de dos nodos (flujo lineal)

Dos nodos que procesan secuencialmente:

```python
def paso_1(state: State) -> dict:
    return {"mensaje": state["mensaje"].upper()}

def paso_2(state: State) -> dict:
    return {"mensaje": f"✅ {state['mensaje']}"}

graph = StateGraph(State)
graph.add_node("paso_1", paso_1)
graph.add_node("paso_2", paso_2)

graph.add_edge(START, "paso_1")
graph.add_edge("paso_1", "paso_2")
graph.add_edge("paso_2", END)

app = graph.compile()
result = app.invoke({"mensaje": "hola mundo"})
# result = {'mensaje': '✅ HOLA MUNDO'}
```

---

## Ejemplo 3: Estado con múltiples campos

El estado puede tener tantos campos como necesites:

```python
class State(TypedDict):
    texto: str
    longitud: int
    procesado: bool

def analizar(state: State) -> dict:
    return {
        "longitud": len(state["texto"]),
        "procesado": True
    }
```

---

## Visualización del grafo

LangGraph permite generar una representación visual del grafo compilado:

```python
app = graph.compile()

# Como ASCII
print(app.get_graph().draw_ascii())

# Como Mermaid (para renderizar en Markdown/notebooks)
print(app.get_graph().draw_mermaid())
```

---

## Resumen

| Concepto | Qué es | Ejemplo |
|---|---|---|
| State | Diccionario tipado compartido | `class State(TypedDict): ...` |
| StateGraph | Constructor del grafo | `StateGraph(State)` |
| Nodo | Función que modifica estado | `def mi_nodo(state) -> dict:` |
| Edge | Conexión entre nodos | `graph.add_edge("a", "b")` |
| START/END | Inicio y fin del grafo | `graph.add_edge(START, "nodo")` |
| Compilación | Crear grafo ejecutable | `app = graph.compile()` |
| Invocación | Ejecutar el grafo | `app.invoke({"campo": "valor"})` |
