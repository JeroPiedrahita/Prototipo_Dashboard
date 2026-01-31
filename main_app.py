import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Universal EDA Pro", layout="wide", page_icon="⚙️")

st.title("🛠️ Analizador de Datos Universal")

# --- CARGA DE ARCHIVOS ---
uploaded_file = st.sidebar.file_uploader("📂 Carga tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Identificación de columnas
    cat_cols = df.select_dtypes(include=['object', 'bool', 'category']).columns.tolist()
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    # --- MÉTRICAS ---
    st.subheader("📌 Resumen General")
    k1, k2, k3 = st.columns(3)
    with k1: st.metric("Registros", f"{df.shape[0]:,}")
    with k2: st.metric("Columnas", f"{df.shape[1]}")
    with k3: st.metric("Nulos", f"{df.isnull().sum().sum()}")

    st.divider()

    # --- SECCIÓN 1: CUALITATIVO ---
    st.header("📊 Análisis Cualitativo")
    c1, c2 = st.columns([1, 2])
    with c1:
        cat_var = st.selectbox("Variable Categórica:", cat_cols)
        tipo_graf = st.radio("Gráfico:", ["Donut", "Barras"])
    with c2:
        counts = df[cat_var].value_counts().reset_index()
        counts.columns = ['Categoría', 'Conteo']
        if tipo_graf == "Donut":
            fig = px.pie(counts, names='Categoría', values='Conteo', hole=0.5)
        else:
            fig = px.bar(counts, x='Categoría', y='Conteo', color='Categoría')
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- SECCIÓN 2: CUANTITATIVO (CORREGIDA) ---
    st.header("🔢 Análisis Cuantitativo")
    tab_dist, tab_corr = st.tabs(["Distribución", "Correlación"])
    
    with tab_dist:
        col_c1, col_c2 = st.columns([1, 3])
        with col_c1:
            var_num = st.selectbox("Variable numérica:", num_cols)
            # Filtro amigable: Color por categoría
            color_sel = st.selectbox("Agrupar por color:", [None] + cat_cols)
        with col_c2:
            # Gráfica con boxplot marginal para ver outliers
            fig_dist = px.histogram(
                df, 
                x=var_num, 
                color=color_sel, 
                marginal="box", 
                title=f"Distribución de {var_num}",
                barmode="overlay"
            )
            st.plotly_chart(fig_dist, use_container_width=True)

    with tab_corr:
        if len(num_cols) > 1:
            st.write("### Mapa de Calor (Seaborn)")
            fig_sns, ax = plt.subplots(figsize=(10, 5))
            sns.heatmap(df[num_cols].corr(), annot=True, cmap="YlGnBu", ax=
