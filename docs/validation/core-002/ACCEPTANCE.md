# CORE-007 — real installation acceptance and v1.3.1 plan

Development preparation only. Core remains 1.3.0 until successful real acceptance
and explicit release approval. No v1.3.1 tag/stable push is authorized yet.

## Deploy the reviewed develop commit

Use a separate, explicitly authorized disposable Bench/site. Never run these
steps on `reybill.localhost`, production Press or a customer site. This document
does not authorize automatically provisioning or resetting any site.

| App | Version | Required upstream commit |
| --- | --- | --- |
| Frappe | 16.36.1 | `97a5dd93ca5883bcc9c4ef9834120c5cba397b67` |
| ERPNext | 16.37.0 | `af63cde4941570ec7b9e12422c68302762cfcf91` |

1. On a clean disposable Frappe/ERPNext Bench, verify both source versions and
   commits before proceeding. Do not pull current upstream branch HEAD or use
   `bench update`. ERPNext must be installed and initial setup incomplete.
2. Obtain Core from `origin/develop`. Pin the exact CORE-002 commit supplied in
   the acceptance handoff and record it with `git rev-parse HEAD`; do not rely
   on a moving branch name. For an existing clean disposable Core checkout:

   ```sh
   git fetch origin develop
   git checkout --detach <CORE-002-commit-from-handoff>
   git rev-parse HEAD
   ```

   For a new disposable Bench, `bench get-app --branch develop
   https://github.com/reybillhq/reybill_core.git`, then pin that same commit
   inside its Core checkout before installation. Use normal protected credential
   handling; do not paste passwords/tokens into commands or evidence.
3. Before the first setup visit, install Core using that disposable site's name:
   `bench --site <disposable-site> install-app reybill_core`. Core cannot brand
   setup before Core itself is installed. Use developer mode off for the native
   profile step. Do not run setup_complete or change setup flags through Console.
4. On that disposable deployment only, refresh native hook/translation caches
   using `bench --site <disposable-site> clear-cache`. Where persistent Python
   processes already imported old hooks, use that deployment's own service
   restart mechanism. Do not restart any existing development/shared service.
   CORE-002 has no schema change and needs no migration or JS bundle build;
   native static assets and app CSV translations are sufficient. Verify the JS
   URL below returns the reviewed source. A generic migrate is not a substitute
   for checking hooks/assets.
5. Record installed apps/versions, the exact Core commit, first-load console and
   network evidence. Required asset:
   `/assets/reybill_core/js/setup_wizard_branding.js`.
   Normal boot should include it in `frappe.boot.setup_wizard_requires` while
   setup is incomplete. Never include credentials, CSRF values, cookies, session
   state or private site configuration in evidence.

## Two-language real-site plan

Prefer two independently authorized disposable sites/environments, one English
and one German, installed from identical pinned app commits. Complete each site
once. Do not reset a completed site, recreate a real company or clear real user
preferences to replay setup. No new environment is created by this preparation.

On each fresh site, sign in normally and select the native language. Record:

| Acceptance gate | Required evidence / result |
| --- | --- |
| First identity | Login, tab identity, official favicon and native-lifecycle ReyBill splash; no failed assets |
| Early startup | Screen recording including first progress frame, preferably with network throttling; no Frappe text flash |
| English | Exact `Starting ReyBill...` |
| German | Exact `ReyBill wird gestartet...` |
| Wizard flow | Native welcome/region -> profile -> persona -> organization; fields, Next/Back/Enter, chart/fiscal-year validation unchanged |
| Progress/completion | Real backend/realtime progress advances, completes successfully and redirects normally to Desk |
| Branding | No unnecessary upstream attribution in audited steps; retain actual technical diagnostics and report errors honestly |
| Responsive UI | 1440, 1280, 768, 430 and 390px; native geometry and keyboard controls, no new overflow |
| CORE-001 | No exact app=reybill_core/name=ReyBill Core launcher in normal Desktop, Customize or Removed Icons |
| Functional inventory | Core stays installed; ReyBill Work, approved modules and other functional apps remain; routes/icons/order preserved |
| About | Customer product version matches installed ERPNext; installed app titles/versions are dynamic, including Core and Farm if installed |
| Existing branding | Theme, Help/Support, module artwork, black/white navbar logo, login/password recovery, favicon and splash remain intact |

