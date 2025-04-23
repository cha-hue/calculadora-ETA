
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Calculadora de ETA", layout="wide")
st.title("⏱️ Calculadora de ETA - Post Cruce")

# Diccionario de velocidades por tipo de servicio
velocidades = {
    "SINGLE": 550,
    "TEAM": 1000,
    "HOTSHOT": 1200
}

st.sidebar.header("Ingresar datos de la unidad")

with st.sidebar.form("eta_form"):
    unidad = st.text_input("Unidad")
    cliente = st.text_input("Cliente")
    date_pu = st.datetime_input("Fecha/Hora de Cruce (DATE P/U)", value=datetime.now())
    millas = st.number_input("Millas restantes", min_value=1)
    tipo_servicio = st.selectbox("Tipo de Servicio", options=list(velocidades.keys()))
    entrega_real = st.datetime_input("Fecha/Hora de Entrega Real (opcional)", value=None, format="YYYY-MM-DD HH:mm", key="entrega")
    submitted = st.form_submit_button("Calcular ETA")

# Inicializar historial de unidades
if "registros" not in st.session_state:
    st.session_state.registros = []

if submitted:
    eta_horas = millas / velocidades[tipo_servicio] * 24
    eta_estimado = date_pu + timedelta(hours=eta_horas)

    if entrega_real:
        if entrega_real <= eta_estimado:
            cumplimiento = "A TIEMPO"
        else:
            cumplimiento = "TARDE"
    else:
        cumplimiento = "PENDIENTE"

    st.success(f"ETA Estimado: {eta_estimado.strftime('%A %d/%m/%Y %I:%M %p')}")
    st.info(f"Cumplimiento: {cumplimiento}")

    st.session_state.registros.append({
        "Unidad": unidad,
        "Cliente": cliente,
        "DATE P/U": date_pu,
        "Millas": millas,
        "Servicio": tipo_servicio,
        "ETA Estimado": eta_estimado,
        "Entrega Real": entrega_real,
        "Cumplimiento": cumplimiento
    })

# Mostrar historial de unidades ingresadas
if st.session_state.registros:
    st.subheader("📅 Unidades Registradas")
    df = pd.DataFrame(st.session_state.registros)
    st.dataframe(df, use_container_width=True)

    # Exportar a Excel
    st.download_button("📄 Descargar Excel", data=df.to_csv(index=False).encode('utf-8'), file_name="ETA_Unidades.csv", mime="text/csv")
