# Agentes - Explicación Detallada

## ¿Qué es un Agente?

Un **agente** es un sistema donde el LLM actúa como "cerebro" que **decide qué acciones tomar** para resolver una tarea. A diferencia de una cadena (donde los pasos son fijos), un agente puede:

1. **Razonar** sobre qué hacer a continuación
2. **Usar herramientas** (buscar en internet, ejecutar código, consultar APIs…)
3. **Iterar** hasta encontrar la respuesta correcta

```
                    ┌─────────┐
                    │  Input  │
                    └────┬────┘
                         │
                    ┌────▼────┐
              ┌────▶│   LLM   │◄────┐
              │     │ (piensa) │     │
              │     └────┬────┘     │
              │          │          │
              │   ¿Necesita tool?   │
              │     /         \     │
              │   Sí           No   │
              │   │             │   │
              │ ┌─▼──────┐     │   │
              │ │  Tool   │     │   │
              │ │(ejecuta)│     │   │
              │ └─┬──────┘     │   │
              │   │             │   │
              └───┘       ┌────▼───┘
                          │ Respuesta
                          │  final
                          ▼
```

---

## Componentes de un Agente

### Herramientas (Tools)
Funciones que el agente puede ejecutar. Cada herramienta tiene:
- **name**: Nombre identificativo
- **description**: Qué hace (el LLM lee esto para decidir cuándo usarla)
- **function**: La función Python que ejecuta

### Tipos de herramientas
| Tipo | Ejemplo |
|---|---|
| Búsqueda web | DuckDuckGo, Google Search, Tavily |
| Cálculo | Python REPL, calculadora |
| Conocimiento | Wikipedia, Arxiv |
| APIs | Herramientas custom para tu API |
| Archivos | Leer/escribir archivos |

### ReAct Pattern
El patrón más común para agentes: **Reason + Act**
1. El LLM **razona** (piensa qué hacer)
2. **Actúa** (ejecuta una herramienta)
3. **Observa** el resultado
4. Repite hasta tener la respuesta

---

## Crear herramientas personalizadas

### Con el decorador `@tool`
```python
from langchain_core.tools import tool

@tool
def multiplicar(a: int, b: int) -> int:
    """Multiplica dos números."""
    return a * b
```

### Con `StructuredTool`
```python
from langchain_core.tools import StructuredTool

def buscar_usuario(nombre: str, edad: int) -> str:
    """Busca un usuario por nombre y edad."""
    return f"Usuario {nombre}, {edad} años encontrado"

tool = StructuredTool.from_function(buscar_usuario)
```

---

## LangGraph para Agentes

**LangGraph** es la forma recomendada de construir agentes en LangChain. Proporciona:
- Control de flujo con grafos
- Estado persistente
- Soporte para múltiples agentes
- Puntos de control (checkpoints)

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(llm, tools)
result = agent.invoke({"messages": [("human", "mi pregunta")]})
```

---

## Código de ejemplo

Revisa `main.py` en esta carpeta para ver ejemplos ejecutables de:
1. Crear herramientas personalizadas con `@tool`
2. Tool calling directo del LLM (sin agente)
3. Agente ReAct con LangGraph
4. Agente con múltiples herramientas
5. Agente conversacional con historial
