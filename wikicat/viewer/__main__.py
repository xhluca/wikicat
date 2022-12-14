import argparse

from . import run



def build_parser():
    """
    Builds the argument parser for the `wikicat.viewer` module. The parser is used
    to parse the command line arguments when running the `wikicat.viewer` module.

    To learn how to use `wikicat.viewer`, run:
    ```
    python -m wikicat.viewer --help
    ```

    Returns
    -------
    argparse.ArgumentParser
        The argument parser for the `wikicat.viewer` module.
    
    """
    parser = argparse.ArgumentParser(
        description="""
        Run a Dash app to explore a category graph.

        The category graph is loaded from a JSON file.

        The app is accessible at http://<host>:<port>
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--load_dir", type=str, default="~/.wikicat_data")
    parser.add_argument("--load_name", type=str, default="category_graph_20181220.json")
    parser.add_argument("--port", type=int, default=8050)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--debug", type=bool, default=True)

    return parser

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    run(**vars(args))
