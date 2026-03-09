# Nodos y Edges - Explicación Detallada

## Nodos: las funciones del grafo

Un **nodo** es una función Python que:
1. Recibe el **estado actual** como único argumento
2. Ejecuta lógica (puede ser pura o con side effects)
3. Retorna un **diccionario parcial** con los campos a actualizar

```python
def mi_nodo(state: State) -> dict:
    # Leer del estado
    input_text = state["input"]
    
    # Procesar
    resultado = input_text.upper()
    
    # Retornar solo lo que cambia
    return {"output": resultado}
```

---

## Tipos de nodos

### Nodo función regular

La forma más común. Una función simple:

```python
def procesar(state: State) -> dict:
    return {"resultado": "OK"}

graph.add_node("procesar", procesar)
```

### Nodo con LLM

Un nodo puede invocar un LLM:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

def llamar_llm(state: State) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

graph.add_node("llm", llamar_llm)
```

### Nodo lambda (inline)

Para lógica trivial puedes usar lambdas, aunque funciones con nombre son preferibles por legibilidad:

```python
graph.add_node("upper", lambda state: {"texto": state["texto"].upper()})
```

---

## Edges: conectando nodos

### Edge fijo (add_edge)

Conexión directa y determinista de un nodo a otro:

```python
graph.add_edge("nodo_a", "nodo_b")  # Siempre: A → B
```

### Constantes START y END

```python
from langgraph.graph import START, END

graph.add_edge(START, "primer_nodo")     # Punto de entrada al grafo
graph.add_edge("ultimo_nodo", END)       # Punto de salida del grafo
```

- `START` es un nodo virtual que marca el inicio
- `END` es un nodo virtual que marca la terminación

### Set entry point (alternativa a START)

```python
graph.set_entry_point("primer_nodo")     # Equivale a add_edge(START, "primer_nodo")
graph.set_finish_point("ultimo_nodo")    # Equivale a add_edge("ultimo_nodo", END)
```

---

## Patrones de flujo

### Lineal: A → B → C

```python
graph.add_edge(START, "A")
graph.add_edge("A", "B")
graph.add_edge("B", "C")
graph.add_edge("C", END)
```

```
START → A → B → C → END
```

### Fan-out: A → [B, C] (ejecución paralela)

Múltiples edges desde un nodo ejecutan los destinos en paralelo:

```python
graph.add_edge(START, "A")
graph.add_edge("A", "B")
graph.add_edge("A", "C")
graph.add_edge("B", "D")
graph.add_edge("C", "D")
graph.add_edge("D", END)
```

```
        ┌→ B ─┐
START → A     ├→ D → END
        └→ C ─┘
```

> **Nota**: Para fan-out necesitas un estado con reducers (Annotated) para que los resultados paralelos se combinen correctamente.

### Ciclo: A → B → A (loop)

LangGraph soporta ciclos, a diferencia de LCEL:

```python
graph.add_edge(START, "A")
graph.add_edge("A", "B")
# B decide si volver a A o ir a END usando conditional_edges
```

---

## Orden de ejecución

LangGraph ejecuta los nodos en **orden topológico**:
1. Parte desde START
2. Ejecuta los nodos respetando las dependencias (edges)
3. Si dos nodos no dependen entre sí, pueden ejecutarse en paralelo
4. Termina cuando llega a END

---

## Ejemplo: Grafo con LLM

```python
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatOpenAI(model="gpt-4o-mini")

class State(TypedDict):
    pregunta: str
    respuesta: str

def generar(state):
    msgs = [
        SystemMessage(content="Responde en una frase corta."),
        HumanMessage(content=state["pregunta"])
    ]
    response = llm.invoke(msgs)
    return {"respuesta": response.content}

def formatear(state):
    return {"respuesta": f"📝 {state['respuesta']}"}
```

---

## Resumen

| Concepto | Qué es | API |
|---|---|---|
| Nodo | Función que modifica estado | `graph.add_node("nombre", fn)` |
| Edge fijo | Conexión directa A → B | `graph.add_edge("a", "b")` |
| START | Punto de entrada virtual | `graph.add_edge(START, "nodo")` |
| END | Punto de salida virtual | `graph.add_edge("nodo", END)` |
| Fan-out | Ejecución paralela | Múltiples edges desde mismo nodo |
| Ciclo | Loop en el grafo | Edge de vuelta + condicional |
