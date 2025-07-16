# 🛰️ Prototipo de Red Rural Inteligente con IA

Este proyecto simula una red de conectividad rural resiliente con ayuda de inteligencia artificial para predecir fallos y optimizar decisiones de mantenimiento. Incluye:

- 🧠 IA con `RandomForestClassifier`
- 🌐 Aplicación web interactiva con Streamlit (`app.py`)
- 🗺️ Visualización geográfica con Folium
- 📊 Gráficos comparativos por tecnología (WiFi vs LoRaWAN)
- 📁 Exportación de datos y alertas automáticas por WhatsApp

[![PDF](https://img.shields.io/badge/Informe-PDF-red)](/PROYECTO_REDES.pdf)

---

## 📦 Estructura del proyecto

```
prototipo_red/
├── app.py                  # Aplicación web con Streamlit
├── iniciar_app.bat         # Lanza la app con doble clic
├── instalador.exe          # Ejecutable que instala las dependencias
├── requirements.txt        # Lista de dependencias
├── README.md
├── recursos/               # Archivos generados automáticamente
│   ├── dataset_ia.csv
│   ├── modelo_entrenado.pkl
│   ├── registro_red.csv
│   ├── resumen_red.xlsx
│   └── informe_red.pdf
```

---

## 🚀 Instalación y uso

1. 📥 **Clona o descarga** este repositorio completo.
2. ⚙️ Ejecuta `instalador.exe` para instalar automáticamente todas las dependencias necesarias.
3. ▶️ Haz doble clic en `iniciar_app.bat` para abrir la aplicación en tu navegador.

La aplicación se abrirá en: [http://localhost:8501](http://localhost:8501)

---

## 💡 Funcionalidades destacadas

- Simulación de nodos WiFi y LoRaWAN con fallos aleatorios
- Predicción de fallos con IA
- Mapa interactivo con estado de nodos
- Alertas por WhatsApp con pywhatkit
- Gráficos comparativos e históricos
- Exportación de resultados a CSV y Excel

---

## 📲 Notificaciones automáticas

Después de cada simulación de ciclo, se programa el envío automático del estado de los nodos por WhatsApp (requiere tener WhatsApp Web abierto y escaneado).

---

## 📄 Autor

David Santiago Nagles Barajas  
Universidad Nacional de Colombia  
Redes de Computadores · Ingeniería Mecatrónica  
2025-1