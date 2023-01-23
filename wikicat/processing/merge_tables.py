"""
This file takes the previously-processed separate CSV files for the page and
category tables and merges them into a single CSV file. This is done to
reduce the number of files that need to be read in order to generate the
category graph.

Usage example:

python -m wikicat.processing.merge_tables \
    --page_csv_filepath /path/to/page/csv \
    --category_csv_filepath /path/to/category/csv \
    --save_filepath /path/to/save/csv \
"""
import argparse
import json
from pathlib import Path

def main(page_csv_filepath, category_csv_filepath, save_filepath):
    page_df = pd.read_csv(page_csv_filepath, \
            usecols = ['page_id', 'page_title', 'page_namespace'], \
            dtype={'page_id': np.int32, 'page_title': str, \
                'page_namespace': np.int32}).set_index('page_id')

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

    # Save the full dataframe to a CSV file
    full_df.to_csv(save_filepath)

    return full_df


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
    parser.add_argument(
        "--page_csv_filepath",
        type=str,
        help="Path to the page CSV file",
        default="~/.wikicat_data/page_table.csv",
    )
    parser.add_argument(
        "--category_csv_filepath",
        type=str,
        help="Path to the category CSV file",
        default="~/.wikicat_data/category_table.csv",
    )
    parser.add_argument(
        "--save_filepath",
        type=str,
        help="Path to save the merged CSV file to",
        default="~/.wikicat_data/full_catgraph.csv",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
