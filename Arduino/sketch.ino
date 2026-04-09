// SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
//
// SPDX-License-Identifier: MPL-2.0

#include "Arduino_RouterBridge.h"

#define SENSOR1 A2  
#define SENSOR2 A3

const float Sensibilidad = 0.066;   
const float offset = 0.100;         
const float V0 = 2.460;             

float get_corriente(int pinSensor) {
    float voltajeSensor;
    float corriente = 0;
    long tiempo = millis();
    
    // --- EL FIX ESTÁ AQUÍ ---
    float Imax = -1000.0; // Inicia muy bajo para que cualquier lectura lo suba
    float Imin = 1000.0;  // Inicia muy alto para que cualquier lectura lo baje

    while (millis() - tiempo < 500) {  
        voltajeSensor = analogRead(pinSensor) * (5.0 / 1023.0);
        
        corriente = 0.9 * corriente + 0.1 * ((voltajeSensor - V0) / Sensibilidad);

        if (corriente > Imax) Imax = corriente;
        if (corriente < Imin) Imin = corriente;
    }
    
    return (((Imax - Imin) / 2) - offset); 
}

float leer_sensor1() { return get_corriente(SENSOR1); }
float leer_sensor2() { return get_corriente(SENSOR2); }

void setup() {
    Bridge.begin();
    Bridge.provide("leer_sensor1", leer_sensor1);
    Bridge.provide("leer_sensor2", leer_sensor2);
}

void loop() {}
