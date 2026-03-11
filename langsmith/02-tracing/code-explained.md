# Tracing - Explicación Detallada

## ¿Qué es el Tracing?

El **tracing** es la funcionalidad central de LangSmith. Captura una **traza completa** de cada ejecución de tu aplicación, mostrando:
- Qué inputs recibió cada paso
- Qué outputs generó
- Cuánto tiempo tardó
- Cuántos tokens consumió
- Si hubo errores o excepciones

---

## Anatomía de un Trace

Un trace tiene una estructura de **árbol**:

```
Trace (Run padre)
├── Prompt Template (Run hijo)
│   ├── Input: {"tema": "Python"}
│   └── Output: [SystemMessage, HumanMessage]
├── ChatOpenAI (Run hijo)
│   ├── Input: [messages]
│   ├── Output: AIMessage("Python es...")
│   ├── Tokens: 45 input, 23 output
│   └── Latencia: 1.2s
└── StrOutputParser (Run hijo)
    ├── Input: AIMessage("Python es...")
    └── Output: "Python es..."
```

### Tipos de Runs

| Tipo | Icono en UI | Descripción |
|---|---|---|
| **Chain** | 🔗 | Cadena o función compuesta |
| **LLM** | 🤖 | Llamada a un modelo de lenguaje |
| **Tool** | 🔧 | Invocación de una herramienta |
| **Retriever** | 🔍 | Búsqueda en un vectorstore |
| **Prompt** | 📝 | Formateo de un prompt template |
| **Parser** | 📄 | Parsing del output |

---

## Tracing Automático

### Con LangChain/LangGraph
Solo necesitas las variables de entorno configuradas. **Todo se tracea automáticamente**:

```python
# Cualquier llamada de LangChain genera un trace
llm = ChatOpenAI(model="gpt-4o-mini")
response = llm.invoke("Hola")  # → Trace automático
```

### Qué se captura automáticamente
- **Inputs y outputs** de cada componente
- **Tokens** consumidos (input, output, total)
- **Latencia** de cada paso
- **Modelo** utilizado y sus parámetros
- **Errores** y stack traces si algo falla

---

## Tracing Manual con `@traceable`

### ¿Cuándo usar `@traceable`?
- Funciones Python puras (no LangChain)
- Lógica de negocio que quieres monitorizar
- Funciones que combinan múltiples pasos

### Uso básico

```python
from langsmith import traceable

@traceable
def mi_funcion(x: int) -> int:
    return x * 2

resultado = mi_funcion(5)
# → Aparece como trace con input=5, output=10
```

### Personalizar el nombre del trace

```python
@traceable(name="calcular_descuento")
def calcular(precio: float, porcentaje: float) -> float:
    return precio * (1 - porcentaje / 100)
```

### Especificar el tipo de run

```python
@traceable(run_type="tool")
def buscar_en_db(query: str) -> list:
    # Se muestra con icono de herramienta en la UI
    return db.search(query)
```

### Tipos de run disponibles para `@traceable`

| run_type | Uso |
|---|---|
| `"chain"` | Default. Para funciones generales |
| `"tool"` | Para herramientas/utilidades |
| `"llm"` | Para wrappers de modelos |
| `"retriever"` | Para funciones de búsqueda |

---

## Metadata y Tags

### Tags
Etiquetas para **filtrar** traces en la UI:

```python
@traceable(tags=["produccion", "chatbot-v2"])
def mi_chatbot(pregunta: str) -> str:
    ...
```

### Metadata
Información adicional como pares clave-valor:

```python
@traceable(metadata={"version": "2.1", "equipo": "backend"})
def procesar(data: dict) -> dict:
    ...
```

### Tags y metadata en LangChain

```python
from langchain_core.runnables import RunnableConfig

config = RunnableConfig(
    tags=["test-A", "gpt4"],
    metadata={"experiment_id": "exp-001"},
    run_name="mi-cadena-custom",  # Nombre personalizado del run
)

response = chain.invoke({"pregunta": "Hola"}, config=config)
```

---

## Runs anidados (Nesting)

Cuando una función `@traceable` llama a otra función `@traceable` o a un componente de LangChain, los traces se **anidan automáticamente**:

```python
@traceable(name="app_principal")
def app(pregunta: str) -> str:
    # Este LLM call aparece como hijo de "app_principal"
    response = llm.invoke(pregunta)
    
    # Esta función también aparece como hija
    resultado = post_procesar(response.content)
    return resultado

@traceable(name="post_procesamiento")
def post_procesar(texto: str) -> str:
    return texto.strip().lower()
```

Resultado en LangSmith:
```
app_principal
├── ChatOpenAI
└── post_procesamiento
```

---

## Filtrar y buscar traces en la UI

En la interfaz de LangSmith puedes:

| Acción | Cómo |
|---|---|
| Filtrar por proyecto | Selector en la barra superior |
| Filtrar por tags | `tag:produccion` en la barra de búsqueda |
| Filtrar por metadata | `metadata.version:2.1` |
| Filtrar por nombre | `name:mi-cadena-custom` |
| Filtrar por estado | `status:error` o `status:success` |
| Filtrar por fecha | Selector de rango de fechas |
| Filtrar por latencia | `latency > 2s` |
| Filtrar por tokens | `total_tokens > 1000` |

---

## Feedback en Runs

Puedes agregar **puntuaciones** a los runs para anotar calidad:

```python
from langsmith import Client

client = Client()

# Agregar feedback a un run específico
client.create_feedback(
    run_id="...",  # ID del run (visible en la UI)
    key="calidad",
    score=0.9,
    comment="Respuesta precisa y concisa"
)
```

### Tipos de feedback

| Key | Tipo | Uso |
|---|---|---|
| `"correctness"` | score (0-1) | ¿Es correcta la respuesta? |
| `"helpfulness"` | score (0-1) | ¿Es útil la respuesta? |
| `"thumbs_up"` | score (0 o 1) | Like/dislike del usuario |
| Custom | cualquiera | Cualquier métrica que definas |

---

## Código de ejemplo

Revisa `main.py` en esta carpeta para ver ejemplos ejecutables de:
1. Trace automático con LangChain
2. Trace manual con `@traceable`
3. Runs anidados (funciones que llaman funciones)
4. Metadata y tags en traces
5. Nombrar traces personalizados
6. Diferentes run_types
