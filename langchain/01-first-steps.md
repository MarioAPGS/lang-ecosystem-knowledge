# LangChain - Guía de Iniciación

## ¿Qué es LangChain?

LangChain es un **framework open-source** diseñado para construir aplicaciones potenciadas por modelos de lenguaje (LLMs). Proporciona una capa de abstracción que facilita la conexión de LLMs con fuentes de datos externas, herramientas y flujos de trabajo complejos.

> **En resumen:** LangChain es el puente entre los modelos de IA (como GPT, Claude, Llama, etc.) y el mundo real (bases de datos, APIs, documentos, internet…).

---

## ¿Para qué sirve?

| Caso de uso | Descripción |
|---|---|
| **Chatbots** | Crear asistentes conversacionales con memoria y contexto |
| **RAG (Retrieval-Augmented Generation)** | Responder preguntas basándose en tus propios documentos |
| **Agentes autónomos** | Construir agentes que usan herramientas (buscar en Google, ejecutar código, consultar APIs…) |
| **Cadenas de procesamiento** | Encadenar múltiples llamadas a LLMs con lógica intermedia |
| **Resumen de documentos** | Resumir textos largos, PDFs, páginas web |
| **Extracción de datos** | Extraer información estructurada de texto no estructurado |

---

## Instalación

```bash
# Instalación base
pip install langchain

# Con proveedor de LLM (ej: OpenAI)
pip install langchain-openai

# Con proveedor Anthropic (Claude)
pip install langchain-anthropic

# Para RAG con vectorstores
pip install langchain-chroma   # o langchain-pinecone, langchain-weaviate...

# Para agentes con grafos
pip install langgraph
```

---

## Configuración de API Keys

La mayoría de proveedores requieren una API key. Configúralas como variables de entorno:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Google
export GOOGLE_API_KEY="..."

# O usa un archivo .env con python-dotenv
pip install python-dotenv
```

```python
from dotenv import load_dotenv
load_dotenv()  # Carga variables desde .env
```

---

## Conceptos Clave

Cada concepto tiene su **carpeta dedicada** con explicación detallada (`code-explained.md`) y código ejecutable (`main.py`):

| # | Concepto | Carpeta | Descripción |
|---|---|---|---|
| 1 | [LLMs y Chat Models](01-llms-chat-models/) | `01-llms-chat-models/` | Comunicación con modelos de lenguaje |
| 2 | [Prompt Templates](02-prompt-templates/) | `02-prompt-templates/` | Plantillas reutilizables para prompts |
| 3 | [Chains con LCEL](03-chains-lcel/) | `03-chains-lcel/` | Composición de cadenas con el operador pipe |
| 4 | [RAG](04-rag/) | `04-rag/` | Respuestas basadas en tus propios documentos |
| 5 | [Agentes](05-agents/) | `05-agents/` | LLMs que usan herramientas autónomamente |
| 6 | [Memoria](06-memory/) | `06-memory/` | Historial de conversación y contexto |

### 1. LLMs y Chat Models

LangChain abstrae la comunicación con distintos modelos de lenguaje:

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# OpenAI
llm_openai = ChatOpenAI(model="gpt-4o", temperature=0.7)

# Anthropic
llm_claude = ChatAnthropic(model="claude-sonnet-4-20250514")

# Usar cualquiera de la misma forma
response = llm_openai.invoke("¿Qué es LangChain?")
print(response.content)
```

### 2. Prompt Templates

Permiten crear prompts reutilizables con variables:

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un experto en {tema}. Responde de forma clara y concisa."),
    ("human", "{pregunta}")
])

# Formatear el prompt
messages = prompt.invoke({
    "tema": "Python",
    "pregunta": "¿Qué son los decoradores?"
})
```

### 3. Chains (Cadenas) con LCEL

**LCEL (LangChain Expression Language)** es la forma moderna de componer cadenas usando el operador `|` (pipe):

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template(
    "Explícame {concepto} como si tuviera 5 años"
)
llm = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

# Componer la cadena con LCEL
chain = prompt | llm | parser

# Ejecutar
resultado = chain.invoke({"concepto": "la fotosíntesis"})
print(resultado)
```

### 4. RAG (Retrieval-Augmented Generation)

Permite que el LLM responda basándose en tus propios documentos:

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 1. Cargar documentos
loader = PyPDFLoader("mi_documento.pdf")
docs = loader.load()

# 2. Dividir en chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)

# 3. Crear vectorstore con embeddings
vectorstore = Chroma.from_documents(chunks, OpenAIEmbeddings())

# 4. Crear retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 5. Buscar documentos relevantes y generar respuesta
docs_relevantes = retriever.invoke("¿De qué trata el documento?")
```

### 5. Agentes

Los agentes pueden usar **herramientas** para realizar acciones:

```python
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent

# Definir herramientas
search = DuckDuckGoSearchRun()
tools = [search]

# Crear agente
llm = ChatOpenAI(model="gpt-4o")
agent = create_react_agent(llm, tools)

# Ejecutar
result = agent.invoke({
    "messages": [("human", "¿Cuál es la última noticia sobre IA?")]
})
```

### 6. Memoria / Historial de Conversación

Para que el chatbot recuerde conversaciones anteriores:

```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Almacén de historial por sesión
store = {}

def get_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente útil."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])
```

---

## Flujo Típico de una Aplicación LangChain

```
                    ┌──────────┐
   Input usuario →  │  Prompt  │
                    │ Template │
                    └────┬─────┘
                         │
                    ┌────▼─────┐      ┌────────────┐
                    │   LLM    │◄────►│ Herramientas│
                    │  (Chat)  │      │  (Tools)    │
                    └────┬─────┘      └────────────┘
                         │
                    ┌────▼─────┐
                    │  Output  │
                    │  Parser  │
                    └────┬─────┘
                         │
                    Respuesta final
```

---

## Próximos Pasos Sugeridos

1. **Instalar LangChain** y ejecutar tu primer "Hello World" con un LLM
2. **Crear un chatbot simple** con prompt templates y LCEL
3. **Implementar RAG** con tus propios documentos (PDF, web, etc.)
4. **Construir un agente** que use herramientas externas
5. **Explorar LangGraph** para flujos más complejos con estado
6. **Monitorizar** con LangSmith para entender qué hace tu aplicación

---

> **Tip:** LangChain evoluciona rápidamente. Siempre consulta la [documentación oficial](https://python.langchain.com/docs/) para la API más actualizada.
