const assert = require("node:assert/strict");
const fs = require("node:fs");
const test = require("node:test");
const vm = require("node:vm");

test("Desktop logo follows native resolved themes and touches only brand-logo", () => {
  const handlers = {};
  const lookups = [];
  const attrs = { src: "native.svg", alt: "App Logo", width: "unchanged" };
  const logos = { light: "black.svg", dark: "white.svg" };
  let theme = "light";
  let exists = true;
  const calls = [];
  const ui = {
    get_current_theme: () => theme,
    set_theme(...args) {
      calls.push({ receiver: this, args });
      theme = args[0] || theme;
      return "native-result";
    },
  };
  const document = {
    getElementById(id) {
      lookups.push(id);
      return exists
        ? {
            setAttribute: (key, value) => {
              attrs[key] = value;
            },
          }
        : null;
    },
  };
  const jquery = () => ({
    off(name) {
      delete handlers[name];
      return this;
    },
    on(name, fn) {
      handlers[name] = fn;
      return this;
    },
  });
  const sandbox = {
    document,
    $: jquery,
    frappe: { ui, boot: { reybill_branding: { navbar_logos: logos } } },
  };
  const source = fs.readFileSync(
    "reybill_core/public/js/desktop_logo.js",
    "utf8"
  );
  vm.runInNewContext(source, sandbox);
  const wrapped = ui.set_theme;
  handlers["desktop_screen.reybill_logo"]();
  assert.equal(attrs.src, logos.light);
  assert.equal(ui.set_theme("dark", "extra"), "native-result");
  assert.equal(attrs.src, logos.dark);
  assert.deepEqual(calls[0].args, ["dark", "extra"]);
  assert.equal(calls[0].receiver, ui);
  theme = "light"; // Native Automatic mode resolves to the system's current theme.
  ui.set_theme();
  assert.equal(attrs.src, logos.light);
  vm.runInNewContext(source, sandbox);
  assert.equal(ui.set_theme, wrapped);
  assert.equal(Object.keys(handlers).length, 1);
  exists = false;
  assert.equal(ui.set_theme("dark"), "native-result");
  assert.equal(attrs.alt, "App Logo");
  assert.equal(attrs.width, "unchanged");
  assert.deepEqual([...new Set(lookups)], ["brand-logo"]);
});
