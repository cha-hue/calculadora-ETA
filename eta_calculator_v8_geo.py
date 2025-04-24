
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from pytz import timezone

st.set_page_config(page_title="ETA Calculator GEO ⏱️", layout="wide")
st.title("ETA Calculator GEO ⏱️")

velocidades = {
    "SINGLE": 50.0,
    "TEAM": 50.0,
    "HOTSHOT": 50.0
}

cst = timezone("America/Monterrey")
est = timezone("US/Eastern")

st.sidebar.header("Ingresar datos de la unidad")

with st.sidebar.form("eta_form"):
    unidad = st.text_input("Unidad")
    cliente = st.text_input("Cliente")
    tipo_servicio = st.selectbox("Tipo de Servicio", options=["LIVE", "MATCHBACK", "DROP&HOOK", "MILK RUN"])
    tipo_transito = st.selectbox("Tipo de Tránsito", options=["SINGLE", "TEAM", "HOTSHOT"])
    ubicacion_actual = st.text_input("Ubicación actual (ej. Laredo, TX)")
    destino_final = st.text_input("Destino final (ej. Telford, TN)")
    fecha_cruce = st.date_input("Fecha de Cruce", value=datetime.today())
    hora_cruce_txt = st.text_input("Hora de Cruce CST (HH:MM, 24h)", value="10:00")
    distancia = # Aquí se integrará el cálculo automático en el futuro
    distancia = st.number_input("Distancia estimada (automática en futuras versiones)", min_value=1, help="Temporal hasta integrar API")

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
        "Ubicación": ubicacion_actual,
        "Destino": destino_final,
        "Fecha Cruce": fecha_cruce_dt,
        "Distancia (mi)": distancia,
        "Velocidad (mi/h)": velocidad,
        "ETA CST": eta_cst,
        "ETA EST": eta_est,
        "Cumplimiento": cumplimiento,
        "Mapa": f"https://www.google.com/maps/dir/{ubicacion_actual.replace(" ", "+")}/{destino_final.replace(" ", "+")}" if ubicacion_actual and destino_final else ""
    })

if st.session_state.registros:
    st.subheader("📅 Unidades Registradas")
    df = pd.DataFrame(st.session_state.registros)
    st.dataframe(df, use_container_width=True)
    st.download_button("📄 Descargar Excel", data=df.to_csv(index=False).encode("utf-8"), file_name="ETA_Unidades_v8_manual.csv", mime="text/csv")
