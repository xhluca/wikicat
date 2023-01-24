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
    --base_dir /path/to/save/intermediate/files
"""
import argparse
import json
from pathlib import Path

import pandas as pd

def merge_tables(page_csv_filepath, category_csv_filepath):
    page_df = pd.read_csv(page_csv_filepath, \
            usecols = ['page_id', 'page_title', 'page_namespace'], \
            dtype={'page_id': 'int32', 'page_title': str, \
                'page_namespace': 'int32'}).set_index('page_id')

    category_df = pd.read_csv(category_csv_filepath).set_index('cl_from')

    full_df = pd.merge(page_df, category_df, left_index=True, \
            right_index=True, how="right", copy=False)

    # keep only certain columns
    full_df = full_df[["page_namespace", "page_title", "cl_to", \
        "cl_type"]]
    
    # keep only articles and categories
    full_df = full_df[(full_df['page_namespace'] == 0) \
            | (full_df['page_namespace'] == 14)]

    full_df.index.name = 'page_id'

    full_df.sort_index(inplace=True)

    return full_df

def main(
        year,
        month,
        day,
        base_dir,
        page_csv_load_path,
        category_csv_load_path,
        save_filepath,
    ):
    base_dir = Path(base_dir).expanduser()
    base_dir.mkdir(parents=True, exist_ok=True)

    int_dir = base_dir / f"enwiki_{year}{month:02d}{day:02d}"
    int_dir.mkdir(exist_ok=True)

    # default names for filepath arguments
    if page_csv_load_path == "None":
        page_csv_load_path = int_dir / f"page.csv"
    
    if category_csv_load_path == "None":
        category_csv_load_path = int_dir / f"categorylinks.csv"
    
    if save_filepath == "None":
        save_filepath = int_dir / f"full_catgraph.csv"

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

    parser.add_argument("--year", type=int, required=True, help="Year of the dump")
    parser.add_argument("--month", type=int, required=True, help="Month of the year")
    parser.add_argument("--day", type=int, required=True, help="Day of the month")

    parser.add_argument(
        "--base_dir", type=str, help="Base directory for intermediate files", default="~/.wikicat_data"
    )

    parser.add_argument(
        "--page_csv_load_path",
        type=str,
        help="Path to the page CSV file",
        default="None",
    )
    parser.add_argument(
        "--category_csv_load_path",
        type=str,
        help="Path to the category CSV file",
        default="None",
    )
    parser.add_argument(
        "--save_filepath",
        type=str,
        help="Path to save the merged CSV file to",
        default="None",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
