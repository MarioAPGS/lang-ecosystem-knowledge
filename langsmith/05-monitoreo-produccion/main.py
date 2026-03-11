"""
Monitoreo en Producción con LangSmith - Ejemplos ejecutables
==============================================================
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
import time
from dotenv import load_dotenv

load_dotenv()

from langsmith import Client, traceable
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig

client = Client()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ============================================================
# 1. Configurar tracing para producción
# ============================================================
print("=" * 60)
print("1. CONFIGURAR TRACING PARA PRODUCCIÓN")
print("=" * 60)

# En producción, usa un proyecto dedicado
os.environ["LANGSMITH_PROJECT"] = "tutorial-monitoreo-prod"
print(f"Proyecto: {os.environ['LANGSMITH_PROJECT']}")

# Verificar que tracing está activo
print(f"Tracing activo: {os.environ.get('LANGSMITH_TRACING', 'false')}")
# Ejemplo salida → Tracing activo: true
print()

# ============================================================
# 2. Trace con metadata de producción
# ============================================================
print("=" * 60)
print("2. TRACE CON METADATA DE PRODUCCIÓN")
print("=" * 60)

prompt = ChatPromptTemplate.from_template(
    "Responde en máximo 2 frases: {pregunta}"
)
chain = prompt | llm | StrOutputParser()

# Simular una petición de producción con contexto completo
config = RunnableConfig(
    tags=["produccion", "chatbot-v3", "us-east-1"],
    metadata={
        "user_id": "user-12345",
        "session_id": "sess-abc-678",
        "app_version": "3.1.0",
        "environment": "production",
        "region": "us-east-1",
    },
    run_name="chatbot-query",
)

response = chain.invoke(
    {"pregunta": "¿Qué es Python?"},
    config=config,
)
print(f"Respuesta: {response}")
# Ejemplo salida → Respuesta: Python es un lenguaje de programación interpretado y de propósito general...
print("→ Trace con metadata: user_id, session_id, version, region")
print()

# ============================================================
# 3. Simular múltiples peticiones (monitoreo)
# ============================================================
print("=" * 60)
print("3. SIMULAR TRÁFICO DE PRODUCCIÓN")
print("=" * 60)

preguntas_simuladas = [
    {"pregunta": "¿Qué es una API?", "user_id": "user-001"},
    {"pregunta": "¿Qué es SQL?", "user_id": "user-002"},
    {"pregunta": "¿Qué es Docker?", "user_id": "user-003"},
    {"pregunta": "¿Qué es Git?", "user_id": "user-001"},
    {"pregunta": "¿Qué es REST?", "user_id": "user-004"},
]

run_ids = []
for i, item in enumerate(preguntas_simuladas):
    config = RunnableConfig(
        tags=["produccion", "simulacion"],
        metadata={
            "user_id": item["user_id"],
            "request_index": i,
        },
        run_name=f"query-{i+1}",
    )

    start = time.time()
    response = chain.invoke(
        {"pregunta": item["pregunta"]},
        config=config,
    )
    elapsed = time.time() - start

    print(f"  [{i+1}/5] {item['pregunta'][:30]}... → {elapsed:.2f}s")

print(f"\n→ {len(preguntas_simuladas)} traces enviados a LangSmith")
print("→ Ve al dashboard para ver latencia, tokens y costes agregados")
print()

# ============================================================
# 4. Feedback programático
# ============================================================
print("=" * 60)
print("4. FEEDBACK PROGRAMÁTICO")
print("=" * 60)


@traceable(name="chatbot_con_feedback")
def chatbot_con_feedback(pregunta: str, user_id: str) -> dict:
    """Chatbot que permite enviar feedback después de responder."""
    response = llm.invoke(f"Responde brevemente: {pregunta}")
    return {
        "respuesta": response.content,
        "user_id": user_id,
    }


# Ejecutar y capturar el run_id para feedback
resultado = chatbot_con_feedback("¿Qué es Kubernetes?", user_id="user-test")
print(f"Respuesta: {resultado['respuesta'][:80]}...")
# Ejemplo salida → Respuesta: Kubernetes es una plataforma de orquestación de contenedores de código abierto...

# Nota: Para enviar feedback, necesitas el run_id del trace.
# En una app real, lo obtendrías del callback handler o del trace.
# Aquí mostramos cómo se haría con un run_id conocido:
print()
print("Ejemplo de cómo enviar feedback (con run_id conocido):")
print("""
    client.create_feedback(
        run_id="<run-id>",
        key="user_satisfaction",
        score=1.0,
        comment="Respuesta útil y precisa"
    )
