import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="EDA Avanzado Energía", layout="wide", page_icon="🌱")

# Estilos personalizados
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stMetric { border: 1px solid #d1d5db; padding: 15px; border-radius: 8px; background: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Dashboard de Análisis Exploratorio (EDA) Profesional")
st.markdown("Carga tus datos para descubrir patrones cuantitativos, cualitativos y correlaciones.")

# --- CARGA DE DATOS ---
uploaded_file = st.sidebar.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    # Cargar datos
    df = pd.read_csv(uploaded_file)
    
    # Preprocesamiento automático
    if 'Fecha_Entrada_Operacion' in df.columns:
        df['Fecha_Entrada_Operacion'] = pd.to_datetime(df['Fecha_Entrada_Operacion'])
    
    # Identificar tipos de variables
    cat_cols = df.select_dtypes(include=['object', 'bool']).columns.tolist()
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    # --- SIDEBAR: FILTROS MAESTROS ---
    st.sidebar.header("⚙️ Filtros Globales")
    selected_operador = st.sidebar.multiselect(
        "Filtrar por Operador:", 
        options=df['Operador'].unique() if 'Operador' in df.columns else [],
        default=df['Operador'].unique() if 'Operador' in df.columns else []
    )
    
    # Aplicar filtro global
    df_filtered = df[df['Operador'].isin(selected_operador)] if 'Operador' in df.columns else df

    # --- MÉTRICAS ---
    st.subheader("📌 Indicadores Clave")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Proyectos", len(df_filtered))
    with m2:
        val = df_filtered['Capacidad_Instalada_MW'].sum() if 'Capacidad_Instalada_MW' in df_filtered.columns else 0
        st.metric("Capacidad Total", f"{val:,.1f} MW")
    with m3:
        val = df_filtered['Eficiencia_Planta_Pct'].mean() if 'Eficiencia_Planta_Pct' in df_filtered.columns else 0
        st.metric("Eficiencia Media", f"{val:.1f}%")
    with m4:
        val = df_filtered['Inversion_Inicial_MUSD'].sum() if 'Inversion_Inicial_MUSD' in df_filtered.columns else 0
        st.metric("Inversión Total", f"${val:,.1f}M")

    st.divider()

    # --- SECCIÓN 1: ANÁLISIS CUALITATIVO (CATEGÓRICO) ---
    st.header("📊 Análisis Cualitativo")
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.write("### Configuración")
        cat_var = st.selectbox("Variable Categórica:", cat_cols)
        color_palette = st.selectbox("Paleta de Color:", ["Set1", "Set2", "Pastel1", "Dark2"])
        chart_type = st.radio("Gráfico:", ["Donut", "Barras"], horizontal=True)

    with col_b:
        if chart_type == "Donut":
            fig_cat = px.pie(df_filtered, names=cat_var, hole=0.5, 
                             color_discrete_sequence=px.colors.qualitative.Alphabet)
        else:
            counts = df_filtered[cat_var].value_counts().reset_index()
            fig_cat = px.bar(counts, x='index', y=cat_var, color='index', labels={'index': cat_var, cat_var: 'Conteo'})
        st.plotly_chart(fig_cat, use_container_width=True)

    st.divider()

    # --- SECCIÓN 2: ESTADO DEL PROYECTO (FILTRO AMIGABLE) ---
    st.header("🎯 Zoom por Energía y Estado")
    
    # Filtro específico solicitado por el usuario dentro del main
    col_filt, col_viz = st.columns([1, 3])
    
    with col_filt:
        st.markdown("### 🔍 Filtrar esta vista")
        if 'Tecnologia' in df_filtered.columns:
            energias_especificas = st.multiselect(
                "Ver solo estas energías:",
                options=df_filtered['Tecnologia'].unique(),
                default=df_filtered['Tecnologia'].unique(),
                key="filter_energy_status"
            )
            df_status_viz = df_filtered[df_filtered['Tecnologia'].isin(energias_especificas)]
        else:
            df_status_viz = df_filtered

    with col_viz:
        if not df_status_viz.empty and 'Estado_Actual' in df_status_viz.columns:
            fig_status = px.histogram(
                df_status_viz, 
                x="Estado_Actual", 
                color="Tecnologia" if 'Tecnologia' in df_status_viz.columns else None,
                barmode="group",
                title="Distribución de Estados según Energía Seleccionada",
                text_auto=True
            )
            st.plotly_chart(fig_status, use_container_width=True)

    st.divider()

    # --- SECCIÓN 3: ANÁLISIS CUANTITATIVO Y CORRELACIÓN ---
    st.header("📈 Análisis Cuantitativo y Estadístico")
    
    tab_dist, tab_corr = st.tabs(["Distribuciones", "Mapa de Correlación (Seaborn)"])
    
    with tab_dist:
        col_c1, col_c2 = st.columns([1, 2])
        with col_c1:
            num_var = st.selectbox("Eje X (Numérico):", num_cols)
            y_var = st.selectbox("Eje Y (Numérico):", num_cols, index=1 if len(num_cols)>1 else 0)
            group_var = st.selectbox("Agrupar por Color:", [None] + cat_cols)
        with col_c2:
            fig_scatter = px.scatter(df_filtered, x=num_var, y=y_var, color=group_var,
                                     marginal_x="box", marginal_y="violin",
                                     title=f"Relación: {num_var} vs {y_var}")
            st.plotly_chart(fig_scatter, use_container_width=True)

    with tab_corr:
        st.write("### Matriz de Correlación de Pearson")
        if len(num_cols) > 1:
            # Uso de Matplotlib y Seaborn
            fig_sns, ax = plt.subplots(figsize=(10, 6))
            corr_matrix = df_filtered[num_cols].corr()
            sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax, linewidths=0.5)
            st.pyplot(fig_sns)
        else:
            st.warning("No hay suficientes variables numéricas para una correlación.")

    # --- TABLA FINAL ---
    with st.expander("📄 Ver Datos Crudos y Descargar"):
        st.dataframe(df_filtered, use_container_width=True)

else:
    st.info("👋 Bienvenido al sistema de EDA. Por favor, carga un archivo CSV en la barra lateral para comenzar.")
    # Imagen decorativa usando matplotlib para mostrar que la librería funciona
    fig_init, ax_init = plt.subplots()
    ax_init.text(0.5, 0.5, 'Esperando datos...', fontsize=20, ha='center')
    ax_init.axis('off')
    st.pyplot(fig_init)
