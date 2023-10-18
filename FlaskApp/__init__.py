from os import  environ
import logging

from flask import Flask, render_template, session, request, abort

from pg_shared import prepare_app
from FlaskApp.dash_apps import dash_map
from plaything import PLAYTHING_NAME, Langstrings, core, menu

app = prepare_app(Flask(__name__))

plaything_root = core.plaything_root

@app.route(f"{plaything_root}/")
# Root shows set of index cards, one for each enabled plaything specification. There is no context language for this; lang is declared at specification level.
# Order of cards follows alphanum sort of the specification ids. TODO consider sort by title.
def index():
    core.record_activity("ROOT", None, session, referrer=request.referrer)

    return render_template("index_cards.html", specifications=core.get_specifications(),
                           with_link=True, url_base=plaything_root, initial_view="hello", query_string=request.query_string.decode())

@app.route(f"{plaything_root}/validate")
# similar output style to root route, but performs some checks and shows error-case specifications and disabled specifications
def validate():
    core.record_activity("validate", None, session, referrer=request.referrer, tag=request.args.get("tag", None))

    return render_template("index_cards.html",
                           specifications=core.get_specifications(include_disabled=True, check_assets=["world_pop"], check_optional_assets=["about"]),
                           with_link=False)

@app.route(f"{plaything_root}/hello/<specification_id>", methods=['GET'])
# view name = "hello", the initial view
def hello(specification_id: str):
    view_name = "hello"

    if specification_id not in core.specification_ids:
        msg = f"Request with invalid specification id = {specification_id} for plaything {PLAYTHING_NAME}"
        logging.warn(msg)
        abort(404, msg)

    core.record_activity(view_name, specification_id, session, referrer=request.referrer, tag=request.args.get("tag", None))
    
    spec = core.get_specification(specification_id)
    langstrings = Langstrings(spec.lang)
    return render_template("hello.html",
                           langstrings=langstrings,
                           top_menu=spec.make_menu(menu, langstrings, plaything_root, view_name, query_string=request.query_string.decode()))

@app.route(f"{plaything_root}/about/<specification_id>", methods=['GET'])
def about(specification_id: str):
    view_name = "about"

    core.record_activity(view_name, specification_id, session, referrer=request.referrer, tag=request.args.get("tag", None))
    spec = core.get_specification(specification_id)
    if "about" not in spec.asset_map:
        abort(404, "'about' is not configured")

    langstrings = Langstrings(spec.lang)

    return render_template("about.html",
                           about=spec.load_asset_markdown(view_name, render=True),
                           top_menu=spec.make_menu(menu, langstrings, plaything_root, view_name, query_string=request.query_string.decode()))

# DASH Apps and route spec
app = dash_map.create_dash(app, f"{plaything_root}/chart/<specification_id>", f"{plaything_root}/dash/chart/")

# if __name__ == "__main__":
#     app.run()