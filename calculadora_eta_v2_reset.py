
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

st.set_page_config(page_title="Calculadora de ETA v2", layout="wide")
st.title("⏱️ Calculadora de ETA v2 - Tipos de Servicio y Tránsito")

# Velocidades por tipo de tránsito (en millas por día)
velocidades = {
    "SINGLE": 550,
    "TEAM": 1000,
    "HOTSHOT": 1200
}

# Horarios aduanales por operación
horarios = {
    "IMPORTACION": {
        "weekday": (time(8, 0), time(23, 59)),
        "weekend": (time(8, 0), time(16, 0))
    },
    "EXPORTACION": {
        "weekday": (time(7, 0), time(23, 0)),
        "weekend": (time(8, 0), time(15, 0))
    }
}

def validar_cruce(dia, hora, tipo_op):
    if dia.weekday() < 5:
        inicio, fin = horarios[tipo_op]["weekday"]
    else:
        inicio, fin = horarios[tipo_op]["weekend"]
    return inicio <= hora <= fin

st.sidebar.header("Ingresar datos de la unidad")

with st.sidebar.form("eta_form"):
    unidad = st.text_input("Unidad")
    cliente = st.text_input("Cliente")

    tipo_servicio = st.selectbox("Tipo de Servicio", options=["LIVE", "MATCHBACK", "DROP&HOOK", "MILK RUN"])
    tipo_transito = st.selectbox("Tipo de Tránsito", options=["SINGLE", "TEAM", "HOTSHOT"])
    tipo_operacion = st.selectbox("Tipo de Operación", options=["IMPORTACION", "EXPORTACION"])

    fecha_cruce = st.date_input("Fecha del Cruce", value=datetime.today())
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

    if not validar_cruce(fecha_cruce, hora_cruce, tipo_operacion):
        st.warning("⚠️ Cruce fuera de horario. Se ajusta al siguiente válido.")
        fecha_ajustada = fecha_cruce + timedelta(days=1)
        inicio, _ = horarios[tipo_operacion]["weekday"]
        inicio_transito = datetime.combine(fecha_ajustada, inicio)
    else:
        inicio_transito = fecha_cruce_dt

    eta_horas = distancia / velocidades[tipo_transito] * 24
    eta_estimado = inicio_transito + timedelta(hours=eta_horas)

    cumplimiento = "PENDIENTE"

    st.success(f"ETA Estimado: {eta_estimado.strftime('%A %d/%m/%Y %I:%M %p')}")
    st.info(f"Cumplimiento: {cumplimiento}")

    st.session_state.registros.append({
        "Unidad": unidad,
        "Cliente": cliente,
        "Servicio": tipo_servicio,
        "Tránsito": tipo_transito,
        "Operación": tipo_operacion,
        "Fecha Cruce": fecha_cruce_dt,
        "Distancia (mi)": distancia,
        "ETA Estimado": eta_estimado,
        "Cumplimiento": cumplimiento
    })

if st.session_state.registros:
    st.subheader("📅 Unidades Registradas")
    df = pd.DataFrame(st.session_state.registros)
    st.dataframe(df, use_container_width=True)
    st.download_button("📄 Descargar Excel", data=df.to_csv(index=False).encode("utf-8"), file_name="ETA_Unidades_v2.csv", mime="text/csv")
