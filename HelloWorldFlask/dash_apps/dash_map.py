# import logging

from pg_shared.dash_utils import create_dash_app_util
from hello_world import core, menu, Langstrings
from flask import session

from dash import html, dcc, callback_context, no_update

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
                html.H1("World Population", id="heading", className="header-title")
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
    
    # This callback handles: A) initial setup of the menu, langstring labels, drop-down options (also langstrings) AND B) the chart.
    # The callback_context is used to control whether or not A updates occur, as this should only occur on initial page load.
    # Doing this saves having two call-backs on the first page load, one for each of A and B
    @app.callback(
        [
            Output("menu", "children"),
            Output("heading", "children"),
            Output("show_label", "children"),
            Output("show", "options"),
            Output("pop_chart", "figure")  # chart is last
        ],
        [
            Input("show", "value"),  # the default value is set in the layout, so we will get the right chart output
            Input("location", "pathname"),
            Input("location", "search")],
    )
    def update_chart(show, pathname, querystring):
        specification_id = pathname.split('/')[-1]
        tag = None
        if len(querystring) > 0:
            for param, value in [pv.split('=') for pv in querystring[1:].split("&")]:
                if param == "tag":
                    tag = value
                    break
        spec = core.get_specification(specification_id)
        langstrings = Langstrings(spec.lang)
    
        if callback_context.triggered_id == "location":
            # initial load
            menu_children = spec.make_menu(menu, langstrings, core.plaything_root, view_name, query_string=querystring, for_dash=True)
            show_options = {k: langstrings.get(k) for k in ["POP", "YEARLY_CHANGE"]}
            output = [
                menu_children,
                langstrings.get("POP"),
                langstrings.get("SHOW_LABEL"),
                show_options]
        else:
            output = [no_update] * 4

        # TODO find a method for capturing the initial referrer. (the referrer in a callback IS the page itself)
        core.record_activity(view_name, specification_id, session, activity={"opt": show}, referrer="(callback)", tag=tag)
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

        output.append({"data": data_chunk, "layout": layout_chunk})

        return output

    return app.server
