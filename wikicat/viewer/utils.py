from collections import deque

import dash
from .. import CategoryGraph, Page
from ..constants import ARTICLE, CATEGORY


def bfs_with_backlinks(cg: CategoryGraph, article: Page, target: Page):
    queue = deque([article])
    backlinks = {}

    while queue:
        page = queue.popleft()
        if page == target:
            return backlinks

        for parent in cg.get_parents(page):
            if parent.id not in backlinks:
                backlinks[parent.id] = page.id
                queue.append(parent)
    return None


def extract_chain(backlinks: dict, article: Page, target: Page):
    if backlinks is None:
        return []

    chain = []
    node = target.id

    while node != article.id:
        chain.append(node)
        node = backlinks[node]

    return chain


def was_triggered(component, prop):
    ctx = dash.callback_context
    if not ctx.triggered:
        return False

    triggered_id, triggered_prop = ctx.triggered[0]["prop_id"].split(".", 1)
    return component.id == triggered_id and prop == triggered_prop


def insert_artificial_root_node(cg: CategoryGraph, root_id: str):
    """
    Workaround to get the graph to have a "root" node that links to all top-level categories.
    """
    cg.id_to_title[root_id] = root_id
    cg.id_to_namespace[root_id] = "category"
    cg.title_to_id[CATEGORY][root_id] = root_id
    cg.parents_to_children[root_id] = " ".join(cg.get_top_level_categories(return_as="id"))
    cg.children_to_parents[root_id] = ""

    return cg
