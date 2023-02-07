import argparse
import json
from pathlib import Path
from urllib.request import urlretrieve


def parse_args():
    parser = argparse.ArgumentParser(
        description="""
        This downloads a SQL dump of relevant files from the "Wikimedia database dump of 
        the English Wikipedia" from archive.org. The files are gzipped SQL file that contains the
        page and categoryliniks tables. To find the list, visit:
        https://archive.org/search.php?query=creator%3A%22Wikimedia+projects+editors%22+%22Wikimedia+database+dump+of+the+English+Wikipedia%22&sort=-date
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--year", "-y", type=int, required=True, help="Year of dump")
    parser.add_argument("--month", "-m", type=int, required=True, help="Month of dump")
    parser.add_argument("--day", "-d", type=int, required=True, help="Day of dump")

    parser.add_argument(
        "--base_url",
        type=str,
        default="https://archive.org/download/",
        help="Base URL of the dump file",
    )
    parser.add_argument(
        "--base_dir",
        type=str,
        help="Directory where a new directory will be created to store the dump files. The directory name will be in the format of enwiki_<YYYY>_<MM>_<DD>.",
        default="~/.wikicat_data",
    )
    parser.add_argument(
        "--ignore_existing",
        action="store_true",
        help="Ignore cached output file. Only do this if you previous downloaded the file and want to redownload it.",
    )

    return parser.parse_args()


# prepare progressbar
def show_progress(block_num, block_size, total_size):
    perc = round(block_num * block_size / total_size * 100, 2)
    print(f"{perc}%", end="\r")


def download_dump(
    year,
    month,
    day,
    base_dir,
    postfix,
    prefix="enwiki-",
    extension="sql.gz",
    base_url="https://archive.org/download/",
    ignore_existing=False,
):
    """
    Download the SQL dump of the English Wikipedia from archive.org. The files are gzipped SQL file that
    contains the page and categoryliniks tables. To find the list, visit:
    https://archive.org/search.php?query=creator%3A%22Wikimedia+projects+editors%22+%22Wikimedia+database+dump+of+the+English+Wikipedia%22&sort=-date

    Parameters
    ----------
    year : int
        Year of the dump
    month : int
        Month of the year
    day : int
        Day of the month
    base_dir : str
        Directory where a new directory will be created to store the dump files. The directory
        name will be in the format of enwiki_<YYYY>_<MM>_<DD>.
    base_url : str, optional
        Base URL of the dump file, by default "https://archive.org/download/"
    prefix : str, optional
        Prefix of the dump file, by default "enwiki-"
    postfix : str
        Postfix of the dump file, should either be "-page" or "-categorylinks"
    extension : str, optional
        Extension of the dump file, by default "sql.gz"
    ignore_existing : bool, optional
        Whether to ignore existing files, by default False

    Returns
    -------
    Path
        Path to the downloaded file
    Notes
    -----
    By default, the downloaded file will be saved to
    ```
    <base_dir>/<prefix>enwiki_<YYYY>_<MM>_<DD><postfix>.<extension>
    ```
    """
    base_dir = Path(base_dir).expanduser()
    base_dir = base_dir / f"enwiki_{year}_{month:02d}_{day:02d}"
    base_dir.mkdir(parents=True, exist_ok=True)

    # Format the URL
    dump_base_name = f"{prefix}{year}{month:02d}{day:02d}"
    dump_full_name = f"{dump_base_name}{postfix}.{extension}"
    dump_url = f"{base_url}{dump_base_name}/{dump_full_name}"
    save_path = base_dir / dump_full_name

    if save_path.is_file() and not ignore_existing:
        print(f"File {save_path} already exists. Skipping.")
        out_path = save_path

    else:
        print("Downloading:", dump_url)
        print("Saving to:", save_path)

        out_path, headers = urlretrieve(dump_url, save_path, show_progress)
        out_path = Path(out_path)

        print("Done.")
        print("Saved to:", out_path)
        print("Size:", out_path.stat().st_size)
        print("Result headers:", headers)

    print("\n====================================\n")

    return out_path


def main(year, month, day, base_dir, base_url, ignore_existing):
    for p in ["-page", "-categorylinks"]:
        download_dump(
            year=year,
            month=month,
            day=day,
            base_dir=base_dir,
            base_url=base_url,
            postfix=p,
            ignore_existing=ignore_existing,
        )


if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
