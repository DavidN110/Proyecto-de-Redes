import streamlit as st
import pandas as pd
import os
import random
import folium
import joblib
import threading
import matplotlib.pyplot as plt
import seaborn as sns
import pywhatkit
import datetime
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
if "mensaje_enviado" not in st.session_state:
    st.session_state.mensaje_enviado = False


class Nodo:
    def __init__(self, nombre, vecinos, lat, lon, tecnologia="WiFi"):
        self.nombre = nombre
        self.vecinos = vecinos
        self.lat = lat
        self.lon = lon
        self.tecnologia = tecnologia  # "WiFi" o "LoRaWAN"
        self.estado = "Activo"
        self.latencia = random.randint(20, 100)
        self.total = 0
        self.activos = 0
        self.fallas = 0
        self.prediccion = 0
        self.rutas = []

    def verificar_estado(self, red):
        self.total += 1

        # Probabilidad de fallo menor para LoRaWAN
        prob_fallo = 0.1 if self.tecnologia == "LoRaWAN" else 0.2

        if self.estado == "Inactivo" and random.random() < 0.3:
            self.estado = "Activo"
        elif random.random() < prob_fallo:
            self.estado = "Inactivo"
            self.fallas += 1

        if self.estado == "Activo":
            self.activos += 1

        # Latencia diferente según tecnología
        self.latencia = random.randint(100, 300) if self.tecnologia == "LoRaWAN" else random.randint(20, 100)
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
            "Tecnologia": self.tecnologia,
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
                "PorcVecinosActivos": len(self.rutas) / len(self.vecinos)
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

def enviar_whatsapp(mensaje, numero="+573112917428"):
    try:
        pywhatkit.sendwhatmsg_instantly(numero, mensaje, wait_time=15, tab_close=True)
        print("✅ Mensaje enviado automáticamente.")
    except Exception as e:
        print(f"❌ Error al enviar mensaje por WhatsApp: {e}")

def programar_envio_whatsapp(mensaje, delay_segundos=60):
    threading.Timer(delay_segundos, enviar_whatsapp, args=[mensaje]).start()
    print(f"⏱️ Envío de WhatsApp programado en {delay_segundos} segundos.")



def simular_ciclo():
    st.session_state.ciclo += 1
    ciclo = st.session_state.ciclo
    nodos = st.session_state.nodos
    if not nodos:
        for k, v in nodos_base.items():
            # Alternar tecnologías: A, C, E con LoRaWAN
            tecnologia = "LoRaWAN" if k in ["Nodo A", "Nodo C", "Nodo E"] else "WiFi"
            nodos[k] = Nodo(k, v["vecinos"], v["lat"], v["lon"], tecnologia)


    modelo = cargar_modelo()
    if ciclo >= 5 and modelo is None:
        modelo = entrenar_y_guardar_modelo()

    for nodo in nodos.values():
        nodo.verificar_estado(nodos)
        nodo.registrar_datos(ciclo)
        nodo.predecir(modelo)
        with open(CSV_REGISTRO, "a") as f:
            f.write(f"{ciclo},{nodo.nombre},{nodo.estado},{nodo.latencia},{nodo.disponibilidad()},{'|'.join(nodo.rutas)}\n")
    if not st.session_state.mensaje_enviado:
        resumen = f"📡 Ciclo {ciclo} - Estado de la red:\n"
        for nodo in nodos.values():
            resumen += (
                f"🔹 {nodo.nombre}: {nodo.estado}, "
                f"Latencia: {nodo.latencia}ms, "
                f"Disp: {nodo.disponibilidad()}%, "
                f"Fallo IA: {'✅' if nodo.prediccion == 1 else '❌'}, "
                f"Tecnología: {nodo.tecnologia}\n"
            )

        programar_envio_whatsapp(resumen, delay_segundos=60)
        st.session_state.mensaje_enviado = True




# === Interfaz Streamlit ===
st.title("🌐 Red Rural Inteligente (Web + IA)")
def simular_con_reset():
    st.session_state.mensaje_enviado = False
    simular_ciclo()

st.sidebar.button("🔁 Simular nuevo ciclo", on_click=simular_con_reset)

st.sidebar.markdown(f"**Ciclo actual:** {st.session_state.ciclo}")

nodos = st.session_state.nodos
if nodos:
    df = pd.DataFrame([{
    "Nodo": n.nombre,
    "Tecnología": n.tecnologia,
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
        icono = "cloud" if n.tecnologia == "LoRaWAN" else "wifi"

        folium.Marker(
            location=[n.lat, n.lon],
            popup=f"{n.nombre}: {n.estado} ({n.tecnologia})",
            icon=folium.Icon(color=color, icon=icono)
        ).add_to(m)

    st_folium(m, width=700, height=400)

    # === Gráfico comparativo de métricas por tecnología ===

    # Agrupación de métricas
    df_grouped = df.groupby("Tecnología").agg({
        "Latencia (ms)": "mean",
        "Disponibilidad (%)": "mean"
    }).reset_index()
    df_grouped["Disponibilidad (%)"] = df_grouped["Disponibilidad (%)"].clip(upper=100)
    df["Disponibilidad (%)"] = df["Disponibilidad (%)"].clip(upper=100)

    # Gráfico
    fig, ax = plt.subplots(figsize=(6, 4))
    width = 0.35
    tecnologias = df_grouped["Tecnología"]
    latencias = df_grouped["Latencia (ms)"]
    disponibilidades = df_grouped["Disponibilidad (%)"]

    bar1 = ax.bar(tecnologias, disponibilidades, width, label="Disponibilidad Prom. (%)", color="lightgreen")
    bar2 = ax.bar(tecnologias, latencias, width, bottom=disponibilidades, label="Latencia Prom. (ms)", color="skyblue")

    ax.set_ylabel("Valores combinados")
    ax.set_title("Comparación de Latencia y Disponibilidad por Tecnología")
    ax.legend()

    # Mostrar valores encima de las barras
    for b in bar1 + bar2:
        height = b.get_height()
        ax.annotate(f'{height:.1f}',
                    xy=(b.get_x() + b.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)


    fig2, ax2 = plt.subplots(figsize=(6, 4))

    # Paleta por tecnología
    colors = {"WiFi": "skyblue", "LoRaWAN": "lightgreen"}

    # Crear barras para cada nodo coloreadas por su tecnología

    legend_labels = set()
    for i, row in df.iterrows():
        label = row["Tecnología"] if row["Tecnología"] not in legend_labels else None
        legend_labels.add(row["Tecnología"])
        ax2.bar(
            row["Nodo"],
            row["Fallos"],
            color=colors.get(row["Tecnología"], "gray"),
            label=label
            )


    # Evita duplicar leyendas
    handles, labels = ax2.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax2.legend(by_label.values(), by_label.keys())

    ax2.set_ylabel("Cantidad de fallos")
    ax2.set_xlabel("Nodos")
    ax2.set_title("Distribución de fallos por nodo y tecnología")
    ax2.set_xticklabels(df["Nodo"], rotation=45)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Comparativo de tecnologías")
        st.pyplot(fig, use_container_width=True)

    with col2:
        st.subheader("📊 Histograma de fallos")
        st.pyplot(fig2, use_container_width=True)

    nodos_sin_ruta = [n.nombre for n in nodos.values() if n.estado == "Inactivo" and not n.rutas]
    if nodos_sin_ruta:
        st.error(f"🚨 Nodos sin rutas activas: {', '.join(nodos_sin_ruta)}")
else:
    st.info("Haz clic en 'Simular nuevo ciclo' para comenzar.")
