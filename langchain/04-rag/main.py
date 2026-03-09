"""
RAG (Retrieval-Augmented Generation) - Ejemplos ejecutables
============================================================
Prerequisitos:
    pip install langchain-openai langchain-chroma langchain-community python-dotenv

Configuración:
    Crea un archivo .env en la raíz del proyecto con:
    OPENAI_API_KEY=sk-...
"""

import os
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = StrOutputParser()

# ============================================================
# 1. Crear documentos de ejemplo
# ============================================================
print("=" * 60)
print("1. CREAR DOCUMENTOS DE EJEMPLO")
print("=" * 60)

# Simulamos una base de conocimiento sobre una empresa ficticia
documentos_raw = [
    Document(
        page_content="""
        TechCorp es una empresa de software fundada en 2020 en Madrid, España.
        Se especializa en desarrollo de aplicaciones web y móviles.
        Cuenta con un equipo de 50 desarrolladores.
        Su tecnología principal es Python y React.
        """,
        metadata={"source": "empresa.txt", "section": "general"},
    ),
    Document(
        page_content="""
        Los productos principales de TechCorp son:
        1. AppBuilder: Una plataforma no-code para crear aplicaciones móviles.
        2. DataFlow: Un sistema de ETL para procesamiento de datos en tiempo real.
        3. CloudDash: Un dashboard de monitorización de infraestructura cloud.
        AppBuilder tiene más de 10,000 usuarios activos.
        """,
        metadata={"source": "productos.txt", "section": "productos"},
    ),
    Document(
        page_content="""
        La política de vacaciones de TechCorp incluye:
        - 25 días laborables de vacaciones al año
        - 3 días de asuntos propios
        - Viernes de verano con jornada intensiva (junio a septiembre)
        - Trabajo remoto 100% flexible
        El horario estándar es de 9:00 a 18:00 con flexibilidad de ± 2 horas.
        """,
        metadata={"source": "rrhh.txt", "section": "rrhh"},
    ),
    Document(
        page_content="""
        El proceso de onboarding en TechCorp dura 2 semanas e incluye:
        - Día 1: Bienvenida y configuración del equipo
        - Día 2-3: Formación sobre herramientas internas (Jira, GitHub, Slack)
        - Día 4-5: Pair programming con un mentor asignado
        - Semana 2: Primer ticket real con supervisión
        Cada nuevo empleado tiene un buddy asignado durante los primeros 3 meses.
        """,
        metadata={"source": "rrhh.txt", "section": "onboarding"},
    ),
]

print(f"Documentos creados: {len(documentos_raw)}")
# Ejemplo salida → Documentos creados: 4
for doc in documentos_raw:
    print(f"  - {doc.metadata['source']} ({doc.metadata['section']}): {len(doc.page_content)} chars")
# Ejemplo salida →
#   - empresa.txt (general): 230 chars
#   - productos.txt (productos): 310 chars
#   - rrhh.txt (rrhh): 295 chars
#   - rrhh.txt (onboarding): 340 chars
print()

# ============================================================
# 2. Dividir en chunks
# ============================================================
print("=" * 60)
print("2. DIVIDIR EN CHUNKS")
print("=" * 60)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,       # Máximo 300 caracteres por chunk
    chunk_overlap=50,     # 50 caracteres de superposición
    separators=["\n\n", "\n", ". ", " "],  # Prioridad de separadores
)

chunks = splitter.split_documents(documentos_raw)

print(f"Documentos originales: {len(documentos_raw)}")
# Ejemplo salida → Documentos originales: 4
print(f"Chunks resultantes: {len(chunks)}")
# Ejemplo salida → Chunks resultantes: 7
print()
for i, chunk in enumerate(chunks):
    print(f"  Chunk {i+1} ({len(chunk.page_content)} chars): {chunk.page_content[:80].strip()}...")
# Ejemplo salida →
#   Chunk 1 (225 chars): TechCorp es una empresa de software fundada en 2020 en Madrid, España...
#   Chunk 2 (280 chars): Los productos principales de TechCorp son...
print()

# ============================================================
# 3. Crear vectorstore con embeddings
# ============================================================
print("=" * 60)
print("3. CREAR VECTORSTORE")
print("=" * 60)

embeddings = OpenAIEmbeddings()

# Crear vectorstore in-memory con Chroma
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="techcorp_docs",
    
)

print(f"Vectorstore creado con {vectorstore._collection.count()} documentos")
# Ejemplo salida → Vectorstore creado con 7 documentos
print()

# ============================================================
# 4. Búsqueda semántica
# ============================================================
print("=" * 60)
print("4. BÚSQUEDA SEMÁNTICA")
print("=" * 60)

# Buscar documentos similares a una consulta
query = "¿Cuántos días de vacaciones tengo?"
docs_encontrados = vectorstore.similarity_search(query, k=2)

