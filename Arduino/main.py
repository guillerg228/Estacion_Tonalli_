# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
# SPDX-License-Identifier: MPL-2.0

from arduino.app_utils import *
import paho.mqtt.client as mqtt

BROKER = "192.168.137.39"  # IP de tu laptop en la red local
PORT   = 1883

voltajeRed    = 127.0
ruido_base_A2 = 6.295
ruido_base_A3 = 4.705

# ── Conectar al broker una sola vez ────────────────────────────────────────
cliente = mqtt.Client()
cliente.connect(BROKER, PORT)
cliente.loop_start()

def loop():
    Ip1 = Bridge.call("leer_sensor1")
    Ip2 = Bridge.call("leer_sensor2")

    # 1. Convertir a RMS
    Irms1_bruto = Ip1 * 0.707
    Irms2_bruto = Ip2 * 0.707

    # 2. Tara
    Irms1 = Irms1_bruto - ruido_base_A2
    Irms2 = Irms2_bruto - ruido_base_A3

    # 3. Banda muerta
    if -0.05 < Irms1 < 0.05:
        Irms1 = 0.0
    if -0.05 < Irms2 < 0.05:
        Irms2 = 0.0

    # 4. Potencia real
    P1 = Irms1 * voltajeRed
    P2 = Irms2 * voltajeRed

    # 5. Publicar al broker
    cliente.publish("sensores/consumo/prioritario", f"{P1:.3f}")
    cliente.publish("sensores/consumo/comun",       f"{P2:.3f}")

    print(f"Publicado → prioritario: {P1:.3f} W | comun: {P2:.3f} W")

App.run(user_loop=loop)
