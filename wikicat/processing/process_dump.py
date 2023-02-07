"""
This file takes the wikipedia dump in sql.gz format for a given date and
process it into a csv file in a record format to be used in further processing.

Usage example:

python -m wikicat.processing.process_dump \
    --year 2018 \
    --month 12 \
    --day 20 \
    --base_dir ~/.wikicat_data/ \
    --use_2018_schema auto
"""
import argparse
import json
from pathlib import Path

import kwnlp_sql_parser

# TODO
# Update requirements.txt to include pandas and kwnlp_sql_parser with current version


def process_dump(
    dumpfile, output_filename, batch_size=50_000_000, use_2018_schema=False
):
    """
    Process a wikipedia dump into a csv file.

    Parameters
    ----------
    dumpfile : str
        Path to the wikipedia dump file.
    output_filename : str
        Path to the output csv file.
    batch_size : int, optional
        Number of rows to process at a time, by default 50_000_000. This
        parameter is passed to kwnlp_sql_parser.WikipediaSqlDump.to_csv.
        A larger batch size will use more memory, but will be faster. Reduce
        the batch size if you run out of memory while processing the dump.
    use_2018_schema : bool, optional
        Whether to use the 2018 schema for the page table, by default False.

    Notes
    -----
    This step may take a while to run (1h+). It is recommended to run this
    script on a machine with a lot of RAM.

    Example
    -------
    >>> # Process page.sql.gz into page.csv
    >>> dumpfile = "~/.wikicat_data/enwiki_2018_12_20/enwiki-20181220-page.sql.gz"
    >>> output_filename = "~/.wikicat_data/enwiki_2018_12_20/page.csv"
    >>> process_dump(dumpfile, output_filename, use_2018_schema=True, batch_size=10_000_000)
    >>>
    >>> # Process categorylinks.sql.gz into categorylinks.csv
    >>> dumpfile = "~/.wikicat_data/enwiki_2018_12_20/enwiki-20181220-categorylinks.sql.gz"
    >>> output_filename = "~/.wikicat_data/enwiki_2018_12_20/categorylinks.csv"
    >>> process_dump(dumpfile, output_filename, use_2018_schema=True, batch_size=10_000_000)
    """
    dumpfile = str(dumpfile)
    output_filename = str(output_filename)

    if isinstance(use_2018_schema, str):
        if use_2018_schema.lower() == "true":
            use_2018_schema = True
        elif use_2018_schema.lower() == "false":
            use_2018_schema = False
        elif use_2018_schema.lower() == "auto":
            use_2018_schema = "2018" in dumpfile

    if not isinstance(use_2018_schema, bool):
        raise ValueError(
            f"Invalid value for use_2018_schema: {use_2018_schema}. "
            "Must be one of True, False, 'true', 'false', or 'auto'."
        )

    print(f"Converting {dumpfile} into csv...")

    if use_2018_schema:
        print("Using 2018 schema")
        # copy original tuple
        original_col_list = tuple(
            list(kwnlp_sql_parser.wp_sql_patterns._TABLE_COLUMN_PATTERNS["page"])
        )
        page_col_l = list(
            kwnlp_sql_parser.wp_sql_patterns._TABLE_COLUMN_PATTERNS["page"]
        )
        # page_r = kwnlp_sql_parser.WikipediaSqlColumn("page_restrictions", kwnlp_sql_parser.wp_sql_patterns.SINGLE_QUOTED_ANYTHING)
        page_c = kwnlp_sql_parser.WikipediaSqlColumn(
            "page_counter", kwnlp_sql_parser.wp_sql_patterns.DIGITS
        )
        # page_col_l.insert(3, page_r)
        page_col_l.insert(4, page_c)
        kwnlp_sql_parser.wp_sql_patterns._TABLE_COLUMN_PATTERNS["page"] = tuple(
            page_col_l
        )

    wsd = kwnlp_sql_parser.WikipediaSqlDump(dumpfile)

    wsd.to_csv(batch_size=batch_size, outfile=output_filename)

    # reverse changes to library's col list
    if use_2018_schema:
        kwnlp_sql_parser.wp_sql_patterns._TABLE_COLUMN_PATTERNS[
            "page"
        ] = original_col_list


def main(year, month, day, base_dir, use_2018_schema, batch_size, ignore_existing):
    base_dir = Path(base_dir).expanduser()
    int_dir = base_dir / f"enwiki_{year}_{month:02d}_{day:02d}"
    int_dir.mkdir(parents=True, exist_ok=True)

    # default names for filepaths
    prefix = f"enwiki-{year}{month:02d}{day:02d}-"

    page_table_load_path = int_dir / f"{prefix}page.sql.gz"
    page_csv_save_path = int_dir / "page.csv"

    category_table_load_path = int_dir / f"{prefix}categorylinks.sql.gz"
    cat_csv_save_path = int_dir / "categorylinks.csv"

    # fix issue with argparse booleans
    if use_2018_schema == "auto":
        use_2018_schema = "2018" == str(year)

    if page_csv_save_path.is_file() and not ignore_existing:
        print(f"Skipping {page_csv_save_path}, already exists...")
    else:
        process_dump(
            page_table_load_path,
            output_filename=page_csv_save_path,
            use_2018_schema=use_2018_schema,
            batch_size=batch_size,
        )
    if cat_csv_save_path.is_file() and not ignore_existing:
        print(f"Skipping {cat_csv_save_path}, already exists...")
    else:
        process_dump(
            category_table_load_path,
            output_filename=cat_csv_save_path,
            use_2018_schema=use_2018_schema,
            batch_size=batch_size,
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="""
        This file takes the wikipedia dump in sql.gz format for a given date and
        process it into a csv file in a record format to be used in further processing.
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--year", "-y", type=int, required=True, help="Year of dump")
    parser.add_argument("--month", "-m", type=int, required=True, help="Month of dump")
    parser.add_argument("--day", "-d", type=int, required=True, help="Day of dump")

    parser.add_argument(
        "--base_dir",
        type=str,
        help="Base directory where the intermediate directory (enwiki_YYYY_MM_DD) is located, after running download_dump.",
        default="~/.wikicat_data",
    )
    parser.add_argument(
        "--use_2018_schema",
        type=str,
        help="Use the 2018 schema for the page table (post 2018 has a different schema)",
        default="auto",
        choices=["auto", "true", "false"],
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        help="Adjust the batch size for the processing. Increasing this will use more memory but will be faster.",
        default=1_000_000,
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
