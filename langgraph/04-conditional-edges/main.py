"""
Conditional Edges - Ejemplos ejecutables
==========================================
Prerequisitos:
    pip install langgraph langchain-openai python-dotenv

Configuración:
    Crea un archivo .env en la raíz del proyecto con:
    OPENAI_API_KEY=sk-...
"""

import os
from typing import Annotated, TypedDict
from operator import add
from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END

# ============================================================
# 1. Router binario simple
# ============================================================
print("=" * 60)
print("1. ROUTER BINARIO SIMPLE")
print("=" * 60)


class NumeroState(TypedDict):
    valor: int
    resultado: str


def analizar_numero(state: NumeroState) -> dict:
    return {}  # Solo prepara, el router decide


def es_positivo(state: NumeroState) -> dict:
    return {"resultado": f"✅ {state['valor']} es positivo"}


def es_negativo(state: NumeroState) -> dict:
    return {"resultado": f"❌ {state['valor']} es negativo o cero"}


def router_signo(state: NumeroState) -> str:
    if state["valor"] > 0:
        return "positivo"
    return "negativo"


graph1 = StateGraph(NumeroState)
graph1.add_node("analizar", analizar_numero)
graph1.add_node("positivo", es_positivo)
graph1.add_node("negativo", es_negativo)

graph1.add_edge(START, "analizar")
graph1.add_conditional_edges("analizar", router_signo)
graph1.add_edge("positivo", END)
graph1.add_edge("negativo", END)

app1 = graph1.compile()

# Test con valor positivo
r1 = app1.invoke({"valor": 42, "resultado": ""})
print(f"Valor 42: {r1['resultado']}")
# Ejemplo salida → Valor 42: ✅ 42 es positivo

# Test con valor negativo
r2 = app1.invoke({"valor": -7, "resultado": ""})
print(f"Valor -7: {r2['resultado']}")
# Ejemplo salida → Valor -7: ❌ -7 es negativo o cero
print()


# ============================================================
# 2. Router multi-ruta (clasificación)
# ============================================================
print("=" * 60)
print("2. ROUTER MULTI-RUTA (CLASIFICACIÓN)")
print("=" * 60)


class TicketState(TypedDict):
    urgencia: str
    descripcion: str
    accion: str


def recibir_ticket(state: TicketState) -> dict:
    return {}


def escalar(state: TicketState) -> dict:
    return {"accion": f"🚨 ESCALADO: '{state['descripcion']}' → Equipo de crisis"}


def priorizar(state: TicketState) -> dict:
    return {"accion": f"⚡ PRIORIZADO: '{state['descripcion']}' → Cola prioritaria"}


def procesar_normal(state: TicketState) -> dict:
    return {"accion": f"📋 PROCESANDO: '{state['descripcion']}' → Cola normal"}


def archivar(state: TicketState) -> dict:
    return {"accion": f"📁 ARCHIVADO: '{state['descripcion']}' → Sin acción requerida"}


def router_urgencia(state: TicketState) -> str:
    nivel = state["urgencia"]
    if nivel == "critica":
        return "escalar"
    elif nivel == "alta":
        return "priorizar"
    elif nivel == "media":
        return "procesar"
    else:
        return "archivar"


graph2 = StateGraph(TicketState)
graph2.add_node("recibir", recibir_ticket)
graph2.add_node("escalar", escalar)
graph2.add_node("priorizar", priorizar)
graph2.add_node("procesar", procesar_normal)
graph2.add_node("archivar", archivar)

graph2.add_edge(START, "recibir")
graph2.add_conditional_edges("recibir", router_urgencia)
graph2.add_edge("escalar", END)
graph2.add_edge("priorizar", END)
graph2.add_edge("procesar", END)
graph2.add_edge("archivar", END)

app2 = graph2.compile()

tickets = [
    {"urgencia": "critica", "descripcion": "Servidor caído", "accion": ""},
    {"urgencia": "alta", "descripcion": "Bug en producción", "accion": ""},
    {"urgencia": "media", "descripcion": "Feature request", "accion": ""},
    {"urgencia": "baja", "descripcion": "Typo en docs", "accion": ""},
]

for ticket in tickets:
    result = app2.invoke(ticket)
    print(f"  {result['accion']}")
# Ejemplo salida →   🚨 ESCALADO: 'Servidor caído' → Equipo de crisis
# Ejemplo salida →   ⚡ PRIORIZADO: 'Bug en producción' → Cola prioritaria
# Ejemplo salida →   📋 PROCESANDO: 'Feature request' → Cola normal
# Ejemplo salida →   📁 ARCHIVADO: 'Typo en docs' → Sin acción requerida
print()


# ============================================================
# 3. Router con path_map
# ============================================================
print("=" * 60)
print("3. ROUTER CON PATH_MAP")
print("=" * 60)


class ExamenState(TypedDict):
    nota: int
    calificacion: str


def evaluar_nota(state: ExamenState) -> dict:
    return {}


def sobresaliente(state: ExamenState) -> dict:
    return {"calificacion": f"🏆 Sobresaliente ({state['nota']}/100)"}


def aprobado(state: ExamenState) -> dict:
    return {"calificacion": f"✅ Aprobado ({state['nota']}/100)"}


def suspendido(state: ExamenState) -> dict:
    return {"calificacion": f"❌ Suspendido ({state['nota']}/100)"}


def router_nota(state: ExamenState) -> str:
    nota = state["nota"]
    if nota >= 90:
        return "A"
    elif nota >= 50:
        return "B"
    return "F"


