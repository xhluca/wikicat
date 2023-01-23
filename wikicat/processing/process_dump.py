"""
This file takes the wikipedia dump in sql.gz format for a given date and
process it into a csv file in a record format to be used in further processing.

Usage example:

python -m wikicat.processing.process_dump \
    --page_table_filepath /path/to/page/table/dump.sql.gz \
    --category_table_filepath /path/to/category/table/dump.sql.gz \
    --use_2018_schema auto
"""
import argparse
import json
from pathlib import Path

import kwnlp_sql_parser

# TODO
# Update requirements.txt to include pandas and kwnlp_sql_parser with current version

def _sql_dump_to_csv(dumpfile, output_filename=None, batch_size=500_000_000):
    print(f"Converting {dumpfile} into csv...")
    wsd = kwnlp_sql_parser.WikipediaSqlDump(f)
    if output_filename is None:
        output_filename = dumpfile.split(".")[0] + ".csv"
    wsd.to_csv(batch_size=batch_size, outfile=output_filename)

def main(page_table_filepath, category_table_filepath, page_csv_outpath=None, cat_csv_outpath=None, use_2018_schema=False):

    if use_2018_schema == "auto":
        use_2018_schema = False
        if "2018" in page_table_filepath:
            use_2018_schema = True

    if use_2018_schema:
        print("Using 2018 schema")
        page_col_l = list(kwnlp_sql_parser.wp_sql_patterns._TABLE_COLUMN_PATTERNS['page'])
        page_r = kwnlp_sql_parser.WikipediaSqlColumn("page_restrictions", kwnlp_sql_parser.wp_sql_patterns.SINGLE_QUOTED_ANYTHING)
        page_c = kwnlp_sql_parser.WikipediaSqlColumn("page_counter", kwnlp_sql_parser.wp_sql_patterns.DIGITS)
        page_col_l.insert(3, page_r)
        page_col_l.insert(4, page_c)
        kwnlp_sql_parser.wp_sql_patterns._TABLE_COLUMN_PATTERNS['page'] = tuple(page_col_l)

    _sql_dump_to_csv(page_table_filepath, output_filename=page_csv_outpath)
    _sql_dump_to_csv(category_table_filepath, output_filename=cat_csv_outpath)


def parse_args():
    parser = argparse.ArgumentParser(
        description="""
        This file takes the wikipedia dump in sql.gz format for a given date and
        process it into a csv file in a record format to be used in further processing.
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--page_table_filepath", 
        type=str, 
        help="Filepath of the page table dump", 
        default="~/wikicat_data/enwiki-page.sql.gz"
    )
    parser.add_argument(
        "--category_table_filepath", 
        type=str, 
        help="Filepath of the categorylinks table dump", 
        default="~/.wikicat_data/enwiki-categorylinks.sql.gz"
    )
    parser.add_argument(
        "--page_csv_outpath", 
        type=str, 
        help="Output filename for th page table csv (for further processing)", 
        default="~/wikicat_data/enwiki-page.csv"
    )
    parser.add_argument(
        "--cat_csv_outpath", 
        type=str, 
        help="Output filename for the categorylinks table csv (for further processing)", 
        default="~/wikicat_data/enwiki-categorylinks.csv"
    )
    parser.add_argument(
        "--use_2018_schema", type=str, help="Use the 2018 schema for the page table", default="auto"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
