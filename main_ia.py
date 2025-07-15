import tkinter as tk
import random
import csv
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

class Nodo:
    def __init__(self, nombre, vecinos):
        self.nombre = nombre
        self.vecinos = vecinos
        self.estado = "Activo"
        self.latencia = 0
        self.fallas = 0
        self.total = 0
        self.activos = 0
        self.prediccion = 0

    def disponibilidad(self):
        return round((self.activos / self.total) * 100, 2) if self.total else 100

    def verificar_estado(self):
        self.total += 1
        if self.estado == "Inactivo" and random.random() < 0.3:
            self.estado = "Activo"
        elif random.random() < 0.2:
            self.estado = "Inactivo"
            self.fallas += 1
        if self.estado == "Activo":
            self.activos += 1
        self.latencia = random.randint(20, 120)

    def registrar_datos_para_ia(self, red, ciclo):
        vecinos_activos = sum(1 for v in self.vecinos if red[v].estado == "Activo")
        porc_activos = vecinos_activos / len(self.vecinos) if self.vecinos else 0
        fila = {
            "Nodo": self.nombre,
            "Ciclo": ciclo,
            "Latencia": self.latencia,
            "Disponibilidad": self.disponibilidad(),
            "Fallos": self.fallas,
            "PorcVecinosActivos": porc_activos,
            "FalloProximo": 1 if self.estado == "Inactivo" else 0
        }
        os.makedirs("recursos", exist_ok=True)
        ruta = "recursos/dataset_ia.csv"
        if not os.path.exists(ruta):
            pd.DataFrame([fila]).to_csv(ruta, index=False)
        else:
            pd.DataFrame([fila]).to_csv(ruta, mode="a", header=False, index=False)

    def predecir_fallo(self):
        ruta_modelo = "recursos/modelo_entrenado.pkl"
        if os.path.exists(ruta_modelo):
            modelo = joblib.load(ruta_modelo)
            nodo_df = pd.DataFrame([{
                "Latencia": self.latencia,
                "Disponibilidad": self.disponibilidad(),
                "Fallos": self.fallas,
                "PorcVecinosActivos": 1.0
            }])
            self.prediccion = modelo.predict(nodo_df)[0]

class RedGUI:
    def __init__(self, master):
        self.master = master
        master.title("Red Inteligente con IA")
        self.ciclo = 0
        self.nodos = {
            "Nodo A": Nodo("Nodo A", ["Nodo B", "Nodo F"]),
            "Nodo B": Nodo("Nodo B", ["Nodo A", "Nodo C"]),
            "Nodo C": Nodo("Nodo C", ["Nodo B", "Nodo D"]),
            "Nodo D": Nodo("Nodo D", ["Nodo C", "Nodo E"]),
            "Nodo E": Nodo("Nodo E", ["Nodo D", "Nodo F"]),
            "Nodo F": Nodo("Nodo F", ["Nodo E", "Nodo A"])
        }

        self.labels = {}
        for i, nombre in enumerate(self.nodos):
            label = tk.Label(master, text=nombre, width=40, relief="solid", padx=5)
            label.grid(row=i, column=0, padx=10, pady=5)
            self.labels[nombre] = label

        self.boton = tk.Button(master, text="Simular ciclo", command=self.simular_red)
        self.boton.grid(row=7, column=0, pady=10)

    def simular_red(self):
        self.ciclo += 1
        datos = [["Ciclo", "Nodo", "Estado", "Latencia", "Disponibilidad"]]
        for nombre, nodo in self.nodos.items():
            nodo.verificar_estado()
            nodo.registrar_datos_para_ia(self.nodos, self.ciclo)
            if self.ciclo >= 5:
                nodo.predecir_fallo()

            color = "green" if nodo.estado == "Activo" else "red"
            if nodo.estado == "Activo" and nodo.prediccion == 1:
                color = "yellow"

            self.labels[nombre].config(
                text=f"{nombre}: {nodo.estado} | Latencia: {nodo.latencia}ms | Disp: {nodo.disponibilidad()}%",
                bg=color
            )
            datos.append([
                self.ciclo, nombre, nodo.estado, nodo.latencia, nodo.disponibilidad()
            ])

        self.exportar_csv(datos)
        if self.ciclo >= 5:
            self.entrenar_modelo()

    def exportar_csv(self, datos):
        ruta = "recursos/registro_red.csv"
        with open(ruta, "a", newline="") as f:
            writer = csv.writer(f)
            for fila in datos[1:]:
                writer.writerow(fila)

    def entrenar_modelo(self):
        ruta = "recursos/dataset_ia.csv"
        if os.path.exists(ruta):
            df = pd.read_csv(ruta)
            if len(df) > 30:
                X = df[["Latencia", "Disponibilidad", "Fallos", "PorcVecinosActivos"]]
                y = df["FalloProximo"]
                modelo = RandomForestClassifier(n_estimators=100)
                modelo.fit(X, y)
                joblib.dump(modelo, "recursos/modelo_entrenado.pkl")
                print("🧠 Modelo IA entrenado y guardado")

if __name__ == "__main__":
    root = tk.Tk()
    app = RedGUI(root)
    root.mainloop()
