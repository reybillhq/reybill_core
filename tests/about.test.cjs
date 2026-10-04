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
          version: "1.0.0",
          logos: { light: "official-black.svg", dark: "official-white.svg" },
          applications: ["ReyBill", "ReyBill Core"],
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
  assert.ok(dialog.body.html.includes("ReyBill Core 1.0.0"));
  assert.ok(
    dialog.body.html.includes(
      "Business management software powered by ReyBill."
    )
  );
  assert.ok(dialog.body.html.includes("Installed Applications"));
  const text = (dialog.body.html + dialog.footer.html).replace(/<[^>]*>/g, "");
  assert.doesNotMatch(text, /Frappe|ERPNext|frappe:|erpnext:/);
  assert.match(text, /© ReyBill Ltd/);
  assert.equal(frappe.ui.misc.about, nativeAbout);
  assert.equal(frappe.ui.toolbar.show_about, nativeAbout);
  assert.equal(frappe.versions, versions);
  assert.equal(frappe.boot.versions, versions);
  theme = "dark";
  reybill.about.show();
  assert.equal(count, 1);
  assert.ok(dialog.body.html.includes('src="official-white.svg"'));
  assert.doesNotMatch(dialog.body.html, /filter:|frappe\.io|github\.com/);
  frappe.boot.reybill_branding.about.version = '<img src="bad">';
  reybill.about.show();
  assert.ok(dialog.body.html.includes("&lt;img src=&quot;bad&quot;&gt;"));
});
