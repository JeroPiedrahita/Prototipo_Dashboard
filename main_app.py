import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from groq import Groq

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Engineering EDA + AI Assistant", layout="wide", page_icon="⚙️")

# --- DISEÑO DE TARJETAS (CSS) ---
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #1E293B;
        padding: 20px;
        border-radius: 12px;
        color: #FFFFFF;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        border: 1px solid #334155;
    }
    [data-testid="stMetricLabel"] { color: #94A3B8 !important; font-weight: 600; }
    [data-testid="stMetricValue"] { color: #F8FAFC !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛠️ Analizador de Ingeniería con Asistente IA")

# --- BARRA LATERAL ---
st.sidebar.header("🔑 Configuración")
groq_api_key = st.sidebar.text_input("Groq API Key:", type="password", help="Introduce tu llave de Groq para habilitar a Llama 3.3")

st.sidebar.divider()
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    df_raw = pd.read_csv(uploaded_file)
    
    # Selector de muestras
    num_muestras = st.sidebar.slider("Muestras a procesar:", 1, len(df_raw), min(100, len(df_raw)))
    df = df_raw.head(num_muestras).copy()

    # Tipos de columnas
    cat_cols = df.select_dtypes(include=['object', 'bool']).columns.tolist()
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    # --- MÉTRICAS ---
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("Muestras", f"{len(df)}")
    with k2: st.metric("Columnas", f"{df.shape[1]}")
    with k3: st.metric("Nulos", f"{df.isnull().sum().sum()}")
    with k4: st.metric("Inversión Prom.", f"${df[num_cols[-1]].mean():.1f}M" if num_cols else "0")

    st.divider()

    # --- NAVEGACIÓN ---
    tabs = st.tabs(["📊 Visualización", "🧬 Estadística", "🤖 Asistente IA", "📄 Tabla"])

    with tabs[0]:
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            if cat_cols:
                v_cat = st.selectbox("Analizar Categoría:", cat_cols)
                st.plotly_chart(px.pie(df, names=v_cat, hole=0.4), use_container_width=True)
        with col_v2:
            if num_cols:
                v_num = st.selectbox("Analizar Variable:", num_cols)
                st.plotly_chart(px.histogram(df, x=v_num, marginal="box", color_discrete_sequence=['#3b82f6']), use_container_width=True)

    with tabs[1]:
        if len(num_cols) > 1:
            fig_corr, ax = plt.subplots(figsize=(10, 5))
            sns.heatmap(df[num_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig_corr)

    # --- SECCIÓN DEL ASISTENTE IA ---
    with tabs[2]:
        st.header("🤖 Análisis Llama 3.3 Versatile")
        
        if not groq_api_key:
            st.warning("⚠️ Por favor, ingresa tu API Key de Groq en la barra lateral para usar el asistente.")
        else:
            if st.button("Generar Informe de Hallazgos"):
                with st.spinner("Llama 3.3 está analizando tus datos..."):
                    try:
                        client = Groq(api_key=groq_api_key)
                        
                        # Preparar contexto para el LLM
                        resumen_datos = df.describe(include='all').to_string()
                        conteo_nulos = df.isnull().sum().to_string()
                        
                        prompt = f"""
                        Actúa como un experto consultor de ingeniería y científico de datos. 
                        Analiza el siguiente resumen de un conjunto de datos (primeras {num_muestras} filas):
                        
                        RESUMEN ESTADÍSTICO:
                        {resumen_datos}
                        
                        DATOS NULOS:
                        {conteo_nulos}
                        
                        Tarea: Describe los 3 hallazgos más importantes, detecta posibles anomalías y 
                        da una recomendación técnica basada en la eficiencia y la inversión.
                        Responde en español de forma profesional y concisa.
                        """
                        
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="llama-3.3-70b-versatile",
                        )
                        
                        st.markdown("### 📋 Informe de la IA")
                        st.write(chat_completion.choices[0].message.content)
                        st.success("Análisis completado exitosamente.")
                        
                    except Exception as e:
                        st.error(f"Error al conectar con Groq: {e}")

    with tabs[3]:
        st.dataframe(df, use_container_width=True)

else:
    st.info("Suba un archivo para comenzar.")
