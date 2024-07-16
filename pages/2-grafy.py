import pandas as pd
import prince
import plotly.graph_objects as go
import plotly.express as px

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
        html.Div(
            [
                html.Label("Výběr autora:"),
                dcc.Dropdown(
                    id="author-dropdown",
                    options=[
                        {"label": author, "value": author}
                        for author in sorted(df["author"].unique())
                    ],
                    value=None,
                    multi=True,
                ),
            ],
            style={"margin": "10px"},
        ),
        html.Div(
            [
                html.Label("Výběr jazyka:"),
                dcc.Dropdown(
                    id="language-dropdown",
                    options=[
                        {"label": language, "value": language}
                        for language in sorted(df["language_cs"].unique())
                    ],
                    value=None,
                    multi=True,
                ),
            ],
            style={"margin": "10px"},
        ),
        html.Div(
            [
                html.Label("Výběr žánru:"),
                dcc.Dropdown(
                    id="genre-dropdown",
                    options=[
                        {"label": genre, "value": genre}
                        for genre in sorted(df["genre"].unique())
                    ],
                    value=None,
                    multi=True,
                ),
            ],
            style={"margin": "10px"},
        ),
        html.Div(
            [
                html.Label("Výběr tématu:"),
                dcc.Dropdown(
                    id="topic-dropdown",
                    options=[
                        {"label": topic, "value": topic}
                        for topic in sorted(df["topic"].unique())
                    ],
                    value=None,
                    multi=True,
                ),
            ],
            style={"margin": "10px"},
        ),
        html.Div(
            [
                html.Label("Výběr intervalu pro zobrazení celkového počtu vydání:"),
                dcc.RadioItems(
                    id="year-interval-checklist",
                    options=[
                        {"label": "Po 1 roce", "value": 1},
                        {"label": "Po 5 letech", "value": 5},
                        {"label": "Po 10 letech", "value": 10},
                    ],
                    value=1,
                    labelStyle={"display": "inline-block"},
                ),
            ],
            style={"margin": "10px"},
        ),
        html.Div([dcc.Graph(id="book-count-by-year")], className="bordered-div"),
        html.Div([dcc.Graph(id="book-count-by-year-line")], className="bordered-div"),
        html.Div(
            [dcc.Graph(id="book-count-by-year-language")], className="bordered-div"
        ),
        html.Div([dcc.Graph(id="book-count-by-year-genre")], className="bordered-div"),
        html.Div([dcc.Graph(id="book-count-by-year-topic")], className="bordered-div"),
        html.Div([dcc.Graph(id="book-count-by-dynasty")], className="bordered-div"),
        html.Div(
            [dcc.Graph(id="book-count-by-dynasty-language")], className="bordered-div"
        ),
        html.Div(
            [dcc.Graph(id="book-count-by-dynasty-genre")], className="bordered-div"
        ),
        html.Div(
            [dcc.Graph(id="book-count-by-dynasty-topic")], className="bordered-div"
        ),
        html.Div([dcc.Graph(id="book-count-by-printer")], className="bordered-div"),
        html.Div([dcc.Graph(id="book-count-by-language")], className="bordered-div"),
        html.Div([dcc.Graph(id="book-count-by-genre")], className="bordered-div"),
        html.Div([dcc.Graph(id="book-count-by-topic")], className="bordered-div"),
        html.Div(
            [dcc.Graph(id="correspondence-analysis-genre")], className="bordered-div"
        ),
        html.Div(
            [dcc.Graph(id="correspondence-analysis-topic")], className="bordered-div"
        ),
    ]
)

def filter_table(
    df,
    selected_year_range,
    selected_printer,
    selected_dynasty,
    selected_author,
    selected_language,
    selected_genre,
    selected_topic,
):
    filtered_df = df[
        (df["publishDate"] >= selected_year_range[0])
        & (df["publishDate"] <= selected_year_range[1])
    ]

    if selected_printer:
        filtered_df = filtered_df[filtered_df["Printer"].isin(selected_printer)]

    if selected_dynasty:
        filtered_df = filtered_df[filtered_df["Dynastie"].isin(selected_dynasty)]

    if selected_author:
        filtered_df = filtered_df[filtered_df["author"].isin(selected_author)]

    if selected_language:
        filtered_df = filtered_df[filtered_df["language_cs"].isin(selected_language)]

    if selected_genre:
        filtered_df = filtered_df[filtered_df["genre"].isin(selected_genre)]

    if selected_topic:
        filtered_df = filtered_df[filtered_df["topic"].isin(selected_topic)]

    filtered_df = filtered_df.drop_duplicates(
        subset=["id", "Printer", "author", "language_cs", "genre", "topic", "Dynastie"]
    )

    return filtered_df

