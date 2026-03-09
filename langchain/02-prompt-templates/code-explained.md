# Prompt Templates - Explicación Detallada

## ¿Qué son los Prompt Templates?

Los **Prompt Templates** son plantillas reutilizables que te permiten construir prompts dinámicos con variables. En lugar de escribir strings a mano cada vez, defines una estructura y la rellenas con datos en tiempo de ejecución.

---

## ¿Por qué usar Prompt Templates?

1. **Reutilización**: Define una vez, usa muchas veces con distintos inputs
2. **Consistencia**: Asegura que los prompts mantengan la misma estructura
3. **Composición**: Se integran perfectamente con LCEL (cadenas con `|`)
4. **Validación**: Detectan variables faltantes antes de enviar al LLM
5. **Versionado**: Puedes versionar tus prompts como código

---

## Tipos de Prompt Templates

### `ChatPromptTemplate`
El más usado. Crea una secuencia de mensajes (system, human, ai):

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un experto en {tema}."),
    ("human", "{pregunta}")
])
```

### `PromptTemplate`
Para prompts simples de texto plano (sin roles de chat):

```python
from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template("Traduce '{texto}' al {idioma}")
```

### `MessagesPlaceholder`
Permite insertar una lista dinámica de mensajes (útil para historial de conversación):

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente útil."),
    MessagesPlaceholder(variable_name="historial"),
    ("human", "{input}")
])
```

---

## Combinando ChatPromptTemplate con tipos de mensaje

Un punto clave es que `ChatPromptTemplate.from_messages()` acepta **3 formas distintas** de definir mensajes, y puedes mezclarlas libremente:

### Forma 1: Tuplas shorthand (lo más conciso)
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un experto en {tema}."),
    ("human", "{pregunta}")
])
```
Las tuplas `("system", ...)`, `("human", ...)`, `("ai", ...)` son atajos que LangChain convierte internamente a `SystemMessage`, `HumanMessage`, `AIMessage`.

### Forma 2: Clases de mensaje directas (para mensajes fijos)
```python
from langchain_core.messages import SystemMessage

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="Siempre responde en español."),   # Fijo, sin variables
    ("human", "{pregunta}")                                   # Dinámico con variable
])
```
Útil cuando un mensaje es **fijo** (sin variables) y quieres dejarlo explícito.

### Forma 3: MessagePromptTemplate (clases con variables)
```python
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("Eres un {rol}. Responde en {idioma}."),
    HumanMessagePromptTemplate.from_template("{pregunta}")
])
```

### Mezcla de todas las formas (few-shot prompting)
```python
from langchain_core.messages import AIMessage

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un tutor de {materia}."),        # Tupla con variable
    SystemMessage(content="Sé breve y claro."),        # Clase fija
    ("human", "¿Qué es una variable?"),                # Tupla fija (ejemplo)
    AIMessage(content="Es un espacio en memoria..."),  # Respuesta de ejemplo
    ("human", "{pregunta}")                            # Input dinámico del usuario
])
```
Este patrón es muy útil para **few-shot prompting**: le das al modelo ejemplos de preguntas y respuestas esperadas antes de la pregunta real.

---

## Métodos principales

| Método | Descripción |
|---|---|
| `.invoke(dict)` | Formatea el template con las variables proporcionadas |
| `.format_messages(dict)` | Devuelve la lista de mensajes formateados |
| `.partial(**kwargs)` | Crea un nuevo template con algunas variables pre-rellenadas |
| `.input_variables` | Lista de variables que necesita el template |

---

## Partial Templates

Puedes "pre-rellenar" algunas variables y dejar otras para después:

```python
prompt = ChatPromptTemplate.from_template("Eres un {rol}. Responde: {pregunta}")

# Pre-rellenar el rol
prompt_dev = prompt.partial(rol="desarrollador senior")

# Ahora solo necesitas la pregunta
resultado = prompt_dev.invoke({"pregunta": "¿Qué es SOLID?"})
```

---

## Código de ejemplo

Revisa `main.py` en esta carpeta para ver ejemplos ejecutables de:
1. `ChatPromptTemplate` con mensajes (tuplas shorthand)
2. `from_template` shortcut
3. `PromptTemplate` (texto plano)
4. Múltiples variables
5. `MessagesPlaceholder` para historial
6. Partial templates
7. Composición con LCEL
8. Combinación de tuplas + clases de mensaje
9. `MessagePromptTemplate` con variables
10. Few-shot prompting mezclando todas las formas
