# Testing y Experiments - Explicación Detallada

## ¿Por qué testing en aplicaciones LLM?

Los tests tradicionales (unit tests, integration tests) **no son suficientes** para aplicaciones LLM porque:
- Las respuestas no son deterministas
- "Correcto" es subjetivo y contextual
- Un cambio de prompt puede mejorar un caso y empeorar otro
- Necesitas evaluar **calidad**, no solo **funcionalidad**

LangSmith resuelve esto con **experiments**: ejecutas tu app contra un dataset y mides la calidad con evaluadores.

---

## Tipos de testing en LLMs

| Tipo | Descripción | Herramienta |
|---|---|---|
| **Unit tests** | Verificar lógica determinista | pytest (tradicional) |
| **Evaluación offline** | Medir calidad contra un dataset | LangSmith experiments |
| **Comparación A/B** | Comparar configuraciones | LangSmith (lado a lado) |
| **Regression testing** | Detectar si un cambio empeoró algo | LangSmith (comparar experiments) |
| **Online evaluation** | Evaluar en producción | LangSmith + feedback |

---

## Experiments en LangSmith

Un **experiment** es una ejecución de tu aplicación contra todos los ejemplos de un dataset, con evaluadores que puntúan cada resultado.

### Flujo de un experiment

```
  Dataset (N ejemplos)
       │
       ▼
  ┌─────────────┐
  │ Tu App      │  → Se ejecuta N veces (una por ejemplo)
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │ Evaluadores │  → Puntúan cada resultado
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │ Resultados  │  → Scores, métricas agregadas
  └─────────────┘
```

### Estructura de resultados

```
Experiment: "test-gpt4o-mini-v2"
┌──────────────────┬───────────┬────────────┬──────────┐
│ Input            │ Output    │ Correctness│ Latencia │
├──────────────────┼───────────┼────────────┼──────────┤
│ ¿Qué es Python?  │ Python es │ 0.95       │ 1.2s     │
│ ¿Qué es una API? │ Una API.. │ 0.85       │ 0.8s     │
│ ¿Qué es SQL?     │ SQL es..  │ 0.90       │ 1.1s     │
├──────────────────┼───────────┼────────────┼──────────┤
│ PROMEDIO         │           │ 0.90       │ 1.03s    │
└──────────────────┴───────────┴────────────┴──────────┘
```

---

## Evaluadores incorporados

LangSmith proporciona evaluadores predefinidos:

### Evaluadores de texto

| Evaluador | Qué mide | Score |
|---|---|---|
| **Exact match** | Coincidencia exacta con el esperado | 0 o 1 |
| **Contains** | Si el output contiene cierto texto | 0 o 1 |
| **String distance** | Distancia de edición entre strings | 0.0 - 1.0 |
| **Regex match** | Si el output cumple un patrón regex | 0 o 1 |

### Evaluadores LLM-as-judge

| Evaluador | Qué mide |
|---|---|
| **Correctness** | ¿Es la respuesta factualmente correcta? |
| **Relevance** | ¿Responde a la pregunta planteada? |
| **Helpfulness** | ¿Es útil para el usuario? |
| **Harmfulness** | ¿Contiene contenido dañino? |
| **Coherence** | ¿Es coherente y bien estructurada? |

---

## Comparar Experiments

La comparación de experiments es la funcionalidad más potente para testing:

### Caso de uso: Comparar modelos

```python
# Experiment 1: GPT-4o-mini
evaluate(app_mini, data="mi-dataset", experiment_prefix="gpt4o-mini")

# Experiment 2: GPT-4o
evaluate(app_4o, data="mi-dataset", experiment_prefix="gpt4o")

# Experiment 3: Claude Sonnet
evaluate(app_claude, data="mi-dataset", experiment_prefix="claude-sonnet")
```

### Caso de uso: Comparar prompts

```python
# Experiment 1: Prompt v1
evaluate(app_v1, data="mi-dataset", experiment_prefix="prompt-v1")

# Experiment 2: Prompt v2 (más detallado)
evaluate(app_v2, data="mi-dataset", experiment_prefix="prompt-v2")
```

### Caso de uso: Comparar temperaturas

```python
# Experiment 1: temperature=0
evaluate(app_t0, data="mi-dataset", experiment_prefix="temp-0")

# Experiment 2: temperature=0.7
evaluate(app_t07, data="mi-dataset", experiment_prefix="temp-0.7")
```

En la UI, puedes ver los resultados **lado a lado** con diff de scores.

---

## Evaluadores custom

### Evaluador basado en reglas

```python
def evaluar_formato(run, example) -> dict:
    """Verifica que la respuesta cumple con el formato esperado."""
    output = run.outputs.get("respuesta", "")

    checks = {
        "no_vacio": len(output.strip()) > 0,
        "longitud_ok": 10 <= len(output) <= 1000,
        "no_error": "error" not in output.lower(),
    }

    score = sum(checks.values()) / len(checks)
    return {"key": "formato", "score": score}
```

### Evaluador compuesto

```python
def evaluar_completo(run, example) -> dict:
    """Combina múltiples criterios en un score único."""
    output = run.outputs.get("respuesta", "")
    expected = example.outputs.get("respuesta", "")

    # Criterio 1: Longitud similar
    len_ratio = min(len(output), len(expected)) / max(len(output), len(expected)) if expected else 0

    # Criterio 2: Palabras clave presentes
    keywords = expected.lower().split()
    keyword_hits = sum(1 for kw in keywords if kw in output.lower())
    keyword_score = keyword_hits / len(keywords) if keywords else 0

    # Score combinado
    score = (len_ratio * 0.3) + (keyword_score * 0.7)
    return {"key": "evaluacion_completa", "score": score}
```

---

## CI/CD con LangSmith

Puedes integrar evaluaciones en tu pipeline de CI/CD:

```python
# En tu script de CI
results = evaluate(
    mi_app,
    data="regression-dataset",
    evaluators=[correctitud, formato],
    experiment_prefix=f"ci-{commit_sha}",
)

# Verificar que los scores cumplen el umbral mínimo
avg_score = results.aggregate_metrics["correctitud"]["mean"]
assert avg_score > 0.85, f"Score demasiado bajo: {avg_score}"
```

---

## Mejores prácticas

1. **Crea datasets representativos**: Incluye casos fáciles, difíciles y edge cases
2. **Usa múltiples evaluadores**: Combina heurísticos y LLM-as-judge
3. **Ejecuta experiments antes de deploy**: Como un "test suite" para tu LLM app
4. **Compara siempre con baseline**: No evalúes en vacío, compara con la versión actual
5. **Versiona tus datasets**: Agrega ejemplos cuando encuentres fallos en producción
6. **Automatiza en CI/CD**: Ejecuta evaluaciones en cada PR o deploy

---

## Código de ejemplo

Revisa `main.py` en esta carpeta para ver ejemplos ejecutables de:
1. Crear un dataset de testing
2. Definir múltiples evaluadores
3. Ejecutar experiments con diferentes configuraciones
4. Comparar modelos (GPT-4o-mini vs GPT-4o)
5. Comparar prompts (v1 vs v2)
6. Evaluar con umbrales de calidad
