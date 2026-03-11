"""
Configuración y Setup de LangSmith - Ejemplos ejecutables
==========================================================
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

# ============================================================
# 1. Verificar configuración
# ============================================================
print("=" * 60)
print("1. VERIFICAR CONFIGURACIÓN")
print("=" * 60)

tracing_enabled = os.environ.get("LANGSMITH_TRACING", "false")
api_key = os.environ.get("LANGSMITH_API_KEY", "")
project = os.environ.get("LANGSMITH_PROJECT", "default")

print(f"Tracing habilitado: {tracing_enabled}")
# Ejemplo salida → Tracing habilitado: true
print(f"API Key configurada: {'✅ Sí' if api_key else '❌ No'}")
# Ejemplo salida → API Key configurada: ✅ Sí
print(f"Proyecto: {project}")
# Ejemplo salida → Proyecto: langsmith-tutorial
print()

# ============================================================
# 2. Verificar conexión con LangSmith
# ============================================================
print("=" * 60)
print("2. VERIFICAR CONEXIÓN CON LANGSMITH")
print("=" * 60)

from langsmith import Client

try:
    client = Client()
    # list_projects es una forma rápida de verificar la conexión
    projects = list(client.list_projects())
    print(f"Conexión exitosa ✅")
    print(f"Proyectos encontrados: {len(projects)}")
    for p in projects[:5]:  # Mostrar los primeros 5
        print(f"  - {p.name}")
except Exception as e:
    print(f"Error de conexión ❌: {e}")
print()

# ============================================================
# 3. Trace automático con LangChain
# ============================================================
print("=" * 60)
print("3. TRACE AUTOMÁTICO CON LANGCHAIN")
print("=" * 60)

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Esta llamada se tracea automáticamente en LangSmith
response = llm.invoke("Di 'hola mundo' y nada más")
print(f"Respuesta: {response.content}")
# Ejemplo salida → Respuesta: hola mundo
print("→ Ve a smith.langchain.com para ver el trace de esta llamada")
print()

# ============================================================
# 4. Trace automático de una cadena LCEL
# ============================================================
print("=" * 60)
print("4. TRACE DE UNA CADENA LCEL")
print("=" * 60)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template(
    "Explica {concepto} en una frase corta."
)
parser = StrOutputParser()

chain = prompt | llm | parser

# El trace mostrará: prompt → LLM → parser (cada paso separado)
resultado = chain.invoke({"concepto": "variables en Python"})
print(f"Resultado: {resultado}")
# Ejemplo salida → Resultado: Las variables en Python son nombres que almacenan valores en memoria.
print("→ En LangSmith verás el trace con 3 pasos: prompt, llm, parser")
print()

# ============================================================
# 5. Trace manual con @traceable
# ============================================================
print("=" * 60)
print("5. TRACE MANUAL CON @traceable")
print("=" * 60)

from langsmith import traceable


@traceable(name="procesar_texto")
def procesar_texto(texto: str) -> dict:
    """Función custom que se tracea en LangSmith."""
    palabras = texto.split()
    return {
        "original": texto,
        "num_palabras": len(palabras),
        "mayusculas": texto.upper(),
    }


resultado = procesar_texto("LangSmith es muy útil para depurar")
print(f"Resultado: {resultado}")
# Ejemplo salida → Resultado: {'original': 'LangSmith es muy útil para depurar', 'num_palabras': 6, 'mayusculas': 'LANGSMITH ES MUY ÚTIL PARA DEPURAR'}
print("→ Esta función aparece como un trace en LangSmith")
print()

# ============================================================
# 6. @traceable con llamadas a LLM dentro
# ============================================================
print("=" * 60)
print("6. @traceable CON LLM DENTRO")
print("=" * 60)


@traceable(name="resumen_inteligente")
def resumen_inteligente(texto: str) -> str:
    """
    Función que combina lógica Python + LLM.
    El trace mostrará la función padre y la llamada al LLM como hijo.
    """
    # Lógica Python (aparece en el trace)
    num_palabras = len(texto.split())

    # Llamada a LLM (aparece como run hijo en el trace)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    response = llm.invoke(f"Resume en 10 palabras: {texto}")

    return f"[{num_palabras} palabras] → {response.content}"


resultado = resumen_inteligente(
    "LangSmith es una plataforma de observabilidad que permite "
    "depurar y evaluar aplicaciones construidas con modelos de lenguaje"
)
print(f"Resultado: {resultado}")
# Ejemplo salida → Resultado: [16 palabras] → Plataforma para depurar y evaluar aplicaciones con modelos de lenguaje.
print("→ En LangSmith verás la función padre con la llamada LLM anidada")
print()

# ============================================================
# 7. Uso de proyectos para organizar traces
# ============================================================
print("=" * 60)
print("7. ORGANIZAR TRACES POR PROYECTO")
print("=" * 60)

# Guardar proyecto actual
proyecto_original = os.environ.get("LANGSMITH_PROJECT", "default")

# Cambiar temporalmente a otro proyecto
os.environ["LANGSMITH_PROJECT"] = "experimento-temporal"
print(f"Proyecto actual: {os.environ['LANGSMITH_PROJECT']}")

response = llm.invoke("Este trace va al proyecto 'experimento-temporal'")
print(f"Respuesta: {response.content}")

# Restaurar proyecto original
os.environ["LANGSMITH_PROJECT"] = proyecto_original
print(f"Proyecto restaurado: {os.environ['LANGSMITH_PROJECT']}")
print()

# ============================================================
# 8. Metadata y tags en traces
# ============================================================
print("=" * 60)
print("8. METADATA Y TAGS EN TRACES")
print("=" * 60)

from langchain_core.runnables import RunnableConfig

# Puedes añadir metadata y tags a cualquier invocación
config = RunnableConfig(
    tags=["tutorial", "setup"],
    metadata={"version": "1.0", "autor": "mi-nombre"},
)

response = llm.invoke("Di 'configuración completa'", config=config)
print(f"Respuesta: {response.content}")
# Ejemplo salida → Respuesta: configuración completa
print("→ En LangSmith puedes filtrar por tags y metadata")
print()

print("=" * 60)
print("✅ SETUP COMPLETADO")
print("=" * 60)
print("Todos los traces de estos ejemplos están en smith.langchain.com")
print(f"Busca en el proyecto: '{proyecto_original}'")
