# Reference for `wikicat`

## `standardize`

```python
wikicat.standardize(title, form="NFC")
```

#### Description

Standardizes a title by replacing spaces with underscores and normalizing it to
a given form following Unicode's normalization (defaults to NFC).


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `title` | `str` |  | The title to standardize. |
| `form` | `str` | `"NFC"` | The form to normalize the title to. Defaults to NFC. |


## `Page`

```python
wikicat.Page(id, title, namespace, standardize_title=True)
```

#### Description

Represents a Wikipedia page. It should be used alongside CategoryGraph to
represent a page in the graph. You can also use it to find the URL of a page.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `id` | `str` |  | The curid of the page. |
| `title` | `str` |  | The canonical title of the page. |
| `namespace` | `str` |  | The namespace of the page. Either "category" or "article". |
| `standardize_title` | `bool` | `True` | Whether to standardize the title. If True, it will replace spaces with underscores and normalize the title to NFC form. |


#### Examples

```python
>>> import wikicat as wc
>>> page = wc.Page(id="7954681", title="Montreal", namespace="article")
>>> page
Page(id="7954681", title="Montreal", namespace="article")
>>> page.is_category()
False
>>> page.is_article()
True
>>> page.get_url()
'https://en.wikipedia.org/wiki/Montreal'
>>> page.get_url(use_curid=True)
'https://en.wikipedia.org/?curid=7954681'
```



### `Page.__repr__`

```python
wikicat.Page.__repr__(self)
```

#### Description



#### Returns

```
str
```

The representation of the page.

#### Examples

```python
>>> import wikicat as wc
>>> page = wc.Page(id="7954681", title="Montreal", namespace="article")
>>> str(page)
```



### `Page.is_category`

```python
wikicat.Page.is_category(self)
```

#### Description



#### Returns

```
bool
```

Whether the page is a category.

### `Page.is_article`

```python
wikicat.Page.is_article(self)
```

#### Description



#### Returns

```
bool
```

Whether the page is an article.

### `Page.get_url`

```python
wikicat.Page.get_url(self, use_curid=False)
```

#### Description



#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `use_curid` | `bool` | `False` | Whether to use the curid in the URL. If False, it will use the title. The curid is more stable, but the title is more human-readable. |


#### Returns

```
str
```

The URL of the page.

## `CategoryGraph`

```python
wikicat.CategoryGraph(graph_json)
```

#### Description

This class represents the category graph. It is used to find the parents and
children of a page (category or article) in the graph. It also contains the
mapping between the curid (a unique ID assigned to each page) and the title of a page.

It is also capable of:
- checking whether the graph contains a page or not
- create a `wikicat.Page` object from a title (given a namespace) or curid
- compute the degree of a page by its in-degree (number of parents) and out-degree (number of children)
- list all the categories or articles in the graph
- rank the categories or articles by their degree
- format the graph as a human-readable string
- traverse all the children or parents of a page for a given depth

Although you can create a CategoryGraph object manually, it is recommended to use
the `read_json` class method to read the graph from a JSON file.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `graph_json` | `dict` |  | The JSON object containing the category graph. |


#### Examples

```python
>>> import json
>>> import wikicat as wc
>>> with open("category_graph_<yyyy>_<mm>_<dd>.json", "r") as f:
...     graph_json = json.load(f)
>>> cg = wc.CategoryGraph(graph_json)
>>> # Get the page for "Montreal"
>>> page = cg.get_page_from_title('Montreal', 'article')
>>> # Get the categories for "Montreal"
>>> cats = cg.get_parents(page=page)
>>> print(f"Category tags of {page.title}: {cats}")
>>> # Get URL of "Montreal"
>>> print("URL:", page.get_url())
```



### `CategoryGraph.read_json`

```python
wikicat.CategoryGraph.read_json(cls, path)
```

#### Description

Loads the category graph from a JSON file.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `path` | `str` |  | The path to the JSON file containing the category graph. |


#### Examples

