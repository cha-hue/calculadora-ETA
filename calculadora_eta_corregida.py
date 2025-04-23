
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

    # Reemplazar datetime_input con date_input + time_input
    fecha_cruce = st.date_input("Fecha de Cruce (DATE P/U)", value=datetime.today())
    hora_cruce = st.time_input("Hora de Cruce", value=datetime.now().time())
    date_pu = datetime.combine(fecha_cruce, hora_cruce)

    millas = st.number_input("Millas restantes", min_value=1)
    tipo_servicio = st.selectbox("Tipo de Servicio", options=list(velocidades.keys()))

    fecha_entrega_real = st.date_input("Fecha de Entrega Real (opcional)", value=datetime.today(), key="fecha_entrega")
    hora_entrega_real = st.time_input("Hora de Entrega Real (opcional)", value=datetime.now().time(), key="hora_entrega")

    submitted = st.form_submit_button("Calcular ETA")

# Inicializar historial de unidades
if "registros" not in st.session_state:
    st.session_state.registros = []

if submitted:
    eta_horas = millas / velocidades[tipo_servicio] * 24
    eta_estimado = date_pu + timedelta(hours=eta_horas)

    if fecha_entrega_real and hora_entrega_real:
        entrega_real = datetime.combine(fecha_entrega_real, hora_entrega_real)
        if entrega_real <= eta_estimado:
            cumplimiento = "A TIEMPO"
        else:
            cumplimiento = "TARDE"
    else:
        entrega_real = None
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