def compute_dtick(table) -> int:
    x_length = len(table["publishDate"].unique())
    return x_length // min(max(1, x_length), 10)

language_colors = {
    "latina": "#52796F",
    "němčina": "#ECBA53",
    "čeština": "#AE2012",
    "italština": "#0A9396",
    "francouzština": "#003049",
    "řečtina": "#006494",
    "španělština": "#778DA9",
    "starodávná řečtina": "#A3B18A",
    "lužická srbština": "#ADC178",
    "hornolužická srbština": "#EE9B00",
    "hebrejština": "#CA6702",
    "portugalština": "#9B2226",
    "čínština": "#987D6D",
    "aramejština": "#C2B3A9",
    "arabština": "#7F7F7F",
    "slovanština": "#00CED1",
    "angličtina": "#FF6347",
}

genre_colors = {
    "příležitostné texty": "#B88992",
    "slovníky": "#006494",
    "legendy": "#0A9396",
    "(žánr nespecifikován)": "#7209B7",
    "odborná pojednání": "#778DA9",
    "populárně-naučné publikace": "#A3B18A",
    "polemiky": "#ADC178",
    "katechismy": "#ECBA53",
    "modlitební knihy": "#EE9B00",
    "kalendáře": "#CA6702",
    "pranostiky": "#BB3E03",
    "letáky": "#AE2012",
    "kázání": "#9B2226",
    "postily": "#987D6D",
    "písně": "#C2B3A9",
    "úřední texty": "#D9BF77",
    "kancionály": "#4F5D75",
    "učebnice": "#F4A261",
    "noviny": "#E76F51",
    "bajky": "#EDF2F4",
    "kroniky": "#264653",
    "zábavné publikace": "#F4A261",
    "zpravodajské texty": "#E9C46A",
    "gramatiky": "#A8DADC",
    "martyrologia": "#457B9D",
    "náboženské texty": "#1D3557",
    "slabikáře": "#8D99AE",
    "divadelní hry": "#2A9D8F",
    "cestopisy": "#EF233C",
    "minuce": "#D90429",
    "básnické texty": "#9B5DE5",
    "konfese": "#F15BB5",
    "notované texty": "#FEE440",
    "obrazové publikace": "#00BBF9",
    "topografické dokumenty": "#00F5D4",
    "liturgické knihy": "#6D8F5D",
    "mapy": "#ACC3B9",
    "disertace": "#52796F",
    "katalogy": "#3A0CA3",
    "prózy": "#EF233C",
    "libreta": "#A8DADC",
    "teze": "#9D4EDD",
    "korespondence": "#577590",
    "encyklopedie": "#FFC300",
    "časopisy": "#B5AC9B",
    "památníky": "#C70039",
    "deníky": "#900C3F",
    "apologie": "#FF5733",
}

topic_colors = {
    "poezie": "#003049",
    "biografie": "#006494",
    "filologie": "#0A9396",
    "hagiografie": "#52796F",
    "(téma nespecifikováno)": "#778DA9",
    "lázeňství": "#A3B18A",
    "zemědělství": "#ADC178",
    "náboženství": "#ECBA53",
    "teologie": "#EE9B00",
    "mariologie": "#CA6702",
    "astronomie": "#BB3E03",
    "astrologie": "#AE2012",
    "etická výchova": "#9B2226",
    "homiletika": "#987D6D",
    "slavnosti": "#C2B3A9",
    "christologie": "#D9BF77",
    "kramářské tisky": "#4F5D75",
    "publicistika": "#F4A261",
    "právo": "#E76F51",
    "ekonomie": "#2A9D8F",
    "lékařství": "#264653",
    "geografie": "#F4A261",
    "historiografie": "#E9C46A",
    "vojenství": "#A8DADC",
    "biblické texty": "#457B9D",
    "matematika": "#1D3557",
    "próza": "#8D99AE",
    "liturgika": "#EDF2F4",
    "prosopografie": "#EF233C",
    "divadlo": "#D90429",
    "územní správa": "#9B5DE5",
    "hudba": "#F15BB5",
    "gastronomie": "#FEE440",
    "veterinární lékařství": "#00BBF9",
    "technika": "#00F5D4",
    "státověda": "#F4A261",
    "biologie": "#264653",
    "filozofie": "#2A9D8F",
    "pedagogika": "#E76F51",
    "personalia": "#F4A261",
    "fyzika": "#ACC3B9",
    "architektura": "#D9BF77",
    "geologie": "#E9C46A",
    "bibliografie": "#B5AC9B",
    "chemie": "#457B9D",
    "výtvarné umění": "#1D3557",
    "alchymie": "#6D8F5D",
}

