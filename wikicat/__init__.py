from typing import Dict, List
import unicodedata

from .constants import ARTICLE, CATEGORY, TOP_LEVEL_CATEGORIES
from .version import __version__

ACCEPTED_NAMESPACES = ("article", "category")


def _namespace_to_code(namespace: str) -> str:
    """
    Converts a namespace to its corresponding code.
    If the namespace is already a code, it will be returned as-is.

    Parameters
    ----------
    namespace
        The namespace to convert.

    Returns
    -------
    str
        The code of the namespace.
    """
    if namespace == "article":
        return ARTICLE
    elif namespace == "category":
        return CATEGORY
    elif namespace in (ARTICLE, CATEGORY):
        return namespace
    else:
        raise ValueError(
            f"Invalid namespace={namespace}. Must be one of: {ACCEPTED_NAMESPACES}."
        )


def _code_to_namespace(code: str) -> str:
    """
    Converts a code to its corresponding namespace. If the code is already a
    namespace, it will be returned as-is.

    Parameters
    ----------
    code
        The code to convert. Must be one of: "article", "category".

    Returns
    -------
    str
        The namespace of the code.
    """
    code = str(code)

    if code == ARTICLE:
        return "article"
    elif code == CATEGORY:
        return "category"
    elif code in ACCEPTED_NAMESPACES:
        return code
    else:
        raise ValueError(f"Invalid code={code}")


def standardize(title: str, form: str = "NFC"):
    """
    Standardizes a title by replacing spaces with underscores and normalizing it to
    a given form following Unicode's normalization (defaults to NFC).

    Parameters
    ----------
    title
        The title to standardize.
    form
        The form to normalize the title to. Defaults to NFC.
    """
    return unicodedata.normalize(form, title.replace(" ", "_"))


class Page:
    def __init__(
        self, id: str, title: str, namespace: str, standardize_title: bool = True
    ):
        """
        Represents a Wikipedia page. It should be used alongside CategoryGraph to
        represent a page in the graph. You can also use it to find the URL of a page.

        Parameters
        ----------
        id
            The curid of the page.
        title
            The canonical title of the page.
        namespace
            The namespace of the page. Either "category" or "article".
        standardize_title
            Whether to standardize the title. If True, it will replace spaces with
            underscores and normalize the title to NFC form.

        Examples
        --------
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
        """
        self.id = str(id)
        self.title = title
        self.namespace = _code_to_namespace(namespace)

        if standardize_title:
            self.title = standardize(self.title)

        if self.namespace not in ACCEPTED_NAMESPACES:
            raise ValueError(
                f"Incorrect namespace={self.namespace}. Must be one of: {ACCEPTED_NAMESPACES}"
            )

    def __repr__(self):
        """
        Returns
        -------
        str
            The representation of the page.

        Examples
        --------
        >>> import wikicat as wc
        >>> page = wc.Page(id="7954681", title="Montreal", namespace="article")
        >>> str(page)
        """
        return (
            f'Page(id="{self.id}", title="{self.title}", namespace="{self.namespace}")'
        )

    def is_category(self) -> bool:
        """
        Returns
        -------
        bool
            Whether the page is a category.
        """
        return self.namespace == "category"

    def is_article(self) -> bool:
        """
        Returns
        -------
        bool
            Whether the page is an article.
        """
        return self.namespace == "article"

    def get_url(self, use_curid: bool = False) -> str:
        """
        Parameters
        ----------
        use_curid
            Whether to use the curid in the URL. If False, it will use the title.
            The curid is more stable, but the title is more human-readable.

        Returns
        -------
        str
            The URL of the page.
        """

        if use_curid:
            return f"https://en.wikipedia.org/?curid={self.id}"
        if self.is_category():
            return f"https://en.wikipedia.org/wiki/Category:{self.title}"
        elif self.is_article():
            return f"https://en.wikipedia.org/wiki/{self.title}"
        else:
            raise ValueError(f"Invalid namespace={self.namespace}")


