"""
This files takes the raw, full catgraph CSV file and converts it
to a JSON file with the following structure.

Usage example:

python -m wikicat.processing.generate_graph \
    --load_dir /path/to/raw/csv \
    --save_dir /path/to/save/json \
    --load_name full_catgraph_20181220.csv \
    --save_name category_graph_20181220.json
"""
import argparse
import json
from pathlib import Path

from .. import standardize


def generate_graph(df) -> dict:
    """
    Generate the graph JSON file from the raw CSV file.

    Parameters
    ----------
    df : pandas.DataFrame
        The raw CSV file. It has the following columns:
        - page_id: the curid used by Wikipedia
        - page_title: the standardized title used by Wikipedia
        - cl_to: the standardized title of the parent category
        - cl_type: the type of the parent category, either "category" or "article"

    Returns
    -------
    dict
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

    Notes
    -----
    - <id> is a string (the curid used by Wikipedia)
    - <title> is a string (the standardized title used by Wikipedia)
    - <type> is a string, either "category" or "article"
    """
    df = df.copy()

    # Standardize and rename the cl_type
    df["page_title"] = df["page_title"].apply(standardize)
    df["cl_to"] = df["cl_to"].apply(standardize)
    df["cl_type"] = (
        df["cl_type"].str.replace("subcat", "category").str.replace("page", "article")
    )

    # Get id to title mapping, and title to id mapping, and id to type mapping
    id_to_title = df.set_index("page_id")["page_title"].to_dict()
    id_to_namespace = df.set_index("page_id")["cl_type"].to_dict()
    title_to_id = {"category": {}, "article": {}}

    for id_, title in id_to_title.items():
        page_type = id_to_namespace[id_]
        title_to_id[page_type][title] = id_

    # Remove missing titles
    cl_to = set(df["cl_to"])
    cat_titles = set(title_to_id["category"].keys())
    missing_cats = cl_to - cat_titles
    df = df[~df["cl_to"].isin(missing_cats)]

    # Create new column of the IDs of the linked parent
    df["cl_id"] = df["cl_to"].apply(lambda title: title_to_id["category"][title])

    # Create children to parents mapping and parents to children mapping
    children_to_parents = df.groupby("page_id")["cl_id"].apply(list).to_dict()
    parents_to_children = df.groupby("cl_id")["page_id"].apply(list).to_dict()

    # Conver to strings
    id_to_title = {str(k): v for k, v in id_to_title.items()}
    id_to_namespace = {str(k): v for k, v in id_to_namespace.items()}
    for namespace in title_to_id:
        title_to_id[namespace] = {k: str(v) for k, v in title_to_id[namespace].items()}
    children_to_parents = {
        str(k): [str(v) for v in v] for k, v in children_to_parents.items()
    }
    parents_to_children = {
        str(k): [str(v) for v in v] for k, v in parents_to_children.items()
    }

    # Save the JSON file
    graph_json = dict(
        id_to_title=id_to_title,
        id_to_namespace=id_to_type,
        title_to_id=title_to_id,
        children_to_parents=children_to_parents,
        parents_to_children=parents_to_children,
    )

    return graph_json


def main(load_dir, save_dir, load_name, save_name):
    import pandas as pd

    load_dir = Path(load_dir).expanduser()
    save_dir = Path(save_dir).expanduser()
    save_dir.mkdir(exist_ok=True)

    raw_df = pd.read_csv(load_dir / load_name, na_filter=False)

    graph_json = generate_graph(raw_df)

    with open(save_dir / save_name, "w") as f:
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
    parser.add_argument(
        "--load_dir", type=str, help="Directory to load the raw CSV file from", default="~/.wikicat_data"
    )
    parser.add_argument(
        "--save_dir", type=str, help="Directory to save the JSON file to", default="~/.wikicat_data"
    )
    parser.add_argument(
        "--load_name",
        type=str,
        default="full_catgraph_20181220.csv",
        help="Name of the raw CSV file",
    )
    parser.add_argument(
        "--save_name",
        type=str,
        default="category_graph_20181220.json",
        help="Name of the JSON file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