# Define callback to update bar chart
@callback(
    Output("book-count-by-year", "figure"),
    Input("year-range-slider", "value"),
    Input("printer-dropdown", "value"),
    Input("dynasty-dropdown", "value"),
    Input("author-dropdown", "value"),
    Input("language-dropdown", "value"),
    Input("genre-dropdown", "value"),
    Input("topic-dropdown", "value"),
    Input("year-interval-checklist", "value"),
)
def update_book_count_by_year(
    selected_year_range,
    selected_printer,
    selected_dynasty,
    selected_author,
    selected_language,
    selected_genre,
    selected_topic,
    selected_interval,
):
    filtered_df = filter_table(
        df,
        selected_year_range,
        selected_printer,
        selected_dynasty,
        selected_author,
        selected_language,
        selected_genre,
        selected_topic,
    )

    filtered_df["interval"] = (
        filtered_df["publishDate"] // selected_interval
    ) * selected_interval
    interval_counts = filtered_df.groupby("interval")["id"].nunique().reset_index()
    interval_counts.columns = ["publishDate", "count"]

    fig = go.Figure(layout=dict(template="plotly"))
    fig = px.bar(
        interval_counts,
        x="publishDate",
        y="count",
        title="",
        color_discrete_sequence=["DarkGreen"],
        text="count",
    )

    fig.update_layout(
        xaxis_title="Rok vydání",
        yaxis_title="Počet vydání",
        title="<b>Celkový počet vydání</b>",
        xaxis_type="category",
        xaxis=dict(
            tickmode="linear",
            dtick=compute_dtick(interval_counts),
        ),
        margin=dict(l=50, r=50, t=50, b=50),
    )

    return fig


# Define callback to update line chart
@callback(
    Output("book-count-by-year-line", "figure"),
    Input("year-range-slider", "value"),
    Input("printer-dropdown", "value"),
    Input("dynasty-dropdown", "value"),
    Input("author-dropdown", "value"),
    Input("language-dropdown", "value"),
    Input("genre-dropdown", "value"),
    Input("topic-dropdown", "value"),
)
def update_book_count_by_year_line(
    selected_year_range,
    selected_printer,
    selected_dynasty,
    selected_author,
    selected_language,
    selected_genre,
    selected_topic,
):
    filtered_df = filter_table(
        df,
        selected_year_range,
        selected_printer,
        selected_dynasty,
        selected_author,
        selected_language,
        selected_genre,
        selected_topic,
    )

    year_counts = filtered_df.groupby("publishDate")["id"].nunique().reset_index()
    year_counts.columns = ["publishDate", "count"]

    fig = px.line(
        year_counts,
        x="publishDate",
        y="count",
        title="<b>Celkový počet vydání</b>",
        markers=False,
        color_discrete_sequence=["DarkGreen"],
        line_shape="linear",
    )

    fig.update_layout(
        xaxis_title="Rok vydání",
        yaxis_title="Počet vydání",
        title="<b>Celkový počet vydání</b>",
        xaxis_type="category",
        xaxis=dict(
            tickmode="linear",
            dtick=compute_dtick(year_counts),
        ),
        margin=dict(
            l=50, r=50, t=50, b=50
        ),
    )

    return fig

# Define callback to update stacked langauges chart
@callback(
    Output("book-count-by-year-language", "figure"),
    Input("year-range-slider", "value"),
    Input("printer-dropdown", "value"),
    Input("dynasty-dropdown", "value"),
    Input("author-dropdown", "value"),
    Input("language-dropdown", "value"),
    Input("genre-dropdown", "value"),
    Input("topic-dropdown", "value"),
    Input("year-interval-checklist", "value"),
)
def update_book_count_by_year_language(
    selected_year_range,
    selected_printer,
    selected_dynasty,
    selected_author,
    selected_language,
    selected_genre,
    selected_topic,
    selected_interval,
):
    filtered_df = filter_table(
        df,
        selected_year_range,
        selected_printer,
        selected_dynasty,
        selected_author,
        selected_language,
        selected_genre,
        selected_topic,
    )

    filtered_df["language_score"] = 1 / filtered_df.groupby("id")[
        "language_cs"
    ].transform("count")

    filtered_df["interval"] = (
        filtered_df["publishDate"] // selected_interval
    ) * selected_interval
    interval_counts = (
        filtered_df.groupby(["interval", "language_cs"])
        .agg({"language_score": "sum"})
        .reset_index()
    )
    interval_counts.columns = ["publishDate", "language_cs", "count"]

    interval_counts = interval_counts.sort_values(by="publishDate")

    fig = go.Figure(layout=dict(template="plotly"))
    fig = px.bar(
        interval_counts,
        x="publishDate",
        y="count",
        color="language_cs",
        title="<b>Počet vydání s jazykovým rozložením</b>",
        labels={
            "count": "Počet vydání (proporční)",
            "publishDate": "Rok vydání",
            "language_cs": "Jazyk",
        },
        color_discrete_map=language_colors,
    )

    fig.update_layout(
        xaxis_title="Rok vydání",
        yaxis_title="Počet vydání (proporční)",
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis_type="category",
        xaxis=dict(
            categoryorder="category ascending",
            tickmode="linear",
            dtick=compute_dtick(interval_counts),
        ),
    )

    return fig