```python
>>> import wikicat as wc
>>> graph = wc.CategoryGraph.read_json("category_graph_<yyyy>_<mm>_<dd>.json")

```



#### Notes

This method uses orjson if it is available, otherwise it uses the standard json module.
You can install orjson with `pip install orjson`.

### `CategoryGraph.remove_hidden_ids`

```python
wikicat.CategoryGraph.remove_hidden_ids(self, ids)
```

#### Description



#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `ids` | `list[str]` |  | A list of IDs to remove hidden categories from. |


#### Returns

```
list of str
```

The list of IDs with hidden categories removed.

### `CategoryGraph.contains_id`

```python
wikicat.CategoryGraph.contains_id(self, id)
```

#### Description

Check whether the graph contains a page with the given ID.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `id` | `str` |  | The ID of the page to check for. |


#### Returns

```
bool
```

Whether the graph contains a page with the given ID.

### `CategoryGraph.contains_page`

```python
wikicat.CategoryGraph.contains_page(self, page)
```

#### Description

Check whether the graph contains the given page.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `page` | `Page` |  | The page to check for. |


#### Returns

```
bool
```

Whether the graph contains the given page.

### `CategoryGraph.contains_title`

```python
wikicat.CategoryGraph.contains_title(self, title, namespace=None, standardize_title=True)
```

#### Description

Check whether the graph contains a page with the given title.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `title` | `str` |  | The title of the page to check for. |
| `namespace` | `str` | `None` | The namespace of the page to check for. If None, then the page can be in any namespace. |
| `standardize_title` | `bool` | `True` | Whether to standardize the title before checking for it. If True, then the title will be converted to lowercase and underscores will be replaced with spaces. |


#### Returns

```
bool
```

Whether the graph contains a page with the given title.

### `CategoryGraph.get_page_from_id`

```python
wikicat.CategoryGraph.get_page_from_id(self, id)
```

#### Description



#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `id` | `str` |  | The ID of the page. |


#### Returns

```
Page
```

The Page object with the given ID.

#### Examples

```python
>>> cg.get_page_from_id("7954681")
Page(id="7954681", title="Montreal", namespace="article")
```



### `CategoryGraph.get_page_from_title`

```python
wikicat.CategoryGraph.get_page_from_title(self, title, namespace, standardize_title=True)
```

#### Description



#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `title` | `str` |  | The title of the page. |
| `namespace` | `str` |  | The namespace of the page. Should be one of: "article", "category". |
| `standardize_title` |  | `True` | Whether to standardize the title. This is recommended, but can be disabled for performance reasons. |


#### Returns

```
Page
```

The page with the given title.

#### Examples

```python
>>> cg.get_page_from_title('Montreal', namespace='article')
Page(id="7954681", title="Montreal", namespace="article")

>>> cg.get_page_from_title('Montreal', namespace='category')
Page(id="808487", title="Montreal", namespace="category")
```



### `CategoryGraph.get_children`

```python
wikicat.CategoryGraph.get_children(self, page=None, id=None, title=None, return_as="page", include_hidden=False, standardize_title=True)
```

#### Description

Get the children of a category page.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `page` | `Page` | `None` | The page to get the parents of. If this is given, then id and title should not be given. |
| `id` | `Page` | `None` | The ID of the page to get the parents of. If this is given, then page and title should not be given. |
| `title` | `Page` | `None` | The title of the page to get the parents of. If this is given, then page and id should not be given. The namespace will be set to "category" because this is the only namespace that has children. |
| `return_as` | `str` | `"page"` | The format to return the parents in. One of: 'title', 'id', 'page'. |
| `include_hidden` | `bool` | `False` | Whether to include hidden categories in the results. |
| `standardize_title` | `bool` | `True` | Whether to standardize the title before searching for it. Only applies if title is given. |


#### Returns

```
list of str or Page
```

The parents of the page, in the format specified by return_as.

#### Examples

