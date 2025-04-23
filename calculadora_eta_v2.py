
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

st.set_page_config(page_title="Calculadora de ETA v2", layout="wide")
st.title("⏱️ Calculadora de ETA v2 - Post Cruce y Matchback")

# Velocidades por servicio
velocidades = {
    "SINGLE": 550,
    "TEAM": 1000,
    "HOTSHOT": 1200,
    "MATCHBACK": 70  # km/h para México
}

# Horarios aduanales por tipo de operación
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

# Función para validar si el cruce es válido en horario
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
    tipo_servicio = st.selectbox("Tipo de Servicio", options=list(velocidades.keys()))
    tipo_operacion = st.selectbox("Tipo de Operación", options=["IMPORTACION", "EXPORTACION"])

    fecha_cruce = st.date_input("Fecha del Cruce (o salida planta si MATCHBACK)", value=datetime.today())
    hora_cruce_txt = st.text_input("Hora de Cruce (HH:MM, 24h)", value="10:00")

    distancia = st.number_input("Distancia restante", min_value=1, help="Millas para EE.UU., km para Matchback")

    submitted = st.form_submit_button("Calcular ETA")

# Inicializar estado
if "registros" not in st.session_state:
    st.session_state.registros = []

if submitted:
    try:
        hora_cruce = datetime.strptime(hora_cruce_txt, "%H:%M").time()
    except ValueError:
        st.error("Formato de hora inválido. Usa HH:MM (24 horas).")
        hora_cruce = time(0, 0)

    fecha_cruce_dt = datetime.combine(fecha_cruce, hora_cruce)

    if tipo_servicio == "MATCHBACK":
        # ETA a aduana desde planta (en km)
        eta_horas = distancia / velocidades["MATCHBACK"]
        eta_estimado = fecha_cruce_dt + timedelta(hours=eta_horas)
    else:
        # Validar horario de cruce aduanal
        if not validar_cruce(fecha_cruce, hora_cruce, tipo_operacion):
            st.warning("⚠️ El cruce está fuera de horario aduanal. Se ajustará al siguiente horario válido.")
            fecha_ajustada = fecha_cruce + timedelta(days=1)
            inicio, _ = horarios[tipo_operacion]["weekday"]
            inicio_valido = datetime.combine(fecha_ajustada, inicio)
            inicio_transito = inicio_valido
        else:
            inicio_transito = fecha_cruce_dt

        eta_horas = distancia / velocidades[tipo_servicio] * 24
        eta_estimado = inicio_transito + timedelta(hours=eta_horas)

    cumplimiento = "PENDIENTE"

    st.success(f"ETA Estimado: {eta_estimado.strftime('%A %d/%m/%Y %I:%M %p')}")
    st.info(f"Cumplimiento: {cumplimiento}")

    st.session_state.registros.append({
        "Unidad": unidad,
        "Cliente": cliente,
        "Tipo Servicio": tipo_servicio,
        "Tipo Operación": tipo_operacion,
        "Fecha Cruce": fecha_cruce_dt,
        "Distancia": distancia,
        "ETA Estimado": eta_estimado,
        "Cumplimiento": cumplimiento
    })

# Mostrar historial
if st.session_state.registros:
    st.subheader("📅 Unidades Registradas")
    df = pd.DataFrame(st.session_state.registros)
    st.dataframe(df, use_container_width=True)
    st.download_button("📄 Descargar Excel", data=df.to_csv(index=False).encode("utf-8"), file_name="ETA_Unidades_v2.csv", mime="text/csv")
