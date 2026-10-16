# v1.3.1 final acceptance — correction and outstanding gates

Assessment date: 2026-10-16. Reviewed development base:
`29f83697343e674fe4c626cf720a50b827f20439`. This correction is approved for
development commit/push; pin its exact resulting commit from the final handoff.
Core stays 1.3.0.
Stable stays `2ca191839fd766ac5fac06b9cb9c4f44635332aa`.

No authorized disposable site or fresh authenticated browser session is available
in this environment. The only local site is reybill.localhost, setup_complete=1.
It was not reset, migrated or taken through onboarding. No site/session/user was
created, no credential injected, and no production infrastructure accessed.

## Confirmed layout bug and narrow correction

Both after_install and after_migrate call `reybill_core.setup.apply_branding`.
That function updates only approved display settings, then calls
`reybill_core.desktop.apply_desktop_branding`.

Previously the Desktop function:

1. Set canonical idx on global standard Desktop Icon records, restored the approved
   default visibility of Home/CRM/Support, and set the removed ERPNext/ReyBill artwork.
2. Loaded every Desktop Layout document, parsed its JSON, rewrote known icon idx
   and cached ERPNext artwork, then db_set the resulting JSON if it differed.

Step 2 overwrote customized order for every affected user and also changed JSON
formatting/cached artwork even when a layout already used canonical order. It
retained hidden flags, but that did not preserve the complete user customization.
An opaque legacy layout value could additionally fail JSON parsing during migrate.
On a fresh site there is no saved layout, so only global defaults matter.

Native locked Frappe's `DesktopPage.sync_layout()` selects its saved data when
present and falls back to `boot.desktop_icons` otherwise. Its normal renderer
uses those saved idx/hidden/folder values. The native save/reset APIs are separate
user actions, not requirements for applying branding defaults.

The correction removes step 2, its unused order_layout helper and json
import. It does not read, parse, reserialize, save, delete or reset Desktop Layout
documents. Step 1 is retained, including routes/permissions/artwork and the
canonical defaults for users with no saved layout. Existing module-artwork client
adapters remain unchanged; no saved artwork URL needs a database rewrite.
The original helper-only test is replaced with eight tests of the actual hook.
All eight are in `tests/test_desktop.py`. The temporary working filename
`tests/test_desktop_migration.py` was moved into that tracked test file; it is
absent from disk and tracked/untracked/ignored Git paths. No durable tests are
omitted and no duplicate test file is needed.

All eight new fixture scenarios failed against the original implementation
(seven assertion failures and one JSON error), then passed after the correction:

- Fresh site without saved layout, with canonical global defaults.
- Existing canonical saved layout, including exact JSON formatting.
- Customized order, folder relationships and extra fields.
- Removed icons and saved artwork.
- Multiple independent user layouts.
- Empty/object/null/opaque saved values, without parsing.
- Repeated hook execution, with no further writes after defaults are applied.
- CORE-001 suppression after the hook while retaining the original persisted
  redundant row, other modules, app inventory and all unrelated saved state.

These are in-memory document/database fixtures, not a real bench migration.
Core's no-layout-write invariant is verified; a full migrate also runs other
installed apps' hooks and must still be accepted on an authorized disposable site.
Do not infer the whole deployment is safe solely from these tests.

## Evidence and acceptance status

| Gate | Isolated evidence | Real-site acceptance |
| --- | --- | --- |
| CORE-001 Desktop/Customize/Removed Icons | Existing real-native JS method contracts and Python boot tests pass; exact app/name filtering preserved | PENDING fresh-site browser evidence |
| CORE-002 en/de startup | Native translator/renderer and offline browser fixtures pass, with branded initial HTML | PENDING first-frame recording/no flash |
| Wizard steps/progress/errors/redirect | Native JS contract tests preserve steps, events, math, errors, methods and redirects | PENDING actual form validation and completed setup |
| Global canonical defaults | Hook fixtures pass | PENDING fresh Desktop default order/artwork check |
| Saved layout migration safety | Bug reproduced; corrected Core hook preserves exact saved JSON for all fixture users | PENDING full disposable migration and actual browser reload |
| Login/password recovery/favicon/splash | Existing scoped context/settings/template regressions pass; runtime code unchanged | PENDING actual fresh-site smoke test |
| Module icons/theme/Help/Support/logo | Existing icon/menu/theme-source contracts pass; assets/CSS unchanged | PENDING light/dark/responsive deployment smoke test |
| Dynamic About and installed versions | Existing metadata/renderer contracts pass; app inventory retained | PENDING real About on the fresh site |

Logs, offline screenshots and before/after integrity records are stored outside
Git in `/tmp/reybill-v131-final-acceptance/`. Browser fixtures have all network
requests blocked and are explicitly not installation evidence.

