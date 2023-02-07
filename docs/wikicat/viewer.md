# Reference for `wikicat.viewer`

## `assign_callbacks`

```python
wikicat.viewer.assign_callbacks(app, cg, cyto_graph, inp, btn, cl, sw, md, sto, dd, root)
```

#### Description

Assign callbacks to the app. This function is called by `wikicat.viewer.app.create_app`.
It is separated from `create_app` to ensure modularity. It takes in all the components
(cyto_graph, inp, btn, cl, sw, md, sto, dd, root) as arguments in order to access their
`id` attributes. It also takes in the `cg` argument to access the `CategoryGraph` object
and the `root` argument to access the root node id.

## `build_app`

```python
wikicat.viewer.build_app(cg, title="Wikipedia Categories Explorer", style=None)
```

#### Description

Builds the Dash app. The app is a Dash app with a Cytoscape graph, a panel with
buttons, inputs, dropdowns, checklists and markdowns, and a store for the selected
nodes. The app is built using the components defined in the components module.
It can be started by using the `wikicat.viewer.run()` function. By default,
it will use the bootstrap style.

## `run`

```python
wikicat.viewer.run(load_dir, load_name, port=8050, host="0.0.0.0", debug=True, app=None)
```

#### Description

Runs the app. If `app` is None, a new app is built. Otherwise, the given app is
used. The app is built using the `wikicat.viewer.build_app()` function.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `load_dir` | `str` |  | Directory where the category graph is stored. If you used `wikicat.processing`, then the directory should be `~/.wikicat_data/enwiki_2018_12_20`. |
| `load_name` | `str` |  | Name of the category graph file. If you used `wikicat.processing`, then the file is called `category_graph.json`. |
| `port` | `int` | `8050` | Port to run the app on, by default 8050 following the Dash convention. |
| `host` | `str` | `"0.0.0.0"` | Host to run the app on, by default "0.0.0.0" to make it accessible from other devices on the network. |
| `debug` | `bool` | `True` | Whether to run the app in debug mode, by default True |


#### Example

>>> import wikicat.viewer as viewer
>>> app = viewer.build_app()
>>> viewer.run(
...     load_dir="~/.wikicat_data/enwiki_2018_12_20", load_name="category_graph.json", app=app
... )

# Reference for `wikicat.viewer.__main__`

## `build_parser`

```python
wikicat.viewer.__main__.build_parser()
```

#### Description

Builds the argument parser for the `wikicat.viewer` module. The parser is used
to parse the command line arguments when running the `wikicat.viewer` module.

To learn how to use `wikicat.viewer`, run:
```
python -m wikicat.viewer --help
```


#### Returns

```
argparse.ArgumentParser
```

The argument parser for the `wikicat.viewer` module.

## `main`

```python
wikicat.viewer.__main__.main(base_dir, year, month, day, port, host, debug)
```

# Reference for `wikicat.viewer.components`

## `inline_div`

```python
wikicat.viewer.components.inline_div(children)
```

#### Description

Create a div with inline-block display style.

## `generate_cytoscape_stylesheet`

```python
wikicat.viewer.components.generate_cytoscape_stylesheet(root_color="red", article_color="#9097C0", category_color="#503B31", selected_node_border_color="blue", edge_color="#705d56")
```

#### Description

Generate a stylesheet for the Cytoscape graph. The stylesheet is a list of
dictionaries, each of which contains a selector and a style. The selector
is a CSS-style string that specifies which elements the style should be applied to.
The style is a dictionary that specifies the CSS style to be applied to the elements.

