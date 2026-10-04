import unittest
from copy import deepcopy

from reybill_core.branding import DESKTOP_ORDER, REYBILL_DESKTOP_ICON
from reybill_core.desktop import order_layout


class DesktopOrderTest(unittest.TestCase):
	def test_layout_preserves_navigation_artwork_and_removal(self):
		icons = [
			{
				"name": name,
				"idx": 100,
				"hidden": index % 2,
				"parent_icon": "ERPNext",
				"icon": "original",
				"url": "/desk/original",
				"roles": ["Desk User"],
			}
			for index, name in enumerate((*DESKTOP_ORDER, "ERPNext", "Unrelated"))
		]
		before = deepcopy(icons)
		order_layout(icons)
		for original, current in zip(before, icons, strict=True):
			expected = dict(original)
			if original["name"] in DESKTOP_ORDER:
				expected["idx"] = DESKTOP_ORDER.index(original["name"])
			if original["name"] == "ERPNext":
				expected["logo_url"] = REYBILL_DESKTOP_ICON
			self.assertEqual(current, expected)
		first = deepcopy(icons)
		order_layout(icons)
		self.assertEqual(icons, first)
