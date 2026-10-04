const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

test("native v16 avatar actions survive ReyBill About routing, repeated renders, and script reloads", () => {
  const nativeSource = fs.readFileSync(
    path.resolve(__dirname, "../../frappe/frappe/desk/page/desktop/desktop.js"),
    "utf8"
  );
  const method = nativeSource.slice(
    nativeSource.indexOf("\tsetup_avatar() {"),
    nativeSource.indexOf(
      "\n\t// `item.order`",
      nativeSource.indexOf("\tsetup_avatar() {")
    )
  );
  assert.ok(
    method.includes('label: "Frappe Support"'),
    "native method still matches adapter contract"
  );
  const calls = [];
  const avatar = {};
  const unrelatedParent = {};
  const document = { documentElement: { getAttribute: () => "light" } };
  let screenHandler;
  const $ = (target) => {
    if (target === document) {
      return {
        off() {
          screenHandler = undefined;
          return this;
        },
        on(_event, handler) {
          screenHandler = handler;
          return this;
        },
      };
    }
    return {
      get: () => (target === ".desktop-avatar" ? avatar : unrelatedParent),
      html() {},
    };
  };
  const frappe = {
    session: { user: "Administrator" },
    boot: {
      reybill_branding: {
        menu_labels: {
          About: "About ReyBill",
          "Frappe Support": "ReyBill Support",
        },
        support_url: "configured-support-destination",
      },
    },
    avatar: () => "native-avatar",
    menu_map: {
      unrelated: { parent: $("other"), menu_items: [{ label: "About" }] },
    },
    utils: { is_rtl: () => false },
    app: { logout: () => calls.push("logout") },
    ui: {
      ThemeSwitcher: function () {
        this.show = () => calls.push("theme");
      },
      toolbar: { show_about: () => calls.push("about") },
      create_menu(options) {
        const id = Object.keys(frappe.menu_map).length;
        frappe.menu_map[id] = { ...options };
      },
    },
  };
  const context = {
    frappe,
    reybill: { about: { show: () => calls.push("reybill-about") } },
    $,
    document,
    DEFAULT_MENU_ITEM_ORDER: 50,
    window: {
      open: (...args) => calls.push(args),
      location: { reload: () => calls.push("reload") },
    },
    reset_to_default: () => calls.push("reset"),
  };
  const nativeSetup = vm.runInNewContext(
    `(function ${method.trim()})`,
    context
  );
  const adapter = fs.readFileSync(
    path.resolve(__dirname, "../reybill_core/public/js/desktop_naming.js"),
    "utf8"
  );
  vm.runInNewContext(adapter, context);
  const extraCallback = () => calls.push("extra");
  const desktop = {
    setup_avatar: nativeSetup,
    desktop_menu_items: [{ label: "Extra", onClick: extraCallback }],
  };
  screenHandler(null, { desktop });
  const wrapped = desktop.setup_avatar;
  screenHandler(null, { desktop });
  assert.equal(desktop.setup_avatar, wrapped);
  desktop.setup_avatar();
  let items = frappe.menu_map[1].menu_items;
  assert.deepEqual(
    Array.from(items, (item) => item.label),
    [
      "Edit Profile",
      "Toggle Theme",
      "About ReyBill",
      "ReyBill Support",
      "Reset Desktop Layout",
      "Extra",
      "Logout",
    ]
  );
  assert.equal(items[0].url, "/desk/user/Administrator");
  assert.equal(items[5].onClick, extraCallback);
  for (const index of [1, 2, 3, 4, 5, 6]) items[index].onClick();
  assert.deepEqual(calls, [
    "theme",
    "reybill-about",
    ["configured-support-destination", "_blank", "noopener,noreferrer"],
    "reset",
    "reload",
    "extra",
    "logout",
  ]);
  assert.equal(frappe.menu_map.unrelated.menu_items[0].label, "About");
  vm.runInNewContext(adapter, context);
  screenHandler(null, { desktop });
  assert.equal(desktop.setup_avatar, wrapped);
  desktop.setup_avatar();
  items = frappe.menu_map[2].menu_items;
  assert.equal(items[2].label, "About ReyBill");
  assert.equal(items[3].label, "ReyBill Support");
});
