"""
ReAct Agent - Ejemplos ejecutables
=====================================
Prerequisitos:
    pip install langgraph langchain-openai python-dotenv

Configuración:
    Crea un archivo .env en la raíz del proyecto con:
    OPENAI_API_KEY=sk-...
"""

import os
import math
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ============================================================
# 1. Herramienta simple con @tool
# ============================================================
print("=" * 60)
print("1. HERRAMIENTA SIMPLE CON @tool")
print("=" * 60)


@tool
def sumar(a: int, b: int) -> int:
    """Suma dos números enteros."""
    return a + b


@tool
def multiplicar(a: int, b: int) -> int:
    """Multiplica dos números enteros."""
    return a * b


# Probar herramientas directamente
print(f"sumar(3, 5) = {sumar.invoke({'a': 3, 'b': 5})}")
# Ejemplo salida → sumar(3, 5) = 8
print(f"multiplicar(4, 7) = {multiplicar.invoke({'a': 4, 'b': 7})}")
# Ejemplo salida → multiplicar(4, 7) = 28
print(f"Schema de 'sumar': {sumar.args_schema.model_json_schema()}")
# Ejemplo salida → Schema de 'sumar': {'description': 'Suma dos números enteros.', 'properties': {'a': {'title': 'A', 'type': 'integer'}, 'b': {'title': 'B', 'type': 'integer'}}, ...}
print()


# ============================================================
# 2. ReAct Agent básico
# ============================================================
print("=" * 60)
print("2. REACT AGENT BÁSICO")
print("=" * 60)

agent1 = create_react_agent(llm, tools=[sumar, multiplicar])

result1 = agent1.invoke({
    "messages": [("human", "¿Cuánto es 15 + 27?")]
})

# Mostrar la respuesta final
print(f"Respuesta: {result1['messages'][-1].content}")
# Ejemplo salida → Respuesta: 15 + 27 es igual a 42.
print()


# ============================================================
# 3. Agent con múltiples herramientas
# ============================================================
print("=" * 60)
print("3. AGENT CON MÚLTIPLES HERRAMIENTAS")
print("=" * 60)


@tool
def raiz_cuadrada(numero: float) -> float:
    """Calcula la raíz cuadrada de un número."""
    return math.sqrt(numero)


@tool
def potencia(base: float, exponente: float) -> float:
    """Calcula la potencia: base elevada a exponente."""
    return base ** exponente


agent_math = create_react_agent(
    llm,
    tools=[sumar, multiplicar, raiz_cuadrada, potencia]
)

result2 = agent_math.invoke({
    "messages": [("human", "Calcula la raíz cuadrada de 144 y luego multiplícala por 5")]
})
print(f"Respuesta: {result2['messages'][-1].content}")
# Ejemplo salida → Respuesta: La raíz cuadrada de 144 es 12, y al multiplicarla por 5, el resultado es 60.
print()


# ============================================================
# 4. Agent con system prompt
# ============================================================
print("=" * 60)
print("4. AGENT CON SYSTEM PROMPT")
print("=" * 60)


@tool
def obtener_fecha() -> str:
    """Obtiene la fecha y hora actual."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def calcular_edad(anio_nacimiento: int) -> int:
    """Calcula la edad aproximada dado el año de nacimiento."""
    return datetime.now().year - anio_nacimiento


agent_personal = create_react_agent(
    llm,
    tools=[obtener_fecha, calcular_edad],
    prompt="Eres un asistente personal amable. Siempre respondes en español y de forma concisa."
)

result3 = agent_personal.invoke({
    "messages": [("human", "¿Qué fecha es hoy y qué edad tendría alguien nacido en 1995?")]
})
print(f"Respuesta: {result3['messages'][-1].content}")
# Ejemplo salida → Respuesta: Hoy es 2026-03-05. Alguien nacido en 1995 tendría aproximadamente 31 años.
print()


# ============================================================
# 5. Streaming del agente (ver pasos intermedios)
# ============================================================
print("=" * 60)
print("5. STREAMING - VER PASOS DEL AGENTE")
print("=" * 60)

print("Pasos del agente:")
for step in agent_math.stream({
    "messages": [("human", "¿Cuánto es 8 elevado a 3?")]
}):
    for node_name, node_data in step.items():
        if node_name == "__end__":
            continue
        last_msg = node_data["messages"][-1]
        msg_type = type(last_msg).__name__
        content_preview = str(last_msg.content)[:100] if last_msg.content else "(tool call)"
        print(f"  [{node_name}] {msg_type}: {content_preview}")
# Ejemplo salida →   [agent] AIMessage: (tool call)
# Ejemplo salida →   [tools] ToolMessage: 512.0
# Ejemplo salida →   [agent] AIMessage: 8 elevado a 3 es igual a 512.
print()


# ============================================================
# 6. Herramienta de conocimiento (lookup)
# ============================================================
print("=" * 60)
print("6. HERRAMIENTA DE CONOCIMIENTO")
print("=" * 60)

DATOS_PAISES = {
    "españa": {"capital": "Madrid", "poblacion": "47M", "idioma": "Español"},
    "mexico": {"capital": "Ciudad de México", "poblacion": "128M", "idioma": "Español"},
    "japon": {"capital": "Tokio", "poblacion": "125M", "idioma": "Japonés"},
    "brasil": {"capital": "Brasilia", "poblacion": "214M", "idioma": "Portugués"},
}


@tool
def info_pais(pais: str) -> str:
    """Obtiene información sobre un país (capital, población, idioma).
    
    Args:
        pais: Nombre del país en minúsculas y sin tildes
    """
    datos = DATOS_PAISES.get(pais.lower())
    if datos:
        return f"Capital: {datos['capital']}, Población: {datos['poblacion']}, Idioma: {datos['idioma']}"
    return f"No tengo información sobre '{pais}'"


agent_geo = create_react_agent(llm, tools=[info_pais])

result4 = agent_geo.invoke({
    "messages": [("human", "¿Cuál es la capital de Japón y qué idioma hablan?")]
})
print(f"Respuesta: {result4['messages'][-1].content}")
# Ejemplo salida → Respuesta: La capital de Japón es Tokio y el idioma que hablan es japonés.
print()


# ============================================================
# 7. Agent que decide NO usar herramientas
# ============================================================
print("=" * 60)
print("7. AGENT QUE DECIDE NO USAR HERRAMIENTAS")
print("=" * 60)

# Si el LLM puede responder sin herramientas, no las usa
result5 = agent_math.invoke({
    "messages": [("human", "¿Qué es una raíz cuadrada en matemáticas?")]
})
print(f"Respuesta: {result5['messages'][-1].content}")
# Ejemplo salida → Respuesta: Una raíz cuadrada de un número es un valor que, al ser multiplicado por sí mismo, da como resultado ese número.

# Contamos cuántos mensajes hubo (menos = no usó herramientas)
num_msgs = len(result5["messages"])
print(f"Mensajes totales: {num_msgs} (2 = sin herramienta, >2 = usó herramienta)")
# Ejemplo salida → Mensajes totales: 2 (2 = sin herramienta, >2 = usó herramienta)
print()

print("=" * 60)
print("✅ Todos los ejemplos de ReAct Agent ejecutados")
print("=" * 60)
