# Chains con LCEL - Explicación Detallada

## ¿Qué es LCEL?

**LCEL (LangChain Expression Language)** es la forma declarativa y moderna de componer cadenas en LangChain. Usa el operador **pipe `|`** para conectar componentes de forma legible e intuitiva.

```python
chain = prompt | llm | parser
```

Esto significa: "toma el prompt, pásalo al LLM, y parsea la salida".

---

## ¿Por qué LCEL?

| Ventaja | Descripción |
|---|---|
| **Streaming nativo** | Cada componente soporta streaming automáticamente |
| **Ejecución async** | Soporte automático para `ainvoke`, `astream`, `abatch` |
| **Paralelismo** | Ejecuta ramas en paralelo con `RunnableParallel` |
| **Reintentos y fallbacks** | `.with_retry()` y `.with_fallbacks()` built-in |
| **Trazabilidad** | Se integra con LangSmith para debugging |

---

## Componentes que puedes encadenar

Cualquier objeto que implemente la interfaz **Runnable** se puede usar en una cadena LCEL:

- `ChatPromptTemplate` → Genera mensajes
- `ChatOpenAI` (LLMs) → Genera respuestas
- `StrOutputParser` → Extrae texto de `AIMessage`
- `JsonOutputParser` → Parsea JSON de la respuesta
- `RunnablePassthrough` → Pasa el input sin modificar
- `RunnableParallel` → Ejecuta múltiples runnables en paralelo
- `RunnableLambda` → Envuelve cualquier función Python
- `itemgetter` → Extrae campos de un dict

---

## Patrones comunes

### Cadena básica
```python
chain = prompt | llm | StrOutputParser()
```

### Cadena con procesamiento previo
```python
chain = {"contexto": retriever, "pregunta": RunnablePassthrough()} | prompt | llm | parser
```

### Cadena con múltiples salidas en paralelo
```python
chain = RunnableParallel(
    resumen=prompt_resumen | llm | parser,
    sentimiento=prompt_sentimiento | llm | parser,
)
```

### Cadena con función personalizada
```python
chain = RunnableLambda(lambda x: x.upper()) | prompt | llm | parser
```

---

## Métodos disponibles en toda cadena LCEL

| Método | Descripción |
|---|---|
| `.invoke(input)` | Ejecuta la cadena completa |
| `.stream(input)` | Streaming token a token |
| `.batch([inputs])` | Procesa múltiples inputs |
| `.ainvoke(input)` | Versión async |
| `.with_retry()` | Añade reintentos automáticos |
| `.with_fallbacks([alt])` | Añade alternativas si falla |
| `.pipe(next)` | Alternativa programática a `\|` |

---

## Código de ejemplo

Revisa `main.py` en esta carpeta para ver ejemplos ejecutables de:
1. Cadena básica `prompt | llm | parser`
2. `RunnablePassthrough` y `RunnableParallel`
3. `RunnableLambda` para funciones custom
4. Streaming de cadenas completas
5. Batch processing
6. Encadenamiento de múltiples pasos
7. Fallbacks entre modelos
