from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

with open('wikicat/viewer/requirements.txt') as f:
    viewer_requirements = f.read().splitlines()

with open('wikicat/processing/requirements.txt') as f:
    processing_requirements = f.read().splitlines()


setup(
    name='simple-pip-example',
    version='0.0.1.dev0',
    author="Xing Han Lu",
    author_email="wikicat@xinghanlu.com",
    url='xhluca.github.io/wikicat',
    description='Toolkit for managing and navigating graphs of Wikipedia categories',
    packages=find_packages(
        include=["wikicat*"],
        exclude=['tests*'],
    ),
    install_requires=[
        # dependencies here
    ],
    extras_require={
        # For special installation, e.g. pip install simple-pip-example[dev]
        'dev': ['black'],
        'viewer': viewer_requirements,
        'processing': processing_requirements,
    }
)