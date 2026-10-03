# ReyBill White-Label Naming audit — v0.0.2

Audit date: 2026-10-04. Site: `reybill.localhost`. Installed source: Frappe 16.36.1 and ERPNext 16.37.0.

## Scope and evidence

This is an inventory, not authorization to implement the remaining surfaces. This milestone changes only Desk display translations and the two requested menu entries. Core source and persistent standard records remain untouched. Colors, layout, logos, login branding, and the About dialog have not been redesigned.

The source scan covers both installed repositories, including templates, Python, JavaScript, JSON, development examples and localization catalogs. It searches `Frappe`, `Frappe Framework`, `Frappe Support`, `ERPNext`, and vendor URLs. It excludes Git internals, dependencies, generated bundles/source maps, ignored files and binary assets. Image branding is inspected separately through the configured asset paths and browser screenshots.

[WHITE_LABEL_SOURCE_INVENTORY.csv](WHITE_LABEL_SOURCE_INVENTORY.csv) contains every matching source line from that scan, with its path, line number, matched terms, classification and rationale. There are 10,092 matching lines: 21 **SAFE TO WHITE-LABEL**, 5,614 **INTERNAL — DO NOT TOUCH**, and 4,457 **NEEDS REVIEW**. The line classifications are conservative: untranslated catalog entries, unfamiliar messages, external-service names and vendor links remain review candidates rather than being assumed safe. A line may contain multiple occurrences; the inventory groups these at their source location. It does not copy full source lines or credentials.

Lowercase Python imports, app IDs, database names, asset namespaces, routes and API paths are technical identifiers, regardless of whether a textual scan matches them. The inventory does not authorize renaming them. A safe visible caption and an internal record key can have identical text; only the rendered caption is a white-label candidate.

The live database inspection covered 35 Desktop Icons, 19 Workspaces, 32 Workspace Sidebars, 5 Navbar Items, 13,760 DocFields, 43 Print Formats, 1 Email Template, 4 Notifications, 1 Website Theme, and the Website/System/Navbar settings. There were no Web Page or Letter Head records. Sent emails, historical notification logs, transaction contents, attachments and generated historical PDFs were not inspected. Their branding can depend on user-authored content and cannot be inferred from current templates alone.

[WHITE_LABEL_SITE_INVENTORY.csv](WHITE_LABEL_SITE_INVENTORY.csv) identifies 32 matched site field entries, including the Framework caption and the two application-name settings. Entries record brand terms and schema/record references, not account secrets or email bodies.

## Classification

- **SAFE TO WHITE-LABEL**: customer-facing presentation can be adapted through supported settings or app extensions while preserving its underlying identity and behavior.
- **INTERNAL — DO NOT TOUCH**: technical identity, route, relationship, source identifier, protocol, migration key, diagnostic identifier, or source attribution that must remain intact.
- **NEEDS REVIEW**: ambiguous context, third-party service identity, external destination, attribution, authentication identity, or content requiring a separate decision.

## Desktop, workspace, launcher and search

