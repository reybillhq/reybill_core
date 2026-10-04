# Module icon validation — reybill.localhost

Date: 2026-10-04. App baseline: v1.0.0, unchanged. Tested installed Frappe v16 and ERPNext v16 with Chromium/Playwright.

## Results

- All 23 approved production PNGs match read-only imports byte-for-byte and match the files fetched from the live site (HTTP 200 and SHA-256).
- All 14 mapped main Desktop tiles render correctly; Home remains its native `#H` symbol. Removed `ERPNext` (customer ReyBill) retains its previous `Reybill_desk_icon.png` and removed state; Workspace/Add New retains its native icon.
- All nine Accounting children render their approved PNGs in the native folder modal. Accounting remains a Folder with the original click behavior.
- All nine children navigate using their native links, and their corresponding sidebar headers use the approved PNG. CRM's mapped sidebar header and native Workspace → Accounting submenu were also observed.
- Native text-only link cards remain text-only; no Workspace icon slot was observed on the tested Accounting destinations. No UI is invented for nonexistent surfaces.
- Light and dark rendering passed at 1440, 1280, 768, 430 and 390px. Native image boxes are 54 × 54px at desktop/tablet widths and 50 × 50px at 430/390px. Full square canvas is contained, filter is `none`, and each mapped tile has one image layer, transparent native background, zero padding and no wrapper shadow. No new icon overflow, label overlap, stretching or cropping was found. Native label ellipsis and the previously approved 150px navbar behavior remain unchanged.
- Repeated reload, live theme changes, route away/return and native folder navigation keep artwork and order intact. Saving Dark/Light on the disposable account and reloading selects the expected theme while retaining the approved artwork.
- A disposable System User was given a copied layout with Home before Framework. Its customized order survived reload and navigation. Native Reset Desktop Layout was clicked **only for that disposable account**, restored canonical order and kept the PNGs. Temporary users, copied layouts and sessions were removed afterward; protected session files are outside Git and were removed.
- Browser evidence contains **zero icon request failures, zero page errors and zero duplicate custom icon layers**. The console is not globally clean: the full run recorded 98 console errors. A targeted Desk → Accounting → Invoicing comparison produced the same five errors with the adapter enabled and disabled: native `/socket.io/` HTTP 404/polling connection errors and an `/undefined` HTTP 404. These existing site/runtime issues were not changed by the icon task. The adapter contract test checks translated display labels against stable names, preserves original Folder callbacks/data/return values, native fallback and repeated installation.
- Existing Python tests: **9 passed**. JavaScript contract tests including the new icon test: **6 passed**. Ruff lint/format, ESLint and Prettier checks passed.
- Frappe's 3,767 and ERPNext's 5,189 tracked files match baseline hashes. ERPNext already had a `banking/yarn.lock` working-tree change before this task; it is unchanged. All seven previous official assets match their hashes; all 23 incoming source files are unchanged. Desktop order/setup code, navbar CSS, version and release tags are unchanged.

Record-integrity results are recorded separately because the final saved-layout fingerprint check detected an Administrator save followed by deletion during this work. The icon adapter contains no layout/database write, and the validation script's native Reset calls were for the disposable accounts. Its cause was not determined. No existing layout has been reconstructed or overwritten; later corrections use fresh matching before/after fingerprints.

## Durable evidence and local-only captures

- [import-inventory.json](import-inventory.json): original 23 imports, dimensions, alpha, sizes and hashes.
- [native-surfaces.json](native-surfaces.json): stable Desktop/Icon/Workspace/Sidebar identities; no saved-layout contents.
- [console-comparison.json](console-comparison.json): existing native console errors reproduced without the adapter.

The screenshots, raw browser output, changed-file manifests and per-run record/source snapshots remain local and untracked. They are intentionally excluded from the icon-system commit. This initial validation predates the Home, Accounting and removed-ReyBill corrections; see the [Home/Accounting notes](../home-accounting/README.md) and [removed application tile notes](../removed-brand-icon/README.md) for final artwork and read-only validation.

The native CRM deprecation banner still references **Frappe CRM**; it is unrelated to module artwork and was left unchanged.

## Reproduction and scope

### Approved final state and finalization checks

The approved family contains **25 production PNGs**: 24 unchanged supplied images and the dedicated Accounting composite. The final mappings include Framework/ReyBill Work → Work, Home → Home, Accounting → the four-glyph Accounting composite, and the hidden ERPNext/ReyBill application tile → ReyBill. All nine Accounting child icons remain included. The composite positions are Invoicing / Payments above Budget / Share Management.

Finalization reran the 10 Python tests, six JavaScript contracts, Ruff lint/format, ESLint, Prettier and whitespace checks. Asset hashes, all production filenames, prior browser observations and upstream hashes were rechecked. The rendering adapter/CSS have not changed since successful final browser validation, so no new browser session or live reset test is needed. Finalization performs zero Administrator or other Desktop Layout saves/deletes/resets; a fresh six-table fingerprint comparison verifies current state remains unchanged.

The Accounting generator is maintained in `scripts/build_accounting_icon.py` and reads repository assets. It was not run against the approved production output during finalization. The full browser harness rejects Administrator/Guest as disposable reset-fixture identities; it is not run during finalization. The focused Home/Accounting and removed-brand harnesses block both layout persistence endpoints.

The Git commit retains implementation, 25 production assets, reusable tests, the offline generator, these compact notes, source inventory, geometry/provenance and selected small integrity/console records. Screenshots, raw browser output and changed-file manifests remain local and untracked. The app version stays `1.0.0`; historical tags and `version-16` are unchanged. Only `develop` is prepared for pushing.

Run the focused contracts without site mutation:

```bash
python -m unittest discover -s tests -p 'test_*.py'
node --test tests/*.test.cjs
```

The live harness is `tests/validate_module_icons.py`. It requires a protected, authorized temporary Administrator session file and a separate disposable-account fixture file. Never point its Reset section at an existing user's account; it asserts the fixture identity before resetting. The Administrator context blocks both native layout Save and Reset endpoints and fails if either is attempted; the final guarded run attempted neither. Fixture creation/cleanup and browser libraries are kept in `/tmp`, outside the app repository. Neither session value nor test account identity is written to browser evidence.

Only cache clearing was required. App CSS, JS and original PNGs are directly served by the existing Frappe asset mapping; there is no new bundle or schema change, so no build or migration was run. No install/setup/order operation was invoked. These validation runs performed no commit, tag or push.
