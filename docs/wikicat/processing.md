# Reference for `wikicat.processing`

# Reference for `wikicat.processing.download_dump`

## `parse_args`

```python
wikicat.processing.download_dump.parse_args()
```

## `show_progress`

```python
wikicat.processing.download_dump.show_progress(block_num, block_size, total_size)
```

## `download_dump`

```python
wikicat.processing.download_dump.download_dump(year, month, day, base_dir, postfix, prefix="enwiki-", extension="sql.gz", base_url="https://archive.org/download/", ignore_existing=False)
```

#### Description

Download the SQL dump of the English Wikipedia from archive.org. The files are gzipped SQL file that
contains the page and categoryliniks tables. To find the list, visit:
https://archive.org/search.php?query=creator%3A%22Wikimedia+projects+editors%22+%22Wikimedia+database+dump+of+the+English+Wikipedia%22&sort=-date


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `year` | `int` |  | Year of the dump |
| `month` | `int` |  | Month of the year |
| `day` | `int` |  | Day of the month |
| `base_dir` | `str` |  | Directory where a new directory will be created to store the dump files. The directory name will be in the format of enwiki_<YYYY>_<MM>_<DD>. |
| `base_url` | `str` | `"https://archive.org/download/"` | Base URL of the dump file, by default "https://archive.org/download/" |
| `prefix` | `str` | `"enwiki-"` | Prefix of the dump file, by default "enwiki-" |
| `postfix` | `str` |  | Postfix of the dump file, should either be "-page" or "-categorylinks" |
| `extension` | `str` | `"sql.gz"` | Extension of the dump file, by default "sql.gz" |
| `ignore_existing` | `bool` | `False` | Whether to ignore existing files, by default False |


#### Returns

```
Path
```

Path to the downloaded file

#### Notes

By default, the downloaded file will be saved to
```
<base_dir>/<prefix>enwiki_<YYYY>_<MM>_<DD><postfix>.<extension>
```

## `main`

```python
wikicat.processing.download_dump.main(year, month, day, base_dir, base_url, ignore_existing)
```

# Reference for `wikicat.processing.generate_graph`

## `generate_graph`

```python
wikicat.processing.generate_graph.generate_graph(df)
```

#### Description

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


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `df` | `pandas.DataFrame` |  | The raw CSV file. It has the following columns: |


#### Returns

```
dict
```

The graph JSON file.

#### Notes

- <id> is a string (the curid used by Wikipedia)
- <title> is a string (the standardized title used by Wikipedia)
- <type> is an int, either 0 (article) or 14 (category)


#### Example

>>> df = pd.read_csv("~/.wikicat_data/enwiki_2018_12_20/full_catgraph.csv")
>>> graph = generate_graph(df)
>>> with open("~/.wikicat_data/enwiki_2018_12_20/category_graph.json", "w") as f:
>>>     json.dump(graph, f)

## `main`

```python
wikicat.processing.generate_graph.main(year, month, day, base_dir, ignore_existing)
```

## `parse_args`

```python
wikicat.processing.generate_graph.parse_args()
```

# Reference for `wikicat.processing.merge_tables`

## `merge_tables`

```python
wikicat.processing.merge_tables.merge_tables(page_csv_filepath, category_csv_filepath)
```

#### Description

Merge the page and category tables into a single table.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `page_csv_filepath` | `str` |  | Path to the page CSV file. |
| `category_csv_filepath` | `str` |  | Path to the category CSV file. |


#### Returns

```
pandas.DataFrame
```

The merged table.

#### Notes

This step may take a while to run (1h+). It is recommended to run this
script on a machine with a lot of RAM.


#### Example

>>> page_csv_filepath = "~/.wikicat_data/enwiki_2018_12_20/page.csv"
>>> category_csv_filepath = "~/.wikicat_data/enwiki_2018_12_20/categorylinks.csv"
>>> df = merge_tables(page_csv_filepath, category_csv_filepath)
>>> print(df.head(10))
>>> df.to_csv("~/.wikicat_data/enwiki_2018_12_20/full_catgraph.csv")

## `main`

```python
wikicat.processing.merge_tables.main(year, month, day, base_dir, ignore_existing)
```

## `parse_args`

```python
wikicat.processing.merge_tables.parse_args()
```

# Reference for `wikicat.processing.process_dump`

## `process_dump`

```python
wikicat.processing.process_dump.process_dump(dumpfile, output_filename, batch_size=50000000, use_2018_schema=False)
```

#### Description

Process a wikipedia dump into a csv file.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `dumpfile` | `str` |  | Path to the wikipedia dump file. |
| `output_filename` | `str` |  | Path to the output csv file. |
| `batch_size` | `int` | `50000000` | Number of rows to process at a time, by default 50_000_000. This parameter is passed to kwnlp_sql_parser.WikipediaSqlDump.to_csv. A larger batch size will use more memory, but will be faster. Reduce the batch size if you run out of memory while processing the dump. |
| `use_2018_schema` | `bool` | `False` | Whether to use the 2018 schema for the page table, by default False. |


#### Notes

This step may take a while to run (1h+). It is recommended to run this
script on a machine with a lot of RAM.


#### Example

>>> # Process page.sql.gz into page.csv
>>> dumpfile = "~/.wikicat_data/enwiki_2018_12_20/enwiki-20181220-page.sql.gz"
>>> output_filename = "~/.wikicat_data/enwiki_2018_12_20/page.csv"
>>> process_dump(dumpfile, output_filename, use_2018_schema=True, batch_size=10_000_000)
>>>
>>> # Process categorylinks.sql.gz into categorylinks.csv
>>> dumpfile = "~/.wikicat_data/enwiki_2018_12_20/enwiki-20181220-categorylinks.sql.gz"
>>> output_filename = "~/.wikicat_data/enwiki_2018_12_20/categorylinks.csv"
>>> process_dump(dumpfile, output_filename, use_2018_schema=True, batch_size=10_000_000)

## `main`

```python
wikicat.processing.process_dump.main(year, month, day, base_dir, use_2018_schema, batch_size, ignore_existing)
```

## `parse_args`

```python
wikicat.processing.process_dump.parse_args()
```

