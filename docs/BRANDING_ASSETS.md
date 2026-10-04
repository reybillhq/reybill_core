# Official ReyBill branding assets

The user-supplied files below are the official source of truth. Preserve their
contents: do not recreate, redraw, recolor, trace, generate replacements, crop
their source artwork, or convert them to substitute branding assets.

## Static assets for CRM / Help / About

The directory is `reybill_core/public/images/branding/`. The originally supplied
`Images/Branding` directory was moved to lowercase with user approval. Linux
paths and served asset URLs are case-sensitive. All supplied filenames and
file contents are preserved byte-for-byte.

| Supplied file | Format / canvas | Planned use |
| --- | --- | --- |
| `reybill-logo-black.svg` | SVG, 1024 × 768 viewBox | About logo on a light background |
| `reybill-logo-white.svg` | SVG, 1024 × 768 viewBox | About logo on a dark background |
| `reybill-icon-black.png` | PNG, 2133 × 2133 | Official icon available for light backgrounds; no icon rollout in this milestone |
| `reybill-icon-white.png` | PNG, 2133 × 2133 | Official icon available for dark backgrounds; no icon rollout in this milestone |

The About implementation should reference the two existing SVG logos through
the central `reybill_core/branding.py` configuration, using asset URLs beginning
with `/assets/reybill_core/images/branding/`. Preserve aspect ratio and original
artwork; select the supplied variant to match the current theme. Do not apply
CSS filters or alter fills to manufacture another variant. No newly generated
`reybill-logo.svg`, `reybill-logo-dark.svg`, or `reybill-icon.svg` is needed.

The CRM / Help / About milestone uses these static logo references in its
ReyBill-owned About dialog. Login, favicon, and splash behavior are unchanged.

## Splash animation: inspected, implementation deferred

The supplied animation sources are:

- `reybill_core/public/animations/Splash_color_logo_gradient_loop.json`
- `reybill_core/public/animations/Splash_color_logo_gradient_loop.svg`

The JSON parses successfully and has the Lottie / Bodymovin animation schema.
Its `v` field is `5.9.0`; this is export metadata, not a requirement to install
that exact player version. Its composition name is `SVG to Lottie`.

| Property | Observed value |
| --- | --- |
| Canvas | 1024 × 768 |
| Frame rate | 30 frames per second |
| Timeline | `ip: 0`, `op: 120`, approximately 4 seconds |
| Layers | One shape layer (`ty: 4`); no 3D layers |
| Shape content | Seven groups, nine paths, seven gradient fills, seven transforms |
| Animated properties | Seven |
| External assets / fonts | No entries in `assets`; no font dependencies declared |
| Expressions / effects / masks | No expression strings, layer effects, masks, or mattes found |

Playing this JSON in a browser requires a Lottie-compatible JavaScript player;
it cannot be displayed directly as an image. For the future splash milestone,
`lottie-web` with its **SVG renderer** is the proposed starting point. This is
a renderer recommendation based on the inspected vector/gradient content,
not a completed playback validation. The official player supports a JSON path
or `animationData`, and documents SVG, Canvas, and HTML renderer options:
[loadAnimation options](https://github.com/airbnb/lottie-web/wiki/loadAnimation-options).
Renderer feature coverage should be checked against the selected player:
[supported features](https://github.com/airbnb/lottie-web/wiki/Features).

No Lottie dependency is declared in the inspected ReyBill Python project or
the installed Frappe / ERPNext root `package.json` manifests. No player has
been installed or added to application assets. The future milestone should
keep any player dependency and integration inside `reybill_core`.

The accompanying SVG parses successfully and contains native SVG `<animate>`
elements for its gradient. It is a separately supplied animated SVG source;
it does not require a Lottie player to use that native SVG mechanism. It has
not been substituted for the JSON or enabled in the application.

The JSON timeline alone does not specify the application's loop or autoplay
policy. Loading behavior, reduced-motion behavior, renderer compatibility,
performance, and visual playback validation belong to the separate splash
milestone. The current CRM / Help / About milestone uses static official logos
only.
