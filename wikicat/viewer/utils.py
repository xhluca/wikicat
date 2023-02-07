from collections import deque

import dash
from .. import CategoryGraph, Page
from ..constants import ARTICLE, CATEGORY


def bfs_with_backlinks(cg: CategoryGraph, article: Page, target: Page):
    """
    Breadth-first search with backlinks. Returns a dictionary of {child: parent} pairs,
    linking the target category to the article. It does not necessarily return the shortest path.
    This function is meant to be used with the `extract_chain` function.

    Parameters
    ----------
    cg
        A `wikicat.CategoryGraph` object.
    article
        The article to start the search from. It is a wikicat.Page object
    target
        The target category page to search for. It is a wikicat.Page object

    Returns
    -------
    dict
        A dictionary of {child: parent} pairs, linking the target category to the article.
    """
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


def extract_chain(backlinks: dict, article: Page, target: Page) -> list:
    """
    Extracts the chain of categories from the backlinks dictionary returned by `bfs_with_backlinks`.

    Parameters
    ----------
    backlinks
        The backlinks dictionary returned by `bfs_with_backlinks`.
    article
        The article to start the search from. It is a wikicat.Page object
    target
        The target category page to search for. It is a wikicat.Page object

    Returns
    -------
    list
        A list of category ids from the article to the target category.
    """
    if backlinks is None:
        return []

    chain = []
    node = target.id

    while node != article.id:
        chain.append(node)
        node = backlinks[node]

    return chain


def was_triggered(component, prop: str):
    """
    Returns True if the component's prop was triggered by the user. This is useful for
    determining if a component's value was changed by the user or by the app when a Dash
    callback has multiple inputs and you want to know which one triggered the callback.

    Parameters
    ----------
    component
        The Dash component to check. For example, `html.Button`.
    prop
        The prop to check. For example, "value" or "n_clicks".
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        return False

    triggered_id, triggered_prop = ctx.triggered[0]["prop_id"].split(".", 1)
    return component.id == triggered_id and prop == triggered_prop


def insert_artificial_root_node(cg: CategoryGraph, root_id: str):
    """
    Workaround to get the graph to have a "root" node that links to all top-level categories.

    Parameters
    ----------
    cg
        A `wikicat.CategoryGraph` object. This object will be modified in-place.

    root_id
        The id of the root node. This id should not be used by any other category.

    Returns
    -------
    cg
        The modified `wikicat.CategoryGraph` object (same object as the input).
    """
    cg.id_to_title[root_id] = root_id
    cg.id_to_namespace[root_id] = "category"
    cg.title_to_id[CATEGORY][root_id] = root_id
    cg.parents_to_children[root_id] = " ".join(
        cg.get_top_level_categories(return_as="id")
    )
    cg.children_to_parents[root_id] = ""

    return cg
