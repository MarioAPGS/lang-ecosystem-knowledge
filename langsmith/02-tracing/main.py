"""
Tracing en LangSmith - Ejemplos ejecutables
=============================================
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

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langsmith import traceable

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ============================================================
# 1. Trace automático - Llamada simple al LLM
# ============================================================
print("=" * 60)
print("1. TRACE AUTOMÁTICO - LLAMADA SIMPLE")
print("=" * 60)

response = llm.invoke("¿Qué es el tracing en software?")
print(f"Respuesta: {response.content[:100]}...")
# Ejemplo salida → Respuesta: El tracing es una técnica para registrar la ejecución de un programa paso a paso...
print("→ Trace visible en LangSmith con: input, output, tokens, latencia")
print()

# ============================================================
# 2. Trace automático - Cadena LCEL completa
# ============================================================
print("=" * 60)
print("2. TRACE DE CADENA LCEL (MÚLTIPLES PASOS)")
print("=" * 60)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un experto en {tema}. Responde en máximo 2 frases."),
    ("human", "{pregunta}")
])
parser = StrOutputParser()

chain = prompt | llm | parser

resultado = chain.invoke({
    "tema": "bases de datos",
    "pregunta": "¿Qué es un índice?"
})
print(f"Resultado: {resultado}")
# Ejemplo salida → Resultado: Un índice es una estructura de datos que mejora la velocidad de las consultas...
print("→ En LangSmith verás 3 runs: PromptTemplate → ChatOpenAI → StrOutputParser")
print()

# ============================================================
# 3. @traceable - Función Python simple
# ============================================================
print("=" * 60)
print("3. @traceable - FUNCIÓN PYTHON SIMPLE")
print("=" * 60)


@traceable(name="transformar_texto")
def transformar_texto(texto: str, modo: str = "upper") -> dict:
    """Función Python pura que se tracea en LangSmith."""
    if modo == "upper":
        resultado = texto.upper()
    elif modo == "lower":
        resultado = texto.lower()
    else:
        resultado = texto.title()

    return {
        "original": texto,
        "transformado": resultado,
        "modo": modo,
        "longitud": len(texto),
    }


resultado = transformar_texto("Hola LangSmith", modo="upper")
print(f"Resultado: {resultado}")
# Ejemplo salida → Resultado: {'original': 'Hola LangSmith', 'transformado': 'HOLA LANGSMITH', 'modo': 'upper', 'longitud': 14}
print("→ Trace muestra input=(texto, modo) y output=(dict con resultado)")
print()

# ============================================================
# 4. @traceable - Con llamada a LLM anidada
# ============================================================
print("=" * 60)
print("4. @traceable CON LLM ANIDADO")
print("=" * 60)


@traceable(name="analisis_sentimiento")
def analizar_sentimiento(texto: str) -> dict:
    """
    Función que combina lógica Python + LLM.
    En el trace se verá la función padre con el LLM como hijo.
    """
    # Paso 1: Pre-procesamiento (lógica Python)
    texto_limpio = texto.strip().lower()
    num_palabras = len(texto_limpio.split())

    # Paso 2: Análisis con LLM (aparece como run hijo)
    response = llm.invoke(
        f"Clasifica el sentimiento de este texto como POSITIVO, NEGATIVO o NEUTRO. "
        f"Responde solo con una palabra.\n\nTexto: {texto_limpio}"
    )

    return {
        "texto": texto_limpio,
        "num_palabras": num_palabras,
        "sentimiento": response.content.strip(),
    }


resultado = analizar_sentimiento("Me encanta programar con Python, es genial!")
print(f"Resultado: {resultado}")
# Ejemplo salida → Resultado: {'texto': 'me encanta programar con python, es genial!', 'num_palabras': 7, 'sentimiento': 'POSITIVO'}
print("→ Trace: analisis_sentimiento → ChatOpenAI (anidado)")
print()

# ============================================================
# 5. Runs anidados - Múltiples niveles
# ============================================================
print("=" * 60)
print("5. RUNS ANIDADOS - MÚLTIPLES NIVELES")
print("=" * 60)


@traceable(name="validar_input")
def validar_input(texto: str) -> str:
    """Nivel 2: Validación."""
    if not texto.strip():
        raise ValueError("Input vacío")
    return texto.strip()


@traceable(name="generar_respuesta")
def generar_respuesta(pregunta: str) -> str:
    """Nivel 2: Generación con LLM."""
    response = llm.invoke(f"Responde en 1 frase: {pregunta}")
    return response.content


@traceable(name="pipeline_completo")
def pipeline_completo(pregunta: str) -> dict:
    """
    Nivel 1: Pipeline principal.
    Llama a validar_input y generar_respuesta como hijos.
    """
    # Hijo 1: Validación
    pregunta_limpia = validar_input(pregunta)

    # Hijo 2: Generación
    respuesta = generar_respuesta(pregunta_limpia)

    return {
        "pregunta": pregunta_limpia,
        "respuesta": respuesta,
    }


resultado = pipeline_completo("  ¿Qué es un API REST?  ")
print(f"Resultado: {resultado}")
# Ejemplo salida → Resultado: {'pregunta': '¿Qué es un API REST?', 'respuesta': 'Un API REST es una interfaz...'}
print("→ Trace: pipeline_completo → validar_input + generar_respuesta → ChatOpenAI")
print()

# ============================================================
# 6. Metadata y tags en @traceable
# ============================================================
print("=" * 60)
print("6. METADATA Y TAGS EN @traceable")
print("=" * 60)


@traceable(
    name="consulta_con_metadata",
    tags=["tutorial", "ejemplo-metadata"],
    metadata={"version": "1.0", "tipo": "demo"},
)
def consulta_con_metadata(pregunta: str) -> str:
    """Función con metadata y tags configurados."""
    response = llm.invoke(pregunta)
    return response.content


resultado = consulta_con_metadata("¿Qué son los tags en LangSmith?")
print(f"Resultado: {resultado[:100]}...")
# Ejemplo salida → Resultado: Los tags en LangSmith son etiquetas que puedes agregar a los traces...
print("→ En LangSmith puedes filtrar este trace por tag:tutorial")
print()

# ============================================================
# 7. Tags y metadata en invocaciones LangChain
# ============================================================
print("=" * 60)
print("7. TAGS Y METADATA EN LANGCHAIN")
print("=" * 60)

from langchain_core.runnables import RunnableConfig

# Configurar metadata y tags por invocación
config = RunnableConfig(
    tags=["comparacion-modelos", "gpt4o-mini"],
    metadata={
        "experiment_id": "exp-001",
        "usuario": "tutorial",
    },
    run_name="consulta-personalizada",
)

response = chain.invoke(
    {"tema": "Python", "pregunta": "¿Qué es un decorador?"},
    config=config,
)
print(f"Resultado: {response}")
# Ejemplo salida → Resultado: Un decorador es una función que envuelve otra función para extender su comportamiento...
print("→ Run nombrado 'consulta-personalizada' con tags y metadata")
print()

# ============================================================
# 8. Tracear un run_type específico
# ============================================================
print("=" * 60)
print("8. RUN TYPES ESPECÍFICOS")
print("=" * 60)


@traceable(name="buscar_documentos", run_type="retriever")
def buscar_documentos(query: str) -> list:
    """Simula una búsqueda. Aparece como 'retriever' en LangSmith."""
    # Simulación de resultados
    docs = [
        {"titulo": "Intro a Python", "relevancia": 0.95},
        {"titulo": "Python avanzado", "relevancia": 0.87},
        {"titulo": "Data Science con Python", "relevancia": 0.82},
    ]
    return [d for d in docs if d["relevancia"] > 0.85]


@traceable(name="formatear_resultado", run_type="tool")
def formatear_resultado(docs: list) -> str:
    """Simula formateo. Aparece como 'tool' en LangSmith."""
    return "\n".join([f"- {d['titulo']} ({d['relevancia']})" for d in docs])


# Ejecución
docs = buscar_documentos("tutoriales de Python")
texto = formatear_resultado(docs)
print(f"Documentos encontrados:\n{texto}")
# Ejemplo salida →
# Documentos encontrados:
# - Intro a Python (0.95)
# - Python avanzado (0.87)
print("→ En LangSmith: buscar_documentos (🔍 retriever) + formatear_resultado (🔧 tool)")
print()

print("=" * 60)
print("✅ TODOS LOS TRACES ENVIADOS A LANGSMITH")
print("=" * 60)
print("Revisa smith.langchain.com para explorar cada trace")
