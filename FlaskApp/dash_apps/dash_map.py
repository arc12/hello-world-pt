from pg_shared.dash_utils import create_dash_app_util
from plaything import PLAYTHING_NAME, core, menu, Langstrings
from flask import request, session

from dash import html, dcc, ctx

from dash.dependencies import Output, Input, State

view_name = "chart"

def create_dash(server, url_rule, url_base_pathname):
    """Create a Dash view"""
    app = create_dash_app_util(server, url_rule, url_base_pathname)

    # dash app definitions goes here
    app.config.suppress_callback_exceptions = True
    app.title = "Hello World Chart"

    app.layout = html.Div([
        dcc.Location(id="location"),
        html.Div(id="menu"),
        html.Div(
            [
                html.H1("Pop chart", id="heading", className="header-title")
            ],
            className="header"),

        html.Div(
            [
                html.Label("Show:", id="show_label"),
                html.Div(
                    dcc.Dropdown(value="POP", id="show", searchable=False, clearable=False, style={"margin-left": "10px"}),
                    style={"width": "250px"}
                )
            ],
            style={"display": "flex"}
        ),

        html.Div(
            dcc.Loading(
                dcc.Graph(id="pop_chart"),
                type="circle"
            )
        )
    ],
    className="wrapper"
    )

    @app.callback(
        [Output("pop_chart", "figure")],
        [Input("show", "value"), State("location", "pathname"), State("location", "search")],
    )
    def update_chart(show, pathname, querystring):
        
        specification_id = pathname.split('/')[-1]
        tag = None
        if len(querystring) > 0:
            for param, value in [pv.split('=') for pv in querystring[1:].split("&")]:
                if param == "tag":
                    tag = value
                    break

        # TODO find a method for capturing the initial referrer. (the referrer in a callback IS the page itself)
        core.record_activity(view_name, specification_id, session, activity={"opt": show}, referrer="(callback)", tag=tag)
        
        spec = core.get_specification(specification_id)
        langstrings = Langstrings(spec.lang)
        data = spec.load_asset_dataframe("world_pop")

        data_chunk = [
            {
                "x": data.Year,
                "y": data["World Population" if show == "POP" else "Yearly Change"],
                "type": "lines",
                "hoverinfo": "none",
                "hovertemplate": "%{x}: %{y}<extra></extra>"
            }
        ]

        layout_chunk = {
            "title": {
                "text": langstrings.get(show),
                "x": 0.05,
                "xanchor": "left",
            },
            "legend": {"y": 0.02, "yanchor": "top"},
            "xaxis": {"title": langstrings.get("YEAR"), "fixedrange": False},
            "yaxis": {"title": langstrings.get(show), "ticksuffix": "%" if show == "YEARLY_CHANGE" else "", "fixedrange": False}
            # "colorway": line_colours
        }

        figure = {"data": data_chunk, "layout": layout_chunk}

        return [figure]

    @app.callback(
        [Output("menu", "children"), Output("heading", "children"), Output("show_label", "children"), Output("show", "options")],
        [Input("location", "pathname"), Input("location", "search")],
    )
    def setup_initial(pathname, querystring):
        specification_id = pathname.split('/')[-1]
        spec = core.get_specification(specification_id)
        
        langstrings = Langstrings(spec.lang)

        menu_children = spec.make_menu(menu, langstrings, core.plaything_root, view_name, query_string=querystring, for_dash=True)

        show_options = {k: langstrings.get(k) for k in ["POP", "YEARLY_CHANGE"]}
        
        return [
            menu_children,
            langstrings.get("POP"),
            langstrings.get("SHOW_LABEL"),
            show_options]

    return app.server
