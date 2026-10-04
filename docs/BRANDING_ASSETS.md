# Official ReyBill branding assets

The user-supplied files below are the official source of truth. Preserve their
contents: do not recreate, redraw, recolor, trace, generate replacements, crop
their source artwork, or convert them to substitute branding assets.

## Static assets for About / Login / favicon

The directory is `reybill_core/public/images/branding/`. The originally supplied
`Images/Branding` directory was moved to lowercase with user approval. Linux
paths and served asset URLs are case-sensitive. All supplied filenames and
file contents are preserved byte-for-byte.

| Supplied file | Format / canvas | Planned use |
| --- | --- | --- |
| `reybill-logo-black.svg` | SVG, 1024 × 768 viewBox | About on a light background, Login / Reset Password, static splash fallback |
| `reybill-logo-white.svg` | SVG, 1024 × 768 viewBox | About and static splash fallback on a dark background |
| `reybill-icon-black.png` | PNG, 2133 × 2133 | Website / Login / Desk favicon, served without conversion |
| `reybill-icon-white.png` | PNG, 2133 × 2133 | Official alternative retained unchanged; not deployed as favicon |

The About implementation should reference the two existing SVG logos through
the central `reybill_core/branding.py` configuration, using asset URLs beginning
with `/assets/reybill_core/images/branding/`. Preserve aspect ratio and original
artwork; select the supplied variant to match the current theme. Do not apply
CSS filters or alter fills to manufacture another variant. No newly generated
`reybill-logo.svg`, `reybill-logo-dark.svg`, or `reybill-icon.svg` is needed.

The v0.0.3 milestone introduced the ReyBill-owned About dialog. The approved
v0.0.4 milestone adds Login / Reset Password, favicon and initial Desk splash.
Login's logo CSS changes only image dimensions: it preserves the entire original
4:3 canvas, intrinsic aspect ratio and artwork. No source cropping or conversion
is performed. Asset URLs and display settings remain centralized in
`reybill_core/branding.py`.

## Splash animation: native SVG runtime, original JSON reference

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

