# Module `wikicat.viewer`

## `wikicat.viewer.build_parser`

```python
wikicat.viewer.build_parser()
```

# Module `wikicat.viewer`

## `wikicat.viewer.bfs_with_backlinks`

```python
wikicat.viewer.bfs_with_backlinks(cg, article, target)
```

## `wikicat.viewer.extract_chain`

```python
wikicat.viewer.extract_chain(backlinks, article, target)
```

## `wikicat.viewer.was_triggered`

```python
wikicat.viewer.was_triggered(component, prop)
```

## `wikicat.viewer.insert_artificial_root_node`

```python
wikicat.viewer.insert_artificial_root_node(cg, root_id)
```

#### Description

Workaround to get the graph to have a "root" node that links to all top-level categories.

# Module `wikicat.viewer`

## `wikicat.viewer.inline_div`

```python
wikicat.viewer.inline_div(children)
```

## `wikicat.viewer.build_cytoscape_graph`

```python
wikicat.viewer.build_cytoscape_graph(root, id="cytoscape-graph")
```

## `wikicat.viewer.build_dropdowns`

```python
wikicat.viewer.build_dropdowns(cg, id="dd-choose-tlc")
```

## `wikicat.viewer.build_panel`

```python
wikicat.viewer.build_panel(btn, inp, md, dd_choose_tlc)
```

## `wikicat.viewer.build_stores`

```python
wikicat.viewer.build_stores(root_id, id="store-selected-nodes")
```

## `wikicat.viewer.build_checklists`

```python
wikicat.viewer.build_checklists(id_children_to_display="cl-children-to-display", id_parents_to_display="cl-parents-to-display")
```

## `wikicat.viewer.build_buttons`

```python
wikicat.viewer.build_buttons(id_update_graph="btn-update-graph", id_reset_graph="btn-reset-graph", id_show_path="btn-show-path")
```

## `wikicat.viewer.build_cards`

```python
wikicat.viewer.build_cards(cl, sw)
```

## `wikicat.viewer.build_switches`

```python
wikicat.viewer.build_switches(id_parents="switch-parents", id_children="switch-children")
```

## `wikicat.viewer.build_markdowns`

```python
wikicat.viewer.build_markdowns()
```

## `wikicat.viewer.build_inputs`

```python
wikicat.viewer.build_inputs()
```

## `wikicat.viewer.build_layout`

```python
wikicat.viewer.build_layout(cyto_graph, panel, cards_column, sto)
```

## `wikicat.viewer.build_card_column`

```python
wikicat.viewer.build_card_column(cards)
```

# Module `wikicat.viewer`

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

