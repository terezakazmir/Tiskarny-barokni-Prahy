import pandas as pd
import folium
from folium.plugins import MarkerCluster
import numpy as np
import os


import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output

dash.register_page(__name__)

DATA_PATH = "data/Tiskaři_souřadnice_mapa_dynastie.csv"
DYNASTY_DATA_PATH = "data/dynastie_přehled.csv"

geolocations = pd.read_csv(DATA_PATH, sep=";")
geolocations["Lat"] = pd.to_numeric(geolocations["Lat"])
geolocations["Lon"] = pd.to_numeric(geolocations["Lon"])

dynasties = pd.read_csv(DYNASTY_DATA_PATH, sep=";")

data = pd.read_csv("data/Data_knihtisk.csv", sep=";")


MIN_YEAR = data["publishDate"].min()
MAX_YEAR = data["publishDate"].max()

geolocations = geolocations.merge(dynasties, on="Printer", how="left")

geolocations["publishDatefrom"] = np.nan
geolocations["publishDateto"] = np.nan

for index, row in geolocations.iterrows():
    printer = row["Printer"]
    min_date = data[data["Printer"] == printer]["publishDate"].min()
    max_date = data[data["Printer"] == printer]["publishDate"].max()

    geolocations.loc[index, "publishDatefrom"] = min_date
    geolocations.loc[index, "publishDateto"] = max_date

geolocations.fillna({"publishDatefrom": 0}, inplace=True)
geolocations.fillna({"publishDateto": 0}, inplace=True)

geolocations["publishDatefrom"] = geolocations["publishDatefrom"].astype(int)
geolocations["publishDateto"] = geolocations["publishDateto"].astype(int)

DEFAULT_LOCATION = [geolocations["Lat"].mean(), geolocations["Lon"].mean()]

hex_colors = [
    "#003049",
    "#006494",
    "#0A9396",
    "#52796F",
    "#778DA9",
    "#A3B18A",
    "#ADC178",
    "#ECBA53",
    "#EE9B00",
    "#CA6702",
    "#BB3E03",
    "#AE2012",
    "#9B2226",
    "#987D6D",
    "#C2B3A9",
]

dynasty_colors = {
    dynasty: hex_colors[i]
    for i, dynasty in enumerate(geolocations["Dynastie"].dropna().unique())
}

if not os.path.exists("mapatiskaři.html"):
    with open("mapatiskaři.html", "w") as f:
        f.write("")


def create_map(geolocations):
    if len(geolocations) == 0:
        location = DEFAULT_LOCATION
    else:
        location = [geolocations["Lat"].mean(), geolocations["Lon"].mean()]

    mymap = folium.Map(location=location, zoom_start=15)

    cluster_radius = 10

    marker_cluster = MarkerCluster(maxClusterRadius=cluster_radius).add_to(mymap)

    for index, row in geolocations.iterrows():
        popup = (
            f"<div style='width: 250px;'><strong>Tiskař:</strong> {row['Printer']}<br>"
        )

        if not pd.isnull(row["Činnost samostatná"]):
            popup += (
                f"<strong>Samostatná činnost:</strong> {row['Činnost samostatná']}<br>"
            )

        if not pd.isnull(row["Činnost závislá"]):
            popup += f"<strong>Činnost závislá:</strong> {row['Činnost závislá']}<br>"

        if not pd.isnull(row["Adresa"]):
            popup += f"<strong>Adresa:</strong> {row['Adresa']}<br>"

        if not pd.isnull(row["Období"]):
            popup += f"<strong>Umístění tiskárny na této adrese:</strong> {row['Období']}<br>"

        popup += "<br>"

        if not pd.isnull(row["Encyklopedie knihy"]):
            popup += f"<a target='_top' href= '{row['Encyklopedie knihy']}'>{'Encyklopedie knihy'}</a><br>"

        if not pd.isnull(row["Poznámka o encyklopedii"]):
            popup += f"{row['Poznámka o encyklopedii']}<br>"

        if not pd.isnull(row["Bibliografická databáze"]):
            popup += f"<a target='_top' href= '{row['Bibliografická databáze']}'>{'Bibliografická databáze'}</a><br>"

        tooltip = f"<strong>{row['Printer']}</strong><br>"
        if not pd.isnull(row["Období"]):
            tooltip += f"Období: {row['Období']}<br>"

        color = dynasty_colors.get(row["Dynastie"], "#228B22")

        icon_html = f"""
        <div style="background-color:{color}; width:24px; height:24px; border-radius:50%; display:flex; align-items:center; justify-content:center;">
            <i class="fas fa-book-open" style="color:white;"></i>
        </div>
        """
        icon = folium.DivIcon(html=icon_html)

        folium.Marker(
            location=[row["Lat"], row["Lon"]], popup=popup, tooltip=tooltip, icon=icon
        ).add_to(marker_cluster)

    mymap.save("mapatiskaři.html")
    return open("mapatiskaři.html", encoding="UTF-8").read()


