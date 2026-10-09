"""Cloud compatibility boundaries; no installation or site access."""

import tomllib
import unittest
from pathlib import Path

from packaging.specifiers import SpecifierSet


class FrappeCompatibilityTest(unittest.TestCase):
	def test_supported_frappe_version_range(self):
		path = Path(__file__).resolve().parents[1] / "pyproject.toml"
		with path.open("rb") as stream:
			metadata = tomllib.load(stream)
		supported = SpecifierSet(metadata["tool"]["bench"]["frappe-dependencies"]["frappe"])
		for version, expected in (
			("16.0.0-dev", True),
			("16.0.0", True),
			("16.36.1", True),
			("16.37.0", True),
			("16.99.0", True),
			("15.99.0", False),
			("17.0.0", False),
			("17.1.0", False),
		):
			with self.subTest(version=version):
				self.assertEqual(supported.contains(version), expected)
