#!/usr/bin/env python3
"""Fern (developer.frame.io) -> Mintlify transformer. Re-run after any rule fix; never hand-patch output.

Sources, in priority order:
  mirror/tree/*.json  original MDX component trees, read statically from compiled bundles
  mirror/md/*.md      Fern's markdown export, for pages that shipped no bundle
  mirror/nav/*.json   sidebar data; openapi/*.json specs; mirror/snippets.json code samples
"""
import json, os, re, sys, html, shutil, collections, subprocess, posixpath, urllib.parse
from bs4 import BeautifulSoup

ROOT = os.getcwd()
HOST = 'https://developer.frame.io'
rows = json.load(open('mirror/inventory.json'))
SLUGS = {r['slug'] for r in rows}
report = collections.defaultdict(list)

# ---------- URL model ----------
def load_nav(name): return json.load(open(f'mirror/nav/{name}.json'))
NAVS = {
 ('Platform','V4'): dict(home='platform_welcome', api='platform_api-reference_files_show', docs='platform_docs_overview', log='platform_changelog'),
 ('Platform','V4 Experimental'): dict(home='platform_v4-experimental_welcome', api='platform_v4-experimental_api-reference_files_bulk-copy', docs='platform_v4-experimental_docs_overview', log='platform_v4-experimental_changelog'),
 ('Platform','Legacy'): dict(docs='platform_v2_index', api='platform_v2_api-reference_webhooks_delete-webhook'),
 ('Camera to Cloud',None): dict(home='camera-to-cloud_welcome', docs='camera-to-cloud_getting-started-with-cloud-device-integrations', api='camera-to-cloud_api-reference_device-identify'),
}
# Section and tab slugs that Fern resolves to their first page.
POINTS = {
 'platform': 'platform/welcome', 'platform/v4': 'platform/welcome', 'platform/v4/welcome': 'platform/welcome',
 'platform/docs': 'platform/docs/overview', 'platform/v4/docs': 'platform/docs/overview',
 'platform/v2': 'platform/v2/index', 'platform/v2/docs': 'platform/v2/index', 'platform/v4-experimental': 'platform/v4-experimental/welcome',
 'camera-to-cloud': 'camera-to-cloud/welcome',
 'camera-to-cloud/docs': 'camera-to-cloud/getting-started-with-cloud-device-integrations',
}
def first_leaf(n):
    if n.get('type') in ('page','endpoint','changelog'): return n.get('slug')
    for c in n.get('children') or []:
        s = first_leaf(c)
        if s: return s
def collect_points(n):
    if n.get('type') in ('section','apiPackage','apiReference') and n.get('slug'):
        s = n.get('pointsTo') or first_leaf(n)
        if s and n['slug'] not in SLUGS: POINTS.setdefault(n['slug'], s)
    for c in n.get('children') or []: collect_points(c)
for ctx, m in NAVS.items():
    for k in m.values():
        for n in load_nav(k)['sidebarChildren']: collect_points(n)
POINTS['platform/api-reference/account-permissions/index'] = POINTS['platform/api-reference/account-permissions']

# The only source link that 404s on the live site (Experimental welcome, SDKs card).
SOURCE_BUGS = {'docs/sdk-reference': 'platform/docs/sdk-reference/python-sdk-reference'}
def public_path(slug):
    """index pages are served at their directory by Mintlify."""
    return '/' + (slug[:-6] if slug == 'platform/v2/index' else slug)

def norm_internal(p):
    p = p.strip('/')
    if p.startswith('platform/v4/'):
        q = 'platform/' + p[len('platform/v4/'):]
        if q in SLUGS or q in POINTS: p = q
    if p == 'platform/v4': p = 'platform'
    return p

TITLES = collections.defaultdict(lambda: collections.defaultdict(set))   # version -> title -> slugs
BASE = collections.defaultdict(set)
for _r in rows:
    if _r['kind'] == 'endpoint': TITLES[(_r['product'], _r['version'])][_r['title'].lower()].add(_r['slug'])
    if _r['kind'] in ('page', 'endpoint'): BASE[_r['slug'].rsplit('/', 1)[-1]].add(_r['slug'])
ROW = {r['slug']: r for r in rows}
def scope_prefix(slug):
    if slug.startswith('platform/v2'): return 'platform/v2/'
    if slug.startswith('platform/v4-experimental'): return 'platform/v4-experimental/'
    if slug.startswith('camera-to-cloud'): return 'camera-to-cloud/'
    return 'platform/'
def in_scope(s, pre):
    if pre == 'platform/': return s.startswith('platform/') and not s.startswith(('platform/v2/', 'platform/v4-experimental/'))
    return s.startswith(pre)

def repair(p, slug, label):
    """Find the one page a dead source link clearly meant. Returns a slug or None."""
    q = norm_internal(p.replace('_', '-').replace('typescript-sdk-reference', 'type-script-sdk-reference'))
    if q in SLUGS: return q
    if '/api-reference/' in p and label:
        s = ROW.get(slug)
        ctx = (s['product'], s['version']) if s else None
        hit = TITLES[ctx].get(re.sub(r'\s+', ' ', label).strip().lower(), set()) if ctx else set()
        if len(hit) == 1: return next(iter(hit))
    base = q.rsplit('/', 1)[-1]
    cands = BASE.get(base, set())
    pre = scope_prefix(slug)
    local = {c for c in cands if in_scope(c, pre) and '/api-reference/' not in c}
    if len(local) == 1: return next(iter(local))
    rest = {c for c in cands if '/api-reference/' not in c}
    if not local and len(rest) == 1: return next(iter(rest))
    return None

