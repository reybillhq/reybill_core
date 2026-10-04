import unittest
from unittest.mock import patch

from reybill_core import __version__
from reybill_core.branding import branding_asset_url


class BrandingAssetTest(unittest.TestCase):
	def test_unavailable_asset_does_not_block_page_rendering(self):
		with patch("reybill_core.branding.Path.read_bytes", side_effect=FileNotFoundError):
			self.assertEqual(
				branding_asset_url("images/branding/missing.svg"),
				f"/assets/reybill_core/images/branding/missing.svg?v={__version__}",
			)

	def test_stable_url_changes_with_release_or_asset_content(self):
		path = "images/branding/Reybill_desk_icon.png"
		with patch("reybill_core.branding.Path.read_bytes", return_value=b"original"):
			original = branding_asset_url(path)
			self.assertEqual(branding_asset_url(path), original)
			self.assertIn(f"?v={__version__}&h=", original)
			with patch("reybill_core.branding.__version__", "next-release"):
				self.assertNotEqual(branding_asset_url(path), original)
		with patch("reybill_core.branding.Path.read_bytes", return_value=b"replacement"):
			self.assertNotEqual(branding_asset_url(path), original)
