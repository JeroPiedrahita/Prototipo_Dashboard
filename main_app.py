import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Ultra EDA Dashboard", layout="wide", page_icon="📈")

# CSS para mejorar la estética
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Sistema de Análisis Exploratorio Profundo")
st.markdown("Herramienta avanzada para la inspección visual y estadística de datos.")

# --- CARGA Y PROCESAMIENTO ---
uploaded_file = st.sidebar.file_uploader("📂 Carga tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Detección automática de tipos
    cat_cols = df.select_dtypes(include=['object', 'bool', 'category']).columns.tolist()
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    date_cols = []
    
    for col in df.columns:
        if 'fecha' in col.lower() or 'date' in col.lower() or 'Fecha' in col:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            date_cols.append(col)

    # --- MÉTRICAS DE RESUMEN ---
    st.subheader("📌 Panorama General")
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("Filas", f"{df.shape[0]:,}")
    with k2: st.metric("Columnas", f"{df.shape[1]}")
    with k3: st.metric("Celdas Nulas", f"{df.isnull().sum().sum()}")
    with k4: st.metric("Duplicados", f"{df.duplicated().sum()}")

    st.divider()

    # --- MENÚ DE NAVEGACIÓN ---
    menu = st.tabs([
        "📊 Estructura y Calidad", 
        "🏷️ Análisis Categórico", 
        "🔢 Análisis Numérico", 
        "🧬 Correlaciones",
        "🕒 Series Temporales",
        "🧪 Relaciones Cruzadas"
    ])

    # --- TAB 1: ESTRUCTURA ---
    with menu[0]:
        st.header("Análisis de Estructura")
        col_et1, col_et2 = st.columns(2)
        with col_et1:
            st.write("**Tipos de Datos:**")
            st.write(df.dtypes.astype(str))
        with col_et2:
            st.write("**Resumen Estadístico:**")
            st.write(df.describe())

    # --- TAB 2: CATEGÓRICO ---
    with menu[1]:
        st.header("Análisis de Composición y Categorías")
        cat_sel = st.selectbox("Selecciona Categoría:", cat_cols, key="ext_cat")
        
        c_cat1, c_cat2 = st.columns(2)
        with c_cat1:
            counts = df[cat_sel].value_counts().reset_index()
            counts.columns = [cat_sel, 'Cantidad']
            fig_bar = px.bar(counts, x=cat_sel, y='Cantidad', color=cat_sel, title=f"Frecuencia de {cat_sel}")
            st.plotly_chart(fig_bar, use_container_width=True)
        with c_cat2:
            # Treemap para ver jerarquía
            fig_tree = px.treemap(df, path=[cat_sel], title=f"Mapa Jerárquico de {cat_sel}")
            st.plotly_chart(fig_tree, use_container_width=True)

    # --- TAB 3: NUMÉRICO ---
    with menu[2]:
        st.header("Análisis de Distribuciones")
        num_sel = st.selectbox("Selecciona Variable Numérica:", num_cols, key="ext_num")
        group_sel = st.selectbox("Segmentar por (opcional):", [None] + cat_cols, key="ext_group")
        
        c_num1, c_num2 = st.columns(2)
        with c_num1:
            fig_hist = px.histogram(df, x=num_sel, color=group_sel, marginal="violin", title=f"Distribución/Violín de {num_sel}")
            st.plotly_chart(fig_hist, use_container_width=True)
        with c_num2:
            fig_box = px.box(df, x=group_sel if group_sel else None, y=num_sel, color=group_sel, title=f"Boxplot de {num_sel}")
            st.plotly_chart(fig_box, use_container_width=True)

    # --- TAB 4: CORRELACIONES ---
    with menu[3]:
        st.header("Análisis de Dependencias")
        if len(num_cols) > 1:
            fig_corr, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(df[num_cols].corr(), annot=True, cmap="RdBu", fmt=".2f", ax=ax)
            st.pyplot(fig_corr)
        else:
            st.info("No hay suficientes columnas numéricas.")

    # --- TAB 5: SERIES TEMPORALES ---
    with menu[4]:
        st.header("Evolución en el Tiempo")
        if date_cols:
            t_col = st.selectbox("Columna de Fecha:", date_cols)
            y_col = st.selectbox("Variable a medir:", num_cols, key="time_y")
            
            # Agregación temporal
            df_time = df.sort_values(t_col)
            fig_line = px.line(df_time, x=t_col, y=y_col, title=f"Evolución de {y_col} a través de {t_col}")
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("No se detectaron columnas de fecha para este análisis.")

    # --- TAB 6: RELACIONES CRUZADAS ---
    with menu[5]:
        st.header("Análisis de Multivariables")
        col_rel1, col_rel2, col_rel3 = st.columns(3)
        with col_rel1: x_rel = st.selectbox("Eje X:", num_cols, index=0)
        with col_rel2: y_rel = st.selectbox("Eje Y:", num_cols, index=min(1, len(num_cols)-1))
        with col_rel3: color_rel = st.selectbox("Color:", [None] + cat_cols, key="rel_col")
        
        fig_scatter = px.scatter(df, x=x_rel, y=y_rel, color=color_rel, 
                                 size=num_cols[0], hover_data=cat_cols,
                                 title=f"Dispersión: {x_rel} vs {y_rel}")
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- VISTA DE DATOS ---
    with st.expander("📄 Explorador de Datos Crudos"):
        st.dataframe(df, use_container_width=True)

else:
    st.info("👋 Sube un archivo CSV para generar el reporte extenso.")
