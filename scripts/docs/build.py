import glob
import json
import pkgutil
import inspect
import ast
from textwrap import dedent

from pathlib import Path


def get_default(obj):
    if isinstance(obj, ast.Num):
        return obj.n
    if isinstance(obj, ast.Str):
        return f'"{obj.s}"'
    if isinstance(obj, ast.NameConstant):
        return obj.value


def line_is_delim(i, lines, delim="-"):
    if i == len(lines):
        return False
    return lines[i].startswith(delim) and all(c == delim for c in lines[i])


def extract_content_from_ast(node: ast.FunctionDef, remove_self=False):
    """
    This extracts the information from a function or method definition node in the AST.

    It returns a dictionary with the following keys:
    - docstring: the docstring of the function/method
    - args: a dictionary where the keys are the names of the arguments and the values are:
        - name: the name of the argument
        - type: the type of the argument
        - default: the default value of the argument
    """
    docstring = ast.get_docstring(node, clean=True)

    arg_list = [
        {"name": arg.arg, "type": getattr(arg.annotation, "id", None)}
        for arg in node.args.args
    ]

    defaults = [get_default(arg) for arg in node.args.defaults]
    defaults = [None] * (len(arg_list) - len(defaults)) + defaults

    for arg, default in zip(arg_list, defaults):
        arg["default"] = default

    args = {arg["name"]: arg for arg in arg_list}

    if remove_self:
        args.pop("self")

    return {"docstring": docstring, "args": args}


def parse_docstring(content: str, parse_params=True, parse_returns=True):
    """
    This parses a docstring formatted using the pandas docstring format.
    """
    lines = content.splitlines()
    key = "Description"
    content = {key: []}

    for i, line in enumerate(lines):
        if line_is_delim(i + 1, lines):
            key = line
            content[key] = []
        elif not line_is_delim(i, lines):
            content[key].append(line)

    if parse_params and "Parameters" in content:
        content["Parameters"] = parse_docstring_params(content["Parameters"])

    if parse_returns and "Returns" in content:
        content["Returns"] = parse_docstring_params(content["Returns"])

    return content


def infer_default_in_description(line: str):
    """
    This function tries to infer the default value from the description
    of a parameter.
    """
    line = line.replace(",optional", ", optional").replace(",default", ", default")
    default = None

    if line.endswith(", optional"):
        line = line.replace(", optional", "").strip()

    elif "default" in line:
        line, default = line.split(", default", maxsplit=1)
        line = line.strip()
        default = default.strip()

    return line, default


def parse_docstring_params(lines: "list[str]"):
    """
    This parses a docstring formatted using the pandas docstring format.
    """
    params = {}
    varname = None

    for line in lines:
        if line == "":
            continue

        if line.startswith(" "):
            if varname is None:
                raise ValueError("Unexpected line in docstring: " + line)
            params[varname]["description"].append(line)

        else:
            if ":" in line:
                varname, line = line.split(":", maxsplit=1)
                varname = varname.strip()
                line = line.strip()
                type_name, default = infer_default_in_description(line)

            else:
                type_name = None
                varname, default = infer_default_in_description(line)

            params[varname] = {"type": type_name, "default": default, "description": []}

    for key, value in params.items():
        params[key]["description"] = dedent("\n".join(value["description"]))

    return params


def param_dict_to_markdown_table(params: dict, args: dict):
    """
    This converts the output of parse_docstring_params to a markdown table.
    """
    markdown = ""
    markdown += "| Name | Type | Default | Description |\n"
    markdown += "| ---- | ---- | ------- | ----------- |\n"

    for varname, p in params.items():
        type_ = p["type"]
        default = p["default"]
        description = p["description"].replace("\n", " ")

        sig_type_ = args[varname]["type"]
        sig_default = args[varname]["default"]

        if type_ is None and sig_type_ is not None:
            type_ = sig_type_
        elif sig_type_ is not None and type_ != sig_type_:
            type_ += f" ({sig_type_})"

        if default is None and sig_default is not None:
            default = sig_default
        elif sig_default is not None and default != sig_default:
            default += f" ({sig_default})"

        if type_ is None:
            type_ = ""
        else:
            type_ = f"`{type_}`"

        if default is None:
            default = ""
        else:
            default = f"`{default}`"

        markdown += f"| `{varname}` | {type_} | {default} | {description} |\n"

    return markdown


def md_header(text, level):
    return "#" * level + f" {text}\n\n"


def signature_list_from_args(args):
    signature = []
    for name in args:
        if args[name]["default"] is not None:
            signature.append(f"{name}={args[name]['default']}")
        else:
            signature.append(f"{name}")
    return signature


