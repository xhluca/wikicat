"""
This file takes the previously-processed separate CSV files for the page and
category tables and merges them into a single CSV file. This is done to
reduce the number of files that need to be read in order to generate the
category graph.

Usage example:

python -m wikicat.processing.merge_tables \
    --year 2018 \
    --month 12 \
    --day 20 \
    --base_dir "~/.wikicat_data/"
"""
import argparse
import json
from pathlib import Path

import pandas as pd


def merge_tables(page_csv_filepath, category_csv_filepath):
    """
    Merge the page and category tables into a single table.

    Parameters
    ----------
    page_csv_filepath : str
        Path to the page CSV file.
    category_csv_filepath : str
        Path to the category CSV file.

    Returns
    -------
    pandas.DataFrame
        The merged table.

    Notes
    -----
    This step may take a while to run (1h+). It is recommended to run this
    script on a machine with a lot of RAM.

    Example
    -------
    >>> page_csv_filepath = "~/.wikicat_data/enwiki_2018_12_20/page.csv"
    >>> category_csv_filepath = "~/.wikicat_data/enwiki_2018_12_20/categorylinks.csv"
    >>> df = merge_tables(page_csv_filepath, category_csv_filepath)
    >>> print(df.head(10))
    >>> df.to_csv("~/.wikicat_data/enwiki_2018_12_20/full_catgraph.csv")
    """
    page_df = pd.read_csv(
        page_csv_filepath,
        usecols=["page_id", "page_title", "page_namespace"],
        dtype={"page_id": "int32", "page_title": str, "page_namespace": "int32"},
    ).set_index("page_id")

    category_df = pd.read_csv(category_csv_filepath).set_index("cl_from")

    full_df = pd.merge(
        page_df, category_df, left_index=True, right_index=True, how="right", copy=False
    )

    # keep only certain columns
    full_df = full_df[["page_namespace", "page_title", "cl_to", "cl_type"]]

    # keep only articles and categories
    full_df = full_df[
        (full_df["page_namespace"] == 0) | (full_df["page_namespace"] == 14)
    ]

    full_df.index.name = "page_id"

    full_df.sort_index(inplace=True)

    return full_df


def main(year, month, day, base_dir, ignore_existing):
    base_dir = Path(base_dir).expanduser()
    base_dir.mkdir(parents=True, exist_ok=True)

    int_dir = base_dir / f"enwiki_{year}_{month:02d}_{day:02d}"

    if not int_dir.is_dir() and not ignore_existing:
        raise ValueError(
            f"Intermediate directory {int_dir} does not exist. Make sure to run the download_dump.py script first."
        )

    # default names for filepath arguments
    page_csv_load_path = int_dir / "page.csv"
    category_csv_load_path = int_dir / "categorylinks.csv"
    save_filepath = int_dir / "full_catgraph.csv"

    # merge the tables
    full_df = merge_tables(page_csv_load_path, category_csv_load_path)

    # Save the full dataframe to a CSV file
    full_df.to_csv(save_filepath)


def parse_args():
    parser = argparse.ArgumentParser(
        description="""
        This file takes the previously-processed separate CSV files for the page and
        category tables and merges them into a single CSV file. This is done to
        reduce the number of files that need to be read in order to generate the
        category graph.
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--year", "-y", type=int, required=True, help="Year of dump")
    parser.add_argument("--month", "-m", type=int, required=True, help="Month of dump")
    parser.add_argument("--day", "-d", type=int, required=True, help="Day of dump")

    parser.add_argument(
        "--base_dir",
        type=str,
        help="The directory containing a directory in the form enwiki_<YYYY>_<MM>_<DD>. The latter contains the dumps and your output file will be stored there.",
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
