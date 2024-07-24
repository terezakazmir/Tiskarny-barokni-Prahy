import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=True),
        html.Div(
            [
                html.Div(
                    dcc.Link(
                        html.Img(
                            src=f"/assets/icons/{page['name'].lower()}.svg",
                            className="page-icon",
                        ),
                        href=page["relative_path"],
                    ),
                    className="page-link",
                )
                for page in dash.page_registry.values()
            ],
            className="page-links",
        ),
        dash.page_container,
    ]
)


@app.callback(
    dash.dependencies.Output("url", "pathname"),
    [dash.dependencies.Input("url", "pathname")],
)
def redirect_to_default(pathname):
    if pathname == "/" or pathname is None:
        return "/1-mapa"
    return dash.no_update


if __name__ == "__main__":
    app.run_server(debug=False)