| Surface / occurrence | Evidence and live state | Classification | v0.0.2 outcome / next decision |
| --- | --- | --- | --- |
| Desktop `Framework` caption | `frappe/frappe/desktop_icon/framework.json`; live name and label `Framework`, visible, fallback link `/desk/build` | SAFE TO WHITE-LABEL | Displays **ReyBill Work** through `__()`. The internal name, original label, visibility, children and target remain intact. |
| Framework app folder | `frappe/frappe/desk/page/desktop/desktop.js`, `DesktopIcon.setup_click()` | SAFE TO WHITE-LABEL | Native click opens its child-icon folder when children exist; its translated title is **ReyBill Work**. It is not forced into a different navigation mode. |
| `ERPNext Settings` caption | `erpnext/erpnext/desktop_icon/erpnext_settings.json`; live visible icon links to the existing Workspace Sidebar | SAFE TO WHITE-LABEL | Displays **ReyBill Settings**. The native first sidebar destination is Global Defaults. |
| `ERPNext` app caption | `erpnext/erpnext/desktop_icon/erpnext.json`; live standard record is already hidden | SAFE TO WHITE-LABEL | Exact display mapping is **ReyBill**. The record stays hidden; no new item is created. |
| `Frappe Framework` app title | `frappe/frappe/hooks.py:6`; no separate live Desktop Icon under this name | SAFE TO WHITE-LABEL | Exact translated Desk display is **ReyBill Framework** wherever this title passes through `__()`. |
| Workspace/sidebar title `ERPNext Settings` | `erpnext/erpnext/workspace_sidebar/erpnext_settings.json`; Workspace label/title and sidebar title exist on site | SAFE TO WHITE-LABEL | Existing translated captions inherit **ReyBill Settings**; stored names/titles and sidebar lookup keys stay unchanged. |
| Sidebar app subtitle `ERPNext` | Rendered beneath **ReyBill Settings** on Global Defaults; `public/js/frappe/ui/sidebar/sidebar_header.html` inserts `header_subtitle` directly without `__()` | NEEDS REVIEW | Still visible. This is not a Desktop Icon caption. It needs a separate render-only extension: changing app metadata used by title lookups or parent navigation keys would exceed the current presentation mappings. |
| Workspace names, `link_to`, `parent_icon`, sidebar map keys | Desktop and sidebar JSON plus `desktop_icon.py`, `desktop.js`, `sidebar.js`; parent groups include `Framework` and `ERPNext` | INTERNAL — DO NOT TOUCH | Original keys retained. Relabeling records would risk routing, role filtering, child grouping and saved layouts. |
| App launcher and app switcher titles | `frappe/frappe/apps.py`, `boot.py`, app `add_to_apps_screen` hooks; Desk menu uses translated display labels | SAFE TO WHITE-LABEL | Desk translated exact labels use the mappings. Server-rendered launcher responses and other app entry points are separately scoped; no global app metadata override was added. |
| App IDs, launcher routes and permissions | `apps.py`, `get_default_path()`, `get_route()`, app permission hooks | INTERNAL — DO NOT TOUCH | `frappe`, `erpnext`, app targets, default-app IDs and permission methods remain unchanged. |
| Search/command palette results | `frappe/frappe/public/js/frappe/ui/toolbar/search_utils.js`, `awesome_bar.js`; Desktop Icon metadata supplies label and target | SAFE TO WHITE-LABEL | Results rendered through `__()` inherit exact caption mappings. Raw search response keys, record names and commands stay original. Additional untranslatable result types need separate review. |
| Search/API payload identifiers | Awesome Bar item type `Desktop Icon`, DocType/report/page identifiers, method paths | INTERNAL — DO NOT TOUCH | No response-key or command rewrites. |
| CRM and Support workspace notices | Live Workspace `CRM.content` references **Frappe CRM**; `Support.content` references **Frappe Helpdesk**. Shipped workspace JSON contains deprecation notices. | NEEDS REVIEW | These identify other products and their destinations. They remain unchanged. |

## Profile, Navbar/Help and About