def format_docstring_to_markdown(
    node_content: dict, node_name, module_prefix=None, level=2
):
    """
    Formats the content of a node extracted from extract_information
    with the docstring parsed by parse_docstring.
    """

    if node_name is None:
        node_name = node_content["name"]

    if module_prefix is not None and module_prefix != "":
        node_name = module_prefix + "." + node_name

    doc_str_dict = node_content["docstring"]
    args = node_content["args"]
    signature_lst = signature_list_from_args(args)

    markdown = md_header(f"`{node_name}`", level=level)
    markdown += f"```python\n{node_name}({', '.join(signature_lst)})\n```\n\n"

    if doc_str_dict is None:
        return markdown

    for key, value in doc_str_dict.items():
        markdown += md_header(key, level=max(4, level + 1))

        if key == "Parameters":
            markdown += param_dict_to_markdown_table(value, args)

        elif key == "Returns":
            if len(value) == 1:
                k, v = list(value.items())[0]
                markdown += f"```\n{k}\n```\n\n{v['description']}"
            else:
                markdown += param_dict_to_markdown_table(value)

        elif key == "Examples":
            markdown += "```python\n"
            markdown += "\n".join(value)
            markdown += "\n```\n\n"

        elif isinstance(value, str):
            markdown += value

        elif isinstance(value, list):
            markdown += "\n".join(value)

        else:
            raise ValueError(f"Unexpected value for key {key}: {value}")

        markdown += "\n\n"

    return markdown


def format_module_from_content(node_contents: dict, module_prefix: str = None):
    formatted_page = ""

    if module_prefix is not None:
        formatted_page += md_header(f"Reference for module `{module_prefix}`", level=1)
    
    if len(node_contents) == 0:
        formatted_page += "No docstring found in module.\n\n"

    for name, node_content in node_contents.items():
        if node_content["docstring"] is not None:
            node_content["docstring"] = parse_docstring(node_content["docstring"])

        if "class" in node_content and node_content["class"] != name:
            level = 3
        else:
            level = 2

        formatted = format_docstring_to_markdown(
            node_content, node_name=name, module_prefix=module_prefix, level=level
        )
        formatted_page += formatted

    return formatted_page


def parse_content_from_ast(tree: ast.Module) -> dict:
    node_contents = {}

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            name = node.name
            if node.name.startswith("_"):
                continue

            node_contents[name] = extract_content_from_ast(node)

        if isinstance(node, ast.ClassDef):
            cls_ = node
            for node in cls_.body:
                if not isinstance(node, ast.FunctionDef):
                    continue
                
                if node.name.startswith("_") and not node.name.endswith("__"):
                    continue

                if node.name == "__init__":
                    name = cls_.name
                    remove_self = True
                else:
                    name = f"{cls_.name}.{node.name}"
                    remove_self = False

                node_contents[name] = extract_content_from_ast(node, remove_self=remove_self)
                node_contents[name]["class"] = cls_.name

    return node_contents


with open("scripts/docs/render_paths.json", "r") as f:
    render_paths = json.load(f)

for target, source_lst in render_paths.items():
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)

    doc_page = ""

    source_lst_globed = []
    for s in source_lst:
        source_lst_globed.extend(glob.glob(s))
    source_lst_globed = sorted(source_lst_globed)
    
    print("Target doc file:", target)
    print("Parsing python files:", source_lst_globed)
    print('-'*50)

    for source in source_lst_globed:
        source = Path(source)
        with open(source, "r") as f:
            tree = ast.parse(f.read())

        node_contents = parse_content_from_ast(tree)
        module_prefix = ".".join(source.parts).replace(".py", "").replace(".__init__", "")
        doc_page_part = format_module_from_content(
            node_contents, module_prefix=module_prefix
        )
        doc_page += doc_page_part

    with open(target, "w") as f:
        f.write(doc_page)

# with open("wikicat/__init__.py", "r") as f:
#     tree = ast.parse(f.read())

# node_contents = parse_content_from_ast(tree)
# doc_page = format_module_from_content(node_contents)

# doc_dir = Path("docs")
# doc_dir.mkdir(exist_ok=True)

# with open(doc_dir / "wikicat.md", "w") as f:
#     f.write(doc_page)

# name = "CategoryGraph.traverse"
# node_content = node_contents[name]

# node_content["docstring"] = parse_docstring(node_content["docstring"])
# formatted = format_docstring_to_markdown(node_content, node_name=name)
