const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const nativeSource = fs.readFileSync(
  path.resolve(__dirname, "../../frappe/frappe/desk/page/desktop/desktop.js"),
  "utf8"
);
const adapter = fs.readFileSync(
  path.resolve(__dirname, "../reybill_core/public/js/desktop_naming.js"),
  "utf8"
);
const plain = (value) => JSON.parse(JSON.stringify(value));
const launcher = {
  label: "ReyBill Core",
  bg_color: "gray",
  link: "/app",
  link_type: "External",
  app: "reybill_core",
  icon_type: "App",
  parent_icon: null,
  icon: null,
  link_to: null,
  idx: 0,
  standard: 0,
  logo_url: "/assets/reybill_core/images/branding/Reybill_desk_icon.png",
  hidden: 0,
  name: "ReyBill Core",
  restrict_removal: 0,
  icon_image: null,
  child_icons: [],
};
const names = [
  "Framework",
  "Home",
  "Organization",
  "Accounting",
  "Assets",
  "Buying",
  "CRM",
  "Manufacturing",
  "Projects",
  "Quality",
  "Selling",
  "Stock",
  "Support",
  "Subcontracting",
  "ERPNext Settings",
];
const canonical = () =>
  names.map((name, idx) => ({
    name,
    label: name,
    idx,
    app: name === "Framework" ? "frappe" : "erpnext",
    icon_type: name === "Accounting" ? "Folder" : "Link",
    link: "/desk/original",
    hidden: 0,
    parent_icon: null,
    logo_url: `original-${name}.png`,
    roles: ["Desk User"],
    child_icons: [],
  }));

function harness(icons) {
  const calls = [];
  const events = new Map();
  const document = {};
  const $ = (target) => {
    assert.equal(target, document);
    return {
      off(name) {
        events.delete(name);
        return this;
      },
      on(name, handler) {
        events.set(name, handler);
        return this;
      },
    };
  };
  const boot = {
    desktop_icons: icons,
    app_data: [{ app_name: "reybill_core", app_title: "ReyBill ERP" }],
    reybill_branding: {
      excluded_desktop_launchers: [
        { app: "reybill_core", name: "ReyBill Core" },
      ],
      about: {
        applications: [{ title: "ReyBill Core", version: "1.3.0" }],
      },
    },
  };
  const frappe = {
    boot,
    session: { user: "isolated-contract-user" },
    pages: { desktop: {} },
    ui: { make_app_page: (options) => ({ ...options }) },
    call() {
      assert.fail("Desktop contracts must never invoke a persistence endpoint");
    },
  };
  const storage = {
    value: null,
    getItem() {
      return this.value;
    },
    setItem() {
      assert.fail("adapter must not overwrite saved browser state");
    },
    removeItem() {
      assert.fail("adapter must not clear saved browser state");
    },
  };
  const context = vm.createContext({
    frappe,
    $,
    document,
    localStorage: storage,
    __: (text) => text,
    DesktopIconGrid: function (options) {
      this.icons_data = options.icons_data;
      this.update_grid = () => calls.push("native-pane-update");
    },
  });
  const classSource = nativeSource.slice(
    nativeSource.indexOf("class DesktopPage {"),
    nativeSource.indexOf("class DesktopIconGrid {")
  );
  assert.ok(classSource.includes("frappe.desktop_icons = this.data"));
  assert.ok(classSource.includes("this.hidden_icons.push(icon)"));
  vm.runInContext(`${classSource}\nthis.DesktopPage = DesktopPage;`, context);
  const originalPrepare = context.DesktopPage.prototype.prepare;
  const nativeEvents = nativeSource.slice(
    nativeSource.indexOf('frappe.pages["desktop"].on_page_load'),
    nativeSource.indexOf("function get_workspaces_from_app_name")
  );
  vm.runInContext(nativeEvents, context);
  const nativeLoad = frappe.pages.desktop.on_page_load;
  frappe.pages.desktop.on_page_load = function (...args) {
    calls.push({ receiver: this, args });
    nativeLoad.apply(this, args);
    return "native-load-result";
  };
  // Exercise real sync_layout/prepare without invoking native DOM or persistence.
  context.DesktopPage.prototype.make = function () {
    this.sync_layout();
    this.prepare();
  };
  const paneSource = nativeSource.slice(
    nativeSource.indexOf("class IconsPane {"),
    nativeSource.indexOf("class InlineEditor {")
  );
  vm.runInContext(`${paneSource}\nthis.IconsPane = IconsPane;`, context);
  const install = () => vm.runInContext(adapter, context);
  install();
  const page = frappe.pages.desktop;
  const result = page.on_page_load.call(page, "original-wrapper");
  assert.equal(result, "native-load-result");
  assert.equal(calls[0].receiver, page);
  assert.deepEqual(calls[0].args, ["original-wrapper"]);
  const desktop = page.desktop_page;
  const show = (data) => {
    desktop.data = data;
    page.on_page_show();
    return {
      active: plain(desktop.apps_icons),
      removed: plain(desktop.hidden_icons),
    };
  };
  const removedPane = () => {
    const pane = Object.create(context.IconsPane.prototype);
    pane.wrapper = { removeClass() {}, append() {} };
    pane.setup = () => {};
    pane.show();
    return plain(pane.grid.icons_data);
  };
  return {
    frappe,
    desktop,
    page,
    show,
    removedPane,
    storage,
    install,
    originalPrepare,
  };
}

