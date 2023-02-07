import argparse
from pathlib import Path

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

    parser.add_argument("--base_dir", type=str, default="~/.wikicat_data")
    parser.add_argument("--year", "-y", type=int, required=True, help="Year of dump")
    parser.add_argument("--month", "-m", type=int, required=True, help="Month of dump")
    parser.add_argument("--day", "-d", type=int, required=True, help="Day of dump")
    parser.add_argument("--port", type=int, default=8050)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--debug", type=bool, default=True)

    return parser


def main(base_dir, year, month, day, port, host, debug):
    load_dir = Path(base_dir).expanduser() / f"enwiki_{year}_{month:02d}_{day:02d}"
    load_name = "category_graph.json"
    run(load_dir, load_name, port, host, debug)


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    run(**vars(args))
