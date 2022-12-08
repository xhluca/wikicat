# `wikicat`: A Python toolkit for managing and navigating graphs of Wikipedia categories

## Processing

The `wikicat.processing` module contains tools for processing the Wikipedia category graph.

To install the processing tools, run:

```
pip3 install wikicat[processing]
```

To generate the graph, run:

```
python -m wikicat.processing.generate_graph
```


## Viewer

The `wikicat.viewer`  is an application that allows you to visually explore the Wikipedia category graph.

To install the viewer, run:

```
pip3 install wikicat[viewer]
```

To run the viewer, run:

```
python3 -m wikicat.viewer --port 8050 --host 0.0.0.0
```

Then, open your browser to `http://0.0.0.0:8050`.

