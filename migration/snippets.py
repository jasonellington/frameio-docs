#!/usr/bin/env python3
"""Harvest the per-language SDK samples Fern renders on each endpoint page (JSON data only)."""
import json, os, collections
from bs4 import BeautifulSoup
def dec(v):
    if isinstance(v, list) and len(v) == 2 and isinstance(v[0], int):
        t, x = v
        if t == 0: return {k: dec(i) for k, i in x.items()} if isinstance(x, dict) else x
        if t == 1: return [dec(i) for i in x]
        return x
    if isinstance(v, list) and len(v) == 1: return None
    return v
out = {}; langs = collections.Counter()
for line in open('mirror/urls-ep.txt'):
    slug = line.strip()
    s = BeautifulSoup(open('mirror/ep/' + slug.replace('/', '__') + '.html', errors='ignore').read(), 'lxml')
    isl = [e for e in s.find_all('astro-island') if 'EndpointIsland' in (e.get('component-url') or '')]
    if not isl:
        out[slug] = {}; langs['#no-island'] += 1; continue
    p = json.loads(isl[0]['props'])
    ep = dec(p['endpoint'])
    got = {}
    for ex in (ep.get('examples') or []):
        for lang, arr in (ex.get('snippets') or {}).items():
            if lang not in got and arr:
                got[lang] = arr[0].get('code')
    for k in got: langs[k] += 1
    out[slug] = got
json.dump(out, open('mirror/snippets.json', 'w'), indent=0)
print(langs)
