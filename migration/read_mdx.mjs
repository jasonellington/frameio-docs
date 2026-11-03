// Static reader for Fern's compiled MDX bundles. The bundle text is parsed into an AST
// and read as data: only literals, arrays, objects and jsx(...) call shapes are interpreted.
// Nothing from the bundle is ever evaluated. Anything unrecognised is emitted as #unknown.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(process.env.ACORN_BASE + '/');
const acorn = require('acorn');

const [, , inDir, outDir] = process.argv;
const unknownCounts = {};
function note(k) { unknownCounts[k] = (unknownCounts[k] || 0) + 1; }

function readBundle(text) {
  const ast = acorn.parse(text, { ecmaVersion: 'latest', sourceType: 'script', allowReturnOutsideFunction: true });
  const src = (n) => text.slice(n.start, Math.min(n.end, n.start + 160));
  const top = new Map();   // name -> init node or FunctionDeclaration
  const funcs = [];
  (function collect(node) {
    if (!node || typeof node !== 'object') return;
    if (Array.isArray(node)) { node.forEach(collect); return; }
    if (node.type === 'FunctionDeclaration') { top.set(node.id.name, node); funcs.push(node); }
    if (node.type === 'VariableDeclarator' && node.id.type === 'Identifier' && node.init && !top.has(node.id.name)) top.set(node.id.name, node.init);
    for (const k of Object.keys(node)) { if (k !== 'start' && k !== 'end') { const v = node[k]; if (v && typeof v === 'object') collect(v); } }
  })(ast);

  const isJsxCallee = (c) => {
    if (c.type === 'SequenceExpression') c = c.expressions[c.expressions.length - 1];
    return c.type === 'MemberExpression' && !c.computed && ['jsx', 'jsxs', 'jsxDEV'].includes(c.property.name);
  };

  function resolveType(n, sc) {
    if (n.type === 'MemberExpression') {
      if (!n.computed && n.property.name === 'Fragment') return '#frag';
      if (!n.computed && n.object.type === 'Identifier' && sc.tags.has(n.object.name)) return n.property.name;
      const o = resolveType(n.object, sc); return (typeof o === 'string' ? o + '.' : '') + (n.property.name || '?');
    }
    if (n.type === 'Identifier') {
      if (sc.comps.has(n.name)) return '@' + sc.comps.get(n.name);
      if (top.get(n.name)?.type === 'FunctionDeclaration') return { local: n.name };
      return '#ident:' + n.name;
    }
    if (n.type === 'Literal') return String(n.value);
    note('type:' + n.type); return '#unknown';
  }

  function ev(n, sc) {
    switch (n.type) {
      case 'Literal': return n.value;
      case 'TemplateLiteral':
        if (n.expressions.length === 0) return n.quasis.map(q => q.value.cooked).join('');
        note('template-expr'); return { t: '#unknown', src: src(n) };
      case 'ArrayExpression': return n.elements.map(e => (e ? ev(e, sc) : null));
      case 'ObjectExpression': {
        const o = {};
        for (const p of n.properties) {
          if (p.type === 'SpreadElement') { const v = ev(p.argument, sc); if (v && typeof v === 'object' && !v.t) Object.assign(o, v); continue; }
          const k = p.key.name ?? p.key.value;
          o[k] = ev(p.value, sc);
        }
        return o;
      }
      case 'UnaryExpression':
        if (n.operator === '!' && n.argument.type === 'Literal') return !n.argument.value;
        if (n.operator === 'void') return undefined;
        if (n.operator === '-' && n.argument.type === 'Literal') return -n.argument.value;
        note('unary:' + n.operator); return { t: '#unknown', src: src(n) };
      case 'SequenceExpression': return ev(n.expressions[n.expressions.length - 1], sc);
      case 'Identifier': {
        if (n.name === 'undefined') return undefined;
        if (sc.params?.has(n.name)) return sc.params.get(n.name);
        const init = top.get(n.name);
        if (init && init.type !== 'FunctionDeclaration' && !/Function/.test(init.type)) return ev(init, sc);
        note('ident'); return { t: '#unknown', src: n.name };
      }
      case 'MemberExpression': {
        const o = ev(n.object, sc);
        if (o && typeof o === 'object' && !n.computed && n.property.name in o) return o[n.property.name];
        note('member'); return { t: '#unknown', src: src(n) };
      }
      case 'ArrowFunctionExpression': case 'FunctionExpression': return '[fn]';
      case 'CallExpression': {
        if (isJsxCallee(n.callee)) {
          const type = resolveType(n.arguments[0], sc);
          const props = n.arguments[1] ? ev(n.arguments[1], sc) : {};
          const { children, ...rest } = props && typeof props === 'object' ? props : {};
          if (type && typeof type === 'object' && type.local) return expandLocal(type.local, props, sc);
          return { t: type, p: rest, c: children };
        }
        note('call'); return { t: '#unknown', src: src(n) };
      }
      case 'ConditionalExpression': case 'LogicalExpression': case 'BinaryExpression':
        note(n.type); return { t: '#unknown', src: src(n) };
      default: note('node:' + n.type); return { t: '#unknown', src: src(n) };
    }
  }

  function scopeFor(fn, params) {
    const sc = { tags: new Set(), comps: new Map(), params };
    for (const st of fn.body.body || []) {
      if (st.type !== 'VariableDeclaration') continue;
      for (const d of st.declarations) {
        if (d.id.type === 'Identifier' && d.init?.type === 'ObjectExpression') sc.tags.add(d.id.name);
        if (d.id.type === 'ObjectPattern') for (const p of d.id.properties) {
          if (p.type === 'Property' && p.value.type === 'Identifier') sc.comps.set(p.value.name, p.key.name ?? p.key.value);
        }
      }
    }
    return sc;
  }
  function returnOf(fn) {
    const r = (fn.body.body || []).filter(s => s.type === 'ReturnStatement').pop();
    return r?.argument;
  }
  function expandLocal(name, props) {
    const fn = top.get(name);
    const arg = returnOf(fn);
    if (!arg) { note('local-noreturn'); return { t: '#unknown', src: name }; }
    const params = new Map();
    const p0 = fn.params[0];
    if (p0?.type === 'Identifier') params.set(p0.name, props);
    if (p0?.type === 'ObjectPattern') for (const p of p0.properties) if (p.value?.type === 'Identifier') params.set(p.value.name, props?.[p.key.name]);
    return ev(arg, scopeFor(fn, params));
  }

  // The content function is the one that destructures components from a tag map and returns jsx.
  const content = funcs.filter(f => /useMDXComponents|\.\.\.[a-zA-Z_$]+\(\),\.\.\.[a-zA-Z_$]+\.components/.test(text.slice(f.start, Math.min(f.end, f.start + 3000))) && returnOf(f) && !/wrapper/.test(text.slice(f.start, f.start + 120)));
  if (content.length !== 1) note('content-fn-count:' + content.length);
  const main = content[content.length - 1];
  return { tree: ev(returnOf(main), scopeFor(main, new Map())), locals: funcs.map(f => f.id.name) };
}

const census = {};
function walk(n, f) { if (Array.isArray(n)) n.forEach(x => walk(x, f)); else if (n && typeof n === 'object' && 't' in n) { f(n); walk(n.c, f); for (const v of Object.values(n.p || {})) walk(v, f); } }
let ok = 0, bad = [];
for (const f of fs.readdirSync(inDir)) {
  const text = fs.readFileSync(path.join(inDir, f), 'utf8');
  try {
    const r = readBundle(text);
    fs.writeFileSync(path.join(outDir, f.replace(/\.txt$/, '.json')), JSON.stringify(r.tree));
    walk(r.tree, n => {
      const k = String(n.t);
      census[k] ??= { n: 0, props: {} };
      census[k].n++;
      for (const p of Object.keys(n.p || {})) census[k].props[p] = (census[k].props[p] || 0) + 1;
    });
    ok++;
  } catch (e) { bad.push(f + ': ' + e.message); }
}
console.log('ok', ok, 'failed', bad.length, bad.slice(0, 5));
console.log('unknown', JSON.stringify(unknownCounts));
for (const [k, v] of Object.entries(census).sort((a, b) => b[1].n - a[1].n)) console.log(v.n, k, JSON.stringify(v.props));
