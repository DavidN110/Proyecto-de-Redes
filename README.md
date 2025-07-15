
# 🛰️ Prototipo de Red Rural Inteligente con IA

Este proyecto simula una red de conectividad rural resiliente usando inteligencia artificial para predecir fallos y optimizar el mantenimiento. Incluye:

- 🧠 IA con `RandomForestClassifier` entrenada con datos simulados
- 📊 Interfaz de simulación de escritorio (`main_ia.py`)
- 🌐 Aplicación web con Streamlit (`app.py`)
- 📁 Exportación de datos a CSV, Excel y PDF
- 🗺️ Visualización con NetworkX y mapas interactivos (Folium)

[![PDF](https://img.shields.io/badge/Informe-PDF-red)](/PROYECTO REDES.pdf)
---

## 📦 Estructura del proyecto

```
prototipo_red/
├── main_ia.py         # Versión escritorio con Tkinter
├── app.py             # Versión web con Streamlit
├── recursos/          # Archivos generados automáticamente
│   ├── dataset_ia.csv
│   ├── modelo_entrenado.pkl
│   ├── registro_red.csv
│   ├── resumen_red.xlsx
│   └── informe_red.pdf
```

---

## 🚀 Requisitos

Instala las dependencias con:

```bash
pip install pandas openpyxl matplotlib fpdf folium networkx scikit-learn streamlit streamlit-folium joblib
```

---

## 🧪 Ejecutar simulación de escritorio

```bash
python main_ia.py
```

---

## 🌐 Ejecutar la versión web

```bash
python -m streamlit run app.py
```

Luego abre el navegador en: http://localhost:8501
(Generalmente es automático)
---

## 💡 Funcionalidades destacadas

- Simulación de nodos con fallos aleatorios
- Predicción de fallos usando IA
- Registro de cada ciclo en CSV y Excel
- Informe PDF automatizado
- Mapa interactivo con estado de nodos
- Visualización web con alertas y gráficos

---

## ✉️ Notificaciones

La versión de escritorio incluye alertas por correo cuando un nodo queda completamente aislado (requiere configurar `EMAIL_REMITENTE` y clave de aplicación).

---

## 📄 Autor

David Santiago Nagles Barajas  
Universidad Nacional de Colombia  
Redes de Computadores · Ingeniería Mecatrónica  
2025-1
