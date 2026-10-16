# CORE-002 — native Setup Wizard white-labeling

Implemented on `develop`, based on `fc5ab92d6dc1de4f3904bd3ac4417850145c89d9`.
Core remains **1.3.0**. No release, version bump, migration or site reset is part
of this change. Real fresh-site acceptance is **PENDING**.

## Frozen environment

| Component | Version | Exact commit |
| --- | --- | --- |
| Frappe | 16.36.1 | `97a5dd93ca5883bcc9c4ef9834120c5cba397b67` |
| ERPNext | 16.37.0 | `af63cde4941570ec7b9e12422c68302762cfcf91` |

Source versions and the existing site's Installed Application records match these
versions. Never update a branch to its latest upstream HEAD to run these tests.
CORE-001 is preserved; its existing fresh-site acceptance gate remains open.

## Root cause and verified loading order

Frappe's `frappe/desk/page/setup_wizard/setup_wizard.js`,
`SetupWizard.show_working_state()` at native lines 308–321, calls:

```js
this.get_message(__("Setting up your system"), __("Starting Frappe ..."))
```

The source message is JavaScript, translated by the standard `__()` function.
The native German catalog maps it to **Frappé starten...** (`locale/de.po`,
`msgid "Starting Frappe ..."`). It is not a backend setup_task event, logo,
Python version value, provisioning message or server-side error.

Existing ReyBill branding covers native authentication/Desk context, splash,
Desktop/sidebar/menu presentation and exact approved names. It does not override
this longer wizard-specific sentence, so the native renderer displayed it.

Verified in the locked sources:

1. Core must be installed on the site before the first setup visit. Its install
   branding settings and hooks then exist. Core cannot brand pages rendered
   before installation; provisioning order is unchanged by this fix.
2. `www/desk.py` builds authenticated boot/context and app asset lists even when
   setup is incomplete. Existing `update_website_context` supplies the ReyBill
   app name, favicon and splash before HTML rendering. Native `www/desk.html`
   loads Desk bundles and installed app includes. This is source-confirmed,
   not an assumption that an ordinary Desktop event fires during setup.
3. `boot.add_home_page()` adds aggregated `setup_wizard_requires` only while
   setup is incomplete. ERPNext already uses this same hook for its slides.
4. The native wizard Page script defines `SetupWizard` and its render methods.
   Its `on_page_load` awaits `frappe.require(requires, callback)` before loading
   languages/user details, emitting before_load and constructing the wizard.
5. The ReyBill hook installs the adapter on this class while those required assets
   load. Every later native startup render is branded before HTML construction.
   No Desktop event, timing delay, observer or DOM text replacement is involved.
6. Native language changes clear the client message dictionary and call
   `setup_wizard.load_messages()`, which sends `get_messages_for_boot()`.
   The locked translation merger supports app CSV and MO dictionaries. Thus the
   context-specific ReyBill translation reloads naturally without replacing the
   global translator or changing a language preference ourselves.
7. Native setup_task handlers, progress calculations, retry and completion/redirect
   functions are untouched. After native completion the existing ReyBill Desktop
   branding continues through its original hooks.

The plain wizard asset URL deliberately uses native `frappe.require` static asset
versioning. It is not added to global app/web includes and needs no asset bundle.
No translation compilation is required for the supported CSV reader.

## Complete audited surface inventory