| Surface / occurrence | Evidence | Classification | v0.0.2 outcome / next decision |
| --- | --- | --- | --- |
| Desktop profile `About` | `desktop.js`, `DesktopPage.setup_avatar()` | SAFE TO WHITE-LABEL | **About ReyBill**, with the original `frappe.ui.toolbar.show_about()` callback. |
| Desktop profile `Frappe Support` | Same native method opens `https://support.frappe.io/help` | SAFE TO WHITE-LABEL | **ReyBill Support**, opening the centralized ReyBill destination in a new tab. |
| Equivalent Help/Navbar items | Live Navbar Items originally named `About` and `Frappe Support`; `Navbar Settings.help_dropdown` is included in boot | SAFE TO WHITE-LABEL | Copies of the boot entries display the new labels; Support gets the centralized URL. Stored child names, actions and standard sync keys are retained. |
| Other menu actions | Edit Profile, Toggle Theme, Reset Desktop Layout, Logout, Keyboard Shortcuts and System Health | INTERNAL — DO NOT TOUCH | Original behavior, routes, callbacks, conditions and order retained. |
| Current About dialog title `About` | `frappe/frappe/public/js/frappe/ui/toolbar/about.js` | SAFE TO WHITE-LABEL | The entry point is renamed; the dialog itself retains its existing title and content for this milestone. |
| Frappe wordmark and image alternative text | About dialog uses `/assets/frappe/images/frappe-comp-logo.svg`, `alt="Frappe"` | SAFE TO WHITE-LABEL | Still visible. Candidate for the next app-owned About experience. |
| `Frappe Framework Version` heading | `about.js:35`; exact phrase includes `Version` | SAFE TO WHITE-LABEL | Still visible; the exact `Frappe Framework` mapping does not replace this longer phrase. |
| Technical framework version `frappe: …` | `about.js`, framework version row | INTERNAL — DO NOT TOUCH | Preserve truthful package/version identifiers in diagnostics and copied information. A future dialog can offer an additional friendly caption. |
| Installed ERPNext title and version | About app rows use `__(app.title)` and separately show `erpnext: …`; icons are supplied by core version metadata | SAFE TO WHITE-LABEL / INTERNAL — DO NOT TOUCH | The exact translated title becomes **ReyBill**. The ERPNext logo and technical `erpnext:` version remain. |
| About Website, Source Code and Forum links | `https://frappe.io/`, `https://github.com/frappe`, `https://discuss.frappe.io` | NEEDS REVIEW | Still original destinations. Choose product links and upstream attribution policy for the next About milestone. |
| About Cloud support block | Conditional `frappe.boot.is_fc_site`; **Frappe Support**, **Visit Frappe Support Portal**, `https://frappecloud.com/support` | NEEDS REVIEW | Remains conditional and unchanged. It is inside About, not the renamed profile/Help entries. |
| About Cloud update link | `about.js`: Frappe Cloud dashboard link appears only for Cloud sites with updates | NEEDS REVIEW | Preserve hosting/update behavior until an explicit product decision. |
| About footer attribution | `© Frappe Technologies Pvt. Ltd. and contributors` | NEEDS REVIEW | Still visible. Preserve upstream attribution when designing its replacement. |
| Copy App Versions and per-app copy behavior | `about.js`, `frappe.utils.change_log.get_versions` | INTERNAL — DO NOT TOUCH | Existing backend, technical names, branch/version information and copy behavior remain intact. |

The About dialog must be considered as a whole in the next milestone. Its tagline, social destinations, vendor wordmark, framework heading, app logos, attribution, version details, conditional support and update controls all need an intentional design. No dedicated About replacement hook was found in the installed source. A future app-owned dialog can be selected through the supported Navbar Action configuration and the scoped Desktop page adapter without editing `frappe.ui.misc.about` or `show_about`.

## Login, titles, logos and authentication

| Surface / occurrence | Evidence and live state | Classification | Next decision |
| --- | --- | --- | --- |
| Login application name | `frappe/frappe/www/login.py:53,149`; Website Settings and System Settings both have `app_name = Frappe` | SAFE TO WHITE-LABEL | Settings remain unchanged. The live v16 login shows **Sign In** and browser title **Login**, with an ERPNext logo; no literal Frappe/ERPNext text appeared in its visible body. Use supported settings in a separate milestone. |
| Browser/page title default | `frappe/frappe/www/desk.py:61`, `www/desk.html`, Website Settings title options | SAFE TO WHITE-LABEL | Desk's initial app-name default remains Frappe; individual Desk routes set their own page titles. Do not rename routes or page records to change titles. |
| Favicon and splash/login/Desktop logos | Website Settings `favicon`/`app_logo` and Navbar Settings `app_logo` are unset. Live login uses `/assets/erpnext/images/erpnext-logo.svg` and `/assets/erpnext/images/erpnext-favicon.svg`; Desktop Framework and About retain Frappe assets. | SAFE TO WHITE-LABEL | Existing graphics remain. Native hooks/fallbacks select the assets even when settings are empty. Future assets belong in ReyBill Core and are selected through settings/hooks. |
| Asset namespaces and filenames | `/assets/frappe`, `/assets/erpnext`, bundle names and image paths | INTERNAL — DO NOT TOUCH | Changing the visible graphic does not require renaming existing technical asset references. |
| OTP issuer default `Frappe Framework` | `System Settings.otp_issuer_name`, JSON default at `system_settings.json:382` | NEEDS REVIEW | This is the issuer shown in authenticator apps, not a Desktop caption. Existing enrollments and re-enrollment implications need explicit review. |
| Social Login Provider `Frappe` | Live `Social Login Key.social_login_provider` options | NEEDS REVIEW | Identifies an OAuth provider and participates in provider configuration. Do not rename the stored option. |

## Setup, settings, notifications and errors

