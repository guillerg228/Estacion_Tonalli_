import threading
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from data_store import store
from mqtt_client import start_mqtt

# ── Iniciar MQTT en hilo separado ──────────────────────────────────────────
threading.Thread(target=start_mqtt, daemon=True).start()

# ── App ────────────────────────────────────────────────────────────────────
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Estación Tonalli"

app.layout = html.Div([

    # ── Título ─────────────────────────────────────────────────────────────
    html.H2(
        "Estación Tonalli — Monitor de carga",
        style={
            "textAlign": "center",
            "marginBottom": "24px",
            "color": "#38bdf8",
            "fontFamily": "Arial, sans-serif"
        }
    ),

    # ── Botones ────────────────────────────────────────────────────────────
    html.Div([
        html.Button(
            "Usuarios Prioritarios",
            id="btn-prioritario",
            n_clicks=0,
            style={
                "marginRight": "12px",
                "padding": "10px 20px",
                "backgroundColor": "#e05c2a",
                "color": "white",
                "border": "none",
                "borderRadius": "8px",
                "cursor": "pointer"
            }
        ),
        html.Button(
            "Usuarios Comunes",
            id="btn-comun",
            n_clicks=0,
            style={
                "padding": "10px 20px",
                "backgroundColor": "#3b82f6",
                "color": "white",
                "border": "none",
                "borderRadius": "8px",
                "cursor": "pointer"
            }
        ),
    ], style={"textAlign": "center", "marginBottom": "32px"}),

    # ── Gráficas ───────────────────────────────────────────────────────────
    html.Div([

        # Card 1: Anillo + indicador
        html.Div([
            html.Div([
                dcc.Graph(id="grafica-anillo", style={"flex": "1"})
            ], style={"flex": "1"}),

            html.Div([
                html.Div("Batería actual", style={
                    "color": "#94a3b8",
                    "fontSize": "14px",
                    "marginBottom": "8px",
                    "textAlign": "center",
                    "letterSpacing": "0.05em",
                    "textTransform": "uppercase",
                }),
                html.Div(
                    id="indicador-bateria",
                    style={
                        "fontSize": "72px",
                        "fontWeight": "bold",
                        "textAlign": "center",
                        "lineHeight": "1",
                        "fontFamily": "monospace",
                    }
                ),
                html.Div("%", style={
                    "textAlign": "center",
                    "fontSize": "28px",
                    "color": "#94a3b8",
                    "marginTop": "4px",
                }),
                html.Div(id="etiqueta-bateria", style={
                    "textAlign": "center",
                    "marginTop": "16px",
                    "fontSize": "13px",
                    "padding": "4px 12px",
                    "borderRadius": "999px",
                    "display": "inline-block",
                    "width": "100%",
                }),
            ], style={
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "center",
                "alignItems": "center",
                "minWidth": "180px",
                "padding": "16px",
                "borderLeft": "1px solid #334155",
            }),
        ], style={
            "display": "flex",
            "alignItems": "center",
            "backgroundColor": "#1e293b",
            "padding": "16px",
            "borderRadius": "12px",
            "marginBottom": "20px",
            "boxShadow": "0 4px 10px rgba(0,0,0,0.3)"
        }),

        # Card 2: Consumo
        html.Div([
            dcc.Graph(id="grafica-consumo")
        ], style={
            "backgroundColor": "#1e293b",
            "padding": "16px",
            "borderRadius": "12px",
            "marginBottom": "20px",
            "boxShadow": "0 4px 10px rgba(0,0,0,0.3)"
        }),
    ]),

    dcc.Store(id="seleccion", data="prioritario"),
    dcc.Interval(id="intervalo", interval=2000, n_intervals=0),
    dcc.Interval(id="intervalo-bateria", interval=500, n_intervals=0),

], style={
    "maxWidth": "900px",
    "margin": "0 auto",
    "padding": "24px",
    "backgroundColor": "#0f172a",
    "color": "white",
    "borderRadius": "12px"
})


