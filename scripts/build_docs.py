import pkgutil
import inspect
import ast
from textwrap import dedent

def get_default(obj):
    if isinstance(obj, ast.Num):
        return obj.n
    if isinstance(obj, ast.Str):
        return obj.s
    if isinstance(obj, ast.NameConstant):
        return obj.value

def line_is_delim(i, lines, delim="-"):
    if i == len(lines):
        return False
    return lines[i].startswith(delim) and all(c == delim for c in lines[i])

def extract_information(node: ast.FunctionDef):
    docstring = ast.get_docstring(node, clean=True)

    args = [
        {"name": arg.arg, "type": getattr(arg.annotation, "id", None)}
        for arg in node.args.args
    ]

    defaults = [get_default(arg) for arg in node.args.defaults]
    defaults = [None] * (len(args) - len(defaults)) + defaults

    for arg, default in zip(args, defaults):
        arg["default"] = default
    
    return {
        "docstring": docstring,
        "args": args
    }

def parse_docstring(docstring: str):
    """
    This parses a docstring formatted using the pandas docstring format.
    """
    lines = docstring.splitlines()
    key = "Description"
    content = {key: []}

    for i, line in enumerate(lines):
        if line_is_delim(i+1, lines):
            key = line
            content[key] = []
        elif line_is_delim(i, lines):
            continue
        
        content[key].append(line)
    
    return content

def format_docstring_params(lines: 'list[str]'):
    """
    This formats the parameter section of the docstring according to the pandas docstring format.
    """
    params = {}
    key = None
    type_name = None
    default = None

    for line in lines[1:]:
        if line == "":
            continue
        
        if line.startswith(' '):
            params[key]['description'].append(line)
        
        else:
            if ":" in line:
                varname, rest = line.split(':', maxsplit=1)
                rest = rest.strip()
                if "," in rest.strip():
                    type_name, default = rest.split(',', maxsplit=1)
                    type_name = type_name.strip()
                    default = default.replace("default", "").strip()

                else:
                    if rest.startswith("optional"):
                        type_name = None
                        default = None
                    elif rest.startswith("default"):
                        type_name = None
                        default = rest.replace("default", "").strip()
                    else:
                        type_name = rest
                        default = None

            else:
                varname = line
            
            varname = varname.strip()

            key = varname
            
            params[key] = {'type': type_name, 'default': default, 'description': []}
    
    for key, value in params.items():
        params[key]['description'] = dedent("\n".join(value['description']))

    return params

            


    


modules = list(pkgutil.walk_packages(["wikicat"]))

mod = modules[1]
mod.module_finder.find_module(mod.name)


with open("wikicat/__init__.py", "r") as f:
    tree = ast.parse(f.read())

nodes = {}
content = {}

for node in tree.body:
    if isinstance(node, ast.FunctionDef):
        name = node.name
        content[name] = extract_information(node)
        nodes[name] = node

    if isinstance(node, ast.ClassDef):
        cls_ = node
        for node in cls_.body:
            if node.name == "__init__":
                name = cls_.name
            else:
                name = f"{cls_.name}.{node.name}"
            
            content[name] = extract_information(node)
            nodes[name] = node


parsed = parse_docstring(content['CategoryGraph.traverse']['docstring'])