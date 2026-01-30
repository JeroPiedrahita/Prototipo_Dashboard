import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración estética
st.set_page_config(page_title="Dashboard Energía Renovable", layout="wide")

# Estilo personalizado para mejorar la legibilidad
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Dashboard de Proyectos Energéticos")
st.write("Carga tu dataset y explora el estado de la transición energética.")

# --- CARGA DE DATOS ---
uploaded_file = st.sidebar.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Limpieza de fechas si existen
    if 'Fecha_Entrada_Operacion' in df.columns:
        df['Fecha_Entrada_Operacion'] = pd.to_datetime(df['Fecha_Entrada_Operacion'])

    # --- FILTROS GLOBALES ---
    st.sidebar.header("⚙️ Filtros Globales")
    
    # Selector amigable para Operadores
    operadores_disponibles = df['Operador'].unique().tolist()
    operador_sel = st.sidebar.multiselect("Filtrar por Operador:", operadores_disponibles, default=operadores_disponibles)
    
    # Aplicar filtro global de operador
    df_global = df[df['Operador'].isin(operador_sel)]

    # --- MÉTRICAS ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Proyectos", len(df_global))
    with m2:
        st.metric("Capacidad Total", f"{df_global['Capacidad
