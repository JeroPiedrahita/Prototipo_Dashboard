import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Ingeniería EDA Pro", layout="wide", page_icon="⚙️")

# --- DISEÑO DE INTERFAZ Y TARJETAS (CSS AVANZADO) ---
st.markdown("""
    <style>
    /* Fondo general */
    .main { background-color: #f4f7f9; }
    
    /* Personalización de Tarjetas de Métricas */
    [data-testid="stMetric"] {
        background-color: #1E293B; /* Azul oscuro pizarra */
        padding: 20px;
        border-radius: 12px;
        color: #FFFFFF;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        border: 1px solid #334155;
    }
    
    /* Color del Título de la métrica */
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important; 
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.9rem;
    }

    /* Color del Valor de la métrica */
    [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-size: 1.8rem;
    }

    /* Tabs personalizados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF;
        border-radius: 5px 5px 0px 0px;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛠️ Analizador de Ingeniería y Datos Complejos")
st.markdown("Dashboard dinámico para análisis exploratorio profundo con segmentación de muestras.")

# --- BARRA LATERAL: CARGA Y FILTROS ---
st.sidebar.header("📁 Gestión de Datos")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    # Carga inicial
    df_raw = pd.read_csv(uploaded_file)
    
    # --- SELECTOR DE MUESTRAS ---
    st.sidebar.divider()
    st.sidebar.subheader("🔢 Control de Muestreo")
    total_filas = len(df_raw)
    num_muestras = st.sidebar.slider(
        "Muestras a procesar:", 
        min_value=1, 
        max_value=total_filas, 
        value=min(100, total_filas)
    )
    
    # DataFrame procesado según el slider
    df = df_raw.head(num_muestras).copy()

    # Identificación de tipos de columnas
    cat_cols = df.select_dtypes(include=['object', 'bool', 'category']).columns.tolist()
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    date_cols = [col for col in df.columns if 'fecha' in col.lower() or 'date' in col.lower()]
    
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    # --- MÉTRICAS SUPERIORES ---
    st.subheader("📌 Resumen de Muestreo")
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("Muestras", f"{df.shape[0]:,}")
    with k2: st.metric("Variables", f"{df.shape[1]}")
    with k3: st.metric("Datos Nulos", f"{df.isnull().sum().sum()}")
    with k4: 
        variedad = df[cat_cols[0]].nunique() if cat_cols else 0
        st.metric("Diversidad Cat.", variedad)

    st.divider()

    # --- NAVEGACIÓN PRINCIPAL ---
    tab_cat, tab_num, tab_rel, tab_corr, tab_raw = st.tabs([
        "🏷️ Cualitativo", "🔢 Cuantitativo", "🔍 Relaciones", "🧬 Estadístico", "📄 Tabla"
    ])

    # 1. ANÁLISIS CUALITATIVO
    with tab_cat:
        if cat_cols:
            c1, c2 = st.columns([1, 2])
            with c1:
                cat_var = st.selectbox("Categoría:", cat_cols, key="tab1_cat")
                chart_style = st.radio("Estilo:", ["Barras", "Donut", "Treemap"])
            with c2:
                counts = df[cat_var].value_counts().reset_index()
                counts.columns = [cat_var, 'Conteo']
                
                if chart_style == "Barras":
                    fig = px.bar(counts, x=cat_var, y='Conteo', color=cat_var, text_auto=True)
                elif chart_style == "Donut":
                    fig = px.pie(counts, names=cat_var, values='Conteo', hole=0.5)
                else:
                    fig = px.treemap(counts, path=[cat_var], values='Conteo')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay columnas categóricas.")

    # 2. ANÁLISIS CUANTITATIVO
    with tab_num:
        if num_cols:
            c3, c4 = st.columns([1, 3])
            with c3:
                num_var = st.selectbox("Variable:", num_cols, key="tab2_num")
                hue_var = st.selectbox("Segmentar por:", [None] + cat_cols, key="tab2_hue")
            with c4:
                fig_num = px.histogram(df, x=num_var, color=hue_var, marginal="box", 
                                       title=f"Distribución Técnica de {num_var}",
                                       barmode="overlay", opacity=0.7)
                st.plotly_chart(fig_num, use_container_width=True)
        else:
            st.warning("No hay columnas numéricas.")

    # 3. RELACIONES
    with tab_rel:
        if len(num_cols) >= 2:
            r1, r2, r3, r4 = st.columns(4)
            with r1: x_ax = st.selectbox("Eje X:", num_cols, key="relx")
            with r2: y_ax = st.selectbox("Eje Y:", num_cols, index=1, key="rely")
            with r3: c_ax = st.selectbox("Color:", [None] + cat_cols, key="relc")
            with r4: s_ax = st.selectbox("Tamaño:", [None] + num_cols, key="rels")
            
            fig_scat = px.scatter(df, x=x_ax, y=y_ax, color=c_ax, size=s_ax,
                                  title=f"Dispersión: {x_ax} vs {y_ax}", template="plotly_white")
            st.plotly_chart(fig_scat, use_container_width=True)
        else:
            st.info("Se necesitan más datos numéricos.")

    # 4. ESTADÍSTICO (SEABORN)
    with tab_corr:
        if len(num_cols) > 1:
            st.subheader("Matriz de Correlación (Pearson)")
            fig_sns, ax = plt.subplots(figsize=(12, 6))
            sns.heatmap(df[num_cols].corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
            st.pyplot(fig_sns)
        else:
            st.info("Sin suficientes variables numéricas para correlación.")

    # 5. TABLA DE DATOS
    with tab_raw:
        st.write(f"Mostrando las primeras {num_muestras} filas del archivo:")
        st.dataframe(df, use_container_width=True)
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Selección en CSV", csv_data, "muestreo_datos.csv", "text/csv")

else:
    # Pantalla de bienvenida
    st.info("👋 Bienvenido. Por favor, sube un archivo CSV en el panel lateral para comenzar.")
    st.markdown("""
    Este dashboard permite:
    - **Muestreo en tiempo real** mediante la barra deslizante lateral.
    - **Análisis de outliers** con diagramas de caja marginales.
    - **Correlación estadística** profunda con mapas de calor.
    - **Visualización jerárquica** con Treemaps.
    """)
