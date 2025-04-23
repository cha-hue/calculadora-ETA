
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

st.set_page_config(page_title="Calculadora de ETA v3", layout="wide")
st.title("⏱️ Calculadora de ETA v3 - Promedio Real y Velocidades")

# Velocidades estimadas por tipo de tránsito (mi/día)
velocidades = {
    "SINGLE": 550,
    "TEAM": 1000,
    "HOTSHOT": 1200
}

# Promedio real desde datos históricos: 38.9 horas
PROMEDIO_REAL_HORAS = 38.9

st.sidebar.header("Ingresar datos de la unidad")

with st.sidebar.form("eta_form"):
    unidad = st.text_input("Unidad")
    cliente = st.text_input("Cliente")

    tipo_transito = st.selectbox("Tipo de Tránsito", options=["SINGLE", "TEAM", "HOTSHOT"])
    fecha_cruce = st.date_input("Fecha de Cruce", value=datetime.today())
    hora_cruce_txt = st.text_input("Hora de Cruce (HH:MM, 24h)", value="10:00")
    distancia = st.number_input("Distancia restante (millas)", min_value=1)

    submitted = st.form_submit_button("Calcular ETA")

# Inicializar registros
if "registros" not in st.session_state:
    st.session_state.registros = []

# Botón para resetear registros
st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Reiniciar registros"):
    st.session_state.registros = []
    st.sidebar.success("Registros eliminados.")

if submitted:
    try:
        hora_cruce = datetime.strptime(hora_cruce_txt, "%H:%M").time()
    except ValueError:
        st.error("Formato de hora inválido. Usa HH:MM (24 horas).")
        hora_cruce = time(0, 0)

    fecha_cruce_dt = datetime.combine(fecha_cruce, hora_cruce)

    # ETA usando duración real promedio
    eta_promedio = fecha_cruce_dt + timedelta(hours=PROMEDIO_REAL_HORAS)

    # ETA tradicional por velocidad de tránsito
    eta_calculada = fecha_cruce_dt + timedelta(hours=(distancia / velocidades[tipo_transito]) * 24)

    cumplimiento = "PENDIENTE"

    st.success(f"ETA Promedio Histórico: {eta_promedio.strftime('%A %d/%m/%Y %I:%M %p')}")
    st.info(f"ETA por Distancia y Velocidad: {eta_calculada.strftime('%A %d/%m/%Y %I:%M %p')}")
    st.warning(f"Cumplimiento: {cumplimiento}")

    st.session_state.registros.append({
        "Unidad": unidad,
        "Cliente": cliente,
        "Tránsito": tipo_transito,
        "Fecha Cruce": fecha_cruce_dt,
        "Distancia (mi)": distancia,
        "ETA Promedio": eta_promedio,
        "ETA Calculada": eta_calculada,
        "Cumplimiento": cumplimiento
    })

if st.session_state.registros:
    st.subheader("📅 Unidades Registradas")
    df = pd.DataFrame(st.session_state.registros)
    st.dataframe(df, use_container_width=True)
    st.download_button("📄 Descargar Excel", data=df.to_csv(index=False).encode("utf-8"), file_name="ETA_Unidades_v3.csv", mime="text/csv")