```python
>>> cg.get_children(id='808487', return_as='id')  # Montreal
['576883', '1456209', '1970548', '2302534', '3079470', ...]

>>> cg.get_children(title="Montreal", return_as='id')
['576883', '1456209', '1970548', '2302534', '3079470', ...]

>>> cg.get_children(title="Montreal", return_as='title')
['List_of_postal_codes_of_Canada:_H', 'Demographics_of_Montreal', ...]

>>> cg.get_children(title="Montreal", return_as='page')
[Page(id="576883", title="...", namespace="article"), ...]
```



### `CategoryGraph.get_parents`

```python
wikicat.CategoryGraph.get_parents(self, page=None, id=None, title=None, return_as="page", include_hidden=False, standardize_title=True, namespace=None)
```

#### Description

Get the parents of a page.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `page` | `Page` | `None` | The page to get the parents of. If this is given, then id and title should not be given. |
| `id` | `str` | `None` | The ID of the page to get the parents of. If this is given, then page and title should not be given. |
| `title` | `str` | `None` | The title of the page to get the parents of. If this is given, then page and id should not be given. The namespace will be set to "category" because this is the only namespace that has parents. |
| `return_as` | `str` | `"page"` | The format to return the parents in. One of: 'title', 'id', 'page'. |
| `include_hidden` | `bool` | `False` | Whether to include hidden categories in the results. |
| `standardize_title` | `bool` | `True` | Whether to standardize the title before searching for it. Only applies if title is given. |
| `namespace` | `str` | `None` | The namespace of the page. Only applies if title is given. If None, then the namespace will be inferred from the title. If the title is not found in either the "article" or "category" namespaces, then an error will be raised. |


#### Returns

```
list of str or Page
```

The parents of the page, in the format specified by return_as.

#### Examples

```python
>>> cg.get_parents(title="Computer", return_as='id')
["880368", "4583997", "27698964", "25645154"]

>>> cg.get_parents(title="Computer", return_as='title')
['Consumer_electronics',
'Computers',
'2000s_fads_and_trends',
'1990s_fads_and_trends']

>>> cg.get_parents(title="Computer", return_as="page")
[Page(id="880368", title="Consumer_electronics", namespace="category"),
Page(id="4583997", title="Computers", namespace="category"),
Page(id="27698964", title="2000s_fads_and_trends", namespace="category"),
Page(id="25645154", title="1990s_fads_and_trends", namespace="category")]
```



### `CategoryGraph.get_degree_counts`

```python
wikicat.CategoryGraph.get_degree_counts(self, include_hidden=False, use_cache=True)
```

#### Description

Get the degree counts for all pages.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `include_hidden` | `bool` | `False` | Whether to include hidden categories in the results. |
| `use_cache` | `bool` | `True` | Whether to use the cached degree counts. If False, then the degree counts will be recomputed. |


#### Returns

```
dict of {str
```

A dictionary mapping page IDs to their degree counts.

#### Examples

```python
>>> counts = cg.get_degree_counts()
>>> counts['808487']  # Montreal
10
```



### `CategoryGraph.rank_page_ids`

```python
wikicat.CategoryGraph.rank_page_ids(self, ids, mode="degree", ascending=False, max_pages=None, return_as="id")
```

#### Description

Rank a list of page IDs.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `ids` | `list[str]` |  | The page IDs to rank. |
| `mode` | `str` | `"degree"` | The mode to rank the pages in. Only "degree" is currently supported. |
| `ascending` | `bool` | `False` | Whether to rank the pages in ascending order. If False, then the pages will be ranked in descending order. |
| `max_pages` | `int` | `None` | The maximum number of pages to return. If None, then all pages will be returned. |
| `return_as` | `str` | `"id"` | The format to return the pages in. One of: 'title', 'id', 'page'. |


#### Returns

```
list of str or Page
```

The ranked pages, in the format specified by return_as.

#### Examples

```python
>>> page_ids = cg.get_parents(title="Computer", return_as='id')
>>> cg.rank_page_ids(page_ids)
['880368', '27698964', '25645154', '4583997']
```