# ── Selección ─────────────────────────────────────────────────────────────
@app.callback(
    Output("seleccion", "data"),
    Input("btn-prioritario", "n_clicks"),
    Input("btn-comun", "n_clicks"),
    prevent_initial_call=True,
)
def actualizar_seleccion(n_prioritario, n_comun):
    ctx = dash.callback_context
    boton = ctx.triggered[0]["prop_id"].split(".")[0]
    return "prioritario" if boton == "btn-prioritario" else "comun"


# ── Gráficas ──────────────────────────────────────────────────────────────
@app.callback(
    Output("grafica-anillo", "figure"),
    Output("grafica-consumo", "figure"),
    Input("intervalo", "n_intervals"),
    State("seleccion", "data"),
)
def actualizar_graficas(n, seleccion):

    pct_bateria = store["bateria"]["porcentaje"]

    consumos_p = list(store["prioritario"]["consumo"])
    consumos_c = list(store["comun"]["consumo"])

    consumo_p = sum(consumos_p) if consumos_p else 0
    consumo_c = sum(consumos_c) if consumos_c else 0
    restante = max(0, pct_bateria - consumo_p - consumo_c)

    # ── Anillo (HORARIO) ───────────────────────────────────────────────
    fig_anillo = go.Figure(go.Pie(
        labels=[
            "Batería consumida por prioritarios",
            "Batería consumida por comunes",
            "Batería disponible"
        ],
        values=[consumo_p, consumo_c, restante],
        hole=0.65,
        marker=dict(colors=["#e05c2a", "#3b82f6", "#d1d5db"]),
        pull=[
            0.06 if seleccion == "prioritario" else 0,
            0.06 if seleccion == "comun" else 0,
            0
        ],
        textinfo="percent",
        direction="clockwise",
        rotation=90
    ))

    fig_anillo.update_layout(
        title="Estado de carga actual",
        paper_bgcolor="#1e293b",
        plot_bgcolor="#1e293b",
        font=dict(color="white"),
    )

    # ── Consumo ────────────────────────────────────────────────────────
    timestamps = list(store[seleccion]["timestamps"])
    consumo_sel = list(store[seleccion]["consumo"])

    if not timestamps:
        timestamps = ["--"]
        consumo_sel = [0]

    fig_consumo = go.Figure(go.Scatter(
        x=timestamps,
        y=consumo_sel,
        mode="lines+markers",
        line=dict(width=3),
        fill="tozeroy",
    ))

    fig_consumo.update_layout(
        title=f"Consumo — {seleccion.capitalize()}",
        xaxis_title="Hora",
        yaxis_title="Consumo (W)",
        paper_bgcolor="#1e293b",
        plot_bgcolor="#1e293b",
        font=dict(color="white"),
        transition_duration=500
    )

    return fig_anillo, fig_consumo


# ── Indicador batería ─────────────────────────────────────────────────────
@app.callback(
    Output("indicador-bateria", "children"),
    Output("indicador-bateria", "style"),
    Output("etiqueta-bateria",  "children"),
    Output("etiqueta-bateria",  "style"),
    Input("intervalo-bateria", "n_intervals"),
)
def actualizar_indicador(_):

    pct_bateria = store["bateria"]["porcentaje"]

    consumos_p = list(store["prioritario"]["consumo"])
    consumos_c = list(store["comun"]["consumo"])

    consumo_p = sum(consumos_p) if consumos_p else 0
    consumo_c = sum(consumos_c) if consumos_c else 0

    pct = max(0, pct_bateria - consumo_p - consumo_c)
    pct_txt = f"{pct:.1f}"

    if pct >= 70:
        color = "#4ade80"
        etiqueta = "✔ Carga óptima"
        bg = "#14532d"
    elif pct >= 30:
        color = "#facc15"
        etiqueta = "⚠ Carga media"
        bg = "#422006"
    else:
        color = "#f87171"
        etiqueta = "✖ Batería baja"
        bg = "#450a0a"

    return pct_txt, {
        "fontSize": "72px",
        "fontWeight": "bold",
        "textAlign": "center",
        "fontFamily": "monospace",
        "color": color,
    }, etiqueta, {
        "backgroundColor": bg,
        "color": color,
        "textAlign": "center",
        "marginTop": "16px",
        "padding": "4px",
        "borderRadius": "999px",
    }

# ── Run ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)