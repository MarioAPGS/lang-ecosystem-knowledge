"""
Memoria / Historial de Conversación - Ejemplos ejecutables
===========================================================
Prerequisitos:
    pip install langchain-openai langchain-community python-dotenv

Configuración:
    Crea un archivo .env en la raíz del proyecto con:
    OPENAI_API_KEY=sk-...
"""

import os
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, trim_messages
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
parser = StrOutputParser()

# ============================================================
# 1. Historial básico en memoria
# ============================================================
print("=" * 60)
print("1. HISTORIAL BÁSICO EN MEMORIA")
print("=" * 60)

# Crear un historial
history = InMemoryChatMessageHistory()

# Agregar mensajes manualmente
history.add_user_message("Hola, me llamo Lucía")
history.add_ai_message("¡Hola Lucía! ¿En qué puedo ayudarte?")
history.add_user_message("Estoy aprendiendo LangChain")
history.add_ai_message("¡Genial! LangChain es un framework excelente.")

# Ver los mensajes almacenados
print("Mensajes en el historial:")
for msg in history.messages:
    role = "User" if isinstance(msg, HumanMessage) else "AI"
    print(f"  {role}: {msg.content}")
# Ejemplo salida →
#   User: Hola, me llamo Lucía
#   AI: ¡Hola Lucía! ¿En qué puedo ayudarte?
#   User: Estoy aprendiendo LangChain
#   AI: ¡Genial! LangChain es un framework excelente.
print()

# Usar el historial en un prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente amable que recuerda toda la conversación."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chain = prompt | llm | parser

# Invocar con el historial
response = chain.invoke({
    "history": history.messages,
    "input": "¿Recuerdas cómo me llamo y qué estoy aprendiendo?"
})
print(f"Respuesta: {response}")
# Ejemplo salida → Respuesta: ¡Claro! Te llamas Lucía y estás aprendiendo LangChain. ¿Te puedo ayudar con algo más?
print()

# ============================================================
# 2. Chatbot con RunnableWithMessageHistory
# ============================================================
print("=" * 60)
print("2. CHATBOT CON RUNNABLEWITHMESSAGEHISTORY")
print("=" * 60)

# Store de sesiones
store = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """Obtiene o crea el historial para una sesión."""
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


