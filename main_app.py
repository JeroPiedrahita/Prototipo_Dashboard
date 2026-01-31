import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE INTERFAZ ---
st.set_page_config(page_title="Universal Engineering EDA", layout="wide", page_icon="⚙️")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🛠️ Analizador de Datos de Ingeniería")
st.markdown("Sube cualquier conjunto de datos para generar un análisis exploratorio automatizado.")

# --- CARGA DINÁMICA DE ARCHIVOS ---
uploaded_file = st.sidebar.file_uploader("📂 Carga tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    # Lectura del archivo
    df = pd.read_csv(uploaded_file)
    
    # Identificación automática de tipos de datos
    # Cualitativos (Categorías)
    cat_cols = df.select_dtypes(include=['object', 'bool', 'category']).columns.tolist()
    # Cuantitativos (Números)
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    # Temporales (Fechas)
    for col in df.columns:
        if 'fecha' in col.lower() or 'date' in col.lower():
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # --- MÉTRICAS GENERALES ---
    st.subheader("📈 Resumen del Conjunto de Datos")
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("Total de Registros", f"{df.shape[0]:,}")
    with kpi2:
        st.metric("Variables Detectadas", f"{df.shape[1]}")
    with kpi3:
        missing = df.isnull().sum().sum()
        st.metric("Datos Faltantes", f"{missing}", delta_color="inverse")

    st.divider()

    # --- SECCIÓN 1: ANÁLISIS CUALITATIVO ---
    st.header("📊 Variables Cualitativas (Categorías)")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        cat_var = st.selectbox("Selecciona la categoría a analizar:", cat_cols, key="cat_sel")
        chart_type = st.radio("Formato de visualización:", ["Donut", "Barras Horizontales"])
        
    with col2:
        # Corrección de nombres para compatibilidad con Pandas 2.0+
        counts = df[cat_var].value_counts().reset_index()
        counts.columns = ['Categoría', 'Conteo']
        
        if chart_type == "Donut":
            fig_cat = px.pie(counts, names='Categoría', values='Conteo', hole=0.5,
                             title=f"Distribución porcentual de {cat_var}")
        else:
            fig_cat = px.bar(counts, x='Conteo', y='Categoría', orientation='h', 
                             color='Categoría', title=f"Frecuencia por {cat_var}")
        st.plotly_chart(fig_cat, use_container_width=True)

    st.divider()

    # --- SECCIÓN 2: ANÁLISIS CUANTITATIVO Y ESTADÍSTICO ---
    st.header("🔢 Variables Cuantitativas (Numéricas)")
    
    tab_dist, tab_corr = st.tabs(["Distribución y Outliers", "Matriz de Correlación"])
    
    with tab_dist:
        col_c1, col_c2 = st.columns([1, 3])
        with col_c1:
            var_num = st.selectbox("Variable numérica:", num_cols, key="num_sel")
            group_by = st.selectbox("Agrupar por (opcional):", [None] + cat_cols)
        with col_c2:
            fig_dist = px.histogram(df, x=var_num, color=group_by, marginal="box", 
                                    title=f"Histograma y Diagrama de Caja de {var_num}",
                                    opacity=0.7, barmode="overlay")
            st.plotly_chart(fig_dist, use_container
