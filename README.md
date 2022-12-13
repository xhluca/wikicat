# `wikicat`: A Python toolkit for managing and navigating graphs of Wikipedia categories

| ![API Sample](assets/api.png) | ![CLI Sample](assets/cli.png) |
|:---:|:---:|
| Simple Python API for exploring graph offline | Useful CLI for processing and launching app |
| ![Interactive network](assets/interactive_network.jpg) | ![panels in the user interface](assets/ui.jpg) |
| Interactive visualization of categories | UI to display information and filter nodes |


## Main API

> **Note** The reference docs can be found in [docs/wikicat.md](docs/wikicat.md)

The main `wikicat` API allows you work with category graphs generated from a certain dump by Wikipedia. Once the dump is processed via `wikicat.processing`, you can easily navigate the graph using simple and clear Python code, all offline (i.e., you do not need to make web requests to Wikipedia, and you can choose dump going back to any date you prefer). The API is designed to be as simple as possible, and is intended to be used by researchers and developers who want to work with the Wikipedia category graph.

To install the API, run:

```
pip3 install wikicat
```

`wikicat` contains two classes to work with the Wikipedia category graph: `CategoryGraph` and `Page`. The `CategoryGraph` class is used to load the graph from a file, and to navigate the graph. The `Page` class is used to represent a Wikipedia page, and to retrieve information about the page from Wikipedia. They are meant to be used together, as shown in the following example:

```python
import wikicat as wc

# Load the graph
cg = wc.CategoryGraph.read_json(
    '/path/to/category_graph_<yyyy>_<mm>_<dd>.json'
)

# Get the page for "Montreal"
page = cg.get_page_from_title('Montreal', 'article')

# Get the categories for "Montreal"
cats = cg.get_parents(page=page)
print(f"Category tags of {page.title}: {cats}")

# Get URL of "Montreal"
print("URL:", page.get_url())
```

By default, the path will be `~/.wikicat_data/`, but the JSON can be stored anywhere you want (see `wikicat.processing` below for more information).

You can find the full documentation in the [our repository wiki](https://github.com/xhluca/wikicat/wiki).


## `wikicat.processing`

*`wikicat.processing` is a command line interface (CLI) for downloading and processing the data*

> **Note** The reference docs can be found in [docs/wikicat/processing.md](docs/wikicat/processing.md)

To install the processing tools, run:

```
pip3 install wikicat[processing]
```

To download a dump directly from web archive:

```bash
# Download DB dump of Wikipedia categories
python3 -m wikicat.processing.download_dump \
        --year <yyyy> \
        --month <mm> \
        --day <dd>
```

If you do not specify `--save_dir`, it will automatically be saved to `~/.wikicat_data`. Once you have downloaded a database dump, you can generate the graph with:

```bash
# Process DB dump into readable category graph
python3 -m wikicat.processing.generate_graph \
        --year <yyyy> \
        --month <mm> \
        --day <dd> \
        --save_prefix category_graph
```

The results will be saved in `~/.wikicat_data/category_graph_<yyyy>_<mm>_<dd>.json`.


## `wikicat.viewer`

*`wikicat.viewer` is an application that lets you visually explore a category graph*

> **Note** The reference docs can be found in [docs/wikicat/viewer.md](docs/wikicat/viewer.md)

To install the viewer, run:

```bash
pip3 install wikicat[viewer]
```

To run the viewer, run:

```bash
python3 -m wikicat.viewer \
        --load_name category_graph_<yyyy>_<mm>_<dd>.json \
        --port 8050
```

Then, open your browser to `http://0.0.0.0:8050`.

### Usage

The viewer let you interact with the nodes. You can zoom in and out, move and click the nodes in the graph.
- When you click on a node, you will see various information (including a list of children articles) appear on the middle panel. 
- On the right panel, you will see various checklists of children and parents of the selected node. When you click on "Update", the checked parents and children will be added to the graph.
- There's a dropdown and a validated input. For the input, a green check will appear if a valid article title is input, otherwise it remains red. The dropdown lets you choose one of [28 top-level categories](https://en.wikipedia.org/wiki/Wikipedia:Contents/Categories). The input let you type the name of an article (not category). When the title is valid, you can click on the "Compute Path" button, which will *try* to find a valid path between the top-level category and the article you chose.
- Click on the "Reset" button to go back to the original view.

### Accessing components

`wikicat.viewer` was built using [Dash](https://dash.plotly.com/), a Python framework for building web applications. The application is composed of several components, which can be accessed inside `wikicat.viewer.components`. For example, to access the `Network` component, you can run:

```python
import wikicat.viewer.components as comp

# Build the network
cytoscape_graph = comp.build_cytoscape_graph(...)

# Build the right panel
panel = comp.build_panel(...)
```

Those can be reused in your custom Dash application. You can also create your own component and add it to the viewer. For example:

```python
import wikicat.viewer as wcv

# ...

# Define app
app = dash.Dash(__name__, external_stylesheets=[style], title=title, **kwargs)

# Define your custom components
def build_btn(...):
    # ...

# Build regular components
cyto_graph = wcv.components.build_cytoscape_graph(root)
# ...
cards = wcv.components.build_cards(cl=cl, sw=sw)
cards_column = wcv.components.build_card_column(cards)

# Build layout
app.layout = wcv.components.build_layout(...)

# Assign callbacks to make app interactive
wcv.components.assign_callbacks(app=app, ...)

# Run app
run(app=app, ...)
```

See the `wikicat.viewer.build_app()` function for more details.

## Warning

Because of the size of the graph, some parts of the API (such as the viewer and the processing CLI) require a lot of memory. We recommend using a machine with at least 32 GB of RAM. We are working on a more memory-efficient version of the API.
