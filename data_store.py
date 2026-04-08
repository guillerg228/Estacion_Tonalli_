# data_store.py
import collections

MAX_HISTORIAL = 100  # puntos máximos por sensor

store = {
    "prioritario": {
        "consumo": collections.deque(maxlen=MAX_HISTORIAL),
        "timestamps": collections.deque(maxlen=MAX_HISTORIAL),
    },
    "comun": {
        "consumo": collections.deque(maxlen=MAX_HISTORIAL),
        "timestamps": collections.deque(maxlen=MAX_HISTORIAL),
    },
    "bateria": {
        "porcentaje": 0.0,
    },
}
