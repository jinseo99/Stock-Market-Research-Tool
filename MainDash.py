import dash
from dash import Dash, html, dcc

app = Dash(__name__, use_pages=True)

app.layout = html.Div([
    # html.H1('Multi-page app with Dash Pages'),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"]),
            style= {"margin-right":"10px"}
        ) for page in dash.page_registry.values()
    ], style={"display":"flex"}),
    dash.page_container,
    ], style={
        "font-family": "Arial, Helvetica, sans-serif",
    }
)

if __name__ == '__main__':
    app.run(debug=True,host="192.168.0.102")
