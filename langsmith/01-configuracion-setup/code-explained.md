# Configuración y Setup - Explicación Detallada

## ¿Qué necesitas para usar LangSmith?

LangSmith funciona como un servicio en la nube (SaaS) al que tu aplicación envía datos de tracing. Solo necesitas:

1. **Una cuenta** en [smith.langchain.com](https://smith.langchain.com/)
2. **Una API key** generada desde la plataforma
3. **Variables de entorno** configuradas en tu aplicación

---

## Paso 1: Crear tu cuenta

1. Ve a [smith.langchain.com](https://smith.langchain.com/)
2. Regístrate con tu email, Google o GitHub
3. Confirma tu email si es necesario

> **Nota:** El plan gratuito incluye suficientes traces para desarrollo y aprendizaje.

---

## Paso 2: Obtener tu API Key

1. Una vez dentro, ve a **Settings** (⚙️)
2. En la sección **API Keys**, haz clic en **Create API Key**
3. Copia la key generada (formato: `lsv2_pt_...`)
4. **Guárdala de forma segura** — no la compartas ni la subas a Git

---

## Paso 3: Variables de entorno

### Variables principales

| Variable | Requerida | Descripción |
|---|---|---|
| `LANGSMITH_TRACING` | Sí | Activa el tracing (`true` / `false`) |
| `LANGSMITH_API_KEY` | Sí | Tu API key de LangSmith |
| `LANGSMITH_PROJECT` | No | Nombre del proyecto (default: `"default"`) |
| `LANGSMITH_ENDPOINT` | No | URL del servidor (solo para self-hosted) |

### Configuración con archivo `.env`

La forma recomendada es usar un archivo `.env` en la raíz de tu proyecto:

```bash
# .env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_pt_tu_api_key_aqui
LANGSMITH_PROJECT=mi-proyecto-langsmith

# También necesitas la API key de tu proveedor LLM
OPENAI_API_KEY=sk-...
```

Y cargarlo con `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()  # Carga todas las variables del archivo .env
```

---

## Paso 4: Verificar la conexión

Una vez configuradas las variables, puedes verificar que todo funciona:

```python
from langsmith import Client

client = Client()
# Si no lanza error, la conexión es correcta
print("Conectado a LangSmith ✅")
```

---

## Tracing automático vs manual

### Tracing automático
Solo con configurar las variables de entorno, **todas las llamadas de LangChain y LangGraph se tracean automáticamente**. No necesitas cambiar ni una línea de código:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
response = llm.invoke("Hola")
# → Este trace aparece automáticamente en LangSmith
```

### Tracing manual con `@traceable`
Para funciones Python que **no son de LangChain**, usa el decorador `@traceable`:

```python
from langsmith import traceable

@traceable
def mi_funcion_custom(texto: str) -> str:
    # Cualquier lógica Python
    return texto.upper()
```

---

## Proyectos (Projects)

Los **projects** agrupan traces. Son útiles para separar:
- **Desarrollo** vs **Producción**
- **Diferentes aplicaciones** o features
- **Diferentes versiones** de tu app

```python
import os

# Cambiar de proyecto es cambiar una variable
os.environ["LANGSMITH_PROJECT"] = "chatbot-v2-produccion"
```

En la UI de LangSmith, puedes filtrar por proyecto para ver solo los traces relevantes.

---

## Desactivar tracing

Cuando no quieras enviar traces (por ejemplo, en tests unitarios):

```python
import os
os.environ["LANGSMITH_TRACING"] = "false"
```

O simplemente no configures la variable `LANGSMITH_TRACING`.

---

## Código de ejemplo

Revisa `main.py` en esta carpeta para ver ejemplos ejecutables de:
1. Configuración básica con variables de entorno
2. Verificación de conexión con el SDK
3. Trace automático con LangChain
4. Trace manual con `@traceable`
5. Uso de proyectos para organizar traces
