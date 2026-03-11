# Datasets y Evaluación - Explicación Detallada

## ¿Qué es un Dataset en LangSmith?

Un **dataset** es una colección de **ejemplos** (pares input/output) que representan el comportamiento esperado de tu aplicación. Son la base para evaluar si tu aplicación LLM funciona correctamente.

```
Dataset: "preguntas-python"
┌────────────────────────────────────┬────────────────────────────────────┐
│ Input                              │ Output esperado                    │
├────────────────────────────────────┼────────────────────────────────────┤
│ {"pregunta": "¿Qué es una lista?"}│ {"respuesta": "Colección ordenada"}│
│ {"pregunta": "¿Qué es un dict?"}  │ {"respuesta": "Pares clave-valor"} │
│ {"pregunta": "¿Qué es un set?"}   │ {"respuesta": "Colección sin dupl"}│
└────────────────────────────────────┴────────────────────────────────────┘
```

---

## ¿Por qué son importantes los Datasets?

| Sin datasets | Con datasets |
|---|---|
| "Creo que funciona bien" | "Mi app acierta el 87% de las veces" |
| Pruebas manuales ad-hoc | Evaluaciones reproducibles |
| No sabes si un cambio rompió algo | Detectas regresiones automáticamente |
| Comparación subjetiva de modelos | Métricas objetivas entre modelos |

---

## Crear un Dataset

### Desde código (SDK)

```python
from langsmith import Client

client = Client()

# Crear el dataset
dataset = client.create_dataset(
    dataset_name="preguntas-python",
    description="Preguntas básicas sobre Python para evaluar el chatbot"
)

# Agregar ejemplos
client.create_examples(
    inputs=[
        {"pregunta": "¿Qué es una lista?"},
        {"pregunta": "¿Qué es un diccionario?"},
    ],
    outputs=[
        {"respuesta": "Una colección ordenada y mutable de elementos"},
        {"respuesta": "Una colección de pares clave-valor"},
    ],
    dataset_id=dataset.id,
)
```

### Desde la UI
1. Ve a la sección **Datasets** en LangSmith
2. Clic en **New Dataset**
3. Puedes subir un CSV/JSON o agregar ejemplos manualmente

### Desde traces existentes
1. En un trace, haz clic en **Add to Dataset**
2. Selecciona el dataset destino
3. El input/output del run se agregan como ejemplo

---

## Evaluadores (Evaluators)

Un **evaluador** es una función que puntúa el output de tu aplicación comparándolo con el output esperado.

### Tipos de evaluadores

| Tipo | Descripción | Ejemplo |
|---|---|---|
| **Heurístico** | Reglas programáticas | Contiene palabra clave, longitud correcta |
| **LLM-as-judge** | Un LLM evalúa la calidad | "¿Es esta respuesta correcta?" |
| **Distancia** | Similitud entre textos | Edit distance, cosine similarity |
| **Custom** | Tu propia lógica | Cualquier función Python |

### Evaluador heurístico

```python
from langsmith.schemas import Example, Run

def contiene_python(run: Run, example: Example) -> dict:
    """Verifica si la respuesta menciona Python."""
    prediction = run.outputs.get("respuesta", "")
    return {
        "key": "menciona_python",
        "score": 1.0 if "python" in prediction.lower() else 0.0,
    }
```

### Evaluador LLM-as-judge

```python
from langchain_openai import ChatOpenAI

def evaluar_correctitud(run: Run, example: Example) -> dict:
    """Usa un LLM para evaluar si la respuesta es correcta."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    pregunta = example.inputs["pregunta"]
    respuesta_esperada = example.outputs["respuesta"]
    respuesta_obtenida = run.outputs["respuesta"]
    
    evaluacion = llm.invoke(
        f"Evalúa si la respuesta obtenida es equivalente a la esperada.\n"
        f"Pregunta: {pregunta}\n"
        f"Esperada: {respuesta_esperada}\n"
        f"Obtenida: {respuesta_obtenida}\n"
        f"Responde solo con un número del 0 al 1."
    )
    
    return {
        "key": "correctitud",
        "score": float(evaluacion.content.strip()),
    }
```

---

## Ejecutar una Evaluación (Experiment)

Un **experiment** ejecuta tu aplicación contra todos los ejemplos de un dataset y calcula las métricas:

```python
from langsmith import evaluate

def mi_app(inputs: dict) -> dict:
    """La función que quieres evaluar."""
    response = llm.invoke(inputs["pregunta"])
    return {"respuesta": response.content}

# Ejecutar evaluación
results = evaluate(
    mi_app,
    data="preguntas-python",
    evaluators=[contiene_python, evaluar_correctitud],
    experiment_prefix="test-v1",
)
```

### ¿Qué devuelve `evaluate()`?

Un objeto con:
- **Resultados por ejemplo**: Score de cada evaluador para cada input
- **Métricas agregadas**: Promedio, mediana, etc.
- **Link al experiment**: URL para ver los resultados en la UI

---

## Comparar Experiments

Puedes ejecutar múltiples experiments con diferentes configuraciones y compararlos:

```python
# Experiment 1: GPT-4o-mini
results_mini = evaluate(
    mi_app_mini,
    data="preguntas-python",
    experiment_prefix="gpt4o-mini",
)

# Experiment 2: GPT-4o
results_4o = evaluate(
    mi_app_4o,
    data="preguntas-python",
    experiment_prefix="gpt4o",
)
```

En la UI de LangSmith puedes ver una **tabla comparativa** con los scores de cada experiment lado a lado.

---

## Gestión de Datasets

### Listar datasets

```python
datasets = list(client.list_datasets())
for ds in datasets:
    print(f"{ds.name} - {ds.example_count} ejemplos")
```

### Agregar ejemplos

```python
client.create_example(
    inputs={"pregunta": "¿Qué es una tupla?"},
    outputs={"respuesta": "Una colección ordenada e inmutable"},
    dataset_id=dataset.id,
)
```

### Actualizar un ejemplo

```python
client.update_example(
    example_id="...",
    outputs={"respuesta": "Nueva respuesta corregida"},
)
```

### Eliminar un dataset

```python
client.delete_dataset(dataset_id=dataset.id)
```

---

## Código de ejemplo

Revisa `main.py` en esta carpeta para ver ejemplos ejecutables de:
1. Crear un dataset desde código
2. Agregar ejemplos al dataset
3. Definir evaluadores heurísticos
4. Definir evaluadores LLM-as-judge
5. Ejecutar un experiment
6. Listar y gestionar datasets