| Surface / occurrence | Evidence | Classification | Next decision |
| --- | --- | --- | --- |
| Setup Wizard `Starting Frappe ...` | `frappe/frappe/desk/page/setup_wizard/setup_wizard.js:315` | SAFE TO WHITE-LABEL | Longer phrase remains unchanged. Site has setup complete; wizard was not restarted. |
| ERPNext setup sample blog | `erpnext/erpnext/setup/setup_wizard/data/sample_blog_post.html` | SAFE TO WHITE-LABEL | Potential generated content, unchanged. No live Web Page records exist. |
| Setup internals | Installer methods, completed-app tracking, company/chart setup and setup routes | INTERNAL — DO NOT TOUCH | No setup lifecycle or business defaults changed. |
| Theme option `Frappe Light` | `frappe/frappe/public/js/frappe/ui/theme_switcher.js:59` | SAFE TO WHITE-LABEL | Remains in the native theme picker. Theme names/stored values and colors are outside this milestone. |
| User onboarding `Welcome to Frappe!` | `user_onboarding.bundle.js` | SAFE TO WHITE-LABEL | Source occurrence remains conditional on onboarding configuration. |
| Item stock description mentioning ERPNext | Live `Item.is_stock_item` DocField description; Item JSON and JS | SAFE TO WHITE-LABEL | Longer explanatory text remains unchanged; only its presentation should change later. |
| `ERPNext User ID` field caption | Live Employee Group Table DocField and shipped JSON | SAFE TO WHITE-LABEL | Caption candidate; `user_id` field and links remain technical. |
| Naming-series help mentioning ERPNext | Live `Document Naming Settings.help_html`; `naming_series.js` | NEEDS REVIEW | Describes dependency-specific variables `.FY.`/`.ABBR.`. Preserve variable syntax and dependency accuracy. |
| SMS settings ERPNext example values | Live `SMS Settings.parameters` description | NEEDS REVIEW | Example parameters can be copied into real provider configurations. No actual gateway parameters changed. |
| Frappe Mail labels and service option | Live Email Account metadata: **Frappe Mail Site**, **Validate Frappe Mail Settings**, service **Frappe Mail** | NEEDS REVIEW | These identify an external service; the service option also drives behavior. Preserve provider identity and stored values. |
| Frappe CRM labels and synchronization notices | Live CRM Settings metadata and `crm/frappe_crm_api.py` | NEEDS REVIEW | External product integration, permission and synchronization semantics remain intact. |
| `Frappe CRM Allowed User` DocType option | Live CRM Settings `allowed_users.options`; core DocType definition | INTERNAL — DO NOT TOUCH | A link target / technical DocType name. |
| Generic ERPNext notification/error prose | Source inventory contains validation, stock, integration and migration messages | NEEDS REVIEW | Review each trigger and whether the name denotes ReyBill presentation or a required dependency/product. No blanket substitution. |
| Current Notification definitions | Four live Notification records scanned; no target brand names found in subject/message fields | SAFE TO WHITE-LABEL | No naming changes needed in these definitions. Historical delivered notifications were not scanned. |
| 404 and server-error pages | `frappe/frappe/www/404.html`, `error.html`; generic Page not found / Server Error text; server error may expose diagnostic details | SAFE TO WHITE-LABEL / INTERNAL — DO NOT TOUCH | Generic error presentation can be branded later; traceback packages/classes and error identifiers remain truthful. |
| Technical headers and diagnostics | `X-Frappe-*`, request IDs, class names, log types and package names | INTERNAL — DO NOT TOUCH | Keep wire protocols and diagnostics intact. |

## Emails, print/PDF, website and footer