# Define callback to update stacked genres chart
@callback(
    Output("book-count-by-year-genre", "figure"),
    Input("year-range-slider", "value"),
    Input("printer-dropdown", "value"),
    Input("dynasty-dropdown", "value"),
    Input("author-dropdown", "value"),
    Input("language-dropdown", "value"),
    Input("genre-dropdown", "value"),
    Input("topic-dropdown", "value"),
    Input("year-interval-checklist", "value"),
)
def update_book_count_by_year_genre(
    selected_year_range,
    selected_printer,
    selected_dynasty,
    selected_author,
    selected_language,
    selected_genre,
    selected_topic,
    selected_interval,
):
    filtered_df = filter_table(
        df,
        selected_year_range,
        selected_printer,
        selected_dynasty,
        selected_author,
        selected_language,
        selected_genre,
        selected_topic,
    )

    filtered_df["genre_score"] = 1 / filtered_df.groupby("id")["genre"].transform(
        "count"
    )

    filtered_df["interval"] = (
        filtered_df["publishDate"] // selected_interval
    ) * selected_interval
    interval_counts = (
        filtered_df.groupby(["interval", "genre"])
        .agg({"genre_score": "sum"})
        .reset_index()
    )
    interval_counts.columns = ["publishDate", "genre", "count"]

    interval_counts = interval_counts.sort_values(by="publishDate")

    fig = go.Figure(layout=dict(template="plotly"))
    fig = px.bar(
        interval_counts,
        x="publishDate",
        y="count",
        color="genre",
        title="<b>Počet vydání se žánrovým rozložením</b>",
        labels={
            "count": "Počet vydání (proporční)",
            "publishDate": "Rok vydání",
            "genre": "Žánr",
        },
        color_discrete_map=genre_colors,
    )

    fig.update_layout(
        xaxis_title="Rok vydání",
        yaxis_title="Počet vydání (proporční)",
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis_type="category",
        xaxis=dict(
            categoryorder="category ascending",
            tickmode="linear",
            dtick=compute_dtick(interval_counts),
        ),
    )

    return fig

# Define callback to update stacked topics chart
@callback(
    Output("book-count-by-year-topic", "figure"),
    Input("year-range-slider", "value"),
    Input("printer-dropdown", "value"),
    Input("dynasty-dropdown", "value"),
    Input("author-dropdown", "value"),
    Input("language-dropdown", "value"),
    Input("genre-dropdown", "value"),
    Input("topic-dropdown", "value"),
    Input("year-interval-checklist", "value"),
)
def update_book_count_by_year_topic(
    selected_year_range,
    selected_printer,
    selected_dynasty,
    selected_author,
    selected_language,
    selected_genre,
    selected_topic,
    selected_interval,
):
    filtered_df = filter_table(
        df,
        selected_year_range,
        selected_printer,
        selected_dynasty,
        selected_author,
        selected_language,
        selected_genre,
        selected_topic,
    )

    filtered_df["topic_score"] = 1 / filtered_df.groupby("id")["topic"].transform(
        "count"
    )

    filtered_df["interval"] = (
        filtered_df["publishDate"] // selected_interval
    ) * selected_interval
    interval_counts = (
        filtered_df.groupby(["interval", "topic"])
        .agg({"topic_score": "sum"})
        .reset_index()
    )
    interval_counts.columns = ["publishDate", "topic", "count"]

    interval_counts = interval_counts.sort_values(by="publishDate")

    fig = go.Figure(layout=dict(template="plotly"))
    fig = px.bar(
        interval_counts,
        x="publishDate",
        y="count",
        color="topic",
        title="<b>Počet vydání s tematickým rozložením</b>",
        labels={
            "count": "Počet vydání (proporční)",
            "publishDate": "Rok vydání",
            "topic": "Téma",
        },
        color_discrete_map=topic_colors,
    )

    fig.update_layout(
        xaxis_title="Rok vydání",
        yaxis_title="Počet vydání (proporční)",
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis_type="category",
        xaxis=dict(
            categoryorder="category ascending",
            tickmode="linear",
            dtick=compute_dtick(interval_counts),
        ),
    )

    return fig

