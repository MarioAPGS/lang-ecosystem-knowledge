# Human-in-the-Loop - Explicación Detallada

## ¿Qué es Human-in-the-Loop?

**Human-in-the-Loop (HITL)** es un patrón donde el grafo **pausa su ejecución** en un punto específico para pedir intervención humana antes de continuar. Es esencial para:

- **Aprobación de acciones críticas** (enviar emails, modificar bases de datos)
- **Revisión de resultados** antes de avanzar
- **Corrección manual** del estado del grafo
- **Validación** de respuestas del LLM

```
START → Generar → [⏸️ PAUSA] → Revisar humano → Ejecutar → END
                      ↑
              "¿Aprobar esta acción?"
```

---

## Pre-requisito: Checkpointer

Para usar HITL necesitas un **checkpointer** que guarde el estado del grafo cuando se pausa:

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = graph.compile(
    checkpointer=memory,
    interrupt_before=["nodo_critico"]  # Pausa ANTES de este nodo
)
```

---

## interrupt_before vs interrupt_after

### `interrupt_before`
**Pausa ANTES** de ejecutar el nodo especificado:

```python
app = graph.compile(
    checkpointer=memory,
    interrupt_before=["ejecutar_accion"]
)
```

```
START → Preparar → [⏸️] ejecutar_accion → END
                    ↑
            Se pausa aquí, antes de ejecutar
```

### `interrupt_after`
**Pausa DESPUÉS** de ejecutar el nodo especificado:

```python
app = graph.compile(
    checkpointer=memory,
    interrupt_after=["generar_plan"]
)
```

```
START → generar_plan [⏸️] → Ejecutar → END
                      ↑
            Se pausa aquí, después de generar
```

---

## Flujo de trabajo HITL

### 1. Primera invocación (hasta la pausa)

```python
config = {"configurable": {"thread_id": "review-1"}}

# El grafo se ejecuta hasta el punto de interrupción
result = app.invoke(input_state, config)
# → Se pausa antes de "nodo_critico"
```

### 2. Revisar el estado actual

```python
# Ver el estado cuando se pausó
state = app.get_state(config)
print(state.values)  # Estado actual
print(state.next)    # Siguiente nodo a ejecutar
```

### 3. Continuar la ejecución

```python
# Opción A: Continuar sin cambios (aprobar)
result = app.invoke(None, config)

# Opción B: Modificar el estado antes de continuar
app.update_state(config, {"campo": "nuevo_valor"})
result = app.invoke(None, config)
```

---

## `update_state`: modificar el estado

Permite **modificar el estado del grafo** antes de retomar la ejecución:

```python
# Cambiar un campo
app.update_state(config, {"aprobado": True})

# Cambiar múltiples campos
app.update_state(config, {
    "aprobado": True,
    "comentario": "Revisado por Lucía"
})
```

### Con `as_node`

Puedes especificar **desde qué nodo** simular la actualización:

```python
app.update_state(
    config,
    {"resultado": "valor_manual"},
    as_node="nodo_revision"
)
```

Esto es útil para inyectar datos como si vinieran de un nodo específico, respetando la lógica del grafo.

---

## Patrón: Aprobación de acciones

El caso de uso más común:

```python
def preparar_accion(state):
    return {"accion": "Enviar email a 500 destinatarios", "aprobado": False}

def ejecutar_accion(state):
    if state["aprobado"]:
        # Ejecutar la acción
        return {"resultado": "Acción ejecutada"}
    return {"resultado": "Acción cancelada"}

graph.add_edge(START, "preparar")
graph.add_edge("preparar", "ejecutar")
graph.add_edge("ejecutar", END)

app = graph.compile(
    checkpointer=memory,
    interrupt_before=["ejecutar"]  # Pausa antes de ejecutar
)

# 1. Corre hasta la pausa
app.invoke(estado_inicial, config)

# 2. El humano revisa y aprueba
app.update_state(config, {"aprobado": True})

# 3. Continúa la ejecución
app.invoke(None, config)
```

---

## Patrón: Revisión y corrección

```python
def generar_respuesta(state):
    # LLM genera una respuesta
    return {"respuesta_draft": llm.invoke(state["pregunta"]).content}

def publicar(state):
    return {"publicada": True}

# Pausa después de generar, para que el humano revise el draft
app = graph.compile(
    checkpointer=memory,
    interrupt_after=["generar"]
)

# 1. Genera el draft y pausa
app.invoke({"pregunta": "..."}, config)

# 2. Humano revisa y corrige si necesario
state = app.get_state(config)
draft = state.values["respuesta_draft"]
# Si no está bien, corregir:
app.update_state(config, {"respuesta_draft": "Versión corregida"})

# 3. Continuar
app.invoke(None, config)
```

---

## Resumen

| Concepto | API | Uso |
|---|---|---|
| interrupt_before | `compile(interrupt_before=["nodo"])` | Pausa ANTES de un nodo |
| interrupt_after | `compile(interrupt_after=["nodo"])` | Pausa DESPUÉS de un nodo  |
| get_state | `app.get_state(config)` | Ver estado pausado |
| update_state | `app.update_state(config, datos)` | Modificar estado antes de continuar |
| Continuar | `app.invoke(None, config)` | Retomar ejecución |
| thread_id | `{"configurable": {"thread_id": "..."}}` | Identificar la sesión |
