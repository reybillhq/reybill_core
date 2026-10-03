# ReyBill Core development rules

## Project and environment

- This repository is the `reybill_core` custom app for Frappe Framework v16 and ERPNext v16.
- Development site: `reybill.localhost`.
- Development branch: `develop`.
- Repository: `reybillhq/reybill_core`.

## Scope and compatibility

- Never modify Frappe or ERPNext core.
- Keep all ReyBill development inside this `reybill_core` repository.
- Preserve standard ERPNext/Frappe functionality and structure unless the user explicitly requests otherwise.
- Prefer official Frappe hooks, APIs, settings, fixtures, CSS variables, and extension points.
- Branding changes must change only branding, labels, logos, colors, and styling unless the user explicitly requests otherwise.
- Do not rename internal Frappe/ERPNext technical objects just for branding.
- Avoid fragile DOM hacks when a supported Frappe v16 mechanism exists.

## Security

- Never commit passwords, API keys, database credentials, tokens, or site secrets.
- Keep site configuration and secrets out of source-controlled code, assets, fixtures, and documentation.

## Development workflow

- Inspect the current Git branch and working tree before making changes. Preserve unrelated user changes.
- Test changes on `reybill.localhost`.
- Work in small, stable milestones and commit only after testing.
- Follow the repository's formatting and lint configuration.
- Describe changes, verification results, and any unresolved limitations before handing work back to the user.

## Initial milestone

- The initial task permits repository inspection, creating this development-rules file, and recommending a clean architecture.
- Do not implement branding or product features during this milestone.
- Summarize the current state and wait for user approval before proceeding to implementation.
