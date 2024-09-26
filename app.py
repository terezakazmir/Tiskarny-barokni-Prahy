import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import argparse

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


parser = argparse.ArgumentParser(
    description="Run the Dash app",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument("--port", type=int, default=8050, help="Port to run the app on")
parser.add_argument(
    "--host", type=str, default="0.0.0.0", help="Host to run the app on"
)
parser.add_argument("--debug", action="store_true", help="Run the app in debug mode")

args = parser.parse_args()

if __name__ == "__main__":
    app.run(host=args.host, port=str(args.port), debug=args.debug)
