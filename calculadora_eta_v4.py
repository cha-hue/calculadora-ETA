
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

st.set_page_config(page_title="Calculadora de ETA v4", layout="wide")
st.title("⏱️ Calculadora de ETA v4 - Velocidad Promedio Real")

# Velocidad real calculada desde datos históricos (mi/h)
VELOCIDAD_REAL_MI_H = 29.96

st.sidebar.header("Ingresar datos de la unidad")

with st.sidebar.form("eta_form"):
    unidad = st.text_input("Unidad")
    cliente = st.text_input("Cliente")

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

    # ETA usando velocidad real promedio (mi/h)
    eta_estimado = fecha_cruce_dt + timedelta(hours=(distancia / VELOCIDAD_REAL_MI_H))
    cumplimiento = "PENDIENTE"

    st.success(f"ETA Estimado (Velocidad Real): {eta_estimado.strftime('%A %d/%m/%Y %I:%M %p')}")
    st.info(f"Cumplimiento: {cumplimiento}")

    st.session_state.registros.append({
        "Unidad": unidad,
        "Cliente": cliente,
        "Fecha Cruce": fecha_cruce_dt,
        "Distancia (mi)": distancia,
        "Velocidad Promedio": VELOCIDAD_REAL_MI_H,
        "ETA Estimado": eta_estimado,
        "Cumplimiento": cumplimiento
    })

if st.session_state.registros:
    st.subheader("📅 Unidades Registradas")
    df = pd.DataFrame(st.session_state.registros)
    st.dataframe(df, use_container_width=True)
    st.download_button("📄 Descargar Excel", data=df.to_csv(index=False).encode("utf-8"), file_name="ETA_Unidades_v4.csv", mime="text/csv")