Recorded checks: 33 Python tests, 17 JavaScript contracts and ten en/de browser
fixtures passed. Ruff lint/format, relevant Prettier and Git whitespace passed.
Full Desk/test JavaScript lint passes with About's existing runtime `reybill`
namespace declared for that file only. Unqualified lint already flags the
unchanged About source for that undeclared global; no unrelated source/config
change or broad rule suppression was introduced. The original 26-test Python
suite now has 33 tests because one helper-only test was replaced by eight actual
hook scenarios. Existing module-icon, login/password context, splash, menu,
theme-logo, CORE-001, CORE-002 and dynamic About contracts remain passing.

## Exact disposable-site deployment and acceptance

No sites are provisioned by this document. Use already authorized disposable
environments; preserve the existing development Bench and reybill.localhost.
Changing an app checkout affects every site in that Bench, so use an independent
test Bench for Site C's before/after version test, or ensure every affected site
is explicitly disposable. Never share a checkout with an active/customer Bench.

For all three sites verify these exact upstream hashes before testing:

```sh
git -C apps/frappe rev-parse HEAD
git -C apps/erpnext rev-parse HEAD
```

Expected Frappe: `97a5dd93ca5883bcc9c4ef9834120c5cba397b67` (16.36.1).
Expected ERPNext: `af63cde4941570ec7b9e12422c68302762cfcf91` (16.37.0).
Do not run bench update or pull a moving upstream branch.

In the disposable Bench's Core checkout, fetch develop and pin the full
migration-fix commit supplied in the final handoff:

```sh
git fetch origin develop
git checkout --detach <migration-fix-commit-from-handoff>
git rev-parse HEAD
```

Keep passwords, API keys and sessions out of commands, Git and evidence. Fresh
sites must have ERPNext installed and Setup Wizard not yet completed. Install
Core before first onboarding with `bench --site <authorized-fresh-site>
install-app reybill_core`, then clear that disposable site's native caches with
`bench --site <authorized-fresh-site> clear-cache`. A persistent old worker may
require that disposable deployment's normal restart procedure; never restart
existing development/shared services. Use developer mode off for the profile
slide. Record source commit hashes, installed app versions and script URL/content.

### Site A — fresh English

Select English in the native language field. Record Login, favicon and ReyBill
splash, each native wizard step, and the first progress frame. It must show
`Starting ReyBill...` immediately, without original-brand flash. Confirm native
field validation, buttons/keyboard, realtime progress, successful completion and
Desk redirect. Record console/server exceptions or missing assets; no success
claim is valid if setup did not actually finish.

### Site B — fresh German

Use a different fresh disposable site with identical app pins and select German.
Record the same lifecycle, verifying `ReyBill wird gestartet...` and no Frappé
flash. Never reset Site A, reybill.localhost or a customer site to repeat setup.

### Site C — completed setup with customization

Use only synthetic users/data on an authorized disposable completed site. For
a version-transition test, begin at Core base 29f8369, make customizations, then
deploy the reviewed migration-fix commit BEFORE running migration.

1. Customize order, remove one icon and retain/create a supported custom folder
   with a child icon. If practical, give a second test user a different order,
   removed selection and folder contents. Save normally through native UI;
   do not use Reset. Record screenshots, user identities and current app commits.
2. Capture exact persisted Desktop Layout records outside Git. From Site C's
   disposable Bench, the following template exports only Desktop Layout data:

   ```sh
   set -e
   REYBILL_TEST_SITE='replace-with-authorized-disposable-site-c'
   test "$REYBILL_TEST_SITE" != 'reybill.localhost'
   REYBILL_ACCEPTANCE_DIR="$(mktemp -d /tmp/reybill-v131-layout-XXXXXX)"
   bench --site "$REYBILL_TEST_SITE" execute frappe.get_all --kwargs '{"doctype":"Desktop Layout","fields":["*"],"order_by":"name asc","limit_page_length":0}' > "$REYBILL_ACCEPTANCE_DIR/layout-before.json"
   ```

   Do not export User documents, private site config, cookies or credentials.
   Keep these snapshots out of every application repository.