prompt_chat = ChatPromptTemplate.from_messages([
    ("system", "Eres un tutor de programación amable y paciente. Responde de forma concisa."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chain_chat = prompt_chat | llm | parser

# Envolver con gestión automática de historial
chatbot = RunnableWithMessageHistory(
    chain_chat,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# Configuración de sesión
config = {"configurable": {"session_id": "session_lucia"}}

# Conversación continua
mensajes = [
    "Hola, soy Lucía y quiero aprender sobre decoradores en Python",
    "¿Puedes darme un ejemplo simple?",
    "¿Y para qué se usan en la práctica?",
    "¿Recuerdas cómo me llamo y sobre qué estamos hablando?",
]

for msg in mensajes:
    print(f"User: {msg}")
    response = chatbot.invoke({"input": msg}, config=config)
    print(f"AI: {response[:200]}{'...' if len(response) > 200 else ''}")
    # Ejemplo salida (primera iteración) →
    #   User: Hola, soy Lucía y quiero aprender sobre decoradores en Python
    #   AI: ¡Hola Lucía! Los decoradores en Python son funciones que modifican el comportamiento de otra función. Se usan con el símbolo @ encima de la función...
    print()

# Ver cuántos mensajes tiene la sesión
session_history = store["session_lucia"]
print(f"Total mensajes en sesión: {len(session_history.messages)}")
# Ejemplo salida → Total mensajes en sesión: 8
print()

# ============================================================
# 3. Múltiples sesiones independientes
# ============================================================
print("=" * 60)
print("3. MÚLTIPLES SESIONES INDEPENDIENTES")
print("=" * 60)

# Sesión de Ana
config_ana = {"configurable": {"session_id": "session_ana"}}
response = chatbot.invoke({"input": "Hola, soy Ana. ¿Qué es una API REST?"}, config=config_ana)
print(f"[Ana] AI: {response[:150]}...")
# Ejemplo salida → [Ana] AI: ¡Hola Ana! Una API REST es una interfaz que permite a aplicaciones comunicarse entre sí usando peticiones HTTP...

# Sesión de Carlos
config_carlos = {"configurable": {"session_id": "session_carlos"}}
response = chatbot.invoke({"input": "Hola, soy Carlos. ¿Qué es Docker?"}, config=config_carlos)
print(f"[Carlos] AI: {response[:150]}...")
# Ejemplo salida → [Carlos] AI: ¡Hola Carlos! Docker es una plataforma que permite empaquetar aplicaciones en contenedores...

# Cada sesión recuerda su propio contexto
response_ana = chatbot.invoke({"input": "¿Recuerdas mi nombre?"}, config=config_ana)
response_carlos = chatbot.invoke({"input": "¿Recuerdas mi nombre?"}, config=config_carlos)

print(f"\n[Ana pregunta su nombre] AI: {response_ana[:100]}")
# Ejemplo salida → [Ana pregunta su nombre] AI: ¡Tu nombre es Ana!
print(f"[Carlos pregunta su nombre] AI: {response_carlos[:100]}")
# Ejemplo salida → [Carlos pregunta su nombre] AI: ¡Te llamas Carlos!
print(f"\nSesiones activas: {list(store.keys())}")
# Ejemplo salida → Sesiones activas: ['session_lucia', 'session_ana', 'session_carlos']
print()

# ============================================================
# 4. Recorte de historial (Trimming)
# ============================================================
print("=" * 60)
print("4. RECORTE DE HISTORIAL (TRIMMING)")
print("=" * 60)

# Crear un historial largo
mensajes_largo = [
    SystemMessage(content="Eres un asistente útil."),
    HumanMessage(content="Hola, me llamo Lucía"),
    AIMessage(content="¡Hola Lucía!"),
    HumanMessage(content="¿Qué es Python?"),
    AIMessage(content="Python es un lenguaje de programación interpretado."),
    HumanMessage(content="¿Y JavaScript?"),
    AIMessage(content="JavaScript es un lenguaje para desarrollo web."),
    HumanMessage(content="¿Y Rust?"),
    AIMessage(content="Rust es un lenguaje de sistemas enfocado en seguridad de memoria."),
    HumanMessage(content="¿Cuál me recomiendas?"),
]

print(f"Mensajes originales: {len(mensajes_largo)}")
# Ejemplo salida → Mensajes originales: 10

# Recortar para mantener solo los últimos N tokens
mensajes_recortados = trim_messages(
    mensajes_largo,
    max_tokens=100,               # Máximo de tokens a mantener
    strategy="last",              # Mantener los últimos mensajes
    token_counter=llm,            # Usar el LLM para contar tokens
    include_system=True,          # Siempre incluir el system message
    allow_partial=False,          # No cortar mensajes a la mitad
)

print(f"Mensajes después del recorte: {len(mensajes_recortados)}")
# Ejemplo salida → Mensajes después del recorte: 4
for msg in mensajes_recortados:
    role = type(msg).__name__.replace("Message", "")
    print(f"  [{role}]: {msg.content[:80]}")
# Ejemplo salida →
#   [System]: Eres un asistente útil.
#   [AI]: JavaScript es un lenguaje para desarrollo web.
#   [Human]: ¿Y Rust?
#   [AI]: Rust es un lenguaje de sistemas enfocado en seguridad de memoria.
print()

# Usar trimming en una cadena
prompt_trimmed = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente útil. Responde de forma breve."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

# Función de trimming integrada en la cadena
trimmer = lambda msgs: trim_messages(
    msgs,
    max_tokens=200,
    strategy="last",
    token_counter=llm,
    include_system=True,
)

# Cadena con trimming automático
chain_trimmed = (
    {
        "history": lambda x: trimmer(x["history"]),
        "input": lambda x: x["input"],
    }
    | prompt_trimmed
    | llm
    | parser
)

response = chain_trimmed.invoke({
    "history": mensajes_largo,
    "input": "¿Cuál de los lenguajes que mencionaste es el más nuevo?",
})
print(f"Respuesta (con historial recortado): {response}")
# Ejemplo salida → Respuesta (con historial recortado): De los lenguajes que mencioné, Rust es el más nuevo, ya que su primera versión estable se lanzó en 2015.
print()

# ============================================================
# 5. Historial con resumen automático
# ============================================================
print("=" * 60)
print("5. HISTORIAL CON RESUMEN AUTOMÁTICO")
print("=" * 60)

prompt_resumen = ChatPromptTemplate.from_template(
    "Resume la siguiente conversación en 2-3 frases, capturando los puntos clave:\n\n{conversacion}"
)

chain_resumen = prompt_resumen | llm | parser

# Formatear el historial como texto
conversacion_texto = "\n".join(
    f"{'User' if isinstance(m, HumanMessage) else 'System' if isinstance(m, SystemMessage) else 'AI'}: {m.content}"
    for m in mensajes_largo
)

resumen = chain_resumen.invoke({"conversacion": conversacion_texto})
print(f"Resumen de la conversación:\n{resumen}")
# Ejemplo salida → Resumen de la conversación:
# Lucía preguntó sobre tres lenguajes de programación. Se discutió Python (interpretado, 1991), JavaScript (desarrollo web) y Rust (seguridad de memoria). Finalmente pidió una recomendación.
print()

# Usar el resumen como contexto para la siguiente conversación
prompt_con_resumen = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente útil. Resumen de la conversación anterior: {resumen}"),
    ("human", "{input}"),
])

chain_con_resumen = prompt_con_resumen | llm | parser

response = chain_con_resumen.invoke({
    "resumen": resumen,
    "input": "Basándote en nuestra conversación anterior, ¿qué lenguaje sería mejor para un principiante?",
})
print(f"Respuesta (usando resumen): {response}")
# Ejemplo salida → Respuesta (usando resumen): Basándome en nuestra conversación, Python sería la mejor opción para un principiante por su sintaxis simple y legible, además de su gran comunidad y recursos de aprendizaje.
