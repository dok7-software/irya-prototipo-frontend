/*
 * Mini runtime para las pantallas del prototipo (formato .dc.html).
 * Sin dependencias: evalúa la clase `Component` de cada pantalla, resuelve
 * <sc-if>, rellena los {{ huecos }} y conecta onClick / onChange.
 */
(function () {
  'use strict';

  var root, comp, tpl, vals, pending = false;

  function DCLogic() { this.props = {}; this.state = {}; }
  DCLogic.prototype.setState = function (o) {
    var patch = typeof o === 'function' ? o(this.state) : o;
    this.state = Object.assign({}, this.state, patch);
    schedule();
  };
  DCLogic.prototype.forceUpdate = function () { schedule(); };
  window.DCLogic = DCLogic;

  function schedule() {
    if (pending) return;
    pending = true;
    Promise.resolve().then(function () { pending = false; render(); });
  }

  function get(obj, path) {
    path = String(path).trim();
    if (path === 'true') return true;
    if (path === 'false') return false;
    if (/^-?\d+(\.\d+)?$/.test(path)) return Number(path);
    var cur = obj, parts = path.split('.');
    for (var i = 0; i < parts.length; i++) {
      if (cur == null) return undefined;
      cur = cur[parts[i]];
    }
    return cur;
  }

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  var IF_RE = /<sc-if\s+value="\{\{([^}]*)\}\}"[^>]*>((?:(?!<sc-if)[\s\S])*?)<\/sc-if>/;

  function build(t, v) {
    var m, guard = 0;
    while ((m = IF_RE.exec(t)) && guard++ < 5000) {
      t = t.slice(0, m.index) + (get(v, m[1]) ? m[2] : '') + t.slice(m.index + m[0].length);
    }
    // atributos cuyo valor completo es un hueco
    t = t.replace(/\s([a-zA-Z][a-zA-Z0-9:-]*)="\{\{([^}]*)\}\}"/g, function (all, attr, p) {
      var a = attr.toLowerCase(), x = get(v, p);
      if (/^on[a-z]+$/.test(a)) return ' data-dc-' + a + '="' + esc(p.trim()) + '"';
      if (a === 'checked' || a === 'disabled' || a === 'selected') return (x ? ' ' + a : '') + ' data-dc-' + a + '="' + (x ? 1 : 0) + '"';
      if (x === undefined || x === null || x === false) return a === 'value' ? ' value="" data-dc-value=""' : '';
      if (a === 'value') return ' value="' + esc(x) + '" data-dc-value="' + esc(x) + '"';
      return ' ' + attr + '="' + esc(x) + '"';
    });
    // huecos dentro de texto o de atributos interpolados
    t = t.replace(/\{\{([^}]*)\}\}/g, function (all, p) {
      var x = get(v, p);
      return x === undefined || x === null ? '' : esc(x);
    });
    t = t.replace(/\shint-[a-z-]+="[^"]*"/g, '');
    // enlaces entre pantallas
    t = t.replace(/href="([^"#:]+)\.dc\.html"/g, 'href="$1.html"');
    return t;
  }

  function fields() { return root.querySelectorAll('input, textarea, select'); }

  function render() {
    vals = comp.renderVals();
    var active = document.activeElement, idx = -1, selS = null, selE = null;
    if (active && root.contains(active)) {
      idx = Array.prototype.indexOf.call(fields(), active);
      try { selS = active.selectionStart; selE = active.selectionEnd; } catch (e) { /* no-op */ }
    }
    root.innerHTML = build(tpl, vals);
    bind();
    if (idx >= 0) {
      var el = fields()[idx];
      if (el) {
        el.focus();
        try { if (selS !== null) el.setSelectionRange(selS, selE); } catch (e) { /* no-op */ }
      }
    }
  }

  function call(path, e) {
    var fn = get(vals, path);
    if (typeof fn === 'function') fn(e);
  }

  function bind() {
    root.querySelectorAll('[data-dc-checked]').forEach(function (el) { el.checked = el.getAttribute('data-dc-checked') === '1'; });
    root.querySelectorAll('[data-dc-value]').forEach(function (el) { el.value = el.getAttribute('data-dc-value'); });
    root.querySelectorAll('[data-dc-onclick]').forEach(function (el) {
      var p = el.getAttribute('data-dc-onclick');
      el.addEventListener('click', function (e) { call(p, e); });
    });
    root.querySelectorAll('[data-dc-onchange]').forEach(function (el) {
      var p = el.getAttribute('data-dc-onchange');
      var type = (el.getAttribute('type') || '').toLowerCase();
      var evt = (el.tagName === 'SELECT' || type === 'checkbox' || type === 'radio' || type === 'file') ? 'change' : 'input';
      el.addEventListener(evt, function (e) { call(p, e); });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    root = document.getElementById('dc-root');
    tpl = JSON.parse(document.getElementById('dc-template').textContent);
    var code = document.getElementById('dc-logic').textContent;
    var Component = new Function('DCLogic', code + '\nreturn Component;')(DCLogic);
    comp = new Component();
    render();
    if (typeof comp.componentDidMount === 'function') comp.componentDidMount();
  });
})();
