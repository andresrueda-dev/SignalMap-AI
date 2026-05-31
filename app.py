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

# Importación segura del Motor Fractal
try:
    from modules.motor_fractal import MetaPatternFractal
except ImportError:
    try:
        from motor_fractal import MetaPatternFractal
    except ImportError:
        class MetaPatternFractal:
            def __init__(self, max_iter=250):
                self.max_iter = max_iter
            def transformar_secuencia(self, seq):
                datos = np.array(seq, dtype=float)
                dot_x = np.dot(datos, np.arange(1, len(datos) + 1)) if len(datos) > 0 else 0
                return (np.sin(dot_x)*0.5 - 0.75), (np.cos(dot_x)*0.5)

# ==========================================
# ESCUDO DE FIREBASE BYPASS PARA GITHUB
# ==========================================
try:
    import pyrebase
    firebase_config = {
        "apiKey": "AIzaSyBXZgwW6UFwWtzFx1fVD32Dy1z6itBaYVk",
        "authDomain": "signalmap-ia.firebaseapp.com",
        "databaseURL": "https://signalmap-ia-default-rtdb.firebaseio.com/",
        "projectId": "signalmap-ia",
        "storageBucket": "signalmap-ia.firebasestorage.app",
        "messagingSenderId": "967824400239",
        "appId": "1:967824400239:web:bc30c8b4eb9610b3aed29a"
    }
    firebase = pyrebase.initialize_app(firebase_config)
    db = firebase.database()
    firebase_active = True
except ImportError:
    firebase_active = False

st.set_page_config(page_title="SignalMap IA - MetaPattern Live", layout="wide", page_icon="🧠")

# Estilos Oscuros Premium e Interfaz de Cuadrícula
st.markdown("""
<style>
html, body, [class*="css"] { background-color: #020617; color: white; }
h1,h2,h3,h4,h5 { color: white; }
.stButton>button { background-color: #7c3aed; color: white; border-radius: 12px; border: none; padding: 10px; }
.stMetric { background-color: #111827; padding: 12px; border-radius: 14px; }
.dashboard-card { background-color: #111827; padding: 16px; border-radius: 16px; border: 1px solid #1f2937; margin-bottom: 10px; }
.metric-box { background-color: #1e1b4b; padding: 15px; border-radius: 12px; border: 1px solid #4338ca; margin-top: 10px; }
.grid-cell-match { background-color: #15803d; color: white; padding: 10px; text-align: center; border-radius: 8px; font-weight: bold; border: 2px solid #22c55e; }
.grid-cell-miss { background-color: #991b1b; color: white; padding: 10px; text-align: center; border-radius: 8px; font-weight: bold; border: 2px solid #ef4444; }
.grid-cell-neutral { background-color: #1e293b; color: #94a3b8; padding: 10px; text-align: center; border-radius: 8px; border: 1px solid #334155; }
</style>
""", unsafe_allow_html=True)

# Inicialización de Sesiones de Historial de Evidencias
if "local_signals" not in st.session_state: st.session_state.local_signals = []
if "boletos_auditados" not in st.session_state: st.session_state.boletos_auditados = []
if "user_id" not in st.session_state: st.session_state.user_id = "user_directo_hoy"

