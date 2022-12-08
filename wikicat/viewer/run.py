import argparse
import json
from textwrap import dedent

import dash
from dash import Input, Output, State
import dash_bootstrap_components as dbc

from .. import CategoryGraph, standardize
from . import utils, components as comp

with open("data/wikicat/category_graph_20181220.json", "r") as f:
    graph_json = json.load(f)

# Load category graph and insert artificial root node
ROOT_ID = "((ROOT))"
cg = CategoryGraph(graph_json)
cg = utils.insert_artificial_root_node(cg, ROOT_ID)
root = cg.page_from_id(ROOT_ID)
root_node = {
    "data": {"id": ROOT_ID, "label": root.title},
    "classes": root.namespace + " root",
}

# Define app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="Wikipedia Categories Explorer",
)
server = app.server

# Build components
cyto_graph = comp.build_cytoscape_graph(root_node)
store_selected_nodes = comp.build_store_selected_nodes(ROOT_ID)
dd_choose_tlc = comp.build_dd_choose_tlc(cg)
panel = comp.build_panel(dd_choose_tlc)

# Build layout
app.layout = comp.build_layout(cyto_graph, panel, comp.cards, store_selected_nodes)

# Define callbacks
@app.callback(
    Output(comp.inp_choose_article, "valid"),
    Output(comp.inp_choose_article, "invalid"),
    Output(comp.btn_show_path, "disabled"),
    Input(comp.inp_choose_article, "value"),
)
def validate_inp_choose_article(text):
    if text is None or text == "":
        return False, True, True

    text = standardize(text)

    if text in cg.title_to_id["article"]:
        return True, False, False
    else:
        return False, True, True


@app.callback(
    Output(comp.md_clicked_node, "children"), Input(cyto_graph, "tapNodeData")
)
def update_clicked_node(node_data):
    if node_data is None:
        return "No node selected"

    page = cg.page_from_id(node_data["id"])

    articles = [c for c in cg.get_children(page) if c.is_article()]

    article_list = [f"- [{a.title.replace('_', ' ')}]({a.get_url()})" for a in articles]
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
    Output(comp.cl_children_to_display, "options"),
    Output(comp.cl_children_to_display, "value"),
    Output(comp.cl_parents_to_display, "options"),
    Output(comp.cl_parents_to_display, "value"),
    Input(comp.sw_children, "value"),
    Input(comp.sw_parents, "value"),
    Input(comp.btn_reset_graph, "n_clicks"),
    Input(cyto_graph, "tapNodeData"),
    State(store_selected_nodes, "data"),
)
def update_checklist(
    child_checked, parent_checked, n_clicks, clicked_data, stored_data
):
    if clicked_data is None:
        raise dash.exceptions.PreventUpdate

    if utils.was_triggered(comp.btn_reset_graph, "n_clicks"):
        return [], [], [], []

    if utils.was_triggered(comp.sw_children, "value"):
        if child_checked:
            res = cg.get_children(id=clicked_data["id"], return_as="id")
        else:
            res = []

        return dash.no_update, res, dash.no_update, dash.no_update

    if utils.was_triggered(comp.sw_parents, "value"):
        if parent_checked:
            res = cg.get_parents(id=clicked_data["id"], return_as="id")
        else:
            res = []

        return dash.no_update, dash.no_update, dash.no_update, res

    stored_data = set(stored_data)
    children = [c for c in cg.get_children(id=clicked_data["id"]) if c.is_category()]
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
    Output(store_selected_nodes, "data"),
    Input(comp.btn_update_graph, "n_clicks"),
    Input(comp.btn_reset_graph, "n_clicks"),
    Input(comp.btn_show_path, "n_clicks"),
    State(comp.cl_children_to_display, "value"),
    State(comp.cl_children_to_display, "options"),
    State(comp.cl_parents_to_display, "value"),
    State(comp.cl_parents_to_display, "options"),
    State(comp.inp_choose_article, "value"),
    State(dd_choose_tlc, "value"),
    State(store_selected_nodes, "data"),
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
    if utils.was_triggered(comp.btn_reset_graph, "n_clicks"):
        return [ROOT_ID]

    if utils.was_triggered(comp.btn_show_path, "n_clicks"):
        if chosen_article_name is None:
            return dash.no_update

        article = cg.page_from_title(chosen_article_name, namespace="article")
        target = cg.page_from_id(chosen_tlc_id)

        backlinks = utils.bfs_with_backlinks(cg, article, target)
        chain = utils.extract_chain(backlinks, article, target)

        return [ROOT_ID] + chain

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
    Input(store_selected_nodes, "data"),
)
def update_graph(selected_nodes):
    if selected_nodes is None:
        return dash.no_update

    selected_nodes = set(selected_nodes)

    nodes = []
    edges = []

    for id in selected_nodes:
        page = cg.page_from_id(id)
        node = {
            "data": {"id": id, "label": page.title.replace("_", " ")},
            "classes": page.namespace,
        }

        if node["data"]["id"] == ROOT_ID:
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


if __name__ == "__main__":
    app.run_server(debug=True, port=8000, host="0.0.0.0")
