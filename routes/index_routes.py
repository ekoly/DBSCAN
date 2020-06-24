import numpy as np
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from sklearn import cluster, datasets
from sklearn.preprocessing import StandardScaler

import time

import plotly.graph_objects as go

from core.dbscan import DBSCAN

layout = (
    html.Div([
        dcc.Dropdown(
            id="dataset-dropdown",
            options=[
                {"label": x, "value": x}
                for x in ["circles", "moons", "blobs", "no structure", "aniso", "varied"]
            ],
        ),
        html.Br(),
        dbc.Row([
            dbc.Col( [
                html.Span("n samples:"),
            ], id="n-samples-label", width=2),
            dbc.Col([
                dcc.Slider(
                    id="n-samples-input",
                    value=700,
                    min=300,
                    max=1000,
                    step=50,
                ),
            ], width=5),
        ]),
        dbc.Row([
            dbc.Col([
                html.Span("epsilon: (dbscan)"),
            ], width=2),
            dbc.Col([
                dcc.Input(
                    id="epsilon-input",
                    type="number",
                    value=0.2,
                ),
            ], width=3),
        ]),
        dbc.Row([
            dbc.Col([
                html.Span("n neighbors: (dbscan)"),
            ], width=2),
            dbc.Col([
                dcc.Input(
                    id="neighbors-input",
                    type="number",
                    value=4,
                ),
            ], width=3),
        ]),
        dbc.Button("Submit", id="submit-button"),
        html.Div(
            [],
            id="graphs",
        ),
    ])
)

from app import app

@app.callback(
    Output("graphs", "children"),
    [Input("submit-button", "n_clicks"),],
    [
        State("n-samples-input", "value"),
        State("dataset-dropdown", "value"),
        State("epsilon-input", "value"),
        State("neighbors-input", "value"),
    ],
)
def update_graphs(clicks, n_samples, dataset, eps, neighbors_input):

    default_base = {
        'n_neighbors': 10,
        'n_clusters': 3,
    }

    if dataset == "circles": 
        data = datasets.make_circles(n_samples=n_samples, factor=0.5, noise=0.05)
        n_clusters = 2

    elif dataset == "moons":
        data = datasets.make_moons(n_samples=n_samples, noise=0.05)
        n_clusters = 2

    elif dataset == "blobs":
        data = datasets.make_blobs(n_samples=n_samples)
        n_clusters = 3

    elif dataset == "no structure":
        data = np.random.rand(n_samples, 2), None
        n_clusters = 3

    elif dataset == "aniso":

        X, y = datasets.make_blobs(n_samples=n_samples)
        transformation = [[0.6, -0.6], [-0.4, 0.8]]
        X_aniso = np.dot(X, transformation)
        data = (X_aniso, y)
        n_clusters = 3

    elif dataset == "varied":
        data = datasets.make_blobs(n_samples=n_samples, cluster_std=[1.0, 2.5, 0.5])
        n_clusters = 3

    else:
        return []

    X, y = data

    X = StandardScaler().fit_transform(X)
    
    fig_actual = go.Figure(
        go.Scatter(x=X[:, 0], y=X[:, 1], mode="markers", marker={"color": y}),
    )
    fig_actual.update_layout(title="Actual Groups", width=500, height=500)

    t1 = time.clock()
    clustering = cluster.KMeans(n_clusters=n_clusters)
    clustering.fit(X)
    t2 = time.clock()

    fig_kmeans = go.Figure(
        go.Scatter(x=X[:, 0], y=X[:, 1], mode="markers", marker={"color": clustering.labels_})
    )
    fig_kmeans.update_layout(title=f"K-Means Predictions: {t2-t1:.3f} seconds", width=500, height=500)

    t1 = time.clock()
    clustering = DBSCAN(eps=eps, minpts=neighbors_input)
    clustering.fit(X)
    t2 = time.clock()

    labels = [label if label != -1 else "#000" for label in clustering.labels_]

    fig_dbscan = go.Figure(
        go.Scatter(x=X[:, 0], y=X[:, 1], mode="markers", marker={"color": labels},)
    )
    fig_dbscan.update_layout(title=f"DBSCAN Predictions: {t2-t1:.3f} seconds", width=500, height=500)

    return [
        dcc.Graph(figure=fig_actual),
        dcc.Graph(figure=fig_kmeans),
        dcc.Graph(figure=fig_dbscan),
    ]

@app.callback(
    Output("n-samples-label", "children"),
    [
        Input("n-samples-input", "value"),
    ]
)
def update_slider(n_samples):
    return [
        html.Span(f"n samples: ({n_samples})")
    ]
