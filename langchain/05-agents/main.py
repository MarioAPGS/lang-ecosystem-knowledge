"""
Agentes - Ejemplos ejecutables
===============================
Prerequisitos:
    pip install langchain-openai langgraph python-dotenv

Configuración:
    Crea un archivo .env en la raíz del proyecto con:
    OPENAI_API_KEY=sk-...
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ============================================================
# 1. Crear herramientas personalizadas con @tool
# ============================================================
print("=" * 60)
print("1. HERRAMIENTAS PERSONALIZADAS")
print("=" * 60)


@tool
def sumar(a: float, b: float) -> float:
    """Suma dos números."""
    return a + b


@tool
def multiplicar(a: float, b: float) -> float:
    """Multiplica dos números."""
    return a * b


@tool
def obtener_fecha_actual() -> str:
    """Obtiene la fecha y hora actual."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def buscar_en_base_datos(query: str) -> str:
    """Busca información en la base de datos de empleados de TechCorp.
    Útil para consultar datos de empleados, departamentos y proyectos."""
    # Simulamos una base de datos
    db = {
        "empleados": 50,
        "departamentos": ["Ingeniería", "Marketing", "RRHH", "Ventas"],
        "proyectos_activos": ["AppBuilder v3", "DataFlow Cloud", "CloudDash Pro"],
        "oficina": "Madrid, Calle Gran Vía 42",
        "ceo": "Ana García",
    }
    query_lower = query.lower()
    resultados = []
    for key, value in db.items():
        if any(word in key for word in query_lower.split()):
            resultados.append(f"{key}: {value}")
    return "\n".join(resultados) if resultados else "No se encontró información para esa consulta."


# Ver información de las herramientas
tools = [sumar, multiplicar, obtener_fecha_actual, buscar_en_base_datos]
for t in tools:
    print(f"  🔧 {t.name}: {t.description}")
# Ejemplo salida →
#   🔧 sumar: Suma dos números.
#   🔧 multiplicar: Multiplica dos números.
#   🔧 obtener_fecha_actual: Obtiene la fecha y hora actual.
#   🔧 buscar_en_base_datos: Busca información en la base de datos de empleados de TechCorp.
print()

# ============================================================
# 2. Tool Calling directo (sin agente)
# ============================================================
print("=" * 60)
print("2. TOOL CALLING DIRECTO (LLM decide qué herramienta usar)")
print("=" * 60)

# Vincular herramientas al LLM
llm_with_tools = llm.bind_tools([sumar, multiplicar])

# El LLM decide si necesita usar una herramienta
response = llm_with_tools.invoke("¿Cuánto es 25 * 13?")

print(f"Contenido: {response.content}")
# Ejemplo salida → Contenido:  (vacío, porque el LLM decide usar una herramienta en vez de responder)
print(f"Tool calls: {response.tool_calls}")
# Ejemplo salida → Tool calls: [{'name': 'multiplicar', 'args': {'a': 25.0, 'b': 13.0}, 'id': 'call_abc123'}]

if response.tool_calls:
    for tc in response.tool_calls:
        print(f"  Herramienta: {tc['name']}")
        # Ejemplo salida →   Herramienta: multiplicar
        print(f"  Argumentos: {tc['args']}")
        # Ejemplo salida →   Argumentos: {'a': 25.0, 'b': 13.0}

        # Ejecutar manualmente la herramienta
        if tc["name"] == "multiplicar":
            resultado = multiplicar.invoke(tc["args"])
            print(f"  Resultado: {resultado}")
            # Ejemplo salida →   Resultado: 325.0
print()

# Sin herramienta necesaria → responde directamente
response2 = llm_with_tools.invoke("¿Qué es Python?")
print(f"Sin tool call - Contenido: {response2.content[:100]}...")
# Ejemplo salida → Sin tool call - Contenido: Python es un lenguaje de programación interpretado de alto nivel...
print(f"Tool calls: {response2.tool_calls}")
# Ejemplo salida → Tool calls: []
print()

# ============================================================
# 3. Agente ReAct con LangGraph
# ============================================================
print("=" * 60)
print("3. AGENTE REACT CON LANGGRAPH")
print("=" * 60)