# ReadMe-era link schemes that survive in Legacy pages.
README_REF = {}
for _r in rows:
    if _r['kind'] == 'endpoint' and _r['version'] == 'Legacy':
        _m = re.search(r'(?m)^(GET|POST|PUT|PATCH|DELETE) https://api\.frame\.io/v2/(\S+)', open('mirror/md/' + _r['slug'].replace('/', '__') + '.md', errors='ignore').read())
        if not _m: continue
        _k = _m.group(1).lower() + '_' + re.sub(r'\{[^}]*\}', '*', _m.group(2)).replace('/', '-').lower()
        README_REF[_k] = _r['slug']
README_DOC = {'webhooks': 'platform/v2/webhooks-overview', 'managing-version-stacks': 'platform/v2/manage-version-stacks',
              'get-a-developer-token': 'platform/v2/authentication', 'authentication': 'platform/v2/authentication'}
def readme_link(href, slug, label):
    kind, name = href.split(':', 1)
    key = re.sub(r'(?<=-)[a-z]*id(?=-|$)', '*', name)
    target = README_REF.get(key) if kind == 'ref' else README_DOC.get(name)
    if kind == 'ref' and not target and 'platform/v2/api-reference/' + name in POINTS:
        target = POINTS['platform/v2/api-reference/' + name]
    if target:
        report['repaired_links'].append(f'{slug}: {href} to /{target}')
        return public_path(target)
    report['placeholder_links'].append(f'{slug}: [{label}]({href})')
    return None

# Fragments that are stale on the live site but have one clear heading today.
ANCHORS = {'h2-section-uploading-reliably': 'uploading-reliably', 'h3-section-offset---handling-paused-devices': 'offset---handling-paused-devices',
           'fetching-connection-information': 'retrieving-connection-information', 'handling-the-paused-status': 'managing-the-paused-status',
           'device-identification-device_id': 'device-identification'}
def rewrite(href, slug, label=None):
    if not href: return href
    if '#' in href:
        base, frag = href.split('#', 1)
        if frag in ANCHORS:
            report['repaired_anchors'].append(f'{slug}: #{frag} to #{ANCHORS[frag]}')
            href = base + '#' + ANCHORS[frag]
        elif frag == 'h3-section-enabling-qr-code-pairing':
            report['dead_anchors_kept'].append(f'{slug}: {href}')
    if re.match(r'^(ref|doc):', href): return readme_link(href, slug, label)
    if href.strip().lower() == 'link':
        report['placeholder_links'].append(f'{slug}: [{label}](link)')
        return None
    h = html.unescape(href)
    absolute = h.startswith(HOST)
    if absolute: h = h[len(HOST):] or '/'
    if re.match(r'^[a-z][a-z0-9+.-]*:', h, re.I) or h.startswith('#') or h.startswith('//'): return h
    m = re.match(r'^([^?#]*)([?#].*)?$', h); path, tail = m.group(1), m.group(2) or ''
    path = re.sub(r'\.(md|mdx|html)$', '', path)
    if not path.startswith('/'):
        path = posixpath.normpath(posixpath.join('/' + posixpath.dirname(slug), path))
    if path.startswith('/_fern-files') or path.startswith('/images/'): return path + tail
    if path.rstrip('/') == '/app/custom-actions/builder':
        return 'https://next.frame.io/settings/actions'
    p = norm_internal(path)
    if p in SOURCE_BUGS:
        report['repaired_links'].append(f'{slug}: /{p} to /{SOURCE_BUGS[p]}')
        p = SOURCE_BUGS[p]
    p = POINTS.get(p, p)
    if p not in SLUGS and p != '' and not absolute:
        fixed = repair(p, slug, label)
        if fixed:
            report['repaired_links'].append(f'{slug}: {href} to /{fixed}')
            p = fixed
    if p in SLUGS or p == '':
        entry = re.match(r'^(platform(?:/v4-experimental)?/changelog)/\d{4}/\d+/\d+$', p)
        if entry: return '/' + entry.group(1) + tail
        return public_path(p) + tail
    report['dead_links_kept'].append(f'{slug}: {HOST}{path}{tail}')
    return HOST + path + tail

# ---------- assets ----------
ASSETS = {}      # remote url -> local path
def asset(src, slug, kind='images'):
    u = html.unescape(src)
    if u.startswith('//'): u = 'https:' + u
    if u.startswith('/'): u = HOST + u
    if u in ASSETS: return ASSETS[u]
    base = urllib.parse.unquote(posixpath.basename(urllib.parse.urlparse(u).path)) or 'asset'
    base = re.sub(r'[^A-Za-z0-9._-]+', '-', base)
    if '.' not in base: base += '.svg' if 'pstmn' in u else ''
    local = f'/{kind}/{slug}/{base}'
    ASSETS[u] = local
    return local

# ---------- text helpers ----------
def slugify(s):
    s = s.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s, flags=re.U)
    return re.sub(r'\s', '-', s)

def text(n):
    if n is None or isinstance(n, bool): return ''
    if isinstance(n, (str, int, float)): return str(n)
    if isinstance(n, list): return ''.join(text(x) for x in n)
    if isinstance(n, dict):
        if str(n.get('t')) in SKIP: return ''
        return text(n.get('c'))
    return ''