graph3 = StateGraph(ExamenState)
graph3.add_node("evaluar", evaluar_nota)
graph3.add_node("sobresaliente", sobresaliente)
graph3.add_node("aprobado", aprobado)
graph3.add_node("suspendido", suspendido)

graph3.add_edge(START, "evaluar")
graph3.add_conditional_edges("evaluar", router_nota, {
    "A": "sobresaliente",
    "B": "aprobado",
    "F": "suspendido"
})
graph3.add_edge("sobresaliente", END)
graph3.add_edge("aprobado", END)
graph3.add_edge("suspendido", END)

app3 = graph3.compile()

for nota in [95, 72, 35]:
    result = app3.invoke({"nota": nota, "calificacion": ""})
    print(f"  Nota {nota}: {result['calificacion']}")
# Ejemplo salida →   Nota 95: 🏆 Sobresaliente (95/100)
# Ejemplo salida →   Nota 72: ✅ Aprobado (72/100)
# Ejemplo salida →   Nota 35: ❌ Suspendido (35/100)
print()


# ============================================================
# 4. Loop con condición de salida
# ============================================================
print("=" * 60)
print("4. LOOP CON CONDICIÓN DE SALIDA")
print("=" * 60)


class RetryState(TypedDict):
    intentos: int
    max_intentos: int
    valor_actual: int
    objetivo: int
    log: Annotated[list[str], add]


import random


def intentar(state: RetryState) -> dict:
    nuevo_valor = random.randint(1, 10)
    intento_num = state["intentos"] + 1
    return {
        "valor_actual": nuevo_valor,
        "intentos": intento_num,
        "log": [f"Intento {intento_num}: generé {nuevo_valor} (objetivo: {state['objetivo']})"]
    }


def verificar_resultado(state: RetryState) -> str:
    if state["valor_actual"] == state["objetivo"]:
        return "exito"
    if state["intentos"] >= state["max_intentos"]:
        return "fallback"
    return "reintentar"


def nodo_exito(state: RetryState) -> dict:
    return {"log": [f"🎉 ¡Éxito en el intento {state['intentos']}!"]}


def nodo_fallback(state: RetryState) -> dict:
    return {"log": [f"😞 Fallback: no se logró en {state['max_intentos']} intentos"]}


graph4 = StateGraph(RetryState)
graph4.add_node("intentar", intentar)
graph4.add_node("exito", nodo_exito)
graph4.add_node("fallback", nodo_fallback)

graph4.add_edge(START, "intentar")
graph4.add_conditional_edges("intentar", verificar_resultado, {
    "exito": "exito",
    "fallback": "fallback",
    "reintentar": "intentar"  # ← Loop: vuelve a intentar
})
graph4.add_edge("exito", END)
graph4.add_edge("fallback", END)

app4 = graph4.compile()

random.seed(42)  # Para resultados reproducibles
result4 = app4.invoke({
    "intentos": 0,
    "max_intentos": 5,
    "valor_actual": 0,
    "objetivo": 7,
    "log": []
})

for entry in result4["log"]:
    print(f"  {entry}")
# Ejemplo salida →   Intento 1: generé 2 (objetivo: 7)
# Ejemplo salida →   Intento 2: generé 1 (objetivo: 7)
# Ejemplo salida →   Intento 3: generé 7 (objetivo: 7)
# Ejemplo salida →   🎉 ¡Éxito en el intento 3!
print()


# ============================================================
# 5. Condicional con END directo
# ============================================================
print("=" * 60)
print("5. CONDICIONAL CON END DIRECTO")
print("=" * 60)


class ValidationState(TypedDict):
    email: str
    es_valido: bool
    mensaje: str


def validar_email(state: ValidationState) -> dict:
    email = state["email"]
    es_valido = "@" in email and "." in email.split("@")[-1]
    return {"es_valido": es_valido}


def router_validacion(state: ValidationState) -> str:
    if state["es_valido"]:
        return "procesar"
    return END  # ← Termina directamente sin procesar


def procesar_email(state: ValidationState) -> dict:
    return {"mensaje": f"📧 Email '{state['email']}' procesado correctamente"}


graph5 = StateGraph(ValidationState)
graph5.add_node("validar", validar_email)
graph5.add_node("procesar", procesar_email)

graph5.add_edge(START, "validar")
graph5.add_conditional_edges("validar", router_validacion)
graph5.add_edge("procesar", END)

app5 = graph5.compile()

# Email válido
r_valido = app5.invoke({"email": "lucia@example.com", "es_valido": False, "mensaje": ""})
print(f"Email válido: {r_valido['mensaje']}")
# Ejemplo salida → Email válido: 📧 Email 'lucia@example.com' procesado correctamente

# Email inválido → termina directo sin procesar
r_invalido = app5.invoke({"email": "no-es-email", "es_valido": False, "mensaje": ""})
print(f"Email inválido: mensaje = '{r_invalido['mensaje']}' (no procesado)")
# Ejemplo salida → Email inválido: mensaje = '' (no procesado)
print()


# ============================================================
# 6. Visualización del grafo con condicionales
# ============================================================
print("=" * 60)
print("6. VISUALIZACIÓN DEL GRAFO CON CONDICIONALES")
print("=" * 60)

print("\n--- Grafo del loop (retry) ---")
print(app4.get_graph().draw_ascii())
print()

print("=" * 60)
print("✅ Todos los ejemplos de Conditional Edges ejecutados")
print("=" * 60)
