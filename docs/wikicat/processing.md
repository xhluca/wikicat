# Reference for module `wikicat.processing`

## `wikicat.processing.generate_graph`

```python
wikicat.processing.generate_graph(df)
```

#### Description

Generate the graph JSON file from the raw CSV file.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `df` | `pandas.DataFrame` |  | The raw CSV file. It has the following columns: - page_id: the curid used by Wikipedia - page_title: the standardized title used by Wikipedia - cl_to: the standardized title of the parent category - cl_type: the type of the parent category, either "category" or "article" |


#### Returns

```
dict
```

The graph JSON file. It has the following structure:
{
    "id_to_title": { <id>: <title>, ... },
    "id_to_namespace": { <id>: <type>, ... },
    "title_to_id": {
        "category": { <title>: <id>, ... },
        "article": { <title>: <id>, ... },
    },
    "children_to_parents": { <id>: [<id>, ...], ... },
    "parents_to_children": { <id>: [<id>, ...], ... },
}

#### Notes

- <id> is a string (the curid used by Wikipedia)
- <title> is a string (the standardized title used by Wikipedia)
- <type> is an int, either 0 (article) or 14 (category)

## `wikicat.processing.main`

```python
wikicat.processing.main(load_dir, save_dir, load_name, save_name)
```

## `wikicat.processing.parse_args`

```python
wikicat.processing.parse_args()
```

# Reference for module `wikicat.processing`

