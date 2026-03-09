# RAG (Retrieval-Augmented Generation) - Explicación Detallada

## ¿Qué es RAG?

**RAG** es un patrón que combina **búsqueda de información** con **generación de texto**. En lugar de depender solo del conocimiento interno del LLM, le proporcionas documentos relevantes como contexto para que genere respuestas más precisas y actualizadas.

```
Pregunta del usuario
        │
        ▼
┌───────────────┐     ┌──────────────┐
│   Retriever   │────▶│  Documentos  │
│  (búsqueda)   │     │  relevantes  │
└───────────────┘     └──────┬───────┘
                             │
                    ┌────────▼────────┐
                    │  Prompt + Docs  │
                    │    + Pregunta   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │      LLM       │
                    └────────┬────────┘
                             │
                    Respuesta fundamentada
```

---

## ¿Por qué RAG?

| Sin RAG | Con RAG |
|---|---|
| El LLM solo sabe lo de su entrenamiento | El LLM accede a tus datos actualizados |
| Puede "alucinar" respuestas | Fundamenta las respuestas en documentos reales |
| No conoce tu información privada | Puede consultar docs internos de tu empresa |
| Conocimiento congelado en el tiempo | Información siempre actualizada |

---

## Pipeline completo de RAG

### 1. Carga de documentos (Document Loaders)
Importar datos desde diversas fuentes:
- `PyPDFLoader` → PDFs
- `TextLoader` → Archivos .txt
- `WebBaseLoader` → Páginas web
- `CSVLoader` → Archivos CSV
- `DirectoryLoader` → Carpetas enteras

### 2. División en chunks (Text Splitters)
Los documentos grandes se dividen en fragmentos manejables:
- `RecursiveCharacterTextSplitter` → El más versátil, divide por párrafos/frases
- `chunk_size` → Tamaño máximo de cada chunk (en caracteres)
- `chunk_overlap` → Superposición entre chunks para no perder contexto

### 3. Embeddings
Convertir texto en vectores numéricos para búsqueda semántica:
- `OpenAIEmbeddings` → Embeddings de OpenAI
- `HuggingFaceEmbeddings` → Embeddings open-source gratuitos

### 4. Vector Store
Almacenar y buscar vectores eficientemente:
- `Chroma` → Ligero, ideal para desarrollo
- `FAISS` → De Meta, muy rápido en memoria
- `Pinecone` → Servicio cloud escalable

### 5. Retriever
Interfaz para buscar documentos relevantes:
```python
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
docs = retriever.invoke("mi pregunta")
```

### 6. Generación
Combinar documentos recuperados con la pregunta en un prompt y enviar al LLM.

---

## Parámetros clave del Text Splitter

| Parámetro | Descripción | Valor típico |
|---|---|---|
| `chunk_size` | Caracteres máx. por chunk | 500-1500 |
| `chunk_overlap` | Superposición entre chunks | 50-200 |
| `separators` | Caracteres para dividir | `["\n\n", "\n", " "]` |

**Regla general:** chunks más pequeños = búsqueda más precisa, chunks más grandes = más contexto.

---

## Código de ejemplo

Revisa `main.py` en esta carpeta para ver ejemplos ejecutables de:
1. Carga de documentos desde texto plano
2. División en chunks con `RecursiveCharacterTextSplitter`
3. Creación de un vectorstore con Chroma (in-memory)
4. Búsqueda semántica de documentos relevantes
5. Pipeline RAG completo: pregunta → búsqueda → respuesta
6. RAG con LCEL
