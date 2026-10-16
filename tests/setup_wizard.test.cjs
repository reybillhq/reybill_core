const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..");
const nativePath = path.resolve(
  root,
  "../frappe/frappe/desk/page/setup_wizard/setup_wizard.js"
);
const nativeSource = fs.readFileSync(nativePath, "utf8");
const adapter = fs.readFileSync(
  root + "/reybill_core/public/js/setup_wizard_branding.js",
  "utf8"
);
const translateSource = fs.readFileSync(
  path.resolve(root, "../frappe/frappe/public/js/frappe/translate.js"),
  "utf8"
);

function runtime() {
  const calls = [];
  let stageListener;
  const node = {
    appendTo(parent) {
      calls.push(["append", parent]);
      return this;
    },
    append(value) {
      calls.push(["append-child", value]);
      return this;
    },
    find(selector) {
      calls.push(["find", selector]);
      return this;
    },
    html(value) {
      calls.push(["html", value]);
      return this;
    },
    css(value) {
      calls.push(["css", value]);
      return this;
    },
    on(event, callback) {
      calls.push(["on", event, callback]);
      return this;
    },
    hide() {
      calls.push(["hide"]);
      return this;
    },
    show() {
      calls.push(["show"]);
      return this;
    },
    remove() {
      calls.push(["remove"]);
      return this;
    },
  };
  const $ = (value) => {
    calls.push(["$", value]);
    return node;
  };
  $.extend = Object.assign;
  $.each = (items, callback) =>
    items.forEach((item, index) => callback(index, item));
  const context = {
    $,
    window: { location: { href: "" } },
    localStorage: { current_route: "/desk/crm" },
    cint: Number,
    cstr: String,
    setTimeout(callback, delay) {
      calls.push(["timeout", delay]);
      callback();
    },
    document: {},
  };
  const frappe = {
    boot: { setup_complete: false, apps_data: { default_path: "/desk" } },
    _messages: {},
    pages: { "setup-wizard": {} },
    ui: {
      Slides: class {
        constructor(args) {
          Object.assign(this, args);
        }
      },
      Slide: class {},
    },
    telemetry: { can_enable: () => false, enabled: false },
    realtime: {
      on(event, callback) {
        calls.push(["realtime", event]);
        stageListener = callback;
      },
    },
    session: { user: "Administrator" },
    set_route(...args) {
      calls.push(["route", ...args]);
    },
    get_route: () => ["setup-wizard", "0"],
    provide(namespace) {
      namespace
        .split(".")
        .reduce((object, key) => (object[key] ||= {}), context);
    },
    call(options) {
      calls.push(["call", options.method]);
      if (options.method.endsWith("load_languages"))
        options.callback({ message: { languages: [] } });
      if (options.method.endsWith("load_user_details"))
        options.callback({ message: {} });
      return options;
    },
  };
  context.frappe = frappe;
  vm.createContext(context);
  vm.runInContext(translateSource, context);
  context.__ = context.window.__;
  vm.runInContext(nativeSource, context);
  const prototype = frappe.setup.SetupWizard.prototype;
  const before = Object.fromEntries(
    Object.getOwnPropertyNames(prototype).map((name) => [name, prototype[name]])
  );
  const install = () => vm.runInContext(adapter, context);
  const wizard = () =>
    Object.assign(Object.create(prototype), {
      parent: "fixture",
      container: node,
      slides: [{ name: "welcome" }, { name: "organization" }],
      page_name: "setup-wizard",
      $working_state: node,
      $abort_btn: node,
    });
  return {
    context,
    frappe,
    calls,
    node,
    prototype,
    before,
    install,
    wizard,
    progress: (data) => stageListener(data),
  };
}

test("English, German and locale fallback use native i18n before the first HTML construction", () => {
  const r = runtime();
  r.install();
  for (const [messages, expected] of [
    [{}, "Starting ReyBill..."],
    [
      {
        "Starting Frappe ...": "Frappé starten...",
        "Starting ReyBill...:ReyBill Setup Wizard": "ReyBill wird gestartet...",
      },
      "ReyBill wird gestartet...",
    ],
    [
      { "Starting Frappe ...": "Démarrage de Frappe..." },
      "Starting ReyBill...",
    ],
    [
      {
        "Starting Frappe ...": "Démarrage de Frappe...",
        "Starting ReyBill...:ReyBill Setup Wizard": "Démarrage de ReyBill...",
      },
      "Démarrage de ReyBill...",
    ],
  ]) {
    r.frappe._messages = messages; // Native load_messages replaces this during a language switch.
    r.calls.length = 0;
    r.wizard().show_working_state();
    const firstHTML = r.calls.find(
      ([action, value]) =>
        action === "$" && value.includes?.("setup-in-progress")
    )[1];
    assert.ok(firstHTML.includes(expected), firstHTML);
    assert.ok(!/Frappe|Frappé|ERPNext/.test(firstHTML), firstHTML);
    assert.ok(
      !r.calls.some(([action]) => action === "html"),
      "no late text replacement"
    );
  }
});

