import streamlit as st
import pandas as pd
import os
import random
import folium
import joblib
from streamlit_folium import st_folium
from sklearn.ensemble import RandomForestClassifier

# Configuración inicial
st.set_page_config(page_title="Red Inteligente", layout="wide")

RUTA_RECURSOS = "recursos"
DATASET_IA = os.path.join(RUTA_RECURSOS, "dataset_ia.csv")
CSV_REGISTRO = os.path.join(RUTA_RECURSOS, "registro_red.csv")
MODELO_PKL = os.path.join(RUTA_RECURSOS, "modelo_entrenado.pkl")

os.makedirs(RUTA_RECURSOS, exist_ok=True)

nodos_base = {
    "Nodo A": {"vecinos": ["Nodo B", "Nodo F"], "lat": 5.0, "lon": -74.0},
    "Nodo B": {"vecinos": ["Nodo A", "Nodo C"], "lat": 5.1, "lon": -74.1},
    "Nodo C": {"vecinos": ["Nodo B", "Nodo D"], "lat": 5.2, "lon": -74.0},
    "Nodo D": {"vecinos": ["Nodo C", "Nodo E"], "lat": 5.3, "lon": -74.2},
    "Nodo E": {"vecinos": ["Nodo D", "Nodo F"], "lat": 5.1, "lon": -74.3},
    "Nodo F": {"vecinos": ["Nodo E", "Nodo A"], "lat": 5.0, "lon": -74.2},
}

if not os.path.exists(CSV_REGISTRO):
    with open(CSV_REGISTRO, "w") as f:
        f.write("Ciclo,Nodo,Estado,Latencia,Disponibilidad,Rutas Alternas\n")

if "ciclo" not in st.session_state:
    st.session_state.ciclo = 0
if "nodos" not in st.session_state:
    st.session_state.nodos = {}

class Nodo:
    def __init__(self, nombre, vecinos, lat, lon):
        self.nombre = nombre
        self.vecinos = vecinos
        self.lat = lat
        self.lon = lon
        self.estado = "Activo"
        self.latencia = random.randint(20, 100)
        self.total = 0
        self.activos = 0
        self.fallas = 0
        self.prediccion = 0
        self.rutas = []

    def verificar_estado(self, red):
        self.total += 1
        if self.estado == "Inactivo" and random.random() < 0.3:
            self.estado = "Activo"
        elif random.random() < 0.2:
            self.estado = "Inactivo"
            self.fallas += 1
        if self.estado == "Activo":
            self.activos += 1
        self.latencia = random.randint(20, 100)
        self.rutas = [v for v in self.vecinos if red[v].estado == "Activo"]

    def disponibilidad(self):
        return round(self.activos / self.total * 100, 2) if self.total else 100

    def registrar_datos(self, ciclo):
        porc_vecinos_activos = len(self.rutas) / len(self.vecinos)
        fila = {
            "Nodo": self.nombre,
            "Ciclo": ciclo,
            "Latencia": self.latencia,
            "Disponibilidad": self.disponibilidad(),
            "Fallos": self.fallas,
            "PorcVecinosActivos": porc_vecinos_activos,
            "FalloProximo": 1 if self.estado == "Inactivo" else 0
        }
        df = pd.DataFrame([fila])
        if not os.path.exists(DATASET_IA):
            df.to_csv(DATASET_IA, index=False)
        else:
            df.to_csv(DATASET_IA, mode="a", header=False, index=False)

    def predecir(self, modelo):
        if modelo is None:
            self.prediccion = 0
        else:
            X = pd.DataFrame([{
                "Latencia": self.latencia,
                "Disponibilidad": self.disponibilidad(),
                "Fallos": self.fallas,
                "PorcVecinosActivos": len(self.rutas)/len(self.vecinos)
            }])
            self.prediccion = int(modelo.predict(X)[0])

def cargar_modelo():
    if os.path.exists(MODELO_PKL):
        return joblib.load(MODELO_PKL)
    return None

def entrenar_y_guardar_modelo():
    if os.path.exists(DATASET_IA):
        df = pd.read_csv(DATASET_IA)
        if len(df) > 30:
            X = df[["Latencia", "Disponibilidad", "Fallos", "PorcVecinosActivos"]]
            y = df["FalloProximo"]
            modelo = RandomForestClassifier(n_estimators=100)
            modelo.fit(X, y)
            joblib.dump(modelo, MODELO_PKL)
            return modelo
    return None

def simular_ciclo():
    st.session_state.ciclo += 1
    ciclo = st.session_state.ciclo
    nodos = st.session_state.nodos
    if not nodos:
        for k, v in nodos_base.items():
            nodos[k] = Nodo(k, v["vecinos"], v["lat"], v["lon"])

    modelo = cargar_modelo()
    if ciclo >= 5 and modelo is None:
        modelo = entrenar_y_guardar_modelo()

    for nodo in nodos.values():
        nodo.verificar_estado(nodos)
        nodo.registrar_datos(ciclo)
        nodo.predecir(modelo)
        with open(CSV_REGISTRO, "a") as f:
            f.write(f"{ciclo},{nodo.nombre},{nodo.estado},{nodo.latencia},{nodo.disponibilidad()},{'|'.join(nodo.rutas)}\n")

# === Interfaz Streamlit ===
st.title("🌐 Red Rural Inteligente (Web + IA)")
st.sidebar.button("🔁 Simular nuevo ciclo", on_click=simular_ciclo)
st.sidebar.markdown(f"**Ciclo actual:** {st.session_state.ciclo}")

nodos = st.session_state.nodos
if nodos:
    df = pd.DataFrame([{
        "Nodo": n.nombre,
        "Estado": n.estado,
        "Latencia (ms)": n.latencia,
        "Disponibilidad (%)": n.disponibilidad(),
        "Fallos": n.fallas,
        "Rutas": ", ".join(n.rutas),
        "Riesgo IA (1=Sí)": n.prediccion
    } for n in nodos.values()])
    st.subheader("📊 Estado actual de nodos")
    st.dataframe(df, use_container_width=True)

    st.subheader("🗺️ Mapa de red")
    m = folium.Map(location=[5.15, -74.15], zoom_start=8)
    for n in nodos.values():
        color = "orange" if n.prediccion == 1 and n.estado == "Activo" else ("green" if n.estado == "Activo" else "red")
        folium.Marker(
            location=[n.lat, n.lon],
            popup=f"{n.nombre}: {n.estado}",
            icon=folium.Icon(color=color)
        ).add_to(m)
    st_folium(m, width=700, height=400)

    nodos_sin_ruta = [n.nombre for n in nodos.values() if n.estado == "Inactivo" and not n.rutas]
    if nodos_sin_ruta:
        st.error(f"🚨 Nodos sin rutas activas: {', '.join(nodos_sin_ruta)}")
else:
    st.info("Haz clic en 'Simular nuevo ciclo' para comenzar.")