The parameters are the colors to be used for the different elements. If you want to
have more control over the style, you can use the
[Cytoscape documentation](https://dash.plotly.com/cytoscape/styling) to create your own.

## `build_cytoscape_graph`

```python
wikicat.viewer.components.build_cytoscape_graph(root, id="cytoscape-graph", stylesheet=None)
```

#### Description

Build a Cytoscape graph from a root node. If no stylesheet is provided, a default one is generated.

## `build_dropdowns`

```python
wikicat.viewer.components.build_dropdowns(cg, id="dd-choose-tlc")
```

#### Description

Build a dropdown to choose a top-level category.

## `build_panel`

```python
wikicat.viewer.components.build_panel(btn, inp, md, dd)
```

#### Description

Build the panel with the controls.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `btn` | `Buttons` |  | Buttons to update the graph, show the path, and reset the graph. |
| `inp` | `Inputs` |  | Inputs to choose an article. |
| `md` | `Markdowns` |  | Markdowns to display the clicked node. |
| `dd` | `Dropdowns` |  | Dropdowns to choose a top-level category. |


## `build_stores`

```python
wikicat.viewer.components.build_stores(root_id, id="store-selected-nodes")
```

#### Description

Build a Dash `dcc.Store` to keep track of the selected nodes.

## `build_checklists`

```python
wikicat.viewer.components.build_checklists(id_children_to_display="cl-children-to-display", id_parents_to_display="cl-parents-to-display")
```

#### Description

Build checklists to display the children and parents of a node.

## `build_buttons`

```python
wikicat.viewer.components.build_buttons(id_update_graph="btn-update-graph", id_reset_graph="btn-reset-graph", id_show_path="btn-show-path")
```

#### Description

Build buttons to update the graph, show the path, and reset the graph.

## `build_cards`

```python
wikicat.viewer.components.build_cards(cl, sw)
```

#### Description

Build cards to display the children and parents of a node.

## `build_switches`

```python
wikicat.viewer.components.build_switches(id_parents="switch-parents", id_children="switch-children")
```

#### Description

Build switches that can select all/none of the children and parents of a node to be displayed.

## `build_markdowns`

```python
wikicat.viewer.components.build_markdowns()
```

#### Description

Build a dash `dcc.Markdown` component to display information about the clicked node.

## `build_inputs`

```python
wikicat.viewer.components.build_inputs()
```

#### Description

Build an input to choose an article name (which will be green if the article exists)

## `build_layout`

```python
wikicat.viewer.components.build_layout(cyto_graph, panel, cards_column, sto)
```

#### Description

Build the layout of the app. The layout is a `dbc.Container` with a `dbc.Row` with three columns:
- the first column contains the graph
- the second column contains the panel with the controls
- the third column contains the cards with the children and parents of a node


#### Examples

```python
>>> import dash
>>> ...
>>> app = dash.Dash(__name__)
>>> ...
>>> app.layout = build_layout(cyto_graph, panel, cards_column, sto)
>>> ...
>>> app.run_server(debug=True)
```



## `build_card_column`

```python
wikicat.viewer.components.build_card_column(cards)
```

#### Description

Build a column with the cards to display the children and parents of a node.

# Reference for `wikicat.viewer.utils`

## `bfs_with_backlinks`

```python
wikicat.viewer.utils.bfs_with_backlinks(cg, article, target)
```

#### Description

Breadth-first search with backlinks. Returns a dictionary of {child: parent} pairs,
linking the target category to the article. It does not necessarily return the shortest path.
This function is meant to be used with the `extract_chain` function.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `cg` | `CategoryGraph` |  | A `wikicat.CategoryGraph` object. |
| `article` | `Page` |  | The article to start the search from. It is a wikicat.Page object |
| `target` | `Page` |  | The target category page to search for. It is a wikicat.Page object |


#### Returns

```
dict
```

A dictionary of {child: parent} pairs, linking the target category to the article.

## `extract_chain`

```python
wikicat.viewer.utils.extract_chain(backlinks, article, target)
```

#### Description

Extracts the chain of categories from the backlinks dictionary returned by `bfs_with_backlinks`.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `backlinks` | `dict` |  | The backlinks dictionary returned by `bfs_with_backlinks`. |
| `article` | `Page` |  | The article to start the search from. It is a wikicat.Page object |
| `target` | `Page` |  | The target category page to search for. It is a wikicat.Page object |


#### Returns

```
list
```

A list of category ids from the article to the target category.

## `was_triggered`

```python
wikicat.viewer.utils.was_triggered(component, prop)
```

#### Description

Returns True if the component's prop was triggered by the user. This is useful for
determining if a component's value was changed by the user or by the app when a Dash
callback has multiple inputs and you want to know which one triggered the callback.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `component` |  |  | The Dash component to check. For example, `html.Button`. |
| `prop` | `str` |  | The prop to check. For example, "value" or "n_clicks". |


## `insert_artificial_root_node`

```python
wikicat.viewer.utils.insert_artificial_root_node(cg, root_id)
```

#### Description

Workaround to get the graph to have a "root" node that links to all top-level categories.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `cg` | `CategoryGraph` |  | A `wikicat.CategoryGraph` object. This object will be modified in-place. |
| `root_id` | `str` |  | The id of the root node. This id should not be used by any other category. |


#### Returns

```
cg
```

The modified `wikicat.CategoryGraph` object (same object as the input).

