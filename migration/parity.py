#!/usr/bin/env python3
"""Word-level parity: every word in Fern's markdown export must exist in the converted MDX."""
import json, re, collections, os, sys
rows = json.load(open('mirror/inventory.json'))
PRE = re.compile(r'^> For AI client integration.*$', re.M)
def words(t):
    t = t.replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"').replace('\u201d', '"')
    fences = ' '.join(re.findall(r'^\s*`{3,}\S*\s+title="([^"]*)"', t, flags=re.M))
    t = re.sub(r'^\s*```\S*.*$', ' ', t, flags=re.M)
    t = t + ' ' + fences + ' ' + ' '.join(re.findall(r'!\[[^\]]*\]\([^ )]* "([^"]*)"\)', t))
    attrs = ' '.join(m.group(2) for m in re.finditer(r'\b(title|tip)="([^"]*)"', t))
    t = t + ' ' + attrs
    t = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', t)
    t = re.sub(r'\]\([^)]*\)', ']', t)
    t = re.sub(r'<svg.*?</svg>', ' ', t, flags=re.S)
    t = re.sub(r'</?[A-Za-z][^>]*>', ' ', t)
    t = t.replace('\\', '')
    t = re.sub(r'&amp;', '&', t); t = re.sub(r'&lt;', '<', t); t = re.sub(r'&gt;', '>', t)
    return collections.Counter(re.findall(r"[A-Za-z0-9][A-Za-z0-9_.'/-]*[A-Za-z0-9]|[A-Za-z0-9]", t))
tot = miss = 0; bad = []
for r in rows:
    if r['kind'] == 'endpoint': continue
    slug = r['slug']
    md = open('mirror/md/' + slug.replace('/', '__') + '.md', errors='ignore').read()
    m = PRE.search(md); md = md[m.end():] if m else md
    md = re.sub(r'^\s*# .+\n+> .+\n', '', md, count=1)                 # meta-only subtitle, title handled below
    md = re.sub(r'(?m)^\*\*`[^`]*`\*\*$', ' ', md)                     # fence title label repeated by the export
    if r['kind'] == 'changelog': continue
    out = slug + '.mdx'
    if r['kind'] == 'changelogEntry':
        out = re.match(r'^(.*/changelog)/', slug).group(1) + '.mdx'
    o = words(open(out, errors='ignore').read())
    w = words(md)
    tot += sum(w.values())
    lost = {k: v - o.get(k, 0) for k, v in w.items() if v > o.get(k, 0) and k not in ('Note','Tip','Info','Warning','Launch','Error','Success')}
    n = sum(lost.values()); miss += n
    if n: bad.append((n, sum(w.values()), slug, sorted(lost.items(), key=lambda x: -x[1])[:10]))
print('words checked', tot, 'missing', miss, 'pages with gaps', len(bad))
for b in sorted(bad, reverse=True)[:int(sys.argv[1]) if len(sys.argv) > 1 else 25]: print(b)