""")
print()

# ============================================================
# 5. Consultar runs recientes con el SDK
# ============================================================
print("=" * 60)
print("5. CONSULTAR RUNS RECIENTES")
print("=" * 60)

project_name = os.environ.get("LANGSMITH_PROJECT", "default")

try:
    # Obtener los últimos runs del proyecto
    runs = list(client.list_runs(
        project_name=project_name,
        limit=5,
    ))

    print(f"Últimos {len(runs)} runs en '{project_name}':")
    for run in runs:
        status = "✅" if run.status == "success" else "❌"
        latency = ""
        if run.end_time and run.start_time:
            latency = f"{(run.end_time - run.start_time).total_seconds():.2f}s"

        tokens_info = ""
        if run.total_tokens:
            tokens_info = f" | {run.total_tokens} tokens"

        print(f"  {status} {run.name or 'unnamed'} - {latency}{tokens_info}")

except Exception as e:
    print(f"Error al consultar runs: {e}")
print()

# ============================================================
# 6. Filtrar runs por metadata
# ============================================================
print("=" * 60)
print("6. FILTRAR RUNS POR METADATA")
print("=" * 60)

try:
    # Filtrar runs de un usuario específico
    runs_usuario = list(client.list_runs(
        project_name=project_name,
        filter='has(metadata, \'{"user_id": "user-001"}\')',
        limit=5,
    ))
    print(f"Runs del user-001: {len(runs_usuario)}")
    for run in runs_usuario:
        print(f"  - {run.name}: {run.status}")
except Exception as e:
    print(f"Nota: Filtrado por metadata puede variar según la versión del SDK")
    print(f"  Error: {e}")
print()

# ============================================================
# 7. Calcular métricas básicas
# ============================================================
print("=" * 60)
print("7. CALCULAR MÉTRICAS BÁSICAS")
print("=" * 60)

try:
    runs_recientes = list(client.list_runs(
        project_name=project_name,
        limit=20,
    ))

    if runs_recientes:
        # Calcular latencia promedio
        latencias = []
        total_tokens = 0
        errores = 0

        for run in runs_recientes:
            if run.end_time and run.start_time:
                latencia = (run.end_time - run.start_time).total_seconds()
                latencias.append(latencia)
            if run.total_tokens:
                total_tokens += run.total_tokens
            if run.status == "error":
                errores += 1

        if latencias:
            latencias.sort()
            avg_latencia = sum(latencias) / len(latencias)
            p50 = latencias[len(latencias) // 2]
            p95_idx = int(len(latencias) * 0.95)
            p95 = latencias[min(p95_idx, len(latencias) - 1)]

            print(f"Métricas de {len(runs_recientes)} runs recientes:")
            print(f"  Latencia promedio: {avg_latencia:.2f}s")
            print(f"  Latencia p50: {p50:.2f}s")
            print(f"  Latencia p95: {p95:.2f}s")
            print(f"  Tokens totales: {total_tokens}")
            print(f"  Tasa de errores: {errores}/{len(runs_recientes)} ({errores/len(runs_recientes)*100:.1f}%)")
        else:
            print("No se encontraron latencias en los runs recientes")
    else:
        print("No hay runs recientes disponibles")
except Exception as e:
    print(f"Error al calcular métricas: {e}")
print()

# Restaurar proyecto original
os.environ["LANGSMITH_PROJECT"] = "langsmith-tutorial"

print("=" * 60)
print("✅ MONITOREO COMPLETADO")
print("=" * 60)
print("En producción real, estas métricas se visualizan en el dashboard de LangSmith:")
print("  - Latencia en tiempo real (p50, p95, p99)")
print("  - Tokens y costes por período")
print("  - Tasa de errores y alertas")
print("  - Feedback de usuarios")
print("  - Filtros por metadata (user_id, version, region)")
