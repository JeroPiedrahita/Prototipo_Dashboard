import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Universal EDA Pro", layout="wide", page_icon="📊")

st.title("🛠️ Analizador Exploratorio de Datos Universal")
st.markdown("Carga cualquier dataset CSV para realizar un análisis dinámico de variables.")

# --- CARGA DE DATOS ---
uploaded_file = st.sidebar.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Identificación automática de columnas
    cat_cols = df.select_dtypes(include=['object', 'bool', 'category']).columns.tolist()
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    # --- MÉTRICAS INICIALES ---
    st.subheader("📌 Resumen del Dataset")
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Filas / Registros", f"{df.shape[0]:,}")
    with m2: st.metric("Total Columnas", f"{df.shape[1]}")
    with m3: st.metric("Datos Faltantes", f"{df.isnull().sum().sum()}")

    st.divider()

    # --- SECCIÓN 1: ANÁLISIS CUALITATIVO (CATEGORÍAS) ---
    st.header("📊 Variables Cualitativas")
    if cat_cols:
        col1, col2 = st.columns([1, 2])
        with col1:
            cat_var = st.selectbox("Selecciona Categoría:", cat_cols)
            tipo_graf = st.radio("Tipo de visualización:", ["Donut", "Barras"])
        with col2:
            counts = df[cat_var].value_counts().reset_index()
            counts.columns = ['Categoría', 'Conteo']
            if tipo_graf == "Donut":
                fig = px.pie(counts, names='Categoría', values='Conteo', hole=0.5,
                             title=f"Proporción por {cat_var}")
            else:
                fig = px.bar(counts, x='Categoría', y='Conteo', color='Categoría',
                             title=f"Distribución de {cat_var}")
            st.plotly_chart(fig, use_container_width=True)