def esc(s, table=False):
    if '](doc:' in s:
        report['placeholder_links'].append('literal broken link text: ' + s.strip()[:90])
        s = re.sub(r'\]\(doc:[a-z0-9-]+\)?', '', s)
    s = s.replace('\\', '\\\\')
    s = re.sub(r'&(?=#?\w+;)', '&amp;', s)
    s = s.replace('<', '&lt;').replace('{', '\\{').replace('}', '\\}')
    s = s.replace('`', '\\`').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]')
    s = re.sub(r'(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])', r'\\_', s)
    s = s.replace('~~', '\\~\\~')
    if table: s = s.replace('|', '\\|').replace('\n', ' ')
    return s

def attr(v):
    v = re.sub(r'\s+', ' ', str(v)).strip()
    return '"' + v.replace('&', '&amp;').replace('"', '&quot;') + '"'

def code_span(s, table=False):
    s = s.replace('\n', ' ')
    if table: s = s.replace('|', '\\|')
    run = max([len(m) for m in re.findall(r'`+', s)] or [0])
    tick = '`' * (run + 1)
    pad = ' ' if s.startswith('`') or s.endswith('`') else ''
    return f'{tick}{pad}{s}{pad}{tick}'

SKIP = {'svg','path','rect','g','defs','stop','radialGradient','linearGradient','style','script'}
DROP_DIV = re.compile(r'hero-bg-image|unicorn')
INLINE = {'code','strong','b','em','i','del','a','@A','br','span','img','@Tooltip','@Badge','@Button'}
BLOCKISH = {'p','h1','h2','h3','h4','h5','h6','@H1','@H2','@H3','@H4','ul','ol','@Ul','@Ol','table','hr','blockquote','pre','div','video',
            '@CodeBlock','@CodeGroup','@Card','@CardGroup','@Accordion','@AccordionGroup','@Step','@StepGroup','@Tab','@TabGroup',
            '@Info','@Note','@Tip','@Warning','@Error','@Callout','@Launch','@Check','@Success','@Frame','@Image'}
TRANSPARENT = {'#frag','@ErrorBoundary'}
CALLOUTS = {'@Info':'Info','@Note':'Note','@Tip':'Tip','@Warning':'Warning','@Error':'Danger','@Launch':'Info','@Check':'Check','@Success':'Check'}
INTENT = {'info':'Info','note':'Note','tip':'Tip','warning':'Warning','error':'Danger','danger':'Danger','success':'Check','check':'Check','launch':'Info'}
BADGE = {'success':'green','note':'blue','info':'blue','tip':'green','warning':'yellow','error':'red','launch':'purple','check':'green'}
LANG = {'curl':'bash','cURL':'bash','math':'text','serialized':'text','python-sdk':'python','ts':'typescript','js':'javascript'}

def flat(children):
    """Children list with transparent wrappers removed."""
    out = []
    items = children if isinstance(children, list) else [children]
    for c in items:
        if c is None or isinstance(c, bool): continue
        if isinstance(c, dict) and c.get('t') in TRANSPARENT: out.extend(flat(c.get('c')))
        elif isinstance(c, list): out.extend(flat(c))
        else: out.append(c)
    return out

class Ctx:
    def __init__(s, slug, title=None): s.slug, s.title = slug, title

def inline(children, ctx, table=False):
    out = []
    for c in flat(children):
        if isinstance(c, (str, int, float)):
            out.append(esc(str(c), table)); continue
        if not isinstance(c, dict): continue
        t = c['t']; p = c.get('p') or {}
        if t in SKIP: continue
        if t == 'code': out.append(code_span(text(c), table))
        elif t in ('strong','b'):
            s = inline(c.get('c'), ctx, table)
            out.append(f'**{s.strip()}**' if s.strip() else '')
        elif t in ('em','i'):
            s = inline(c.get('c'), ctx, table)
            out.append(f'*{s.strip()}*' if s.strip() else '')
        elif t == 'del': out.append(f'~~{inline(c.get("c"), ctx, table)}~~')
        elif t in ('a','@A','@Button'):
            label = inline(c.get('c'), ctx, table).strip()
            href = rewrite(p.get('href'), ctx.slug, text(c))
            out.append(f'[{label}]({href})' if href else label)
        elif t == 'br': out.append('<br />')
        elif t == 'span': out.append(inline(c.get('c'), ctx, table))
        elif t == 'img': out.append(image(p, ctx))
        elif t == '@Tooltip': out.append(f'<Tooltip tip={attr(p.get("tip",""))}>{inline(c.get("c"), ctx, table)}</Tooltip>')
        elif t == '@Badge': out.append(f'<Badge color="{BADGE.get(p.get("intent"),"gray")}">{esc(text(c))}</Badge>')
        elif t == 'p': out.append(inline(c.get('c'), ctx, table))
        else:
            report['inline_unmapped'].append(f'{ctx.slug}: {t}')
            out.append(inline(c.get('c'), ctx, table))
    return ''.join(out)

def image(p, ctx):
    src = asset(p.get('src',''), ctx.slug)
    alt = (p.get('alt') or '').replace('[','').replace(']','').replace('\n',' ')
    title = p.get('title')
    if re.search(r'[()\s]', src): return f'<img src={attr(src)} alt={attr(alt)} />'
    if title: return f'![{alt}]({src} "{title.replace(chr(34), "")}")'
    return f'![{alt}]({src})'

