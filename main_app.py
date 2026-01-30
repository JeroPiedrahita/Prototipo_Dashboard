import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Energía Renovable", layout="wide")

# Estilo para mejorar la visualización
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Dashboard de Proyectos Energéticos")

# --- CARGA DE DATOS ---
uploaded_file = st.sidebar.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Preprocesamiento de fechas
    if 'Fecha_Entrada_Operacion' in df.columns:
        df['Fecha_Entrada_Operacion'] = pd.to_datetime(df['Fecha_Entrada_Operacion'])

    # --- FILTROS GLOBALES ---
    st.sidebar.header("⚙️ Filtros Globales")
    operadores = df['Operador'].unique().tolist()
    operador_sel = st.sidebar.multiselect("Filtrar por Operador:", operadores, default=operadores)
    
    df_global = df[df['Operador'].isin(operador_sel)]

    # --- MÉTRICAS (CORREGIDAS) ---
    st.header("📌 Resumen General")
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("Total Proyectos", len(df_global))
    with m2:
        # Aquí estaba el error: se cerró correctamente el f-string y los corchetes
        capacidad = df_global['Capacidad_Instalada_MW'].sum()
        st.metric("Capacidad Total", f"{capacidad:,.1f} MW")
    with m3:
        eficiencia = df_global['Eficiencia_Planta_Pct'].mean()
        st.metric("Eficiencia Media", f"{eficiencia:.1f}%")
    with m4:
        inversion = df_global['Inversion_Inicial_MUSD'].sum()
        st.metric("Inversión Total", f"${inversion:,.1f}M")

    st.divider()

    # --- SECCIÓN: GRÁFICA CON FILTRO AMIGABLE ---
    st.header("📊 Estado de Proyectos por Energía")
    
    col_chart, col_filter = st.columns([3, 1])

    with col_filter:
        st.subheader("🎯 Filtro de Gráfica")
        tecs_disponibles = df_global['Tecnologia'].unique().tolist()
        # Selección amigable para el usuario
        tecs_seleccionadas = st.multiselect(
            "Selecciona tipo de energía:",
            options=tecs_disponibles,
            default=tecs_disponibles
        )

    with col_chart:
        df_status = df_global[df_global['Tecnologia'].isin(tecs_seleccionadas)]
        
        if not df_status.empty:
            fig_status = px.histogram(
                df_status, 
                x="Estado_Actual", 
                color="Tecnologia",
                barmode="group",
                title="Distribución por Estado",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.warning("Selecciona al menos una tecnología para visualizar la gráfica.")

    # --- TABLA DE DATOS ---
    with st.expander("🔍 Ver tabla de datos filtrados"):
        st.dataframe(df_global, use_container_width=True)

else:
    st.info("👋 Por favor, sube el archivo CSV desde la barra lateral para generar el reporte.")
