# Documentations

The documentation loosely follows the pandas documentation style. This allows it to be readable but also easy to parse. 

## Rendering

The docs are rendered into markdown via a custom `scripts/docs/build.py`. To build the documentation, run:

```bash
python scripts/docs/build.py
```

This will automatically generate the documentation from the docstrings in the code. The documentation is then rendered into markdown and placed in the `docs/` folder.

## Configuring the paths

Each new python module is routed to a markdown file manually. This is done in the `scripts/docs/render_paths.json` file. The format is:

```json
{
    "docs/path/to/file.md": [
        "wikicat/path/to/module.py",
        "wikicat/path/to/other_module.py",
        ...
    ],
    ...
}
```

For example, if you want `wikicat/__init__.py` to be rendered into `docs/wikicat.md`, you would add the following to the `render_paths.json` file:

```json
{
    "docs/wikicat.md": [
        "wikicat/__init__.py"
    ]
}
```

You can also use `glob` patterns to match multiple files. For example, if you want to render all the files in the `wikicat/processing` folder, you would add the following to the `render_paths.json` file:

```json
{
    "docs/wikicat/processing.md": [
        "wikicat/processing/*.py"
    ]
}
```