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

# --- INICIO: Módulo de Convergencia (SignalMap IA) ---
def inicializar_session_state():
    if 'convergencia_critica' not in st.session_state:
        st.session_state.convergencia_critica = False
    if 'nivel_intensidad' not in st.session_state:
        st.session_state.nivel_intensidad = 0

def interceptador_de_senales():
    st.sidebar.markdown("### ⚡ Interceptador de Convergencia")
    with st.sidebar.expander("Registro Inmediato de Señal"):
        entrada_datos = st.text_input("Ingresa vector (Ej: 7,11,4,3,8,5)")
        slider_nivel = st.slider("Nivel de Convergencia IA", 0, 100, 50)
        if st.button("Validar Señal"):
            st.session_state.nivel_intensidad = slider_nivel
            if slider_nivel > 80:
                st.session_state.convergencia_critica = True
                st.error("⚠️ ALERTA: Convergencia Crítica Detectada")
            else:
                st.session_state.convergencia_critica = False
                st.success("Estado: Convergencia Estable")

def calcular_convergencia(secuencia, codigo_base, temperatura):
    if not secuencia or temperatura == 0:
        return 0.0
    sumatoria = sum(secuencia)
    resultado = (sumatoria * codigo_base) / temperatura
    return round(resultado, 2)

# Ejecutar lógica de inicio
st.set_page_config(page_title="SignalMap IA - MetaPattern Live", layout="wide", page_icon="🧠")
inicializar_session_state()
interceptador_de_senales()
# --- FIN DE INTEGRACIÓN ---

# ========================================================
# SEGURIDAD Y CONTROL DE USUARIOS
# ========================================================
USUARIOS = {"andrew": "7122", "javier": "8514"}

if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if "usuario" not in st.session_state: st.session_state["usuario"] = None

def registrar_log(evento):
    archivo = "logs_usuarios.csv"
    fila = pd.DataFrame([{"fecha": datetime.now(), "usuario": st.session_state["usuario"], "evento": evento}])
    if os.path.exists(archivo): fila.to_csv(archivo, mode="a", header=False, index=False)
    else: fila.to_csv(archivo, index=False)

def login():
    st.title("🔐 SIGNALMAP IA")
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        usuario = usuario.lower()
        if usuario in USUARIOS and USUARIOS[usuario] == password:
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario
            registrar_log("Inicio de sesión")
            st.rerun()
        else: st.error("Usuario o contraseña incorrectos")

if not st.session_state["autenticado"]:
    login()
    st.stop()

# --- (El resto de tu código sigue exactamente igual a partir de aquí) ---
# [MANTÉN TUS CONFIGURACIONES DE GAME_CONFIG, ESTILOS Y MENÚS AQUÍ]
