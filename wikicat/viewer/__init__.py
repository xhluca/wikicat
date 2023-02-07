from pathlib import Path
from textwrap import dedent

import dash
from dash import Input, Output, State
import dash_bootstrap_components as dbc

from .. import standardize, CategoryGraph
from ..constants import ARTICLE
from . import utils
from . import components as comp


def assign_callbacks(
    app: dash.Dash, cg: CategoryGraph, cyto_graph, inp, btn, cl, sw, md, sto, dd, root
):
    """
    Assign callbacks to the app. This function is called by `wikicat.viewer.app.create_app`.
    It is separated from `create_app` to ensure modularity. It takes in all the components
    (cyto_graph, inp, btn, cl, sw, md, sto, dd, root) as arguments in order to access their
    `id` attributes. It also takes in the `cg` argument to access the `CategoryGraph` object
    and the `root` argument to access the root node id.
    """

    # Define callbacks
    @app.callback(
        Output(inp.choose_article, "valid"),
        Output(inp.choose_article, "invalid"),
        Output(btn.show_path, "disabled"),
        Input(inp.choose_article, "value"),
    )
    def validate_inp_choose_article(text):
        if text is None or text == "":
            return False, True, True

        text = standardize(text)

        if text in cg.title_to_id[ARTICLE]:
            return True, False, False
        else:
            return False, True, True

    @app.callback(Output(md.clicked_node, "children"), Input(cyto_graph, "tapNodeData"))
    def update_clicked_node(node_data):
        if node_data is None:
            return "No node selected"

        page = cg.get_page_from_id(node_data["id"])

        articles = [c for c in cg.get_children(page) if c.is_article()]

        article_list = [
            f"- [{a.title.replace('_', ' ')}]({a.get_url()})" for a in articles
        ]
        article_list_str = "\n".join(article_list)

        pre = dedent(
            f"""
            ## [{page.title.replace('_', ' ')}]({page.get_url()})
            
            ID: {page.id}

            Namespace: {page.namespace}
            
            Articles:

            """
        )

        return pre + article_list_str

    @app.callback(
        Output(cl.children_to_display, "options"),
        Output(cl.children_to_display, "value"),
        Output(cl.parents_to_display, "options"),
        Output(cl.parents_to_display, "value"),
        Input(sw.children, "value"),
        Input(sw.parents, "value"),
        Input(btn.reset_graph, "n_clicks"),
        Input(cyto_graph, "tapNodeData"),
        State(sto.selected_nodes, "data"),
    )
    def update_checklist(
        child_checked, parent_checked, n_clicks, clicked_data, stored_data
    ):
        if clicked_data is None:
            raise dash.exceptions.PreventUpdate

        if utils.was_triggered(btn.reset_graph, "n_clicks"):
            return [], [], [], []

        if utils.was_triggered(sw.children, "value"):
            if child_checked:
                res = cg.get_children(id=clicked_data["id"], return_as="id")
            else:
                res = []

            return dash.no_update, res, dash.no_update, dash.no_update

        if utils.was_triggered(sw.parents, "value"):
            if parent_checked:
                res = cg.get_parents(id=clicked_data["id"], return_as="id")
            else:
                res = []

            return dash.no_update, dash.no_update, dash.no_update, res

        stored_data = set(stored_data)
        children = [
            c for c in cg.get_children(id=clicked_data["id"]) if c.is_category()
        ]
        parents = [p for p in cg.get_parents(id=clicked_data["id"]) if p.is_category()]

        options_children = [
            {"label": c.title.replace("_", " "), "value": c.id} for c in children
        ]
        value_children = [c.id for c in children if c.id in stored_data]

        options_parents = [
            {"label": p.title.replace("_", " "), "value": p.id} for p in parents
        ]
        value_parents = [p.id for p in parents if p.id in stored_data]

        return options_children, value_children, options_parents, value_parents

    @app.callback(
        Output(sto.selected_nodes, "data"),
        Input(btn.update_graph, "n_clicks"),
        Input(btn.reset_graph, "n_clicks"),
        Input(btn.show_path, "n_clicks"),
        State(cl.children_to_display, "value"),
        State(cl.children_to_display, "options"),
        State(cl.parents_to_display, "value"),
        State(cl.parents_to_display, "options"),
        State(inp.choose_article, "value"),
        State(dd.choose_tlc, "value"),
        State(sto.selected_nodes, "data"),
    )
    def update_selected_nodes(
        n_clicks_update,
        n_clicks_reset,
        n_clicks_show_path,
        selected_children,
        options_children,
        selected_parents,
        options_parents,
        chosen_article_name,
        chosen_tlc_id,
        stored_data,
    ):
        if utils.was_triggered(btn.reset_graph, "n_clicks"):
            return [root.id]

        if utils.was_triggered(btn.show_path, "n_clicks"):
            if chosen_article_name is None:
                return dash.no_update

            article = cg.get_page_from_title(chosen_article_name, namespace="article")
            target = cg.get_page_from_id(chosen_tlc_id)

            backlinks = utils.bfs_with_backlinks(cg, article, target)
            chain = utils.extract_chain(backlinks, article, target)

            return [root.id] + chain

        if n_clicks_update is None:
            return dash.no_update

        # If btn_update_graph was triggered, continue here
        if selected_children is None and selected_parents is None:
            return dash.no_update

        if selected_children is None:
            selected_children = []

        if selected_parents is None:
            selected_parents = []

        if stored_data is None:
            stored_data = []

        selected = set(selected_children + selected_parents)
        options = options_children + options_parents

        stored_data = set(stored_data)
        not_selected = [o["value"] for o in options if o["value"] not in selected]

        for id in selected:
            stored_data.add(id)

        for i in not_selected:
            stored_data.discard(i)

        return list(stored_data)

    @app.callback(
        Output(cyto_graph, "elements"),
        Input(sto.selected_nodes, "data"),
    )
    def update_graph(selected_nodes):
        if selected_nodes is None:
            return dash.no_update

        selected_nodes = set(selected_nodes)

        nodes = []
        edges = []

        for id in selected_nodes:
            page = cg.get_page_from_id(id)
            node = {
                "data": {"id": id, "label": page.title.replace("_", " ")},
                "classes": page.namespace,
            }

            if node["data"]["id"] == root.id:
                node["classes"] += " root"

            nodes.append(node)
            for child_id in cg.get_children(id=id, return_as="id"):
                if child_id in selected_nodes:
                    edges.append(
                        {
                            "data": {"source": id, "target": child_id},
                        }
                    )

            for parent_id in cg.get_parents(id=id, return_as="id"):
                if parent_id in selected_nodes:
                    edges.append(
                        {
                            "data": {"source": parent_id, "target": id},
                        }
                    )

        return nodes + edges


