const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const test = require("node:test");

const script = fs.readFileSync(
  "reybill_core/public/js/module_icons.js",
  "utf8"
);

test("module artwork follows stable names and preserves native folders, fallback, returns and repeated renders", async () => {
  class Element {
    constructor() {
      this.children = [];
      this.attributes = {};
      this.className = "";
      this.classList = {
        add: (name) => {
          this.className += ` ${name}`;
        },
        contains: (name) => this.className.split(/\s+/).includes(name),
      };
    }
    setAttribute(name, value) {
      this.attributes[name] = value;
    }
    getAttribute(name) {
      return this.attributes[name];
    }
    replaceChildren(...children) {
      this.children = children;
    }
    get firstElementChild() {
      return this.children[0];
    }
    get childElementCount() {
      return this.children.length;
    }
  }
  const events = {};
  const document = { createElement: () => new Element() };
  const jquery = {
    off: (event) => {
      delete events[event];
      return jquery;
    },
    on: (event, callback) => {
      events[event] = callback;
      return jquery;
    },
  };
  const records = [
    { name: "Accounting", label: "Accounting" },
    { name: "Home", label: "Home" },
  ];
  const fallbackCalls = [];
  const originalLookup = function (...args) {
    fallbackCalls.push({ args, receiver: this });
    return "native-home";
  };
  class Workspace {
    async show_page(page) {
      this._page = page;
      return "native-workspace-result";
    }
  }
  const frappe = {
    boot: {
      desktop_icons: records,
      reybill_branding: {
        module_icons: {
          Accounting: "approved-accounting",
          Invoicing: "approved-invoicing",
        },
      },
    },
    utils: {
      get_desktop_icon: originalLookup,
      get_desktop_icon_by_label: (label) =>
        records.find((r) => r.label === label),
    },
    views: { Workspace },
  };
  const context = vm.createContext({ frappe, document, $: () => jquery });
  const callback = () => "original-navigation";
  class DesktopIcon {
    constructor(name, label) {
      this.icon_data = Object.freeze({
        name,
        label,
        icon_type: "Folder",
        parent_icon: "original-parent",
        idx: 9,
      });
      this.container = new Element();
      this.icon = { children: () => ({ get: () => this.container }) };
      this.onClick = callback;
      this.nativeCalls = 0;
    }
    render_folder_thumbnail(...args) {
      this.nativeCalls++;
      this.nativeArgs = args;
      this.container.replaceChildren(new Element(), new Element());
      return "native-thumbnail-result";
    }
  }
  const folder = new DesktopIcon("Accounting", "Buchhaltung");
  const nativeHome = new DesktopIcon("Home", "Start");
  const before = JSON.stringify(folder.icon_data);
  vm.runInContext(script, context);
  const receiver = { marker: "native-this" };
  assert.equal(
    frappe.utils.get_desktop_icon.call(receiver, "Home", "solid"),
    "native-home"
  );
  assert.deepEqual(fallbackCalls[0], { args: ["Home", "solid"], receiver });
  assert.equal(
    frappe.utils.get_desktop_icon("Accounting", "solid"),
    "approved-accounting"
  );
  events["desktop_screen.reybill_module_icons"](
    {},
    { desktop: { icon_grid: { icons: [folder, nativeHome] } } }
  );
  assert.equal(
    folder.container.firstElementChild.getAttribute("src"),
    "approved-accounting"
  );
  assert.equal(nativeHome.container.childElementCount, 0);
  const method = DesktopIcon.prototype.render_folder_thumbnail;
  vm.runInContext(script, context);
  events["desktop_screen.reybill_module_icons"](
    {},
    { desktop: { icon_grid: { icons: [folder, nativeHome] } } }
  );
  assert.equal(DesktopIcon.prototype.render_folder_thumbnail, method);
  assert.equal(
    folder.render_folder_thumbnail("native-argument"),
    "native-thumbnail-result"
  );
  assert.equal(folder.nativeCalls, 1);
  assert.deepEqual(folder.nativeArgs, ["native-argument"]);
  assert.equal(folder.container.childElementCount, 1);
  assert.equal(
    folder.container.firstElementChild.getAttribute("src"),
    "approved-accounting"
  );
  assert.equal(JSON.stringify(folder.icon_data), before);
  assert.equal(folder.onClick, callback);
  const renamed = new DesktopIcon("custom-folder", "Accounting");
  renamed.render_folder_thumbnail();
  assert.equal(renamed.container.childElementCount, 2);
  const workspace = new Workspace();
  const slot = new Element();
  workspace.wrapper = { find: () => ({ get: () => slot }) };
  assert.equal(
    await workspace.show_page({ name: "Invoicing" }),
    "native-workspace-result"
  );
  assert.equal(
    slot.firstElementChild.getAttribute("src"),
    "approved-invoicing"
  );
  assert.equal(records.length, 2);
});
