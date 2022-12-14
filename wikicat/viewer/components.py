from typing import NamedTuple

from dash import dcc, html
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc

from .. import CategoryGraph, Page


class Checklists(NamedTuple):
    children_to_display: dbc.Checklist
    parents_to_display: dbc.Checklist


class Buttons(NamedTuple):
    update_graph: dbc.Button
    show_path: dbc.Button
    reset_graph: dbc.Button


class Cards(NamedTuple):
    children_to_display: dbc.Card
    parents_to_display: dbc.Card


class Switches(NamedTuple):
    children: dbc.Switch
    parents: dbc.Switch


class Inputs(NamedTuple):
    choose_article: dbc.Input


class Markdowns(NamedTuple):
    clicked_node: dcc.Markdown


class Stores(NamedTuple):
    selected_nodes: dcc.Store


class Dropdowns(NamedTuple):
    choose_tlc: dcc.Dropdown


def inline_div(children, **kwargs) -> html.Div:
    """
    Create a div with inline-block display style.
    """
    return html.Div(children, style={"display": "inline-block"}, **kwargs)


def generate_cytoscape_stylesheet(
    root_color="red",
    article_color="#9097C0",
    category_color="#503B31",
    selected_node_border_color="blue",
    edge_color="#705d56",
) -> list:
    """
    Generate a stylesheet for the Cytoscape graph. The stylesheet is a list of
    dictionaries, each of which contains a selector and a style. The selector
    is a CSS-style string that specifies which elements the style should be applied to.
    The style is a dictionary that specifies the CSS style to be applied to the elements.

    The parameters are the colors to be used for the different elements. If you want to
    have more control over the style, you can use the
    [Cytoscape documentation](https://dash.plotly.com/cytoscape/styling) to create your own.
    """
    return [
        {
            "selector": ".category",
            "style": {
                "background-color": category_color,
            },
        },
        {
            "selector": ".article",
            "style": {"background-color": article_color, "shape": "square"},
        },
        {
            "selector": "node",
            "style": {"label": "data(label)", "text-wrap": "wrap"},
        },
        {
            "selector": "edge",
            "style": {
                "mid-target-arrow-color": edge_color,
                "line-color": edge_color,
                "mid-target-arrow-shape": "triangle",
                "arrow-scale": 1.5,
            },
        },
        {
            "selector": "node:selected",
            "style": {
                "border-width": 3,
                "border-color": selected_node_border_color,
            },
        },
        {
            "selector": ".root",
            "style": {
                "background-color": root_color,
                "shape": "star",
            },
        },
    ]


def build_cytoscape_graph(
    root: Page, id="cytoscape-graph", stylesheet=None
) -> cyto.Cytoscape:
    """
    Build a Cytoscape graph from a root node. If no stylesheet is provided, a default one is generated.
    """
    root_node = {
        "data": {"id": root.id, "label": root.title},
        "classes": root.namespace + " root",
    }

    if stylesheet is None:
        stylesheet = generate_cytoscape_stylesheet()

    cyto_graph = cyto.Cytoscape(
        id=id,
        elements=[root_node],
        style={"height": "calc(98vh - 30px)", "width": "100%"},
        layout={
            "name": "breadthfirst",
            "directed": True,
            "roots": [root_node["data"]["id"]],
        },
        stylesheet=stylesheet,
    )

    return cyto_graph


def build_dropdowns(cg: CategoryGraph, id="dd-choose-tlc") -> Dropdowns:
    """
    Build a dropdown to choose a top-level category.
    """
    return Dropdowns(
        choose_tlc=dbc.Select(
            id=id,
            options=[
                {"label": p.title.replace("_", " "), "value": p.id}
                for p in cg.get_top_level_categories()
            ],
        )
    )


def build_panel(btn: Buttons, inp: Inputs, md: Markdowns, dd: Dropdowns) -> html.Div:
    """
    Build the panel with the controls.

    Parameters
    ----------
    btn : Buttons
        Buttons to update the graph, show the path, and reset the graph.
    inp : Inputs
        Inputs to choose an article.
    md : Markdowns
        Markdowns to display the clicked node.
    dd : Dropdowns
        Dropdowns to choose a top-level category.
    """
    panel = html.Div(
        [
            dbc.Row(
                dbc.ButtonGroup([btn.update_graph, btn.show_path, btn.reset_graph]),
            ),
            dd.choose_tlc,
            inp.choose_article,
            md.clicked_node,
        ]
    )

    return panel


