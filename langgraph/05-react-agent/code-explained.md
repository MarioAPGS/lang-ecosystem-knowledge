# ReAct Agent - Explicación Detallada

## ¿Qué es un Agente ReAct?

**ReAct** (Reasoning + Acting) es un patrón donde el LLM:
1. **Razona** sobre qué hacer (Thought)
2. **Actúa** ejecutando una herramienta (Action)
3. **Observa** el resultado (Observation)
4. **Repite** hasta tener la respuesta final

```
┌─────────────────────────────────────────────┐
│              Ciclo ReAct                     │
│                                              │
│  Pregunta → Razonar → ¿Usar herramienta?   │
│                              │               │
│                     Sí       │    No         │
│                     ↓        │    ↓          │
│              Ejecutar tool   │  Respuesta    │
│                     ↓        │    final      │
│              Observar        │               │
│              resultado       │               │
│                     ↓        │               │
│              Volver a ───────┘               │
│              razonar                         │
└─────────────────────────────────────────────┘
```

---

## `create_agent`: el agente prebuilt

LangChain provee un agente ReAct listo para usar:

```python
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_agent(llm, tools=[herramienta1, herramienta2])
```

Internamente, `create_agent` crea un grafo con:
- Un nodo **"agent"** que invoca al LLM
- Un nodo **"tools"** que ejecuta las herramientas
- Conditional edges que deciden si usar herramientas o terminar

---

## Herramientas (Tools)

### Crear herramientas con `@tool`

```python
from langchain_core.tools import tool

@tool
def calcular(operacion: str) -> str:
    """Ejecuta una operación matemática simple."""
    try:
        return str(eval(operacion))
    except:
        return "Error en la operación"
```

> **Importante**: El **docstring** es crucial. El LLM lo usa para decidir cuándo y cómo usar la herramienta.

### Parámetros de herramientas

El LLM infiere los parámetros del type hint y el docstring:

```python
@tool
def buscar_clima(ciudad: str, unidad: str = "celsius") -> str:
    """Busca el clima actual de una ciudad.
    
    Args:
        ciudad: Nombre de la ciudad
        unidad: Sistema de unidades (celsius o fahrenheit)
    """
    return f"El clima en {ciudad} es 22°{unidad[0].upper()}"
```

---

## Invocando el agente

```python
result = agent.invoke({
    "messages": [("human", "¿Cuánto es 25 * 17?")]
})

# El resultado contiene todo el historial de mensajes
for msg in result["messages"]:
    print(msg.content)
```

### Con system prompt

```python
agent = create_agent(
    llm,
    tools=[herramienta],
    system_prompt="Eres un asistente matemático. Solo respondes sobre números."
)
```

---

## Streaming del agente

Para ver el razonamiento paso a paso:

```python
for step in agent.stream({
    "messages": [("human", "¿Cuál es la raíz cuadrada de 144?")]
}):
    print(step)
```

Cada `step` muestra el estado después de cada nodo (agent → tools → agent → ...).

---

## Herramientas comunes del ecosistema

| Herramienta | Paquete | Descripción |
|---|---|---|
| DuckDuckGoSearchRun | langchain-community | Búsqueda web |
| WikipediaQueryRun | langchain-community | Consultas a Wikipedia |
| PythonREPL | langchain-community | Ejecución de código Python |
| HumanTool | langchain-community | Pedir input al humano |

---

## Agent vs Chain: cuándo usar cada uno

| Escenario | Usar |
|---|---|
| Flujo predecible: prompt → LLM → output | Chain (LCEL) |
| LLM decide qué herramientas usar | Agent |
| Múltiples herramientas opcionales | Agent |
| Pipeline fijo de procesamiento | Chain |
| Iteración hasta conseguir resultado | Agent |

---

## Resumen

| Concepto | Qué es | API |
|---|---|---|
| ReAct | Patrón Reasoning + Acting | Ciclo: razonar → actuar → observar |
| `create_agent` | Agente prebuilt | `create_agent(llm, tools)` |
| `@tool` | Decorador para crear herramientas | `from langchain_core.tools import tool` |
| System prompt | Instrucciones del agente | Parámetro `system_prompt` |
| Streaming | Ver cada paso del agente | `agent.stream({"messages": [...]})` |
