#!/usr/bin/env python3
"""Decode Fern's Astro island props into a sidebar tree for one rendered page."""
import re, html, json, sys

def dec(v):
    if isinstance(v, list) and len(v) == 2 and isinstance(v[0], int):
        t, x = v
        if t == 0:
            return {k: dec(i) for k, i in x.items()} if isinstance(x, dict) else x
        if t == 1:
            return [dec(i) for i in x]
        return x
    if isinstance(v, list) and len(v) == 1:
        return None
    if isinstance(v, dict):
        return {k: dec(i) for k, i in v.items()}
    return v

def islands(path):
    t = open(path, errors='ignore').read()
    for m in re.finditer(r'<astro-island\b[^>]*?component-url="([^"]*)"[^>]*?props="([^"]*)"', t):
        try:
            yield m.group(1), dec_props(html.unescape(m.group(2)))
        except Exception as e:
            pass

def dec_props(s):
    d = json.loads(s)
    return {k: dec(v) for k, v in d.items()}

if __name__ == '__main__':
    for url, p in islands(sys.argv[1]):
        print(url, list(p.keys())[:12], len(json.dumps(p)))