def build_app(
    cg: CategoryGraph,
    title="Wikipedia Categories Explorer",
    style=None,
    **kwargs,
) -> dash.Dash:
    """
    Builds the Dash app. The app is a Dash app with a Cytoscape graph, a panel with
    buttons, inputs, dropdowns, checklists and markdowns, and a store for the selected
    nodes. The app is built using the components defined in the components module.
    It can be started by using the `wikicat.viewer.run()` function. By default,
    it will use the bootstrap style.
    """
    if style is None:
        style = dbc.themes.BOOTSTRAP

    ROOT_ID = "((ROOT))"
    cg = utils.insert_artificial_root_node(cg, ROOT_ID)
    root = cg.get_page_from_id(ROOT_ID)

    # Define app
    app = dash.Dash(__name__, external_stylesheets=[style], title=title, **kwargs)

    # Build components
    cyto_graph = comp.build_cytoscape_graph(root)
    dd = comp.build_dropdowns(cg)
    cl = comp.build_checklists()
    btn = comp.build_buttons()
    sw = comp.build_switches()
    inp = comp.build_inputs()
    md = comp.build_markdowns()
    sto = comp.build_stores(root.id)
    panel = comp.build_panel(btn, inp, md, dd)
    cards = comp.build_cards(cl=cl, sw=sw)
    cards_column = comp.build_card_column(cards)

    # Build layout
    app.layout = comp.build_layout(cyto_graph, panel, cards_column, sto)

    # Assign callbacks to make app interactive
    assign_callbacks(app, cg, cyto_graph, inp, btn, cl, sw, md, sto, dd, root)

    return app


def run(load_dir, load_name, port=8050, host="0.0.0.0", debug=True, app=None):
    """
    Runs the app. If `app` is None, a new app is built. Otherwise, the given app is
    used. The app is built using the `wikicat.viewer.build_app()` function.

    Parameters
    ----------
    load_dir : str
        Directory where the category graph is stored. If you used `wikicat.processing`,
        then the directory should be `~/.wikicat_data/enwiki_2018_12_20`.
    load_name : str
        Name of the category graph file. If you used `wikicat.processing`, then
        the file is called `category_graph.json`.
    port : int, optional
        Port to run the app on, by default 8050 following the Dash convention.
    host : str, optional
        Host to run the app on, by default "0.0.0.0" to make it accessible from
        other devices on the network.
    debug : bool, optional
        Whether to run the app in debug mode, by default True

    Example
    -------
    >>> import wikicat.viewer as viewer
    >>> app = viewer.build_app()
    >>> viewer.run(
    ...     load_dir="~/.wikicat_data/enwiki_2018_12_20", load_name="category_graph.json", app=app
    ... )
    """
    # Load category graph and insert artificial root node
    load_dir = Path(load_dir).expanduser()
    cg = CategoryGraph.read_json(load_dir / load_name)

    # Build app and run
    if app is None:
        app = build_app(cg)

    app.run_server(debug=debug, host=host, port=port)
