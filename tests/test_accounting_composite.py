"""Check the generated asset's external visual requirements, without site writes."""

import unittest
from pathlib import Path

from PIL import Image

ASSET = (
	Path(__file__).resolve().parents[1]
	/ "reybill_core/public/images/branding/module-icons/reybill-icon-accounting.png"
)


class AccountingCompositeTest(unittest.TestCase):
	def test_one_family_frame_four_separated_glyphs_and_no_vendor_blue(self):
		image = Image.open(ASSET).convert("RGBA")
		self.assertEqual(image.size, (512, 512))
		self.assertEqual(image.getpixel((0, 0))[3], 0)
		for point in ((256, 36), (36, 256)):
			for channel, approved in zip(image.getpixel(point)[:3], (241, 216, 226), strict=True):
				self.assertLessEqual(abs(channel - approved), 2)
		# The visible frame uses the established 36px margin / 440px tile.
		visible = image.getchannel("A").point(lambda alpha: 255 if alpha >= 128 else 0)
		self.assertEqual(visible.getbbox(), (36, 36, 476, 476))
		# Both gutters must be clear of glyphs or nested miniature tile outlines.
		for n in range(85, 428):
			self.assertGreater(image.getpixel((256, n))[1], 235)
			self.assertGreater(image.getpixel((n, 256))[1], 235)
		for left, top in ((100, 100), (264, 100), (100, 264), (264, 264)):
			box = image.crop((left, top, left + 150, top + 150))
			pixels = list((getattr(box, "get_flattened_data", None) or box.getdata)())
			self.assertGreater(sum(green < 10 and alpha > 200 for _, green, _, alpha in pixels), 3000)
			self.assertFalse(any(blue > red + 40 and alpha > 100 for red, _, blue, alpha in pixels))