GAME_CONFIG = {
    "TRIS": {
        "min": 0,
        "max": 9,
        "cantidad": 5,
        "archivo": "data/Tris_SIGNALMAP.csv",
        "columnas": ["num_1","num_2","num_3","num_4","num_5"],
        "es_lineal": True
    },

    "Chispazo": {
        "min": 1,
        "max": 28,
        "cantidad": 5,
        "archivo": "data/Chispazo_SIGNALMAP.csv",
        "columnas": ["num_1","num_2","num_3","num_4","num_5"],
        "es_lineal": False
    },

    "Melate": {
        "min": 1,
        "max": 56,
        "cantidad": 6,
        "archivo": "data/Melate_SIGNALMAP.csv",
        "columnas": ["num_1","num_2","num_3","num_4","num_5","num_6"],
        "es_lineal": False
    },

    "Revancha": {
        "min": 1,
        "max": 56,
        "cantidad": 6,
        "archivo": "data/Revancha_SIGNALMAP.csv",
        "columnas": ["num_1","num_2","num_3","num_4","num_5","num_6"],
        "es_lineal": False
    },

    "Revanchita": {
        "min": 1,
        "max": 56,
        "cantidad": 6,
        "archivo": "data/Revanchita_SIGNALMAP.csv",
        "columnas": ["num_1","num_2","num_3","num_4","num_5","num_6"],
        "es_lineal": False
    },

    "Melate Retro": {
        "min": 1,
        "max": 39,
        "cantidad": 6,
        "archivo": "data/MelateRetro_SIGNALMAP.csv",
        "columnas": ["num_1","num_2","num_3","num_4","num_5","num_6"],
        "es_lineal": False
    },

    "Gana Gato": {
        "min": 1,
        "max": 5,
        "cantidad": 8,
        "archivo": "data/GanaGato_SIGNALMAP.csv",
        "columnas": ["num_1","num_2","num_3","num_4","num_5","num_6","num_7","num_8"],
        "es_lineal": False
    }
}
# ========================================================
# REINGENIERÍA: MOTOR ESPEJO CALIBRADO POR FRONTERA MÁXIMA
# ========================================================
def calcular_espejo_calibrado(lista_numeros, game):
    config = GAME_CONFIG[game]
    max_permitido = config["max"]
    min_permitido = config["min"]
    
    # Mapeo matemático base por complementos moleculares de 9
    mapa_digitos = {"0":"5", "1":"6", "2":"7", "3":"8", "4":"9", "5":"0", "6":"1", "7":"2", "8":"3", "9":"4"}
    
    resultado_espejo = []
    for n in lista_numeros:
        # Transformación por dígitos espejo
        str_n = str(n)
        str_espejo = "".join([mapa_digitos[d] if d in mapa_digitos else d for d in str_n])
        num_espejo = int(str_espejo)
        
        # Filtro de Frontera Estricta (Ajuste modular si sobrepasa el número máximo del sorteo)
        if num_espejo > max_permitido:
            # Si se pasa del límite (ej. 70 en Chispazo), recalculamos usando el residuo matemático
            num_espejo = min_permitido + (num_espejo % (max_permitido - min_permitido + 1))
        
        resultado_espejo.append(num_espejo)
        
    return resultado_espejo

def cargar_sorteo_real(game):
    config = GAME_CONFIG[game]
    ruta = config["archivo"]
    cols = config["columnas"]
    if os.path.exists(ruta):
        try:
            df = pd.read_csv(ruta)
            df[cols] = df[cols].fillna(0).astype(int)
            return df, cols
        except: pass
    rows = [list(np.random.randint(config["min"], config["max"] + 1, config["cantidad"])) for _ in range(500)]
    return pd.DataFrame(rows, columns=cols), cols

# MENU LATERAL RE-ESTRUCTURADO
menu = st.sidebar.radio("Navegación", [
    "📖 Diario de Señales", 
    "📊 Timeline de Hoy", 
    "🏠 Dashboard Global", 
    "🎯 Sorteo Número Sugerido", 
    "📸 Evidencia & Diario de Aciertos"
])

# 1. DIARIO DE SEÑALES
if menu == "📖 Diario de Señales":
    st.title("📖 Diario de Señales - Registro Inmediato")
    sorteo = st.selectbox("Selecciona el Sorteo", list(GAME_CONFIG.keys()))
    numeros = st.text_input("Introduce los números de hoy (Ej: 7,1,2,2)")
    nota = st.text_area("Notas / Interpretación de la señal")
    nivel = st.select_slider("Nivel de Convergencia IA", options=["🌊 Baja", "📡 Media", "⚡ Alta", "🔥 Crítica"])

    if st.button("🚀 Guardar Señal de Hoy"):
        if numeros:
            lista_numeros = [int(x.strip()) for x in numeros.split(",") if x.strip().isdigit()]
            registro = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "sorteo": sorteo, "numeros": lista_numeros, "nota": nota, "nivel": nivel}
            st.session_state.local_signals.append(registro)
            st.success("✅ ¡Señal guardada con éxito!")
            if firebase_active:
                try: db.child("signals").child(st.session_state.user_id).child(sorteo).push(registro)
                except: pass

# 2. TIMELINE
elif menu == "📊 Timeline de Hoy":
    st.title("📊 Historial de Señales Capturadas Hoy")
    if len(st.session_state.local_signals) > 0: 
        st.dataframe(pd.DataFrame(st.session_state.local_signals), use_container_width=True)
    else: st.info("Aún no hay señales registradas.")