Playing this JSON in a browser would require a Lottie-compatible JavaScript
player; it cannot be displayed directly as an image. The original JSON remains
unchanged as the source animation/reference and is **not requested at runtime**.
For a future JSON playback decision, the official player documents a JSON path
or `animationData`, and SVG, Canvas, and HTML renderer options:
[loadAnimation options](https://github.com/airbnb/lottie-web/wiki/loadAnimation-options).
Renderer feature coverage should be checked against the selected player:
[supported features](https://github.com/airbnb/lottie-web/wiki/Features).

No compatible Lottie renderer was found in the inspected Frappe / ERPNext
frontend source or root `package.json` manifests. No Lottie or other animation
dependency has been installed, and no CDN player is used.

The accompanying SVG parses successfully and contains native SVG `<animate>`
elements for its gradient, with a four-second repeating timeline. It is a
separately supplied official animation asset, not a conversion produced by
ReyBill Core. With explicit user approval, v0.0.4 uses this SVG as an image
through native browser SVG animation. See
[SVG as an image](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image).

The app-owned splash include preserves `.centered.splash`. Frappe's native
`Application.make_page_container()` still removes it; no readiness callbacks,
routes, four-second minimum duration or artificial delays are added. The
component starts with the official static logo appropriate to the existing
Desk theme (black on light, white on dark), preloads the animated
SVG, and changes only that component's image when loading succeeds. Failed
animation/script loading and JavaScript-disabled rendering retain the static
ReyBill image. Reduced-motion preferences skip animation loading; a preference
change while the splash exists updates that same component. Detached splash
images are never reattached. An Automatic Desk theme uses a native picture
source selected by `prefers-color-scheme`, so the static variant remains
readable even when component JavaScript is disabled. This does not change the
user's theme, application colors or supplied asset contents.

Frappe also embeds the splash include inside its native Login success handler's
JavaScript string before redirecting. That transition uses static branding;
the component script is emitted only in initial Desk HTML, avoiding nested
script tags in Login code. The native redirect behavior is unchanged.

The additionally supplied Desktop artwork is
`reybill_core/public/images/branding/Reybill_desk_icon.png` (exact capitalization).
It is used only for the existing internally named `ERPNext` Desktop Icon,
displayed as ReyBill, including its Removed Icons presentation. It is never used
for the navbar. Its bytes are preserved; no duplicate asset is created.

The Desktop navbar uses the original black/white SVGs from `LOGOS` in the central
branding module. A scoped client adapter calls the native `frappe.ui.set_theme`
unchanged and updates only `#brand-logo` after the native resolved theme changes,
including Automatic mode. The native `desktop_screen` event handles rendering
and navigation back to Desktop. Dimensions, surrounding elements and clicks are
untouched; no observer, CSS filter or asset transformation is added.

All six original official asset hashes are checked against their preimplementation
baseline. Browser evidence and the test-only network hold used to observe the
short-lived splash are documented in
[Login / favicon / splash validation](validation/login-favicon-splash/README.md).

## v0.0.4 asset cache invalidation

`branding_asset_url()` is the single constructor for used ReyBill branding
assets. It emits the ReyBill Core `__version__` and a twelve-character SHA-256
content fingerprint, for example:

```
/assets/reybill_core/images/branding/Reybill_desk_icon.png?v=0.0.4&h=c2b0e400d772
```

The two logo variants, favicon, runtime splash SVG, static splash fallback and
removed ReyBill Desktop artwork use these URLs. The JSON remains a
source/reference asset and is not loaded.
Unchanged content in the same release retains a stable cacheable URL. New
release versions or different content generate a different cache key when
branding configuration is loaded. Normal deployment applies setup/migration,
clears server caches and restarts workers; a same-release development asset
replacement can reapply setup from a fresh process. Customers do not need to
clear browser caches. No response cache headers, third-party asset URLs or
Frappe/ERPNext cache mechanisms are changed. An unavailable owned asset still
gets an owned versioned URL; it cannot prevent Login/Desk rendering or cause a
vendor-artwork fallback.

The actual Desktop filename remains `Reybill_desk_icon.png` (lowercase `b`),
with no duplicate or rename. Its current source SHA-256 and the actual browser
image-response SHA-256 match. The source hash still matches the prior milestone
review; no different replacement bytes were present in this directory during
this check.

## Historical v0.0.4 Desktop logo sizing: native Frappe v16

All ReyBill navbar sizing experiments, including the 320 × 150 rule and its
mobile override, were removed at the user's final release instruction.
`desktop_branding.css` and its `app_include_css` hook are absent from the release.
No ReyBill CSS sets width, height, maximum dimensions or object fit on
`.navbar-home img` or `#brand-logo`.

The native Desk bundle supplies `.navbar-home img { width: 32px; height: 32px; }`;
the native Desktop page supplies `#brand-logo { width: auto; }`. Chromium computes
the unchanged official 1024 × 768 SVG to approximately 42.65625 × 32 pixels.
Native navbar height remains 52 pixels, and all canvas padding is retained.
The existing scoped source adapter still selects black for light and white for
dark, including live native theme switching and reloads. Logo assets and other
Desktop artwork remain unchanged.

[Focused cache/sizing validation](validation/login-favicon-splash/BRANDING_FIXES.md).

## v1.0.0 stable base: approved 150px Desk logo

The first major base release includes the subsequently approved
`desk_navbar_logo.css` through the versioned `app_include_css` hook.
`.navbar-home img` uses `height: 150px`, `width: auto !important`, and
`object-fit: contain`. The official 1024 × 768 SVG computes to 200 × 150 pixels.
The native navbar remains 52px tall; no container, Desktop icon, ordering or
navigation changes accompany this sizing rule. Black/white source switching
continues through the existing native theme adapter.

The centered wordmark is visible, but the transparent SVG canvas extends below
the navbar. At 390px the Search contents can wrap outside their button; at
390px and 430px the transparent image box overlaps the upper first-icon region.
These approved observations are retained for a later responsive milestone.
All official asset bytes are unchanged. Historical release notes above remain
as evidence of the previous sizing decision.

[Major base release validation](validation/v1.0.0/RELEASE_VALIDATION.md).