### `CategoryGraph.rank_pages`

```python
wikicat.CategoryGraph.rank_pages(self, pages, mode="degree", ascending=False, max_pages=None)
```

#### Description

Rank a list of Page objects.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `pages` | `list[Page]` |  | The pages to rank. |
| `mode` | `str` | `"degree"` | The mode to rank the pages in. Only "degree" is currently supported. |
| `ascending` | `bool` | `False` | Whether to rank the pages in ascending order. If False, then the pages will be ranked in descending order, with the most important pages first (i.e. the pages with the highest degree counts). |
| `max_pages` | `int` | `None` | The maximum number of ranked pages to keep. |


#### Returns

```
list of str or Page
```

The ranked pages, in the format specified by return_as.

#### Examples

```python
>>> pages = cg.get_parents(title="Computer", return_as='page')
>>> cg.rank_pages(pages)
[Page(id="880368", title="Consumer_electronics", namespace="category"),
 Page(id="27698964", title="2000s_fads_and_trends", namespace="category"),
 Page(id="25645154", title="1990s_fads_and_trends", namespace="category"),
 Page(id="4583997", title="Computers", namespace="category")]
```



### `CategoryGraph.format_page_ids`

```python
wikicat.CategoryGraph.format_page_ids(self, ids, sep="; ", replace_underscores=True)
```

#### Description

Format a list of page IDs into a string that is human readable.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `ids` | `list[str]` |  | The page IDs to format. |
| `sep` | `str` | `"; "` | The separator to use between page titles. |
| `replace_underscores` | `bool` | `True` | Whether to replace underscores with spaces in the page titles. |


#### Returns

```
str
```

The formatted page IDs (in a human readable format).

#### Examples

```python
>>> page_ids = cg.get_parents(title="Computer", return_as='id')
>>> cg.format_page_ids(page_ids)
'Consumer electronics; Computers; 2000s fads and trends; 1990s fads and trends'
```



### `CategoryGraph.format_pages`

```python
wikicat.CategoryGraph.format_pages(pages, sep="; ", replace_underscores=True)
```

#### Description

This static method formats a list of `Page` objects into a string that is human readable.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `pages` | `list[Page]` |  | The pages to format. |
| `sep` | `str` | `"; "` | The separator to use between page titles. |
| `replace_underscores` | `bool` | `True` | Whether to replace underscores with spaces in the page titles. |


#### Returns

```
str
```

The formatted pages (in a human readable format).

#### Examples

```python
>>> pages = cg.get_parents(title="Computer", return_as='page')
>>> cg.format_pages(pages)
'Consumer electronics; Computers; 2000s fads and trends; 1990s fads and trends'
```



### `CategoryGraph.traverse`

```python
wikicat.CategoryGraph.traverse(self, page, direction, level=1, flatten=True, include_hidden=False, return_as="page")
```

#### Description

Traverse the parents of a page for a given level.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `page` | `Page` |  | The page to start traversing from. |
| `direction` | `str` |  | The direction to traverse. One of: 'parents', 'children'. |
| `level` | `int` | `1` | The number of levels to traverse. If 1, then only the parents/children of the page will be returned. If 2, then the parents/children of the parents/children of the page will be returned, and so on. |
| `flatten` | `bool` | `True` | Whether to flatten the results into a single list. If False, then the results will be a list of lists, where each list is the parents/children of the page at a given level. |
| `include_hidden` | `bool` | `False` | Whether to include hidden categories in the results. |
| `return_as` | `str` | `"page"` | The format to return the parents/children in. One of: 'title', 'id', 'page'. |


#### Returns

```
list of str or Page
```

A list of all traversed pages, in the format specified by return_as. If flatten=False,
then the results will be a list of lists, where each list.

### `CategoryGraph.get_top_level_categories`

```python
wikicat.CategoryGraph.get_top_level_categories(self, return_as="page")
```