Native developer mode can omit the profile slide; record that setting rather
than treating it as a branding defect. Realtime connectivity and full form
validation require real deployment evidence, not local fixtures.

For saved-layout acceptance, use only synthetic customizations on an authorized
disposable test site. Capture layout JSON/checksums, order, folders, removed
states and custom fields before the reviewed update; compare after deployment,
reload and normal logout/login. Exercise Customize without clicking Reset.
CORE-001's exclusion must preserve the persisted source layout while filtering
the exact redundant runtime launcher; unrelated hidden/removed items remain.

The risk identified during CORE-007 is confirmed in committed base `29f8369`:
`setup.apply_branding` calls `apply_desktop_branding`, which rewrites saved layout
indices/artwork. A subsequent local correction removes that saved-layout loop
and keeps canonical defaults on global Desktop Icon records only. Finalization
authorizes this correction's development commit/push, not stable publication.
See [FINAL_ACCEPTANCE.md](FINAL_ACCEPTANCE.md) for Site A/B/C procedures.
Pin the exact migration-fix commit from the handoff, not base 29f8369 alone,
for the preservation gate. If deployment includes migrate, test that exact
procedure only on a disposable customized site and compare persisted JSON.
Any unexpected change remains a release blocker. Never use the development
site's real saved layouts for this experiment.

Provide a PASS/FAIL/PENDING table, both language recordings/screenshots, console/
asset errors, installed commit/version details and before/after layout evidence.
Real fresh-site acceptance remains PENDING until the developer supplies results.
The prior 10 offline browser fixtures do not satisfy these installation gates.

## Remaining onboarding observations: source-traced disposition

| Observation | Locked-source investigation | Disposition |
| --- | --- | --- |
| sample_blog_post.html ERPNext prose | Whole-source search finds the template but no caller. Current setup_demo_data reads configured demo_data JSON for item/customer/supplier/order masters/transactions, not this HTML | Follow-up legacy website content; no demonstrated normal-journey blocker. If real testing displays it, record route/trigger and request approval |
| Welcome to Frappe! module fallback | Sidebar passes endpoint title; Module Onboarding.title is required. All inspected standard onboarding JSON titles are nonempty and neutral | Follow-up for missing/custom titles; not selected by the normal shipped path. Verify first-Desk modules and escalate if observed |

Neither observation authorizes unrelated rendering, fixture or upstream changes.
This is static reachability evidence, not a claim that a real fresh site passed.

## Future stable promotion — execute only after explicit approval

Observed stable base: `2ca191839fd766ac5fac06b9cb9c4f44635332aa` (Core 1.3.0).
Development/stable have divergent histories containing equivalent theme/About
patches and different historical version bumps. Do not merge develop blindly
or replay those already-equivalent patches/version commits.

Recheck remote refs and the content diff immediately before the release. Starting
from the verified clean stable base, promote only these patches, in this order:

1. `1841082cf7e6fc265ba68149534281d5e7b96955` — packaging v16 compatibility
   declaration and its durable test. Preserve this prerequisite; it is currently
   missing from stable, although already present on develop.
2. `fc5ab92d6dc1de4f3904bd3ac4417850145c89d9` — CORE-001 and associated tests/docs.
3. Exact reviewed CORE-002 handoff commit — wizard hook, adapter, translation,
   durable tests, offline validator and acceptance/audit documentation.
4. Reviewed migration-safety correction and its eight regression scenarios,
   identified by the exact development commit in the acceptance handoff.

Use normal `git cherry-pick -x` commits; stop for unexpected conflicts or changed
remote scope rather than resolving unrelated changes. No force push or history
rewrite. If an equivalent prerequisite already exists then, verify content and
omit its replay; never drop the packaging declaration to make promotion easier.

After acceptance approval, make explicit version-only commits setting
`reybill_core/__init__.py` to `__version__ = "1.3.1"` on BOTH develop and version-16.
The package version is dynamic from this file; do not edit historical version
records or assume the two branch histories must become identical. Run the safe
suite on the promoted content and verify both trees match in approved scope.

Only then create annotated `v1.3.1` on the final stable release commit, verify its
target, and push approved develop, version-16 and that tag through normal pushes.
Historical tags remain untouched. Return to develop and verify clean state and
remote refs. No version bump, stable promotion or tag is performed for CORE-007.