| Surface / occurrence | Evidence and live state | Classification | Next decision |
| --- | --- | --- | --- |
| Email masthead name/logo | `frappe/frappe/templates/emails/standard.html`; variables `brand_name`, `brand_logo`, `site_url`; fallback framework logo and website | SAFE TO WHITE-LABEL | Use app/site branding context later. No emails were sent during validation. |
| Email sender-name fallback `Frappe` | `Email Account.get_smtp_server`, default sender configuration in `email_account.py` | SAFE TO WHITE-LABEL | Separate sender display from delivery address/provider settings. No account configuration changed. |
| Configured Email Template | One live Email Template inspected; no target terms found in subject/response fields | SAFE TO WHITE-LABEL | No current matching template body. Historical messages and user-authored content remain outside this scan. |
| ERPNext email/footer setup default | `erpnext/erpnext/setup/install.py` defines ERPNext footer HTML | SAFE TO WHITE-LABEL | Installation default does not prove the current site's sent-email appearance. Review actual sender/footer configuration before changing it. |
| Email transport identifiers | `X-Frappe-Site`, SMTP/OAuth settings, Frappe Mail classes | INTERNAL — DO NOT TOUCH | Preserve delivery behavior and provider configuration. |
| Print Format / PDF surfaces | 43 live Print Formats scanned, no target terms in HTML/builder/format-data fields; no Letter Head records | SAFE TO WHITE-LABEL | No matching current print definitions found. Dynamic document content, future letterheads and historical PDFs require separate checks. No transaction was created solely for the audit. |
| PDF renderer | `frappe/frappe/utils/pdf.py`, `FrappePDFKit` and underlying renderer setup | INTERNAL — DO NOT TOUCH | Technical renderer names and behavior remain unchanged. |
| Website powered footer | Frappe `templates/includes/footer/footer_powered.html`: **Built on Frappe**; ERPNext counterpart: **Powered by ERPNext** | SAFE TO WHITE-LABEL | Existing website templates remain. Review supported footer settings/template selection in the next milestone. |
| Website Settings footer and theme | Live footer/copyright strings empty, Website Theme `Standard`; one theme and no Web Pages | SAFE TO WHITE-LABEL | No website branding configuration changed. Empty settings do not imply every fallback footer is absent. |
| HTML source attribution | `frappe/frappe/templates/base.html` comment `Built on Frappe` | INTERNAL — DO NOT TOUCH | Not rendered customer text; no change needed. |
| `ERPNext Certification` and banking page fallback | `erpnext/erpnext/www/payment_setup_certification.html`; `www/banking.py` | NEEDS REVIEW | Certification may identify an actual service/product. Banking's fallback app caption is a presentation candidate, but both are outside this milestone. |
| Documentation, forum, school, marketplace and issue links | Source inventory; ERPNext setup Help definitions; `help_links.js`, field documentation URLs | NEEDS REVIEW | Preserve useful destinations until ReyBill equivalents or an explicit upstream-link policy exist. |

## Implementation boundaries and validation

The four Desktop mappings are merged into a copy of Desk boot's `__messages`. This is an exact-string display translation, so other Desk captions using the same complete strings inherit the naming. It does not alter substrings such as `Frappe Framework Version`, website settings, server-side `_()` translations, database labels or identifiers. Generic `About` and `Frappe Support` are not globally translated: only the requested menu models are adapted.

The Help/Navbar boot document is copied before changing its requested entries. This avoids modifying the cached standard document or causing standard item sync to create duplicate rows on migration. In this installed v16 implementation, `frappe.sessions.get()` refreshes `navbar_settings` after `extend_bootinfo` (`sessions.py:184`). The supported `update_website_context` hook therefore reapplies presentation to a copy of the final boot context only when the template is `www/desk.html`. Other website pages are unaffected. Desktop's native `desktop_screen` event is used through `page_js["desktop"]`; the adapter wraps only the emitted page instance's `setup_avatar`, then changes the current avatar menu's two item models before display. It does not replace DOM text, override the global menu factory, or edit the native About function. The installed v16 menu/event contract is covered by the native-source regression test and live browser checks.

The only runtime support destination is defined in `reybill_core/branding.py` as `SUPPORT_URL`; it is exposed through boot to the Desktop adapter and reused for equivalent Navbar Route entries. No site settings or standard record setup/migration is necessary. Cache clearing activates the hooks; page JS is appended by Frappe's page loader, so no asset bundle rebuild is required.

Validation artifacts are in [validation/](validation/). The reset action is exercised with its native callback and page reload, while its deletion request is intercepted so the user's saved Desktop Layout is preserved. The support popup receives the configured destination, with its external network request intercepted. Opening the native theme picker does not save a different theme. Logout uses the explicitly approved temporary validation session only.

Core tracked-file fingerprints and site record fingerprints are compared with the pre-validation baseline. ERPNext's pre-existing `banking/yarn.lock` modification is preserved and is unrelated to this milestone. All ReyBill changes remain uncommitted pending review.