test("native requires loads ReyBill before before_load, construction and first slide", () => {
  const r = runtime();
  r.frappe.boot.setup_wizard_requires = [
    "/assets/reybill_core/js/setup_wizard_branding.js",
  ];
  r.frappe.require = (assets, callback) => {
    assert.deepEqual(Array.from(assets), r.frappe.boot.setup_wizard_requires);
    r.install();
    callback();
  };
  r.frappe.setup.on("before_load", () => {
    assert.equal(r.prototype.get_message.reybill_setup_branding, true);
  });
  // Only prevent form construction in this contract fixture; keep the native on_page_load.
  const show = r.prototype.show_slide;
  r.prototype.show_slide = (id) => r.calls.push(["slide", id]);
  r.frappe.pages["setup-wizard"].on_page_load("fixture");
  r.prototype.show_slide = show;
  assert.ok(r.calls.some(([action, id]) => action === "slide" && id === 0));
  assert.deepEqual(
    Array.from(r.frappe.setup.slides, (slide) => slide.name),
    ["welcome", "user"]
  );
  assert.ok(
    !r.calls.some(
      ([action, method]) =>
        action === "call" && method.endsWith("setup_complete")
    )
  );
});

test("reloading is idempotent and only the wizard message renderer changes", () => {
  const r = runtime();
  const translator = r.context.__;
  r.install();
  const wrapped = r.prototype.get_message;
  r.install();
  r.install();
  assert.equal(r.prototype.get_message, wrapped);
  assert.equal(r.context.__, translator);
  for (const [name, method] of Object.entries(r.before)) {
    if (name !== "get_message") assert.equal(r.prototype[name], method, name);
  }
  const receiver = {};
  let seen;
  const native = function (...args) {
    seen = { receiver: this, args };
    return receiver;
  };
  r.prototype.get_message = native;
  r.install();
  assert.equal(
    r.prototype.get_message.call(receiver, "Neutral title", "Neutral text", 17),
    receiver
  );
  assert.equal(seen.receiver, receiver);
  assert.deepEqual(seen.args, ["Neutral title", "Neutral text", 17]);
  const old = r.frappe.setup;
  delete r.frappe.setup;
  assert.doesNotThrow(r.install); // No effect on a normal Desk page.
  r.frappe.setup = old;
});

test("native progress math, neutral messages, error diagnostics and completion redirects survive", () => {
  const r = runtime();
  r.install();
  const wizard = r.wizard();
  wizard.listen_for_setup_stages();
  r.progress({ stage_status: "Setting up company", progress: [1, 4] });
  assert.ok(
    r.calls.some(
      ([action, value]) => action === "html" && value === "Setting up company"
    )
  );
  assert.ok(
    r.calls.some(([action, value]) => action === "css" && value.width === "50%")
  );
  r.progress({ fail_msg: "frappe.ValidationError: ERPNext dependency failed" });
  assert.ok(
    r.calls.some(
      ([action, value]) =>
        action === "html" &&
        value.includes?.("frappe.ValidationError: ERPNext dependency failed")
    )
  );
  r.progress({ status: "ok" });
  assert.equal(r.context.window.location.href, "/desk/crm");
  assert.ok(
    r.calls.some(
      ([action, value]) => action === "html" && value === "Setup Complete"
    )
  );
  assert.ok(
    r.calls.some(([action, value]) => action === "timeout" && value === 2000)
  );
  assert.equal(r.prototype.action_on_complete, r.before.action_on_complete);
  assert.equal(r.prototype.handle_enter_press, r.before.handle_enter_press);
  assert.equal(r.prototype.attach_abort_button, r.before.attach_abort_button);
});

test("all original non-branding wizard HTML remains byte-for-byte native", () => {
  const r = runtime();
  const wizard = r.wizard();
  r.before.get_message.call(
    wizard,
    "Setting up your system",
    "Starting Frappe ..."
  );
  const original = r.calls.find(([action]) => action === "$")[1];
  r.calls.length = 0;
  r.install();
  wizard.get_message("Setting up your system", "Starting Frappe ...");
  const branded = r.calls.find(([action]) => action === "$")[1];
  assert.equal(
    branded,
    original.replace("Starting Frappe ...", "Starting ReyBill...")
  );
  for (const message of [
    "Wrapping up",
    "Refreshing...",
    "Retry",
    "ERPNext dependency unavailable",
  ]) {
    r.calls.length = 0;
    wizard.get_message("Neutral", message);
    assert.ok(r.calls[0][1].includes(message));
  }
});

test("audited native steps and translatable product-branding inventory stay explicit", () => {
  const r = runtime();
  r.install();
  const erpSource = fs.readFileSync(
    path.resolve(root, "../erpnext/erpnext/public/js/setup_wizard.js"),
    "utf8"
  );
  vm.runInContext(erpSource, r.context);
  r.frappe.setup.run_event("before_load");
  assert.deepEqual(
    Array.from(r.frappe.setup.slides, (slide) => slide.name),
    ["welcome", "user", "persona", "organization"]
  );
  const files = [
    nativePath,
    path.resolve(
      root,
      "../frappe/frappe/desk/page/setup_wizard/setup_wizard.py"
    ),
    path.resolve(root, "../frappe/frappe/public/js/frappe/ui/slides.js"),
    path.resolve(root, "../erpnext/erpnext/setup/setup_wizard/setup_wizard.py"),
    path.resolve(root, "../erpnext/erpnext/public/js/setup_wizard.js"),
  ];
  const branding = files.flatMap((file) =>
    Array.from(
      fs.readFileSync(file, "utf8").matchAll(/_\(\s*"([^"\n]*)"/g),
      (match) => match[1]
    ).filter((text) => /Frappe|Frappé|ERPNext/.test(text))
  );
  assert.deepEqual(branding, ["Starting Frappe ..."]);
});
