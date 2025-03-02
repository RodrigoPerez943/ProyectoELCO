# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify
import plotly.graph_objs as go
import plotly.io as pio
import random
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/data')
def data():
    # Generar datos aleatorios
    valores = [random.randint(0, 100) for _ in range(10)]
    df = pd.DataFrame({'x': list(range(1, 11)), 'y': valores})

    # Crear la grafica con Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['x'], y=df['y'], mode='lines+markers', name='Datos'))

    # Convertir la grafica a JSON para enviarla a la web
    graph_json = pio.to_json(fig)
    return jsonify(graph_json)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
