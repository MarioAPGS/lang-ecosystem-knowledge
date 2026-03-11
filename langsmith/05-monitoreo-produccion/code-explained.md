# Monitoreo en Producción - Explicación Detallada

## ¿Por qué monitorizar aplicaciones LLM?

Las aplicaciones LLM tienen desafíos únicos que no existen en software tradicional:
- **Costes variables**: Cada llamada al LLM tiene un coste en tokens
- **Latencia impredecible**: El tiempo de respuesta varía según la carga del proveedor
- **Calidad no determinista**: La misma pregunta puede generar respuestas diferentes
- **Errores silenciosos**: Una respuesta incorrecta no lanza excepción

LangSmith proporciona herramientas para monitorizar todos estos aspectos en producción.

---

## Dashboard de LangSmith

El dashboard muestra métricas agregadas de tu proyecto:

```
┌───────────────────────────────────────────────────┐
│                 Dashboard                          │
├───────────┬───────────┬───────────┬───────────────┤
│  Traces   │  Latencia │  Tokens   │  Errores      │
│  1,234    │  1.2s avg │  45K tot  │  2.1% rate    │
│  ↑12%     │  ↓0.3s    │  ↑8%      │  ↓0.5%        │
├───────────┴───────────┴───────────┴───────────────┤
│                                                    │
│  📊 Latencia (últimas 24h)                        │
│  ████████████████████░░░░  p50: 0.8s              │
│  ██████████████████████░░  p95: 2.1s              │
│  ████████████████████████  p99: 4.5s              │
│                                                    │
│  💰 Costes (últimos 7 días)                       │
│  Lun: $2.30 | Mar: $1.80 | Mie: $3.10 | ...      │
│                                                    │
└───────────────────────────────────────────────────┘
```

---

## Métricas principales

### 1. Latencia

| Métrica | Descripción | Uso |
|---|---|---|
| **p50** | Mediana de latencia | Experiencia típica del usuario |
| **p95** | Percentil 95 | Peor caso "normal" |
| **p99** | Percentil 99 | Outliers y problemas |
| **Promedio** | Media aritmética | Visión general |

### 2. Tokens

| Métrica | Descripción |
|---|---|
| **Input tokens** | Tokens enviados al modelo (prompt) |
| **Output tokens** | Tokens generados por el modelo (respuesta) |
| **Total tokens** | Suma de input + output |
| **Tokens por trace** | Promedio de tokens por ejecución completa |

### 3. Costes

LangSmith estima los costes basándose en:
- El modelo utilizado (GPT-4o vs GPT-4o-mini, etc.)
- Los tokens consumidos (input y output)
- Los precios públicos de cada proveedor

### 4. Errores

| Métrica | Descripción |
|---|---|
| **Error rate** | Porcentaje de traces con error |
| **Tipos de error** | Clasificación (timeout, rate limit, etc.) |
| **Stack traces** | Traza completa del error |

---

## Feedback en producción

### Feedback automático
Puedes enviar feedback programáticamente después de cada interacción:

```python
from langsmith import Client

client = Client()

# Enviar feedback después de cada respuesta
client.create_feedback(
    run_id=run_id,
    key="user_satisfaction",
    score=1.0,  # El usuario dio like
    comment="Respuesta útil"
)
```

### Feedback de usuario
Integra botones de like/dislike en tu UI:

```python
# Cuando el usuario hace clic en 👍
def on_thumbs_up(run_id: str):
    client.create_feedback(
        run_id=run_id,
        key="user_rating",
        score=1.0,
    )

# Cuando el usuario hace clic en 👎
def on_thumbs_down(run_id: str, comment: str = ""):
    client.create_feedback(
        run_id=run_id,
        key="user_rating",
        score=0.0,
        comment=comment,
    )
```

---

## Monitorizar con tags y metadata

### Separar tráfico por entorno

```python
import os

# En producción
os.environ["LANGSMITH_PROJECT"] = "chatbot-produccion"

# En staging
os.environ["LANGSMITH_PROJECT"] = "chatbot-staging"
```

### Etiquetar traces con contexto

```python
from langchain_core.runnables import RunnableConfig

config = RunnableConfig(
    tags=["produccion", "chatbot-v3"],
    metadata={
        "user_id": "user-123",
        "session_id": "sess-456",
        "version": "3.1.0",
        "region": "us-east-1",
    }
)

response = chain.invoke(input_data, config=config)
```

---

## Alertas y umbrales

En la UI de LangSmith puedes configurar alertas cuando:
- La latencia promedio supera un umbral (ej: > 3 segundos)
- La tasa de errores sube (ej: > 5%)
- El coste diario supera un límite (ej: > $50)
- El feedback negativo aumenta (ej: > 20% thumbs down)

---

## Filtrar traces en producción

### Por rendimiento
```
latency > 3s          → Traces lentos
total_tokens > 5000   → Traces costosos
status:error          → Traces con error
```

### Por contexto
```
tag:produccion                    → Solo traces de producción
metadata.user_id:user-123         → Traces de un usuario específico
metadata.version:3.1.0            → Traces de una versión específica
```

---

## Mejores prácticas de monitoreo

1. **Separa proyectos** por entorno (dev, staging, prod)
2. **Agrega metadata** útil (user_id, session_id, version)
3. **Recopila feedback** de usuarios (thumbs up/down)
4. **Configura alertas** para latencia y errores
5. **Revisa traces lentos** periódicamente
6. **Monitoriza costes** semanalmente
7. **Usa tags** para filtrar rápidamente

---

## Código de ejemplo

Revisa `main.py` en esta carpeta para ver ejemplos ejecutables de:
1. Configurar tracing para producción
2. Agregar metadata y tags a traces
3. Enviar feedback programático
4. Consultar métricas con el SDK
5. Simular monitoreo con múltiples ejecuciones
