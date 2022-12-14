import ast
import json
import glob
from pathlib import Path
import unittest

from scripts.docs import build as doc_build

class TestDocs(unittest.TestCase):
    def test_build(self):
        with open("scripts/docs/render_paths.json", "r") as f:
            render_paths = json.load(f)
        
        for target, source_lst in render_paths.items():
            target = Path(target)
            sources_globed = doc_build.build_globed_sources(source_lst)
            
            doc_page = doc_build.build_docs(sources_globed)
            error_msg = """
            The generated documentation page does not match the expected output.
            Please run `python scripts/docs.py` to update the documentation.
            """

            with open(target, "r") as f:
                self.assertEqual(f.read(), doc_page, error_msg)