def build_stores(root_id, id="store-selected-nodes") -> Stores:
    """
    Build a Dash `dcc.Store` to keep track of the selected nodes.
    """
    return Stores(selected_nodes=dcc.Store(id=id, data=[root_id]))


def build_checklists(
    id_children_to_display="cl-children-to-display",
    id_parents_to_display="cl-parents-to-display",
) -> Checklists:
    """
    Build checklists to display the children and parents of a node.
    """
    return Checklists(
        children_to_display=dbc.Checklist(
            id=id_children_to_display,
            options=[],
            style={"height": "calc(49vh - 100px)", "overflow-y": "scroll"},
        ),
        parents_to_display=dbc.Checklist(
            id=id_parents_to_display,
            options=[],
            style={"height": "calc(49vh - 100px)", "overflow-y": "scroll"},
        ),
    )


def build_buttons(
    id_update_graph="btn-update-graph",
    id_reset_graph="btn-reset-graph",
    id_show_path="btn-show-path",
) -> Buttons:
    """
    Build buttons to update the graph, show the path, and reset the graph.
    """
    return Buttons(
        update_graph=dbc.Button(
            id=id_update_graph,
            children="Update",
            color="success",
            className="mt-2",
        ),
        reset_graph=dbc.Button(
            id=id_reset_graph,
            children="Reset",
            color="danger",
            className="mt-2",
        ),
        show_path=dbc.Button(
            id=id_show_path,
            children="Compute Path",
            color="primary",
            className="mt-2",
            disabled=True,
        ),
    )


def build_cards(cl: Checklists, sw: Switches) -> Cards:
    """
    Build cards to display the children and parents of a node.
    """
    return Cards(
        children_to_display=dbc.Card(
            [
                dbc.CardHeader(
                    [
                        inline_div("Children to display"),
                        sw.children,
                    ]
                ),
                dbc.CardBody([cl.children_to_display]),
            ],
            style={"width": "100%"},
        ),
        parents_to_display=dbc.Card(
            [
                dbc.CardHeader(
                    [
                        inline_div("Parents to display"),
                        sw.parents,
                    ]
                ),
                dbc.CardBody([cl.parents_to_display]),
            ],
            style={"width": "100%"},
        ),
    )


def build_switches(
    id_parents="switch-parents", id_children="switch-children"
) -> Switches:
    """
    Build switches that can select all/none of the children and parents of a node to be displayed.
    """
    switch_style = {"margin-left": "15px", "display": "inline-block"}
    return Switches(
        children=dbc.Switch(id=id_children, value=False, style=switch_style),
        parents=dbc.Switch(id=id_parents, value=False, style=switch_style),
    )


def build_markdowns() -> Markdowns:
    """
    Build a dash `dcc.Markdown` component to display information about the clicked node.
    """
    return Markdowns(
        clicked_node=dcc.Markdown(
            id="md-clicked-node",
            link_target="_blank",
            style={"max-height": "calc(98vh - 200px)", "overflow-y": "scroll"},
        ),
    )


def build_inputs() -> Inputs:
    """
    Build an input to choose an article name (which will be green if the article exists)
    """
    return Inputs(
        choose_article=dbc.Input(
            id="inp-choose-article", placeholder="Write name of article..."
        )
    )


def build_layout(
    cyto_graph: cyto.Cytoscape, panel: html.Div, cards_column: html.Div, sto: Stores
) -> dbc.Container:
    """
    Build the layout of the app. The layout is a `dbc.Container` with a `dbc.Row` with three columns:
    - the first column contains the graph
    - the second column contains the panel with the controls
    - the third column contains the cards with the children and parents of a node

    Examples
    --------
    >>> import dash
    >>> ...
    >>> app = dash.Dash(__name__)
    >>> ...
    >>> app.layout = build_layout(cyto_graph, panel, cards_column, sto)
    >>> ...
    >>> app.run_server(debug=True)
    """
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(cyto_graph, width=6),
                    dbc.Col(panel, width=3),
                    dbc.Col(cards_column, width=3),
                ]
            ),
            sto.selected_nodes,
        ],
        fluid=True,
    )


def build_card_column(cards: Cards) -> html.Div:
    """
    Build a column with the cards to display the children and parents of a node.
    """
    return html.Div(
        [cards.children_to_display, html.Br(), cards.parents_to_display],
    )