| Surface / native location | Original visible text or identity | Language | Result / mechanism | Evidence |
| --- | --- | --- | --- | --- |
| Startup progress, `SetupWizard.show_working_state()` -> `get_message()` | Starting Frappe ... | en | Starting ReyBill...; exact argument adapter before native HTML construction | Native JS contract + offline browser fixtures PASS; fresh site pending |
| Same startup, native German catalog | Frappé starten... | de | ReyBill wird gestartet...; `Starting ReyBill...` in context `ReyBill Setup Wizard`, app `translations/de.csv` | Native CSV merger + translator + offline browser fixtures PASS; fresh site pending |
| Neutral startup heading | Setting up your system / native German translation | en/de | Unchanged | Native original/branded HTML and geometry comparison PASS |
| Welcome/region step (`welcome`) | Welcome + first name; language, country, timezone, currency, usage-data option | en/de | Unchanged; no upstream product branding found in this step's rendered copy | Source/step contracts PASS; actual fields/fresh browser pending |
| Profile step (`user`) | Let's set up your account; name/email/password | en/de | Unchanged; suppressed by native developer mode where applicable | Source/step contracts PASS; authentication/validation unchanged |
| ERPNext persona step (`persona`) | A little about you; implementation purpose, company size, industry, current system, module choices | en/de | Unchanged; no product attribution found | Source/step contracts PASS; actual form interaction pending |
| Organization step (`organization`) | Setup your organization; company/abbreviation, chart of accounts, fiscal year, optional demo data | en/de | Unchanged; native Company creation and validation retained | Source/step contracts PASS; no company was created |
| Backend Frappe stages, `get_setup_stages()` | Updating global settings; Wrapping up; neutral failure messages | en/de | Unchanged; no product identity substitutions needed | Static audit; native event plumbing contracts PASS |
| Backend ERPNext stages, `get_setup_stages()` | Installing presets; Setting up company; Setting defaults; Personalizing your setup; optional Creating demo data | en/de | Unchanged; native operation descriptions remain truthful | Static audit; actual provisioning operations NOT RUN |
| Queued startup | starting the setup... | en/de | Unchanged neutral native copy | Static/renderer contract |
| Completion (`post_setup_success`) | Setup Complete; Refreshing... | en/de | Unchanged, native delay/redirect/session route handling retained | VM redirect contract + offline completion fixtures PASS |
| Errors/retry (`abort_setup`, `attach_abort_button`) | Setup failed; Could not start up:; Retry; actual diagnostic detail | en/de | Unchanged; do not replace Frappe/ERPNext in genuine errors or tracebacks | VM and offline Retry/error fixtures PASS |
| Initial Desk HTML title | Existing app_name context -> ReyBill | shared | Existing context hook retained; neutral document/page titles preserved | Existing Python context tests PASS; fresh browser pending |
| Favicon / native startup set_favicon | Existing official ReyBill icon | shared | Existing context/settings retained; native startup reuses HTML href | Existing tests/source audit PASS; fresh browser pending |
| Initial loading logo | Existing official static/animated ReyBill splash, reduced-motion/error fallback | shared | Existing app-owned include retained; native .splash removal unchanged | Existing tests PASS; no asset/template changes |
| Wizard logo / footer / copyright | No product logo, attribution or copyright in native wizard markup | shared | No new decorations, logo sizing or company text introduced | Native source/HTML audit |
| Top navigation during setup | Native `make_nav_bar()` skips toolbar when home_page is setup-wizard | shared | No new navbar adapter or logo replacement required | Native source audit; real mobile boot pending |
| Technical APIs/modules/app keys | frappe.*, erpnext.*, internal routes/DocTypes and native error identifiers | shared | Intentionally unchanged | File/prototype/API contracts |

Only one inappropriate product-brand sentence was found in the audited wizard
rendering/steps/stage copy. The full audit does not justify rewriting neutral text
or adding invented welcome/preparation/completion states. No wizard CSS, HTML
template, slide definition, field, button, permission or backend function changed.

Separate findings preserved for review:

- Legacy `setup/setup_wizard/data/sample_blog_post.html` includes ERPNext prose,
  but the locked source has no caller for it. Current optional demo setup loads
  item/customer/supplier/order JSON rather than this HTML. It is not a confirmed
  normal-onboarding defect; retain as a follow-up, not a reason to rewrite setup.
- The separate module onboarding panel (`UserOnboarding`) has an optional
  `Welcome to Frappe!` fallback when its caller supplies no title. It is not a
  wizard step; the native endpoint passes the required Module Onboarding title,
  and every shipped onboarding record inspected has a nonempty, neutral title.
  The fallback is not selected in the normal source path. Retain as a follow-up
  for missing/custom titles and verify first Desk during real acceptance.
- Setup cannot be white-labeled by Core before Core has been installed. A deploy
  still running cached old hook data must refresh that deployment's native hook/
  translation cache. This task does not change provisioning or restart services.

## Implementation and regression coverage

Runtime files:

- `reybill_core/hooks.py`: one native `setup_wizard_requires` registration.
- `reybill_core/public/js/setup_wizard_branding.js`: idempotent wrapper of only
  `SetupWizard.prototype.get_message`, matching the exact currently translated
  native starting sentence. It preserves the receiver, title, extra arguments and
  return value, and delegates all HTML/geometry to the native method.
- `reybill_core/translations/de.csv`: one context-specific ReyBill-owned phrase;
  no global override of Frappe, ERPNext, or the original technical source key.

Tests:

- `tests/test_setup_wizard.py`: native translation file parsing/app dictionary
  merging, hook scoping, locked source ordering and language-refresh contract.
- `tests/setup_wizard.test.cjs`: executes native JS/translator in VM fixtures;
  tests English/German/other-locale fallback, language switches, exact pre-render
  branding, idempotency, receiver/return/args, original progress math, errors,
  native redirect behavior, unchanged methods/HTML, actual slide identities and
  the complete audited translatable branding inventory.
