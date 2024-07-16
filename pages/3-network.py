import pandas as pd
import plotly.graph_objects as go
import networkx as nx

from dash import dcc, html, callback
import dash
from dash.dependencies import Input, Output

dash.register_page(__name__)

df = pd.read_csv("data/Data_knihtisk.csv", sep=";")
dynasties = pd.read_csv("data/dynastie_přehled.csv", sep=";")

df["publishDate"] = df["publishDate"].astype(int)
df["Printer"] = df["Printer"].astype(str)
df["genre"] = df["genre"].astype(str)
df["topic"] = df["topic"].astype(str)
df["author"] = df["author"].astype(str)
df["id"] = df["id"].astype(str)
df["language_cs"] = df["language_cs"].astype(str)
df["author"] = df["author"].astype(str)


MIN_YEAR = df["publishDate"].min()
MAX_YEAR = df["publishDate"].max()

df = df.merge(dynasties, on="Printer", how="left")

language_options = [
    {"label": lang, "value": lang}
    for lang in df["language_cs"].unique()
    if pd.notna(lang)
]
genre_options = [
    {"label": lang, "value": lang} for lang in df["genre"].unique() if pd.notna(lang)
]
topic_options = [
    {"label": lang, "value": lang} for lang in df["topic"].unique() if pd.notna(lang)
]
author_options = [
    {"label": lang, "value": lang} for lang in df["author"].unique() if pd.notna(lang)
]

layout = html.Div(
    [
        html.Div(
            [
                html.Label("Rok vydání:"),
                dcc.RangeSlider(
                    id="year-range-slider",
                    min=df["publishDate"].min(),
                    max=df["publishDate"].max(),
                    step=1,
                    marks={year: str(year) for year in range(MIN_YEAR, MAX_YEAR+1, 5)},
                    value=[df["publishDate"].min(), df["publishDate"].max()],
                ),
            ],
            style={"margin": "10px"},
        ),
        html.Div(
            [
                html.Label("Výběr tiskaře:"),
                dcc.Dropdown(
                    id="printer-dropdown",
                    options=[
                        {"label": printer, "value": printer}
                        for printer in sorted(df["Printer"].unique())
                    ],
                    value=None,
                    multi=True,
                ),
            ],
            style={"margin": "10px"},
        ),
        html.Div(
            [
                html.Label("Výběr tiskařské rodiny/dynastie:"),
                dcc.Dropdown(
                    id="dynasty-dropdown",
                    options=[
                        {"label": dynasty, "value": dynasty}
                        for dynasty in dynasties["Dynastie"].dropna().unique()
                    ],
                    value=None,
                    multi=True,
                ),
            ],
            style={"margin": "10px"},
        ),
        html.Div([dcc.Graph(id="social-network-analysis")], className="bordered-div"),
    ]
)

def filter_table(
    df,
    selected_year_range,
    selected_printer,
    selected_dynasty,
):
    filtered_df = df[
        (df["publishDate"] >= selected_year_range[0])
        & (df["publishDate"] <= selected_year_range[1])
    ]

    if selected_printer:
        filtered_df = filtered_df[filtered_df["Printer"].isin(selected_printer)]

    if selected_dynasty:
        dynasties_printers = df[df["Dynastie"].isin(selected_dynasty)][
            "Printer"
        ].unique()
        filtered_df = filtered_df[filtered_df["Printer"].isin(dynasties_printers)]

    filtered_df = filtered_df.drop_duplicates(
        subset=["id", "Printer", "author", "language_cs", "genre", "topic", "Dynastie"]
    )

    return filtered_df


@callback(
    Output("social-network-analysis", "figure"),
    Input("year-range-slider", "value"),
    Input("printer-dropdown", "value"),
    Input("dynasty-dropdown", "value"),
)
def update_social_network_analysis(
    selected_year_range,
    selected_printer,
    selected_dynasty,
):
    filtered_df = filter_table(
        df,
        selected_year_range,
        selected_printer,
        selected_dynasty,
    )

    unique_author_books = filtered_df.drop_duplicates(subset=["id", "author"])

    if selected_printer is None:
        selected_printer = []

    if selected_dynasty:
        selected_printer.extend(
            df[df["Dynastie"].isin(selected_dynasty)]["Printer"].unique()
        )

    B = nx.Graph()

    printers = filtered_df["Printer"].unique()
    authors = filtered_df["author"].unique()

    B.add_nodes_from(printers, bipartite=0)
    B.add_nodes_from(authors, bipartite=1)

    edges = list(filtered_df[["Printer", "author"]].itertuples(index=False, name=None))
    B.add_edges_from(edges)

    valid_selected_printers = [
        printer for printer in selected_printer if printer in B.nodes
    ]

    neighbors = set()
    for printer in valid_selected_printers:
        neighbors.update(B.neighbors(printer))

    subgraph_nodes = set(valid_selected_printers).union(neighbors)
    subgraph = B.subgraph(subgraph_nodes)

    author_counts = unique_author_books.groupby("author")["id"].nunique().to_dict()
    printer_total_counts = {
        printer: unique_author_books[unique_author_books["Printer"] == printer][
            "id"
        ].nunique()
        for printer in printers
        if printer in subgraph.nodes()
    }

    pos = nx.spring_layout(subgraph)

    degree_centrality = nx.degree_centrality(subgraph)
    closeness_centrality = nx.closeness_centrality(subgraph)
    betweenness_centrality = nx.betweenness_centrality(subgraph)

    node_degrees = dict(subgraph.degree())

    edge_trace = []
    for edge in subgraph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace.append(
            go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                line=dict(width=1, color="#888"),
                hoverinfo="none",
                mode="lines",
            )
        )

    node_sizes = []
    node_colors = []
    node_texts = []
    hover_text = []
    for node in subgraph.nodes():
        degree = node_degrees[node]
        if node in selected_printer:
            total_books = printer_total_counts.get(node, 0)
            node_sizes.append(15)  
            node_colors.append("Maroon")  
            node_texts.append(node)  
            hover_text.append(
                f"{node}: {total_books} vydání, Počet vazeb: {degree}, Degree: {degree_centrality[node]:.2f}, Closeness: {closeness_centrality[node]:.2f}, Betweenness: {betweenness_centrality[node]:.2f}"
            )
        else:
            count = author_counts.get(node, 0)
            node_sizes.append(count * 1)  
            node_colors.append("DarkGreen")
            node_texts.append(node)
            hover_text.append(f"{node}: {count} vydání")

    node_trace = go.Scatter(
        x=[pos[node][0] for node in subgraph.nodes()],
        y=[pos[node][1] for node in subgraph.nodes()],
        text=node_texts, 
        mode="markers+text",
        textposition="top center",
        marker=dict(size=node_sizes, color=node_colors),
        hoverinfo="text",
        hovertext=hover_text,
        name="Nodes",
    )

    fig = go.Figure(
        data=edge_trace + [node_trace],
        layout=go.Layout(
            title="Sociální síť pro vybrané tiskaře",
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[dict(text=(""), showarrow=False, xref="paper", yref="paper")],
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
            autosize=True,
            width=None,
            height=None,
        ),
    )

    return fig