# Define callback to update book count by dynasty chart
@callback(
    Output("book-count-by-dynasty", "figure"),
    Input("year-range-slider", "value"),
    Input("printer-dropdown", "value"),
    Input("dynasty-dropdown", "value"),
    Input("author-dropdown", "value"),
    Input("language-dropdown", "value"),
    Input("genre-dropdown", "value"),
    Input("topic-dropdown", "value"),
)
def update_book_count_by_dynasty(
    selected_year_range,
    selected_printer,
    selected_dynasty,
    selected_author,
    selected_language,
    selected_genre,
    selected_topic,
):
    filtered_df = filter_table(
        df,
        selected_year_range,
        selected_printer,
        selected_dynasty,
        selected_author,
        selected_language,
        selected_genre,
        selected_topic,
    )

    dynasty_counts = filtered_df.groupby("Dynastie")["id"].nunique().reset_index()
    dynasty_counts.columns = ["Dynastie", "count"]

    dynasty_counts = dynasty_counts.sort_values(by="count", ascending=False)

    dynasty_counts = dynasty_counts[
        dynasty_counts["Dynastie"].isin(filtered_df["Dynastie"].unique())
    ]

    total_count = dynasty_counts["count"].sum()
    dynasty_counts["percentage"] = (dynasty_counts["count"] / total_count) * 100
    dynasty_counts["totalpercentage"] = (dynasty_counts["count"] / 9698) * 100

    fig = go.Figure(layout=dict(template="plotly"))
    fig = px.bar(
        dynasty_counts,
        x="Dynastie",
        y="count",
        title="<b>Počet vydání podle tiskařské rodiny/dynastie</b>",
        color_discrete_sequence=["IndianRed"],
        text="count",
    )

    fig.update_layout(
        xaxis_title="Tiskařské rodiny/dynastie",
        yaxis_title="Počet vydání",
        xaxis_type="category",
        xaxis=dict(
            categoryorder="sum descending",
            tickmode="linear",
        ),
        margin=dict(l=50, r=50, t=50, b=50),
    )

    return fig


# Define callback to update stacked dynasties langauges chart
@callback(
    Output("book-count-by-dynasty-language", "figure"),
    Input("year-range-slider", "value"),
    Input("printer-dropdown", "value"),
    Input("dynasty-dropdown", "value"),
    Input("author-dropdown", "value"),
    Input("language-dropdown", "value"),
    Input("genre-dropdown", "value"),
    Input("topic-dropdown", "value"),
)
def update_book_count_by_dynasty_language(
    selected_year_range,
    selected_printer,
    selected_dynasty,
    selected_author,
    selected_language,
    selected_genre,
    selected_topic,
):
    filtered_df = filter_table(
        df,
        selected_year_range,
        selected_printer,
        selected_dynasty,
        selected_author,
        selected_language,
        selected_genre,
        selected_topic,
    )

    filtered_df["language_score"] = 1 / filtered_df.groupby(["Dynastie", "id"])[
        "language_cs"
    ].transform("count")

    dynasty_counts = (
        filtered_df.groupby(["Dynastie", "language_cs"])
        .agg({"language_score": "sum"})
        .reset_index()
    )
    dynasty_counts.columns = ["Dynastie", "language_cs", "count"]

    fig = go.Figure(layout=dict(template="plotly"))
    fig = px.bar(
        dynasty_counts,
        x="Dynastie",
        y="count",
        color="language_cs",
        title="<b>Počet vydání podle tiskařských rodin/dynastií a jazyků</b>",
        labels={
            "count": "Počet vydání (proporční)",
            "Dynastie": "Tiskařská rodina/dynastie",
            "language_cs": "Jazyk",
        },
        color_discrete_map=language_colors,
    )

    fig.update_layout(
        xaxis_title="Tiskařská dynastie",
        yaxis_title="Počet vydání (proporční)",
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis_type="category",
        xaxis=dict(
            categoryorder="sum descending",
            tickmode="linear",
        ),
    )

    return fig


# Define callback to update stacked dynasties genres chart
@callback(
    Output("book-count-by-dynasty-genre", "figure"),
    Input("year-range-slider", "value"),
    Input("printer-dropdown", "value"),
    Input("dynasty-dropdown", "value"),
    Input("author-dropdown", "value"),
    Input("language-dropdown", "value"),
    Input("genre-dropdown", "value"),
    Input("topic-dropdown", "value"),
)
def update_book_count_by_dynasty_genre(
    selected_year_range,
    selected_printer,
    selected_dynasty,
    selected_author,
    selected_language,
    selected_genre,
    selected_topic,
):
    filtered_df = filter_table(
        df,
        selected_year_range,
        selected_printer,
        selected_dynasty,
        selected_author,
        selected_language,
        selected_genre,
        selected_topic,
    )

    filtered_df["genre_score"] = 1 / filtered_df.groupby("id")["genre"].transform(
        "count"
    )

    dynasty_counts = (
        filtered_df.groupby(["Dynastie", "genre"])
        .agg({"genre_score": "sum"})
        .reset_index()
    )
    dynasty_counts.columns = ["Dynastie", "genre", "count"]

    dynasty_counts = dynasty_counts.sort_values(by="Dynastie")

    fig = go.Figure(layout=dict(template="plotly"))
    fig = px.bar(
        dynasty_counts,
        x="Dynastie",
        y="count",
        color="genre",
        title="<b>Počet vydání podle tiskařských rodin/dynastií a žánrů</b>",
        labels={
            "count": "Počet vydání (proporční)",
            "Dynastie": "Tiskařská rodina/dynastie",
            "genre": "Žánr",
        },
        color_discrete_map=genre_colors,
    )

    fig.update_layout(
        xaxis_title="Tiskařská dynastie",
        yaxis_title="Počet vydání (proporční)",
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis_type="category",
        xaxis=dict(
            categoryorder="sum descending",
            tickmode="linear",
        ),
    )

    return fig

