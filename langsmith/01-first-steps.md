# LangSmith - Guía de Iniciación

## ¿Qué es LangSmith?

LangSmith es la **plataforma de observabilidad, depuración, testing y evaluación** del ecosistema LangChain. Permite visualizar cada paso que ocurre dentro de tus cadenas, agentes y grafos — desde el prompt enviado hasta la respuesta recibida, pasando por cada llamada a herramientas, retrieval, y más.

> **En resumen:** LangSmith es el "debugger" y "monitor" de tus aplicaciones LLM. Te muestra exactamente qué está pasando, cuánto cuesta, y te permite evaluar si tus respuestas son buenas.

---

## ¿Por qué necesitas LangSmith?

Cuando construyes aplicaciones con LLMs, surgen problemas difíciles de diagnosticar:

| Problema | Sin LangSmith | Con LangSmith |
|---|---|---|
| ¿Qué prompt se envió al modelo? | Tienes que hacer print() manual | Ves el prompt exacto en la UI |
| ¿Por qué la respuesta fue mala? | No sabes qué paso falló | Ves cada paso del trace completo |
| ¿Cuánto cuesta cada llamada? | Calculas manualmente | Dashboard con costes automáticos |
| ¿Mi agente eligió la herramienta correcta? | Difícil de rastrear | Ves el árbol de decisiones completo |
| ¿Mis cambios mejoraron las respuestas? | Pruebas manuales | Evaluaciones automáticas con datasets |
| ¿Cómo funciona en producción? | Logs básicos | Monitoreo con métricas y alertas |

---

## Arquitectura de LangSmith

```
┌─────────────────────────────────────────────────────────────┐
│                        LangSmith                             │
├──────────────┬──────────────┬────────────┬──────────────────┤
│              │              │            │                    │
│   Tracing    │  Datasets &  │  Prompt    │   Monitoreo       │
│              │  Evaluación  │  Hub       │   Producción      │
│              │              │            │                    │
│ • Runs       │ • Datasets   │ • Guardar  │ • Dashboards      │
│ • Traces     │ • Evaluators │ • Versionar│ • Métricas        │
│ • Feedback   │ • Experiments│ • Compartir│ • Alertas         │
│ • Metadata   │ • Scores     │ • Pull/Push│ • Costes          │
│              │              │            │                    │
└──────────────┴──────────────┴────────────┴──────────────────┘
                          ▲
                          │ SDK / API
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                    Tu Aplicación                             │
│  (LangChain, LangGraph, o cualquier código Python)          │
└─────────────────────────────────────────────────────────────┘
```

---

## Conceptos Clave

### 1. Trace
Un **trace** es la historia completa de una ejecución. Si tienes una cadena `prompt → LLM → parser`, el trace muestra cada uno de esos pasos con sus inputs, outputs, duración y tokens.

### 2. Run
Cada paso dentro de un trace es un **run**. Los runs pueden ser:
- **LLM Run**: Llamada a un modelo de lenguaje
- **Chain Run**: Ejecución de una cadena
- **Tool Run**: Invocación de una herramienta
- **Retriever Run**: Búsqueda en un vectorstore

### 3. Project
Un **project** agrupa traces relacionados. Por ejemplo, puedes tener un project para desarrollo y otro para producción.

### 4. Dataset
Colección de pares input/output esperados que se usan para evaluar y testear tu aplicación.

### 5. Experiment
Una ejecución de tu aplicación contra un dataset, con métricas de evaluación calculadas automáticamente.

### 6. Feedback
Puntuaciones y anotaciones sobre los outputs (pueden ser automáticas o humanas).

---

## Instalación

```bash
# SDK de LangSmith
pip install langsmith

# LangChain (ya incluye integración con LangSmith)
pip install langchain langchain-openai

# Utilidades
pip install python-dotenv
```

---

## Configuración

LangSmith se configura con variables de entorno:

```bash
# Activar tracing (obligatorio)
export LANGSMITH_TRACING=true

# API key de LangSmith (obtener en https://smith.langchain.com/settings)
export LANGSMITH_API_KEY="lsv2_pt_..."

# Nombre del proyecto (opcional, default: "default")
export LANGSMITH_PROJECT="mi-proyecto"

# Endpoint (opcional, solo si usas LangSmith self-hosted)
# export LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
```

```python
# O configura desde Python
import os
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = "lsv2_pt_..."
os.environ["LANGSMITH_PROJECT"] = "mi-proyecto"
```

> **Importante:** Con solo configurar estas variables de entorno, **todas las llamadas de LangChain/LangGraph se tracean automáticamente**. No necesitas cambiar tu código.

---

## Conceptos Clave - Lecciones

Cada concepto tiene su **carpeta dedicada** con explicación detallada (`code-explained.md`) y código ejecutable (`main.py`):

