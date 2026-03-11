"""
Prompts Hub en LangSmith - Ejemplos ejecutables
=================================================
Prerequisitos:
    pip install langsmith langchain-openai python-dotenv

Configuración:
    Crea un archivo .env en la raíz del proyecto con:
    LANGSMITH_TRACING=true
    LANGSMITH_API_KEY=lsv2_pt_...
    LANGSMITH_PROJECT=langsmith-tutorial
    OPENAI_API_KEY=sk-...
"""

import os
from dotenv import load_dotenv

load_dotenv()

from langsmith import Client
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

client = Client()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = StrOutputParser()

# ============================================================
# 1. Crear y subir un prompt al Hub
# ============================================================
print("=" * 60)
print("1. CREAR Y SUBIR UN PROMPT AL HUB")
print("=" * 60)

prompt_asistente = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un asistente experto en {tema}. "
     "Responde de forma {estilo}. "
     "Si no sabes algo, di 'No tengo esa información'."),
    ("human", "{pregunta}")
])

prompt_name = "tutorial-asistente"

try:
    client.push_prompt(
        prompt_name,
        object=prompt_asistente,
        description="Prompt de asistente con tema y estilo configurables",
        is_public=False,
    )
    print(f"Prompt '{prompt_name}' subido al Hub ✅")
except Exception as e:
    print(f"Nota: {e}")
    print("Si el prompt ya existe, se actualiza con una nueva versión")
# Ejemplo salida → Prompt 'tutorial-asistente' subido al Hub ✅
print()

# ============================================================
# 2. Descargar y usar un prompt del Hub
# ============================================================
print("=" * 60)
print("2. DESCARGAR Y USAR UN PROMPT DEL HUB")
print("=" * 60)

try:
    prompt_descargado = client.pull_prompt(prompt_name)
    print(f"Prompt descargado: {type(prompt_descargado).__name__}")
    # Ejemplo salida → Prompt descargado: ChatPromptTemplate

    # Usar en una cadena LCEL
    chain = prompt_descargado | llm | parser

    resultado = chain.invoke({
        "tema": "Python",
        "estilo": "breve y con ejemplos",
        "pregunta": "¿Qué es una list comprehension?"
    })
    print(f"Resultado: {resultado}")
    # Ejemplo salida → Resultado: Una list comprehension es una forma concisa de crear listas: [x**2 for x in range(5)] → [0, 1, 4, 9, 16]
except Exception as e:
    print(f"Error al descargar prompt: {e}")
print()

# ============================================================
# 3. Actualizar un prompt (nueva versión)
# ============================================================
print("=" * 60)
print("3. ACTUALIZAR UN PROMPT (NUEVA VERSIÓN)")
print("=" * 60)

prompt_v2 = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un asistente experto en {tema}. "
     "Responde de forma {estilo}. "
     "Incluye siempre un ejemplo práctico. "
     "Si no sabes algo, di 'No tengo esa información'."),
    ("human", "{pregunta}")
])

try:
    client.push_prompt(
        prompt_name,
        object=prompt_v2,
        description="v2: Ahora incluye siempre un ejemplo práctico",
    )
    print(f"Prompt '{prompt_name}' actualizado a v2 ✅")
    # Ejemplo salida → Prompt 'tutorial-asistente' actualizado a v2 ✅
    print("→ En LangSmith verás el historial de versiones")
except Exception as e:
    print(f"Error: {e}")
print()

# ============================================================
# 4. Crear un prompt más complejo
# ============================================================
print("=" * 60)
print("4. PROMPT COMPLEJO CON CONTEXTO")
print("=" * 60)

prompt_rag = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un asistente que responde preguntas basándose ÚNICAMENTE "
     "en el contexto proporcionado. Si la respuesta no está en el "
     "contexto, di 'No encontré esa información en los documentos'."),
    ("human",
     "Contexto:\n{contexto}\n\n"
     "Pregunta: {pregunta}\n\n"
     "Respuesta:")
])

rag_prompt_name = "tutorial-rag-prompt"

try:
    client.push_prompt(
        rag_prompt_name,
        object=prompt_rag,
        description="Prompt para RAG - responde basándose en contexto",
        is_public=False,
    )
    print(f"Prompt RAG '{rag_prompt_name}' subido ✅")

    # Usar el prompt RAG
    chain_rag = prompt_rag | llm | parser

    resultado = chain_rag.invoke({
        "contexto": "Python fue creado por Guido van Rossum en 1991. "
                    "Es un lenguaje interpretado de propósito general. "
                    "La versión 3.0 se lanzó en 2008.",
        "pregunta": "¿Quién creó Python y en qué año?"
    })
    print(f"Resultado RAG: {resultado}")
    # Ejemplo salida → Resultado RAG: Python fue creado por Guido van Rossum en 1991.
except Exception as e:
    print(f"Error: {e}")
print()

# ============================================================
# 5. Usar prompt descargado en cadena completa
# ============================================================
print("=" * 60)
print("5. PROMPT DEL HUB EN CADENA COMPLETA")
print("=" * 60)

try:
    # Descargar prompt y construir cadena
    prompt_hub = client.pull_prompt(prompt_name)
    chain_completa = prompt_hub | llm | parser

    # Ejecutar múltiples preguntas
    preguntas = [
        {"tema": "JavaScript", "estilo": "breve", "pregunta": "¿Qué es async/await?"},
        {"tema": "SQL", "estilo": "técnica", "pregunta": "¿Qué es un JOIN?"},
        {"tema": "Git", "estilo": "simple", "pregunta": "¿Qué es un branch?"},
    ]

    for q in preguntas:
        resultado = chain_completa.invoke(q)
        print(f"[{q['tema']}] {q['pregunta']}")
        print(f"  → {resultado[:100]}...")
        print()
except Exception as e:
    print(f"Error: {e}")
print()

# ============================================================
# 6. Listar prompts existentes
# ============================================================
print("=" * 60)
print("6. LISTAR PROMPTS EN EL HUB")
print("=" * 60)

try:
    prompts = list(client.list_prompts())
    print(f"Prompts en tu Hub: {len(prompts.repos)}")
    for p in prompts.repos[:10]:
        print(f"  - {p.repo_handle}: {p.description or 'Sin descripción'}")
except Exception as e:
    print(f"Error al listar: {e}")
print()

# ============================================================
# 7. Limpiar prompts de tutorial
# ============================================================
print("=" * 60)
print("7. LIMPIAR PROMPTS DE TUTORIAL")
print("=" * 60)

# Descomenta para eliminar los prompts creados
# try:
#     client.delete_prompt(prompt_name)
#     print(f"Prompt '{prompt_name}' eliminado")
#     client.delete_prompt(rag_prompt_name)
#     print(f"Prompt '{rag_prompt_name}' eliminado")
# except Exception as e:
#     print(f"Error: {e}")

print("Prompts conservados para revisión en la UI")
print("→ Ve a smith.langchain.com → Hub para gestionarlos")
print()

print("=" * 60)
print("✅ PROMPTS HUB COMPLETADO")
print("=" * 60)
print("Conceptos clave aprendidos:")
print("  - push_prompt() para subir prompts")
print("  - pull_prompt() para descargar prompts")
print("  - Versionado automático con cada push")
print("  - Uso de prompts del Hub en cadenas LCEL")