# Define callback to update stacked dynasties topics chart
@callback(
    Output("book-count-by-dynasty-topic", "figure"),
    Input("year-range-slider", "value"),
    Input("printer-dropdown", "value"),
    Input("dynasty-dropdown", "value"),
    Input("author-dropdown", "value"),
    Input("language-dropdown", "value"),
    Input("genre-dropdown", "value"),
    Input("topic-dropdown", "value"),
)
def update_book_count_by_dynasty_topic(
    selected_year_range,
    selected_printer,
    selected_dynasty,
    selected_author,
    selected_language,
    selected_genre,
    selected_topic,
):
    filtered_df = filter_table(
        df,
        selected_year_range,
        selected_printer,
        selected_dynasty,
        selected_author,
        selected_language,
        selected_genre,
        selected_topic,
    )

    filtered_df["topic_score"] = 1 / filtered_df.groupby("id")["topic"].transform(
        "count"
    )

    dynasty_counts = (
        filtered_df.groupby(["Dynastie", "topic"])
        .agg({"topic_score": "sum"})
        .reset_index()
    )
    dynasty_counts.columns = ["Dynastie", "topic", "count"]

    dynasty_counts = dynasty_counts.sort_values(by="Dynastie")

    fig = go.Figure(layout=dict(template="plotly"))
    fig = px.bar(
        dynasty_counts,
        x="Dynastie",
        y="count",
        color="topic",
        title="<b>Počet vydání podle tiskařských rodin/dynastií a témat</b>",
        labels={
            "count": "Počet vydání (proporční)",
            "Dynastie": "Tiskařská rodina/dynastie",
            "topic": "Téma",
        },
        color_discrete_map=topic_colors,
    )

    fig.update_layout(
        xaxis_title="Tiskařská dynastie",
        yaxis_title="Počet vydání (proporční)",
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis_type="category",
        xaxis=dict(
            categoryorder="sum descending",
            tickmode="linear",
        ),
    )

    return fig


# Define callback to update book count by printer chart
@callback(
    Output("book-count-by-printer", "figure"),
    Input("year-range-slider", "value"),
    Input("printer-dropdown", "value"),
    Input("dynasty-dropdown", "value"),
    Input("author-dropdown", "value"),
    Input("language-dropdown", "value"),
    Input("genre-dropdown", "value"),
    Input("topic-dropdown", "value"),
)
def update_book_count_by_printer(
    selected_year_range,
    selected_printer,
    selected_dynasty,
    selected_author,
    selected_language,
    selected_genre,
    selected_topic,
):
    filtered_df = filter_table(
        df,
        selected_year_range,
        selected_printer,
        selected_dynasty,
        selected_author,
        selected_language,
        selected_genre,
        selected_topic,
    )

    printer_counts = filtered_df.groupby("Printer")["id"].nunique().reset_index()
    printer_counts.columns = ["Printer", "count"]

    printer_counts = printer_counts.sort_values(by="count", ascending=False)

    printer_counts = printer_counts[
        printer_counts["Printer"].isin(filtered_df["Printer"].unique())
    ]

    fig = go.Figure(layout=dict(template="plotly"))
    fig = px.bar(
        printer_counts,
        x="Printer",
        y="count",
        title="<b>Počet vydání podle tiskárny</b>",
        color_discrete_sequence=["CadetBlue"],
        text="count",
    )

    fig.update_layout(
        xaxis_title="Tiskárny",
        yaxis_title="Počet vydání",
        xaxis_type="category",
        margin=dict(
            l=50, r=50, t=50, b=50
        ),  
    )

    return fig