print(f"Query: '{query}'")
print(f"Documentos encontrados: {len(docs_encontrados)}")
# Ejemplo salida → Documentos encontrados: 2
for i, doc in enumerate(docs_encontrados):
    print(f"\n  Doc {i+1} (source: {doc.metadata.get('source', 'N/A')}):")
    print(f"  {doc.page_content[:150].strip()}...")
# Ejemplo salida →
#   Doc 1 (source: rrhh.txt):
#   La política de vacaciones de TechCorp incluye: - 25 días laborables de vacaciones al año...
print()

# También puedes obtener scores de similitud
docs_con_score = vectorstore.similarity_search_with_score(query, k=2)
print("Con scores de similitud:")
for doc, score in docs_con_score:
    print(f"  Score: {score:.4f} | {doc.page_content[:80].strip()}...")
# Ejemplo salida →
#   Score: 0.3421 | La política de vacaciones de TechCorp incluye...
#   Score: 0.5872 | El proceso de onboarding en TechCorp dura 2 semanas...
print()

# ============================================================
# 5. Crear retriever
# ============================================================
print("=" * 60)
print("5. RETRIEVER")
print("=" * 60)

retriever = vectorstore.as_retriever(
    search_type="similarity",  # o "mmr" para diversidad
    search_kwargs={"k": 2},    # Número de documentos a recuperar
)

# El retriever tiene la misma interfaz .invoke()
docs = retriever.invoke("¿Qué productos tiene la empresa?")
print(f"Retriever encontró {len(docs)} documentos:")
for doc in docs:
    print(f"  - {doc.page_content[:100].strip()}...")
# Ejemplo salida →
#   Retriever encontró 2 documentos:
#   - Los productos principales de TechCorp son: 1. AppBuilder: Una plataforma no-code...
#   - TechCorp es una empresa de software fundada en 2020...
print()

# ============================================================
# 6. Pipeline RAG completo
# ============================================================
print("=" * 60)
print("6. PIPELINE RAG COMPLETO")
print("=" * 60)

# Prompt especializado para RAG
rag_prompt = ChatPromptTemplate.from_template("""
Responde la pregunta basándote ÚNICAMENTE en el siguiente contexto.
Si no encuentras la respuesta en el contexto, di "No tengo información sobre eso".

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:""")


def format_docs(docs):
    """Convierte una lista de documentos en un string."""
    return "\n\n".join(doc.page_content for doc in docs)


# Cadena RAG con LCEL
rag_chain = (
    {"contexto": retriever | format_docs, "pregunta": RunnablePassthrough()}
    | rag_prompt
    | llm
    | parser
)

# Probar con varias preguntas
preguntas = [
    "¿Cuántos días de vacaciones tengo al año?",
    "¿Qué es AppBuilder y cuántos usuarios tiene?",
    "¿Cómo es el proceso de onboarding?",
    "¿Cuál es el precio de las acciones?",  # No está en los documentos
]

for pregunta in preguntas:
    respuesta = rag_chain.invoke(pregunta)
    print(f"P: {pregunta}")
    print(f"R: {respuesta}")
    # Ejemplo salida →
    #   P: ¿Cuántos días de vacaciones tengo al año?
    #   R: Tienes 25 días laborables de vacaciones al año, además de 3 días de asuntos propios.
    #   P: ¿Cuál es el precio de las acciones?
    #   R: No tengo información sobre eso.
    print()

# ============================================================
# 7. RAG con fuentes (citar de dónde viene la info)
# ============================================================
print("=" * 60)
print("7. RAG CON FUENTES")
print("=" * 60)

rag_prompt_sources = ChatPromptTemplate.from_template("""
Responde la pregunta basándote en el contexto. Al final, cita las fuentes usadas.

Contexto:
{contexto}

Fuentes disponibles:
{fuentes}

Pregunta: {pregunta}

Respuesta (incluye las fuentes al final):""")


def format_docs_with_sources(docs):
    """Formatea documentos y extrae las fuentes."""
    contexto = "\n\n".join(doc.page_content for doc in docs)
    fuentes = ", ".join(set(doc.metadata.get("source", "desconocido") for doc in docs))
    return {"contexto": contexto, "fuentes": fuentes}


pregunta = "¿Cuántos desarrolladores tiene TechCorp y en qué tecnologías trabajan?"
docs = retriever.invoke(pregunta)
docs_info = format_docs_with_sources(docs)

respuesta = (rag_prompt_sources | llm | parser).invoke({
    **docs_info,
    "pregunta": pregunta,
})

print(f"P: {pregunta}")
print(f"R: {respuesta}")
# Ejemplo salida →
#   P: ¿Cuántos desarrolladores tiene TechCorp y en qué tecnologías trabajan?
#   R: TechCorp cuenta con 50 desarrolladores. Su tecnología principal es Python y React. (Fuente: empresa.txt)

# Limpieza
vectorstore.delete_collection()
print("\n✅ Vectorstore limpiado")
