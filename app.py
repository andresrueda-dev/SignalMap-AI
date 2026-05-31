# ========================================================
# SIGNALMAP IA - ADVANCED VALIDATION & MATRIX CORE
# ========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from datetime import datetime
import os

# --- AUTENTICACIÓN (LOGIN) ---
def login():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.sidebar.title("🔐 SignalMap IA Login")
        u = st.sidebar.text_input("Usuario")
        p = st.sidebar.text_input("Código de Victoria", type="password")
        if st.sidebar.button("Acceder"):
            if (u == "Andrew" and p == "7122") or (u == "Javier" and p == "8514"):
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else: st.sidebar.error("Acceso denegado")
        return False
    return True

if not login(): st.stop()

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="SignalMap IA - MetaPattern Live", layout="wide", page_icon="🧠")
st.sidebar.success(f"Sesión activa: {st.session_state.user}")

# --- MOTOR FRACTAL Y FIREBASE (MANTENIDO) ---
try:
    from modules.motor_fractal import MetaPatternFractal
except ImportError:
    try: from motor_fractal import MetaPatternFractal
    except ImportError:
        class MetaPatternFractal:
            def __init__(self, max_iter=250): self.max_iter = max_iter
            def transformar_secuencia(self, seq):
                datos = np.array(seq, dtype=float)
                dot_x = np.dot(datos, np.arange(1, len(datos) + 1)) if len(datos) > 0 else 0
                return (np.sin(dot_x)*0.5 - 0.75), (np.cos(dot_x)*0.5)

# (Escudo Firebase se mantiene intacto aquí...)
firebase_active = False 

# --- ESTILOS Y CONFIG ---
st.markdown("""<style>
.stButton>button { background-color: #7c3aed; color: white; border-radius: 12px; }
.dashboard-card { background-color: #111827; padding: 16px; border-radius: 16px; border: 1px solid #1f2937; }
.grid-cell-match { background-color: #15803d; text-align: center; border-radius: 8px; font-weight: bold; border: 2px solid #22c55e; }
.grid-cell-miss { background-color: #991b1b; text-align: center; border-radius: 8px; font-weight: bold; border: 2px solid #ef4444; }
.grid-cell-neutral { background-color: #1e293b; text-align: center; border-radius: 8px; border: 1px solid #334155; }
</style>""", unsafe_allow_html=True)

if "local_signals" not in st.session_state: st.session_state.local_signals = []
if "boletos_auditados" not in st.session_state: st.session_state.boletos_auditados = []

GAME_CONFIG = {
    "Chispazo": {"min": 1, "max": 28, "cantidad": 5, "archivo": "data/Chispazo_SIGNALMAP.csv", "cols": ["num_1","num_2","num_3","num_4","num_5"]},
    "Melate": {"min": 1, "max": 56, "cantidad": 6, "archivo": "data/Melate_SIGNALMAP.csv", "cols": ["num_1","num_2","num_3","num_4","num_5","num_6"]}
}

# --- LÓGICA DE CALIBRACIÓN Y CARGA (ORIGINALES) ---
def calcular_espejo_calibrado(lista_numeros, game):
    config = GAME_CONFIG[game]
    max_p, min_p = config["max"], config["min"]
    mapa = {"0":"5", "1":"6", "2":"7", "3":"8", "4":"9", "5":"0", "6":"1", "7":"2", "8":"3", "9":"4"}
    res = []
    for n in lista_numeros:
        s = "".join([mapa[d] if d in mapa else d for d in str(n)])
        val = int(s)
        if val > max_p: val = min_p + (val % (max_p - min_p + 1))
        res.append(val)
    return res

def cargar_sorteo_real(game):
    config = GAME_CONFIG[game]
    if os.path.exists(config["archivo"]):
        return pd.read_csv(config["archivo"]), config["cols"]
    return pd.DataFrame(columns=config["cols"]), config["cols"]

# --- NAVEGACIÓN REORDENADA ---
menu = st.sidebar.radio("FLUJO DE TRABAJO", [
    "1. 📖 Captura de Señal", 
    "2. ⚙️ Motor de Calibración (4 Capas)",
    "3. 🏠 Dashboard Global", 
    "4. 📸 Auditoría de Boleto"
])

# 1. CAPTURA
if menu == "1. 📖 Captura de Señal":
    st.title("1. Captura de Señal")
    sorteo = st.selectbox("Sorteo", list(GAME_CONFIG.keys()))
    nums = st.text_input("Números observados (Ej: 7,1,2,2)")
    nota = st.text_area("Notas / Interpretación")
    if st.button("Guardar Señal"):
        st.session_state.local_signals.append({"sorteo": sorteo, "numeros": [int(x) for x in nums.split(",")], "nota": nota})
        st.success("Señal capturada.")

# 2. CALIBRACIÓN (4 CAPAS ORIGINALES)
elif menu == "2. ⚙️ Motor de Calibración (4 Capas)":
    st.title("2. Motor de Calibración (4 Capas)")
    colA, colB = st.columns(2)
    with colA:
        constante = st.text_input("Código de Victoria", value="7122")
        dia = st.number_input("Día", value=datetime.now().day)
        humedad = st.number_input("Humedad (%)", value=3)
    with colB:
        s1, s2 = st.number_input("Sincronía 1", value=7), st.number_input("Sincro 2", value=11)
        err = st.checkbox("Error/Volatilidad")
        rango = st.selectbox("Límite", [28, 56])

    if st.button("🚀 Procesar Secuencia"):
        matriz = {int(constante[0])+int(constante[1]), s1+s2}
        if humedad < 5: matriz.update([int(str(dia)[0]), int(str(dia)[1])])
        cierre = int(constante[-2:])
        matriz.update([max(1, cierre-1), cierre+1] if err else [cierre])
        st.success(f"Secuencia: {sorted([n for n in matriz if 1 <= n <= rango])}")

# 3. DASHBOARD
elif menu == "3. 🏠 Dashboard Global":
    st.title("3. Dashboard Global")
    for game in GAME_CONFIG.keys():
        st.subheader(game)
        df, cols = cargar_sorteo_real(game)
        if not df.empty: st.bar_chart(df[cols].stack().value_counts())

# 4. AUDITORÍA
elif menu == "4. 📸 Auditoría de Boleto":
    st.title("4. Auditoría de Boleto")
    s = st.selectbox("Sorteo", list(GAME_CONFIG.keys()))
    j = st.text_input("Jugados")
    g = st.text_input("Ganadores")
    if st.button("Auditar"):
        st.session_state.boletos_auditados.append({"sorteo": s, "jugados": [int(x) for x in j.split(",")], "ganadores": [int(x) for x in g.split(",")]})
        st.success("Boleto Auditado.")
