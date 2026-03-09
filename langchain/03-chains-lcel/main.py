"""
Chains con LCEL - Ejemplos ejecutables
=======================================
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
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
parser = StrOutputParser()

# ============================================================
# 1. Cadena básica: prompt | llm | parser
# ============================================================
print("=" * 60)
print("1. CADENA BÁSICA")
print("=" * 60)

prompt = ChatPromptTemplate.from_template(
    "Explica {concepto} en una frase simple"
)

# Componer la cadena
chain = prompt | llm | parser

# Ejecutar
resultado = chain.invoke({"concepto": "la recursión"})
print(f"Resultado: {resultado}")
# Ejemplo salida → Resultado: La recursión es cuando una función se llama a sí misma para resolver un problema dividiéndolo en partes más pequeñas.
print()

# ============================================================
# 2. Cadena con múltiples variables
# ============================================================
print("=" * 60)
print("2. CADENA CON MÚLTIPLES VARIABLES")
print("=" * 60)

prompt_traductor = ChatPromptTemplate.from_messages([
    ("system", "Eres un traductor profesional de {origen} a {destino}."),
    ("human", "Traduce: {texto}")
])

chain_traductor = prompt_traductor | llm | parser

resultado = chain_traductor.invoke({
    "origen": "español",
    "destino": "japonés",
    "texto": "Buenos días, ¿cómo estás?"
})
print(f"Traducción: {resultado}")
# Ejemplo salida → Traducción: おはようございます、お元気ですか？
print()

# ============================================================
# 3. RunnablePassthrough
# ============================================================
print("=" * 60)
print("3. RUNNABLEPASSTHROUGH")
print("=" * 60)

# RunnablePassthrough pasa el input tal cual
# Útil para inyectar datos en un RunnableParallel

prompt_qa = ChatPromptTemplate.from_template(
    "Contexto: {contexto}\n\nPregunta: {pregunta}\n\nResponde basándote solo en el contexto."
)


def obtener_contexto(input_dict):
    """Simula obtener contexto de una base de datos."""
    contextos = {
        "python": "Python fue creado por Guido van Rossum en 1991. Es un lenguaje interpretado y de tipado dinámico.",
        "javascript": "JavaScript fue creado por Brendan Eich en 1995. Se ejecuta en navegadores y servidores (Node.js).",
    }
    tema = input_dict.get("pregunta", "").lower()
    for key, value in contextos.items():
        if key in tema:
            return value
    return "No se encontró contexto relevante."


chain_qa = (
    {"contexto": RunnableLambda(obtener_contexto), "pregunta": RunnablePassthrough()}
    | prompt_qa
    | llm
    | parser
)

# Nota: RunnablePassthrough pasa el dict completo, pero la pregunta también
# está disponible en el contexto
resultado = chain_qa.invoke({"pregunta": "¿Quién creó Python?"})
print(f"Respuesta: {resultado}")
# Ejemplo salida → Respuesta: Python fue creado por Guido van Rossum en 1991.
print()

# ============================================================
# 4. RunnableParallel - Ejecución en paralelo
# ============================================================
print("=" * 60)
print("4. RUNNABLEPARALLEL")
print("=" * 60)

prompt_resumen = ChatPromptTemplate.from_template(
    "Resume este texto en una frase: {texto}"
)

prompt_idioma = ChatPromptTemplate.from_template(
    "¿En qué idioma está escrito este texto? Responde solo el nombre del idioma: {texto}"
)

prompt_sentimiento = ChatPromptTemplate.from_template(
    "¿Cuál es el sentimiento de este texto (positivo/negativo/neutro)? Responde una sola palabra: {texto}"
)

# Ejecutar 3 análisis en paralelo
chain_analisis = RunnableParallel(
    resumen=prompt_resumen | llm | parser,
    idioma=prompt_idioma | llm | parser,
    sentimiento=prompt_sentimiento | llm | parser,
)

texto = "Me encanta programar en Python, es un lenguaje maravilloso que me permite crear cosas increíbles."

resultado = chain_analisis.invoke({"texto": texto})
print(f"Resumen: {resultado['resumen']}")
# Ejemplo salida → Resumen: El autor expresa su entusiasmo por programar en Python y lo considera un lenguaje que permite crear cosas increíbles.
print(f"Idioma: {resultado['idioma']}")
# Ejemplo salida → Idioma: Español
print(f"Sentimiento: {resultado['sentimiento']}")
# Ejemplo salida → Sentimiento: Positivo
print()

# ============================================================
# 5. RunnableLambda - Funciones custom
# ============================================================
print("=" * 60)
print("5. RUNNABLELAMBDA")
print("=" * 60)


def limpiar_texto(texto: str) -> str:
    """Limpia y normaliza el texto."""
    return texto.strip().lower().replace("  ", " ")


def contar_palabras(texto: str) -> dict:
    """Cuenta las palabras del texto."""
    palabras = texto.split()
    return {"texto": texto, "num_palabras": len(palabras)}


# Encadenar funciones Python con LLM
chain_procesamiento = (
    RunnableLambda(limpiar_texto)
    | RunnableLambda(contar_palabras)
    | RunnableLambda(
        lambda x: f"El texto tiene {x['num_palabras']} palabras: '{x['texto']}'"
    )
)

resultado = chain_procesamiento.invoke("  Hola   Mundo   desde   LangChain  ")
print(f"Resultado: {resultado}")
# Ejemplo salida → Resultado: El texto tiene 4 palabras: 'hola mundo desde langchain'
print()

# ============================================================
# 6. Streaming de cadenas
# ============================================================
print("=" * 60)
print("6. STREAMING DE CADENAS")
print("=" * 60)

prompt_historia = ChatPromptTemplate.from_template(
    "Escribe una micro-historia de 3 frases sobre {tema}"
)

chain_historia = prompt_historia | llm | parser

print("Historia en streaming: ", end="")
for chunk in chain_historia.stream({"tema": "un robot que aprende a cocinar"}):
    print(chunk, end="", flush=True)
print("\n")
# Ejemplo salida → Historia en streaming: Robot-7 quemó su primer huevo frito. Después de 847 intentos, dominó la tortilla perfecta. Ahora tiene un restaurante con estrella Michelin.

# ============================================================
# 7. Batch - Múltiples ejecuciones
# ============================================================
print("=" * 60)
print("7. BATCH")
print("=" * 60)

prompt_emoji = ChatPromptTemplate.from_template(
    "Representa '{palabra}' con un solo emoji. Responde SOLO el emoji."
)

chain_emoji = prompt_emoji | llm | parser

# Procesar múltiples inputs a la vez
palabras = [
    {"palabra": "sol"},
    {"palabra": "lluvia"},
    {"palabra": "programar"},
    {"palabra": "café"},
]

resultados = chain_emoji.batch(palabras)
for palabra, emoji in zip(palabras, resultados):
    print(f"  {palabra['palabra']} → {emoji.strip()}")
# Ejemplo salida →
#   sol → ☀️
#   lluvia → 🌧️
#   programar → 💻
#   café → ☕
print()

# ============================================================
# 8. Encadenamiento multi-paso
# ============================================================
print("=" * 60)
print("8. ENCADENAMIENTO MULTI-PASO")
print("=" * 60)

# Paso 1: Generar un tema
prompt_tema = ChatPromptTemplate.from_template(
    "Sugiere un tema interesante de {area}. Responde solo el nombre del tema."
)

# Paso 2: Escribir sobre ese tema
prompt_escribir = ChatPromptTemplate.from_template(
    "Escribe un párrafo corto (2-3 frases) sobre: {tema}"
)

# Cadena multi-paso: un LLM genera el tema, otro escribe sobre él
chain_multi = (
    prompt_tema
    | llm
    | parser
    | (lambda tema: {"tema": tema})  # Transformar string a dict
    | prompt_escribir
    | llm
    | parser
)

resultado = chain_multi.invoke({"area": "inteligencia artificial"})
print(f"Resultado multi-paso: {resultado}")
# Ejemplo salida → Resultado multi-paso: Las redes neuronales transformadoras (Transformers) revolucionaron el procesamiento del lenguaje natural al permitir que los modelos procesen secuencias completas en paralelo en lugar de secuencialmente.
