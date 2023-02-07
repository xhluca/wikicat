"""
This files takes the raw, full catgraph CSV file and converts it
to a JSON file with the following structure.

Usage example:

python -m wikicat.processing.generate_graph \
    --year 2018 \
    --month 12 \
    --day 20 \
    --base_dir /path/to/save/intermediate/files
"""
import argparse
import json
from pathlib import Path

from .. import standardize
from ..constants import ARTICLE, CATEGORY


def generate_graph(df) -> dict:
    """
    Generate the graph JSON file from the raw CSV file.

    The input CSV should have the following columns:
    - page_id: the curid used by Wikipedia
    - page_title: the standardized title used by Wikipedia
    - cl_to: the standardized title of the parent category
    - cl_type: the type of the parent category, either "category" or "article"

    The output JSON file has the following structure:
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

    Parameters
    ----------
    df : pandas.DataFrame
        The raw CSV file. It has the following columns:

    Returns
    -------
    dict
        The graph JSON file.

    Notes
    -----
    - <id> is a string (the curid used by Wikipedia)
    - <title> is a string (the standardized title used by Wikipedia)
    - <type> is an int, either 0 (article) or 14 (category)

    Example
    -------
    >>> df = pd.read_csv("~/.wikicat_data/enwiki_2018_12_20/full_catgraph.csv")
    >>> graph = generate_graph(df)
    >>> with open("~/.wikicat_data/enwiki_2018_12_20/category_graph.json", "w") as f:
    >>>     json.dump(graph, f)
    """
    df = df.copy()

    # Standardize and rename the cl_type
    df["page_title"] = df["page_title"].apply(standardize)
    df["cl_to"] = df["cl_to"].apply(standardize)
    df["cl_type"] = (
        df["cl_type"].str.replace("subcat", CATEGORY).str.replace("page", ARTICLE)
    )

    # Get id to title mapping, and title to id mapping, and id to type mapping
    id_to_title = df.set_index("page_id")["page_title"].to_dict()
    id_to_namespace = df.set_index("page_id")["cl_type"].to_dict()
    title_to_id = {CATEGORY: {}, ARTICLE: {}}

    for id_, title in id_to_title.items():
        page_type = id_to_namespace[id_]
        title_to_id[page_type][title] = id_

    # Remove missing titles
    cl_to = set(df["cl_to"])
    cat_titles = set(title_to_id[CATEGORY].keys())
    missing_cats = cl_to - cat_titles
    df = df[~df["cl_to"].isin(missing_cats)]

    # Create new column of the IDs of the linked parent
    df["cl_id"] = df["cl_to"].apply(lambda title: title_to_id[CATEGORY][title])

    def encode_data(data):
        return " ".join([str(x) for x in list(data)])

    # Create children to parents mapping and parents to children mapping
    children_to_parents = df.groupby("page_id")["cl_id"].apply(encode_data).to_dict()
    parents_to_children = df.groupby("cl_id")["page_id"].apply(encode_data).to_dict()

    # Convert to strings
    id_to_title = {k: v for k, v in id_to_title.items()}
    id_to_namespace = {k: v for k, v in id_to_namespace.items()}

    # Save the JSON file
    graph_json = dict(
        id_to_title=id_to_title,
        id_to_namespace=id_to_namespace,
        title_to_id=title_to_id,
        children_to_parents=children_to_parents,
        parents_to_children=parents_to_children,
    )

    return graph_json


def main(year, month, day, base_dir, ignore_existing):
    import pandas as pd

    base_dir = Path(base_dir).expanduser()
    int_dir = base_dir / f"enwiki_{year}_{month:02d}_{day:02d}"

    if not int_dir.exists() and not ignore_existing:
        raise ValueError(
            f"Intermediate directory {int_dir} does not exist. Make run all previous scripts before this one."
        )

    raw_df = pd.read_csv(int_dir / "full_catgraph.csv", na_filter=False)
    graph_json = generate_graph(raw_df)

    with open(int_dir / "category_graph.json", "w") as f:
        json.dump(graph_json, f)


def parse_args():
    parser = argparse.ArgumentParser(
        description="""
        This files takes the raw, full catgraph CSV file and converts it
        to a graph JSON file with a special structure that is more space
        efficient and easier to work with.
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--year", "-y", type=int, required=True, help="Year of dump")
    parser.add_argument("--month", "-m", type=int, required=True, help="Month of dump")
    parser.add_argument("--day", "-d", type=int, required=True, help="Day of dump")
    parser.add_argument(
        "--base_dir",
        type=str,
        help="Base directory for all data",
        default="~/.wikicat_data",
    )
    parser.add_argument(
        "--ignore_existing",
        action="store_true",
        help="Ignore cached output file. Only do this if you previous generated the file and want to regenerate it.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