# Define callback to update book count by language chart
@callback(
    Output("book-count-by-language", "figure"),
    Input("year-range-slider", "value"),
    Input("printer-dropdown", "value"),
    Input("dynasty-dropdown", "value"),
    Input("author-dropdown", "value"),
    Input("language-dropdown", "value"),
    Input("genre-dropdown", "value"),
    Input("topic-dropdown", "value"),
)
def update_book_count_by_language(
    selected_year_range,
    selected_printer,
    selected_dynasty,
    selected_author,
    selected_language,
    selected_genre,
    selected_topic,
):
    filtered_df = filter_table(
        df,
        selected_year_range,
        selected_printer,
        selected_dynasty,
        selected_author,
        selected_language,
        selected_genre,
        selected_topic,
    )

    language_counts = filtered_df.groupby("language_cs")["id"].nunique().reset_index()
    language_counts.columns = ["language_cs", "count"]

    language_counts = language_counts.sort_values(by="count", ascending=False)

    language_counts = language_counts[
        language_counts["language_cs"].isin(filtered_df["language_cs"].unique())
    ]

    fig = go.Figure(layout=dict(template="plotly"))
    fig = px.bar(
        language_counts,
        x="language_cs",
        y="count",
        title="<b>Počet vydání podle jazyka</b>",
        color_discrete_sequence=["Maroon"],
        text="count",
    )

    fig.update_layout(
        xaxis_title="Jazyky",
        yaxis_title="Počet vydání",
        xaxis_type="category",
        margin=dict(l=50, r=50, t=50, b=50),
    )

    return fig


# Define callback to update book count by genre chart
@callback(
    Output("book-count-by-genre", "figure"),
    Input("year-range-slider", "value"),
    Input("printer-dropdown", "value"),
    Input("dynasty-dropdown", "value"),
    Input("author-dropdown", "value"),
    Input("language-dropdown", "value"),
    Input("genre-dropdown", "value"),
    Input("topic-dropdown", "value"),
)
def update_book_count_by_genre(
    selected_year_range,
    selected_printer,
    selected_dynasty,
    selected_author,
    selected_language,
    selected_genre,
    selected_topic,
):
    filtered_df = filter_table(
        df,
        selected_year_range,
        selected_printer,
        selected_dynasty,
        selected_author,
        selected_language,
        selected_genre,
        selected_topic,
    )

    genre_counts = filtered_df.groupby("genre")["id"].nunique().reset_index()
    genre_counts.columns = ["genre", "count"]

    genre_counts = genre_counts.sort_values(by="count", ascending=False)

    genre_counts = genre_counts.dropna(subset=["genre"])

    genre_counts = genre_counts[
        genre_counts["genre"].isin(filtered_df["genre"].unique())
    ]

    fig = go.Figure(layout=dict(template="plotly"))
    fig = px.bar(
        genre_counts,
        x="genre",
        y="count",
        title="<b>Počet vydání podle žánru</b>",
        color_discrete_sequence=["DarkSeaGreen"],
        text="count",
    )

    fig.update_layout(
        xaxis_title="Žánry",
        yaxis_title="Počet vydání",
        xaxis_type="category",
        margin=dict(l=50, r=50, t=50, b=50),
    )

    return fig


# Define callback to update book count by topic chart
@callback(
    Output("book-count-by-topic", "figure"),
    Input("year-range-slider", "value"),
    Input("printer-dropdown", "value"),
    Input("dynasty-dropdown", "value"),
    Input("author-dropdown", "value"),
    Input("language-dropdown", "value"),
    Input("genre-dropdown", "value"),
    Input("topic-dropdown", "value"),
)
def update_book_count_by_topic(
    selected_year_range,
    selected_printer,
    selected_dynasty,
    selected_author,
    selected_language,
    selected_genre,
    selected_topic,
):
    filtered_df = filter_table(
        df,
        selected_year_range,
        selected_printer,
        selected_dynasty,
        selected_author,
        selected_language,
        selected_genre,
        selected_topic,
    )

    topic_counts = filtered_df.groupby("topic")["id"].nunique().reset_index()
    topic_counts.columns = ["topic", "count"]

    topic_counts = topic_counts.sort_values(by="count", ascending=False)

    topic_counts = topic_counts.dropna(subset=["topic"])

    topic_counts = topic_counts[
        topic_counts["topic"].isin(filtered_df["topic"].unique())
    ]

    fig = go.Figure(layout=dict(template="plotly"))
    fig = px.bar(
        topic_counts,
        x="topic",
        y="count",
        title="<b>Počet vydání podle tématu</b>",
        color_discrete_sequence=["MidnightBlue"],
        text="count",
    )

    fig.update_layout(
        xaxis_title="Témata",
        yaxis_title="Počet vydání",
        xaxis_type="category",
        margin=dict(l=50, r=50, t=50, b=50),
    )

    return fig


