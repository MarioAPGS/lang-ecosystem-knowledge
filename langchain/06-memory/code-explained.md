# Memoria / Historial de Conversación - Explicación Detallada

## ¿Qué es la Memoria en LangChain?

La **memoria** permite que un chatbot o aplicación **recuerde interacciones anteriores** dentro de una conversación. Sin memoria, cada llamada al LLM es independiente y no tiene contexto de lo que se habló antes.

```
Sin memoria:                     Con memoria:
┌──────────┐                     ┌──────────┐
│ User: Hola │                   │ User: Hola │
│ AI: ¡Hola!│                    │ AI: ¡Hola!│
└──────────┘                     │ User: Soy Lucía │
┌──────────┐                     │ AI: ¡Hola Lucía!│
│ User: ¿Cómo me llamo? │       │ User: ¿Cómo me llamo?│
│ AI: No lo sé ❌        │       │ AI: Te llamas Lucía ✅│
└──────────┘                     └──────────┘
```

---

## Estrategias de Memoria

### 1. `InMemoryChatMessageHistory`
Almacena el historial completo en memoria RAM. Simple y directo.
- **Pros**: Fácil de usar, sin dependencias externas
- **Contras**: Se pierde al reiniciar, crece sin límite

### 2. Memoria con ventana (Window)
Solo mantiene los últimos N mensajes.
- **Pros**: Controla el uso de tokens
- **Contras**: Pierde contexto antiguo

### 3. Memoria con resumen (Summary)
Usa el LLM para resumir la conversación periódicamente.
- **Pros**: Mantiene contexto global sin usar muchos tokens
- **Contras**: Pierde detalles específicos

### 4. Persistente (Base de datos)
Guarda el historial en una base de datos (Redis, PostgreSQL, etc.).
- **Pros**: Persiste entre reinicios, escalable
- **Contras**: Requiere infraestructura adicional

---

## Gestión de sesiones

Cada conversación independiente necesita su propio historial. Se gestiona con **session IDs**:

```python
store = {}  # session_id → ChatMessageHistory

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]
```

---

## Tokens y contexto

El historial ocupa tokens en cada llamada al LLM:

| Modelo | Context Window | Consideración |
|---|---|---|
| GPT-4o-mini | 128K tokens | Caben muchas conversaciones |
| GPT-4o | 128K tokens | Amplio, pero costoso |
| Claude Sonnet | 200K tokens | Muy amplio |

**Regla:** Aunque el contexto sea grande, más tokens = más coste y latencia. Usa estrategias de recorte.

---

## Código de ejemplo

Revisa `main.py` en esta carpeta para ver ejemplos ejecutables de:
1. Historial básico en memoria
2. Chatbot con `RunnableWithMessageHistory`
3. Múltiples sesiones independientes
4. Recorte de historial (trimming)
5. Historial con resumen automático
