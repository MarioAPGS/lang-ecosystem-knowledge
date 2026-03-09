# LLMs y Chat Models - Explicación Detallada

## ¿Qué son los Chat Models?

Los **Chat Models** son la pieza fundamental de LangChain. Son wrappers alrededor de los modelos de lenguaje (GPT, Claude, Gemini, Llama...) que estandarizan la forma en que interactúas con ellos.

La idea clave es que **no importa qué proveedor uses**, la interfaz es siempre la misma: `.invoke()`, `.stream()`, `.batch()`.

---

## Tipos de mensajes

Los Chat Models trabajan con **mensajes tipados**:

| Tipo | Rol | Descripción |
|---|---|---|
| `SystemMessage` | system | Instrucciones de comportamiento para el modelo |
| `HumanMessage` | human | Mensaje del usuario |
| `AIMessage` | ai | Respuesta del modelo |
| `ToolMessage` | tool | Resultado de una herramienta ejecutada |

```python
from langchain_core.messages import SystemMessage, HumanMessage

messages = [
    SystemMessage(content="Eres un experto en Python."),
    HumanMessage(content="¿Qué es un decorador?")
]
```

---

## Parámetros importantes

### `temperature`
Controla la **creatividad** de las respuestas:
- `0.0` → Respuestas deterministas y consistentes (ideal para tareas precisas)
- `0.7` → Balance entre creatividad y coherencia
- `1.0+` → Respuestas más creativas pero menos predecibles

### `model`
Especifica qué modelo usar del proveedor. Cada proveedor tiene sus propios modelos.

### `max_tokens`
Limita la longitud máxima de la respuesta generada.

---

## Métodos principales

| Método | Descripción | Uso |
|---|---|---|
| `.invoke()` | Ejecuta y devuelve la respuesta completa | Uso general |
| `.stream()` | Devuelve la respuesta token a token | UX en tiempo real |
| `.batch()` | Procesa múltiples inputs en paralelo | Procesamiento masivo |
| `.ainvoke()` | Versión async de invoke | Aplicaciones async |

---

## ¿Qué devuelve `.invoke()`?

Devuelve un objeto `AIMessage` con:
- `.content` → El texto de la respuesta
- `.response_metadata` → Metadata del proveedor (tokens usados, modelo, etc.)
- `.usage_metadata` → Tokens de input, output y total

---

## Código de ejemplo

Revisa `main.py` en esta carpeta para ver ejemplos ejecutables de:
1. Inicialización básica de un Chat Model
2. Uso de diferentes tipos de mensajes
3. Streaming de respuestas
4. Procesamiento por lotes (batch)
5. Comparación de temperaturas