def indent(s, n):
    pad = ' ' * n
    return '\n'.join(pad + l if l.strip() else '' for l in s.split('\n'))

def is_inline(c):
    if isinstance(c, (str, int, float)): return True
    return isinstance(c, dict) and c.get('t') in INLINE

def blocks(children, ctx):
    """Render a container's children; runs of inline nodes become paragraphs."""
    out, run = [], []
    def flush():
        if run:
            s = inline(run, ctx).strip()
            s = re.sub(r'[ \t]*\n[ \t]*', '\n', s)
            if s: out.append(para(s))
            run.clear()
    for c in flat(children):
        if is_inline(c): run.append(c); continue
        flush()
        if isinstance(c, dict):
            b = block(c, ctx)
            if b: out.append(b)
    flush()
    return '\n\n'.join(out)

def para(s):
    lines = s.split('\n')
    fixed = []
    for l in lines:
        if re.match(r'^(#{1,6}\s|[-+]\s|\d+[.)]\s|>\s?)', l): l = '\\' + l
        fixed.append(l)
    s = '\n'.join(fixed)
    if s.count('$') >= 2: s = s.replace('$', '\\$')
    return s

def heading(c, ctx, level):
    p = c.get('p') or {}
    s = inline(c.get('c'), ctx).strip().replace('\n', ' ')
    if not s: return ''
    hid = p.get('id')
    if hid and hid != slugify(text(c)):
        report['pinned_anchors'].append(f'{ctx.slug}#{hid}')
        s += f' {{#{hid}}}'
    return '#' * level + ' ' + s

def fence(p):
    code = p.get('code')
    code = code if isinstance(code, str) else text(code)
    code = code.rstrip('\n')
    lang = p.get('language') or ''
    lang = LANG.get(lang, lang)
    run = max([len(m) for m in re.findall(r'^\s*(`{3,})', code, re.M)] or [2])
    tick = '`' * max(3, run + 1)
    title = p.get('title')
    meta = ''
    if title:
        lang = lang or 'text'
        t = re.sub(r'\s+', ' ', str(title)).strip()
        meta = f' title={json.dumps(t, ensure_ascii=False)}' if '"' not in t else f' {t}'
    return f'{tick}{lang}{meta}\n{code}\n{tick}'

def table(c, ctx):
    head, body = [], []
    aligns = []
    for sec in flat(c.get('c')):
        if not isinstance(sec, dict): continue
        for tr in flat(sec.get('c')):
            if not isinstance(tr, dict) or tr.get('t') != 'tr': continue
            cells = [x for x in flat(tr.get('c')) if isinstance(x, dict) and x.get('t') in ('td','th')]
            vals = [re.sub(r'\s*\n\s*', ' ', inline(x.get('c'), ctx, table=True)).strip() for x in cells]
            if sec.get('t') == 'thead':
                head = vals
                for x in cells:
                    a = ((x.get('p') or {}).get('style') or {})
                    aligns.append(a.get('textAlign') if isinstance(a, dict) else None)
            else: body.append(vals)
    p = c.get('p') or {}
    if p.get('searchable'): report['table_search'].append(ctx.slug)
    if p.get('sticky'): report['table_sticky'].append(ctx.slug)
    if body and not any(h.strip() for h in head):
        report['empty_table_headers'].append(ctx.slug)
        head, body = body[0], body[1:]
    w = len(head)
    sep = {'center':':---:','right':'---:','left':':---'}
    lines = ['| ' + ' | '.join(head) + ' |', '| ' + ' | '.join(sep.get(a,'---') for a in (aligns + [None]*w)[:w]) + ' |']
    for r in body: lines.append('| ' + ' | '.join((r + ['']*w)[:w]) + ' |')
    return '\n'.join(lines)

def lst(c, ctx, ordered):
    p = c.get('p') or {}
    start = int(p.get('start') or 1)
    out = []
    i = start
    for li in flat(c.get('c')):
        if not isinstance(li, dict): continue
        marker = f'{i}. ' if ordered else '- '
        body = blocks(li.get('c'), ctx)
        out.append(marker + indent(body, len(marker)).lstrip())
        i += 1
    tight = all('\n\n' not in o for o in out)
    return ('\n' if tight else '\n\n').join(out)

def wrap(tag, attrs, body):
    a = ''.join(f' {k}={v}' for k, v in attrs if v is not None)
    if not body.strip(): return f'<{tag}{a} />'
    return f'<{tag}{a}>\n\n{body}\n\n</{tag}>'

def callout(tag, p, children, ctx):
    body = blocks(children, ctx)
    title = p.get('title')
    if title and str(title).strip().lower() != tag.lower():
        t = esc(str(title))
        body = f'**{t}**\n\n{body}' if body else f'**{t}**'
    return wrap(tag, [], body)

def icon_attrs(icon, ctx):
    if not icon: return []
    s = str(icon)
    m = re.search(r'data-icon=\\?"([a-z0-9-]+)\\?"', s)
    if m:
        pre = re.search(r'data-prefix=\\?"([a-z]+)\\?"', s)
        kinds = {'fas':'solid','far':'regular','fab':'brands','fal':'light','fat':'thin','fad':'duotone'}
        return [('icon', attr(m.group(1))), ('iconType', attr(kinds.get(pre.group(1) if pre else '', 'solid')))]
    m = re.match(r'^fa-(solid|regular|brands|light|thin|duotone) fa-([a-z0-9-]+)$', s)
    if m: return [('icon', attr(m.group(2))), ('iconType', attr(m.group(1)))]
    if s == 'trending-up':
        report['icon_mapped'].append(f'{ctx.slug}: trending-up to arrow-trend-up')
        return [('icon', attr('arrow-trend-up')), ('iconType', attr('solid'))]
    report['icon_plain'].append(f'{ctx.slug}: {s[:40]}')
    return [('icon', attr(s))]

