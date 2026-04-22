import tomllib
import unittest
from pathlib import Path

import divicast


class TestVersion(unittest.TestCase):
    def test_package_version_matches_project_metadata(self):
        pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
        pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

        self.assertEqual(divicast.__version__, pyproject["project"]["version"])
