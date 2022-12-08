import argparse
from collections import deque
import json
from textwrap import dedent
from typing import NamedTuple

import dash
from dash import dcc, html, Input, Output, State
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc


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
    return html.Div(children, style={"display": "inline-block"}, **kwargs)


def build_cytoscape_graph(root_node, id="cytoscape-graph") -> cyto.Cytoscape:
    default_stylesheet = [
        {
            "selector": ".root",
            "style": {
                "background-color": "#020202",
            },
        },
        {
            "selector": ".category",
            "style": {
                "background-color": "#503B31",
            },
        },
        {
            "selector": ".article",
            "style": {"background-color": "#9097C0", "shape": "square"},
        },
        {
            "selector": "node",
            "style": {"label": "data(label)", "text-wrap": "wrap"},
        },
        {
            "selector": "edge",
            "style": {
                "mid-target-arrow-color": "#705d56",
                "line-color": "#705d56",
                "mid-target-arrow-shape": "triangle",
                "arrow-scale": 1.5,
            },
        },
        {
            "selector": "node:selected",
            "style": {
                "border-width": 3,
                "border-color": "blue",
            },
        },
        {
            "selector": ".root",
            "style": {
                "background-color": "red",
                "shape": "star",
            },
        },
    ]

    cyto_graph = cyto.Cytoscape(
        id=id,
        elements=[root_node],
        style={"height": "calc(98vh - 30px)", "width": "100%"},
        layout={
            "name": "breadthfirst",
            "directed": True,
            "roots": [root_node["data"]["id"]],
        },
        stylesheet=default_stylesheet,
    )

    return cyto_graph


def build_dropdowns(cg, id="dd-choose-tlc") -> Dropdowns:
    return Dropdowns(
        choose_tlc=dbc.Select(
            id=id,
            options=[
                {"label": p.title.replace("_", " "), "value": p.id}
                for p in cg.get_top_level_categories()
            ],
        )
    )


def build_panel(btn: Buttons, inp: Inputs, md: Markdowns, dd_choose_tlc) -> html.Div:
    panel = html.Div(
        [
            dbc.Row(
                dbc.ButtonGroup([btn.update_graph, btn.show_path, btn.reset_graph]),
            ),
            dd_choose_tlc,
            inp.choose_article,
            md.clicked_node,
        ]
    )

    return panel


def build_stores(root_id, id="store-selected-nodes") -> Stores:
    return Stores(selected_nodes=dcc.Store(id=id, data=[root_id]))


def build_checklists(
    id_children_to_display="cl-children-to-display",
    id_parents_to_display="cl-parents-to-display",
) -> Checklists:
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
    switch_style = {"margin-left": "15px", "display": "inline-block"}
    return Switches(
        children=dbc.Switch(id=id_children, value=False, style=switch_style),
        parents=dbc.Switch(id=id_parents, value=False, style=switch_style),
    )


def build_markdowns() -> Markdowns:
    return Markdowns(
        clicked_node=dcc.Markdown(
            id="md-clicked-node",
            link_target="_blank",
            style={"max-height": "calc(98vh - 200px)", "overflow-y": "scroll"},
        ),
    )


def build_inputs() -> Inputs:
    return Inputs(
        choose_article=dbc.Input(
            id="inp-choose-article", placeholder="Write name of article..."
        )
    )


def build_layout(cyto_graph, panel, cards_column, sto: Stores) -> dbc.Container:
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
    return html.Div(
        [cards.children_to_display, html.Br(), cards.parents_to_display],
    )