def block(c, ctx):
    t = c['t']; p = c.get('p') or {}; ch = c.get('c')
    if t in SKIP: return ''
    if t == 'p':
        kids = flat(ch)
        if any(isinstance(k, dict) and k.get('t') in BLOCKISH for k in kids): return blocks(ch, ctx)
        s = inline(ch, ctx).strip()
        return para(re.sub(r'[ \t]*\n[ \t]*', '\n', s))
    m = re.match(r'^@?[hH]([1-6])$', t)
    if m:
        if m.group(1) == '1' and ctx.title and text(c).strip() == ctx.title: return ''
        return heading(c, ctx, int(m.group(1)))
    if t in ('ul','@Ul'): return lst(c, ctx, False)
    if t in ('ol','@Ol'): return lst(c, ctx, True)
    if t == 'hr': return '---'
    if t == 'table': return table(c, ctx)
    if t == 'blockquote': return '\n'.join(('> ' + l).rstrip() for l in blocks(ch, ctx).split('\n'))
    if t == '@CodeBlock': return fence(p)
    if t == '@CodeGroup':
        fences = []
        for k in flat(ch):
            if isinstance(k, dict) and k.get('t') == '@CodeBlock': fences.append(fence(k.get('p') or {}))
            elif isinstance(k, dict): report['codegroup_other'].append(f'{ctx.slug}: {k.get("t")}')
        return '<CodeGroup>\n\n' + '\n\n'.join(fences) + '\n\n</CodeGroup>'
    if t in CALLOUTS:
        if t == '@Launch': report['launch_callouts'].append(ctx.slug)
        return callout(CALLOUTS[t], p, ch, ctx)
    if t == '@Callout': return callout(INTENT.get(p.get('intent'), 'Note'), p, ch, ctx)
    if t == '@CardGroup':
        cols = p.get('cols') or 2
        return f'<CardGroup cols={{{cols}}}>\n\n' + blocks(ch, ctx) + '\n\n</CardGroup>'
    if t == '@Card':
        ttl = p.get('title')
        ttl = ttl if isinstance(ttl, str) else text(ttl)
        a = [('title', attr(ttl.strip()))] + icon_attrs(p.get('icon'), ctx)
        if p.get('href'): a.append(('href', attr(rewrite(p['href'], ctx.slug))))
        if p.get('iconPosition') == 'left': a.append(('horizontal', '{true}'))
        return wrap('Card', a, blocks(ch, ctx))
    if t == '@AccordionGroup': return '<AccordionGroup>\n\n' + blocks(ch, ctx) + '\n\n</AccordionGroup>'
    if t == '@Accordion':
        ttl = p.get('title')
        ttl = ttl if isinstance(ttl, str) else text(ttl)
        a = [('title', attr(ttl))]
        if p.get('id') and p['id'] != slugify(ttl): a.append(('id', attr(p['id'])))
        if p.get('defaultOpen'): a.append(('defaultOpen', '{true}'))
        return wrap('Accordion', a, blocks(ch, ctx))
    if t == '@StepGroup': return '<Steps>\n\n' + blocks(ch, ctx) + '\n\n</Steps>'
    if t == '@Step':
        ttl = p.get('title')
        ttl = ttl if isinstance(ttl, str) else text(ttl)
        return wrap('Step', [('title', attr(ttl))], blocks(ch, ctx))
    if t == '@TabGroup': return '<Tabs>\n\n' + blocks(ch, ctx) + '\n\n</Tabs>'
    if t == '@Tab':
        ttl = p.get('title')
        ttl = ttl if isinstance(ttl, str) else text(ttl)
        return wrap('Tab', [('title', attr(ttl))], blocks(ch, ctx))
    if t == '@Frame':
        cap = p.get('caption')
        return wrap('Frame', [('caption', attr(cap))] if cap else [], blocks(ch, ctx))
    if t == '@Image':
        img = image(p, ctx)
        cap = p.get('caption')
        return wrap('Frame', [('caption', attr(cap))], img) if cap else img
    if t == 'video':
        src = asset(p.get('src',''), ctx.slug, 'videos')
        report['video_poster_dropped'].append(ctx.slug) if p.get('poster') else None
        extra = ''.join(f' {k}={{true}}' for k in ('autoPlay','loop','muted','playsInline','controls') if p.get(k) not in (None, False))
        return f'<video src={attr(src)}{extra} />'
    if t == 'div':
        cn = str(p.get('className') or '')
        if DROP_DIV.search(cn):
            report['hero_dropped'].append(f'{ctx.slug}: {cn}')
            return ''
        return blocks(ch, ctx)
    report['block_unmapped'].append(f'{ctx.slug}: {t}')
    return blocks(ch, ctx)

# ---------- page metadata ----------
PRE_END = re.compile(r'^> For AI client integration.*$', re.M)
def strip_preamble(md):
    m = PRE_END.search(md)
    return md[m.end():].lstrip('\n') if m else md

