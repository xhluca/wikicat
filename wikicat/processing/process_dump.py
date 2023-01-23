"""
This file takes the wikipedia dump in sql.gz format for a given date and
process it into a csv file in a record format to be used in further processing.

Usage example:

python -m wikicat.processing.process_dump \
    --year 2018 \
    --month 12 \
    --day 20 \
    --base_dir /path/to/save/intermediate/files \
    --use_2018_schema auto
"""
import argparse
import json
from pathlib import Path

import kwnlp_sql_parser

# TODO
# Update requirements.txt to include pandas and kwnlp_sql_parser with current version

def sql_dump_to_csv(dumpfile, output_filename=None, batch_size=500_000_000, use_2018_schema=False):
    print(f"Converting {dumpfile} into csv...")

    if use_2018_schema:
        print("Using 2018 schema")
        original_col_list = kwnlp_sql_parser.wp_sql_patterns._TABLE_COLUMN_PATTERNS['page'].copy()
        page_col_l = kwnlp_sql_parser.wp_sql_patterns._TABLE_COLUMN_PATTERNS['page'].copy()
        page_r = kwnlp_sql_parser.WikipediaSqlColumn("page_restrictions", kwnlp_sql_parser.wp_sql_patterns.SINGLE_QUOTED_ANYTHING)
        page_c = kwnlp_sql_parser.WikipediaSqlColumn("page_counter", kwnlp_sql_parser.wp_sql_patterns.DIGITS)
        page_col_l.insert(3, page_r)
        page_col_l.insert(4, page_c)
        kwnlp_sql_parser.wp_sql_patterns._TABLE_COLUMN_PATTERNS['page'] = tuple(page_col_l)
    
    wsd = kwnlp_sql_parser.WikipediaSqlDump(f)

    wsd.to_csv(batch_size=batch_size, outfile=str(output_filename))

    # reverse changes to library's col list
    if use_2018_schema:
        kwnlp_sql_parser.wp_sql_patterns._TABLE_COLUMN_PATTERNS['page'] = original_col_list

def main(
        year,
        month,
        day,
        base_dir,
        page_table_filepath,
        category_table_filepath,
        page_csv_outpath,
        cat_csv_outpath,
        use_2018_schema="auto",
    ):

    base_dir = Path(base_dir).expanduser()
    base_dir.mkdir(parents=True, exist_ok=True)

    int_dir = base_dir / f"enwiki_{year}{month:02d}{day:02d}"
    int_dir.mkdir(exist_ok=True)

    # default names for filepaths
    if page_table_filepath is None:
        page_table_filepath = int_dir / "enwiki-page.sql.gz"

    if category_table_filepath is None:
        category_table_filepath = int_dir / "enwiki-categorylinks.sql.gz"

    if page_csv_outpath is None:
        page_csv_outpath = int_dir / "page.csv"

    if cat_csv_outpath is None:
        cat_csv_outpath = int_dir / "categorylinks.csv"

    # fix issue with argparse booleans
    if use_2018_schema == "auto":
        use_2018_schema = False
        if "2018" in str(int_dir):
            use_2018_schema = True

    sql_dump_to_csv(page_table_filepath, page_csv_outpath, use_2018_schema=use_2018_schema)
    sql_dump_to_csv(category_table_filepath, cat_csv_outpath, use_2018_schema=use_2018_schema)


def parse_args():
    parser = argparse.ArgumentParser(
        description="""
        This file takes the wikipedia dump in sql.gz format for a given date and
        process it into a csv file in a record format to be used in further processing.
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
        "--page_table_filepath", 
        type=str, 
        help="Filepath of the page table dump", 
        default="None"
    )
    parser.add_argument(
        "--category_table_filepath", 
        type=str, 
        help="Filepath of the categorylinks table dump", 
        default="None"
    )
    parser.add_argument(
        "--page_csv_outpath", 
        type=str, 
        help="Output filename for th page table csv (for further processing)", 
        default="None"
    )
    parser.add_argument(
        "--cat_csv_outpath", 
        type=str, 
        help="Output filename for the categorylinks table csv (for further processing)", 
        default="None"
    )
    parser.add_argument(
        "--use_2018_schema", type=str, help="Use the 2018 schema for the page table", default="auto"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
