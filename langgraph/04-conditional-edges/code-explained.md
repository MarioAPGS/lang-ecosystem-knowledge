# Conditional Edges - Explicación Detallada

## ¿Qué son los Conditional Edges?

Los **conditional edges** permiten que el flujo del grafo tome **caminos diferentes según el estado**. Es como un `if/elif/else` pero a nivel de grafo.

```
                    ┌──────────┐
                    │  Evaluar │
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
        score > 80   score > 50    else
              │          │          │
        ┌─────▼──┐ ┌────▼────┐ ┌──▼──────┐
        │Aprobar │ │ Revisar │ │Rechazar │
        └────────┘ └─────────┘ └─────────┘
```

---

## `add_conditional_edges`

La API principal para routing condicional:

```python
graph.add_conditional_edges(
    source="nodo_origen",        # Desde qué nodo se evalúa
    path=funcion_router,         # Función que decide el destino
    path_map={                   # Opcional: mapea retornos a nombres de nodo
        "valor_a": "nodo_a",
        "valor_b": "nodo_b"
    }
)
```

### La función router

Es una función que:
1. Recibe el **estado actual**
2. Retorna un **string** con el nombre del siguiente nodo (o END)

```python
def decidir_ruta(state: State) -> str:
    if state["score"] > 80:
        return "aprobar"
    elif state["score"] > 50:
        return "revisar"
    else:
        return "rechazar"
```

---

## Retornar END desde un router

Si la función router retorna `END`, el grafo termina su ejecución:

```python
from langgraph.graph import END

def check_terminacion(state: State) -> str:
    if state["completado"]:
        return END  # Terminar el grafo
    return "siguiente_paso"
```

---

## path_map: mapeo explícito

El `path_map` es **opcional** pero útil para:
1. Documentar las rutas posibles
2. Desacoplar los valores del router de los nombres de nodo

```python
# Sin path_map: el return del router DEBE ser el nombre del nodo
def router(state):
    return "nodo_aprobado"  # Debe coincidir con graph.add_node("nodo_aprobado", ...)

# Con path_map: puedes usar valores arbitrarios
def router(state):
    return "ok"  # Valor abstracto

graph.add_conditional_edges("eval", router, {
    "ok": "nodo_aprobado",      # "ok" → nodo_aprobado
    "fail": "nodo_rechazado"    # "fail" → nodo_rechazado
})
```

---

## Patrón común: Loop con condición de salida

Un patrón muy usado en agentes es el **loop** que se repite hasta cumplir una condición:

```python
def should_continue(state: State) -> str:
    if state["intentos"] >= 3 or state["exito"]:
        return END
    return "reintentar"

graph.add_conditional_edges("verificar", should_continue)
graph.add_edge("reintentar", "ejecutar")
graph.add_edge("ejecutar", "verificar")  # Loop: ejecutar → verificar → ¿reintentar?
```

```
START → ejecutar → verificar ──┬── éxito ──→ END
                     ▲          │
                     │          │
                     └── reintentar
```

---

## Múltiples conditional edges

Un grafo puede tener **varios nodos** con conditional edges:

```python
graph.add_conditional_edges("clasificar", router_clasificacion)
graph.add_conditional_edges("validar", router_validacion)
```

---

## Ejemplo 1: Router simple (binario)

```python
def decidir(state):
    if state["valor"] > 0:
        return "positivo"
    return "negativo"

graph.add_conditional_edges("analizar", decidir)
```

---

## Ejemplo 2: Router multi-ruta

```python
def clasificar_urgencia(state):
    nivel = state["urgencia"]
    if nivel == "critica":
        return "escalar"
    elif nivel == "alta":
        return "priorizar"
    elif nivel == "media":
        return "procesar"
    else:
        return "cola"
```

---

## Ejemplo 3: Loop con máximo de intentos

```python
def retry_logic(state):
    if state["intentos"] >= state["max_intentos"]:
        return "fallback"
    if state["exito"]:
        return END
    return "reintentar"
```

---

## Resumen

| Concepto | API | Uso |
|---|---|---|
| Conditional edge | `add_conditional_edges()` | Routing dinámico basado en estado |
| Función router | `def fn(state) -> str:` | Decide el siguiente nodo |
| path_map | `{"valor": "nodo"}` | Mapeo explícito de valores a nodos |
| Retornar END | `return END` | Terminar ejecución desde un router |
| Loop pattern | condicional + edge de vuelta | Repetir hasta condición |