def md_head(md):
    body = strip_preamble(md)
    m = re.match(r'^# (.+)\n+', body)
    title = None
    if m: title, body = m.group(1).strip(), body[m.end():]
    sub = None
    m = re.match(r'^> (.+)\n+', body)
    if m: sub, body = m.group(1).strip(), body[m.end():]
    return title, sub, body

def page_header(slug):
    """Title and subtitle as actually rendered, from the page header island."""
    f = 'mirror/html/' + slug.replace('/', '__') + '.html'
    s = BeautifulSoup(open(f, errors='ignore').read(), 'lxml')
    for e in s.find_all('astro-island'):
        if 'PageHeaderIsland' in (e.get('component-url') or ''):
            d = json.loads(e['props'])
            g = lambda k: (d.get(k) or [0, None])[1] if isinstance(d.get(k), list) and len(d.get(k)) > 1 else None
            return g('title'), g('subtitle')
    return None, None

def fm(d):
    lines = ['---']
    for k, v in d.items():
        if v is None: continue
        if isinstance(v, bool): lines.append(f'{k}: {str(v).lower()}'); continue
        v = str(v).replace('\n', ' ').strip()
        q = "'" if '"' in v and "'" not in v else '"'
        v = v.replace('\\', '\\\\').replace('"', '\\"') if q == '"' else v
        lines.append(f'{k}: {q}{v}{q}')
    lines.append('---')
    return '\n'.join(lines)

# ---------- markdown path (pages with no bundle, and changelog entries) ----------
def safe_md(body, slug):
    out, infence, tick = [], False, ''
    for line in body.split('\n'):
        m = re.match(r'^\s*(`{3,})', line)
        if m:
            if not infence: infence, tick = True, m.group(1)
            elif line.strip() == tick or line.strip().startswith(tick) and not line.strip().strip('`'): infence = False
            out.append(line); continue
        if infence: out.append(line); continue
        parts = re.split(r'(`+[^`]*`+)', line)
        for i in range(0, len(parts), 2):
            seg = parts[i]
            seg = re.sub(r'(?<!\\)\{', r'\\{', seg)
            seg = re.sub(r'(?<!\\)\}', r'\\}', seg)
            seg = re.sub(r'<(?=[^A-Za-z/!]|$)', '&lt;', seg)
            seg = re.sub(r'<([A-Za-z][\w-]*)>', r'`<\1>`', seg)
            def relink(m):
                href = rewrite(m.group(2), slug, re.sub(r'[*_`]', '', m.group(1)))
                return f'[{m.group(1)}]({href})' if href else m.group(1)
            seg = re.sub(r'(?<!!)\[([^\]]*)\]\(([^)\s]+)\)', relink, seg)
            parts[i] = seg
        out.append(''.join(parts))
    return '\n'.join(out)

