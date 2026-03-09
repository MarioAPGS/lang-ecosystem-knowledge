"""
LLMs y Chat Models - Ejemplos ejecutables
==========================================
Prerequisitos:
    pip install langchain-openai python-dotenv

Configuración:
    Crea un archivo .env en la raíz del proyecto con:
    OPENAI_API_KEY=sk-...
"""

import os
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# ============================================================
# 1. Inicialización básica
# ============================================================
print("=" * 60)
print("1. INICIALIZACIÓN BÁSICA")
print("=" * 60)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Invocación simple con un string
response = llm.invoke("¿Qué es Python en una frase?")
print(f"Respuesta: {response.content}")
# Ejemplo salida → Respuesta: Python es un lenguaje de programación interpretado, de alto nivel y propósito general.
print(f"Tipo: {type(response)}")
# Ejemplo salida → Tipo: <class 'langchain_core.messages.ai.AIMessage'>
print()

# ============================================================
# 2. Uso de mensajes tipados
# ============================================================
print("=" * 60)
print("2. MENSAJES TIPADOS")
print("=" * 60)

messages = [
    SystemMessage(content="Eres un experto en Python. Responde de forma breve y directa."),
    HumanMessage(content="¿Qué es una list comprehension?"),
]

response = llm.invoke(messages)
print(f"Respuesta: {response.content}")
# Ejemplo salida → Respuesta: Una list comprehension es una forma concisa de crear listas usando una expresión dentro de corchetes, como [x**2 for x in range(10)].
print()

# ============================================================
# 3. Metadata de la respuesta
# ============================================================
print("=" * 60)
print("3. METADATA DE LA RESPUESTA")
print("=" * 60)

response = llm.invoke("Di 'hola' y nada más")
print(f"Contenido: {response.content}")
# Ejemplo salida → Contenido: hola
print(f"Modelo usado: {response.response_metadata.get('model_name', 'N/A')}")
# Ejemplo salida → Modelo usado: gpt-4o-mini
print(f"Tokens input: {response.usage_metadata.get('input_tokens', 'N/A')}")
# Ejemplo salida → Tokens input: 14
print(f"Tokens output: {response.usage_metadata.get('output_tokens', 'N/A')}")
# Ejemplo salida → Tokens output: 2
print(f"Tokens total: {response.usage_metadata.get('total_tokens', 'N/A')}")
# Ejemplo salida → Tokens total: 16
print()

# ============================================================
# 4. Streaming - Respuesta token a token
# ============================================================
print("=" * 60)
print("4. STREAMING")
print("=" * 60)

print("Respuesta en streaming: ", end="")
for chunk in llm.stream("Escribe un haiku sobre programar"):
    print(chunk.content, end="", flush=True)
print("\n")
# Ejemplo salida → Respuesta en streaming: Teclas que susurran / lógica en cada línea / el código florece

# ============================================================
# 5. Batch - Procesamiento por lotes
# ============================================================
print("=" * 60)
print("5. BATCH (PROCESAMIENTO POR LOTES)")
print("=" * 60)

preguntas = [
    "¿Qué es una variable?",
    "¿Qué es una función?",
    "¿Qué es una clase?",
]

respuestas = llm.batch(preguntas)
for pregunta, respuesta in zip(preguntas, respuestas):
    print(f"P: {pregunta}")
    print(f"R: {respuesta.content[:100]}...")
    # Ejemplo salida →
    #   P: ¿Qué es una variable?
    #   R: Una variable es un espacio en memoria que almacena un valor y se identifica con un nombre...
    print()

# ============================================================
# 6. Comparación de temperaturas
# ============================================================
print("=" * 60)
print("6. COMPARACIÓN DE TEMPERATURAS")
print("=" * 60)

prompt = "Inventa un nombre para una tienda de café"

for temp in [0.0, 0.5, 1.0]:
    llm_temp = ChatOpenAI(model="gpt-4o-mini", temperature=temp)
    response = llm_temp.invoke(prompt)
    print(f"  Temp {temp}: {response.content}")
# Ejemplo salida →
#   Temp 0.0: Café del Alma
#   Temp 0.5: Aroma & Letras
#   Temp 1.0: El Rincón del Grano Soñador
print()

# ============================================================
# 7. Parámetros adicionales
# ============================================================
print("=" * 60)
print("7. PARÁMETROS ADICIONALES")
print("=" * 60)

llm_custom = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    max_tokens=50,  # Limitar longitud de respuesta
)

response = llm_custom.invoke("Explica qué es la recursión en programación")
print(f"Respuesta (max 50 tokens): {response.content}")
# Ejemplo salida → Respuesta (max 50 tokens): La recursión es cuando una función se llama a sí misma para resolver un problema dividiéndolo en sub
print(f"Tokens usados: {response.usage_metadata.get('output_tokens', 'N/A')}")
# Ejemplo salida → Tokens usados: 50