class CategoryGraph:
    def __init__(self, graph_json: dict):
        """
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

        Parameters
        ----------
        graph_json
            The JSON object containing the category graph.

        Examples
        --------
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
        """
        self.id_to_title: dict = graph_json["id_to_title"]
        self.id_to_namespace: dict = graph_json["id_to_namespace"]
        self.title_to_id: dict = graph_json["title_to_id"]
        self.children_to_parents: dict = graph_json["children_to_parents"]
        self.parents_to_children: dict = graph_json["parents_to_children"]

        hidden_id = str(self.title_to_id[CATEGORY]["Hidden_categories"])
        self.hidden_categories = frozenset(self.parents_to_children[hidden_id].split())

    def __autoconvert_list_of_ids(self, ids, return_as):
        if return_as == "title":
            return [self.id_to_title[str(parent_id)] for parent_id in ids]
        elif return_as == "id":
            return ids
        elif return_as == "page":
            return [self.get_page_from_id(parent_id) for parent_id in ids]
        else:
            raise ValueError(
                f"return_as={return_as} is invalid. It should be one of: 'title', 'id', 'page'."
            )

    def _autodetect_id(
        self,
        page: Page,
        id: str,
        title: str,
        standardize_title: str,
        skip_error_checking: bool = False,
        namespace: str = None,
    ):
        if not skip_error_checking:
            total_not_none = sum(x is not None for x in [page, id, title])
            if total_not_none == 0 or total_not_none > 1:
                raise ValueError(
                    f"Must give exactly one of page, id, title. {total_not_none} were given."
                )

        if page is not None:
            return page.id

        elif id is not None:
            return str(id)

        elif title is not None:
            if standardize_title:
                title = standardize(title)

            if namespace is None:
                if title in self.title_to_id[ARTICLE]:
                    namespace = "article"
                elif title in self.title_to_id[CATEGORY]:
                    namespace = "category"

            page = self.get_page_from_title(
                title, standardize_title=False, namespace=namespace
            )

            return page.id

    @classmethod
    def read_json(cls, path: str):
        """
        Loads the category graph from a JSON file.

        Parameters
        ----------
        path
            The path to the JSON file containing the category graph.

        Examples
        --------
        >>> import wikicat as wc
        >>> graph = wc.CategoryGraph.read_json("category_graph_<yyyy>_<mm>_<dd>.json")

        Notes
        -----
        This method uses orjson if it is available, otherwise it uses the standard json module.
        You can install orjson with `pip install orjson`.

        """
        from importlib.util import find_spec

        if find_spec("orjson") is not None:
            import orjson

            with open(path, "rb") as f:
                graph_json = orjson.loads(f.read())

        else:
            import json

            with open(path) as f:
                graph_json = json.load(f)

        return cls(graph_json)

    def remove_hidden_ids(self, ids: "list[str]") -> "list[str]":
        """
        Parameters
        ----------
        ids
            A list of IDs to remove hidden categories from.

        Returns
        -------
        list of str
            The list of IDs with hidden categories removed.
        """
        return [id_ for id_ in ids if id_ not in self.hidden_categories]

    def contains_id(self, id: str) -> bool:
        """
        Check whether the graph contains a page with the given ID.

        Parameters
        ----------
        id
            The ID of the page to check for.

        Returns
        -------
        bool
            Whether the graph contains a page with the given ID.
        """
        return id in self.id_to_title

    def contains_page(self, page: Page) -> bool:
        """
        Check whether the graph contains the given page.

        Parameters
        ----------
        page
            The page to check for.

        Returns
        -------
        bool
            Whether the graph contains the given page.
        """
        return self.contains_id(page.id)

    def contains_title(
        self, title: str, namespace: str = None, standardize_title: bool = True
    ) -> bool:
        """
        Check whether the graph contains a page with the given title.

        Parameters
        ----------
        title
            The title of the page to check for.
        namespace
            The namespace of the page to check for. If None, then the page can be in any namespace.
        standardize_title
            Whether to standardize the title before checking for it. If True, then the title will be
            converted to lowercase and underscores will be replaced with spaces.

        Returns
        -------
        bool
            Whether the graph contains a page with the given title.
        """
        if standardize_title:
            title = standardize(title)

        if namespace is not None:
            namespace_code = _namespace_to_code(namespace)
            return title in self.title_to_id[namespace_code]
        else:
            for namespace_code in self.title_to_id:
                if title in self.title_to_id[namespace_code]:
                    return True
            return False

    def get_page_from_id(self, id: str) -> Page:
        """
        Parameters
        ----------
        id
            The ID of the page.

        Returns
        -------
        Page
            The Page object with the given ID.

        Examples
        --------
        >>> cg.get_page_from_id("7954681")
        Page(id="7954681", title="Montreal", namespace="article")
        """
        id = str(id)
        if id not in self.id_to_title:
            raise ValueError(f"Page with ID={id} was not found in the graph.")
        if id not in self.id_to_namespace:
            raise ValueError(f"Could not determine the type of Page with ID={id}.")

        return Page(
            id=id, title=self.id_to_title[id], namespace=self.id_to_namespace[id]
        )

    def get_page_from_title(
        self, title: str, namespace: str, standardize_title=True
    ) -> Page:
        """
        Parameters
        ----------
        title
            The title of the page.
        namespace
            The namespace of the page. Should be one of: "article", "category".
        standardize_title
            Whether to standardize the title. This is recommended, but can be disabled
            for performance reasons.

        Returns
        -------
        Page
            The page with the given title.

        Examples
        --------
        >>> cg.get_page_from_title('Montreal', namespace='article')
        Page(id="7954681", title="Montreal", namespace="article")

        >>> cg.get_page_from_title('Montreal', namespace='category')
        Page(id="808487", title="Montreal", namespace="category")
        """
        if standardize_title:
            title = standardize(title)

        namespace_code = _namespace_to_code(namespace)

        if namespace_code not in self.title_to_id:
            raise ValueError(
                f"namespace={namespace} is invalid. It should be one of {ACCEPTED_NAMESPACES}."
            )

        if title not in self.title_to_id[namespace_code]:
            raise ValueError(f"Title {title} not found in graph.")
        id = self.title_to_id[namespace_code][title]
        return self.get_page_from_id(id)

    def get_children(
        self,
        page: Page = None,
        id: Page = None,
        title: Page = None,
        return_as: str = "page",
        include_hidden: bool = False,
        standardize_title: bool = True,
    ):
        """
        Get the children of a category page.

        Parameters
        ----------
        page
            The page to get the parents of. If this is given, then id and title
            should not be given.
        id
            The ID of the page to get the parents of. If this is given, then page
            and title should not be given.
        title
            The title of the page to get the parents of. If this is given, then page
            and id should not be given. The namespace will be set to "category" because
            this is the only namespace that has children.
        return_as
            The format to return the parents in. One of: 'title', 'id', 'page'.
        include_hidden
            Whether to include hidden categories in the results.
        standardize_title
            Whether to standardize the title before searching for it. Only applies
            if title is given.

        Returns
        -------
        list of str or Page
            The parents of the page, in the format specified by return_as.

        Examples
        --------
        >>> cg.get_children(id='808487', return_as='id')  # Montreal
        ['576883', '1456209', '1970548', '2302534', '3079470', ...]

        >>> cg.get_children(title="Montreal", return_as='id')
        ['576883', '1456209', '1970548', '2302534', '3079470', ...]

        >>> cg.get_children(title="Montreal", return_as='title')
        ['List_of_postal_codes_of_Canada:_H', 'Demographics_of_Montreal', ...]

        >>> cg.get_children(title="Montreal", return_as='page')
        [Page(id="576883", title="...", namespace="article"), ...]
        """
        page_id = self._autodetect_id(
            page, id, title, standardize_title=standardize_title, namespace="category"
        )
        parent_ids = self.parents_to_children.get(page_id, "").split()

        if not include_hidden:
            parent_ids = self.remove_hidden_ids(parent_ids)

        return self.__autoconvert_list_of_ids(parent_ids, return_as)

    def get_parents(
        self,
        page: Page = None,
        id: str = None,
        title: str = None,
        return_as: str = "page",
        include_hidden: bool = False,
        standardize_title: bool = True,
        namespace: str = None,
    ):
        """
        Get the parents of a page.

        Parameters
        ----------
        page: Page, optional
            The page to get the parents of. If this is given, then id and title
            should not be given.
        id: str, optional
            The ID of the page to get the parents of. If this is given, then page
            and title should not be given.
        title: str, optional
            The title of the page to get the parents of. If this is given, then page
            and id should not be given. The namespace will be set to "category" because
            this is the only namespace that has parents.
        return_as: str, default "page"
            The format to return the parents in. One of: 'title', 'id', 'page'.
        include_hidden: bool, default False
            Whether to include hidden categories in the results.
        standardize_title: bool, default True
            Whether to standardize the title before searching for it. Only applies
            if title is given.
        namespace: str, default None
            The namespace of the page. Only applies if title is given. If None, then
            the namespace will be inferred from the title. If the title is not found
            in either the "article" or "category" namespaces, then an error will be
            raised.

        Returns
        -------
        list of str or Page
            The parents of the page, in the format specified by return_as.

        Examples
        --------
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
        """

        page_id = self._autodetect_id(
            page, id, title, standardize_title=standardize_title, namespace=namespace
        )
        child_ids = self.children_to_parents.get(page_id, "").split()

        if not include_hidden:
            child_ids = self.remove_hidden_ids(child_ids)

        return self.__autoconvert_list_of_ids(child_ids, return_as)

    def get_degree_counts(
        self, include_hidden: bool = False, use_cache: bool = True
    ) -> Dict[str, int]:
        """
        Get the degree counts for all pages.

        Parameters
        ----------
        include_hidden
            Whether to include hidden categories in the results.
        use_cache
            Whether to use the cached degree counts. If False, then the degree counts
            will be recomputed.

        Returns
        -------
        dict of {str: int}
            A dictionary mapping page IDs to their degree counts.

        Examples
        --------
        >>> counts = cg.get_degree_counts()
        >>> counts['808487']  # Montreal
        10
        """
        # Check if cached
        if use_cache and hasattr(self, "degree_counts"):
            return self.degree_counts

        # if not cached, compute and cache
        self.degree_counts = {}

        for id_ in self.id_to_title:
            parents = self.children_to_parents.get(id_, "").split()
            children = self.parents_to_children.get(id_, "").split()

            if not include_hidden:
                parents = self.remove_hidden_ids(parents)
                children = self.remove_hidden_ids(children)

            num_children = len(children)
            num_parents = len(parents)

            self.degree_counts[id_] = num_parents + num_children

        return self.degree_counts

    def rank_page_ids(
        self,
        ids: "list[str]",
        mode: str = "degree",
        ascending: bool = False,
        max_pages: int = None,
        return_as: str = "id",
    ) -> list:
        """
        Rank a list of page IDs.

        Parameters
        ----------
        ids
            The page IDs to rank.
        mode
            The mode to rank the pages in. Only "degree" is currently supported.
        ascending
            Whether to rank the pages in ascending order. If False, then the pages
            will be ranked in descending order.
        max_pages
            The maximum number of pages to return. If None, then all pages will be
            returned.
        return_as
            The format to return the pages in. One of: 'title', 'id', 'page'.

        Returns
        -------
        list of str or Page
            The ranked pages, in the format specified by return_as.

        Examples
        --------
        >>> page_ids = cg.get_parents(title="Computer", return_as='id')
        >>> cg.rank_page_ids(page_ids)
        ['880368', '27698964', '25645154', '4583997']
        """

        if mode != "degree":
            raise ValueError(
                f"mode={mode} is invalid. Only 'degree' is currently supported."
            )

        counts = self.get_degree_counts()
        ranked = sorted(ids, key=lambda page_id: counts[page_id], reverse=not ascending)
        if max_pages is not None:
            ranked = ranked[:max_pages]
        return self.__autoconvert_list_of_ids(ranked, return_as)

    def rank_pages(
        self,
        pages: "list[Page]",
        mode: str = "degree",
        ascending: bool = False,
        max_pages: int = None,
    ) -> "list[Page]":
        """
        Rank a list of Page objects.

        Parameters
        ----------
        pages
            The pages to rank.
        mode
            The mode to rank the pages in. Only "degree" is currently supported.
        ascending
            Whether to rank the pages in ascending order. If False, then the pages
            will be ranked in descending order, with the most important pages first
            (i.e. the pages with the highest degree counts).
        max_pages
            The maximum number of ranked pages to keep.

        Returns
        -------
        list of str or Page
            The ranked pages, in the format specified by return_as.

        Examples
        --------
        >>> pages = cg.get_parents(title="Computer", return_as='page')
        >>> cg.rank_pages(pages)
        [Page(id="880368", title="Consumer_electronics", namespace="category"),
         Page(id="27698964", title="2000s_fads_and_trends", namespace="category"),
         Page(id="25645154", title="1990s_fads_and_trends", namespace="category"),
         Page(id="4583997", title="Computers", namespace="category")]
        """
        ranked_ids = self.rank_page_ids(
            [page.id for page in pages],
            mode=mode,
            ascending=ascending,
            max_pages=max_pages,
        )

        return [self.get_page_from_id(page_id) for page_id in ranked_ids]

    def format_page_ids(
        self, ids: "list[str]", sep: str = "; ", replace_underscores: bool = True
    ) -> str:
        """
        Format a list of page IDs into a string that is human readable.

        Parameters
        ----------
        ids
            The page IDs to format.
        sep
            The separator to use between page titles.
        replace_underscores
            Whether to replace underscores with spaces in the page titles.

        Returns
        -------
        str
            The formatted page IDs (in a human readable format).

        Examples
        --------
        >>> page_ids = cg.get_parents(title="Computer", return_as='id')
        >>> cg.format_page_ids(page_ids)
        'Consumer electronics; Computers; 2000s fads and trends; 1990s fads and trends'
        """
        pages = [self.get_page_from_id(id_) for id_ in ids]
        return self.format_pages(
            pages, sep=sep, replace_underscores=replace_underscores
        )

    @staticmethod
    def format_pages(
        pages: "list[Page]", sep: str = "; ", replace_underscores: bool = True
    ) -> str:
        """
        This static method formats a list of `Page` objects into a string that is human readable.

        Parameters
        ----------
        pages
            The pages to format.
        sep
            The separator to use between page titles.
        replace_underscores
            Whether to replace underscores with spaces in the page titles.

        Returns
        -------
        str
            The formatted pages (in a human readable format).

        Examples
        --------
        >>> pages = cg.get_parents(title="Computer", return_as='page')
        >>> cg.format_pages(pages)
        'Consumer electronics; Computers; 2000s fads and trends; 1990s fads and trends'
        """
        titles = [page.title for page in pages]

        if replace_underscores:
            titles = [title.replace("_", " ") for title in titles]
        return sep.join(titles)

    def traverse(
        self,
        page: Page,
        direction: str,
        level: int = 1,
        flatten: bool = True,
        include_hidden: bool = False,
        return_as: str = "page",
    ) -> list:
        """
        Traverse the parents of a page for a given level.

        Parameters
        ----------
        page: Page
            The page to start traversing from.
        direction: str
            The direction to traverse. One of: 'parents', 'children'.
        level: int
            The number of levels to traverse. If 1, then only the parents/children of the page
            will be returned. If 2, then the parents/children of the parents/children of the page will
            be returned, and so on.
        flatten: bool
            Whether to flatten the results into a single list. If False, then the
            results will be a list of lists, where each list is the parents/children of the
            page at a given level.
        include_hidden: bool
            Whether to include hidden categories in the results.
        return_as: str, default "page"
            The format to return the parents/children in. One of: 'title', 'id', 'page'.

        Returns
        -------
        list of str or Page
            A list of all traversed pages, in the format specified by return_as. If flatten=False,
            then the results will be a list of lists, where each list.
        """
        if direction == "parents":
            get_neighbors = self.get_parents
        elif direction == "children":
            get_neighbors = self.get_children
        else:
            raise ValueError(
                f"direction={direction} is invalid. Must be one of: 'parents', 'children'."
            )

        lvl_page_ids = get_neighbors(
            page=page, include_hidden=include_hidden, return_as="id"
        )
        visited_ids = set()
        all_page_ids = []

        for _ in range(level):
            if not flatten:
                all_page_ids.append([])
            next_lvl_page_ids = []

            for page_id in lvl_page_ids:
                if page_id not in visited_ids:
                    if flatten:
                        all_page_ids.append(page_id)
                    else:
                        all_page_ids[-1].append(page_id)

                    neighbor_ids = get_neighbors(
                        id=page_id, include_hidden=include_hidden, return_as="id"
                    )
                    next_lvl_page_ids.extend(neighbor_ids)
                    visited_ids.add(page_id)
            lvl_page_ids = next_lvl_page_ids

        if flatten:
            return self.__autoconvert_list_of_ids(all_page_ids, return_as)
        else:
            return [
                self.__autoconvert_list_of_ids(page_ids, return_as)
                for page_ids in all_page_ids
            ]

    def get_top_level_categories(self, return_as="page"):
        categories = [
            self.get_page_from_title(title, namespace="category").id
            for title in TOP_LEVEL_CATEGORIES
        ]

        return self.__autoconvert_list_of_ids(categories, return_as)