# ---------- pages ----------
written = {}
def write_page(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w').write(content.rstrip() + '\n')
    written[path] = True

manifest = []
def trail(r): return ' > '.join(filter(None, [r['product'], r['version'], r['tab']] + r['trail']))

def emit_page(r):
    slug = r['slug']; key = slug.replace('/', '__')
    md = open(f'mirror/md/{key}.md', errors='ignore').read()
    mtitle, msub, mbody = md_head(md)
    htitle, hsub = page_header(slug)
    is_welcome = slug.endswith('/welcome') or slug == 'platform/welcome'
    tree_file = f'mirror/tree/{key}.json'
    title = htitle if isinstance(htitle, str) and htitle else mtitle
    sub = hsub if isinstance(hsub, str) and hsub else None
    if tree_file and os.path.exists(tree_file):
        tree = json.load(open(tree_file))
        if is_welcome:
            h1 = []
            def find(n):
                if isinstance(n, list): [find(x) for x in n]
                elif isinstance(n, dict) and 't' in n:
                    if re.match(r'^@?[hH]1$', str(n['t'])): h1.append(text(n).strip())
                    find(n.get('c'))
            find(tree)
            title = h1[0] if h1 else title
            sub = None
        ctx = Ctx(slug, title)
        body = blocks(tree, ctx)
    else:
        body = safe_md(mbody, slug)
    body = re.sub(r'^(---\s*\n+)+', '', body.lstrip())
    body = re.sub(r'(?m)^---\n\n(?=---$)', '', body)
    label = r['title']
    meta = {'title': title}
    if label and label != title: meta['sidebarTitle'] = label
    if sub: meta['description'] = re.sub(r'[*_`]', '', sub)
    write_page(slug + '.mdx', fm(meta) + '\n\n' + body)
    return slug + '.mdx', title

def emit_changelog(root, entries):
    """One page of Update blocks, newest first, in nav order."""
    parts = []
    for e in entries:
        key = e['slug'].replace('/', '__')
        md = open(f'mirror/md/{key}.md', errors='ignore').read()
        _, _, body = md_head(md)
        body = safe_md(body, e['slug']).strip()
        parts.append(f'<Update label={attr(e["title"])}>\n\n{body}\n\n</Update>')
    write_page(root + '.mdx', fm({'title': 'Changelog', 'rss': True}) + '\n\n' + '\n\n'.join(parts))

by_kind = collections.defaultdict(list)
for r in rows: by_kind[r['kind']].append(r)

for r in by_kind['page']:
    f, title = emit_page(r)
    manifest.append(dict(source_url=f'{HOST}/{r["slug"]}', source_title=title, source_sidebar_label=r['title'], nav_section=trail(r), converted_file=f, status='done', notes=''))

changelogs = {}
for r in by_kind['changelog']:
    entries = [e for e in by_kind['changelogEntry'] if e['slug'].startswith(r['slug'] + '/')]
    changelogs[r['slug']] = entries
    emit_changelog(r['slug'], entries)
    manifest.append(dict(source_url=f'{HOST}/{r["slug"]}', source_title='Changelog', source_sidebar_label='Changelog', nav_section=trail(r), converted_file=r['slug'] + '.mdx', status='done', notes='Listing page; consolidated with its entries.'))
    for e in entries:
        manifest.append(dict(source_url=f'{HOST}/{e["slug"]}', source_title=e['title'], source_sidebar_label=e['title'], nav_section=trail(e), converted_file=r['slug'] + '.mdx', status='done', notes='Entry merged into the consolidated changelog page.'))

# ---------- API: overlays ----------
SPECS = {('Platform','V4'):'v4', ('Platform','V4 Experimental'):'v4-experimental', ('Platform','Legacy'):'v2', ('Camera to Cloud',None):'camera-to-cloud'}
SRC = {'v4':'api-reference','v4-experimental':'api-reference-2','v2':'api-reference-3','camera-to-cloud':'api-reference-4'}
os.makedirs('openapi', exist_ok=True)
for name, src in SRC.items():
    if os.path.exists(f'mirror/openapi-src/{src}.json'): shutil.copy(f'mirror/openapi-src/{src}.json', f'openapi/{name}.json')
snippets = json.load(open('mirror/snippets.json'))
LABEL = {'curl':'cURL','python':'Python','javascript':'JavaScript','typescript':'TypeScript','go':'Go','ruby':'Ruby','java':'Java','php':'PHP','csharp':'C#','swift':'Swift'}
ORDER = ['curl','python','typescript','javascript','go','ruby','java','php','csharp','swift']
op_of = {}
actions = collections.defaultdict(list)
for r in by_kind['endpoint']:
    name = SPECS[(r['product'], r['version'])]
    md = open('mirror/md/' + r['slug'].replace('/', '__') + '.md', errors='ignore').read()
    m = re.search(r'(?m)^(GET|POST|PUT|PATCH|DELETE) https://api\.frame\.io(\S+)', md)
    meth, path = m.group(1), m.group(2)
    op_of[r['slug']] = (name, meth, path)
    spec = json.load(open(f'openapi/{name}.json')) if name not in actions else None
    samples = snippets.get(r['slug']) or {}
    if 'python sdk' in samples:
        samples.setdefault('python', samples.pop('python sdk'))
    cs = [{'lang': l, 'label': LABEL[l], 'source': samples[l]} for l in ORDER if samples.get(l)]
    upd = {'x-mint': {'href': public_path(r['slug'])}, 'x-codeSamples': cs}
    summary = (json.load(open(f'openapi/{name}.json'))['paths'].get(path, {}).get(meth.lower(), {}) or {}).get('summary')
    if r['title'] and r['title'] != summary:
        upd['x-mint']['metadata'] = {'sidebarTitle': r['title']}
        report['endpoint_label_differs'].append(f'{r["slug"]}: {summary} / {r["title"]}')
    actions[name].append({'target': f"$.paths['{path}'].{meth.lower()}", 'update': upd})
    manifest.append(dict(source_url=f'{HOST}/{r["slug"]}', source_title=r['title'], source_sidebar_label=r['title'], nav_section=trail(r), converted_file=f'openapi/{name}.json {meth} {path}', status='done', notes='Generated from the OpenAPI spec at the original URL.'))
for name, acts in actions.items():
    json.dump({'overlay':'1.1.0','info':{'title':f'Frame.io docs overlay: {name}','version':'1.0.0'},'extends':f'./{name}.json','actions':acts}, open(f'openapi/{name}.overlay.json','w'), indent=1, ensure_ascii=False)

# ---------- navigation ----------
def nav_nodes(children, spec=None):
    out = []
    for n in children:
        t = n.get('type')
        if t == 'page': out.append(n['slug'])
        elif t == 'endpoint':
            name, meth, path = op_of[n['slug']]
            out.append(f'{meth} {path}')
        elif t in ('section','apiPackage','apiReference'):
            out.append({'group': n['title'], 'pages': nav_nodes(n.get('children') or [])})
        elif t == 'changelog': out.append(n['slug'])
    return out

def tab(label, icon, key, spec=None):
    ch = load_nav(key)['sidebarChildren']
    nodes = nav_nodes(ch)
    groups = [g for g in nodes if isinstance(g, dict)]
    d = {'tab': label, 'icon': icon}
    if spec: d['openapi'] = {'source': f'openapi/{spec}.json', 'overlays': [f'openapi/{spec}.overlay.json']}
    # Single flat Changelog group: the changelog page is the whole tab.
    d['groups'] = groups
    return d

def changelog_tab(slug): return {'tab': 'Changelog', 'icon': 'list', 'pages': [slug]}
v4 = NAVS[('Platform','V4')]; ex = NAVS[('Platform','V4 Experimental')]; lg = NAVS[('Platform','Legacy')]; c2 = NAVS[('Camera to Cloud',None)]
navigation = {'products': [
  {'product':'Platform','description':'Build powerful integrations','icon':'layer-group','versions':[
    {'version':'V4','default':True,'tabs':[tab('Home','house',v4['home']),tab('API Reference','code',v4['api'],'v4'),tab('Docs','book',v4['docs']),changelog_tab('platform/changelog')]},
    {'version':'V4 Experimental','tabs':[tab('Home','house',ex['home']),tab('API Reference','code',ex['api'],'v4-experimental'),tab('Docs','book',ex['docs']),changelog_tab('platform/v4-experimental/changelog')]},
    {'version':'Legacy','tabs':[tab('Docs','book',lg['docs']),tab('API Reference','code',lg['api'],'v2')]},
  ]},
  {'product':'Camera to Cloud','description':'Integrate your cameras and devices','icon':'camera','tabs':[tab('Home','house',c2['home']),tab('Docs','book',c2['docs']),tab('API Reference','code',c2['api'],'camera-to-cloud')]},
]}

# ---------- redirects ----------
red = []
seen = set()
def add(src, dst):
    if src == dst or src in seen: return
    seen.add(src); red.append({'source': src, 'destination': dst})
add('/', '/platform/welcome')
# Mintlify treats /x/index as /x, so a redirect from /x would hijack a real /x/index page.
def has_index(s): return s + '/index' in SLUGS
for s, d in sorted(POINTS.items()):
    d = POINTS.get(d, d)
    if has_index(s):
        report['section_lands_on_index'].append(f'/{s} serves /{s}/index instead of redirecting to /{d}')
        continue
    add('/' + s, public_path(d))
add('/platform/v2/index', '/platform/v2')
add('/app/custom-actions/builder', 'https://next.frame.io/settings/actions')
def anchor(title): return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
for root, entries in changelogs.items():
    for e in entries:
        add('/' + e['slug'], f'/{root}#{anchor(e["title"])}')
        if e['slug'].startswith('platform/changelog/'):
            add('/platform/v4/' + e['slug'][len('platform/'):], f'/{root}#{anchor(e["title"])}')
add('/platform/v4/changelog', '/platform/changelog')
# Fern served every V4 page at both /platform/x and /platform/v4/x, and llms.txt advertises the second form.
def is_v4(s): return s.startswith('platform/') and not s.startswith(('platform/v2', 'platform/v4-experimental', 'platform/v4/', 'platform/changelog/'))
for s in sorted(SLUGS):
    if is_v4(s): add('/platform/v4/' + s[len('platform/'):], '/' + s)
for s, d in sorted(POINTS.items()):
    if is_v4(s):
        d = POINTS.get(d, d)
        add('/platform/v4/' + s[len('platform/'):], '/' + s if has_index(s) else public_path(d))
add('/platform/v4/:slug*', '/platform/:slug*')
for loc in ['de-DE','es-ES','fr-FR','it-IT','ja-JP','ko-KR','pt-BR','ru-RU','zh-CN','en-US']:
    add(f'/{loc}/:slug*', '/:slug*')
json.dump(red, open('redirects.json','w'), indent=2)

# ---------- docs.json ----------
BRAND = json.load(open('migration/brand.json')) if os.path.exists('migration/brand.json') else {}
docs = {
 '$schema':'https://mintlify.com/docs.json','theme':'mint','name':'Frame.io API Documentation',
 'colors':{'primary':'#FFFFFF','light':'#FFFFFF','dark':'#FFFFFF'},
 'appearance':{'default':'dark','strict':True},
 'background':{'color':{'dark':'#010101'}},
 'logo':{'light':'/logo/frame-io-symbol.svg','dark':'/logo/frame-io-symbol.svg','href':'https://frame.io/?utm_campaign=demo&utm_medium=framedocs&utm_source=logo'},
 'favicon':'/favicon.jpg',
 'navbar':{'links':[
   {'label':'Tokens','href':'https://console.frame.io/app/tokens'},
   {'label':'Webhooks','href':'https://next.frame.io/settings/webhooks'},
   {'label':'Custom Actions','href':'https://next.frame.io/settings/actions'},
   {'label':'OAuth Apps','href':'https://console.frame.io/app/oauth-apps'},
   {'label':'Community','href':'https://forum.frame.io/'},
   {'label':'Contact Us','href':'https://frame.io/contact?utm_campaign=demo&utm_medium=framedocs&utm_source=navbar'}],
  'primary':{'type':'button','label':'Console','href':'https://developer.adobe.com/console?utm_campaign=demo&utm_medium=framedocs&utm_source=navbar'}},
 'footer':{'links':[{'header':'Adobe Inc.','items':[
   {'label':'Terms','href':'https://frame.io/terms'},
   {'label':'Privacy','href':'https://frame.io/privacy'},
   {'label':'Do not sell or share my personal information','href':'https://frame.io/privacy#my-personal-information'}]}]},
 'api':{'playground':{'display':'interactive'},'examples':{'languages':['curl','python','typescript','javascript','go','ruby','java','php','csharp','swift']}},
 'navigation':navigation,
 'redirects':{'$ref':'./redirects.json'},
}
docs.update(BRAND)
json.dump(docs, open('docs.json','w'), indent=2, ensure_ascii=False)

json.dump(manifest, open('migration-manifest.json','w'), indent=2, ensure_ascii=False)
json.dump(ASSETS, open('mirror/assets.json','w'), indent=1)
json.dump({k: sorted(set(v)) for k, v in report.items()}, open('mirror/report.json','w'), indent=1, ensure_ascii=False)
print('pages', len(written), 'manifest', len(manifest), 'assets', len(ASSETS), 'redirects', len(red))
print({k: len(set(v)) for k, v in report.items()})
