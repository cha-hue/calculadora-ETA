
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

st.set_page_config(page_title="Calculadora de ETA", layout="wide")
st.title("⏱️ Calculadora de ETA - Post Cruce")

# Diccionario de velocidades por tipo de servicio
velocidades = {
    "SINGLE": 550,
    "TEAM": 1000,
    "HOTSHOT": 1200
}

# Horarios de operación
hora_cierre_aduana = time(22, 0)  # 10 PM CST
hora_inicio_operacion = time(7, 0)
hora_fin_operacion = time(16, 0)

st.sidebar.header("Ingresar datos de la unidad")

with st.sidebar.form("eta_form"):
    unidad = st.text_input("Unidad")
    cliente = st.text_input("Cliente")

    fecha_cruce = st.date_input("Fecha de Cruce (DATE P/U)", value=datetime.today())
    hora_cruce = st.time_input("Hora de Cruce", value=datetime.now().time())
    date_pu = datetime.combine(fecha_cruce, hora_cruce)

    millas = st.number_input("Millas restantes", min_value=1)
    tipo_servicio = st.selectbox("Tipo de Servicio", options=list(velocidades.keys()))

    submitted = st.form_submit_button("Calcular ETA")

# Inicializar historial de unidades
if "registros" not in st.session_state:
    st.session_state.registros = []

if submitted:
    # Regla 1: si cruce es después de las 22:00, el tránsito inicia al día siguiente a las 7:00 AM
    if hora_cruce >= hora_cierre_aduana:
        inicio_transito = datetime.combine(fecha_cruce + timedelta(days=1), hora_inicio_operacion)
    else:
        inicio_transito = date_pu

    # ETA base (en horas según velocidad)
    eta_horas = millas / velocidades[tipo_servicio] * 24
    eta_estimado = inicio_transito + timedelta(hours=eta_horas)

    # Regla 2: si ETA cae fuera del horario de planta (7 AM - 4 PM), mover al siguiente día 7 AM
    hora_eta = eta_estimado.time()
    if hora_eta < hora_inicio_operacion or hora_eta > hora_fin_operacion:
        eta_estimado = datetime.combine(eta_estimado.date() + timedelta(days=1), hora_inicio_operacion)

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
        "Cumplimiento": cumplimiento
    })

# Mostrar historial de unidades ingresadas
if st.session_state.registros:
    st.subheader("📅 Unidades Registradas")
    df = pd.DataFrame(st.session_state.registros)
    st.dataframe(df, use_container_width=True)

    # Exportar a Excel
    st.download_button("📄 Descargar Excel", data=df.to_csv(index=False).encode('utf-8'), file_name="ETA_Unidades.csv", mime="text/csv")
