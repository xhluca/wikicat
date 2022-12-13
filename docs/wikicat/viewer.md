# Reference for module `wikicat.viewer`

## `wikicat.viewer.assign_callbacks`

```python
wikicat.viewer.assign_callbacks(app, cg, cyto_graph, inp, btn, cl, sw, md, sto, dd, root)
```

## `wikicat.viewer.build_app`

```python
wikicat.viewer.build_app(cg, title="Wikipedia Categories Explorer", style)
```

## `wikicat.viewer.run`

```python
wikicat.viewer.run(load_dir, load_name, port=8050, host="0.0.0.0", debug=True, app)
```

# Reference for module `wikicat.viewer.__main__`

## `wikicat.viewer.__main__.build_parser`

```python
wikicat.viewer.__main__.build_parser()
```

# Reference for module `wikicat.viewer.components`

## `wikicat.viewer.components.inline_div`

```python
wikicat.viewer.components.inline_div(children)
```

## `wikicat.viewer.components.build_cytoscape_graph`

```python
wikicat.viewer.components.build_cytoscape_graph(root, id="cytoscape-graph")
```

## `wikicat.viewer.components.build_dropdowns`

```python
wikicat.viewer.components.build_dropdowns(cg, id="dd-choose-tlc")
```

## `wikicat.viewer.components.build_panel`

```python
wikicat.viewer.components.build_panel(btn, inp, md, dd_choose_tlc)
```

## `wikicat.viewer.components.build_stores`

```python
wikicat.viewer.components.build_stores(root_id, id="store-selected-nodes")
```

## `wikicat.viewer.components.build_checklists`

```python
wikicat.viewer.components.build_checklists(id_children_to_display="cl-children-to-display", id_parents_to_display="cl-parents-to-display")
```

## `wikicat.viewer.components.build_buttons`

```python
wikicat.viewer.components.build_buttons(id_update_graph="btn-update-graph", id_reset_graph="btn-reset-graph", id_show_path="btn-show-path")
```

## `wikicat.viewer.components.build_cards`

```python
wikicat.viewer.components.build_cards(cl, sw)
```

## `wikicat.viewer.components.build_switches`

```python
wikicat.viewer.components.build_switches(id_parents="switch-parents", id_children="switch-children")
```

## `wikicat.viewer.components.build_markdowns`

```python
wikicat.viewer.components.build_markdowns()
```

## `wikicat.viewer.components.build_inputs`

```python
wikicat.viewer.components.build_inputs()
```

## `wikicat.viewer.components.build_layout`

```python
wikicat.viewer.components.build_layout(cyto_graph, panel, cards_column, sto)
```

## `wikicat.viewer.components.build_card_column`

```python
wikicat.viewer.components.build_card_column(cards)
```

# Reference for module `wikicat.viewer.utils`

## `wikicat.viewer.utils.bfs_with_backlinks`

```python
wikicat.viewer.utils.bfs_with_backlinks(cg, article, target)
```

## `wikicat.viewer.utils.extract_chain`

```python
wikicat.viewer.utils.extract_chain(backlinks, article, target)
```

## `wikicat.viewer.utils.was_triggered`

```python
wikicat.viewer.utils.was_triggered(component, prop)
```

## `wikicat.viewer.utils.insert_artificial_root_node`

```python
wikicat.viewer.utils.insert_artificial_root_node(cg, root_id)
```

#### Description

Workaround to get the graph to have a "root" node that links to all top-level categories.

