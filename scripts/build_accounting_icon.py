"""Offline composition of the approved desktop Accounting glyphs; never edit inputs.

Native desktop positions were measured with the ReyBill adapter omitted. The
six-column clipped grid exposes indices 0, 1, 6, 7. Mobile's native two-column
variation exposes different children; this asset preserves the desktop four.
PNG inputs are raster artwork, so the honest output is PNG, not a traced SVG.
"""

import argparse
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "reybill_core/public/images/branding/module-icons"
COMPONENTS = ("invoicing", "payments", "budget", "share-management")
CANVAS = 512
TILE = 440
# Native miniature image box: 16px in a 54px folder. Measured cell pitch:
# 18px grid track + 2.09375px resolved gap. Keep those proportions, centered.
GLYPH_BOX = round(TILE * 16 / 54)
PITCH = TILE * 20.09375 / 54


def foreground(source):
	"""Isolate existing Burgundy coverage, excluding the supplied tile/background.

	Unmatte against the source's pale surface; preserve opaque source glyph colors
	and silhouettes. No tracing, path reconstruction or source-file rewrite occurs.
	"""
	get_pixels = getattr(source, "get_flattened_data", None) or source.getdata
	pixels = list(get_pixels())
	background = Counter(p[:3] for p in pixels if p[1] > 235 and p[3] > 200).most_common(1)[0][0]
	core = Counter(p[:3] for p in pixels if p[1] < 5 and p[3] > 200).most_common(1)[0][0]
	layer = Image.new("RGBA", source.size)
	output = []
	for red, green, blue, alpha in pixels:
		if alpha <= 200 or green >= 200:
			output.append((0, 0, 0, 0))
			continue
		coverage = min(1, (background[1] - green) / (background[1] - core[1]))
		channels = [
			max(0, min(255, round((value - (1 - coverage) * bg) / coverage)))
			for value, bg in zip((red, green, blue), background, strict=True)
		]
		output.append((*channels, round(alpha * coverage)))
	layer.putdata(output)
	bounds = layer.getbbox()
	if not bounds:
		raise ValueError("Approved glyph was not found")
	return layer.crop(bounds)


def frame(source):
	"""Reuse the official Work tile frame/alpha; clear only its central glyph area."""
	result = source.copy()
	bounds = foreground(source).size
	# Work is centered; include ample antialias clearance around its glyph.
	left = (source.width - bounds[0]) // 2 - 8
	top = (source.height - bounds[1]) // 2 - 8
	right = left + bounds[0] + 16
	bottom = top + bounds[1] + 16
	for y in range(top, bottom):
		pale = Counter(
			source.getpixel((x, y))
			for x in range(source.width)
			if source.getpixel((x, y))[1] > 235 and source.getpixel((x, y))[3] == 255
		).most_common(1)[0][0]
		for x in range(left, right):
			result.putpixel((x, y), pale)
	return result.resize((CANVAS, CANVAS), Image.Resampling.LANCZOS)


def compose():
	result = frame(Image.open(ASSETS / "reybill-icon-work.png").convert("RGBA"))
	for index, name in enumerate(COMPONENTS):
		glyph = foreground(Image.open(ASSETS / f"reybill-icon-{name}.png").convert("RGBA"))
		glyph.thumbnail((GLYPH_BOX, GLYPH_BOX), Image.Resampling.LANCZOS)
		center_x = CANVAS / 2 + (-0.5 if index % 2 == 0 else 0.5) * PITCH
		center_y = CANVAS / 2 + (-0.5 if index < 2 else 0.5) * PITCH
		result.alpha_composite(glyph, (round(center_x - glyph.width / 2), round(center_y - glyph.height / 2)))
	return result


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--output", type=Path, default=ASSETS / "reybill-icon-accounting.png")
	args = parser.parse_args()
	compose().save(args.output, format="PNG")
	print(f"Created {args.output.name}: 512x512; one official tile frame and four desktop glyphs.")
