"""
Prompt Templates - Ejemplos ejecutables
=======================================
Prerequisitos:
    pip install langchain-openai python-dotenv

Configuración:
    Crea un archivo .env en la raíz del proyecto con:
    OPENAI_API_KEY=sk-...
"""

import os
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# ============================================================
# 1. ChatPromptTemplate básico
# ============================================================
print("=" * 60)
print("1. CHATPROMPTTEMPLATE BÁSICO")
print("=" * 60)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un experto en {tema}. Responde de forma clara y breve."),
    ("human", "{pregunta}")
])

# Ver las variables necesarias
print(f"Variables requeridas: {prompt.input_variables}")
# Ejemplo salida → Variables requeridas: ['pregunta', 'tema']

# Formatear y ver los mensajes generados
messages = prompt.invoke({
    "tema": "bases de datos",
    "pregunta": "¿Qué diferencia hay entre SQL y NoSQL?"
})
print(f"Mensajes generados: {messages}")
# Ejemplo salida → Mensajes generados: messages=[SystemMessage(content='Eres un experto en bases de datos...'), HumanMessage(content='¿Qué diferencia hay...')]
print()

# Usar con el LLM
response = llm.invoke(messages)
print(f"Respuesta: {response.content}")
# Ejemplo salida → Respuesta: SQL usa tablas con esquemas fijos (relacional), mientras que NoSQL permite estructuras flexibles como documentos, clave-valor o grafos.
print()

# ============================================================
# 2. from_template shortcut
# ============================================================
print("=" * 60)
print("2. FROM_TEMPLATE (SHORTCUT)")
print("=" * 60)

# Crea un ChatPromptTemplate con un solo mensaje human
prompt_simple = ChatPromptTemplate.from_template(
    "Explica qué es {concepto} en máximo 2 frases"
)

print(f"Variables: {prompt_simple.input_variables}")
# Ejemplo salida → Variables: ['concepto']

messages = prompt_simple.invoke({"concepto": "un API REST"})
response = llm.invoke(messages)
print(f"Respuesta: {response.content}")
# Ejemplo salida → Respuesta: Un API REST es una interfaz que permite a sistemas comunicarse entre sí mediante peticiones HTTP (GET, POST, PUT, DELETE) siguiendo principios de arquitectura REST.
print()

# ============================================================
# 3. PromptTemplate (texto plano)
# ============================================================
print("=" * 60)
print("3. PROMPTTEMPLATE (TEXTO PLANO)")
print("=" * 60)

prompt_text = PromptTemplate.from_template(
    "Traduce la siguiente frase al {idioma}: '{texto}'"
)

print(f"Variables: {prompt_text.input_variables}")
# Ejemplo salida → Variables: ['idioma', 'texto']

resultado = prompt_text.invoke({"idioma": "inglés", "texto": "Hola, ¿cómo estás?"})
print(f"Prompt generado: {resultado.text}")
# Ejemplo salida → Prompt generado: Traduce la siguiente frase al inglés: 'Hola, ¿cómo estás?'

# Usar con LLM
response = llm.invoke(resultado.text)
print(f"Respuesta: {response.content}")
# Ejemplo salida → Respuesta: Hello, how are you?
print()

# ============================================================
# 4. Múltiples variables
# ============================================================
print("=" * 60)
print("4. MÚLTIPLES VARIABLES")
print("=" * 60)

prompt_multi = ChatPromptTemplate.from_messages([
    ("system", "Eres un profesor de {materia} para estudiantes de nivel {nivel}."),
    ("human", "Explícame {tema}. Usa ejemplos de {contexto}.")
])

print(f"Variables: {prompt_multi.input_variables}")
# Ejemplo salida → Variables: ['contexto', 'materia', 'nivel', 'tema']

messages = prompt_multi.invoke({
    "materia": "programación",
    "nivel": "principiante",
    "tema": "los bucles for",
    "contexto": "la vida cotidiana"
})

response = llm.invoke(messages)
print(f"Respuesta: {response.content[:300]}...")
# Ejemplo salida → Respuesta: Un bucle for es como recorrer una lista de tareas. Imagina que tienes una lista de compras: leche, pan, huevos. El bucle for va pasando por cada elemento uno a uno...
print()

# ============================================================
# 5. MessagesPlaceholder (para historial)
# ============================================================
print("=" * 60)
print("5. MESSAGESPLACEHOLDER")
print("=" * 60)

prompt_with_history = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente que recuerda la conversación."),
    MessagesPlaceholder(variable_name="historial"),
    ("human", "{input}")
])

# Simular un historial de conversación previo
historial_previo = [
    HumanMessage(content="Me llamo Lucía"),
    AIMessage(content="¡Hola Lucía! ¿En qué puedo ayudarte?"),
    HumanMessage(content="Estoy aprendiendo Python"),
    AIMessage(content="¡Genial! Python es un excelente lenguaje para empezar. ¿Qué te gustaría aprender?"),
]

messages = prompt_with_history.invoke({
    "historial": historial_previo,
    "input": "¿Recuerdas cómo me llamo y qué estoy aprendiendo?"
})

response = llm.invoke(messages)
print(f"Respuesta (con memoria): {response.content}")
# Ejemplo salida → Respuesta (con memoria): ¡Claro! Te llamas Lucía y estás aprendiendo Python. ¿En qué más puedo ayudarte?
print()

# ============================================================
# 6. Partial Templates
# ============================================================
print("=" * 60)
print("6. PARTIAL TEMPLATES")
print("=" * 60)

prompt_base = ChatPromptTemplate.from_messages([
    ("system", "Eres un {rol}. Responde en {idioma}."),
    ("human", "{pregunta}")
])

