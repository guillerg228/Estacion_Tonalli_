
import paho.mqtt.client as mqtt
from datetime import datetime
from data_store import store

BROKER = "localhost"
PORT   = 1883

TOPICS = [
    "sensores/consumo/prioritario",
    "sensores/consumo/comun",
    "sensores/bateria",
]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado al broker")
        for topic in TOPICS:
            client.subscribe(topic)
    else:
        print(f"Error de conexión, código: {rc}")

def on_message(client, userdata, msg):
    print("Mensaje recibido:", msg.topic, msg.payload)
    topic   = msg.topic
    payload = msg.payload.decode("utf-8")

    try:
        valor = float(payload)
    except ValueError:
        print(f"Payload inválido en {topic}: {payload}")
        return

    ahora = datetime.now().strftime("%H:%M:%S")

    if topic == "sensores/consumo/prioritario":
        store["prioritario"]["consumo"].append(valor)
        store["prioritario"]["timestamps"].append(ahora)

    elif topic == "sensores/consumo/comun":
        store["comun"]["consumo"].append(valor)
        store["comun"]["timestamps"].append(ahora)

    elif topic == "sensores/bateria":
        store["bateria"]["porcentaje"] = valor

def start_mqtt():
    print("Iniciando MQTT...")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_forever()