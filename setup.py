from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

with open('wikicat/viewer/requirements.txt') as f:
    viewer_requirements = f.read().splitlines()

with open('wikicat/processing/requirements.txt') as f:
    processing_requirements = f.read().splitlines()


setup(
    name='wikicat',
    version='0.0.1.dev0',
    author="Xing Han Lu, Aristides Milios",
    author_email="wikicat@xinghanlu.com",
    url='https://xhluca.github.io/wikicat',
    description='Toolkit for managing and navigating graphs of Wikipedia categories',
    long_description=long_description,
    packages=find_packages(
        include=["wikicat*"],
        exclude=['tests*', 'scripts*'],
    ),
    install_requires=[
        # dependencies here
    ],
    extras_require={
        'dev': ['black', 'wheel'],
        'viewer': viewer_requirements,
        'processing': processing_requirements,
    }
)