layout = html.Div(
    children=[
        html.H1(
            children="Tiskárny barokní Prahy",
            style={"font-weight": "bold"},
            className="map-title",
        ),
        html.Div(
            id="selectors",
            style={"display": "block", "gap": "20px"},
            children=[
                html.Div(
                    className="rounded-box",
                    children=[
                        html.Span("Výběr tiskárny"),
                        html.Div(
                            className="dropdown-container",
                            children=[
                                html.Div(
                                    className="dropdown",
                                    children=[
                                        dcc.Checklist(
                                            id="printer_dropdown",
                                            options=[
                                                {"label": printer, "value": printer}
                                                for printer in geolocations[
                                                    "Printer"
                                                ].unique()
                                            ],
                                            inputClassName="custom-input",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="rounded-box",
                    children=[
                        html.Span("Výběr tiskařské rodiny/dynastie"),
                        html.Div(
                            className="dropdown-container",
                            children=[
                                html.Div(
                                    className="dropdown",
                                    children=[
                                        dcc.Checklist(
                                            id="dynasty_dropdown",
                                            options=[
                                                {"label": dynasty, "value": dynasty}
                                                for dynasty in geolocations["Dynastie"]
                                                .dropna()
                                                .unique()
                                            ],
                                            inputClassName="custom-input",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="rounded-box",
                    children=[
                        html.Span("Výběr podle roků vydávání"),
                        html.Div(
                            className="dropdown-container",
                            children=[
                                html.Div(
                                    className="year-range",
                                    children=[
                                        dcc.RangeSlider(
                                            id="year-range-slider",
                                            min=MIN_YEAR,
                                            max=MAX_YEAR,
                                            step=1,
                                            marks={
                                                year: str(year)
                                                for year in range(
                                                    MIN_YEAR, MAX_YEAR + 1, 5
                                                )
                                            },
                                            value=[MIN_YEAR, MAX_YEAR],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            id="map-container",
            children=[
                html.Iframe(
                    id="mapa",
                    srcDoc=open("mapatiskaři.html", "r", encoding="UTF-8").read(),
                    style={
                        "width": "100%",
                        "height": "100%",
                        "border": "none",
                    },
                )
            ],
        ),
        html.Div(
            id="legend-container",
            children=[
                html.H3(
                    "Tiskařské rodiny a dynastie",
                    style={"font-weight": "bold", "font-size": "18px"},
                ),
                html.Ul(
                    [
                        html.Li(
                            f"{dynasty}",
                            style={"color": color, "font-weight": "bold"},
                        )
                        for dynasty, color in sorted(
                            dynasty_colors.items(), key=lambda x: x[0]
                        )
                    ]
                ),
            ],
        ),
    ]
)


@callback(
    Output("mapa", "srcDoc"),
    Input("printer_dropdown", "value"),
    Input("dynasty_dropdown", "value"),
    Input("year-range-slider", "value"),
)
def listen_events(
    printers: list[str], dynasties: list[str], year_range: tuple[int, int]
):
    subframe = geolocations.copy()

    year_min, year_max = year_range
    subframe = geolocations[
        ~(
            (geolocations["publishDateto"] < year_min)
            | (geolocations["publishDatefrom"] > year_max)
        )
    ]

    if printers and dynasties:
        dynasty_printers = (
            geolocations[geolocations["Dynastie"].isin(dynasties)]["Printer"]
            .unique()
            .tolist()
        )
        combined_printers = list(set(printers + dynasty_printers))
        subframe = subframe[subframe["Printer"].isin(combined_printers)]

    elif printers:
        subframe = subframe[subframe["Printer"].isin(printers)]
    elif dynasties:
        subframe = subframe[subframe["Dynastie"].isin(dynasties)]

    return create_map(subframe)
