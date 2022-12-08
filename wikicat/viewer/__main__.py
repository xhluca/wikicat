import argparse
import json
from pathlib import Path
from textwrap import dedent

import dash
from dash import Input, Output, State
import dash_bootstrap_components as dbc

from .. import CategoryGraph, standardize
from . import build_app
from . import utils
from . import components as comp


def run(load_dir, load_name, port=8050, host="0.0.0.0", debug=True):
    # Load category graph and insert artificial root node
    load_dir = Path(load_dir).expanduser()
    ROOT_ID = "((ROOT))"
    cg = CategoryGraph.read_json(load_dir / load_name)
    cg = utils.insert_artificial_root_node(cg, ROOT_ID)
    root = cg.page_from_id(ROOT_ID)

    # Build app and run
    app = build_app(cg, root)
    app.run_server(debug=debug, host=host, port=port)


def build_parser():
    parser = argparse.ArgumentParser(
        description="""
        Run a Dash app to explore a category graph.

        The category graph is loaded from a JSON file.

        The app is accessible at http://<host>:<port>
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--load_dir", type=str, default="~/.wikicat_data")
    parser.add_argument("--load_name", type=str, default="category_graph_20181220.json")
    parser.add_argument("--port", type=int, default=8050)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--debug", type=bool, default=True)

    return parser

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    run(**vars(args))
