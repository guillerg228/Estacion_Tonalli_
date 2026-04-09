# Estacion_Tonalli_

**Dispensador autónomo inteligente de energía solar para comunidades sin acceso a la red eléctrica o en situaciones de emergencia.**

Desarrollado por el equipo **GND (Gente No Durmiendo)** para el Hackathon Qualcomm Sustainable Power Cities.

---

## Descripción general

Estación Tonalli es un sistema embebido que mide, clasifica y distribuye energía solar de forma autónoma. Integra sensores de corriente, un modelo de machine learning para reconocimiento facial, comunicación MQTT y un dashboard web de monitoreo en tiempo real.

---

## Arquitectura del sistema

```
Arduino UNO Q (Qualcomm Dragonwing QRB2210)
    ├── STM32 (sketch .ino)
    │       ├── Lee ACS712 A2 → carga prioritaria
    │       ├── Lee ACS712 A3 → carga común
    │       └── Controla relé (bloqueo de enchufes comunes)
    │
    ├── QRB2210 (Linux, scripts Python)
    │       ├── Bridge RPC ↔ STM32
    │       ├── Modelo Edge Impulse (.eim) → reconocimiento facial
    │       └── Cliente MQTT → publica al broker
    │
    ▼
Broker MQTT (Mosquitto — laptop)
    │
    ▼
Dashboard web (Dash + Plotly — laptop)
```

---

## Componentes de hardware

| Componente            | Función                                                   |
|-----------------------|-----------------------------------------------------------|
| Arduino UNO Q         | Procesamiento principal (QRB2210 + STM32)                 |
| ACS712 30A (x2)       | Medición de corriente en cargas prioritaria y común       |
| Relé                  | Bloqueo físico del enchufe común ante usuario prioritario |
| Webcam USB            | Captura de imagen para reconocimiento facial              |
| Panel solar           | Fuente de energía del sistema                             |

---

## Estructura del repositorio

```
estacion-tonalli/
├── arduino/
│   └── sketch.ino          # Sketch STM32: lectura ACS712 + control relé via Bridge RPC
|       main.py
├── python/
│   ├── app.py              # Dashboard web (Dash + Plotly)
│   ├── data_store.py       # Store compartido entre MQTT y Dash
│   ├── mqtt_client.py      # Suscriptor MQTT → alimenta el store
├── modelo/
│   └── *.eim               # Ejecutable Edge Impulse (Linux AARCH64)
└── README.md
```

---

## Topics MQTT

| Topic                          | Dirección        | Contenido                     |
|--------------------------------|------------------|-------------------------------|
| `sensores/consumo/prioritario` | Arduino → Broker | Potencia en W (float)         |
| `sensores/consumo/comun`       | Arduino → Broker | Potencia en W (float)         |
| `sensores/bateria`             | Arduino → Broker | Porcentaje de batería (float) |
| `sensores/estado`              | Arduino → Broker | `"prioritario"` o `"comun"`   |

---

## Requisitos

### Laptop (dashboard)

- Python 3.10+
- Mosquitto MQTT broker

```bash
sudo apt install mosquitto mosquitto-clients
pip install dash plotly paho-mqtt==1.6.1
```

### Arduino UNO Q

```bash
pip3 install edge_impulse_linux opencv-python-headless paho-mqtt --break-system-packages
```

---

## Cómo correr el sistema

### 1. Laptop — iniciar broker y dashboard

```bash
# Terminal 1 (tmux recomendado)
sudo systemctl start mosquitto

# Terminal 2
python app.py
```

Abrir el dashboard en: `http://127.0.0.1:8050`

### 2. Arduino UNO Q — iniciar el pipeline

Desde el Arduino App Lab, correr `sensor_publisher.py`. Este script:

1. Captura frames de la webcam
2. Los pasa al modelo `.eim` de Edge Impulse
3. Si detecta a **Tannia** (usuario prioritario): activa el relé via Bridge RPC y bloquea la carga común
4. Lee corriente de ambos sensores ACS712
5. Calcula potencia real (Irms × 127 V)
6. Publica los valores al broker MQTT en la laptop

---

## Modelo de Machine Learning

Entrenado en **Edge Impulse** con las siguientes características:

| Parámetro             | Valor                   |
|-----------------------|-------------------------|
| Tipo                  | Object detection (FOMO) |
| Clases                | `Person`, `Tannia`      |
| Resolución de entrada | 96 × 96 px RGB          |
| Score mínimo          | 0.5                     |
| Exportado como        | Linux AARCH64 (.eim)    |

El modelo corre directamente en el QRB2210 sin necesidad de conexión a internet.

---

## Lógica de distribución de energía

```
¿Se detecta a Tannia (usuario prioritario)?
        │
       SÍ ──→ Relé activa bloqueo de enchufes comunes
        │      Solo enchufes prioritarios disponibles
        │      Dashboard muestra estado: PRIORITARIO
        │
        NO ──→ Todos los enchufes disponibles
               Dashboard muestra consumo de ambas cargas
```

---

## Equipo

**GND — Gente No Durmiendo** 
Hackathon Qualcomm Sustainable Power Cities