from langgraph.prebuilt import create_react_agent

# Crear agente con todas las herramientas
agent = create_react_agent(llm, tools)

# El agente razona y usa herramientas automáticamente
result = agent.invoke({
    "messages": [HumanMessage(content="¿Cuánto es (15 + 27) * 3? Hazlo paso a paso.")]
})

print("Mensajes del agente:")
for msg in result["messages"]:
    role = type(msg).__name__
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        print(f"  [{role}] Tool calls: {[tc['name'] for tc in msg.tool_calls]}")
    elif hasattr(msg, "name"):
        print(f"  [{role} - {msg.name}] {str(msg.content)[:100]}")
    else:
        print(f"  [{role}] {str(msg.content)[:150]}")
# Ejemplo salida →
#   [HumanMessage] ¿Cuánto es (15 + 27) * 3? Hazlo paso a paso.
#   [AIMessage] Tool calls: ['sumar']
#   [ToolMessage - sumar] 42.0
#   [AIMessage] Tool calls: ['multiplicar']
#   [ToolMessage - multiplicar] 126.0
#   [AIMessage] El resultado de (15 + 27) * 3 es 126.
print()

# ============================================================
# 4. Agente con herramientas de conocimiento
# ============================================================
print("=" * 60)
print("4. AGENTE CON HERRAMIENTAS DE CONOCIMIENTO")
print("=" * 60)

result = agent.invoke({
    "messages": [HumanMessage(
        content="¿Cuántos empleados tiene TechCorp y en qué proyectos están trabajando?"
    )]
})

# Mostrar solo la respuesta final
respuesta_final = result["messages"][-1].content
print(f"Respuesta: {respuesta_final}")
# Ejemplo salida → Respuesta: TechCorp tiene 50 empleados y están trabajando en los proyectos: AppBuilder v3, DataFlow Cloud y CloudDash Pro.
print()

# ============================================================
# 5. Agente con pregunta que requiere fecha
# ============================================================
print("=" * 60)
print("5. AGENTE CON FECHA ACTUAL")
print("=" * 60)

result = agent.invoke({
    "messages": [HumanMessage(content="¿Qué fecha y hora es ahora mismo?")]
})

respuesta_final = result["messages"][-1].content
print(f"Respuesta: {respuesta_final}")
# Ejemplo salida → Respuesta: La fecha y hora actual es 2026-03-05 14:32:17.
print()

# ============================================================
# 6. Agente conversacional (con historial)
# ============================================================
print("=" * 60)
print("6. AGENTE CONVERSACIONAL")
print("=" * 60)

# Primera interacción
result1 = agent.invoke({
    "messages": [HumanMessage(content="Suma 100 + 200")]
})
print(f"User: Suma 100 + 200")
print(f"Agent: {result1['messages'][-1].content}")
# Ejemplo salida → Agent: El resultado de 100 + 200 es 300.

# Segunda interacción (con historial)
result2 = agent.invoke({
    "messages": [
        *result1["messages"],  # Historial previo
        HumanMessage(content="Ahora multiplica ese resultado por 5"),
    ]
})
print(f"\nUser: Ahora multiplica ese resultado por 5")
print(f"Agent: {result2['messages'][-1].content}")
# Ejemplo salida → Agent: El resultado de 300 * 5 es 1500.
print()

# ============================================================
# 7. Agente con system prompt personalizado
# ============================================================
print("=" * 60)
print("7. AGENTE CON SYSTEM PROMPT")
print("=" * 60)

agent_custom = create_react_agent(
    llm,
    tools,
    prompt="Eres un asistente de TechCorp. Siempre responde en español y de forma amable. Usa las herramientas disponibles cuando sea necesario.",
)

result = agent_custom.invoke({
    "messages": [HumanMessage(content="Hola! ¿Quién es el CEO y dónde está la oficina?")]
})

print(f"Respuesta: {result['messages'][-1].content}")
# Ejemplo salida → Respuesta: ¡Hola! La CEO de TechCorp es Ana García y la oficina está ubicada en Madrid, Calle Gran Vía 42. ¿Puedo ayudarte en algo más?