| # | Concepto | Carpeta | Descripción |
|---|---|---|---|
| 1 | [Configuración y Setup](01-configuracion-setup/) | `01-configuracion-setup/` | API keys, SDK, primeros traces automáticos |
| 2 | [Tracing](02-tracing/) | `02-tracing/` | Runs, traces, decorador @traceable, metadata |
| 3 | [Datasets y Evaluación](03-datasets-evaluacion/) | `03-datasets-evaluacion/` | Crear datasets, evaluators, experiments |
| 4 | [Prompts Hub](04-prompts-hub/) | `04-prompts-hub/` | Guardar, versionar y compartir prompts |
| 5 | [Monitoreo en Producción](05-monitoreo-produccion/) | `05-monitoreo-produccion/` | Dashboards, métricas, costes, alertas |
| 6 | [Testing y Experiments](06-testing-experiments/) | `06-testing-experiments/` | Tests automáticos, comparar modelos, CI/CD |

---

### 1. Configuración y Setup

Solo necesitas 3 cosas para empezar:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Con estas variables, todo se tracea automáticamente
# LANGSMITH_TRACING=true
# LANGSMITH_API_KEY=lsv2_pt_...
# LANGSMITH_PROJECT=mi-proyecto

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
response = llm.invoke("¿Qué es LangSmith?")
# → Este trace aparece automáticamente en smith.langchain.com
```

### 2. Tracing

Puedes tracear **cualquier función Python** con el decorador `@traceable`:

```python
from langsmith import traceable

@traceable
def mi_funcion(pregunta: str) -> str:
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(pregunta)
    return response.content

# Esta ejecución aparece como un trace en LangSmith
resultado = mi_funcion("¿Qué es Python?")
```

### 3. Datasets y Evaluación

Crea datasets para evaluar tu aplicación de forma sistemática:

```python
from langsmith import Client

client = Client()

# Crear un dataset
dataset = client.create_dataset("preguntas-python")

# Agregar ejemplos
client.create_examples(
    inputs=[
        {"pregunta": "¿Qué es una lista?"},
        {"pregunta": "¿Qué es un diccionario?"},
    ],
    outputs=[
        {"respuesta": "Una colección ordenada de elementos"},
        {"respuesta": "Una colección de pares clave-valor"},
    ],
    dataset_id=dataset.id,
)
```

### 4. Prompts Hub

Guarda y versiona tus prompts en LangSmith:

```python
from langsmith import Client

client = Client()

# Subir un prompt
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un experto en {tema}."),
    ("human", "{pregunta}")
])

client.push_prompt("mi-prompt", object=prompt)

# Descargar un prompt (desde cualquier lugar)
prompt = client.pull_prompt("mi-prompt")
```

### 5. Monitoreo en Producción

LangSmith recopila métricas automáticamente:
- **Latencia** de cada paso y del trace completo
- **Tokens** consumidos (input y output)
- **Costes** estimados por proveedor
- **Tasa de errores** y excepciones
- **Feedback** de usuarios

### 6. Testing y Experiments

Ejecuta evaluaciones automáticas comparando diferentes configuraciones:

```python
from langsmith import evaluate

def mi_app(inputs: dict) -> dict:
    # Tu lógica de aplicación
    response = llm.invoke(inputs["pregunta"])
    return {"respuesta": response.content}

# Evaluar contra un dataset
results = evaluate(
    mi_app,
    data="preguntas-python",
    evaluators=[correctness, relevance],
    experiment_prefix="test-gpt4o-mini",
)
```

---

## Flujo Típico con LangSmith

```
  1. Configurar variables de entorno (API key + tracing)
  2. Desarrollar tu aplicación (LangChain/LangGraph/Python)
  3. Los traces se envían automáticamente a LangSmith
  4. Inspeccionar traces en la UI para depurar
  5. Crear datasets con inputs/outputs esperados
  6. Ejecutar evaluaciones automáticas
  7. Comparar experiments (modelos, prompts, configs)
  8. Monitorizar en producción con dashboards
```

---

## Próximos Pasos Sugeridos

1. **Crear tu cuenta** en [smith.langchain.com](https://smith.langchain.com/) y obtener tu API key
2. **Configurar tracing** y ejecutar tu primera cadena de LangChain (Lección 1)
3. **Explorar traces** en la UI para entender qué pasa internamente (Lección 2)
4. **Crear un dataset** con preguntas y respuestas esperadas (Lección 3)
5. **Versionar tus prompts** en el Prompt Hub (Lección 4)
6. **Monitorizar costes** y latencia de tu aplicación (Lección 5)
7. **Automatizar testing** con experiments y evaluadores (Lección 6)

---

> **Tip:** LangSmith es gratuito para uso personal con límites generosos. Para equipos y producción, existen planes de pago con más capacidad.
