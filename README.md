### ReyBill Core

Core branding and platform integration for ReyBill.

ReyBill Core **v1.0.0** is the first stable base for Frappe Framework v16 and
ERPNext v16. It includes Desktop naming/order, CRM and Help branding, ReyBill
About/Support, native Login/Forgot/Reset branding, favicon, app identity,
versioned official assets, SVG splash/fallback and theme-aware Desk logo.
Technical framework/app identities and ERP behavior remain intact.

See [release validation and known responsive observations](docs/validation/v1.0.0/RELEASE_VALIDATION.md)
and the [white-label audit](docs/WHITE_LABEL_AUDIT.md).

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench install-app reybill_core
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/reybill_core
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
