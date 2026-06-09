# ========================================================
# SIGNALMAP IA - ADVANCED VALIDATION & MATRIX CORE
# ========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime
import os

# --- MÓDULOS DE EXPANSIÓN (INTEGRACIÓN) ---

def check_alerta_proximidad(x_nuevo, y_nuevo, pilares_df, umbral=5.0):
    distancias = np.sqrt((pilares_df['X'] - x_nuevo)**2 + (pilares_df['Y'] - y_nuevo)**2)
    min_dist = distancias.min()
    idx_cercano = distancias.idxmin()
    if min_dist <= umbral:
        st.sidebar.warning(f"⚠️ ¡ALERTA! A {min_dist:.2f}u del Pilar {idx_cercano}. ALTA PROBABILIDAD.")
        return True, idx_cercano
    return False, None

def modulo_visualizacion_impactos(df_historico, df_impactos, pilares_x, pilares_y):
    plt.figure(figsize=(10, 6))
    plt.scatter(df_historico['X'], df_historico['Y'], c='gray', alpha=0.1, s=1)
    plt.scatter(pilares_x, pilares_y, c='yellow', marker='*', s=100, label='Pilares Constantes')
    if not df_impactos.empty:
        premiados = df_impactos[df_impactos['Premiado'] == True]
        plt.scatter(premiados['X'], premiados['Y'], c='lime', s=150, edgecolors='white', label='Impacto Ganador')
    plt.title("Mapa de Estructura de Ganancia")
    plt.legend()
    st.pyplot(plt)

def modulo_entrada_masiva_inteligente():
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 Ingesta Inteligente")
    datos_input = st.sidebar.text_area("Formato: TIPO,FECHA,NUMEROS", placeholder="TRIS,2026-06-09,12-15-22-30-45")
    if st.sidebar.button("Procesar y Calibrar"):
        if datos_input:
            archivo_historico = "base_datos_historica.csv"
            lineas = datos_input.strip().split('\n')
            registros = [{"Fecha": l.split(',')[1], "Sorteo": l.split(',')[0].upper(), "Resultado": l.split(',')[2]} for l in lineas]
            df_nuevos = pd.DataFrame(registros)
            if os.path.exists(archivo_historico):
                df_maestro = pd.concat([pd.read_csv(archivo_historico), df_nuevos])
            else:
                df_maestro = df_nuevos
            df_maestro.to_csv(archivo_historico, index=False)
            st.sidebar.success("¡Base calibrada!")

def modulo_registro_impactos():
    st.sidebar.markdown("---")
    st.sidebar.subheader("Registro de Impactos")
    archivo_csv = "impactos_historicos.csv"
    with st.sidebar.form("form_registro"):
        x_val, y_val = st.number_input("X"), st.number_input("Y")
        pilar_id, premiado = st.number_input("Pilar ID"), st.checkbox("¿Ganador?")
        if st.form_submit_button("Registrar"):
            pd.DataFrame({"X":[x_val], "Y":[y_val], "Pilar_ID":[pilar_id], "Premiado":[premiado]}).to_csv(archivo_csv, mode='a', header=not os.path.exists(archivo_csv), index=False)

# --- MOTOR PRINCIPAL ---

try:
    from modules.motor_fractal import MetaPatternFractal
except ImportError:
    class MetaPatternFractal:
        def __init__(self, max_iter=250): self.max_iter = max_iter
        def transformar_secuencia(self, seq):
            d = np.array(seq, dtype=float)
            dot_x = np.dot(d, np.arange(1, len(d)+1)) if len(d)>0 else 0
            return (np.sin(dot_x)*0.5 - 0.75), (np.cos(dot_x)*0.5)

st.set_page_config(page_title="SignalMap IA - MetaPattern Live", layout="wide", page_icon="🧠")

st.markdown("""
<style>
html, body { background-color: #020617; color: white; }
.stButton>button { background-color: #7c3aed; color: white; border-radius: 12px; }
.metric-box { background-color: #1e1b4b; padding: 15px; border-radius: 12px; border: 1px solid #4338ca; }
</style>
""", unsafe_allow_html=True)

if "local_signals" not in st.session_state: st.session_state.local_signals = []
if "boletos_auditados" not in st.session_state: st.session_state.boletos_auditados = []

GAME_CONFIG = {
    "TRIS": {"min": 0, "max": 9, "cantidad": 5, "archivo": "data/Tris_SIGNALMAP.csv", "columnas": ["num_1","num_2","num_3","num_4","num_5"]},
    "Chispazo": {"min": 1, "max": 28, "cantidad": 5, "archivo": "data/Chispazo_SIGNALMAP.csv", "columnas": ["num_1","num_2","num_3","num_4","num_5"]},
    "Melate": {"min": 1, "max": 56, "cantidad": 6, "archivo": "data/Melate_SIGNALMAP.csv", "columnas": ["num_1","num_2","num_3","num_4","num_5","num_6"]}
}

def calcular_espejo_calibrado(lista_numeros, game):
    config = GAME_CONFIG[game]
    mapa = {"0":"5", "1":"6", "2":"7", "3":"8", "4":"9", "5":"0", "6":"1", "7":"2", "8":"3", "9":"4"}
    res = []
    for n in lista_numeros:
        espejo = int("".join([mapa.get(d, d) for d in str(n)]))
        if espejo > config["max"]: espejo = config["min"] + (espejo % (config["max"] - config["min"] + 1))
        res.append(espejo)
    return res

menu = st.sidebar.radio("Navegación", ["📖 Diario", "📊 Timeline", "🏠 Dashboard", "🎯 Sugeridos", "📸 Evidencias"])

if menu == "📖 Diario":
    sorteo = st.selectbox("Sorteo", list(GAME_CONFIG.keys()))
    numeros = st.text_input("Números")
    if st.button("Guardar"):
        st.session_state.local_signals.append({"sorteo": sorteo, "numeros": [int(x) for x in numeros.split(",")]})

elif menu == "🏠 Dashboard":
    st.title("Matriz Global")
    # Invocar módulos aquí
    modulo_entrada_masiva_inteligente()
    modulo_registro_impactos()

elif menu == "🎯 Sugeridos":
    st.title("Sorteo Sugerido")
    motor_f = MetaPatternFractal()
    for game in GAME_CONFIG.keys():
        sugeridos = [1, 2, 3, 4, 5] # Placeholder lógico
        st.success(f"🎯 {game}: {sugeridos}")

elif menu == "📸 Evidencias":
    st.title("Auditoría Visual")
    # Lógica de planilla interactiva mantenida aquí