- `tests/validate_setup_wizard.py`: offline browser fixture for native
  progress/retry/completion markup + native compiled CSS, in en/de at 1440,
  1280, 768, 430 and 390 pixels. All network is blocked. This does not instantiate
  real authenticated forms or execute backend setup. Evidence goes outside Git.

All existing CORE-001, icons, Desktop naming/order, logo, About and website
contracts must also pass. Browser fixtures are explicitly not fresh-site proof.

## Fresh-site acceptance procedure — not executed on reybill.localhost

No disposable site was authorized or created. The live development site's
setup_complete is 1; it must never be reset or navigated into an active setup run.

On a separately authorized disposable/fresh ERPNext site:

1. Pin the exact upstream versions above. Install ERPNext and the reviewed Core
   tree before the first setup visit. Record the deployed Core hash/diff. Do not
   use v16.50+, production Press or a real customer site for this acceptance.
2. Refresh hook/translation caches on that disposable deployment through its
   normal deployment procedure. No migration/schema change or JS bundle build is
   required by this fix. A new site starts with a clean cache; there is no new API.
3. Sign in normally. Confirm Setup Wizard boot includes Core's setup_wizard_requires
   asset, loaded before wizard construction. Record console/network errors and
   the first startup frame; use slow network to check there is no original-brand
   flash. Never expose setup credentials or session data in evidence.
4. Verify Welcome/region -> profile -> persona -> organization, all native field
   rules, keyboard controls, back/next, chart of accounts, fiscal-year validation,
   selected company/currency and telemetry choices. Developer mode can suppress
   the profile step; do not misreport this as a missing ReyBill step.
5. Select German through the native language field; verify all neutral labels
   remain native and startup is `ReyBill wird gestartet...`. Verify English gives
   `Starting ReyBill...`. Complete separate fresh runs where needed; do not reset
   the development site. Check locale switching and untranslated-locale fallback.
6. Capture initial progress, each backend stage, completion and normal Desk
   redirect. Preserve/review real error messages and Retry without manufacturing
   corruption. Validate realtime progress in the actual deployment.
7. At all five requested widths check native geometry, keyboard/accessibility,
   tab identity, favicon and initial splash. Do not add a wizard logo/footer.
8. Verify first Desktop naming, canonical default order, approved icons, About
   dynamic versions and support; CORE-001 must exclude only the exact redundant
   Core launcher from normal/customize/Removed Icons while retaining app inventory,
   ReyBill Work, Farm and unrelated apps. Do not reset saved Desktop layouts.
9. Report optional demo website/module-onboarding attribution separately. Preserve
   diagnostic framework/package names; do not implement unreviewed extra surfaces.

Gate: user/developer real fresh-site acceptance is required before release.
CORE-007 authorizes committing/pushing this reviewed fix to develop only, while
keeping the version at 1.3.0. The fresh-site acceptance and stable-release gate
remains closed. See [ACCEPTANCE.md](ACCEPTANCE.md) for deployment, evidence and
the explicit future v1.3.1 promotion plan.

## Recorded validation — 2026-10-16

| Check | Result |
| --- | --- |
| Python regression suite | PASS, 26 tests (including three new wizard contracts and CORE-001) |
| JavaScript contracts | PASS, 17 tests (including six new wizard contracts and CORE-001) |
| Ruff lint / format | PASS, app and test Python files |
| ESLint / Prettier | PASS, new adapter and wizard JS contracts |
| Git whitespace | PASS |
| Offline native browser fixtures | PASS, en/de × 1440/1280/768/430/390px; startup/progress/retry/completion |
| Geometry comparison | PASS, original/branded native progress markup measured identically at each viewport |
| Browser overflow / errors | No horizontal overflow or page JavaScript errors in the ten fixtures |
| Official assets | Existing file hashes unchanged |
| Frappe / ERPNext / Farm | Source/Git state unchanged; pre-existing ERPNext banking/yarn.lock edit preserved |
| Live site integrity | Desktop Icon/Layout, Workspace/Sidebar, Singles/settings, installed-app and Company counts/checksums unchanged |
| Real authenticated fresh-site lifecycle | PENDING; no authorized disposable site available, no live setup reset or run |

Logs, 20 screenshots, locale/viewport results and final integrity hashes are under
`/tmp/reybill-core-002-validation/`. Browser tools and three extracted browser
libraries were installed only into that temporary directory; no system package,
Bench environment or app dependency was changed. Browser fixtures blocked all
network requests and used no real session, credential or application data.
Screenshots show isolated native progress markup, not the complete authenticated
wizard shell/fields. Real form validation, realtime deployment and first-Desk
acceptance remain pending as described above. No services were restarted and no
live cache-clearing, setup backend, language-preference writes or migration ran.
