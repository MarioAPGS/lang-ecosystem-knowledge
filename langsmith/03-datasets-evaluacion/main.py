"""
Datasets y Evaluación en LangSmith - Ejemplos ejecutables
===========================================================
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

client = Client()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ============================================================
# 1. Crear un Dataset
# ============================================================
print("=" * 60)
print("1. CREAR UN DATASET")
print("=" * 60)

dataset_name = "tutorial-preguntas-python"

# Verificar si ya existe y eliminarlo para empezar limpio
try:
    existing = client.read_dataset(dataset_name=dataset_name)
    client.delete_dataset(dataset_id=existing.id)
    print(f"Dataset '{dataset_name}' existente eliminado")
except Exception:
    pass

# Crear el dataset
dataset = client.create_dataset(
    dataset_name=dataset_name,
    description="Preguntas básicas sobre Python para evaluar respuestas del LLM"
)
print(f"Dataset creado: {dataset.name}")
# Ejemplo salida → Dataset creado: tutorial-preguntas-python
print(f"ID: {dataset.id}")
print()

# ============================================================
# 2. Agregar ejemplos al Dataset
# ============================================================
print("=" * 60)
print("2. AGREGAR EJEMPLOS AL DATASET")
print("=" * 60)

# Agregar múltiples ejemplos de una vez
client.create_examples(
    inputs=[
        {"pregunta": "¿Qué es una lista en Python?"},
        {"pregunta": "¿Qué es un diccionario en Python?"},
        {"pregunta": "¿Qué es una tupla en Python?"},
        {"pregunta": "¿Qué es un set en Python?"},
        {"pregunta": "¿Qué es una función lambda en Python?"},
    ],
    outputs=[
        {"respuesta": "Una lista es una colección ordenada y mutable de elementos que puede contener datos de diferentes tipos."},
        {"respuesta": "Un diccionario es una colección de pares clave-valor, donde cada clave es única y se usa para acceder a su valor asociado."},
        {"respuesta": "Una tupla es una colección ordenada e inmutable de elementos, similar a una lista pero que no puede modificarse después de crearse."},
        {"respuesta": "Un set es una colección desordenada de elementos únicos, que no permite duplicados."},
        {"respuesta": "Una función lambda es una función anónima de una sola expresión, definida con la palabra clave lambda."},
    ],
    dataset_id=dataset.id,
)

# Verificar cuántos ejemplos tiene
examples = list(client.list_examples(dataset_id=dataset.id))
print(f"Ejemplos agregados: {len(examples)}")
# Ejemplo salida → Ejemplos agregados: 5

for ex in examples:
    print(f"  - Input: {ex.inputs['pregunta'][:50]}...")
print()

# ============================================================
# 3. Agregar un ejemplo individual
# ============================================================
print("=" * 60)
print("3. AGREGAR EJEMPLO INDIVIDUAL")
print("=" * 60)

client.create_example(
    inputs={"pregunta": "¿Qué es una list comprehension en Python?"},
    outputs={"respuesta": "Una list comprehension es una forma concisa de crear listas usando una expresión dentro de corchetes."},
    dataset_id=dataset.id,
)

examples = list(client.list_examples(dataset_id=dataset.id))
print(f"Total de ejemplos ahora: {len(examples)}")
# Ejemplo salida → Total de ejemplos ahora: 6
print()

# ============================================================
# 4. Definir la aplicación a evaluar
# ============================================================
print("=" * 60)
print("4. DEFINIR LA APLICACIÓN A EVALUAR")
print("=" * 60)

from langsmith import traceable


@traceable(name="chatbot_python")
def chatbot_python(inputs: dict) -> dict:
    """
    La aplicación que queremos evaluar.
    Recibe un dict con 'pregunta' y devuelve un dict con 'respuesta'.
    """
    response = llm.invoke(
        f"Responde de forma breve y clara: {inputs['pregunta']}"
    )
    return {"respuesta": response.content}


# Probar que funciona
test = chatbot_python({"pregunta": "¿Qué es una lista en Python?"})
print(f"Test: {test['respuesta'][:80]}...")
# Ejemplo salida → Test: Una lista en Python es una colección ordenada y mutable que puede contener...
print()

# ============================================================
# 5. Definir evaluadores
# ============================================================
print("=" * 60)
print("5. DEFINIR EVALUADORES")
print("=" * 60)

from langsmith.schemas import Example, Run


# Evaluador 1: Heurístico - ¿La respuesta menciona "Python"?
def menciona_python(run: Run, example: Example) -> dict:
    """Verifica si la respuesta menciona Python."""
    prediction = run.outputs.get("respuesta", "")
    score = 1.0 if "python" in prediction.lower() else 0.0
    return {"key": "menciona_python", "score": score}


# Evaluador 2: Heurístico - ¿La respuesta tiene longitud razonable?
def longitud_adecuada(run: Run, example: Example) -> dict:
    """Verifica si la respuesta tiene entre 20 y 500 caracteres."""
    prediction = run.outputs.get("respuesta", "")
    length = len(prediction)
    score = 1.0 if 20 <= length <= 500 else 0.0
    return {"key": "longitud_adecuada", "score": score}


# Evaluador 3: LLM-as-judge - ¿La respuesta es semánticamente correcta?
def correctitud_llm(run: Run, example: Example) -> dict:
    """Usa GPT para evaluar si la respuesta es correcta."""
    judge = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    pregunta = example.inputs["pregunta"]
    respuesta_esperada = example.outputs.get("respuesta", "")
    respuesta_obtenida = run.outputs.get("respuesta", "")

    evaluacion = judge.invoke(
        f"Evalúa si la respuesta obtenida es semánticamente equivalente a la esperada.\n\n"
        f"Pregunta: {pregunta}\n"
        f"Respuesta esperada: {respuesta_esperada}\n"
        f"Respuesta obtenida: {respuesta_obtenida}\n\n"
        f"Responde SOLO con un número decimal entre 0.0 y 1.0, donde:\n"
        f"- 1.0 = completamente correcta\n"
        f"- 0.5 = parcialmente correcta\n"
        f"- 0.0 = incorrecta"
    )

    try:
        score = float(evaluacion.content.strip())
        score = max(0.0, min(1.0, score))  # Clamp entre 0 y 1
    except ValueError:
        score = 0.0

    return {"key": "correctitud_llm", "score": score}


print("Evaluadores definidos:")
print("  1. menciona_python (heurístico)")
print("  2. longitud_adecuada (heurístico)")
print("  3. correctitud_llm (LLM-as-judge)")
print()

# ============================================================
# 6. Ejecutar evaluación (Experiment)
# ============================================================
print("=" * 60)
print("6. EJECUTAR EVALUACIÓN (EXPERIMENT)")
print("=" * 60)

from langsmith import evaluate

results = evaluate(
    chatbot_python,
    data=dataset_name,
    evaluators=[menciona_python, longitud_adecuada, correctitud_llm],
    experiment_prefix="tutorial-eval-v1",
    max_concurrency=2,  # Limitar concurrencia para no saturar la API
)

print("Evaluación completada ✅")
print(f"→ Ve a smith.langchain.com para ver los resultados detallados")
print()

# ============================================================
# 7. Listar datasets existentes
# ============================================================
print("=" * 60)
print("7. LISTAR DATASETS")
print("=" * 60)

datasets = list(client.list_datasets())
print(f"Datasets en tu cuenta: {len(datasets)}")
for ds in datasets[:10]:
    example_count = ds.example_count if hasattr(ds, 'example_count') else "?"
    print(f"  - {ds.name} ({example_count} ejemplos)")
print()

# ============================================================
# 8. Limpiar - Eliminar dataset de tutorial
# ============================================================
print("=" * 60)
print("8. LIMPIAR DATASET DE TUTORIAL")
print("=" * 60)

# Descomenta la siguiente línea si quieres eliminar el dataset
# client.delete_dataset(dataset_id=dataset.id)
# print(f"Dataset '{dataset_name}' eliminado")
print(f"Dataset '{dataset_name}' conservado para revisión en la UI")
print("→ Puedes eliminarlo manualmente desde smith.langchain.com")
print()

print("=" * 60)
print("✅ EVALUACIÓN COMPLETADA")
print("=" * 60)
print("Revisa smith.langchain.com → Datasets & Testing para ver:")
print("  - El dataset con los ejemplos")
print("  - El experiment con los scores de cada evaluador")
print("  - La tabla comparativa de resultados")
