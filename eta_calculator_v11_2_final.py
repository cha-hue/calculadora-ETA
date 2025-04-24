
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from pytz import timezone

st.set_page_config(page_title="ETA Calculator Final v11 ⏱️", layout="wide")
st.title("ETA Calculator Final v11 ⏱️")

velocidades = {
    "SINGLE": 50.0,
    "TEAM": 65.0,
    "HOTSHOT": 70.0
}

cst = timezone("America/Monterrey")
est = timezone("US/Eastern")

st.sidebar.header("Ingresar datos de la unidad")

with st.sidebar.form("eta_form"):
    unidad = st.text_input("Unidad")
    cliente = st.text_input("Cliente")
    tipo_servicio = st.selectbox("Tipo de Servicio", options=["LIVE", "MATCHBACK", "DROP&HOOK", "MILK RUN"])
    tipo_transito = st.selectbox("Tipo de Tránsito", options=["SINGLE", "TEAM", "HOTSHOT"])
    fecha_cruce = st.date_input("Fecha de Cruce", value=datetime.today())
    hora_cruce_txt = st.text_input("Hora de Cruce CST (HH:MM, 24h)", value="10:00")
    distancia_manual = st.number_input("Distancia (mi)", min_value=1, value=100)

    submitted = st.form_submit_button("Calcular ETA")

if "registros" not in st.session_state:
    st.session_state.registros = []

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

    fecha_cruce_dt = cst.localize(datetime.combine(fecha_cruce, hora_cruce))

    distancia = distancia_manual
    velocidad = velocidades[tipo_transito]
    eta_estimado = fecha_cruce_dt + timedelta(hours=(distancia / velocidad))
    eta_cst = eta_estimado.astimezone(cst)
    eta_est = eta_estimado.astimezone(est)
    cumplimiento = "PENDIENTE"

    st.success(f"ETA México: {eta_cst.strftime('%A %d/%m/%Y %I:%M %p %Z')}")
    st.info(f"ETA EE.UU.: {eta_est.strftime('%A %d/%m/%Y %I:%M %p %Z')}")
    st.warning(f"Cumplimiento: {cumplimiento}")

    st.session_state.registros.append({
        "Unidad": unidad,
        "Cliente": cliente,
        "Servicio": tipo_servicio,
        "Tránsito": tipo_transito,
        "Fecha Cruce": fecha_cruce_dt,
        "Distancia (mi)": distancia,
        "Velocidad (mi/h)": velocidad,
        "ETA CST": eta_cst,
        "ETA EST": eta_est,
        "Cumplimiento": cumplimiento
    })

if st.session_state.registros:
    st.subheader("📅 Unidades Registradas")
    df = pd.DataFrame(st.session_state.registros)
    st.dataframe(df, use_container_width=True)
    st.download_button("📄 Descargar Excel", data=df.to_csv(index=False).encode("utf-8"), file_name="ETA_Unidades_v11_2.csv", mime="text/csv")
