import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="EDA Energía Renovable", layout="wide")

# Título de la aplicación
st.title("📊 Análisis Exploratorio de Datos: Plantas de Energía Renovable")
st.markdown("Esta aplicación permite explorar el estado, capacidad y eficiencia de los proyectos de energía.")

# Carga de datos
@st.cache_data
def load_data():
    df = pd.read_csv('energia_renovable.csv')
    df['Fecha_Entrada_Operacion'] = pd.to_datetime(df['Fecha_Entrada_Operacion'])
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("No se encontró el archivo 'energia_renovable.csv'. Asegúrate de que esté en el mismo directorio.")
    st.stop()

# --- SIDEBAR: Filtros ---
st.sidebar.header("Filtros de Datos")
tecnologia_filter = st.sidebar.multiselect(
    "Selecciona Tecnología:",
    options=df["Tecnologia"].unique(),
    default=df["Tecnologia"].unique()
)

operador_filter = st.sidebar.multiselect(
    "Selecciona Operador:",
    options=df["Operador"].unique(),
    default=df["Operador"].unique()
)

# Aplicar filtros
df_filtered = df[
    (df["Tecnologia"].isin(tecnologia_filter)) & 
    (df["Operador"].isin(operador_filter))
]

# --- SECCIÓN 1: Métricas Clave ---
st.header("📌 Indicadores Clave (KPIs)")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Total Proyectos", len(df_filtered))
with kpi2:
    st.metric("Capacidad Total (MW)", f"{df_filtered['Capacidad_Instalada_MW'].sum():,.1f}")
with kpi3:
    st.metric("Eficiencia Promedio", f"{df_filtered['Eficiencia_Planta_Pct'].mean():.1f}%")
with kpi4:
    st.metric("Inversión Total (MUSD)", f"${df_filtered['Inversion_Inicial_MUSD'].sum():,.1f}")

# --- SECCIÓN 2: Vista de Datos ---
with st.expander("Ver tabla de datos completa"):
    st.dataframe(df_filtered, use_container_width=True)

# --- SECCIÓN 3: Análisis Visual ---
st.header("📈 Análisis Visual")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribución por Tecnología")
    fig_pie = px.pie(df_filtered, names='Tecnologia', values='Capacidad_Instalada_MW', hole=0.4,
                     title="Capacidad Instalada (MW) por Tecnología")
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Estado de los Proyectos")
    fig_bar_estado = px.bar(df_filtered.groupby('Estado_Actual').size().reset_index(name='Conteo'), 
                            x='Estado_Actual', y='Conteo', color='Estado_Actual',
                            title="Cantidad de Proyectos por Estado")
    st.plotly_chart(fig_bar_estado, use_container_width=True)

# --- SECCIÓN 4: Relaciones y Correlaciones ---
st.header("🔍 Relaciones entre Variables")
col3, col4 = st.columns(2)

with col3:
    st.subheader("Capacidad vs Generación Diaria")
    fig_scatter = px.scatter(df_filtered, x='Capacidad_Instalada_MW', y='Generacion_Diaria_MWh',
                             color='Tecnologia', hover_name='ID_Proyecto',
                             title="Capacidad (MW) vs Generación (MWh)")
    st.plotly_chart(fig_scatter, use_container_width=True)

with col4:
    st.subheader("Eficiencia por Tecnología")
    fig_box = px.box(df_filtered, x='Tecnologia', y='Eficiencia_Planta_Pct', color='Tecnologia',
                     title="Distribución de Eficiencia (%)")
    st.plotly_chart(fig_box, use_container_width=True)

# --- SECCIÓN 5: Análisis Temporal ---
st.header("📅 Evolución Temporal")
df_timeline = df_filtered.sort_values("Fecha_Entrada_Operacion")
df_timeline['Capacidad_Acumulada'] = df_timeline['Capacidad_Instalada_MW'].cumsum()

fig_line = px.line(df_timeline, x='Fecha_Entrada_Operacion', y='Capacidad_Acumulada',
                   title="Crecimiento de la Capacidad Instalada Acumulada")
st.plotly_chart(fig_line, use_container_width=True)

# Footer
st.info("Desarrollado con Streamlit para el análisis de Energías Renovables.")
