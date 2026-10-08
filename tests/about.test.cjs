const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

test("ReyBill About uses configured original assets, preserves diagnostics and never calls native About", () => {
  let count = 0;
  let theme = "light";
  const reybill = { about: {} };
  const nativeAbout = () => {
    throw new Error("Native About must not be called");
  };
  const versions = {
    frappe: "native-framework-version",
    erpnext: "native-erp-version",
  };
  const $ = (target) => ({
    addClass(value) {
      target.classes = value;
      return this;
    },
    removeClass() {
      return this;
    },
    html(value) {
      target.html = value;
      return this;
    },
  });
  const frappe = {
    provide() {},
    versions,
    boot: {
      versions,
      reybill_branding: {
        support_url: "configured-owned-url",
        about: {
          product_version: "16.37.0",
          logos: { light: "official-black.svg", dark: "official-white.svg" },
          company_name: "ReyBill Technologies Ltd",
          applications: [
            { title: "ReyBill Core", version: "1.0.0" },
            { title: "ReyBill Farm", version: "0.0.3" },
          ],
        },
      },
    },
    ui: {
      misc: { about: nativeAbout },
      toolbar: { show_about: nativeAbout },
      get_current_theme: () => theme,
      Dialog: function (options) {
        count++;
        this.title = options.title;
        this.wrapper = {};
        this.body = {};
        this.footer = {};
        this.show = () => {
          this.visible = true;
        };
      },
    },
    utils: {
      escape_html: (value) =>
        String(value)
          .replaceAll("&", "&amp;")
          .replaceAll('"', "&quot;")
          .replaceAll("<", "&lt;")
          .replaceAll(">", "&gt;"),
      icon: () => "<svg></svg>",
    },
  };
  const source = fs.readFileSync(
    path.resolve(__dirname, "../reybill_core/public/js/about.js"),
    "utf8"
  );
  vm.runInNewContext(source, { reybill, frappe, $, __: (value) => value });
  assert.equal(reybill.about.show(), false);
  const dialog = reybill.about.dialog;
  assert.equal(dialog.title, "About ReyBill");
  assert.ok(dialog.body.html.includes('src="official-black.svg"'));
  assert.ok(
    dialog.body.html.includes('href="configured-owned-url" target="_blank"')
  );
  assert.ok(dialog.body.html.includes("ReyBill v16.37.0"));
  assert.ok(dialog.body.html.includes('class="about-app-name">ReyBill Core'));
  assert.ok(dialog.body.html.includes('class="about-app-version">v1.0.0'));
  assert.ok(dialog.body.html.includes('class="about-app-name">ReyBill Farm'));
  assert.ok(dialog.body.html.includes('class="about-app-version">v0.0.3'));
  assert.equal(
    (dialog.body.html.match(/class="about-app-row"/g) || []).length,
    2
  );
  assert.ok(
    dialog.body.html.includes(
      "Business management software powered by ReyBill."
    )
  );
  assert.ok(dialog.body.html.includes("Installed Applications"));
  const text = (dialog.body.html + dialog.footer.html).replace(/<[^>]*>/g, "");
  assert.doesNotMatch(text, /Frappe|ERPNext|frappe:|erpnext:/);
  assert.match(text, /© ReyBill Technologies Ltd/);
  assert.equal(frappe.ui.misc.about, nativeAbout);
  assert.equal(frappe.ui.toolbar.show_about, nativeAbout);
  assert.equal(frappe.versions, versions);
  assert.equal(frappe.boot.versions, versions);
  theme = "dark";
  reybill.about.show();
  assert.equal(count, 1);
  assert.ok(dialog.body.html.includes('src="official-white.svg"'));
  assert.doesNotMatch(dialog.body.html, /filter:|frappe\.io|github\.com/);
  frappe.boot.reybill_branding.about.product_version = "16.40.2";
  frappe.boot.reybill_branding.about.applications.push({
    title: "ReyBill Water",
    version: "0.1.0",
  });
  reybill.about.show();
  assert.ok(dialog.body.html.includes("ReyBill v16.40.2"));
  assert.ok(dialog.body.html.includes("ReyBill Water"));
  assert.ok(dialog.body.html.includes('class="about-app-version">v0.1.0'));
  frappe.boot.reybill_branding.about.applications =
    frappe.boot.reybill_branding.about.applications.filter(
      (app) => app.title !== "ReyBill Farm"
    );
  reybill.about.show();
  assert.ok(!dialog.body.html.includes("ReyBill Farm"));
  frappe.boot.reybill_branding.about.product_version = '<img src="bad">';
  frappe.boot.reybill_branding.about.applications.push({
    title: '<script src="bad">',
    version: '<img src="bad">',
  });
  reybill.about.show();
  assert.ok(dialog.body.html.includes("&lt;img src=&quot;bad&quot;&gt;"));
  assert.ok(dialog.body.html.includes("&lt;script src=&quot;bad&quot;&gt;"));
  assert.ok(!dialog.body.html.includes('<script src="bad">'));
  frappe.boot.reybill_branding.about.product_version = null;
  frappe.boot.reybill_branding.about.applications = [
    { title: "Unversioned App", version: null },
  ];
  reybill.about.show();
  assert.ok(dialog.body.html.includes("Version unavailable"));
  assert.ok(!dialog.body.html.includes("vnull"));
  assert.ok(!dialog.body.html.includes("vundefined"));
  assert.equal(count, 1);
});