# Define callback to update correspondence analysis chart for genres
@callback(
    Output("correspondence-analysis-genre", "figure"),
    Input("year-range-slider", "value"),
    Input("printer-dropdown", "value"),
    Input("dynasty-dropdown", "value"),
    Input("author-dropdown", "value"),
    Input("language-dropdown", "value"),
    Input("genre-dropdown", "value"),
    Input("topic-dropdown", "value"),
)
def update_correspondence_analysis_genre(
    selected_year_range,
    selected_printer,
    selected_dynasty,
    selected_author,
    selected_language,
    selected_genre,
    selected_topic,
):
    filtered_df = filter_table(
        df,
        selected_year_range,
        selected_printer,
        selected_dynasty,
        selected_author,
        selected_language,
        selected_genre,
        selected_topic,
    )

    contingency_table = pd.crosstab(filtered_df["genre"], filtered_df["language_cs"])

    if contingency_table.shape[0] < 3 or contingency_table.shape[1] < 3:
        fig_ca = go.Figure()
        fig_ca.add_annotation(
            text="Nedostatek dat pro provedení korespondenční analýzy",
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=20),
        )
        fig_ca.update_layout(
            title="Korespondenční analýza – jazyky a žánry",
            autosize=True,
            width=None,
            height=None,
        )
        return fig_ca

    ca = prince.CA(n_components=2)
    ca = ca.fit(contingency_table)

    row_coords = ca.row_coordinates(contingency_table)
    col_coords = ca.column_coordinates(contingency_table)

    df_ca_plot = pd.concat(
        [row_coords, col_coords], keys=["Žánry", "Jazyky"]
    ).reset_index()
    df_ca_plot.columns = ["Prvky", "Category", "Dim1", "Dim2"]

    color_map = {"Žánry": "DarkSeaGreen", "Jazyky": "Maroon"}
    df_ca_plot["Color"] = df_ca_plot["Prvky"].map(color_map)

    fig_ca = go.Figure()

    for prvky, group in df_ca_plot.groupby("Prvky"):
        fig_ca.add_trace(
            go.Scatter(
                x=group["Dim1"],
                y=group["Dim2"],
                mode="markers+text",
                text=group["Category"],
                marker=dict(color=color_map[prvky]),
                name=prvky,
                textposition="top center",
            )
        )

    fig_ca.update_layout(
        title="<b>Korespondenční analýza – jazyky a žánry</b>",
        xaxis_title="Dimenze 1",
        yaxis_title="Dimenze 2",
        autosize=True
    )

    return fig_ca


# Define callback to update correspondence analysis chart for topics
@callback(
    Output("correspondence-analysis-topic", "figure"),
    Input("year-range-slider", "value"),
    Input("printer-dropdown", "value"),
    Input("dynasty-dropdown", "value"),
    Input("author-dropdown", "value"),
    Input("language-dropdown", "value"),
    Input("genre-dropdown", "value"),
    Input("topic-dropdown", "value"),
)
def update_correspondence_analysis_topic(
    selected_year_range,
    selected_printer,
    selected_dynasty,
    selected_author,
    selected_language,
    selected_genre,
    selected_topic,
):
    filtered_df = filter_table(
        df,
        selected_year_range,
        selected_printer,
        selected_dynasty,
        selected_author,
        selected_language,
        selected_genre,
        selected_topic,
    )

    contingency_table = pd.crosstab(filtered_df["topic"], filtered_df["language_cs"])

    if contingency_table.shape[0] < 3 or contingency_table.shape[1] < 3:
        fig_ca = go.Figure()
        fig_ca.add_annotation(
            text="Nedostatek dat pro provedení korespondenční analýzy",
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=20),
        )
        fig_ca.update_layout(
            title="Korespondenční analýza – jazyky a témata",
            autosize=True,
            width=None,
            height=None,
        )
        return fig_ca

    ca = prince.CA(n_components=2)
    ca = ca.fit(contingency_table)

    row_coords = ca.row_coordinates(contingency_table)
    col_coords = ca.column_coordinates(contingency_table)

    df_ca_plot = pd.concat(
        [row_coords, col_coords], keys=["Témata", "Jazyky"]
    ).reset_index()
    df_ca_plot.columns = ["Prvky", "Category", "Dim1", "Dim2"]

    color_map = {"Témata": "MidnightBlue", "Jazyky": "PaleVioletRed"}
    df_ca_plot["Color"] = df_ca_plot["Prvky"].map(color_map)

    fig_ca = go.Figure()

    for prvky, group in df_ca_plot.groupby("Prvky"):
        fig_ca.add_trace(
            go.Scatter(
                x=group["Dim1"],
                y=group["Dim2"],
                mode="markers+text",
                text=group["Category"],
                marker=dict(color=color_map[prvky]),
                name=prvky,
                textposition="top center",
            )
        )

    fig_ca.update_layout(
        title="<b>Korespondenční analýza – jazyky a témata</b>",
        xaxis_title="Dimenze 1",
        yaxis_title="Dimenze 2",
        autosize=True
    )

    return fig_ca
