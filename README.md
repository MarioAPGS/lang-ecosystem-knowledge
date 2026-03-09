# Lang Ecosystem Knowledge

Repositorio de aprendizaje sobre el ecosistema **LangChain** y sus herramientas asociadas para construir aplicaciones potenciadas por modelos de lenguaje (LLMs).

---

## ¿Qué es el Ecosistema LangChain?

El ecosistema LangChain es un conjunto de paquetes y plataformas diseñados para facilitar el desarrollo de aplicaciones con LLMs. Cada componente tiene un rol específico:

```
┌─────────────────────────────────────────────────┐
│                  LangChain Ecosystem             │
├─────────────────────────────────────────────────┤
│                                                  │
│  langchain-core      → Abstracciones base        │
│  langchain           → Cadenas, agentes, RAG     │
│  langchain-community → Integraciones comunidad   │
│  langgraph           → Flujos con grafos/estado  │
│  langserve           → Desplegar como API REST   │
│  langsmith           → Observabilidad y testing  │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## Componentes del Ecosistema

### `langchain-core`
Interfaces y abstracciones base (LLMs, prompts, output parsers). Es la **fundación** sobre la que se construye todo el ecosistema. Define los contratos que implementan el resto de paquetes.

### `langchain`
El paquete principal. Contiene cadenas, agentes y utilidades de alto nivel para construir aplicaciones con LLMs de forma rápida.

### `langchain-community`
Integraciones mantenidas por la comunidad: vectorstores, document loaders, herramientas, etc. Es el punto de entrada para conectar con servicios de terceros.

### Paquetes de proveedores (`langchain-openai`, `langchain-anthropic`, `langchain-google`...)
Integraciones oficiales con proveedores específicos de LLMs. Cada paquete contiene los wrappers optimizados para su proveedor.

### `langgraph`
Framework para construir aplicaciones **multi-agente** y flujos con estado usando **grafos dirigidos**. Ideal para workflows complejos donde los agentes necesitan coordinarse, tomar decisiones condicionales o mantener estado entre pasos.

### `langserve`
Permite **exponer cadenas de LangChain como APIs REST** con muy poco código. Genera automáticamente endpoints con documentación, playground interactivo y soporte para streaming.

### `langsmith`
Plataforma de **observabilidad, depuración y testing** para aplicaciones LLM. Permite:
- Trazar cada paso de una cadena o agente
- Depurar prompts y respuestas
- Crear datasets de evaluación
- Monitorizar costes y latencia en producción

---

## Integraciones Disponibles

El ecosistema ofrece integraciones con cientos de servicios:

### Modelos de Lenguaje (LLMs)
- OpenAI (GPT-4o, GPT-4o-mini)
- Anthropic (Claude Sonnet, Opus, Haiku)
- Google (Gemini)
- Meta (Llama vía Ollama, Together AI)
- Mistral, Cohere, AWS Bedrock...

### Vector Stores (para RAG)
- Chroma, Pinecone, Weaviate
- FAISS, Qdrant, Milvus
- PostgreSQL (pgvector), Redis

### Document Loaders
- PDF, Word, Excel, CSV
- Páginas web, YouTube transcripts
- GitHub repos, Notion, Confluence
- S3, Google Drive

### Herramientas para Agentes
- Búsqueda web (Google, DuckDuckGo)
- Wikipedia, Arxiv
- Ejecución de código (Python REPL)
- APIs personalizadas

---

## Recursos Generales

| Recurso | Enlace |
|---|---|
| Documentación oficial | https://python.langchain.com/docs/ |
| LangChain GitHub | https://github.com/langchain-ai/langchain |
| LangSmith | https://smith.langchain.com/ |
| LangGraph docs | https://langchain-ai.github.io/langgraph/ |
| Tutoriales oficiales | https://python.langchain.com/docs/tutorials/ |
| API Reference | https://python.langchain.com/api_reference/ |

---

## Estructura del Repositorio

```
lang-ecosystem-knowledge/
├── README.md                          ← Visión general del ecosistema (estás aquí)
├── langchain/
│   ├── 01-first-steps.md              ← Guía de iniciación a LangChain
│   ├── 01-llms-chat-models/
│   │   ├── code-explained.md          ← Explicación detallada
│   │   └── main.py                    ← Código ejecutable
│   ├── 02-prompt-templates/
│   │   ├── code-explained.md
│   │   └── main.py
│   ├── 03-chains-lcel/
│   │   ├── code-explained.md
│   │   └── main.py
│   ├── 04-rag/
│   │   ├── code-explained.md
│   │   └── main.py
│   ├── 05-agents/
│   │   ├── code-explained.md
│   │   └── main.py
│   └── 06-memory/
│       ├── code-explained.md
│       └── main.py
└── langgraph/
    ├── 01-first-steps.md              ← Guía de iniciación a LangGraph
    ├── 01-conceptos-fundamentales/
    │   ├── code-explained.md
    │   └── main.py
    ├── 02-state-graph/
    │   ├── code-explained.md
    │   └── main.py
    ├── 03-nodes-edges/
    │   ├── code-explained.md
    │   └── main.py
    ├── 04-conditional-edges/
    │   ├── code-explained.md
    │   └── main.py
    ├── 05-react-agent/
    │   ├── code-explained.md
    │   └── main.py
    ├── 06-human-in-the-loop/
    │   ├── code-explained.md
    │   └── main.py
    └── 07-persistence-checkpoints/
        ├── code-explained.md
        └── main.py
```