test("fresh default rendering excludes the confirmed launcher before native grid preparation", () => {
  const icons = [plain(launcher), ...canonical()];
  const before = plain(icons);
  const h = harness(icons);
  const registry = plain(h.frappe.boot.app_data);
  const about = plain(h.frappe.boot.reybill_branding.about);
  const state = h.show({});
  assert.deepEqual(
    state.active.map((icon) => icon.name),
    names
  );
  assert.deepEqual(state.removed, []);
  assert.equal(icons.length, before.length);
  assert.deepEqual(icons[0], before[0]);
  assert.deepEqual(h.frappe.boot.app_data, registry);
  assert.deepEqual(h.frappe.boot.reybill_branding.about, about);
});

test("saved customization and Removed Icons preserve every unrelated row and custom index", () => {
  const icons = canonical().reverse();
  icons.splice(3, 0, plain(launcher));
  icons[1].hidden = 1;
  const separateReybill = {
    name: "ERPNext",
    label: "ERPNext",
    app: "erpnext",
    hidden: 1,
    idx: 100,
    logo_url: "original-separate-reybill.png",
    link: "/app/home",
  };
  icons.push(separateReybill);
  icons.forEach((icon, index) => {
    icon.idx = 40 + index;
  });
  const saved = JSON.stringify(icons);
  const h = harness(canonical());
  h.storage.value = saved;
  const state = h.show(icons);
  assert.deepEqual(
    state.active,
    plain(icons.filter((icon) => icon !== icons[3] && icon.hidden !== 1))
  );
  assert.deepEqual(state.removed, [icons[1], separateReybill]);
  assert.deepEqual(h.removedPane(), state.removed);
  assert.equal(h.desktop.data, icons);
  assert.equal(h.desktop.data.length, 17);
  assert.equal(h.desktop.data[3].name, "ReyBill Core");
  assert.equal(h.storage.value, saved);
});

test("an already removed launcher is excluded without removing other ReyBill-owned shortcuts", () => {
  const validWork = { ...launcher, name: "Framework", label: "ReyBill Work" };
  const sameCaption = { ...launcher, name: "Personal Shortcut" };
  const otherApp = { ...launcher, app: "another_app" };
  const translated = {
    ...launcher,
    label: "Translated caption",
    hidden: 1,
    idx: 999,
  };
  const icons = [validWork, translated, sameCaption, otherApp];
  const h = harness(icons);
  const state = h.show({});
  assert.deepEqual(
    state.active.map((icon) => icon.name),
    ["Framework", "Personal Shortcut", "ReyBill Core"]
  );
  assert.deepEqual(state.removed, []);
  assert.deepEqual(h.removedPane(), []);
});

test("edit-mode preparation, repeated renders and script reloads never restore the launcher", () => {
  const rawSaved = [plain(launcher), ...canonical()];
  const h = harness(canonical());
  const prepare = h.desktop.prepare;
  const load = h.page.on_page_load;
  for (let reload = 0; reload < 3; reload++) {
    h.install();
    assert.equal(h.desktop.prepare, prepare);
    assert.equal(h.page.on_page_load, load);
    assert.deepEqual(
      h.show(rawSaved).active.map((icon) => icon.name),
      names
    );
    h.desktop.edit_mode = true;
    h.frappe.new_desktop_icons = [{ ...launcher, hidden: 1 }, ...canonical()];
    h.desktop.prepare();
    assert.deepEqual(
      plain(h.desktop.apps_icons).map((icon) => icon.name),
      names
    );
    assert.deepEqual(plain(h.desktop.hidden_icons), []);
    assert.deepEqual(h.removedPane(), []);
    h.desktop.edit_mode = false;
    assert.equal(rawSaved.length, names.length + 1);
  }
});

test("native preparation keeps its receiver, arguments, return and folder grouping", () => {
  const icons = canonical();
  icons.push({
    name: "Invoicing",
    label: "Invoicing",
    app: "erpnext",
    hidden: 0,
    idx: 29,
    parent_icon: "Accounting",
    icon_type: "Link",
  });
  const h = harness(icons);
  const state = h.show({});
  assert.equal(h.frappe.desktop_icons, icons);
  assert.deepEqual(
    state.active
      .find((icon) => icon.name === "Accounting")
      .child_icons.map((icon) => icon.name),
    ["Invoicing"]
  );
  const calls = [];
  const original = function (...args) {
    calls.push({ receiver: this, args });
    return "preserved-result";
  };
  h.desktop.prepare = original;
  h.install();
  assert.equal(h.desktop.prepare("argument"), "preserved-result");
  assert.equal(calls[0].receiver, h.desktop);
  assert.deepEqual(calls[0].args, ["argument"]);
  h.desktop.prepare = h.originalPrepare;
});
