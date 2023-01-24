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
    parser.add_argument("--year", type=int, required=True, help="Year of the dump")
    parser.add_argument("--month", type=int, required=True, help="Month of the year")
    parser.add_argument("--day", type=int, required=True, help="Day of the month")
    parser.add_argument(
        "--base_url",
        type=str,
        default="https://archive.org/download/",
        help="Base URL of the dump file",
    )
    parser.add_argument(
        "--name_prefix",
        type=str,
        default="enwiki-",
        help="Prefix of the dump file name",
    )
    parser.add_argument(
        "--save_dir",
        type=str,
        help="Directory to save the JSON file to",
        default="~/.wikicat_data",
    )

    return parser.parse_args()


# prepare progressbar
def show_progress(block_num, block_size, total_size):
    print(round(block_num * block_size / total_size *100,2), end="\r")

def main(
    year,
    month,
    day,
    save_dir,
    base_url="https://archive.org/download/",
    name_prefix="enwiki-",
):
    postfix = ("-page", "-categorylinks")
    save_dir = Path(save_dir).expanduser()
    save_dir = save_dir / f"enwiki_{year}{month:02d}{day:02d}"
    save_dir.mkdir(parents=True, exist_ok=True)

    # Format the URL
    base_name = f"{name_prefix}{year}{month:02d}{day:02d}"
    extension = "sql.gz"

    for p in postfix:
        dump_name = f"{base_name}{p}.{extension}"
        dump_url = f"{base_url}{base_name}/{dump_name}"
        print("Downloading:", dump_url)
        dump_path = save_dir / dump_name

        urlretrieve(dump_url, dump_path, show_progress)


if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
