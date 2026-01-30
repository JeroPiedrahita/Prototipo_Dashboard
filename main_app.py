import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="EDA Dinámico - Energía Renovable", layout="wide")

st.title("📊 Herramienta de Análisis Exploratorio de Datos (EDA)")
st.markdown("Sube tu archivo CSV para generar visualizaciones automáticas sobre proyectos de energía.")

# --- SECCIÓN: Carga de Archivo ---
uploaded_file = st.sidebar.file_uploader("Sube tu archivo .csv aquí", type=["csv"])

if uploaded_file is not None:
    # Leer el archivo subido
    df = pd.read_csv(uploaded_file)
    
    # Preprocesamiento básico (Convertir fechas si existe la columna)
    if 'Fecha_Entrada_Operacion' in df.columns:
        df['Fecha_Entrada_Operacion'] = pd.to_datetime(df['Fecha_Entrada_Operacion'])

    # --- SIDEBAR: Filtros Dinámicos ---
    st.sidebar.header("Filtros")
    
    # Filtro por Tecnología (si la columna existe)
    if 'Tecnologia' in df.columns:
        tecnologias = st.sidebar.multiselect("Tecnología", df['Tecnologia'].unique(), default=df['Tecnologia'].unique())
        df = df[df['Tecnologia'].isin(tecnologias)]

    # --- SECCIÓN 1: Métricas Principales ---
    st.header("📌 Resumen General")
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.metric("Total de Proyectos", len(df))
    with m2:
        if 'Capacidad_Instalada_MW' in df.columns:
            total_cap = df['Capacidad_Instalada_MW'].sum()
            st.metric("Capacidad Total", f"{total_cap:,.1f} MW")
    with m3:
        if 'Inversion_Inicial_MUSD' in df.columns:
            total_inv = df['Inversion_Inicial_MUSD'].sum()
            st.metric("Inversión Total", f"${total_inv:,.1f} MUSD")

    # --- SECCIÓN 2: Visualizaciones ---
    st.header("📈 Visualizaciones")
    
    col1, col2 = st.columns(2)

    with col1:
        if 'Tecnologia' in df.columns:
            st.subheader("Distribución por Tecnología")
            fig1 = px.pie(df, names='Tecnologia', title="Proyectos por Tipo")
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        if 'Estado_Actual' in df.columns:
            st.subheader("Estado de Proyectos")
            fig2 = px.histogram(df, x='Estado_Actual', color='Estado_Actual', title="Conteo por Estado")
            st.plotly_chart(fig2, use_container_width=True)

    # --- SECCIÓN 3: Relación de Variables ---
    if 'Capacidad_Instalada_MW' in df.columns and 'Generacion_Diaria_MWh' in df.columns:
        st.subheader("Relación: Capacidad vs Generación")
        fig3 = px.scatter(df, x='Capacidad_Instalada_MW', y='Generacion_Diaria_MWh', 
                          color='Tecnologia' if 'Tecnologia' in df.columns else None,
                          size='Eficiencia_Planta_Pct' if 'Eficiencia_Planta_Pct' in df.columns else None,
                          hover_data=['ID_Proyecto'] if 'ID_Proyecto' in df.columns else None)
        st.plotly_chart(fig3, use_container_width=True)

    # Mostrar Datos
    with st.expander("Ver Datos Crudos"):
        st.write(df)

else:
    # Mensaje si no hay archivo
    st.info("👋 Por favor, sube un archivo CSV desde la barra lateral para comenzar el análisis.")
    st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=200)
