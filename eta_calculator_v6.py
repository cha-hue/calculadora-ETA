
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

st.set_page_config(page_title="Calculadora de ETA v4.1", layout="wide")
st.title("ETA Calculator ⏱️")

# Velocidades estándar por tipo de tránsito (mi/h basados en equivalentes realistas)
velocidades = {
    "SINGLE": 55.0,
    "TEAM": 55.0,
    "HOTSHOT": 55.0
}

st.sidebar.header("Ingresar datos de la unidad")

with st.sidebar.form("eta_form"):
    unidad = st.text_input("Unidad")
    cliente = st.text_input("Cliente")
    
    tipo_servicio = st.selectbox("Tipo de Servicio", options=["LIVE", "MATCHBACK", "DROP&HOOK", "MILK RUN"])
    tipo_transito = st.selectbox("Tipo de Tránsito", options=["SINGLE", "TEAM", "HOTSHOT"])

    fecha_cruce = st.date_input("Fecha de Cruce", value=datetime.today())
    hora_cruce_txt = st.text_input("Hora de Cruce (HH:MM, 24h)", value="10:00")
    distancia = st.number_input("Distancia restante (millas)", min_value=1)

    submitted = st.form_submit_button("Calcular ETA")

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

    # Calcular ETA con velocidad correspondiente
    velocidad = velocidades[tipo_transito]
    eta_estimado = fecha_cruce_dt + timedelta(hours=(distancia / velocidad))
    cumplimiento = "PENDIENTE"

    
from pytz import timezone
cst = timezone("America/Monterrey")
est = timezone("US/Eastern")
eta_cst = eta_estimado.astimezone(cst)
eta_est = eta_estimado.astimezone(est)

st.success(f"ETA CST (México): {eta_cst.strftime('%A %d/%m/%Y %I:%M %p')}")
st.info(f"ETA EST (EE.UU.): {eta_est.strftime('%A %d/%m/%Y %I:%M %p')}")
    st.info(f"Cumplimiento: {cumplimiento}")

    st.session_state.registros.append({
        "Unidad": unidad,
        "Cliente": cliente,
        "Servicio": tipo_servicio,
        "Tránsito": tipo_transito,
        "Fecha Cruce": fecha_cruce_dt,
        "Distancia (mi)": distancia,
        "Velocidad (mi/h)": velocidad,
        "ETA Estimado": eta_estimado,
        "Cumplimiento": cumplimiento
    })

if st.session_state.registros:
    st.subheader("📅 Unidades Registradas")
    df = pd.DataFrame(st.session_state.registros)
    st.dataframe(df, use_container_width=True)
    st.download_button("📄 Descargar Excel", data=df.to_csv(index=False).encode("utf-8"), file_name="ETA_Unidades_v4.1.csv", mime="text/csv")
