"""
Testing y Experiments en LangSmith - Ejemplos ejecutables
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

from langsmith import Client, evaluate, traceable
from langsmith.schemas import Example, Run
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

client = Client()

# ============================================================
# 1. Crear dataset de testing
# ============================================================
print("=" * 60)
print("1. CREAR DATASET DE TESTING")
print("=" * 60)

dataset_name = "tutorial-testing-conceptos"

# Limpiar si existe
try:
    existing = client.read_dataset(dataset_name=dataset_name)
    client.delete_dataset(dataset_id=existing.id)
except Exception:
    pass

dataset = client.create_dataset(
    dataset_name=dataset_name,
    description="Conceptos de programación para testing de diferentes configuraciones"
)

# Ejemplos con respuestas esperadas
client.create_examples(
    inputs=[
        {"pregunta": "¿Qué es una variable?"},
        {"pregunta": "¿Qué es una función?"},
        {"pregunta": "¿Qué es un bucle for?"},
        {"pregunta": "¿Qué es una clase en programación?"},
        {"pregunta": "¿Qué es un array?"},
        {"pregunta": "¿Qué es recursión?"},
        {"pregunta": "¿Qué es una API REST?"},
        {"pregunta": "¿Qué es un tipo de dato?"},
    ],
    outputs=[
        {"respuesta": "Una variable es un espacio en memoria que almacena un valor y se identifica con un nombre."},
        {"respuesta": "Una función es un bloque de código reutilizable que realiza una tarea específica y puede recibir parámetros y devolver un resultado."},
        {"respuesta": "Un bucle for es una estructura de control que repite un bloque de código un número determinado de veces o sobre los elementos de una colección."},
        {"respuesta": "Una clase es una plantilla que define las propiedades y comportamientos de un tipo de objeto en programación orientada a objetos."},
        {"respuesta": "Un array es una estructura de datos que almacena una colección de elementos del mismo tipo en posiciones contiguas de memoria."},
        {"respuesta": "La recursión es una técnica donde una función se llama a sí misma para resolver un problema dividiéndolo en subproblemas más pequeños."},
        {"respuesta": "Una API REST es una interfaz que permite la comunicación entre sistemas usando el protocolo HTTP con operaciones estándar como GET, POST, PUT y DELETE."},
        {"respuesta": "Un tipo de dato define la naturaleza de un valor (entero, texto, booleano, etc.) y las operaciones que se pueden realizar con él."},
    ],
    dataset_id=dataset.id,
)

print(f"Dataset '{dataset_name}' creado con 8 ejemplos ✅")
print()

# ============================================================
# 2. Definir evaluadores
# ============================================================
print("=" * 60)
print("2. DEFINIR EVALUADORES")
print("=" * 60)


# Evaluador 1: Longitud razonable
def eval_longitud(run: Run, example: Example) -> dict:
    """Verifica que la respuesta tiene longitud adecuada (20-500 chars)."""
    output = run.outputs.get("respuesta", "")
    length = len(output)
    score = 1.0 if 20 <= length <= 500 else 0.0
    return {"key": "longitud_ok", "score": score}


# Evaluador 2: No está vacía
def eval_no_vacia(run: Run, example: Example) -> dict:
    """Verifica que la respuesta no está vacía."""
    output = run.outputs.get("respuesta", "")
    score = 1.0 if output.strip() else 0.0
    return {"key": "no_vacia", "score": score}


# Evaluador 3: Contiene palabras clave del esperado
def eval_keywords(run: Run, example: Example) -> dict:
    """Verifica si la respuesta contiene palabras clave relevantes."""
    output = run.outputs.get("respuesta", "").lower()
    expected = example.outputs.get("respuesta", "").lower()

    # Extraer palabras significativas (>4 caracteres) del esperado
    keywords = [w for w in expected.split() if len(w) > 4]

    if not keywords:
        return {"key": "keywords", "score": 1.0}

    hits = sum(1 for kw in keywords if kw in output)
    score = hits / len(keywords)
    return {"key": "keywords", "score": round(score, 2)}


# Evaluador 4: LLM-as-judge para correctitud
def eval_correctitud(run: Run, example: Example) -> dict:
    """Usa un LLM para evaluar la correctitud de la respuesta."""
    judge = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    pregunta = example.inputs["pregunta"]
    esperada = example.outputs.get("respuesta", "")
    obtenida = run.outputs.get("respuesta", "")

    evaluacion = judge.invoke(
        f"Evalúa la calidad de la respuesta obtenida comparada con la esperada.\n\n"
        f"Pregunta: {pregunta}\n"
        f"Respuesta esperada: {esperada}\n"
        f"Respuesta obtenida: {obtenida}\n\n"
        f"Criterios:\n"
        f"- ¿Es factualmente correcta?\n"
        f"- ¿Cubre los puntos principales?\n"
        f"- ¿Es clara y concisa?\n\n"
        f"Responde SOLO con un número decimal entre 0.0 y 1.0."
    )

    try:
        score = float(evaluacion.content.strip())
        score = max(0.0, min(1.0, score))
    except ValueError:
        score = 0.0

    return {"key": "correctitud", "score": score}


print("Evaluadores definidos:")
print("  1. eval_longitud - Longitud entre 20-500 chars")
print("  2. eval_no_vacia - Respuesta no vacía")
print("  3. eval_keywords - Palabras clave presentes")
print("  4. eval_correctitud - LLM-as-judge")
print()

# ============================================================
# 3. Experiment 1: GPT-4o-mini con prompt simple
# ============================================================
print("=" * 60)
print("3. EXPERIMENT 1: GPT-4o-mini + PROMPT SIMPLE")
print("=" * 60)

llm_mini = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt_simple = ChatPromptTemplate.from_template(
    "Responde brevemente: {pregunta}"
)
chain_simple = prompt_simple | llm_mini | StrOutputParser()


@traceable(name="app_prompt_simple")
def app_prompt_simple(inputs: dict) -> dict:
    resultado = chain_simple.invoke({"pregunta": inputs["pregunta"]})
    return {"respuesta": resultado}


results_1 = evaluate(
    app_prompt_simple,
    data=dataset_name,
    evaluators=[eval_longitud, eval_no_vacia, eval_keywords, eval_correctitud],
    experiment_prefix="exp1-mini-simple",
    max_concurrency=2,
)

print("Experiment 1 completado ✅")
print()

# ============================================================
# 4. Experiment 2: GPT-4o-mini con prompt detallado
# ============================================================
print("=" * 60)
print("4. EXPERIMENT 2: GPT-4o-mini + PROMPT DETALLADO")
print("=" * 60)

prompt_detallado = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un profesor de programación. "
     "Responde de forma clara, precisa y concisa. "
     "Incluye la definición y un detalle importante. "
     "Máximo 2-3 frases."),
    ("human", "{pregunta}")
])
chain_detallado = prompt_detallado | llm_mini | StrOutputParser()


@traceable(name="app_prompt_detallado")
def app_prompt_detallado(inputs: dict) -> dict:
    resultado = chain_detallado.invoke({"pregunta": inputs["pregunta"]})
    return {"respuesta": resultado}


results_2 = evaluate(
    app_prompt_detallado,
    data=dataset_name,
    evaluators=[eval_longitud, eval_no_vacia, eval_keywords, eval_correctitud],
    experiment_prefix="exp2-mini-detallado",
    max_concurrency=2,
)

print("Experiment 2 completado ✅")
print()

# ============================================================
# 5. Experiment 3: GPT-4o-mini con temperatura alta
# ============================================================
print("=" * 60)
print("5. EXPERIMENT 3: GPT-4o-mini + TEMPERATURA ALTA")
print("=" * 60)

llm_creative = ChatOpenAI(model="gpt-4o-mini", temperature=1.0)
chain_creative = prompt_detallado | llm_creative | StrOutputParser()


@traceable(name="app_temperatura_alta")
def app_temperatura_alta(inputs: dict) -> dict:
    resultado = chain_creative.invoke({"pregunta": inputs["pregunta"]})
    return {"respuesta": resultado}


results_3 = evaluate(
    app_temperatura_alta,
    data=dataset_name,
    evaluators=[eval_longitud, eval_no_vacia, eval_keywords, eval_correctitud],
    experiment_prefix="exp3-mini-temp-alta",
    max_concurrency=2,
)

print("Experiment 3 completado ✅")
print()

# ============================================================
# 6. Resumen de resultados
# ============================================================
print("=" * 60)
print("6. RESUMEN DE EXPERIMENTS")
print("=" * 60)

print("""
┌─────────────────────────────────────────────────────────────┐
│ Experiments ejecutados:                                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 1. exp1-mini-simple      → GPT-4o-mini + prompt básico      │
│ 2. exp2-mini-detallado   → GPT-4o-mini + prompt con sistema │
│ 3. exp3-mini-temp-alta   → GPT-4o-mini + temperature=1.0    │
│                                                              │
│ Evaluadores aplicados:                                       │
│   • longitud_ok    (heurístico)                              │
│   • no_vacia       (heurístico)                              │
│   • keywords       (heurístico)                              │
│   • correctitud    (LLM-as-judge)                            │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│ → Ve a smith.langchain.com → Datasets & Testing              │
│ → Selecciona el dataset 'tutorial-testing-conceptos'         │
│ → Compara los 3 experiments lado a lado                      │
└─────────────────────────────────────────────────────────────┘
""")

# ============================================================
# 7. Ejemplo de CI/CD - Verificar umbrales
# ============================================================
print("=" * 60)
print("7. VERIFICAR UMBRALES (EJEMPLO CI/CD)")
print("=" * 60)

# En CI/CD, ejecutarías un experiment y verificarías los scores
print("Ejemplo de verificación de umbrales en CI/CD:")
print("""
    results = evaluate(
        mi_app,
        data="regression-dataset",
        evaluators=[eval_correctitud],
        experiment_prefix=f"ci-{os.environ.get('COMMIT_SHA', 'local')}",
    )

    # Verificar umbral mínimo
    for result in results:
        scores = result.evaluation_results
        for score in scores:
            if score.key == "correctitud" and score.score < 0.80:
                raise AssertionError(
                    f"Score de correctitud ({score.score}) "
                    f"por debajo del umbral (0.80)"
                )
    
    print("✅ Todos los scores pasan el umbral")
""")
print()

# ============================================================
# 8. Limpiar dataset de tutorial
# ============================================================
print("=" * 60)
print("8. LIMPIAR")
print("=" * 60)

# Descomenta para eliminar el dataset
# client.delete_dataset(dataset_id=dataset.id)
# print(f"Dataset '{dataset_name}' eliminado")
print(f"Dataset '{dataset_name}' conservado para revisión en la UI")
print()

print("=" * 60)
print("✅ TESTING Y EXPERIMENTS COMPLETADO")
print("=" * 60)
print("Lo que aprendiste:")
print("  1. Crear datasets de testing con inputs/outputs esperados")
print("  2. Definir evaluadores heurísticos y LLM-as-judge")
print("  3. Ejecutar experiments con diferentes configuraciones")
print("  4. Comparar resultados entre experiments")
print("  5. Verificar umbrales para CI/CD")