3. Pin the reviewed fix as above, refresh only the disposable deployment's loaded
   code as needed, then run its migration and compare the persisted records:

   ```sh
   bench --site "$REYBILL_TEST_SITE" migrate
   bench --site "$REYBILL_TEST_SITE" execute frappe.get_all --kwargs '{"doctype":"Desktop Layout","fields":["*"],"order_by":"name asc","limit_page_length":0}' > "$REYBILL_ACCEPTANCE_DIR/layout-after-first.json"
   cmp "$REYBILL_ACCEPTANCE_DIR/layout-before.json" "$REYBILL_ACCEPTANCE_DIR/layout-after-first.json"
   bench --site "$REYBILL_TEST_SITE" migrate
   bench --site "$REYBILL_TEST_SITE" execute frappe.get_all --kwargs '{"doctype":"Desktop Layout","fields":["*"],"order_by":"name asc","limit_page_length":0}' > "$REYBILL_ACCEPTANCE_DIR/layout-after-second.json"
   cmp "$REYBILL_ACCEPTANCE_DIR/layout-before.json" "$REYBILL_ACCEPTANCE_DIR/layout-after-second.json"
   ```

   Review any difference and stop approval. Do not normalize/reorder the JSON
   to make a failing comparison pass. Full migration includes other apps' hooks;
   retain the failure evidence and identify the actual writer if there is one.
4. Reload, log out/in normally and inspect each user's Desktop, Customize and
   Removed Icons. Order, removed selections, folders/contents must remain intact.
   The exact redundant Core launcher must be absent from all rendered lists,
   while Core remains installed and present in dynamic About. Verify global
   canonical defaults separately with a disposable user who has no saved layout.

### Shared branding and evidence checklist

1. Deploy the exact reviewed migration-fix development
   commit/diff to separately authorized disposable en/de sites. Pin Frappe
   16.36.1 (`97a5dd93ca5883bcc9c4ef9834120c5cba397b67`) and ERPNext 16.37.0
   (`af63cde4941570ec7b9e12422c68302762cfcf91`); install Core before first onboarding.
   Use [ACCEPTANCE.md](ACCEPTANCE.md) for the deployment and evidence details.
2. Record the first startup frame: English `Starting ReyBill...`, German
   `ReyBill wird gestartet...`; no original-brand flash. Complete all native
   steps and realtime progress normally, check errors/validation, then Desk.
   Use separate fresh sites if necessary, never reset a completed live site.
3. Check Desktop, Customize and Removed Icons after repeated loading: no exact
   app=reybill_core/name=ReyBill Core launcher; Core remains installed and About
   lists it. Keep ReyBill Work, Home, every approved module and functional app.
4. On an authorized disposable customized site only, capture each user's Desktop
   Layout JSON/checksum, idx, folders and removed selections. Run the actual
   intended migration there, compare exact persisted values, repeat migration,
   reload/login and inspect Customize. Never click Reset. Report every difference.
   The migration command is `bench --site <authorized-disposable-site> migrate`
   from that site's separate test Bench; never substitute reybill.localhost.
5. Smoke-test Login/password recovery, favicon, splash, theme/black-white logo,
   icons, Help/Support, dynamic About and native navigation. Record browser/server
   errors and commit/version details, with no tokens/cookies/private config.

No new normal-path branding defect was identified beyond the fixes under test.
The old sample blog HTML has no caller in the locked sources; standard module
onboarding passes required nonempty neutral titles instead of the framework
welcome fallback. These remain follow-ups unless actually seen during acceptance.

Prior assessment integrity check: Frappe, ERPNext and Farm tracked/unignored file hashes,
Git HEADs and tags match the initial baseline. Official assets are unchanged.
Read-only before/after checksums for Desktop Icon/Layout, Workspace/Sidebar,
Singles/settings, Installed Application and Company all match. The pre-existing
ERPNext banking/yarn.lock modification is preserved. The finalization handoff
records the resulting development commit and remote verification; version
remains 1.3.0. No actual setup or migration was run on the development site.

## Release plan and remaining blockers

The three approved commits are development ancestors: packaging 1841082,
CORE-001 fc5ab92, and CORE-002 29f8369. Stable/develop have divergent histories
with equivalent earlier theme/About patches and separate version bumps.

After real acceptance AND explicit approval, promote only these patches from
verified stable base 2ca1918 with normal cherry-pick -x:

1. `1841082cf7e6fc265ba68149534281d5e7b96955` — preserve packaging compatibility.
2. `fc5ab92d6dc1de4f3904bd3ac4417850145c89d9` — CORE-001.
3. `29f83697343e674fe4c626cf720a50b827f20439` — CORE-002 and acceptance docs.
4. Approved migration-safety correction commit from the final development handoff.

Then make version-only commits declaring 1.3.1 on both develop and version-16,
verify approved content and run the safe checks. Create annotated v1.3.1 on the
final stable commit and publish only after the required explicit approval.
Do not replay unrelated/equivalent commits, merge blindly, force-push or rewrite
historical tags. Recheck remote changes before any promotion.

**Not ready to publish:** real en/de fresh acceptance, real customized-site
migration evidence and publication approval remain outstanding. This task
authorizes the correction's development commit/push only. No stable promotion,
version bump or tag is authorized or performed.