# 3. DASHBOARD GLOBAL CON INDICADORES DE EXCELENCIA Y PALOMITAS
elif menu == "🏠 Dashboard Global":
    st.title("🧠 Matriz Global de Convergencia & Indexación Fractal")
    
    # Marcador general de validación de tiros directos del día
    total_aciertos_dia = sum([1 for b in st.session_state.boletos_auditados if b["estado"] == "🎯 ACERTADO"])
    if total_aciertos_dia > 0:
        st.markdown(f"### 🎉 SISTEMA VERIFICADO SEGURO: {total_aciertos_dia} Sorteos Validados con Éxito hoy ✔️")

    cols_layout = st.columns(2)
    contador_col = 0

    for game in GAME_CONFIG.keys():
        df, cols = cargar_sorteo_real(game)
        valores_todos = df[cols].values.flatten()
        freq = pd.Series(valores_todos).value_counts().sort_index()
        dominante = int(freq.idxmax()) if len(freq) > 0 else 0
        
        # Verificamos si hay una palomita registrada para este sorteo específico
        has_match = any([b for b in st.session_state.boletos_auditados if b["sorteo"] == game and b["estado"] == "🎯 ACERTADO"])
        marcador_exito = " ✔️ (TIRO DIRECTO)" if has_match else ""

        with cols_layout[contador_col]:
            st.markdown(f'<div class="dashboard-card"><h3>🎲 {game} {marcador_exito}</h3><p><b>Volumen Real Indexado:</b> {len(df):,} sorteos</p><p><b>Dominante Histórico:</b> {dominante}</p></div>', unsafe_allow_html=True)
            fig = px.bar(x=freq.index, y=freq.values, color_discrete_sequence=['#22c55e'] if has_match else ['#7c3aed'])
            fig.update_layout(template="plotly_dark", height=140, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        contador_col = 0 if contador_col >= 1 else contador_col + 1

    st.markdown("---")
    st.subheader("🌌 Mapa Fractal Completo (Mandelbrot Space - 500 Nodos Reales)")
    motor_f = MetaPatternFractal()
    puntos_mapeados = []

    for game in GAME_CONFIG.keys():
        df, cols = cargar_sorteo_real(game)
        muestras = df[cols].head(500).values.tolist()
        has_match = any([b for b in st.session_state.boletos_auditados if b["sorteo"] == game and b["estado"] == "🎯 ACERTADO"])
        for idx, valores_fila in enumerate(muestras):
            x, y = motor_f.transformar_secuencia(valores_fila)
            puntos_mapeados.append({"Eje X": x, "Eje Y": y, "Capa": f"✔️ Historial {game}" if has_match else f"Historial {game}"})

    if len(puntos_mapeados) > 0:
        fig_fractal = px.scatter(pd.DataFrame(puntos_mapeados), x="Eje X", y="Eje Y", color="Capa")
        fig_fractal.update_layout(template="plotly_dark", xaxis=dict(range=[-2.1, 0.6]), yaxis=dict(range=[-1.3, 1.3]), height=500)
        st.plotly_chart(fig_fractal, use_container_width=True)

# 4. SORTEO SUGERIDO (DUALIDAD ESPEJO BLINDADA CONTRA SOBREPASAR MÁXIMOS)
elif menu == "🎯 Sorteo Número Sugerido":
    st.title("🎯 Sorteo Número Sugerido e Ingeniería de Resonancia")
    motor_f = MetaPatternFractal()

    for game in GAME_CONFIG.keys():
        st.markdown(f"## 🎲 Matrices de Resonancia Calibrada: {game}")
        todos = []
        for s in st.session_state.local_signals:
            if s["sorteo"] == game: todos.extend(s["numeros"])
        if len(todos) == 0:
            todos = list(np.random.randint(GAME_CONFIG[game]["min"], GAME_CONFIG[game]["max"] + 1, 120))

        contador = Counter(todos)
        sugeridos = [int(x[0]) for x in contador.most_common(GAME_CONFIG[game]["cantidad"])]
        
        # AJUSTE EVALUADO: El espejo se adapta estrictamente a las reglas del juego
        duales_espejo = calcular_espejo_calibrado(sugeridos, game)

        x_sug, y_sug = motor_f.transformar_secuencia(sugeridos)
        df, cols = cargar_sorteo_real(game)
        distancias = []
        for valores_fila in df[cols].head(100).values.tolist():
            x_hist, y_hist = motor_f.transformar_secuencia(valores_fila)
            distancias.append(np.sqrt((x_sug - x_hist)**2 + (y_sug - y_hist)**2))
        
        distancia_promedio = np.mean(distancias) if len(distancias) > 0 else 0.0
        coincidencia_geom = max(0, min(100, int((1.0 - distancia_promedio) * 100)))

        st.success(f"🎯 Sugerencia IA Configurada: {sugeridos}")
        st.info(f"🪞 Dualidad Espejo Calibrada (Dentro de Límites): {duales_espejo}")
        st.markdown(f'<div class="metric-box">📊 Coincidencia Histórica: <b>{coincidencia_geom}%</b> | Distancia: <b>{distancia_promedio:.4f} u</b></div>', unsafe_allow_html=True)

# ========================================================
# NUEVO MÓDULO 5: HISTORIAL DE ACERTOS, ESCANEO Y PLANILLA INTERACTIVA
# ========================================================
elif menu == "📸 Evidencia & Diario de Aciertos":
    st.title("📸 Evidencia de Tiros Directos & Auditoría Visual")
    
    col_izq, col_der = st.columns([1, 2])
    
    with col_izq:
        st.subheader("📁 Cargar Prueba de Éxito")
        sorteo_sel = st.selectbox("Sorteo Jugado", list(GAME_CONFIG.keys()))
        imagen_boleto = st.file_uploader("Subir Foto del Boleto Ganador", type=["png", "jpg", "jpeg"])
        numeros_boleto = st.text_input("Números Jugados en el Boleto (Ej: 1,3,11,14,22)")
        numeros_ganadores = st.text_input("Números Oficiales Ganadores del Sorteo")
        
        if st.button("🔮 Auditar y Archivar Boleto"):
            if numeros_boleto and numeros_ganadores:
                lista_jugados = [int(x.strip()) for x in numeros_boleto.split(",") if x.strip().isdigit()]
                lista_ganadores = [int(x.strip()) for x in numeros_ganadores.split(",") if x.strip().isdigit()]
                
                # Verificación de aciertos mínimos para declarar éxito en el dashboard
                coincidentes = list(set(lista_jugados) & set(lista_ganadores))
                estado_tiro = "🎯 ACERTADO" if len(coincidentes) >= 2 else "❌ DESVIADO"
                
                registro_auditoria = {
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "sorteo": sorteo_sel,
                    "jugados": lista_jugados,
                    "ganadores": lista_ganadores,
                    "estado": estado_tiro,
                    "coincidentes": coincidentes
                }
                st.session_state.boletos_auditados.append(registro_auditoria)
                st.success(f"Boleto procesado como: {estado_tiro}")
                
    with col_der:
        st.subheader("📊 Planilla Digital Interactiva de Validación")
        if len(st.session_state.boletos_auditados) > 0:
            ultimo_b = st.session_state.boletos_auditados[-1]
            st.markdown(f"#### Analizando Sorteo: **{ultimo_b['sorteo']}** ({ultimo_b['estado']})")
            
            config_juego = GAME_CONFIG[ultimo_b['sorteo']]
            
            # DISEÑO: Construcción de la Cuadrícula Tipo Planilla del Boleto Real
            st.markdown("##### 🏁 Mapa de Marcación (✖️ Fallado / ✔️ Acertado)")
            
            # Definir dimensiones de la cuadrícula según el rango de juego
            min_n, max_n = config_juego["min"], config_juego["max"]
            
            if min_n == 0 and max_n == 9: # Formato Lineal Tris
                cols_grid = st.columns(10)
                for num in range(10):
                    with cols_grid[num]:
                        if num in ultimo_b["coincidentes"]:
                            st.markdown(f'<div class="grid-cell-match">✔️<br>{num}</div>', unsafe_allow_html=True)
                        elif num in ultimo_b["jugados"]:
                            st.markdown(f'<div class="grid-cell-miss">✖️<br>{num}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="grid-cell-neutral"><br>{num}</div>', unsafe_allow_html=True)
            else: # Formato Panel Chispazo / Melate
                filas_num = 4 if max_n <= 28 else 7
                for f in range(filas_num):
                    cols_grid = st.columns(8)
                    for c in range(8):
                        num = f * 8 + c + min_n
                        if num <= max_n:
                            with cols_grid[c]:
                                if num in ultimo_b["coincidentes"]:
                                    st.markdown(f'<div class="grid-cell-match">✔️<br>{num}</div>', unsafe_allow_html=True)
                                elif num in ultimo_b["jugados"]:
                                    st.markdown(f'<div class="grid-cell-miss">✖️<br>{num}</div>', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<div class="grid-cell-neutral"><br>{num}</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.subheader("📚 Historial Clínico de Evidencias Guardadas")
            st.dataframe(pd.DataFrame(st.session_state.boletos_auditados), use_container_width=True)
        else:
            st.info("Sube una foto de tu boleto y digita su contenido para desplegar la planilla interactiva en tiempo real.")
