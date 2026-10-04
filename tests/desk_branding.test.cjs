const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

test("native v16 sidebar keeps app identity and internal switches while removing only CRM advertising", () => {
  const source = fs.readFileSync(
    path.resolve(
      __dirname,
      "../../frappe/frappe/public/js/frappe/ui/sidebar/sidebar.js"
    ),
    "utf8"
  );
  const setup = source.slice(
    source.indexOf("\tsetup(workspace_title) {"),
    source.indexOf("\tadd_sidebar_card(")
  );
  assert.ok(
    setup.indexOf('trigger("sidebar_setup"') < setup.indexOf("this.prepare()")
  );
  const document = {};
  let handler;
  const $ = (target) =>
    target === document
      ? {
          off() {
            handler = undefined;
            return this;
          },
          on(_name, callback) {
            handler = callback;
            return this;
          },
        }
      : {};
  const app = {
    app_name: "erpnext",
    app_title: "ERPNext",
    app_logo_url: "native-logo",
    workspaces: ["CRM"],
  };
  const frappe = {
    ui: {},
    boot: {
      app_name_style: "App Name",
      app_data: [app],
      workspace_sidebar_item: { crm: { app: "erpnext" } },
      apps_data: { apps: [] },
      reybill_branding: { sidebar_labels: { ERPNext: "ReyBill" } },
    },
  };
  const context = { frappe, $, document, __: (value) => value };
  vm.runInNewContext(
    source.slice(source.indexOf("frappe.ui.Sidebar =")),
    context
  );
  const sidebar = Object.create(frappe.ui.Sidebar.prototype);
  Object.assign(sidebar, {
    sidebar_title: "CRM",
    workspace_title: "crm",
    all_sidebar_items: { crm: { module: "CRM" } },
    promotional_banners: [],
  });
  const adapter = fs.readFileSync(
    path.resolve(__dirname, "../reybill_core/public/js/desk_branding.js"),
    "utf8"
  );
  vm.runInNewContext(adapter, context);
  handler(null, { sidebar });
  const choose = sidebar.choose_app_name;
  const banner = sidebar.get_crm_banner;
  sidebar.choose_app_name();
  assert.equal(sidebar.header_subtitle, "ReyBill");
  assert.equal(frappe.current_app, app);
  assert.equal(app.app_title, "ERPNext");
  assert.equal(app.app_name, "erpnext");
  assert.equal(sidebar.app_logo_url, "native-logo");
  const other = { title: "Other extension" };
  sidebar.promotional_banners.push(other);
  sidebar.get_crm_banner("CRM");
  assert.deepEqual(sidebar.promotional_banners, [other]);
  sidebar.get_helpdesk_banner("Support");
  assert.equal(sidebar.promotional_banners.length, 2);
  assert.ok(
    sidebar.promotional_banners[1].link.startsWith("https://frappe.io/helpdesk")
  );
  frappe.boot.apps_data.apps.push({ name: "crm", route: "/crm" });
  sidebar.get_crm_banner("CRM");
  assert.equal(sidebar.promotional_banners.at(-1).link, "/crm");
  assert.equal(sidebar.promotional_banners.at(-1).is_internal, true);
  app.app_title = "Custom product";
  sidebar.choose_app_name();
  assert.equal(sidebar.header_subtitle, "Custom product");
  vm.runInNewContext(adapter, context);
  handler(null, { sidebar });
  assert.equal(sidebar.choose_app_name, choose);
  assert.equal(sidebar.get_crm_banner, banner);
  const count = sidebar.promotional_banners.length;
  sidebar.get_crm_banner("Sales");
  assert.equal(sidebar.promotional_banners.length, count);
});

test("native Help builder retains shortcuts and System Health and routes only About to ReyBill", () => {
  const source = fs.readFileSync(
    path.resolve(
      __dirname,
      "../../frappe/frappe/public/js/frappe/ui/sidebar/sidebar_header.js"
    ),
    "utf8"
  );
  const calls = [];
  const health = {
    name: "health-id",
    item_label: "System Health",
    item_type: "Route",
    route: "/desk/system-health-report",
  };
  const frappe = {
    ui: {},
    boot: {
      navbar_settings: {
        help_dropdown: [
          {
            name: "about-id",
            item_label: "About ReyBill",
            item_type: "Action",
            action: "reybill.about.show()",
          },
          {
            name: "keys-id",
            item_label: "Keyboard Shortcuts",
            item_type: "Action",
            action: "frappe.ui.toolbar.show_shortcuts(event)",
          },
          health,
          {
            name: "support-id",
            item_label: "ReyBill Support",
            item_type: "Route",
            route: "configured-support-destination",
          },
          { name: "hidden-id", item_label: "Hidden", hidden: 1 },
        ],
      },
    },
    utils: { eval: (action) => calls.push(action) },
  };
  vm.runInNewContext(source, { frappe });
  const header = Object.create(frappe.ui.SidebarHeader.prototype);
  header.get_custom_help_links = () => [];
  const items = header.get_help_siblings();
  assert.deepEqual(
    Array.from(items, (item) => item.label),
    ["About ReyBill", "Keyboard Shortcuts", "System Health", "ReyBill Support"]
  );
  items[0].onClick();
  items[1].onClick();
  assert.deepEqual(calls, [
    "reybill.about.show()",
    "frappe.ui.toolbar.show_shortcuts(event)",
  ]);
  assert.equal(items[1].shortcut, "Shift+/");
  assert.equal(items[2].url, health.route);
  assert.equal(items[3].url, "configured-support-destination");
});
