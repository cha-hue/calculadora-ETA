
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from pytz import timezone
import requests

st.set_page_config(page_title="ETA Calculator Ultimate v10 ⏱️", layout="wide")
st.title("ETA Calculator Ultimate v10 ⏱️")

API_KEY = "5b3ce3597851110001cf6248d8e6be00ebe54622816d535b51dd2bce"
ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"

velocidades = {
    "SINGLE": 50.0,
    "TEAM": 50.0,
    "HOTSHOT": 50.0
}

cst = timezone("America/Monterrey")
est = timezone("US/Eastern")

def get_coords(place):
    response = requests.get(
        "https://api.openrouteservice.org/geocode/search",
        params={"api_key": API_KEY, "text": place, "size": 1}
    )
    if response.status_code == 200:
        data = response.json()
        if data["features"]:
            return data["features"][0]["geometry"]["coordinates"]
    return None

def get_distance(origin, destination):
    coords_origin = get_coords(origin)
    coords_dest = get_coords(destination)
    if coords_origin and coords_dest:
        body = {"coordinates": [coords_origin, coords_dest]}
        headers = {"Authorization": API_KEY, "Content-Type": "application/json"}
        response = requests.post(ORS_URL, json=body, headers=headers)
        if response.status_code == 200:
            meters = response.json()["features"][0]["properties"]["summary"]["distance"]
            return round(meters / 1609.34, 2)
    return None

st.sidebar.header("Ingresar datos de la unidad")

with st.sidebar.form("eta_form"):
    unidad = st.text_input("Unidad")
    cliente = st.text_input("Cliente")
    tipo_servicio = st.selectbox("Tipo de Servicio", options=["LIVE", "MATCHBACK", "DROP&HOOK", "MILK RUN"])
    tipo_transito = st.selectbox("Tipo de Tránsito", options=["SINGLE", "TEAM", "HOTSHOT"])
    fecha_cruce = st.date_input("Fecha de Cruce", value=datetime.today())
    hora_cruce_txt = st.text_input("Hora de Cruce CST (HH:MM, 24h)", value="10:00")
    usar_manual = st.checkbox("Ingresar distancia manualmente si falla la API")
    distancia_manual = st.number_input("Distancia manual (mi)", min_value=1, value=100)

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

    distancia = None
    if not usar_manual:
        distancia = get_distance(ubicacion_actual, destino_final)

    if distancia is None:
        st.warning("No se pudo calcular la distancia automáticamente. Se usará el valor manual.")
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
        "Cumplimiento": cumplimiento,
        "Mapa": "N/A"
    })

if st.session_state.registros:
    st.subheader("📅 Unidades Registradas")
    df = pd.DataFrame(st.session_state.registros)
    st.dataframe(df, use_container_width=True)
    st.download_button("📄 Descargar Excel", data=df.to_csv(index=False).encode("utf-8"), file_name="ETA_Unidades_v10.csv", mime="text/csv")
