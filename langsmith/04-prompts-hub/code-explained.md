# Prompts Hub - Explicación Detallada

## ¿Qué es el Prompt Hub?

El **Prompt Hub** de LangSmith es un repositorio centralizado para **guardar, versionar y compartir** tus prompts. En lugar de tener prompts hardcodeados en tu código, los gestionas desde LangSmith y los descargas en runtime.

---

## ¿Por qué usar el Prompt Hub?

| Sin Prompt Hub | Con Prompt Hub |
|---|---|
| Prompts hardcodeados en el código | Prompts centralizados y versionados |
| Cambiar un prompt = deploy nuevo | Cambiar un prompt = editar en la UI |
| Sin historial de cambios | Versionado automático |
| Difícil compartir entre equipos | Compartir con un enlace |
| Sin forma de comparar versiones | Diff entre versiones |
| Prompts mezclados con lógica | Separación clara prompt vs código |

---

## Conceptos clave

### Prompt
Un prompt almacenado en el Hub. Puede ser:
- `ChatPromptTemplate` (lo más común)
- `PromptTemplate` (para strings simples)
- Cualquier `Runnable` de LangChain

### Versiones (Commits)
Cada vez que actualizas un prompt, se crea una nueva versión. Puedes:
- Ver el historial de cambios
- Rollback a una versión anterior
- Comparar versiones con diff

### Tags
Etiquetas para marcar versiones específicas (similar a Git tags):
- `latest` → Siempre apunta a la versión más reciente
- `production` → La versión en uso en producción
- `staging` → Versión en testing

---

## Flujo de trabajo

```
  1. Desarrollar prompt localmente
  2. Subir al Hub con client.push_prompt()
  3. Iterar en la UI de LangSmith
  4. Descargar en tu app con client.pull_prompt()
  5. Evaluar con datasets
  6. Promover a producción con tags
```

---

## Operaciones principales

### Subir (Push) un prompt

```python
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate

client = Client()

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un experto en {tema}. Responde de forma {estilo}."),
    ("human", "{pregunta}")
])

# Subir al Hub
client.push_prompt("mi-asistente", object=prompt)
```

### Descargar (Pull) un prompt

```python
# Descargar la última versión
prompt = client.pull_prompt("mi-asistente")

# Descargar una versión específica (por commit hash)
prompt = client.pull_prompt("mi-asistente:abc123")

# Usar directamente
chain = prompt | llm | parser
result = chain.invoke({"tema": "Python", "estilo": "concisa", "pregunta": "¿Qué es un decorador?"})
```

### Listar prompts

```python
prompts = list(client.list_prompts())
for p in prompts:
    print(f"{p.repo_handle} - {p.description}")
```

---

## Prompt con modelo configurado

Puedes subir un prompt **con un modelo asociado**, de forma que al descargarlo ya incluye la configuración del LLM:

```python
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un chatbot amable."),
    ("human", "{input}")
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Subir prompt + modelo como runnable
runnable = prompt | llm
client.push_prompt("chatbot-completo", object=runnable)

# Al descargarlo, ya tiene el modelo configurado
chain = client.pull_prompt("chatbot-completo")
result = chain.invoke({"input": "Hola"})
```

---

## Compartir prompts

### Visibilidad

| Visibilidad | Descripción |
|---|---|
| **Private** | Solo visible para tu organización |
| **Public** | Visible para cualquier usuario de LangSmith |

### Compartir con el equipo

```python
# Los prompts son accesibles por cualquier miembro de tu organización
# Solo necesitan la misma LANGSMITH_API_KEY de la organización

# Persona A sube
client.push_prompt("prompt-del-equipo", object=prompt)

# Persona B descarga
prompt = client.pull_prompt("prompt-del-equipo")
```

---

## Mejores prácticas

1. **Nombra tus prompts descriptivamente**: `chatbot-soporte-v2`, `rag-respuesta-tecnica`
2. **Usa tags**: Marca con `production` el prompt que está en producción
3. **No hardcodees prompts**: Siempre descárgalos del Hub en runtime
4. **Evalúa antes de promover**: Usa datasets para evaluar un prompt antes de taggearlo como `production`
5. **Documenta cambios**: Usa la descripción del prompt para documentar para qué sirve

---

## Código de ejemplo

Revisa `main.py` en esta carpeta para ver ejemplos ejecutables de:
1. Crear y subir un prompt al Hub
2. Descargar un prompt y usarlo
3. Actualizar un prompt (nueva versión)
4. Listar prompts existentes
5. Usar prompts dentro de cadenas LCEL
