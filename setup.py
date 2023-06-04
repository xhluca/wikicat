import ast
from setuptools import setup, find_packages


def get_version(path, var="__version__"):
    with open(path) as f:
        body = ast.parse(f.read()).body

    for node in body:
        if isinstance(node, ast.Assign) and node.targets[0].id == var:
            version = node.value.s
            return version

    return None


with open("README.md", "r") as f:
    long_description = f.read()

with open("wikicat/viewer/requirements.txt") as f:
    viewer_requirements = f.read().splitlines()

with open("wikicat/processing/requirements.txt") as f:
    processing_requirements = f.read().splitlines()

version = get_version("wikicat/version.py")


setup(
    name="wikicat",
    version=version,
    author="Xing Han Lu, Aristides Milios",
    author_email="wikicat@xinghanlu.com",
    url="https://xhluca.github.io/wikicat",
    description="Toolkit for managing and navigating graphs of Wikipedia categories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    python_requires=">=3.7",
    packages=find_packages(
        include=["wikicat*"],
        exclude=["tests*", "scripts*"],
    ),
    install_requires=[
        # dependencies here
    ],
    extras_require={
        "dev": ["black==23.*", "wheel"],
        "viewer": viewer_requirements,
        "processing": processing_requirements,
    },
)