# Pre-rellenar el rol e idioma → reutilizar para muchas preguntas
prompt_dev_es = prompt_base.partial(rol="desarrollador senior de Python", idioma="español")
prompt_dev_en = prompt_base.partial(rol="senior Python developer", idioma="english")

print(f"Variables restantes (ES): {prompt_dev_es.input_variables}")
# Ejemplo salida → Variables restantes (ES): ['pregunta']

response_es = llm.invoke(prompt_dev_es.invoke({"pregunta": "¿Qué es un context manager?"}))
response_en = llm.invoke(prompt_dev_en.invoke({"pregunta": "What is a context manager?"}))

print(f"Respuesta ES: {response_es.content[:150]}...")
# Ejemplo salida → Respuesta ES: Un context manager es un objeto que define un contexto de ejecución usando `with`. Gestiona recursos automáticamente (abrir/cerrar archivos, conexiones)...
print(f"Respuesta EN: {response_en.content[:150]}...")
# Ejemplo salida → Respuesta EN: A context manager is an object that manages resources using the `with` statement, ensuring proper setup and teardown...
print()

# ============================================================
# 7. Composición con LCEL (preview)
# ============================================================
print("=" * 60)
print("7. COMPOSICIÓN CON LCEL (PREVIEW)")
print("=" * 60)

from langchain_core.output_parsers import StrOutputParser

# Los prompt templates se integran directamente en cadenas LCEL
chain = prompt_simple | llm | StrOutputParser()

resultado = chain.invoke({"concepto": "la programación funcional"})
print(f"Resultado de la cadena: {resultado}")
# Ejemplo salida → Resultado de la cadena: La programación funcional es un paradigma que trata la computación como evaluación de funciones matemáticas, evitando estados mutables y efectos secundarios.
print()

# ============================================================
# 8. Combinar tuplas con clases de mensaje
# ============================================================
print("=" * 60)
print("8. COMBINAR TUPLAS CON CLASES DE MENSAJE")
print("=" * 60)

# Las tuplas ("system", ...) son atajos para SystemMessage, etc.
# Pero puedes mezclar tuplas con clases directas:

prompt_mixto = ChatPromptTemplate.from_messages([
    SystemMessage(content="Siempre responde en español."),   # Clase fija (sin variables)
    ("system", "Eres un experto en {tema}."),                # Tupla con variable
    ("human", "{pregunta}")                                   # Tupla con variable
])

print(f"Variables: {prompt_mixto.input_variables}")
# Ejemplo salida → Variables: ['pregunta', 'tema']

messages = prompt_mixto.invoke({"tema": "cocina", "pregunta": "¿Cómo se hace una tortilla?"})
response = llm.invoke(messages)
print(f"Respuesta: {response.content[:200]}...")
# Ejemplo salida → Respuesta: Para hacer una tortilla española, bate 6 huevos, freí patatas cortadas finas en aceite, mézclalas con el huevo batido y cuájala en la sartén por ambos lados...
print()

# ============================================================
# 9. MessagePromptTemplate (clases con variables)
# ============================================================
print("=" * 60)
print("9. MESSAGEPROMPTTEMPLATE (CLASES CON VARIABLES)")
print("=" * 60)

# Cuando quieres usar clases de mensaje explícitas PERO con variables dinámicas:
prompt_msg_templates = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "Eres un {rol}. Tu especialidad es {especialidad}."
    ),
    HumanMessagePromptTemplate.from_template(
        "Necesito ayuda con: {consulta}"
    )
])

print(f"Variables: {prompt_msg_templates.input_variables}")
# Ejemplo salida → Variables: ['consulta', 'especialidad', 'rol']

messages = prompt_msg_templates.invoke({
    "rol": "arquitecto de software",
    "especialidad": "microservicios",
    "consulta": "¿Cuándo conviene usar un monolito vs microservicios?"
})

response = llm.invoke(messages)
print(f"Respuesta: {response.content[:250]}...")
# Ejemplo salida → Respuesta: Un monolito es ideal cuando el proyecto es pequeño o el equipo es reducido. Los microservicios convienen cuando necesitas escalar componentes de forma independiente y tienes equipos autónomos...
print()

# ============================================================
# 10. Few-shot prompting (mezcla de todas las formas)
# ============================================================
print("=" * 60)
print("10. FEW-SHOT PROMPTING (MEZCLA COMPLETA)")
print("=" * 60)

# Damos ejemplos al modelo de cómo queremos que responda
prompt_fewshot = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente que clasifica el sentimiento de frases."),
    # Ejemplo 1 (mensajes fijos como few-shot)
    HumanMessage(content="Me encanta este producto, es increíble"),
    AIMessage(content="POSITIVO"),
    # Ejemplo 2
    HumanMessage(content="Horrible experiencia, no lo recomiendo"),
    AIMessage(content="NEGATIVO"),
    # Ejemplo 3
    HumanMessage(content="El paquete llegó a las 3pm"),
    AIMessage(content="NEUTRO"),
    # Pregunta real del usuario (con variable)
    ("human", "{frase}")
])

frases_test = [
    "¡Qué día tan maravilloso para programar!",
    "El servidor se cayó otra vez, estoy harto",
    "La reunión es a las 10 de la mañana",
]

for frase in frases_test:
    messages = prompt_fewshot.invoke({"frase": frase})
    response = llm.invoke(messages)
    print(f"  \"{frase}\" → {response.content.strip()}")
# Ejemplo salida →
#   "¡Qué día tan maravilloso para programar!" → POSITIVO
#   "El servidor se cayó otra vez, estoy harto" → NEGATIVO
#   "La reunión es a las 10 de la mañana" → NEUTRO
